from django.db.models import Q

from ..models import Comment

from .literals import TEST_COMMENT_TEXT, TEST_COMMENT_TEXT_EDITED


class CommentAPIViewTestMixin:
    def _request_test_comment_create_api_view(self):
        pk_list = list(Comment.objects.values_list('pk', flat=True))

        response = self.post(
            viewname='rest_api:comment-list', kwargs={
                'document_id': self.test_document.pk
            }, data={
                'text': TEST_COMMENT_TEXT
            }
        )

        try:
            self.test_document_comment = Comment.objects.get(
                ~Q(pk__in=pk_list)
            )
        except Comment.DoesNotExist:
            self.test_document_comment = None

        return response

    def _request_test_comment_delete_api_view(self):
        return self.delete(
            viewname='rest_api:comment-detail', kwargs={
                'document_id': self.test_document.pk,
                'comment_id': self.test_document_comment.pk,
            }
        )

    def _request_test_comment_detail_api_view(self):
        return self.get(
            viewname='rest_api:comment-detail', kwargs={
                'document_id': self.test_document.pk,
                'comment_id': self.test_document_comment.pk
            }
        )

    def _request_test_comment_edit_patch_api_view(self):
        return self.patch(
            viewname='rest_api:comment-detail', kwargs={
                'document_id': self.test_document.pk,
                'comment_id': self.test_document_comment.pk,
            }, data={'text': TEST_COMMENT_TEXT_EDITED}
        )

    def _request_test_comment_list_api_view(self):
        return self.get(
            viewname='rest_api:comment-list', kwargs={
                'document_id': self.test_document.pk
            }
        )


class DocumentCommentTestMixin:
    def _create_test_comment(self):
        self.test_document_comment = self.test_document.comments.create(
            text=TEST_COMMENT_TEXT, user=self.test_user
        )


class DocumentCommentViewTestMixin:
    def _request_test_comment_create_view(self):
        pk_list = list(Comment.objects.values_list('pk', flat=True))

        response = self.post(
            viewname='comments:comment_add', kwargs={
                'document_id': self.test_document.pk
            }, data={'text': TEST_COMMENT_TEXT}
        )

        try:
            self.test_document_comment = Comment.objects.get(
                ~Q(pk__in=pk_list)
            )
        except Comment.DoesNotExist:
            self.test_document_comment = None

        return response

    def _request_test_comment_delete_view(self):
        return self.post(
            viewname='comments:comment_delete', kwargs={
                'comment_id': self.test_document_comment.pk
            },
        )

    def _request_test_comment_detail_view(self):
        return self.get(
            viewname='comments:comment_details', kwargs={
                'comment_id': self.test_document_comment.pk
            },
        )

    def _request_test_comment_edit_view(self):
        return self.post(
            viewname='comments:comment_edit', kwargs={
                'comment_id': self.test_document_comment.pk,
            }, data={
                'text': TEST_COMMENT_TEXT_EDITED
            }
        )

    def _request_test_comment_list_view(self):
        return self.get(
            viewname='comments:comments_for_document', kwargs={
                'document_id': self.test_document.pk,
            }
        )
