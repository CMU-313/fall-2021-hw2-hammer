*********
Languages
*********

The list of languages choices in the language dropdown used for documents is
based on the current ISO 639 list. This list can be quite extensive. To reduce
the number of languages available use the setting ``DOCUMENTS_LANGUAGE_CODES``,
and set it to a nested list of abbreviations. This setting can be found in the
:menuselection:`System --> Setup --> Settings --> Common` menu.

For example, to reduce the list to just English and Spanish use
::

    DOCUMENTS_LANGUAGE_CODES = ('eng', 'spa')


The default language to appear on the dropdown can also be configured using::

    DOCUMENTS_LANGUAGE = 'spa'

Use the correct ISO 639-3 language abbreviation (https://en.wikipedia.org/wiki/ISO_639)
as this code is used in several subsystems in Mayan EDMS such as the OCR app
to determine how to interpret the document.

If using the Docker image, these settings can also be passed to the container
as environment variables by prepending the ``MAYAN_`` suffix.

Example::

  -e MAYAN_DOCUMENTS_LANGUAGE_CODES='["eng", "spa"]'

For more information check out the
:ref:`environment variables <environment_variables>` chapter of the
:doc:`../topics/settings` topic.


