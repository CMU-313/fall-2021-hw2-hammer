from __future__ import absolute_import, unicode_literals

import logging

from django.apps import apps

logger = logging.getLogger(__name__)


class ModelPermission(object):
    _inheritances = {}
    _proxies = {}
    _registry = {}

    @classmethod
    def get_classes(cls, as_content_type=False):
        ContentType = apps.get_model(
            app_label='contenttypes', model_name='ContentType'
        )

        if as_content_type:
            content_type_dictionary = ContentType.objects.get_for_models(
                *cls._registry.keys()
            )
            content_type_ids = [
                content_type.pk for content_type in content_type_dictionary.values()
            ]

            return ContentType.objects.filter(pk__in=content_type_ids)
        else:
            return cls._registry.keys()

    @classmethod
    def get_for_class(cls, klass):
        return cls._registry.get(klass, ())

    @classmethod
    def get_for_instance(cls, instance):
        StoredPermission = apps.get_model(
            app_label='permissions', model_name='StoredPermission'
        )

        permissions = cls.get_for_class(klass=type(instance))

        pks = [
            permission.stored_permission.pk for permission in permissions
        ]
        return StoredPermission.objects.filter(pk__in=pks)

    @classmethod
    def get_inheritances(cls, model):
        return cls._inheritances[model]

    @classmethod
    def register(cls, model, permissions):
        from django.contrib.contenttypes.fields import GenericRelation

        cls._registry.setdefault(model, [])
        for permission in permissions:
            cls._registry[model].append(permission)

        AccessControlList = apps.get_model(
            app_label='acls', model_name='AccessControlList'
        )

        model.add_to_class(
            name='acls', value=GenericRelation(to=AccessControlList)
        )

    @classmethod
    def register_inheritance(cls, model, related):
        cls._inheritances.setdefault(model, [])
        cls._inheritances[model].append(related)

    @classmethod
    def register_proxy(cls, source, model):
        cls._proxies[model] = source
