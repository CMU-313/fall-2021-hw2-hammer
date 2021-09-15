from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions import PermissionNamespace

namespace = PermissionNamespace(label=_('OCR'), name='ocr')

permission_document_version_ocr = namespace.add_permission(
    label=_('Submit documents for OCR'), name='ocr_document'
)
permission_document_version_ocr_content_view = namespace.add_permission(
    label=_('View the transcribed text from document'),
    name='ocr_content_view'
)
permission_document_type_ocr_setup = namespace.add_permission(
    label=_('Change document type OCR settings'),
    name='ocr_document_type_setup'
)
