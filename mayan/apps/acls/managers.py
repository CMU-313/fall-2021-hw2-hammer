from functools import reduce
import logging
import operator

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import CharField, Q, Value
from django.db.models.functions import Cast, Concat
from django.utils.encoding import force_text
from django.utils.translation import ugettext

from mayan.apps.common.utils import (
    get_related_field, resolve_attribute, return_related
)
from mayan.apps.permissions import Permission
from mayan.apps.permissions.models import StoredPermission

from .exceptions import PermissionNotValidForClass
from .classes import ModelPermission

logger = logging.getLogger(name=__name__)


class AccessControlListManager(models.Manager):
    """
    Implement a 3 tier permission system, involving a permissions, an actor
    and an object
    """
    def _get_acl_filters(
        self, queryset, stored_permission, user, fk_field_cast=None,
        related_field_name=None
    ):
        """
        This method does the bulk of the work. It generates filters for the
        AccessControlList model to determine if there are ACL entries for the
        members of the queryset's model provided.
        """
        # Determine which of the cases we need to address:
        # 1: No related field
        # 2: Related field
        # 3: Related field that is Generic Foreign Key
        # 4: No related field, but has an inherited related field, solved by
        # recursion, branches to #2 or #3.
        # 5: Inherited field of a related field
        # 6: Inherited field of a related field that is Generic Foreign Key
        # -- Not addressed yet --
        # 7: Has a related function
        result = []

        if related_field_name:
            related_field = get_related_field(
                model=queryset.model, related_field_name=related_field_name
            )

            if isinstance(related_field, GenericForeignKey):
                # Case 3: Generic Foreign Key, multiple ContentTypes + object
                # id combinations.
                # Also handles case #6 using the parent related field
                # reference template.

                # Craft a double underscore reference to a previous related
                # field in the case where multiple related fields are
                # associated.
                # Example: object_layer__content_type
                recursive_related_reference = '__'.join(related_field_name.split('__')[0:-1])

                # If there is at least one parent related field we add a
                # double underscore to make it a valid filter template.
                if recursive_related_reference:
                    recursive_related_reference = '{}__'.format(recursive_related_reference)

                content_type_object_id_queryset = queryset.annotate(
                    ct_fk_combination=Concat(
                        '{}{}'.format(
                            recursive_related_reference, related_field.ct_field
                        ), Value('-'),
                        '{}{}'.format(
                            recursive_related_reference, related_field.fk_field
                        ), output_field=CharField()
                    )
                ).values('ct_fk_combination')

                acl_filter = self.annotate(
                    ct_fk_combination=Concat(
                        'content_type', Value('-'), 'object_id',
                        output_field=CharField()
                    )
                ).filter(
                    permissions=stored_permission, role__groups__user=user,
                    ct_fk_combination__in=content_type_object_id_queryset
                )

                if fk_field_cast:
                    clean_acl_filter = acl_filter.annotate(
                        clean_object_id=Cast(
                            'object_id', output_field=fk_field_cast()
                        )
                    ).values_list('clean_object_id')
                else:
                    clean_acl_filter = acl_filter.values('object_id')

                field_lookup = '{}{}__in'.format(
                    recursive_related_reference, related_field.fk_field
                )
                result.append(Q(**{field_lookup: clean_acl_filter}))
            else:
                # Case 2: Related field of a single type, single ContentType,
                # multiple object id.
                content_type = ContentType.objects.get_for_model(
                    model=related_field.related_model
                )
                field_lookup = '{}_id__in'.format(related_field_name)
                acl_filter = self.filter(
                    content_type=content_type, permissions=stored_permission,
                    role__groups__user=user
                ).values('object_id')
                # Don't add empty filters otherwise the default AND operator
                # of the Q object will return an empty queryset when reduced
                # and filter out objects that should be in the final queryset.
                if acl_filter:
                    result.append(Q(**{field_lookup: acl_filter}))

                # Case 5: Related field, has an inherited related field itself
                # Bubble up permission check.
                # Recurse and reduce.
                try:
                    related_field_model_inheritances = (
                        ModelPermission.get_inheritances(
                            model=related_field.related_model
                        )
                    )
                except KeyError:
                    pass
                else:
                    relation_result = []
                    for related_field_model_inheritance in related_field_model_inheritances:
                        new_related_field_name = '{}__{}'.format(related_field_name, related_field_model_inheritance['field_name'])
                        related_field_inherited_acl_queries = self._get_acl_filters(
                            fk_field_cast=related_field_model_inheritance['fk_field_cast'],
                            queryset=queryset,
                            stored_permission=stored_permission, user=user,
                            related_field_name=new_related_field_name
                        )
                        if related_field_inherited_acl_queries:
                            relation_result.append(
                                reduce(
                                    operator.and_,
                                    related_field_inherited_acl_queries
                                )
                            )

                    if relation_result:
                        result.append(reduce(operator.or_, relation_result))
        else:
            # Case 1: Original model, single ContentType, multiple object id.
            content_type = ContentType.objects.get_for_model(
                model=queryset.model
            )
            field_lookup = 'id__in'
            acl_filter = self.filter(
                content_type=content_type, permissions=stored_permission,
                role__groups__user=user
            ).values('object_id')
            result.append(Q(**{field_lookup: acl_filter}))

            # Case 4: Original model, has an inherited related field.
            try:
                inheritances = (
                    ModelPermission.get_inheritances(
                        model=queryset.model
                    )
                )
            except KeyError:
                """
                Does not have inheritance entries. Proceed to next case.
                """
            else:
                relation_result = []

                for inheritance in inheritances:
                    inherited_acl_queries = self._get_acl_filters(
                        fk_field_cast=inheritance['fk_field_cast'],
                        queryset=queryset, stored_permission=stored_permission,
                        related_field_name=inheritance['field_name'], user=user
                    )
                    if inherited_acl_queries:
                        relation_result.append(
                            reduce(operator.and_, inherited_acl_queries)
                        )

                if relation_result:
                    result.append(reduce(operator.or_, relation_result))

            # Case 7: Has a function.
            try:
                field_query_function = ModelPermission.get_field_query_function(
                    model=queryset.model
                )
            except KeyError:
                pass
            else:
                function_results = field_query_function()

                # Filter by the model's content type.
                content_type = ContentType.objects.get_for_model(
                    model=queryset.model
                )
                acl_filter = self.filter(
                    content_type=content_type, permissions=stored_permission,
                    role__groups__user=user
                ).values('object_id')

                # Obtain a queryset of filtered, authorized model instances.
                acl_queryset = queryset.model._meta.default_manager.filter(
                    id__in=acl_filter
                ).filter(**function_results['acl_filter'])

                if 'acl_values' in function_results:
                    acl_queryset = acl_queryset.values(
                        *function_results['acl_values']
                    )

                # Get the final query using the filtered queryset as the
                # reference.
                result.append(
                    Q(**{function_results['field_lookup']: acl_queryset})
                )

        return result

    def check_access(self, obj, permissions, user):
        # Allow specific managers for models that have more than one
        # for example the Document model when checking for access for a trashed
        # document.

        meta = getattr(obj, '_meta', None)

        if not meta:
            logger.debug(
                ugettext(
                    'Object "%s" is not a model and cannot be checked for '
                    'access.'
                ) % force_text(s=obj)
            )
            return True
        else:
            manager = ModelPermission.get_manager(model=obj._meta.model)
            source_queryset = manager.all()

        restricted_queryset = manager.none()
        for permission in permissions:
            # Default relationship betweens permissions is OR.
            restricted_queryset = restricted_queryset | self.restrict_queryset(
                permission=permission, queryset=source_queryset, user=user
            )

        if restricted_queryset.filter(pk=obj.pk).exists():
            return True
        else:
            raise PermissionDenied(
                ugettext(message='Insufficient access for: %s') % force_text(
                    s=obj
                )
            )

    def restrict_queryset(self, permission, queryset, user):
        if not user.is_authenticated:
            return queryset.none()

        # Check directly granted permission via a role
        try:
            Permission.check_user_permissions(
                permissions=(permission,), user=user
            )
        except PermissionDenied:
            acl_filters = self._get_acl_filters(
                queryset=queryset,
                stored_permission=permission.stored_permission, user=user
            )

            final_query = None
            for acl_filter in acl_filters:
                if final_query is None:
                    final_query = acl_filter
                else:
                    final_query = final_query | acl_filter

            return queryset.filter(final_query)
        else:
            # User has direct permission assignment via a role, is superuser
            # or is staff. Return the entire queryset.
            return queryset

    def get_inherited_permissions(self, obj, role):
        # Get permission inherited from a related object's ACLs.
        queryset = self._get_inherited_object_permissions(obj=obj, role=role)

        # Get permission granted to the role
        queryset = queryset | role.permissions.all()

        # Filter the permissions to the ones that apply to the model.
        queryset = ModelPermission.get_for_instance(
            instance=obj
        ).filter(
            pk__in=queryset
        )

        return queryset

    def _get_inherited_object_permissions(self, obj, role):
        queryset = StoredPermission.objects.none()

        if not obj:
            return queryset

        try:
            inheritances = ModelPermission.get_inheritances(
                model=type(obj)
            )
        except KeyError:
            """
            Does not have inheritance to other models.
            """
        else:
            for inheritance in inheritances:
                try:
                    parent_object = resolve_attribute(
                        obj=obj, attribute=inheritance['field_name']
                    )
                except AttributeError:
                    # Parent accessor is not an attribute, try it as a related
                    # field.
                    parent_object = return_related(
                        instance=obj, related_field=inheritance['field_name']
                    )
                content_type = ContentType.objects.get_for_model(
                    model=parent_object
                )
                try:
                    queryset = queryset | self.get(
                        content_type=content_type, object_id=parent_object.pk,
                        role=role
                    ).permissions.all()
                except self.model.DoesNotExist:
                    pass

                if type(parent_object) == type(obj):
                    # Object and parent are of the same type. Break recursion.
                    return queryset
                else:
                    queryset = queryset | self._get_inherited_object_permissions(
                        obj=parent_object, role=role
                    )

        return queryset

    def grant(self, permission, role, obj):
        class_permissions = ModelPermission.get_for_class(klass=obj.__class__)
        if permission not in class_permissions:
            raise PermissionNotValidForClass

        content_type = ContentType.objects.get_for_model(model=obj)
        acl, created = self.get_or_create(
            content_type=content_type, object_id=obj.pk,
            role=role
        )

        acl.permissions.add(permission.stored_permission)

    def revoke(self, permission, role, obj):
        content_type = ContentType.objects.get_for_model(model=obj)
        acl, created = self.get_or_create(
            content_type=content_type, object_id=obj.pk,
            role=role
        )

        acl.permissions.remove(permission.stored_permission)

        if acl.permissions.count() == 0:
            acl.delete()
