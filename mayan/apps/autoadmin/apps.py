from django.conf import settings
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig

from .handlers import handler_auto_admin_account_password_change


class AutoAdminAppConfig(MayanAppConfig):
    has_tests = True
    name = 'mayan.apps.autoadmin'
    verbose_name = _('Auto administrator')

    def ready(self):
        super().ready()

        post_save.connect(
            dispatch_uid='autoadmin_handler_account_password_change',
            receiver=handler_auto_admin_account_password_change,
            sender=settings.AUTH_USER_MODEL
        )
