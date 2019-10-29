import json
import sys
from threading import RLock
import logging

import jedi

# increase default cache duration
jedi.settings.call_signatures_validity = 30 # XXX needed ?


# map jedi type to the name of monaco.languages.CompletionItemKind
# This mapping and the functions below (_format_completion, _label, _detail, _sort_text )
# are copied/inspired by jedi integration in python-language-server
# https://github.com/palantir/python-language-server/blob/19b10c47988df504872a4fe07c421b0555b3127e/pyls/plugins/jedi_completion.py
# python-language-server is Copyright 2017 Palantir Technologies, Inc. and distributed under MIT License.
# https://github.com/palantir/python-language-server/blob/19b10c47988df504872a4fe07c421b0555b3127e/LICENSE

_TYPE_MAP = {
  'none': 'Value',
  'type': 'Class',
  'tuple': 'Class',
  'dict': 'Class',
  'dictionary': 'Class',
  'function': 'Function',
  'lambda': 'Function',
  'generator': 'Function',
  'class': 'Class',
  'instance': 'Reference',
  'method': 'Method',
  'builtin': 'Class',
  'builtinfunction': 'Function',
  'module': 'Module',
  'file': 'File',
  'xrange': 'Class',
  'slice': 'Class',
  'traceback': 'Class',
  'frame': 'Class',
  'buffer': 'Class',
  'dictproxy': 'Class',
  'funcdef': 'Function',
  'property': 'Property',
  'import': 'Module',
  'keyword': 'Keyword',
  'constant': 'Variable',
  'variable': 'Variable',
  'value': 'Value',
  'param': 'Variable',
  'statement': 'Keyword',
}

def _label(definition):
  if definition.type in ('function', 'method') and hasattr(definition, 'params'):
    params = ', '.join([param.name for param in definition.params])
    return '{}({})'.format(definition.name, params)
  return definition.name

def _detail(definition):
  try:
    return definition.parent().full_name or ''
  except AttributeError:
    return definition.full_name or ''

def _sort_text(definition):
  """ Ensure builtins appear at the bottom.
  Description is of format <type>: <module>.<item>
  """
  # If its 'hidden', put it next last
  prefix = 'z{}' if definition.name.startswith('_') else 'a{}'
  return prefix.format(definition.name)

def _format_docstring(docstring):
  return docstring

def _format_completion(d):
  completion = {
      'label': _label(d),
      '_kind': _TYPE_MAP.get(d.type),
      'detail': _detail(d),
      'documentation': _format_docstring(d.docstring()),
      'sortText': _sort_text(d),
      'insertText': d.name
  }
  return completion

def _guessType(name):
  """guess the type of python script parameters based on naming conventions.

  TODO: depend on the script name, for Person_getSomething, context is a erp5.portal_type.Person
  """
  name = name.split('=')[0] # support also assigned names ( like REQUEST=None in params)
  if name in ('context', 'container',):
    return 'Products.ERP5Type.Core.Folder.Folder'
  if name == 'script':
    return 'Products.PythonScripts.PythonScript'
  if name == 'REQUEST':
    return 'ZPublisher.HTTPRequest.HTTPRequest'
  if name == 'RESPONSE':
    return 'ZPublisher.HTTPRequest.HTTPResponse'
  return 'str' # assume string by default

#jedi_lock = RLock() # jedi is not thread safe
import Products.ERP5Type.Utils
logger = logging.getLogger("erp5.extension.Jedi")

# Jedi is not thread safe
jedi_lock = getattr(Products.ERP5Type.Utils, 'jedi_lock', None)
if jedi_lock is None:
  logger.critical("There was no lock, making a new one")
  jedi_lock = Products.ERP5Type.Utils.jedi_lock = RLock()
logger.info("Jedi locking with %s (%s)", jedi_lock, id(jedi_lock))


def ERP5Site_getPythonSourceCodeCompletionList(self, data, REQUEST=None):
  """Complete source code with jedi.
  """
  logger.info('jedi get lock %s (%s)', jedi_lock, id(jedi_lock))
  with jedi_lock:
    if isinstance(data, basestring):
      data = json.loads(data)

    # data contains the code, the bound names and the script params. From this
    # we reconstruct a function that can be checked
    def indent(text):
      return ''.join(("  " + line) for line in text.splitlines(True))

    is_python_script = 'bound_names' in data
    if is_python_script:
      signature_parts = data['bound_names']
      if data['params']:
        signature_parts += [data['params']]
      signature = ", ".join(signature_parts)

      imports = "import Products.ERP5Type.Core.Folder; import ZPublisher.HTTPRequest; import Products.PythonScripts"
      function_name = "function_name"
      type_annotation = "  #  type: (%s) -> None" % (
          ', '.join([_guessType(part) for part in signature_parts]))
      body = "%s\ndef %s(%s):\n%s\n%s" % (
          imports,
          function_name,
          signature,
          type_annotation,
          indent(data['code']) or "  pass")
      data['position']['line'] = data['position']['line'] + 3 # imports, fonction header + type annotation line
      data['position']['column'] = data['position']['column'] + 2 # "  " from indent(text)
    else:
      body = data['code']

    logger.info("jedi getting completions....")
    script = jedi.Script(
        body,
        data['position']['line'],
        data['position']['column'] - 1,
        'example.py', #  TODO name
        sys_path=list(sys.path),
      )

    completions = [_format_completion(c) for c in script.completions()]
    logger.info("jedi got completion")

    if REQUEST is not None:
      REQUEST.RESPONSE.setHeader('content-type', 'application/json')
    return json.dumps(completions)

