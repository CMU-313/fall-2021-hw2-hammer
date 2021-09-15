import logging

from django.apps import apps
from django.contrib.auth.models import Group
from django.db import models
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.events.classes import EventManagerSave
from mayan.apps.events.decorators import method_event
from mayan.apps.user_management.permissions import permission_group_view

from .classes import Permission
from .events import event_role_created, event_role_edited
from .managers import RoleManager, StoredPermissionManager

logger = logging.getLogger(name=__name__)


class Role(ExtraDataModelMixin, models.Model):
    """
    This model represents a Role. Roles are permission units. They are the
    only object to which permissions can be granted. They are themselves
    containers too, containing Groups, which are organization units. Roles
    are the basic method to grant a permission to a group. Permissions granted
    to a group using a role, are granted for the entire system.
    """
    label = models.CharField(
        help_text=_('A short text describing the role.'), max_length=128,
        unique=True, verbose_name=_('Label')
    )
    permissions = models.ManyToManyField(
        related_name='roles', to='StoredPermission',
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
        return reverse(viewname='permissions:role_list')

    def get_group_count(self, user):
        """
        Return the numeric count of groups that have this role contains.
        The count is filtered by access.
        """
        return self.get_groups(user=user).count()

    def get_groups(self, user):
        """
        Return a filtered queryset groups that have this role contains.
        """
        AccessControlList = apps.get_model(
            app_label='acls', model_name='AccessControlList'
        )

        return AccessControlList.objects.restrict_queryset(
            permission=permission_group_view, queryset=self.groups.all(),
            user=user
        )
    get_group_count.short_description = _('Group count')

    def get_permission_count(self):
        """
        Return the numeric count of permissions that have this role
        has granted. The count is filtered by access.
        """
        return self.permissions.count()
    get_permission_count.short_description = _('Permission count')

    def grant(self, permission):
        self.permissions.add(permission.stored_permission)

    def groups_add(self, queryset, _event_actor=None):
        for obj in queryset:
            self.groups.add(obj)
            event_role_edited.commit(
                action_object=obj, actor=_event_actor or self._event_actor,
                target=self
            )

    def groups_remove(self, queryset, _event_actor=None):
        for obj in queryset:
            self.groups.remove(obj)
            event_role_edited.commit(
                action_object=obj, actor=_event_actor or self._event_actor,
                target=self
            )

    def natural_key(self):
        return (self.label,)
    natural_key.dependencies = ['auth.Group', 'permissions.StoredPermission']

    def permissions_add(self, queryset, _event_actor=None):
        for obj in queryset:
            self.permissions.add(obj)
            event_role_edited.commit(
                action_object=obj, actor=_event_actor or self._event_actor,
                target=self
            )

    def permissions_remove(self, queryset, _event_actor=None):
        for obj in queryset:
            self.permissions.remove(obj)
            event_role_edited.commit(
                action_object=obj, actor=_event_actor or self._event_actor,
                target=self
            )

    def revoke(self, permission):
        self.permissions.remove(permission.stored_permission)

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'event': event_role_created,
            'target': 'self',
        },
        edited={
            'event': event_role_edited,
            'target': 'self',
        }
    )
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


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
            return force_text(s=self.volatile_permission)
        except KeyError:
            return self.name

    @cached_property
    def volatile_permission_id(self):
        """
        Return the identifier of the real permission class represented by
        this model instance.
        """
        return '{}.{}'.format(self.namespace, self.name)

    @cached_property
    def volatile_permission(self):
        """
        Returns the real class of the permission represented by this model
        instance.
        """
        return Permission.get(
            pk=self.volatile_permission_id, class_only=True
        )

    def natural_key(self):
        return (self.namespace, self.name)

    def user_has_this(self, user):
        """
        Helper method to check if a user has been granted this permission.
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

        if not user.is_authenticated:
            return False

        if Role.objects.filter(groups__user=user, permissions=self).exists():
            return True
        else:
            logger.debug(
                'Fallthru: Permission "%s" not granted to user "%s"', self, user
            )
            return False
