from __future__ import unicode_literals

from django.conf.urls import include, url

from .api_views import APIRoot, BrowseableObtainAuthToken, schema_view


api_urls = [
    url(regex=r'^$', view=APIRoot.as_view(), name='api_root'),
    url(
        regex=r'^auth/token/obtain/$', view=BrowseableObtainAuthToken.as_view(),
        name='auth_token_obtain'
    ),
]

urlpatterns = [
    url(
        regex=r'^auth/token/obtain/$', name='auth_token_obtain',
        view=BrowseableObtainAuthToken.as_view()
    ),
    url(
        regex=r'^swagger(?P<format>.json|.yaml)$', name='schema-json',
        view=schema_view.without_ui(cache_timeout=None),
    ),
    url(
        regex=r'^swagger/$', name='schema-swagger-ui',
        view=schema_view.with_ui('swagger', cache_timeout=None)
    ),
    url(
        regex=r'^redoc/$', name='schema-redoc',
        view=schema_view.with_ui('redoc', cache_timeout=None)
    ),
    url(regex=r'^', view=include(api_urls)),
]
