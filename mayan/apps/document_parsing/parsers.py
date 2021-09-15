import logging
import os
from shutil import copyfileobj
import subprocess

from django.apps import apps
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from mayan.apps.storage.utils import NamedTemporaryFile

from .exceptions import ParserError
from .settings import setting_pdftotext_path

logger = logging.getLogger(name=__name__)


class Parser:
    """
    Parser base class
    """
    _registry = {}

    @classmethod
    def parse_document_file_page(cls, document_file_page):
        for parser_class in cls._registry.get(document_file_page.document_file.mimetype, ()):
            try:
                parser = parser_class()
                parser.process_document_file_page(document_file_page)
            except ParserError:
                # If parser raises error, try next parser in the list
                pass
            else:
                # If parser was successfull there is no need to try
                # others in the list for this mimetype
                return

    @classmethod
    def parse_document_file(cls, document_file):
        for parser_class in cls._registry.get(document_file.mimetype, ()):
            try:
                parser = parser_class()
                parser.process_document_file(document_file)
            except ParserError:
                # If parser raises error, try next parser in the list
                pass
            else:
                # If parser was successfull there is no need to try
                # others in the list for this mimetype
                return

    @classmethod
    def register(cls, mimetypes, parser_classes):
        for mimetype in mimetypes:
            for parser_class in parser_classes:
                cls._registry.setdefault(
                    mimetype, []
                ).append(parser_class)

    def process_document_file(self, document_file):
        logger.info(
            'Starting parsing for document file: %s', document_file
        )
        logger.debug('document file: %d', document_file.pk)

        for document_file_page in document_file.pages.all():
            self.process_document_file_page(document_file_page=document_file_page)

    def process_document_file_page(self, document_file_page):
        DocumentFilePageContent = apps.get_model(
            app_label='document_parsing', model_name='DocumentFilePageContent'
        )

        logger.info(
            'Processing page: %d of document file: %s',
            document_file_page.page_number, document_file_page.document_file
        )

        file_object = document_file_page.document_file.get_intermediate_file()

        try:
            document_file_page_content, created = DocumentFilePageContent.objects.get_or_create(
                document_file_page=document_file_page
            )
            document_file_page_content.content = self.execute(
                file_object=file_object, page_number=document_file_page.page_number
            )
            document_file_page_content.save()
        except Exception as exception:
            error_message = _('Exception parsing page; %s') % exception
            logger.error(error_message, exc_info=True)
            raise ParserError(error_message)
        finally:
            file_object.close()

        logger.info(
            'Finished processing page: %d of document file: %s',
            document_file_page.page_number, document_file_page.document_file
        )

    def execute(self, file_object, page_number):
        raise NotImplementedError(
            'Your %s class has not defined the required execute() method.' %
            self.__class__.__name__
        )


class PopplerParser(Parser):
    """
    PDF parser using the pdftotext execute from the poppler package
    """
    def __init__(self):
        self.pdftotext_path = setting_pdftotext_path.value
        if not os.path.exists(self.pdftotext_path):
            error_message = _(
                'Cannot find pdftotext executable at: %s'
            ) % self.pdftotext_path
            logger.error(error_message)
            raise ParserError(error_message)

        logger.debug('self.pdftotext_path: %s', self.pdftotext_path)

    def execute(self, file_object, page_number):
        logger.debug('Parsing PDF page: %d', page_number)

        temporary_file_object = NamedTemporaryFile()
        copyfileobj(fsrc=file_object, fdst=temporary_file_object)
        temporary_file_object.seek(0)

        command = []
        command.append(self.pdftotext_path)
        command.append('-f')
        command.append(str(page_number))
        command.append('-l')
        command.append(str(page_number))
        command.append(temporary_file_object.name)
        command.append('-')

        proc = subprocess.Popen(
            command, close_fds=True, stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        return_code = proc.wait()
        if return_code != 0:
            logger.error(proc.stderr.readline())
            temporary_file_object.close()

            raise ParserError

        output = proc.stdout.read()
        temporary_file_object.close()

        if output == b'\x0c':
            logger.debug('Parser didn\'t return any output')
            return ''

        if output[-3:] == b'\x0a\x0a\x0c':
            return force_text(s=output[:-3])

        return force_text(s=output)


Parser.register(
    mimetypes=('application/pdf',),
    parser_classes=(PopplerParser,)
)
