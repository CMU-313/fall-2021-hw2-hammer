from __future__ import unicode_literals

import json
import logging

from jinja2 import Template

from django.contrib.sites.models import Site
from django.core import mail
from django.db import models
from django.utils.html import strip_tags
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from .managers import UserMailerManager
from .utils import split_recipient_list

logger = logging.getLogger(__name__)


class LogEntry(models.Model):
    datetime = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name=_('Date and time')
    )
    message = models.TextField(
        blank=True, editable=False, verbose_name=_('Message')
    )

    class Meta:
        get_latest_by = 'datetime'
        ordering = ('-datetime',)
        verbose_name = _('Log entry')
        verbose_name_plural = _('Log entries')


class UserMailer(models.Model):
    """
    This model is used to create mailing profiles that can be used from inside
    the system. These profiles differ from the system mailing profile in that
    they can be created at runtime and can be assigned ACLs to restrict
    their use.
    """
    label = models.CharField(
        max_length=128, unique=True, verbose_name=_('Label')
    )
    default = models.BooleanField(
        default=True, help_text=_(
            'If default, this mailing profile will be pre-selected on the '
            'document mailing form.'
        ), verbose_name=_('Default')
    )
    enabled = models.BooleanField(default=True, verbose_name=_('Enabled'))
    backend_path = models.CharField(
        max_length=128,
        help_text=_('The dotted Python path to the backend class.'),
        verbose_name=_('Backend path')
    )
    backend_data = models.TextField(
        blank=True, verbose_name=_('Backend data')
    )

    objects = UserMailerManager()

    class Meta:
        ordering = ('label',)
        verbose_name = _('User mailer')
        verbose_name_plural = _('User mailers')

    def __str__(self):
        return self.label

    def backend_label(self):
        """
        Return the label that the backend itself provides. The backend is
        loaded but not initialized. As such the label returned is a class
        property.
        """
        return self.get_backend().label
    backend_label.short_description = _('Backend label')

    def dumps(self, data):
        """
        Serialize the backend configuration data.
        """
        self.backend_data = json.dumps(data)
        self.save()

    def get_class_data(self):
        """
        Return the actual mailing class initialization data
        """
        backend = self.get_backend()
        return {
            key: value for key, value in self.loads().items() if key in backend.get_class_fields()
        }

    def get_backend(self):
        """
        Retrieves the backend by importing the module and the class
        """
        return import_string(self.backend_path)

    def get_connection(self):
        """
        Establishes a reusable connection to the server by loading the
        backend, initializing it, and the using the backend instance to get
        a connection.
        """
        return mail.get_connection(
            backend=self.get_backend().class_path, **self.get_class_data()
        )

    def loads(self):
        """
        Deserialize the stored backend data.
        """
        return json.loads(self.backend_data)

    def natural_key(self):
        return (self.label,)

    def save(self, *args, **kwargs):
        if self.default:
            UserMailer.objects.select_for_update().exclude(pk=self.pk).update(
                default=False
            )

        return super(UserMailer, self).save(*args, **kwargs)

    def send(self, to, subject='', body='', attachments=None):
        """
        Send a simple email. There is no document or template knowledge.
        attachments is a list of dictionaries with the keys:
        filename, content, and  mimetype.
        """
        recipient_list = split_recipient_list(recipients=[to])
        backend_data = self.loads()

        with self.get_connection() as connection:
            email_message = mail.EmailMultiAlternatives(
                body=strip_tags(body), connection=connection,
                from_email=backend_data.get('from'), subject=subject,
                to=recipient_list,
            )

            for attachment in attachments or []:
                email_message.attach(
                    filename=attachment['filename'],
                    content=attachment['content'],
                    mimetype=attachment['mimetype']
                )

            email_message.attach_alternative(body, 'text/html')

            try:
                email_message.send()
            except Exception as exception:
                self.error_log.create(message=exception)
            else:
                self.error_log.all().delete()

    def send_document(self, document, to, subject='', body='', as_attachment=False):
        """
        Send a document using this user mailing profile.
        """
        context_dictionary = {
            'link': 'http://%s%s' % (
                Site.objects.get_current().domain,
                document.get_absolute_url()
            ),
            'document': document
        }

        body_template = Template(body)
        body_html_content = body_template.render(**context_dictionary)

        subject_template = Template(subject)
        subject_text = strip_tags(subject_template.render(**context_dictionary))

        attachments = []
        if as_attachment:
            with document.open() as file_object:
                attachments.append(
                    {
                        'content': file_object.read(),
                        'filename': document.label,
                        'mimetype': document.file_mimetype
                    }
                )

        return self.send(
            attachments=attachments, body=body_html_content,
            subject=subject_text, to=to,
        )

    def test(self, to):
        """
        Send a test message to make sure the mailing profile settings are
        correct.
        """
        self.send(subject=_('Test email from Mayan EDMS'), to=to)


class UserMailerLogEntry(models.Model):
    user_mailer = models.ForeignKey(
        on_delete=models.CASCADE, related_name='error_log', to=UserMailer,
        verbose_name=_('User mailer')
    )
    datetime = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name=_('Date time')
    )
    message = models.TextField(
        blank=True, editable=False, verbose_name=_('Message')
    )

    class Meta:
        get_latest_by = 'datetime'
        ordering = ('-datetime',)
        verbose_name = _('User mailer log entry')
        verbose_name_plural = _('User mailer log entries')
