from __future__ import unicode_literals

import logging

from django.contrib.auth.models import Group
from django.db import models
from django.urls import reverse
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .classes import Permission
from .managers import RoleManager, StoredPermissionManager

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class StoredPermission(models.Model):
    """
    This model is the counterpart of the permissions.classes.Permission
    class. Allows storing a database counterpart of a permission class.
    It is used to store the permissions help by a role or in an ACL.
    """
    namespace = models.CharField(max_length=64, verbose_name=_('Namespace'))
    name = models.CharField(max_length=64, verbose_name=_('Name'))

    objects = StoredPermissionManager()

    class Meta:
        ordering = ('namespace',)
        unique_together = ('namespace', 'name')
        verbose_name = _('Permission')
        verbose_name_plural = _('Permissions')

    def __str__(self):
        try:
            return force_text(self.volatile_permission)
        except KeyError:
            return self.name

    @property
    def volatile_permission_id(self):
        """
        Return the identifier of the real permission class represented by
        this model instance.
        """
        return '{}.{}'.format(self.namespace, self.name)

    @property
    def volatile_permission(self):
        """
        Returns the real class of the permission represented by this model
        instance.
        """
        return Permission.get(
            pk=self.volatile_permission_id, proxy_only=True
        )

    def natural_key(self):
        return (self.namespace, self.name)

    def requester_has_this(self, user):
        """
        Helper method to check if an user has been granted this permission.
        The check is done sequentially over all of the user's groups and
        roles. The check is interrupted at the first positive result.
        The check always returns True for superusers or staff users.
        """
        if user.is_superuser or user.is_staff:
            logger.debug(
                'Permission "%s" granted to user "%s" as superuser or staff',
                self, user
            )
            return True

        # Request is one of the permission's holders?
        for group in user.groups.all():
            for role in group.roles.all():
                if self in role.permissions.all():
                    logger.debug(
                        'Permission "%s" granted to user "%s" through role "%s"',
                        self, user, role
                    )
                    return True

        logger.debug(
            'Fallthru: Permission "%s" not granted to user "%s"', self, user
        )
        return False


@python_2_unicode_compatible
class Role(models.Model):
    """
    This model represents a Role. Roles are permission units. They are the
    only object to which permissions can be granted. They are themselves
    containers too, containing Groups, which are organization units. Roles
    are the basic method to grant a permission to a group. Permissions granted
    to a group using a role, are granted for the entire system.
    """
    label = models.CharField(
        max_length=64, unique=True, verbose_name=_('Label')
    )
    permissions = models.ManyToManyField(
        related_name='roles', to=StoredPermission,
        verbose_name=_('Permissions')
    )
    groups = models.ManyToManyField(
        related_name='roles', to=Group, verbose_name=_('Groups')
    )

    objects = RoleManager()

    class Meta:
        ordering = ('label',)
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')

    def __str__(self):
        return self.label

    def get_absolute_url(self):
        return reverse('permissions:role_list')

    def natural_key(self):
        return (self.label,)
    natural_key.dependencies = ['auth.Group', 'permissions.StoredPermission']
