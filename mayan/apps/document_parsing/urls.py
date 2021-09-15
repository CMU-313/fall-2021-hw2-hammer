from __future__ import unicode_literals

from django.conf.urls import url

from .api_views import APIDocumentPageContentView
from .views import (
    DocumentContentDownloadView, DocumentContentView, DocumentPageContentView,
    DocumentParsingErrorsListView, DocumentSubmitView,
    DocumentTypeSettingsEditView, DocumentTypeSubmitView, ParseErrorListView
)

urlpatterns = [
    url(
        r'^documents/(?P<pk>\d+)/content/$', DocumentContentView.as_view(),
        name='document_content'
    ),
    url(
        r'^documents/pages/(?P<pk>\d+)/content/$',
        DocumentPageContentView.as_view(), name='document_page_content'
    ),
    url(
        r'^documents/(?P<pk>\d+)/content/download/$',
        DocumentContentDownloadView.as_view(), name='document_content_download'
    ),
    url(
        r'^documents/(?P<pk>\d+)/submit/$', DocumentSubmitView.as_view(),
        name='document_submit'
    ),
    url(
        r'^documents/multiple/submit/$', DocumentSubmitView.as_view(),
        name='document_multiple_submit'
    ),
    url(
        r'^documents/(?P<pk>\d+)/errors/$',
        DocumentParsingErrorsListView.as_view(),
        name='document_parsing_error_list'
    ),
    url(
        r'^document_types/submit/$', DocumentTypeSubmitView.as_view(),
        name='document_type_submit'
    ),
    url(
        r'^document_types/(?P<pk>\d+)/parsing/settings/$',
        DocumentTypeSettingsEditView.as_view(),
        name='document_type_parsing_settings'
    ),
    url(r'^errors/all/$', ParseErrorListView.as_view(), name='error_list'),
]

api_urls = [
    url(
        r'^documents/(?P<document_pk>\d+)/versions/(?P<version_pk>\d+)/pages/(?P<page_pk>\d+)/content/$',
        APIDocumentPageContentView.as_view(),
        name='document-page-content-view'
    ),
]
