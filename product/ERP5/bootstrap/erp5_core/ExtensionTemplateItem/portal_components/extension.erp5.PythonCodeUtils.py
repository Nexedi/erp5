import re
import six
import json
import sys
from zExceptions import ExceptionFormatter
from Products.ERP5Type.Utils import checkPythonSourceCode


match_PEP263 = re.compile(r'^[ \t\f]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)').match


def checkPythonSourceCodeAsJSON(self, data, REQUEST=None):
  """
  Check Python source suitable for Source Code Editor and return a JSON object
  """

  # XXX data is encoded as json, because jQuery serialize lists as []
  if isinstance(data, six.string_types):
    data = json.loads(data)

  # data contains the code, the bound names and the script params. From this
  # we reconstruct a function that can be checked
  def indent(text):
    return ''.join(("  " + line) for line in text.splitlines(True))

  # don't show 'undefined-variable' errors for {Python,Workflow} Script parameters
  is_script = 'bound_names' in data
  if is_script:
    signature_parts = data['bound_names']
    if data['params']:
      signature_parts += [data['params']]
    signature = ", ".join(signature_parts)

    # keep the PEP263 magic comment
    pep263_comment = '#'
    lines = data['code'].splitlines() + ['', '']
    for line in lines[0], lines[1]:
      m = match_PEP263(line)
      if m:
        pep263_comment = '# coding=' + m.groups()[0]
        break

    body = "%s\n"\
           "from __future__ import print_function\n"\
           "def function_name(%s):\n%s" % (
              pep263_comment,
              signature,
              indent(data['code']) or "  pass")
  else:
    body = data['code']

  if six.PY2:
    body = body.encode('utf8')
  try:
    message_list = checkPythonSourceCode(body, data.get('portal_type'))
  except Exception:
    message_list = [{
      'type': 'E',
      'row': 0,
      'column': 0,
      'text': 'pylint failed:\n%s' % ''.join(ExceptionFormatter.format_exception(*sys.exc_info())),
    }]
  for message_dict in message_list:
    if is_script:
      message_dict['row'] = message_dict['row'] - 3
      message_dict['column'] = message_dict['column'] - 2

    if message_dict['type'] in ('E', 'F'):
      message_dict['type'] = 'error'
    else:
      message_dict['type'] = 'warning'

  if REQUEST is not None:
    REQUEST.RESPONSE.setHeader('content-type', 'application/json')
  return json.dumps(dict(annotations=message_list))
