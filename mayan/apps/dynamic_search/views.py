import logging

from django.contrib import messages
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import RedirectView

from mayan.apps.common.generics import (
    ConfirmView, SimpleView, SingleObjectListView
)
from mayan.apps.common.literals import LIST_MODE_CHOICE_ITEM

from .classes import SearchModel
from .forms import SearchForm, AdvancedSearchForm
from .icons import icon_search_submit
from .mixins import SearchModelMixin
from .permissions import permission_search_tools
from .runtime import search_backend
from .tasks import task_index_search_model

logger = logging.getLogger(name=__name__)


class ResultsView(SearchModelMixin, SingleObjectListView):
    def get_extra_context(self):
        context = {
            'hide_object': True,
            'no_results_icon': icon_search_submit,
            'no_results_text': _(
                'Try again using different terms. '
            ),
            'no_results_title': _('No search results'),
            'search_model': self.search_model,
            'title': _('Search results for: %s') % self.search_model.label,
        }

        if self.search_model.list_mode == LIST_MODE_CHOICE_ITEM:
            context['list_as_items'] = True

        return context

    def get_source_queryset(self):
        self.search_model = self.get_search_model()

        if self.request.GET:
            # Only do search if there is user input, otherwise just render
            # the template with the extra_context

            if self.request.GET.get('_match_all', 'off') == 'on':
                global_and_search = True
            else:
                global_and_search = False

            queryset = search_backend.search(
                global_and_search=global_and_search,
                search_model=self.search_model,
                query_string=self.request.GET, user=self.request.user
            )

            return queryset


class SearchAgainView(RedirectView):
    pattern_name = 'search:search_advanced'
    query_string = True


class SearchBackendReindexView(ConfirmView):
    extra_context = {
        'title': _('Reindex search backend'),
        'subtitle': _(
            'This tool is required only for some search backends.'
        ),
    }
    view_permission = permission_search_tools

    def get_post_action_redirect(self):
        return reverse(viewname='common:tools_list')

    def view_action(self):
        for search_model in SearchModel.all():
            task_index_search_model.apply_async(
                kwargs={
                    'search_model_full_name': search_model.get_full_name(),
                }
            )

        messages.success(
            message=_('Search backend reindexing queued.'),
            request=self.request
        )


class SearchView(SearchModelMixin, SimpleView):
    template_name = 'appearance/generic_form.html'
    title = _('Search')

    def get_extra_context(self):
        self.search_model = self.get_search_model()
        return {
            'form': self.get_form(),
            'form_action': reverse(
                viewname='search:results', kwargs={
                    'search_model_name': self.search_model.get_full_name()
                }
            ),
            'search_model': self.search_model,
            'submit_icon_class': icon_search_submit,
            'submit_label': _('Search'),
            'submit_method': 'GET',
            'title': _('Search for: %s') % self.search_model.label,
        }

    def get_form(self):
        if ('q' in self.request.GET) and self.request.GET['q'].strip():
            query_string = self.request.GET['q']
            return SearchForm(initial={'q': query_string})
        else:
            return SearchForm()


class AdvancedSearchView(SearchView):
    title = _('Advanced search')

    def get_form(self):
        return AdvancedSearchForm(
            data=self.request.GET, search_model=self.get_search_model()
        )
