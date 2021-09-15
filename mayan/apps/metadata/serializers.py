from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.serializers import (
    DocumentSerializer, DocumentTypeSerializer
)

from .models import DocumentMetadata, DocumentTypeMetadataType, MetadataType
from .permissions import permission_document_metadata_add


class MetadataTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_field': 'pk', 'lookup_url_kwarg': 'metadata_type_pk',
                'view_name': 'rest_api:metadatatype-detail'
            },
        }
        fields = (
            'default', 'id', 'label', 'lookup', 'name', 'parser', 'url',
            'validation'
        )
        model = MetadataType


class DocumentTypeMetadataTypeSerializer(serializers.HyperlinkedModelSerializer):
    document_type = DocumentTypeSerializer(read_only=True)
    metadata_type = MetadataTypeSerializer(read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        fields = ('document_type', 'id', 'metadata_type', 'required', 'url')
        model = DocumentTypeMetadataType

    def get_url(self, instance):
        return reverse(
            'rest_api:documenttypemetadatatype-detail', args=(
                instance.document_type.pk, instance.pk
            ), request=self.context['request'], format=self.context['format']
        )


class NewDocumentTypeMetadataTypeSerializer(serializers.ModelSerializer):
    metadata_type_pk = serializers.IntegerField(
        help_text=_('Primary key of the metadata type to be added.'),
        write_only=True
    )
    url = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'metadata_type_pk', 'required', 'url'
        )
        model = DocumentTypeMetadataType

    def get_url(self, instance):
        return reverse(
            'rest_api:documenttypemetadatatype-detail', args=(
                instance.document_type.pk, instance.pk
            ), request=self.context['request'], format=self.context['format']
        )

    def validate(self, attrs):
        attrs['document_type'] = self.context['document_type']
        attrs['metadata_type'] = MetadataType.objects.get(
            pk=attrs.pop('metadata_type_pk')
        )

        instance = DocumentTypeMetadataType(**attrs)
        try:
            instance.full_clean()
        except DjangoValidationError as exception:
            raise ValidationError(exception)

        return attrs


class WritableDocumentTypeMetadataTypeSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'required', 'url'
        )
        model = DocumentTypeMetadataType

    def get_url(self, instance):
        return reverse(
            'rest_api:documenttypemetadatatype-detail', args=(
                instance.document_type.pk, instance.pk
            ), request=self.context['request'], format=self.context['format']
        )


class DocumentMetadataSerializer(serializers.HyperlinkedModelSerializer):
    document = DocumentSerializer(read_only=True)
    metadata_type = MetadataTypeSerializer(read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        fields = ('document', 'id', 'metadata_type', 'url', 'value')
        model = DocumentMetadata
        read_only_fields = ('document', 'metadata_type',)

    def get_url(self, instance):
        return reverse(
            'rest_api:documentmetadata-detail', args=(
                instance.document.pk, instance.pk
            ), request=self.context['request'], format=self.context['format']
        )

    def validate(self, attrs):
        self.instance.value = attrs['value']

        try:
            self.instance.full_clean()
        except DjangoValidationError as exception:
            raise ValidationError(exception)

        attrs['value'] = self.instance.value

        return attrs


class NewDocumentMetadataSerializer(serializers.ModelSerializer):
    metadata_type_pk = serializers.IntegerField(
        help_text=_(
            'Primary key of the metadata type to be added to the document.'
        ),
        write_only=True
    )
    url = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'metadata_type_pk', 'url', 'value')
        model = DocumentMetadata

    def create(self, validated_data):
        queryset = AccessControlList.objects.restrict_queryset(
            queryset=MetadataType.objects.all(),
            permission=permission_document_metadata_add,
            user=self.context['request'].user
        )
        get_object_or_404(
            klass=queryset, pk=validated_data['metadata_type'].pk
        )

        return super(NewDocumentMetadataSerializer, self).create(
            validated_data=validated_data
        )

    def get_url(self, instance):
        return reverse(
            'rest_api:documentmetadata-detail', args=(
                instance.document.pk, instance.pk
            ), request=self.context['request'], format=self.context['format']
        )

    def validate(self, attrs):
        attrs['document'] = self.context['document']
        attrs['metadata_type'] = MetadataType.objects.get(
            pk=attrs.pop('metadata_type_pk')
        )

        instance = DocumentMetadata(**attrs)
        try:
            instance.full_clean()
        except DjangoValidationError as exception:
            raise ValidationError(exception)

        attrs['value'] = instance.value

        return attrs
