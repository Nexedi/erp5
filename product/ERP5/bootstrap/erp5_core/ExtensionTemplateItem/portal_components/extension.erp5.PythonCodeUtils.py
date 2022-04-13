from six import string_types as basestring
import json
from Products.ERP5Type.Utils import checkPythonSourceCode

def checkPythonSourceCodeAsJSON(self, data, REQUEST=None):
  """
  Check Python source suitable for Source Code Editor and return a JSON object
  """

  # XXX data is encoded as json, because jQuery serialize lists as []
  if isinstance(data, basestring):
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

    function_name = "function_name"
    body = "def %s(%s):\n%s" % (function_name,
                                signature,
                                indent(data['code']) or "  pass")
  else:
    body = data['code']

  message_list = checkPythonSourceCode(body.encode('utf8'), data.get('portal_type'))
  for message_dict in message_list:
    if is_script:
      message_dict['row'] = message_dict['row'] - 2
    else:
      message_dict['row'] = message_dict['row'] - 1

    if message_dict['type'] in ('E', 'F'):
      message_dict['type'] = 'error'
    else:
      message_dict['type'] = 'warning'

  if REQUEST is not None:
    REQUEST.RESPONSE.setHeader('content-type', 'application/json')
  return json.dumps(dict(annotations=message_list))
