from __future__ import absolute_import

import os
import hashlib
import logging

from django.utils.encoding import smart_str

from common.textparser import TextParser, TEXT_PARSER_MIMETYPES
from mimetype.api import get_mimetype

from .literals import (DEFAULT_PAGE_NUMBER,
    DEFAULT_ZOOM_LEVEL, DEFAULT_ROTATION, DEFAULT_FILE_FORMAT)
from .literals import (TRANSFORMATION_CHOICES, TRANSFORMATION_RESIZE,
    TRANSFORMATION_ROTATE, TRANSFORMATION_ZOOM, DIMENSION_SEPARATOR,
    FILE_FORMATS)
from .utils import cleanup
from .runtime import office_converter
from .exceptions import OfficeConversionError, UnknownFileFormat

HASH_FUNCTION = lambda x: hashlib.sha256(x).hexdigest()

logger = logging.getLogger(__name__)
text_parser = TextParser()
TEXT_PARSER_FILE_SUFFIX = '_text_parser'


def cache_cleanup(input_filepath, *args, **kwargs):
    try:
        os.remove(create_image_cache_filename(input_filepath, *args, **kwargs))
    except OSError:
        pass


def create_image_cache_filename(input_filepath, *args, **kwargs):
    from common.settings import TEMPORARY_DIRECTORY

    if input_filepath:
        hash_value = HASH_FUNCTION(u''.join([HASH_FUNCTION(smart_str(input_filepath)), unicode(args), unicode(kwargs)]))
        return os.path.join(TEMPORARY_DIRECTORY, hash_value)
    else:
        return None


def convert(input_filepath, output_filepath=None, cleanup_files=False, mimetype=None, *args, **kwargs):
    from .runtime import backend
    from common.settings import TEMPORARY_DIRECTORY

    size = kwargs.get('size')
    file_format = kwargs.get('file_format', DEFAULT_FILE_FORMAT)
    zoom = kwargs.get('zoom', DEFAULT_ZOOM_LEVEL)
    rotation = kwargs.get('rotation', DEFAULT_ROTATION)
    page = kwargs.get('page', DEFAULT_PAGE_NUMBER)
    transformations = kwargs.get('transformations', [])

    if transformations is None:
        transformations = []

    if output_filepath is None:
        output_filepath = create_image_cache_filename(input_filepath, *args, **kwargs)

    if os.path.exists(output_filepath):
        return output_filepath

    if not mimetype:
        with open(input_filepath, 'rb') as descriptor:
            mimetype2, encoding = get_mimetype(descriptor, input_filepath, mimetype_only=True)
    
    logger.debug('mimetype: %s' % mimetype)
    
    if mimetype in TEXT_PARSER_MIMETYPES:
        logger.debug('creating page image with TextParser')
        parser_output_filepath = os.path.join(TEMPORARY_DIRECTORY, u''.join([input_filepath, str(page), TEXT_PARSER_FILE_SUFFIX]))
        logger.debug('parser_output_filepath: %s', parser_output_filepath)
        with open(parser_output_filepath, 'wb') as descriptor:
            descriptor.write(text_parser.render_to_image(input_filepath, mimetype=mimetype, page_number=page))
        
        input_filepath = parser_output_filepath
        mimetype = 'image/png'
    elif office_converter:
        try:
            office_converter.convert(input_filepath, mimetype=mimetype)
            if office_converter.exists:
                input_filepath = office_converter.output_filepath
                mimetype = 'application/pdf'
            else:
                # Recycle the already detected mimetype
                mimetype = office_converter.mimetype

        except OfficeConversionError:
            raise UnknownFileFormat('office converter exception')

    if size:
        transformations.append(
            {
                'transformation': TRANSFORMATION_RESIZE,
                'arguments': dict(zip([u'width', u'height'], size.split(DIMENSION_SEPARATOR)))
            }
        )

    if zoom != 100:
        transformations.append(
            {
                'transformation': TRANSFORMATION_ZOOM,
                'arguments': {'percent': zoom}
            }
        )

    if rotation != 0 and rotation != 360:
        transformations.append(
            {
                'transformation': TRANSFORMATION_ROTATE,
                'arguments': {'degrees': rotation}
            }
        )

    try:
        backend.convert_file(input_filepath=input_filepath, output_filepath=output_filepath, transformations=transformations, page=page, file_format=file_format, mimetype=mimetype)
    finally:
        if cleanup_files:
            cleanup(input_filepath)

    return output_filepath


def get_page_count(input_filepath):
    from .runtime import backend

    # Try to determine the page count first with the TextParser
    with open(input_filepath, 'rb') as descriptor:
        mimetype, encoding = get_mimetype(descriptor, input_filepath, mimetype_only=True)
        logger.debug('mimetype: %s' % mimetype)
        if mimetype in TEXT_PARSER_MIMETYPES:
            logger.debug('getting page count with text parser')
            parser = TextParser()
            return len(parser.render_to_viewport(input_filepath))
  
    logger.debug('office_converter: %s' % office_converter)
    if office_converter:
        try:
            office_converter.convert(input_filepath)
            logger.debug('office_converter.exists: %s' % office_converter.exists)
            if office_converter.exists:
                input_filepath = office_converter.output_filepath

        except OfficeConversionError:
            raise UnknownFileFormat('office converter exception')

    return backend.get_page_count(input_filepath)

'''
def get_document_dimensions(document, *args, **kwargs):
    document_filepath = create_image_cache_filename(document.checksum, *args, **kwargs)
    if os.path.exists(document_filepath):
        options = [u'-format', u'%w %h']
        return [int(dimension) for dimension in backend.identify_file(unicode(document_filepath), options).split()]
    else:
        return [0, 0]
'''

def get_available_transformations_choices():
    result = []
    for transformation in backend.get_available_transformations():
        transformation_template = u'%s %s' % (TRANSFORMATION_CHOICES[transformation]['label'], u','.join(['<%s>' % argument['name'] if argument['required'] else '[%s]' % argument['name'] for argument in TRANSFORMATION_CHOICES[transformation]['arguments']]))
        result.append([transformation, transformation_template])

    return result


def get_format_list():
    from .runtime import backend
    
    return [(format, FILE_FORMATS.get(format, u'')) for format in backend.get_format_list()]
