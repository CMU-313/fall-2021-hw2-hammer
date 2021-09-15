from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings.classes import Namespace

from .literals import DEFAULT_LOGIN_METHOD, DEFAULT_MAXIMUM_SESSION_LENGTH

namespace = Namespace(label=_('Authentication'), name='authentication')
setting_login_method = namespace.add_setting(
    global_name='AUTHENTICATION_LOGIN_METHOD', default=DEFAULT_LOGIN_METHOD,
    help_text=_(
        'Controls the mechanism used to authenticated user. Options are: '
        'username, email'
    )
)
setting_maximum_session_length = namespace.add_setting(
    global_name='AUTHENTICATION_MAXIMUM_SESSION_LENGTH',
    default=DEFAULT_MAXIMUM_SESSION_LENGTH, help_text=_(
        'Maximum time a user clicking the "Remember me" checkbox will '
        'remain logged in. Value is time in seconds.'
    )
)
setting_disable_password_reset = namespace.add_setting(
    global_name='AUTHENTICATION_DISABLE_PASSWORD_RESET',
    default=False, help_text=_(
        'Remove the "Forgot your password?" link on the login form used to '
        'trigger the password reset.'
    )
)
