import copy

from ..models import MetadataType

from .literals import (
    TEST_METADATA_TYPE_LABEL_EDITED, TEST_METADATA_TYPE_NAME_EDITED,
    TEST_METADATA_TYPES_FIXTURES, TEST_METADATA_VALUE_EDITED
)


class DocumentMetadataViewTestMixin:
    def _request_test_document_metadata_add_get_view(self):
        return self.get(
            viewname='metadata:metadata_add', kwargs={
                'document_id': self.test_document.pk
            }, data={'metadata_type': self.test_metadata_type.pk}
        )

    def _request_test_document_metadata_add_post_view(self):
        return self.post(
            viewname='metadata:metadata_add', kwargs={
                'document_id': self.test_document.pk
            }, data={'metadata_type': self.test_metadata_type.pk}
        )

    def _request_test_document_metadata_multiple_add_post_view(self):
        return self.post(
            viewname='metadata:metadata_add', kwargs={
                'document_id': self.test_document.pk
            }, data={
                'metadata_type': [
                    metadata_type.pk for metadata_type in self.test_metadata_types
                ],
            }
        )

    def _request_test_document_metadata_edit_post_view(self):
        return self.post(
            viewname='metadata:metadata_edit', kwargs={
                'document_id': self.test_document.pk
            }, data={
                'form-0-id': self.test_metadata_type.pk,
                'form-0-update': True,
                'form-0-value': TEST_METADATA_VALUE_EDITED,
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-MAX_NUM_FORMS': '',
            }
        )

    def _request_test_document_metadata_list_view(self):
        return self.get(
            viewname='metadata:metadata_view', kwargs={
                'document_id': self.test_document.pk
            }
        )

    def _request_test_document_metadata_remove_get_view(self):
        return self.get(
            viewname='metadata:metadata_remove', kwargs={
                'document_id': self.test_document.pk
            }
        )

    def _request_test_document_metadata_remove_post_view(self, index=0):
        return self.post(
            viewname='metadata:metadata_remove',
            kwargs={'document_id': self.test_document.pk}, data={
                'form-0-id': self.test_metadata_types[index].pk,
                'form-0-update': True,
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-MAX_NUM_FORMS': '',
            }
        )

    def _request_test_document_multiple_metadata_add_post_view(self):
        return self.post(
            viewname='metadata:metadata_multiple_add', data={
                'id_list': '{},{}'.format(
                    self.test_documents[0].pk, self.test_documents[1].pk
                ),
                'metadata_type': self.test_metadata_type.pk
            }
        )

    def _request_test_document_multiple_metadata_edit_post_view(self):
        return self.post(
            viewname='metadata:metadata_multiple_edit', data={
                'id_list': '{},{}'.format(
                    self.test_documents[0].pk, self.test_documents[1].pk
                ),
                'form-0-id': self.test_metadata_type.pk,
                'form-0-update': True,
                'form-0-value': TEST_METADATA_VALUE_EDITED,
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-MAX_NUM_FORMS': '',
            }
        )

    def _request_test_document_multiple_metadata_remove_post_view(self):
        return self.post(
            viewname='metadata:metadata_multiple_remove', data={
                'id_list': '{},{}'.format(
                    self.test_documents[0].pk, self.test_documents[1].pk
                ),
                'form-0-id': self.test_metadata_type.pk,
                'form-0-update': True,
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-MAX_NUM_FORMS': '',
            }
        )


class MetadataTypeAPIViewTestMixin:
    def setUp(self):
        super(MetadataTypeAPIViewTestMixin, self).setUp()
        self.test_metadata_types_fixtures_api_views = copy.copy(
            TEST_METADATA_TYPES_FIXTURES
        )

    def _request_test_metadata_type_create_view(self):
        return self.post(
            viewname='rest_api:metadatatype-list',
            data=self.test_metadata_types_fixtures_api_views.pop()
        )

    def _request_test_metadata_type_delete_view(self):
        return self.delete(
            viewname='rest_api:metadatatype-detail',
            kwargs={'metadata_type_pk': self.test_metadata_type.pk}
        )

    def _request_test_metadata_type_detail_view(self):
        return self.get(
            viewname='rest_api:metadatatype-detail',
            kwargs={'metadata_type_pk': self.test_metadata_type.pk}
        )

    def _request_test_metadata_type_edit_view_via_patch(self):
        return self.patch(
            viewname='rest_api:metadatatype-detail',
            kwargs={'metadata_type_pk': self.test_metadata_type.pk}, data={
                'label': '{} edited'.format(self.test_metadata_type.label),
                'name': '{}_edited'.format(self.test_metadata_type.name),
            }
        )

    def _request_test_metadata_type_edit_view_via_put(self):
        return self.put(
            viewname='rest_api:metadatatype-detail',
            kwargs={'metadata_type_pk': self.test_metadata_type.pk}, data={
                'label': '{} edited'.format(self.test_metadata_type.label),
                'name': '{}_edited'.format(self.test_metadata_type.name),
            }
        )

    def _request_test_metadata_type_list_view(self):
        return self.get(viewname='rest_api:metadatatype-list')


class MetadataTypeTestMixin:
    def setUp(self):
        super(MetadataTypeTestMixin, self).setUp()
        self.test_metadata_types_fixtures_models = copy.copy(
            TEST_METADATA_TYPES_FIXTURES
        )
        self.test_metadata_types = []

    def _get_test_metadata_type_queryset(self):
        return MetadataType.objects.filter(
            pk__in=[
                metadata_type.pk for metadata_type in self.test_metadata_types
            ]
        )

    def _create_test_metadata_type(self):
        self.test_metadata_type = MetadataType.objects.create(
            **self.test_metadata_types_fixtures_models.pop()
        )
        self.test_metadata_types.append(self.test_metadata_type)


class MetadataTypeViewTestMixin:
    def setUp(self):
        super(MetadataTypeViewTestMixin, self).setUp()
        self.test_metadata_types_fixtures_views = copy.copy(
            TEST_METADATA_TYPES_FIXTURES
        )

    def _request_test_document_type_relationship_edit_view(self):
        # This request assumes there is only one document type and
        # blindly sets the first form of the formset.

        return self.post(
            viewname='metadata:setup_document_type_metadata_types',
            kwargs={'document_type_id': self.test_document_type.pk}, data={
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-0-relationship_type': 'required'
            }
        )

    def _request_test_metadata_type_create_view(self):
        return self.post(
            viewname='metadata:setup_metadata_type_create',
            data=self.test_metadata_types_fixtures_views.pop()
        )

    def _request_test_metadata_type_delete_view(self):
        return self.post(
            viewname='metadata:setup_metadata_type_delete', kwargs={
                'metadata_type_id': self.test_metadata_type.pk
            }
        )

    def _request_test_metadata_type_edit_view(self):
        return self.post(
            viewname='metadata:setup_metadata_type_edit', kwargs={
                'metadata_type_id': self.test_metadata_type.pk
            }, data={
                'label': TEST_METADATA_TYPE_LABEL_EDITED,
                'name': TEST_METADATA_TYPE_NAME_EDITED
            }
        )

    def _request_metadata_type_list_view(self):
        return self.get(
            viewname='metadata:setup_metadata_type_list',
        )

    def _request_test_metadata_type_relationship_edit_view(self):
        # This request assumes there is only one document type and
        # blindly sets the first form of the formset.

        return self.post(
            viewname='metadata:setup_metadata_type_document_types',
            kwargs={'metadata_type_id': self.test_metadata_type.pk}, data={
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-0-relationship_type': 'required'
            }
        )
