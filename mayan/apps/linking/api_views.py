from __future__ import absolute_import, unicode_literals

from django.shortcuts import get_object_or_404

from rest_framework import generics

from acls.models import AccessControlList
from documents.models import Document
from documents.permissions import permission_document_view
from rest_api.filters import MayanObjectPermissionsFilter
from rest_api.permissions import MayanPermission

from .models import SmartLink
from .permissions import (
    permission_smart_link_create, permission_smart_link_delete,
    permission_smart_link_edit, permission_smart_link_view
)
from .serializers import (
    ResolvedSmartLinkDocumentSerializer, ResolvedSmartLinkSerializer,
    SmartLinkConditionSerializer, SmartLinkSerializer,
    WritableSmartLinkSerializer
)


class APIResolvedSmartLinkDocumentListView(generics.ListAPIView):
    """
    get: Returns a list of the smart link documents that apply to the document.
    """
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {'GET': (permission_document_view,)}
    permission_classes = (MayanPermission,)
    serializer_class = ResolvedSmartLinkDocumentSerializer

    def get_document(self):
        document = get_object_or_404(Document, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_document_view, user=self.request.user,
            obj=document
        )

        return document

    def get_smart_link(self):
        smart_link = get_object_or_404(
            SmartLink.objects.get_for(document=self.get_document()),
            pk=self.kwargs['smart_link_pk']
        )

        AccessControlList.objects.check_access(
            permissions=permission_smart_link_view, user=self.request.user,
            obj=smart_link
        )

        return smart_link

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(APIResolvedSmartLinkDocumentListView, self).get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'document': self.get_document(),
                    'smart_link': self.get_smart_link(),
                }
            )

        return context

    def get_queryset(self):
        return self.get_smart_link().get_linked_document_for(
            document=self.get_document()
        )


class APIResolvedSmartLinkView(generics.RetrieveAPIView):
    """
    get: Return the details of the selected resolved smart link.
    """
    filter_backends = (MayanObjectPermissionsFilter,)
    lookup_url_kwarg = 'smart_link_pk'
    mayan_object_permissions = {'GET': (permission_smart_link_view,)}
    permission_classes = (MayanPermission,)
    serializer_class = ResolvedSmartLinkSerializer

    def get_document(self):
        document = get_object_or_404(Document, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_document_view, user=self.request.user,
            obj=document
        )

        return document

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(APIResolvedSmartLinkView, self).get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'document': self.get_document(),
                }
            )

        return context

    def get_queryset(self):
        return SmartLink.objects.get_for(document=self.get_document())


class APIResolvedSmartLinkListView(generics.ListAPIView):
    """
    get: Returns a list of the smart links that apply to the document.
    """
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {'GET': (permission_smart_link_view,)}
    permission_classes = (MayanPermission,)
    serializer_class = ResolvedSmartLinkSerializer

    def get_document(self):
        document = get_object_or_404(Document, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_document_view, user=self.request.user,
            obj=document
        )

        return document

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(APIResolvedSmartLinkListView, self).get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'document': self.get_document(),
                }
            )

        return context

    def get_queryset(self):
        return SmartLink.objects.filter(
            document_types=self.get_document().document_type
        )


class APISmartLinkConditionListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all the smart link conditions.
    post: Create a new smart link condition.
    """
    serializer_class = SmartLinkConditionSerializer

    def get_queryset(self):
        return self.get_smart_link().conditions.all()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(APISmartLinkConditionListView, self).get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'smart_link': self.get_smart_link(),
                }
            )

        return context

    def get_smart_link(self):
        if self.request.method == 'GET':
            permission_required = permission_smart_link_view
        else:
            permission_required = permission_smart_link_edit

        smart_link = get_object_or_404(SmartLink, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_required, user=self.request.user,
            obj=smart_link
        )

        return smart_link


class APISmartLinkConditionView(generics.RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the selected smart link condition.
    get: Return the details of the selected smart link condition.
    patch: Edit the selected smart link condition.
    put: Edit the selected smart link condition.
    """
    lookup_url_kwarg = 'condition_pk'
    serializer_class = SmartLinkConditionSerializer

    def get_queryset(self):
        return self.get_smart_link().conditions.all()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(APISmartLinkConditionView, self).get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'smart_link': self.get_smart_link(),
                }
            )

        return context

    def get_smart_link(self):
        if self.request.method == 'GET':
            permission_required = permission_smart_link_view
        else:
            permission_required = permission_smart_link_edit

        smart_link = get_object_or_404(SmartLink, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_required, user=self.request.user,
            obj=smart_link
        )

        return smart_link


class APISmartLinkListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all the smart links.
    post: Create a new smart link.
    """
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {'GET': (permission_smart_link_view,)}
    mayan_view_permissions = {'POST': (permission_smart_link_create,)}
    permission_classes = (MayanPermission,)
    queryset = SmartLink.objects.all()

    def get_serializer(self, *args, **kwargs):
        if not self.request:
            return None

        return super(APISmartLinkListView, self).get_serializer(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SmartLinkSerializer
        else:
            return WritableSmartLinkSerializer


class APISmartLinkView(generics.RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the selected smart link.
    get: Return the details of the selected smart link.
    patch: Edit the selected smart link.
    put: Edit the selected smart link.
    """
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {
        'DELETE': (permission_smart_link_delete,),
        'GET': (permission_smart_link_view,),
        'PATCH': (permission_smart_link_edit,),
        'PUT': (permission_smart_link_edit,)
    }
    queryset = SmartLink.objects.all()

    def get_serializer(self, *args, **kwargs):
        if not self.request:
            return None

        return super(APISmartLinkView, self).get_serializer(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SmartLinkSerializer
        else:
            return WritableSmartLinkSerializer
