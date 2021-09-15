from __future__ import absolute_import, unicode_literals

from datetime import timedelta

from kombu import Exchange, Queue

from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from acls import ModelPermission
from common import MayanAppConfig, menu_facet, menu_main, menu_sidebar
from mayan.celery import app
from rest_api.classes import APIEndPoint

from .links import (
    link_checkin_document, link_checkout_document, link_checkout_info,
    link_checkout_list
)
from .literals import CHECK_EXPIRED_CHECK_OUTS_INTERVAL
from .permissions import (
    permission_document_checkin, permission_document_checkin_override,
    permission_document_checkout, permission_document_checkout_detail_view
)
from .tasks import task_check_expired_check_outs  # NOQA
# This import is required so that celerybeat can find the task


class CheckoutsApp(MayanAppConfig):
    name = 'checkouts'
    test = True
    verbose_name = _('Checkouts')

    def ready(self):
        super(CheckoutsApp, self).ready()

        APIEndPoint(app=self, version_string='1')

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )

        DocumentCheckout = self.get_model('DocumentCheckout')

        Document.add_to_class(
            'check_in',
            lambda document, user=None: DocumentCheckout.on_organization.check_in_document(document, user)
        )
        Document.add_to_class(
            'checkout_info',
            lambda document: DocumentCheckout.on_organization.document_checkout_info(
                document
            )
        )
        Document.add_to_class(
            'checkout_state',
            lambda document: DocumentCheckout.on_organization.document_checkout_state(
                document
            )
        )
        Document.add_to_class(
            'is_checked_out',
            lambda document: DocumentCheckout.on_organization.is_document_checked_out(
                document
            )
        )

        ModelPermission.register(
            model=Document, permissions=(
                permission_document_checkout,
                permission_document_checkin,
                permission_document_checkin_override,
                permission_document_checkout_detail_view
            )
        )

        app.conf.CELERYBEAT_SCHEDULE.update(
            {
                'task_check_expired_check_outs': {
                    'task': 'checkouts.tasks.task_check_expired_check_outs',
                    'schedule': timedelta(
                        seconds=CHECK_EXPIRED_CHECK_OUTS_INTERVAL
                    ),
                },
            }
        )

        app.conf.CELERY_QUEUES.append(
            Queue(
                'checkouts_periodic', Exchange('checkouts_periodic'),
                routing_key='checkouts_periodic', delivery_mode=1
            ),
        )

        app.conf.CELERY_ROUTES.update(
            {
                'checkouts.tasks.task_check_expired_check_outs': {
                    'queue': 'checkouts_periodic'
                },
            }
        )

        menu_facet.bind_links(links=(link_checkout_info,), sources=(Document,))
        menu_main.bind_links(links=(link_checkout_list,))
        menu_sidebar.bind_links(
            links=(link_checkout_document, link_checkin_document),
            sources=(
                'checkouts:checkout_info', 'checkouts:checkout_document',
                'checkouts:checkin_document'
            )
        )
