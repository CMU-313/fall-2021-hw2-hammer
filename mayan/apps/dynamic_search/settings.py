from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings.classes import Namespace

namespace = Namespace(label=_('Search'), name='search')

setting_search_backend = namespace.add_setting(
    global_name='SEARCH_BACKEND',
    default='mayan.apps.dynamic_search.backends.django.DjangoSearchBackend',
    help_text=_(
        'Full path to the backend to be used to handle keys and signatures.'
    )
)
setting_search_backend_arguments = namespace.add_setting(
    global_name='SEARCH_BACKEND_ARGUMENTS',
    default={}
)
setting_disable_simple_search = namespace.add_setting(
    global_name='SEARCH_DISABLE_SIMPLE_SEARCH',
    default=False, help_text=_(
        'Disables the single term bar search leaving only the advanced '
        'search button.'
    )
)
