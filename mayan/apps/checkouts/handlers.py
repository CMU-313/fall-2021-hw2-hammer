from django.apps import apps

from .exceptions import NewDocumentVersionNotAllowed


def handler_check_new_version_creation(sender, instance, **kwargs):
    """
    Make sure that new version creation is allowed for this document
    """
    NewVersionBlock = apps.get_model(
        app_label='checkouts', model_name='NewVersionBlock'
    )
    if NewVersionBlock.objects.is_blocked(document=instance.document) and not instance.pk:
        # Block only new versions (no pk), not existing version being updated.
        raise NewDocumentVersionNotAllowed
