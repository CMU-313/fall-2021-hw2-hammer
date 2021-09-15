from __future__ import unicode_literals

from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation import Link

from .icons import (
    icon_transformation, icon_transformation_create, icon_transformation_delete,
    icon_transformation_edit
)
from .permissions import (
    permission_transformation_create, permission_transformation_delete,
    permission_transformation_edit, permission_transformation_view
)


def get_kwargs_factory(variable_name):
    def get_kwargs(context):
        ContentType = apps.get_model(
            app_label='contenttypes', model_name='ContentType'
        )

        content_type = ContentType.objects.get_for_model(
            context[variable_name]
        )
        return {
            'app_label': '"{}"'.format(content_type.app_label),
            'model': '"{}"'.format(content_type.model),
            'object_id': '{}.pk'.format(variable_name)
        }

    return get_kwargs


link_transformation_create = Link(
    icon_class=icon_transformation_create,
    kwargs=get_kwargs_factory('content_object'),
    permission=permission_transformation_create,
    text=_('Create new transformation'), view='converter:transformation_create'
)
link_transformation_delete = Link(
    icon_class=icon_transformation_delete,
    kwargs={'transformation_id': 'resolved_object.pk'},
    permission=permission_transformation_delete, tags='dangerous',
    text=_('Delete'), view='converter:transformation_delete'
)
link_transformation_edit = Link(
    icon_class=icon_transformation_edit,
    kwargs={'transformation_id': 'resolved_object.pk'},
    permission=permission_transformation_edit, text=_('Edit'),
    view='converter:transformation_edit'
)
link_transformation_list = Link(
    icon_class=icon_transformation,
    kwargs=get_kwargs_factory('resolved_object'),
    permission=permission_transformation_view, text=_('Transformations'),
    view='converter:transformation_list'
)
