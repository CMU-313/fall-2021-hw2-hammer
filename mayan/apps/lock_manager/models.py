from django.db import models
from django.utils.translation import ugettext_lazy as _

from .literals import DEFAULT_LOCK_MANAGER_DEFAULT_LOCK_TIMEOUT
from .managers import LockManager
from .settings import setting_default_lock_timeout


class Lock(models.Model):
    """
    Model to provide distributed resource locking using the database.
    """
    creation_datetime = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Creation datetime')
    )
    timeout = models.IntegerField(
        default=DEFAULT_LOCK_MANAGER_DEFAULT_LOCK_TIMEOUT,
        verbose_name=_('Timeout')
    )
    name = models.CharField(
        max_length=255, unique=True, verbose_name=_('Name')
    )

    objects = LockManager()

    class Meta:
        verbose_name = _('Lock')
        verbose_name_plural = _('Locks')

    def __str__(self):
        return self.name

    def release(self):
        """
        Release a previously held lock.
        """
        try:
            lock = Lock.objects.get(
                name=self.name, creation_datetime=self.creation_datetime
            )
        except Lock.DoesNotExist:
            """
            Our lock has expired and was reassigned.
            """
        else:
            lock.delete()

    def save(self, *args, **kwargs):
        if not self.timeout and not kwargs.get('timeout'):
            self.timeout = setting_default_lock_timeout.value

        super().save(*args, **kwargs)
