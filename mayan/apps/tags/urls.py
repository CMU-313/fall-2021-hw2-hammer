from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import (
    APIDocumentTagView, APIDocumentTagListView, APITagDocumentListView,
    APITagListView, APITagView
)
from .views import (
    DocumentTagListView, TagAttachActionView, TagCreateView,
    TagDeleteActionView, TagEditView, TagListView, TagRemoveActionView,
    TagDocumentListView
)

urlpatterns = [
    url(regex=r'^list/$', view=TagListView.as_view(), name='tag_list'),
    url(regex=r'^create/$', view=TagCreateView.as_view(), name='tag_create'),
    url(
        regex=r'^(?P<pk>\d+)/delete/$', view=TagDeleteActionView.as_view(),
        name='tag_delete'
    ),
    url(
        regex=r'^(?P<pk>\d+)/edit/$', view=TagEditView.as_view(),
        name='tag_edit'
    ),
    url(
        regex=r'^(?P<pk>\d+)/documents/$', view=TagDocumentListView.as_view(),
        name='tag_document_list'
    ),
    url(
        regex=r'^multiple/delete/$', view=TagDeleteActionView.as_view(),
        name='tag_multiple_delete'
    ),
    url(
        regex=r'^multiple/remove/document/(?P<pk>\d+)/$',
        view=TagRemoveActionView.as_view(),
        name='single_document_multiple_tag_remove'
    ),
    url(
        regex=r'^multiple/remove/document/multiple/$',
        view=TagRemoveActionView.as_view(),
        name='multiple_documents_selection_tag_remove'
    ),
    url(
        regex=r'^selection/attach/document/(?P<pk>\d+)/$',
        view=TagAttachActionView.as_view(), name='tag_attach'
    ),
    url(
        regex=r'^selection/attach/document/multiple/$',
        view=TagAttachActionView.as_view(), name='multiple_documents_tag_attach'
    ),
    url(
        regex=r'^document/(?P<pk>\d+)/tags/$',
        view=DocumentTagListView.as_view(), name='document_tag_list'
    ),
]

api_urls = [
    url(
        regex=r'^tags/(?P<pk>[0-9]+)/documents/$',
        view=APITagDocumentListView.as_view(), name='tag-document-list'
    ),
    url(
        regex=r'^tags/(?P<pk>[0-9]+)/$', view=APITagView.as_view(),
        name='tag-detail'
    ),
    url(regex=r'^tags/$', view=APITagListView.as_view(), name='tag-list'),
    url(
        regex=r'^documents/(?P<document_pk>[0-9]+)/tags/$',
        view=APIDocumentTagListView.as_view(), name='document-tag-list'
    ),
    url(
        regex=r'^documents/(?P<document_pk>[0-9]+)/tags/(?P<pk>[0-9]+)/$',
        view=APIDocumentTagView.as_view(), name='document-tag-detail'
    ),
]
