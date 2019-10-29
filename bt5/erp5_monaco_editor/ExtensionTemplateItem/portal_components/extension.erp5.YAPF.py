from yapf.yapflib import yapf_api
import json
import tempfile
import textwrap


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
              based_on_style = chromium
              #SPLIT_ALL_TOP_LEVEL_COMMA_SEPARATED_VALUES = true
              #SPLIT_ARGUMENTS_WHEN_COMMA_TERMINATED = true
              SPLIT_BEFORE_EXPRESSION_AFTER_OPENING_PAREN = true
              BLANK_LINE_BEFORE_NESTED_CLASS_OR_DEF = false
              ALLOW_SPLIT_BEFORE_DICT_VALUE = true
              SPLIT_BEFORE_FIRST_ARGUMENT = true
              SPLIT_BEFORE_LOGICAL_OPERATOR = true
              SPLIT_BEFORE_DOT = true
              '''))
      f.flush()
      formatted_code, changed = yapf_api.FormatCode(
          data['code'], style_config=f.name, **extra)
  except SyntaxError as e:
    return json.dumps(dict(error=True, error_line=e.lineno))

  if REQUEST is not None:
    REQUEST.RESPONSE.setHeader('content-type', 'application/json')
  return json.dumps(dict(formatted_code=formatted_code, changed=changed))
