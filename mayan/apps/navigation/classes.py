import inspect
import logging

from furl import furl

from django.apps import apps
from django.contrib.admin.utils import (
    help_text_for_field, label_for_field
)
from django.core.exceptions import (
    FieldDoesNotExist, ImproperlyConfigured, PermissionDenied
)
from django.db.models.constants import LOOKUP_SEP
from django.template import RequestContext, Variable, VariableDoesNotExist
from django.template.defaulttags import URLNode
from django.urls import resolve, reverse
from django.utils.encoding import force_str, force_text
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.settings import setting_home_view
from mayan.apps.common.utils import get_related_field, resolve_attribute
from mayan.apps.permissions import Permission
from mayan.apps.views.icons import icon_sort_down, icon_sort_up
from mayan.apps.views.literals import (
    TEXT_SORT_FIELD_PARAMETER, TEXT_SORT_FIELD_VARIABLE_NAME
)

from .html_widgets import SourceColumnLinkWidget
from .utils import get_current_view_name

logger = logging.getLogger(name=__name__)


class Link:
    _registry = {}

    @staticmethod
    def conditional_active_by_view_name(context, resolved_link):
        return resolved_link.link.view == resolved_link.current_view_name

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    @classmethod
    def remove(cls, name):
        del cls._registry[name]

    def __init__(
        self, text=None, view=None, args=None, badge_text=None, condition=None,
        conditional_active=None, conditional_disable=None, description=None,
        html_data=None, html_extra_classes=None, icon=None,
        keep_query=False, kwargs=None, name=None, permissions=None,
        remove_from_query=None, tags=None, url=None
    ):
        self.args = args or []
        self.badge_text = badge_text
        self.condition = condition
        self.conditional_active = conditional_active or Link.conditional_active_by_view_name
        self.conditional_disable = conditional_disable
        self.description = description
        self.html_data = html_data
        self.html_extra_classes = html_extra_classes
        self.icon = icon
        self.keep_query = keep_query
        self.kwargs = kwargs or {}
        self.name = name
        self.permissions = permissions or []
        self.remove_from_query = remove_from_query or []
        self.tags = tags
        self.text = text
        self.view = view
        self.url = url

        if name:
            self.__class__._registry[name] = self

    def resolve(self, context=None, request=None, resolved_object=None):
        if not context and not request:
            raise ImproperlyConfigured(
                'Must provide a context or a request in order to resolve the '
                'link.'
            )

        AccessControlList = apps.get_model(
            app_label='acls', model_name='AccessControlList'
        )

        if not context:
            context = RequestContext(request=request)

        if not request:
            # Try to get the request object the faster way and fallback to the
            # slower method.
            try:
                request = context.request
            except AttributeError:
                request = Variable('request').resolve(context=context)

        current_path = request.META['PATH_INFO']
        current_view_name = resolve(current_path).view_name

        # ACL is tested agains the resolved_object or just {{ object }} if not
        if not resolved_object:
            try:
                resolved_object = Variable('object').resolve(context=context)
            except VariableDoesNotExist:
                """No object variable in the context"""

        # If this link has a required permission check that the user has it
        # too
        if self.permissions:
            if resolved_object:
                try:
                    AccessControlList.objects.check_access(
                        obj=resolved_object, permissions=self.permissions,
                        user=request.user
                    )
                except PermissionDenied:
                    return None
            else:
                try:
                    Permission.check_user_permissions(
                        permissions=self.permissions, user=request.user
                    )
                except PermissionDenied:
                    return None

        # Check to see if link has conditional display function and only
        # display it if the result of the conditional display function is
        # True
        if self.condition:
            if not self.condition(context=context):
                return None

        resolved_link = ResolvedLink(
            current_view_name=current_view_name, link=self
        )

        if self.view:
            view_name = Variable('"{}"'.format(self.view))
            if isinstance(self.args, list) or isinstance(self.args, tuple):
                args = [Variable(var=arg) for arg in self.args]
            else:
                args = [Variable(var=self.args)]

            # If we were passed an instance of the view context object we are
            # resolving, inject it into the context. This help resolve links for
            # object lists.
            if resolved_object:
                context['resolved_object'] = resolved_object

            try:
                kwargs = self.kwargs(context)
            except TypeError:
                # Is not a callable
                kwargs = self.kwargs

            kwargs = {key: Variable(value) for key, value in kwargs.items()}

            # Use Django's exact {% url %} code to resolve the link
            node = URLNode(
                view_name=view_name, args=args, kwargs=kwargs, asvar=None
            )
            try:
                resolved_link.url = node.render(context=context)
            except VariableDoesNotExist as exception:
                """Not critical, ignore"""
                logger.debug(
                    'VariableDoesNotExist when resolving link "%s" URL; %s',
                    self.text, exception
                )
            except Exception as exception:
                logger.error(
                    'Error resolving link "%s" URL; %s', self.text, exception,
                    exc_info=True
                )
        elif self.url:
            resolved_link.url = self.url

        # This is for links that should be displayed but that are not clickable
        if self.conditional_disable:
            resolved_link.disabled = self.conditional_disable(context=context)
        else:
            resolved_link.disabled = False

        # Lets a new link keep the same URL query string of the current URL
        if self.keep_query:
            # Sometimes we are required to remove a key from the URL QS
            parsed_url = furl(
                force_str(
                    request.get_full_path() or request.META.get(
                        'HTTP_REFERER', reverse(setting_home_view.value)
                    )
                )
            )

            for key in self.remove_from_query:
                try:
                    parsed_url.query.remove(key)
                except KeyError:
                    pass

            # Use the link's URL but with the previous URL querystring
            new_url = furl(url=resolved_link.url)
            new_url.args = parsed_url.querystr
            resolved_link.url = new_url.url

        resolved_link.context = context
        return resolved_link


class Menu:
    _registry = {}

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    @classmethod
    def remove(cls, name):
        del cls._registry[name]

    def __init__(
        self, name, condition=None, icon=None, label=None,
        non_sorted_sources=None
    ):
        if name in self.__class__._registry:
            raise Exception('A menu with this name already exists')

        self.bound_links = {}
        self.condition = condition
        self.icon = icon
        self.label = label
        self.link_positions = {}
        self.name = name
        self.non_sorted_sources = non_sorted_sources or []
        self.proxy_inclusions = set()
        self.unbound_links = {}
        self.__class__._registry[name] = self

    def __repr__(self):
        return '<Menu: {}>'.format(self.name)

    def _map_links_to_source(self, links, source, map_variable='bound_links', position=None):
        source_links = getattr(self, map_variable).setdefault(source, [])

        for link in links:
            source_links.append(link)
            self.link_positions[link] = position or 0

    def add_proxy_inclusions(self, source):
        self.proxy_inclusions.add(source)

    def add_unsorted_source(self, source):
        self.non_sorted_sources.append(source)

    def check_condition(self, context):
        """
        Check to see if menu has a conditional display function and return
        the result of the condition function against the context.
        """
        if self.condition:
            return self.condition(context=context)
        else:
            return True

    def bind_links(self, links, sources=None, position=None):
        """
        Associate a link to a model, a view inside this menu
        """
        try:
            for source in sources:
                self._map_links_to_source(
                    links=links, position=position, source=source
                )
        except TypeError:
            # Unsourced links display always
            self._map_links_to_source(
                links=links, position=position, source=sources
            )

    def get_resolved_navigation_object_list(self, context, source):
        resolved_navigation_object_list = []

        if source:
            resolved_navigation_object_list = [source]
        else:
            navigation_object_list = context.get(
                'navigation_object_list', ('object',)
            )

            logger.debug('navigation_object_list: %s', navigation_object_list)

            # Multiple objects
            for navigation_object in navigation_object_list:
                try:
                    resolved_navigation_object_list.append(
                        Variable(navigation_object).resolve(context)
                    )
                except VariableDoesNotExist:
                    pass

        logger.debug(
            'resolved_navigation_object_list: %s',
            force_text(s=resolved_navigation_object_list)
        )
        return resolved_navigation_object_list

    def get_result_position(self, item):
        """
        Method to help sort results by position.
        """
        if isinstance(item, ResolvedLink):
            return self.link_positions.get(item.link, 0)
        else:
            return self.link_positions.get(item, 0) or 0

    def get_result_label(self, item):
        """
        Method to help sort results by label.
        """
        if isinstance(item, ResolvedLink):
            return item.link.text
        else:
            return item.label

    def resolve(self, context=None, request=None, source=None, sort_results=False):
        if not context and not request:
            raise ImproperlyConfigured(
                'Must provide a context or a request in order to resolve the '
                'menu.'
            )

        if not context:
            context = RequestContext(request=request)

        if not self.check_condition(context=context):
            return []

        result = []

        if not request:
            try:
                request = context.request
            except AttributeError:
                # Simple request extraction failed. Might not be a view context.
                # Try alternate method.
                try:
                    request = Variable('request').resolve(context)
                except VariableDoesNotExist:
                    # There is no request variable, most probable a 500 in a test
                    # view. Don't return any resolved links then.
                    logger.warning('No request variable, aborting menu resolution')
                    return ()

        current_view_name = get_current_view_name(request=request)
        if not current_view_name:
            return ()

        resolved_navigation_object_list = self.get_resolved_navigation_object_list(
            context=context, source=source
        )

        for resolved_navigation_object in resolved_navigation_object_list:
            resolved_links = []

            # Check to see if object is a proxy model. If it is, add its parent model
            # menu links too.
            if hasattr(resolved_navigation_object, '_meta'):
                if resolved_navigation_object._meta.model in self.proxy_inclusions:
                    parent_model = resolved_navigation_object._meta.proxy_for_model
                    if parent_model:
                        parent_instance = parent_model.objects.filter(pk=resolved_navigation_object.pk)
                        if parent_instance.exists():
                            for link_set in self.resolve(context=context, source=parent_instance.first()):
                                for link in link_set['links']:
                                    if link.link not in self.unbound_links.get(resolved_navigation_object, ()):
                                        resolved_links.append(link)

            for bound_source, links in self.bound_links.items():
                try:
                    if inspect.isclass(bound_source):
                        if type(resolved_navigation_object) == bound_source:
                            for link in links:
                                resolved_link = link.resolve(
                                    context=context,
                                    resolved_object=resolved_navigation_object
                                )
                                if resolved_link:
                                    if resolved_link.link not in self.unbound_links.get(bound_source, ()):
                                        resolved_links.append(resolved_link)
                            # No need for further content object match testing
                            break
                        elif hasattr(resolved_navigation_object, 'get_deferred_fields') and resolved_navigation_object.get_deferred_fields() and isinstance(resolved_navigation_object, bound_source):
                            # Second try for objects using .defer() or .only()
                            for link in links:
                                resolved_link = link.resolve(
                                    context=context,
                                    resolved_object=resolved_navigation_object
                                )
                                if resolved_link:
                                    if resolved_link.link not in self.unbound_links.get(bound_source, ()):
                                        resolved_links.append(resolved_link)
                            # No need for further content object match testing
                            break

                except TypeError:
                    """
                    Normal when source is a dictionary. Non fatal.
                    """

            # Remove duplicated resolved link by using their source link
            # instance as reference. The actual resolved link can't be used
            # since a single source link can produce multiple resolved links.
            # Since dictionaries keys can't have duplicates, we use that as a
            # native deduplicator.
            resolved_links_dict = {}
            for resolved_link in resolved_links:
                resolved_links_dict[resolved_link.link] = resolved_link

            resolved_links = resolved_links_dict.values()

            if resolved_links:
                result.append(
                    {
                        'object': resolved_navigation_object,
                        'links': resolved_links
                    }
                )

        resolved_links = []
        # View links
        for link in self.bound_links.get(current_view_name, []):
            resolved_link = link.resolve(context=context)
            if resolved_link:
                if resolved_link.link not in self.unbound_links.get(current_view_name, ()):
                    resolved_links.append(resolved_link)

        if resolved_links:
            result.append(
                {
                    'object': current_view_name,
                    'links': resolved_links
                }
            )

        resolved_links = []

        # Main menu links
        for link in self.bound_links.get(None, []):
            if isinstance(link, Menu):
                condition = link.check_condition(context=context)
                if condition and link not in self.unbound_links.get(None, ()):
                    resolved_links.append(link)
            else:
                # "Always show" links
                resolved_link = link.resolve(context=context)
                if resolved_link:
                    if resolved_link.link not in self.unbound_links.get(None, ()):
                        resolved_links.append(resolved_link)

        if resolved_links:
            result.append(
                {
                    'object': None,
                    'links': resolved_links
                }
            )

        if result:
            unsorted_source = False
            for resolved_navigation_object in resolved_navigation_object_list:
                for source in self.non_sorted_sources:
                    if isinstance(resolved_navigation_object, source):
                        unsorted_source = True
                        break

            if sort_results and not unsorted_source:
                for link_group in result:
                    link_group['links'] = sorted(
                        link_group['links'], key=self.get_result_label
                    )
            else:
                for link_group in result:
                    link_group['links'] = sorted(
                        link_group['links'], key=self.get_result_position
                    )

        return result

    def unbind_links(self, links, sources=None):
        """
        Allow unbinding links from sources, used to allow 3rd party apps to
        change the link binding of core apps
        """
        try:
            for source in sources:
                self._map_links_to_source(
                    links=links, source=source, map_variable='unbound_links'
                )
        except TypeError:
            # Unsourced links display always
            self._map_links_to_source(
                links=links, source=sources, map_variable='unbound_links'
            )


class ResolvedLink:
    def __init__(self, link, current_view_name):
        self.context = None
        self.current_view_name = current_view_name
        self.disabled = False
        self.link = link
        self.request = None
        self.url = '#'

    def __repr__(self):
        return '<ResolvedLink: {}>'.format(self.url)

    @property
    def active(self):
        conditional_active = self.link.conditional_active
        if conditional_active:
            return conditional_active(
                context=self.context, resolved_link=self
            )

    @property
    def badge_text(self):
        if self.link.badge_text:
            return self.link.badge_text(context=self.context)

    @property
    def description(self):
        return self.link.description

    @property
    def html_data(self):
        return self.link.html_data

    @property
    def html_extra_classes(self):
        return self.link.html_extra_classes or ''

    @property
    def icon(self):
        return self.link.icon

    @property
    def tags(self):
        return self.link.tags

    @property
    def text(self):
        try:
            return self.link.text(context=self.context)
        except TypeError:
            return self.link.text


class Separator(Link):
    """
    Menu separator. Renders to an <hr> tag
    """
    def __init__(self, *args, **kwargs):
        self.icon = None
        self.text = None
        self.view = None

    def resolve(self, *args, **kwargs):
        result = ResolvedLink(current_view_name=None, link=self)
        result.separator = True
        return result


class SourceColumn:
    _registry = {}

    @staticmethod
    def get_attribute_recursive(attribute, model):
        """
        Walk over the double underscore (__) separated path to the last
        field. Returns the field name and the corresponding model class.
        Used to introspect the label or short_description of a model's
        attribute.
        """
        last_model = model
        for part in attribute.split(LOOKUP_SEP):
            last_model = model
            try:
                field = model._meta.get_field(part)
            except FieldDoesNotExist:
                break
            else:
                model = field.related_model or field.model

        return part, last_model

    @staticmethod
    def sort(columns):
        return sorted(columns, key=lambda x: x.order)

    @classmethod
    def get_for_source(
        cls, source, exclude_identifier=False, only_identifier=False
    ):
        # Process columns as a set to avoid duplicate resolved column
        # detection code.
        columns = []
        source_classes = set()

        if hasattr(source, '_meta'):
            source_classes.add(source._meta.model)
        else:
            source_classes.add(source)

        try:
            primary_model_columns = cls._registry[source]
        except KeyError:
            """Primary model has no columns."""
            try:
                # Might be an instance, try its class.
                # Works for model instances and custom class instances.
                primary_model_instance_columns = cls._registry[source.__class__]
            except KeyError:
                # Might be a subclass, try its super classes.
                for super_class in source.__class__.__mro__[1:-1]:
                    columns.extend(cls._registry.get(super_class, ()))
            else:
                columns.extend(primary_model_instance_columns)

        else:
            columns.extend(primary_model_columns)

        try:
            # Might be an related class instance, try its parent class.
            parent_class_columns = cls._registry[source.source_ptr.__class__]
        except (KeyError, AttributeError):
            """The parent class has no columns."""
        else:
            columns.extend(parent_class_columns)

        try:
            # Try it as a queryset.
            queryset_model_columns = cls._registry[source.model]
        except (AttributeError, KeyError):
            """Is not a queryset model or queryset model has no columns."""
            try:
                # Special case for queryset items produced from
                # .defer() or .only() optimizations.
                queryset_model_columns = cls._registry[list(source._meta.parents.items())[0][0]]
            except (AttributeError, KeyError, IndexError):
                """Queryset model has no columns."""
            else:
                columns.extend(queryset_model_columns)
        else:
            columns.extend(queryset_model_columns)

        if exclude_identifier:
            columns = [column for column in columns if not column.is_identifier]
        else:
            # exclude_identifier and only_identifier and mutually exclusive.
            if only_identifier:
                for column in columns:
                    if column.is_identifier:
                        return column

                # There is no column with the identifier marker.
                return None

        # Move filtering outside of the queryset area to work for all kind of
        # objects and to avoid filtering when only_identifier is used.
        filtered_columns = set()
        for column_index, column in enumerate(iterable=columns, start=100):
            # Make sure the column has not been excluded for proxies.
            # Examples: Workflow runtime proxy and index instances in 3.2.x
            if not source_classes.intersection(column.exclude):
                column.order = column.order or column_index
                filtered_columns.add(column)

        # Sort columns by their `order` attribute and return as a list.
        # Keep sorting as the very last operation to sort only was is really
        # needed.
        columns = SourceColumn.sort(columns=filtered_columns)

        return columns

    def __init__(
        self, source, attribute=None, empty_value=None, func=None,
        help_text=None, html_extra_classes=None, include_label=False,
        is_attribute_absolute_url=False, is_object_absolute_url=False,
        is_identifier=False, is_sortable=False, kwargs=None, label=None,
        order=None, sort_field=None, widget=None,
        widget_condition=None
    ):
        self._label = label
        self._help_text = help_text
        self.source = source
        self.attribute = attribute
        self.empty_value = empty_value
        self.exclude = set()
        self.func = func
        self.html_extra_classes = html_extra_classes
        self.is_attribute_absolute_url = is_attribute_absolute_url
        self.is_object_absolute_url = is_object_absolute_url
        self.is_identifier = is_identifier
        self.is_sortable = is_sortable
        self.kwargs = kwargs or {}
        self.include_label = include_label
        self.order = order or 0
        self.sort_field = sort_field
        self.widget = widget
        self.widget_condition = widget_condition

        if self.is_attribute_absolute_url or self.is_object_absolute_url:
            if not self.widget:
                self.widget = SourceColumnLinkWidget

        self.__class__._registry.setdefault(source, [])
        self.__class__._registry[source].append(self)

        self._calculate_label()
        self._calculate_help_text()
        if self.is_sortable:
            field_name = self.sort_field or self.attribute
            try:
                get_related_field(
                    model=self.source, related_field_name=field_name
                )
            except FieldDoesNotExist as exception:
                raise ImproperlyConfigured(
                    '"{}" is not a field of "{}", cannot be used as a '
                    'sortable column.'.format(field_name, self.source)
                ) from exception

    def _calculate_help_text(self):
        if not self._help_text:
            if self.attribute:
                try:
                    attribute = resolve_attribute(
                        obj=self.source, attribute=self.attribute
                    )
                    self._help_text = getattr(attribute, 'help_text')
                except AttributeError:
                    try:
                        name, model = SourceColumn.get_attribute_recursive(
                            attribute=self.attribute, model=self.source._meta.model
                        )
                        self._help_text = help_text_for_field(
                            name=name, model=model
                        )
                    except AttributeError:
                        self._help_text = None

        self.help_text = self._help_text

    def _calculate_label(self):
        if not self._label:
            if self.attribute:
                try:
                    attribute = resolve_attribute(
                        obj=self.source, attribute=self.attribute
                    )
                    self._label = getattr(attribute, 'short_description')
                except AttributeError:
                    try:
                        name, model = SourceColumn.get_attribute_recursive(
                            attribute=self.attribute, model=self.source._meta.model
                        )
                        self._label = label_for_field(
                            name=name, model=model
                        )
                    except AttributeError:
                        self._label = self.attribute
            else:
                self._label = getattr(
                    self.func, 'short_description', _('Unnamed function')
                )

        self.label = self._label

    def add_exclude(self, source):
        self.exclude.add(source)

    def check_widget_condition(self, context):
        if self.widget_condition:
            return self.widget_condition(context=context)
        else:
            return True

    def get_absolute_url(self, obj):
        if self.is_object_absolute_url:
            return obj.get_absolute_url()
        elif self.is_attribute_absolute_url:
            result = resolve_attribute(
                attribute=self.attribute, kwargs=self.kwargs,
                obj=obj
            )
            if result:
                return result.get_absolute_url()

    def get_previous_sort_fields(self, context):
        previous_sort_fields = context.get(TEXT_SORT_FIELD_VARIABLE_NAME, None)

        if previous_sort_fields:
            previous_sort_fields = previous_sort_fields.split(',')
        else:
            previous_sort_fields = ()

        return previous_sort_fields

    def get_sort_field(self):
        if self.sort_field:
            return self.sort_field
        else:
            return self.attribute

    def get_sort_field_querystring(self, context):
        # We do this to get an mutable copy we can modify
        querystring = context.request.GET.copy()

        previous_sort_fields = self.get_previous_sort_fields(context=context)

        sort_field = self.get_sort_field()

        if sort_field in previous_sort_fields:
            result = '-{}'.format(sort_field)
        else:
            result = '{}'.format(sort_field)

        querystring[TEXT_SORT_FIELD_PARAMETER] = result

        return '?{}'.format(querystring.urlencode())

    def get_sort_icon(self, context):
        previous_sort_fields = self.get_previous_sort_fields(context=context)
        sort_field = self.get_sort_field()

        if sort_field in previous_sort_fields:
            return icon_sort_down
        elif '-{}'.format(sort_field) in previous_sort_fields:
            return icon_sort_up

    def resolve(self, context):
        if self.attribute:
            result = resolve_attribute(
                attribute=self.attribute, kwargs=self.kwargs,
                obj=context['object']
            )
        elif self.func:
            result = self.func(context=context, **self.kwargs)
        else:
            result = context['object']

        self.absolute_url = self.get_absolute_url(obj=context['object'])
        if self.widget:
            if self.check_widget_condition(context=context):
                widget_instance = self.widget(
                    column=self, request=context['request']
                )
                return widget_instance.render(value=result)

        if not result:
            if self.empty_value:
                return self.empty_value
            else:
                return result
        else:
            return result


class Text(Link):
    """
    Menu text. Renders to a plain <li> tag
    """
    def __init__(self, *args, **kwargs):
        self.html_extra_classes = kwargs.get('html_extra_classes', '')
        self.icon = None
        self.text = kwargs.get('text')
        self.view = None

    def resolve(self, *args, **kwargs):
        result = ResolvedLink(current_view_name=None, link=self)
        result.context = kwargs.get('context')
        result.text_span = True
        return result
