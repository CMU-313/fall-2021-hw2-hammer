from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Link

from .icons import (
    icon_about, icon_book, icon_current_user_locale_profile_details,
    icon_current_user_locale_profile_edit, icon_documentation,
    icon_forum, icon_license, icon_setup, icon_source_code, icon_store,
    icon_support, icon_tools
)
from .permissions_runtime import permission_error_log_view


def get_kwargs_factory(variable_name):
    def get_kwargs(context):
        ContentType = apps.get_model(
            app_label='contenttypes', model_name='ContentType'
        )

        content_type = ContentType.objects.get_for_model(
            model=context[variable_name]
        )
        return {
            'app_label': '"{}"'.format(content_type.app_label),
            'model_name': '"{}"'.format(content_type.model),
            'object_id': '{}.pk'.format(variable_name)
        }

    return get_kwargs


link_about = Link(
    icon_class=icon_about, text=_('About this'), view='common:about_view'
)
link_book = Link(
    icon_class=icon_book, tags='new_window', text=_('Get the book'),
    url='https://mayan-edms.com/book/'
)
link_current_user_locale_profile_details = Link(
    icon_class=icon_current_user_locale_profile_details,
    text=_('Locale profile'),
    view='common:current_user_locale_profile_details'
)
link_current_user_locale_profile_edit = Link(
    icon_class=icon_current_user_locale_profile_edit,
    text=_('Edit locale profile'),
    view='common:current_user_locale_profile_edit'
)
link_documentation = Link(
    icon_class=icon_documentation, tags='new_window',
    text=_('Documentation'), url='https://docs.mayan-edms.com'
)
link_object_error_list = Link(
    icon_class_path='mayan.apps.common.icons.icon_object_error_list',
    kwargs=get_kwargs_factory('resolved_object'),
    permissions=(permission_error_log_view,), text=_('Errors'),
    view='common:object_error_list',
)
link_object_error_list_clear = Link(
    icon_class_path='mayan.apps.common.icons.icon_object_error_list_clear',
    kwargs=get_kwargs_factory('resolved_object'),
    permissions=(permission_error_log_view,), text=_('Clear all'),
    view='common:object_error_list_clear',
)
link_forum = Link(
    icon_class=icon_forum, tags='new_window', text=_('Forum'),
    url='https://forum.mayan-edms.com'
)
link_license = Link(
    icon_class=icon_license, text=_('License'), view='common:license_view'
)
link_setup = Link(
    icon_class=icon_setup, text=_('Setup'), view='common:setup_list'
)
link_source_code = Link(
    icon_class=icon_source_code, tags='new_window', text=_('Source code'),
    url='https://gitlab.com/mayan-edms/mayan-edms'
)
link_store = Link(
    icon_class=icon_store, tags='new_window', text=_('Online store'),
    url='https://teespring.com/stores/mayan-edms'
)
link_support = Link(
    icon_class=icon_support, tags='new_window', text=_('Get support'),
    url='http://www.mayan-edms.com/providers/'
)
link_tools = Link(
    icon_class=icon_tools, text=_('Tools'), view='common:tools_list'
)
