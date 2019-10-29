from yapf.yapflib import yapf_api
import json
import tempfile
import textwrap
import logging

logger = logging.getLogger(__name__)


def ERP5Site_formatPythonSourceCode(self, data, REQUEST=None):
  if isinstance(data, basestring):
    data = json.loads(data)
  try:
    extra = {}
    if data['range']:
      extra['lines'] = (
          (data['range']['startLineNumber'], data['range']['endLineNumber']),)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.style.yapf') as f:
      f.write(
          textwrap.dedent(
              '''
              [style]
              based_on_style = pep8
              indent_width = 2
              continuation_indent_width = 2
              split_before_expression_after_opening_paren = true
              blank_line_before_nested_class_or_def = false
              allow_split_before_dict_value = false
              split_before_first_argument = true
              split_before_logical_operator = true
              split_before_dot = true
              '''))
      f.flush()
      formatted_code, changed = yapf_api.FormatCode(
          data['code'], style_config=f.name, **extra)
  except SyntaxError as e:
    logger.exception("Error in source code")
    return json.dumps(dict(error=True, error_line=e.lineno))

  if REQUEST is not None:
    REQUEST.RESPONSE.setHeader('content-type', 'application/json')
  return json.dumps(dict(formatted_code=formatted_code, changed=changed))
