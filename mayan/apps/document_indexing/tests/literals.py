from __future__ import unicode_literals

TEST_INDEX_LABEL = 'test label'
TEST_INDEX_LABEL_EDITED = 'test edited label'
TEST_INDEX_SLUG = 'test_slug'
TEST_METADATA_TYPE_LABEL = 'test metadata label'
TEST_METADATA_TYPE_NAME = 'test_metadata_name'
TEST_METADATA_VALUE = '0001'
TEST_INDEX_TEMPLATE_METADATA_EXPRESSION = '{{{{ document.get_metadata("{}").value }}}}'.format(TEST_METADATA_TYPE_NAME)
TEST_INDEX_TEMPLATE_DOCUMENT_LABEL_EXPRESSION = '{{ document.label }}'
TEST_INDEX_TEMPLATE_DOCUMENT_DESCRIPTION_EXPRESSION = '{{ document.description }}'
TEST_INDEX_TEMPLATE_DOCUMENT_UUID_EXPRESSION = '{{ document.uuid }}'
TEST_INDEX_TEMPLATE_NODE_EXPRESSION_EDITED = 'expression edited'
