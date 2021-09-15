from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings import Namespace

from .literals import DEFAULT_EMAIL, DEFAULT_PASSWORD, DEFAULT_USERNAME

namespace = Namespace(name='autoadmin', label=_('Auto administrator'))

setting_email = namespace.add_setting(
    global_name='AUTOADMIN_EMAIL', default=DEFAULT_EMAIL,
    help_text=_(
        'Sets the email of the automatically created super user account.'
    )
)
setting_password = namespace.add_setting(
    global_name='AUTOADMIN_PASSWORD', default=DEFAULT_PASSWORD,
    help_text=_(
        'The password of the automatically created super user account. '
        'If it is equal to None, the password is randomly generated.'
    )
)
setting_username = namespace.add_setting(
    global_name='AUTOADMIN_USERNAME', default=DEFAULT_USERNAME,
    help_text=_(
        'The username of the automatically created super user account.'
    )
)
