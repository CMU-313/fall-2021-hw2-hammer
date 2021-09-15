from django.db import migrations


def operation_move_from_content_type_user_to_foreign_key_field_user(apps, schema_editor):
    # The model references the use who checked out the document using a
    # generic.GenericForeignKey. This migrations changes that to a simpler
    # ForeignKey to the User model

    DocumentCheckout = apps.get_model(
        app_label='checkouts', model_name='DocumentCheckout'
    )

    for document_checkout in DocumentCheckout.objects.using(alias=schema_editor.connection.alias).all():
        document_checkout.user = document_checkout.user_object
        document_checkout.save()


class Migration(migrations.Migration):
    dependencies = [
        ('checkouts', '0002_documentcheckout_user'),
    ]

    operations = [
        migrations.RunPython(
            code=operation_move_from_content_type_user_to_foreign_key_field_user
        ),
    ]
