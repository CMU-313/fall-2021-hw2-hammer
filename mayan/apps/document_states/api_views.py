from __future__ import absolute_import, unicode_literals

from django.shortcuts import get_object_or_404

from rest_framework import generics

from acls.models import AccessControlList
from documents.models import Document, DocumentType
from documents.permissions import permission_document_type_view
from rest_api.filters import MayanObjectPermissionsFilter
from rest_api.permissions import MayanPermission

from .models import Workflow
from .permissions import (
    permission_workflow_create, permission_workflow_delete,
    permission_workflow_edit, permission_workflow_view
)
from .serializers import (
    NewWorkflowDocumentTypeSerializer, WorkflowDocumentTypeSerializer,
    WorkflowInstanceSerializer, WorkflowInstanceLogEntrySerializer,
    WorkflowSerializer, WorkflowStateSerializer, WorkflowTransitionSerializer,
    WritableWorkflowInstanceLogEntrySerializer, WritableWorkflowSerializer,
    WritableWorkflowTransitionSerializer
)


class APIDocumentTypeWorkflowListView(generics.ListAPIView):
    """
    get: Returns a list of all the document type workflows.
    """
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {
        'GET': (permission_workflow_view,),
    }
    serializer_class = WorkflowSerializer

    def get_document_type(self):
        document_type = get_object_or_404(DocumentType, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_document_type_view, user=self.request.user,
            obj=document_type
        )

        return document_type

    def get_queryset(self):
        return self.get_document_type().workflows.all()


class APIWorkflowDocumentTypeList(generics.ListCreateAPIView):
    """
    get: Returns a list of all the document types attached to a workflow.
    post: Attach a document type to a specified workflow.
    """
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {
        'GET': (permission_document_type_view,),
    }

    def get_queryset(self):
        """
        This view returns a list of document types that belong to a workflow.
        """
        return self.get_workflow().document_types.all()

    def get_serializer(self, *args, **kwargs):
        if not self.request:
            return None

        return super(APIWorkflowDocumentTypeList, self).get_serializer(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return WorkflowDocumentTypeSerializer
        elif self.request.method == 'POST':
            return NewWorkflowDocumentTypeSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(APIWorkflowDocumentTypeList, self).get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'workflow': self.get_workflow(),
                }
            )

        return context

    def get_workflow(self):
        """
        Retrieve the parent workflow of the workflow document type.
        Perform custom permission and access check.
        """
        if self.request.method == 'GET':
            permission_required = permission_workflow_view
        else:
            permission_required = permission_workflow_edit

        workflow = get_object_or_404(Workflow, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_required, user=self.request.user,
            obj=workflow
        )

        return workflow


class APIWorkflowDocumentTypeView(generics.RetrieveDestroyAPIView):
    """
    delete: Remove a document type from the selected workflow.
    get: Returns the details of the selected workflow document type.
    """
    filter_backends = (MayanObjectPermissionsFilter,)
    lookup_url_kwarg = 'document_type_pk'
    mayan_object_permissions = {
        'GET': (permission_document_type_view,),
    }
    serializer_class = WorkflowDocumentTypeSerializer

    def get_queryset(self):
        return self.get_workflow().document_types.all()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(APIWorkflowDocumentTypeView, self).get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'workflow': self.get_workflow(),
                }
            )

        return context

    def get_workflow(self):
        """
        This view returns a document types that belongs to a workflow
        RESEARCH: Could the documents.api_views.APIDocumentTypeView class
        be subclasses for this?
        RESEARCH: Since this is a parent-child API view could this be made
        into a generic API class?
        RESEARCH: Reuse get_workflow method from APIWorkflowDocumentTypeList?
        """
        if self.request.method == 'GET':
            permission_required = permission_workflow_view
        else:
            permission_required = permission_workflow_edit

        workflow = get_object_or_404(Workflow, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_required, user=self.request.user,
            obj=workflow
        )

        return workflow

    def perform_destroy(self, instance):
        """
        RESEARCH: Move this kind of methods to the serializer instead it that
        ability becomes available in Django REST framework
        """
        self.get_workflow().document_types.remove(instance)


class APIWorkflowListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all the workflows.
    post: Create a new workflow.
    """
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {'GET': (permission_workflow_view,)}
    mayan_view_permissions = {'POST': (permission_workflow_create,)}
    permission_classes = (MayanPermission,)
    queryset = Workflow.objects.all()

    def get_serializer(self, *args, **kwargs):
        if not self.request:
            return None

        return super(APIWorkflowListView, self).get_serializer(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return WorkflowSerializer
        else:
            return WritableWorkflowSerializer


class APIWorkflowView(generics.RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the selected workflow.
    get: Return the details of the selected workflow.
    patch: Edit the selected workflow.
    put: Edit the selected workflow.
    """
    filter_backends = (MayanObjectPermissionsFilter,)
    mayan_object_permissions = {
        'DELETE': (permission_workflow_delete,),
        'GET': (permission_workflow_view,),
        'PATCH': (permission_workflow_edit,),
        'PUT': (permission_workflow_edit,)
    }
    queryset = Workflow.objects.all()

    def get_serializer(self, *args, **kwargs):
        if not self.request:
            return None

        return super(APIWorkflowView, self).get_serializer(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return WorkflowSerializer
        else:
            return WritableWorkflowSerializer


# Workflow state views


class APIWorkflowStateListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all the workflow states.
    post: Create a new workflow state.
    """
    serializer_class = WorkflowStateSerializer

    def get_queryset(self):
        return self.get_workflow().states.all()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(APIWorkflowStateListView, self).get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'workflow': self.get_workflow(),
                }
            )

        return context

    def get_workflow(self):
        if self.request.method == 'GET':
            permission_required = permission_workflow_view
        else:
            permission_required = permission_workflow_edit

        workflow = get_object_or_404(Workflow, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_required, user=self.request.user,
            obj=workflow
        )

        return workflow


class APIWorkflowStateView(generics.RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the selected workflow state.
    get: Return the details of the selected workflow state.
    patch: Edit the selected workflow state.
    put: Edit the selected workflow state.
    """
    lookup_url_kwarg = 'state_pk'
    serializer_class = WorkflowStateSerializer

    def get_queryset(self):
        return self.get_workflow().states.all()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(APIWorkflowStateView, self).get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'workflow': self.get_workflow(),
                }
            )

        return context

    def get_workflow(self):
        if self.request.method == 'GET':
            permission_required = permission_workflow_view
        else:
            permission_required = permission_workflow_edit

        workflow = get_object_or_404(Workflow, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_required, user=self.request.user,
            obj=workflow
        )

        return workflow


# Workflow transition views


class APIWorkflowTransitionListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all the workflow transitions.
    post: Create a new workflow transition.
    """
    def get_queryset(self):
        return self.get_workflow().transitions.all()

    def get_serializer(self, *args, **kwargs):
        if not self.request:
            return None

        return super(APIWorkflowTransitionListView, self).get_serializer(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return WorkflowTransitionSerializer
        else:
            return WritableWorkflowTransitionSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(APIWorkflowTransitionListView, self).get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'workflow': self.get_workflow(),
                }
            )

        return context

    def get_workflow(self):
        if self.request.method == 'GET':
            permission_required = permission_workflow_view
        else:
            permission_required = permission_workflow_edit

        workflow = get_object_or_404(Workflow, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_required, user=self.request.user,
            obj=workflow
        )

        return workflow


class APIWorkflowTransitionView(generics.RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the selected workflow transition.
    get: Return the details of the selected workflow transition.
    patch: Edit the selected workflow transition.
    put: Edit the selected workflow transition.
    """
    lookup_url_kwarg = 'transition_pk'

    def get_queryset(self):
        return self.get_workflow().transitions.all()

    def get_serializer(self, *args, **kwargs):
        if not self.request:
            return None

        return super(APIWorkflowTransitionView, self).get_serializer(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return WorkflowTransitionSerializer
        else:
            return WritableWorkflowTransitionSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(APIWorkflowTransitionView, self).get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'workflow': self.get_workflow(),
                }
            )

        return context

    def get_workflow(self):
        if self.request.method == 'GET':
            permission_required = permission_workflow_view
        else:
            permission_required = permission_workflow_edit

        workflow = get_object_or_404(Workflow, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_required, user=self.request.user,
            obj=workflow
        )

        return workflow


# Document workflow views


class APIWorkflowInstanceListView(generics.ListAPIView):
    """
    get: Returns a list of all the document workflows.
    """
    filter_backends = (MayanObjectPermissionsFilter,)
    serializer_class = WorkflowInstanceSerializer
    mayan_object_permissions = {
        'GET': (permission_workflow_view,),
    }

    def get_document(self):
        document = get_object_or_404(Document, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_workflow_view, user=self.request.user,
            obj=document
        )

        return document

    def get_queryset(self):
        return self.get_document().workflows.all()


class APIWorkflowInstanceView(generics.RetrieveAPIView):
    """
    get: Return the details of the selected document workflow.
    """
    filter_backends = (MayanObjectPermissionsFilter,)
    lookup_url_kwarg = 'workflow_pk'
    mayan_object_permissions = {
        'GET': (permission_workflow_view,),
    }
    serializer_class = WorkflowInstanceSerializer

    def get_document(self):
        document = get_object_or_404(Document, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_workflow_view, user=self.request.user,
            obj=document
        )

        return document

    def get_queryset(self):
        return self.get_document().workflows.all()


class APIWorkflowInstanceLogEntryListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all the document workflows log entries.
    post: Transition a document workflow by creating a new document workflow log entry.
    """
    def get_document(self):
        document = get_object_or_404(Document, pk=self.kwargs['pk'])

        if self.request.method == 'GET':
            """
            Only test for permission if reading. If writing, the permission
            will be checked in the serializer

            IMPROVEMENT:
            When writing, add check for permission or ACL for the workflow.
            Failing that, check for ACLs for any of the workflow's transitions.
            Failing that, then raise PermissionDenied
            """
            AccessControlList.objects.check_access(
                permissions=permission_workflow_view, user=self.request.user,
                obj=document
            )

        return document

    def get_serializer(self, *args, **kwargs):
        if not self.request:
            return None

        return super(APIWorkflowInstanceLogEntryListView, self).get_serializer(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return WorkflowInstanceLogEntrySerializer
        else:
            return WritableWorkflowInstanceLogEntrySerializer

    def get_serializer_context(self):
        context = super(APIWorkflowInstanceLogEntryListView, self).get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'workflow_instance': self.get_workflow_instance(),
                }
            )

        return context

    def get_queryset(self):
        return self.get_workflow_instance().log_entries.all()

    def get_workflow_instance(self):
        workflow = get_object_or_404(
            self.get_document().workflows, pk=self.kwargs['workflow_pk']
        )

        return workflow
