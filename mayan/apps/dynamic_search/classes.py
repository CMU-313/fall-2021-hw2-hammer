import logging

from django.apps import apps
from django.db.models.signals import post_save, pre_delete
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.utils.translation import ugettext as _

from mayan.apps.common.literals import LIST_MODE_CHOICE_LIST
from mayan.apps.common.utils import get_related_field

logger = logging.getLogger(name=__name__)


class SearchBackend:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def _search(self, global_and_search, search_model, query_string, user):
        raise NotImplementedError

    def deindex_instance(self, instance):
        raise NotImplementedError

    def index_instance(self, instance):
        raise NotImplementedError

    def search(self, search_model, query_string, user, global_and_search=False):
        AccessControlList = apps.get_model(
            app_label='acls', model_name='AccessControlList'
        )

        # Clean up the query_string
        # The original query_string is immutable, create a new
        # mutable copy
        query_string = query_string.copy()
        query_string.pop('_match_all', None)

        queryset = self._search(
            global_and_search=global_and_search, search_model=search_model,
            query_string=query_string, user=user
        )

        if search_model.permission:
            queryset = AccessControlList.objects.restrict_queryset(
                permission=search_model.permission, queryset=queryset,
                user=user
            )

        return queryset


class SearchField:
    """
    Search for terms in fields that directly belong to the parent SearchModel
    """
    def __init__(self, search_model, field, label, transformation_function=None):
        self.search_model = search_model
        self.field = field
        self.label = label
        self.transformation_function = transformation_function

    def get_full_name(self):
        return self.field

    def get_model(self):
        return self.search_model.model

    def get_model_field(self):
        return get_related_field(
            model=self.get_model(), related_field_name=self.field
        )


class SearchModel:
    _model_search_relationships = {}
    _registry = {}

    @staticmethod
    def initialize():
        # Hide a circular import
        from .handlers import (
            handler_factory_deindex_instance, handler_index_instance
        )

        for search_model in SearchModel.all():
            post_save.connect(
                dispatch_uid='search_handler_index_instance',
                receiver=handler_index_instance,
            )
            pre_delete.connect(
                dispatch_uid='search_handler_deindex_instance_{}'.format(search_model),
                receiver=handler_factory_deindex_instance(search_model=search_model),
                sender=search_model.model,
                weak=False
            )

            search_model._initialize()

    @classmethod
    def all(cls):
        return sorted(list(cls._registry.values()), key=lambda x: x.label)

    @classmethod
    def as_choices(cls):
        return cls._registry

    @classmethod
    def get(cls, name):
        try:
            result = cls._registry[name]
        except KeyError:
            raise KeyError(_('No search model matching the query'))
        if not hasattr(result, 'serializer'):
            result.serializer = import_string(dotted_path=result.serializer_path)

        return result

    @classmethod
    def get_for_model(cls, instance):
        return cls.get(name=instance._meta.label)

    def __init__(
        self, app_label, model_name, serializer_path, label=None,
        list_mode=None, permission=None, queryset=None
    ):
        self.app_label = app_label
        self.list_mode = list_mode or LIST_MODE_CHOICE_LIST
        self.model_name = model_name
        self.search_fields = []
        self._model = None  # Lazy
        self._label = label
        self.serializer_path = serializer_path
        self.permission = permission
        self.queryset = queryset
        self.__class__._registry[self.get_full_name()] = self

    def __repr__(self):
        return '<{}: {}>'.format(
            self.__class__.__name__, self.label
        )

    def __str__(self):
        return force_text(self.label)

    def _initialize(self):
        for search_field in self.search_fields:
            related_model = get_related_field(
                model=self.model, related_field_name=search_field.field
            ).model

            if related_model != self.model:
                self.__class__._model_search_relationships.setdefault(self.model, set())
                self.__class__._model_search_relationships[self.model].add(related_model)

                self.__class__._model_search_relationships.setdefault(related_model, set())
                self.__class__._model_search_relationships[related_model].add(self.model)

    def add_model_field(self, *args, **kwargs):
        """
        Add a search field that directly belongs to the parent SearchModel
        """
        search_field = SearchField(self, *args, **kwargs)
        self.search_fields.append(search_field)

    def get_fields_simple_list(self):
        """
        Returns a list of the fields for the SearchModel
        """
        result = []
        for search_field in self.search_fields:
            result.append((search_field.get_full_name(), search_field.label))

        return result

    def get_full_name(self):
        return '%s.%s' % (self.app_label, self.model_name)

    def get_queryset(self):
        if self.queryset:
            return self.queryset()
        else:
            return self.model.objects.all()

    def get_search_field(self, full_name):
        try:
            return self.search_fields[full_name]
        except KeyError:
            raise KeyError('No search field named: %s' % full_name)

    @cached_property
    def label(self):
        if not self._label:
            self._label = self.model._meta.verbose_name
        return self._label

    @cached_property
    def model(self):
        if not self._model:
            self._model = apps.get_model(self.app_label, self.model_name)
        return self._model

    @cached_property
    def pk(self):
        return self.get_full_name()
