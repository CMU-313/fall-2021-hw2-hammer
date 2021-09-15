from rest_framework.filters import BaseFilterBackend

from mayan.apps.acls.models import AccessControlList


class MayanObjectPermissionsFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        # TODO: fix variable name to make it clear it should be a single
        # permission

        required_permissions = getattr(
            view, 'mayan_object_permissions', {}
        ).get(request.method, None)

        if required_permissions:
            return AccessControlList.objects.restrict_queryset(
                queryset=queryset, permission=required_permissions[0],
                user=request.user
            )
        else:
            return queryset
