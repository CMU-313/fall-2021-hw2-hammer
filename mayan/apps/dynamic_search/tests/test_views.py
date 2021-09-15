from django.test import override_settings

from mayan.apps.documents.models.document_models import DocumentSearchResult
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.search import document_search
from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin
from mayan.apps.testing.tests.base import GenericViewTestCase
from mayan.apps.storage.utils import fs_cleanup, mkdtemp

from ..classes import SearchBackend, SearchModel
from ..permissions import permission_search_tools
from ..settings import setting_backend_arguments

from .mixins import SearchToolsViewTestMixin, SearchViewTestMixin


class AdvancedSearchViewTestCase(
    DocumentTestMixin, SearchViewTestMixin, GenericViewTestCase
):
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self.test_document_count = 4

        # Upload many instances of the same test document
        for i in range(self.test_document_count):
            self._upload_test_document()

        self.search_backend = SearchBackend.get_instance()

    def test_advanced_search_past_first_page(self):
        test_document_label = self.test_documents[0].label

        for document in self.test_documents:
            self.grant_access(
                obj=document, permission=permission_document_view
            )

        # Make sure all documents are returned by the search
        queryset = self.search_backend.search(
            search_model=document_search,
            query_string={'label': test_document_label},
            user=self._test_case_user
        )
        self.assertEqual(queryset.count(), self.test_document_count)

        with self.settings(VIEWS_PAGINATE_BY=2):
            # Functional test for the first page of advanced results
            response = self._request_search_results_view(
                data={'label': test_document_label}, kwargs={
                    'search_model_name': document_search.get_full_name()
                }
            )

            # Total (1 - 2 out of 4) (Page 1 of 2)
            # 4 results total, 2 pages, current page is 1,
            # object in this page: 2
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.context['paginator'].object_list.count(), 4
            )
            self.assertEqual(response.context['paginator'].num_pages, 2)
            self.assertEqual(response.context['page_obj'].number, 1)
            self.assertEqual(
                response.context['page_obj'].object_list.count(), 2
            )

            # Functional test for the second page of advanced results
            response = self._request_search_results_view(
                data={'label': test_document_label, 'page': 2}, kwargs={
                    'search_model_name': document_search.get_full_name()
                }
            )
            # Total (3 - 4 out of 4) (Page 2 of 2)
            # 4 results total, 2 pages, current page is 1,
            # object in this page: 2
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.context['paginator'].object_list.count(), 4
            )
            self.assertEqual(response.context['paginator'].num_pages, 2)
            self.assertEqual(response.context['page_obj'].number, 2)
            self.assertEqual(
                response.context['page_obj'].object_list.count(), 2
            )


class SearchViewTestCase(
    DocumentTestMixin, SearchViewTestMixin, GenericViewTestCase
):
    def test_result_view_with_search_mode_in_data(self):
        self.grant_access(
            obj=self.test_document, permission=permission_document_view
        )

        response = self._request_search_results_view(
            data={
                'label': self.test_document.label,
                '_search_model_name': document_search.get_full_name()
            }
        )
        self.assertContains(
            response=response, status_code=200, text=self.test_document.label
        )


@override_settings(SEARCH_BACKEND='mayan.apps.dynamic_search.backends.whoosh.WhooshSearchBackend')
class SearchToolsViewTestCase(
    DocumentTestMixin, SearchToolsViewTestMixin, GenericViewTestCase
):
    def setUp(self):
        self.old_value = setting_backend_arguments.value
        super().setUp()
        self.document_search_model = SearchModel.get_for_model(
            instance=DocumentSearchResult
        )
        setting_backend_arguments.set(
            value={'index_path': mkdtemp()}
        )
        self.search_backend = SearchBackend.get_instance()

    def tearDown(self):
        fs_cleanup(
            filename=setting_backend_arguments.value['index_path']
        )
        setting_backend_arguments.set(value=self.old_value)
        super().tearDown()

    def test_search_backend_reindex_view_no_permission(self):
        self.search_backend.clear_search_model_index(
            search_model=self.document_search_model
        )
        self.grant_access(
            obj=self.test_document, permission=permission_document_view
        )

        response = self._request_search_backend_reindex_view()
        self.assertEqual(response.status_code, 403)

        queryset = self.search_backend.search(
            search_model=self.document_search_model,
            query_string={'q': self.test_document.label},
            user=self._test_case_user
        )
        self.assertEqual(queryset.count(), 0)

    def test_search_backend_reindex_view_with_permission(self):
        self.search_backend.clear_search_model_index(
            search_model=self.document_search_model
        )
        self.grant_access(
            obj=self.test_document, permission=permission_document_view
        )
        self.grant_permission(permission=permission_search_tools)

        response = self._request_search_backend_reindex_view()
        self.assertEqual(response.status_code, 302)

        queryset = self.search_backend.search(
            search_model=self.document_search_model,
            query_string={'q': self.test_document.label},
            user=self._test_case_user
        )
        self.assertNotEqual(queryset.count(), 0)
