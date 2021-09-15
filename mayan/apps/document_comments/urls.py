from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import APICommentListView, APICommentView
from .views import (
    DocumentCommentCreateView, DocumentCommentDeleteView,
    DocumentCommentDetailView, DocumentCommentEditView,
    DocumentCommentListView
)

urlpatterns = [
    url(
        regex=r'^(?P<pk>\d+)/comment/add/$',
        view=DocumentCommentCreateView.as_view(), name='comment_add'
    ),
    url(
        regex=r'^comment/(?P<pk>\d+)/delete/$',
        view=DocumentCommentDeleteView.as_view(), name='comment_delete'
    ),
    url(
        regex=r'^comment/(?P<pk>\d+)/$',
        view=DocumentCommentDetailView.as_view(), name='comment_details'
    ),
    url(
        regex=r'^comment/(?P<pk>\d+)/edit/$',
        view=DocumentCommentEditView.as_view(), name='comment_edit'
    ),
    url(
        regex=r'^(?P<pk>\d+)/comment/list/$',
        view=DocumentCommentListView.as_view(), name='comments_for_document'
    ),
]

api_urls = [
    url(
        regex=r'^documents/(?P<document_pk>[0-9]+)/comments/$',
        view=APICommentListView.as_view(), name='comment-list'
    ),
    url(
        regex=r'^documents/(?P<document_pk>[0-9]+)/comments/(?P<comment_pk>[0-9]+)/$',
        view=APICommentView.as_view(), name='comment-detail'
    ),
]
