import logging

from django.apps import apps

from mayan.apps.lock_manager.backends.base import LockingBackend
from mayan.apps.lock_manager.exceptions import LockError
from mayan.celery import app

from .literals import CHECKOUT_EXPIRATION_LOCK_EXPIRE

logger = logging.getLogger(name=__name__)


@app.task(ignore_result=True)
def task_check_expired_check_outs():
    DocumentCheckout = apps.get_model(
        app_label='checkouts', model_name='DocumentCheckout'
    )

    logger.debug(msg='executing...')
    lock_id = 'task_expired_check_outs'
    try:
        logger.debug('trying to acquire lock: %s', lock_id)
        lock = LockingBackend.get_backend().acquire_lock(
            name=lock_id, timeout=CHECKOUT_EXPIRATION_LOCK_EXPIRE
        )
        logger.debug('acquired lock: %s', lock_id)
        DocumentCheckout.objects.check_in_expired_check_outs()
        lock.release()
    except LockError:
        logger.debug(msg='unable to obtain lock')
