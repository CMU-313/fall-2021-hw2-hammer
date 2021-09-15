from __future__ import unicode_literals

from django.conf.urls import url

from .views import (
    NamespaceDetailView, NamespaceListView, StatisticDetailView,
    StatisticQueueView
)

urlpatterns = [
    url(regex=r'^$', view=NamespaceListView.as_view(), name='namespace_list'),
    url(
        regex=r'^namespace/(?P<slug>[\w-]+)/details/$',
        view=NamespaceDetailView.as_view(), name='namespace_details'
    ),
    url(
        regex=r'^(?P<slug>[\w-]+)/view/$', view=StatisticDetailView.as_view(),
        name='statistic_detail'
    ),
    url(
        regex=r'^(?P<slug>[\w-]+)/queue/$', view=StatisticQueueView.as_view(),
        name='statistic_queue'
    ),
]
