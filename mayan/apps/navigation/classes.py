from __future__ import unicode_literals

import inspect
import logging

from furl import furl

from django.apps import apps
from django.conf import settings
from django.contrib.admin.utils import label_for_field
from django.core.exceptions import FieldDoesNotExist, PermissionDenied
from django.db.models.constants import LOOKUP_SEP
from django.shortcuts import resolve_url
from django.template import VariableDoesNotExist, Variable
from django.template.defaulttags import URLNode
from django.urls import resolve
from django.utils.encoding import force_str, force_text
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.literals import (
    TEXT_SORT_FIELD_PARAMETER, TEXT_SORT_FIELD_VARIABLE_NAME,
    TEXT_SORT_ORDER_CHOICE_ASCENDING, TEXT_SORT_ORDER_CHOICE_DESCENDING,
    TEXT_SORT_ORDER_PARAMETER, TEXT_SORT_ORDER_VARIABLE_NAME
)
from mayan.apps.common.utils import resolve_attribute
from mayan.apps.permissions import Permission

from .exceptions import NavigationError
from .utils import get_current_view_name

logger = logging.getLogger(__name__)


class ResolvedLink(object):
    def __init__(self, link, current_view_name):
        self.current_view_name = current_view_name
        self.disabled = False
        self.link = link
        self.url = '#'
        self.context = None
        self.request = None

    @property
    def active(self):
        return self.link.view == self.current_view_name

    @property
    def description(self):
        return self.link.description

    @property
    def html_data(self):
        return self.link.html_data

    @property
    def html_extra_classes(self):
        return self.link.html_extra_classes

    @property
    def icon(self):
        return self.link.icon

    @property
    def icon_class(self):
        return self.link.icon_class

    @property
    def tags(self):
        return self.link.tags

    @property
    def text(self):
        try:
            return self.link.text(context=self.context)
        except TypeError:
            return self.link.text


class Menu(object):
    _registry = {}

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    @classmethod
    def remove(cls, name):
        del cls._registry[name]

    def __init__(self, name, condition=None, icon=None, icon_class=None, label=None, non_sorted_sources=None):
        if name in self.__class__._registry:
            raise Exception('A menu with this name already exists')

        self.condition = condition
        self.icon = icon
        self.icon_class = icon_class
        self.name = name
        self.label = label
        self.bound_links = {}
        self.unbound_links = {}
        self.link_positions = {}
        self.__class__._registry[name] = self
        self.non_sorted_sources = non_sorted_sources or []

    def _map_links_to_source(self, links, source, map_variable='bound_links', position=None):
        source_links = getattr(self, map_variable).setdefault(source, [])

        for link in links:
            source_links.append(link)
            self.link_positions[link] = position

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
            force_text(resolved_navigation_object_list)
        )
        return resolved_navigation_object_list

    def resolve(self, context, source=None, sort_results=False):
        if not self.check_condition(context=context):
            return []

        result = []

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
                    # When source is a dictionary
                    pass

            if resolved_links:
                result.append(resolved_links)

        resolved_links = []
        # View links
        for link in self.bound_links.get(current_view_name, []):
            resolved_link = link.resolve(context=context)
            if resolved_link:
                if resolved_link.link not in self.unbound_links.get(current_view_name, ()):
                    resolved_links.append(resolved_link)

        if resolved_links:
            result.append(resolved_links)

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
            result.append(resolved_links)

        if result:
            unsorted_source = False
            for resolved_navigation_object in resolved_navigation_object_list:
                for source in self.non_sorted_sources:
                    if isinstance(resolved_navigation_object, source):
                        unsorted_source = True
                        break

            if sort_results and not unsorted_source:
                result[0] = sorted(
                    result[0], key=lambda item: (
                        item.link.text if isinstance(item, ResolvedLink) else item.label
                    )
                )
            else:
                # Sort links by position value passed during bind
                result[0] = sorted(
                    result[0], key=lambda item: (self.link_positions.get(item.link) or 0) if isinstance(item, ResolvedLink) else (self.link_positions.get(item) or 0)
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


class Link(object):
    _registry = {}

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    @classmethod
    def remove(cls, name):
        del cls._registry[name]

    def __init__(self, text, view=None, args=None, condition=None,
                 conditional_disable=None, description=None, html_data=None,
                 html_extra_classes=None, icon=None, icon_class=None,
                 keep_query=False, kwargs=None, name=None, permissions=None,
                 permissions_related=None, remove_from_query=None, tags=None,
                 url=None):

        self.args = args or []
        self.condition = condition
        self.conditional_disable = conditional_disable
        self.description = description
        self.html_data = html_data
        self.html_extra_classes = html_extra_classes
        self.icon = icon
        self.icon_class = icon_class
        self.keep_query = keep_query
        self.kwargs = kwargs or {}
        self.name = name
        self.permissions = permissions or []
        self.permissions_related = permissions_related
        self.remove_from_query = remove_from_query or []
        self.tags = tags
        self.text = text
        self.view = view
        self.url = url

        if name:
            self.__class__._registry[name] = self

    def resolve(self, context, resolved_object=None):
        AccessControlList = apps.get_model(
            app_label='acls', model_name='AccessControlList'
        )

        # Try to get the request object the faster way and fallback to the
        # slower method.
        try:
            request = context.request
        except AttributeError:
            request = Variable('request').resolve(context)

        current_path = request.META['PATH_INFO']
        current_view_name = resolve(current_path).view_name

        # ACL is tested agains the resolved_object or just {{ object }} if not
        if not resolved_object:
            try:
                resolved_object = Variable('object').resolve(context=context)
            except VariableDoesNotExist:
                pass

        # If this link has a required permission check that the user has it
        # too
        if self.permissions:
            if resolved_object:
                try:
                    AccessControlList.objects.check_access(
                        permissions=self.permissions, user=request.user,
                        obj=resolved_object, related=self.permissions_related
                    )
                except PermissionDenied:
                    return None
            else:
                try:
                    Permission.check_permissions(
                        requester=request.user, permissions=self.permissions
                    )
                except PermissionDenied:
                    return None

        # Check to see if link has conditional display function and only
        # display it if the result of the conditional display function is
        # True
        if self.condition:
            if not self.condition(context):
                return None

        resolved_link = ResolvedLink(
            current_view_name=current_view_name, link=self
        )

        if self.view:
            view_name = Variable('"{}"'.format(self.view))
            if isinstance(self.args, list) or isinstance(self.args, tuple):
                # TODO: Don't check for instance check for iterable in try/except
                # block. This update required changing all 'args' argument in
                # links.py files to be iterables and not just strings.
                args = [Variable(arg) for arg in self.args]
            else:
                args = [Variable(self.args)]

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
                resolved_link.url = node.render(context)
            except Exception as exception:
                logger.error(
                    'Error resolving link "%s" URL; %s', self.text, exception
                )
        elif self.url:
            resolved_link.url = self.url

        # This is for links that should be displayed but that are not clickable
        if self.conditional_disable:
            resolved_link.disabled = self.conditional_disable(context)
        else:
            resolved_link.disabled = False

        # Lets a new link keep the same URL query string of the current URL
        if self.keep_query:
            # Sometimes we are required to remove a key from the URL QS
            parsed_url = furl(
                force_str(
                    request.get_full_path() or request.META.get(
                        'HTTP_REFERER', resolve_url(settings.LOGIN_REDIRECT_URL)
                    )
                )
            )

            for key in self.remove_from_query:
                try:
                    parsed_url.query.remove(key)
                except KeyError:
                    pass

            # Use the link's URL but with the previous URL querystring
            new_url = furl(resolved_link.url)
            new_url.args = parsed_url.querystr
            resolved_link.url = new_url.url

        resolved_link.context = context
        return resolved_link


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


class SourceColumn(object):
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
    def get_for_source(cls, context, source, exclude_identifier=False, only_identifier=False):
        try:
            result = cls._registry[source]
        except KeyError:
            try:
                # Might be an instance, try its class
                result = cls._registry[source.__class__]
            except KeyError:
                try:
                    # Might be an inherited class insance, try its source class
                    result = cls._registry[source.source_ptr.__class__]
                except (KeyError, AttributeError):
                    try:
                        # Try it as a queryset
                        result = cls._registry[source.model]
                    except AttributeError:
                        try:
                            # Special case for queryset items produced from
                            # .defer() or .only() optimizations
                            result = cls._registry[list(source._meta.parents.items())[0][0]]
                        except (AttributeError, KeyError, IndexError):
                            result = ()
        except TypeError:
            # unhashable type: list
            result = ()

        result = SourceColumn.sort(columns=result)

        if exclude_identifier:
            result = [item for item in result if not item.is_identifier]
        else:
            if only_identifier:
                for item in result:
                    if item.is_identifier:
                        return item
                return None

        final_result = []

        try:
            request = context.request
        except AttributeError:
            # Simple request extraction failed. Might not be a view context.
            # Try alternate method.
            try:
                request = Variable('request').resolve(context)
            except VariableDoesNotExist:
                # There is no request variable, most probable a 500 in a test
                # view. Don't return any resolved request.
                logger.warning(
                    'No request variable, aborting request resolution'
                )
                return result

        current_view_name = get_current_view_name(request=request)
        for item in result:
            if item.views:
                if current_view_name in item.views:
                    final_result.append(item)
            else:
                final_result.append(item)

        return final_result

    def __init__(self, source, attribute=None, empty_value=None, func=None, include_label=False, is_absolute_url=False, is_identifier=False, is_sortable=False, kwargs=None, label=None, order=None, views=None, widget=None):
        self.source = source
        self._label = label
        self.attribute = attribute
        self.empty_value = empty_value
        self.func = func
        self.kwargs = kwargs or {}
        self.order = order or 0
        self.include_label = include_label
        self.is_absolute_url = is_absolute_url
        self.is_identifier = is_identifier
        self.is_sortable = is_sortable
        self.__class__._registry.setdefault(source, [])
        self.__class__._registry[source].append(self)
        self.label = None
        self.views = views or []
        self.widget = widget
        if not attribute and not func:
            raise NavigationError(
                'Must provide either an attribute or a function'
            )

        self._calculate_label()

    def _calculate_label(self):
        if not self._label:
            if self.attribute:
                try:
                    attribute = resolve_attribute(
                        obj=self.source, attribute=self.attribute
                    )
                    self._label = getattr(attribute, 'short_description')
                except AttributeError:
                    name, model = SourceColumn.get_attribute_recursive(
                        attribute=self.attribute, model=self.source._meta.model
                    )
                    self._label = label_for_field(
                        name=name, model=model
                    )
            else:
                self._label = getattr(
                    self.func, 'short_description', _('Unnamed function')
                )

        self.label = self._label

    def get_sort_field_querystring(self, context):
        # We do this to get an mutable copy we can modify
        querystring = context.request.GET.copy()

        previous_sort_field = context.get(TEXT_SORT_FIELD_VARIABLE_NAME, None)
        previous_sort_order = context.get(
            TEXT_SORT_ORDER_VARIABLE_NAME, TEXT_SORT_ORDER_CHOICE_DESCENDING
        )

        if previous_sort_field != self.attribute:
            sort_order = TEXT_SORT_ORDER_CHOICE_ASCENDING
        else:
            if previous_sort_order == TEXT_SORT_ORDER_CHOICE_DESCENDING:
                sort_order = TEXT_SORT_ORDER_CHOICE_ASCENDING
            else:
                sort_order = TEXT_SORT_ORDER_CHOICE_DESCENDING

        querystring[TEXT_SORT_FIELD_PARAMETER] = self.attribute
        querystring[TEXT_SORT_ORDER_PARAMETER] = sort_order

        return '?{}'.format(querystring.urlencode())

    def resolve(self, context):
        if self.views:
            if get_current_view_name(request=context.request) not in self.views:
                return

        if self.attribute:
            result = resolve_attribute(
                obj=context['object'], attribute=self.attribute,
                kwargs=self.kwargs
            )
        elif self.func:
            result = self.func(context=context, **self.kwargs)

        if self.widget:
            widget_instance = self.widget()
            return widget_instance.render(name=self.attribute, value=result)

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
        self.icon = None
        self.text = kwargs.get('text')
        self.view = None

    def resolve(self, *args, **kwargs):
        result = ResolvedLink(current_view_name=None, link=self)
        result.context = kwargs.get('context')
        result.text_span = True
        return result
