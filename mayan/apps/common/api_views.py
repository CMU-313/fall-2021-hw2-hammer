from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .classes import Template
from .serializers import ContentTypeSerializer, TemplateSerializer


class APIContentTypeList(generics.ListAPIView):
    """
    Returns a list of all the available content types.
    """
    serializer_class = ContentTypeSerializer
    queryset = ContentType.objects.order_by('app_label', 'model')


class APITemplateListView(generics.ListAPIView):
    """
    Returns a list of partial templates.
    get: Returns a list of partial templates.
    """
    serializer_class = TemplateSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Template.all(rendered=True, request=self.request)


class APITemplateView(generics.RetrieveAPIView):
    """
    Returns the selected partial template details.
    get: Retrieve the details of the partial template.
    """
    serializer_class = TemplateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return Template.get(name=self.kwargs['name']).render(
            request=self.request
        )
