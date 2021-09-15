from __future__ import unicode_literals

import hashlib

from django.apps import apps
from django.db import models
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .settings import setting_home_view


@python_2_unicode_compatible
class ErrorLogNamespace(object):
    def __init__(self, name, label=None):
        self.name = name
        self.label = label or name

    def __str__(self):
        return force_text(self.label)

    def all(self):
        ErrorLogEntry = apps.get_model(
            app_label='common', model_name='ErrorLogEntry'
        )

        return ErrorLogEntry.objects.filter(namespace=self.name)

    def create(self, obj, result):
        obj.error_logs.create(namespace=self.name, result=result)


class MissingItem(object):
    _registry = []

    @classmethod
    def get_all(cls):
        return cls._registry

    @classmethod
    def get_missing(cls):
        result = []
        for item in cls.get_all():
            if item.condition():
                result.append(item)
        return result

    def __init__(self, label, condition, description, view):
        self.label = label
        self.condition = condition
        self.description = description
        self.view = view
        self.__class__._registry.append(self)


class PropertyHelper(object):
    """
    Makes adding fields using __class__.add_to_class easier.
    Each subclass must implement the `constructor` and the `get_result`
    method.
    """
    @staticmethod
    @property
    def constructor(source_object):
        return PropertyHelper(source_object)

    def __init__(self, instance):
        self.instance = instance

    def __getattr__(self, name):
        return self.get_result(name=name)

    def get_result(self, name):
        """
        The method that produces the actual result. Must be implemented
        by each subclass.
        """
        raise NotImplementedError


class Template(object):
    _registry = {}

    @classmethod
    def all(cls, rendered=False, request=None):
        if not rendered:
            return cls._registry.values()
        else:
            result = []
            for template in cls._registry.values():
                result.append(template.render(request=request))
            return result

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    def __init__(self, name, template_name):
        self.name = name
        self.template_name = template_name
        self.__class__._registry[name] = self

    def get_absolute_url(self):
        return reverse(
            kwargs={
                'template_name': self.name
            }, viewname='rest_api:template-detail'
        )

    def render(self, request):
        context = {
            'home_view': setting_home_view.value,
        }
        result = TemplateResponse(
            request=request,
            template=self.template_name,
            context=context,
        ).render()

        # Calculate the hash of the bytes version but return the unicode
        # version
        self.html = result.rendered_content.replace('\n', '')
        self.hex_hash = hashlib.sha256(result.content).hexdigest()
        return self


class ModelAttribute(object):
    _class_registry = []
    _model_registry = {}

    @classmethod
    def get_all_choices_for(cls, model):
        result = []

        for klass in cls._class_registry:
            result.append((klass.class_label, klass.get_choices_for(model=model)))

        return result

    @classmethod
    def get_choices_for(cls, model):
        return sorted(
            [
                (entry.name, entry.get_display()) for entry in cls.get_for(model=model)
            ], key=lambda x: x[1]
        )

    @classmethod
    def get_for(cls, model):
        try:
            return cls._model_registry[cls.class_name][model]
        except KeyError:
            # We were passed a model instance, try again using the model of
            # the instance

            # If we are already in the model class, exit with an error
            if model.__class__ == models.base.ModelBase:
                raise

            return cls.get_for(model=type(model))

    @classmethod
    def register(cls, klass):
        cls._class_registry.append(klass)

    def __init__(self, model, name, label=None, description=None):
        self.model = model
        self.label = label
        self.name = name
        self.description = description
        self._model_registry.setdefault(self.class_name, {})
        self._model_registry[self.class_name].setdefault(model, [])
        self._model_registry[self.class_name][model].append(self)

    def get_display(self, show_name=False):
        if self.description:
            return '{} - {}'.format(
                self.name if show_name else self.label, self.description
            )
        else:
            return force_text(self.name if show_name else self.label)


class ModelProperty(ModelAttribute):
    class_label = _('Model properties')
    class_name = 'property'


class ModelField(ModelAttribute):
    class_label = _('Model fields')
    class_name = 'field'

    def __init__(self, *args, **kwargs):
        super(ModelField, self).__init__(*args, **kwargs)
        self._final_model_verbose_name = None

        if not self.label:
            self.label = self.get_field_attribute(
                attribute='verbose_name'
            )
            if self.label != self._final_model_verbose_name:
                self.label = '{}, {}'.format(
                    self._final_model_verbose_name, self.label
                )

        if not self.description:
            self.description = self.get_field_attribute(
                attribute='help_text'
            )

    def get_field_attribute(self, attribute, model=None, field_name=None):
        if not model:
            model = self.model

        if not field_name:
            field_name = self.name

        parts = field_name.split('__')
        if len(parts) > 1:
            return self.get_field_attribute(
                model=model._meta.get_field(parts[0]).related_model,
                field_name='__'.join(parts[1:]), attribute=attribute
            )
        else:
            self._final_model_verbose_name = model._meta.verbose_name
            return getattr(
                model._meta.get_field(field_name=field_name),
                attribute
            )


class ModelFieldRelated(ModelField):
    class_label = _('Model related fields')
    class_name = 'related_field'


ModelAttribute.register(klass=ModelProperty)
ModelAttribute.register(klass=ModelField)
ModelAttribute.register(klass=ModelFieldRelated)
