import time
import json
import logging
from Products.ERP5Type.Utils import checkPythonSourceCode

logger = logging.getLogger('extension.erp5.PythonCodeUtils')

import erp5.portal_type
import typing


def checkPythonSourceCodeAsJSON(self, data, REQUEST=None):
  #xtype: (erp5.portal_type.ERP5Site, str, str) -> str
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

  script_name = data.get('script_name') or 'unknown.py'
  is_python_script = 'bound_names' in data
  if is_python_script:
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

  start = time.time()
  code = body.encode('utf8')

  import pyflakes.api
  import pyflakes.reporter
  import pyflakes.messages

  class Reporter(pyflakes.reporter.Reporter):
    def __init__(self):  # pylint: disable=super-init-not-called
      self.message_list = []

    def addMessage(self, row, column, level, text):
      self.message_list.append(
          dict(row=row, column=column, type=level, text=text))

    def flake(self, message):
      # type: (pyflakes.messages.Message,) -> None
      self.addMessage(
          row=message.lineno,
          column=message.col,
          text=message.message % (message.message_args),
          level='W')

    def syntaxError(self, filename, msg, lineno, offset, text):
      self.addMessage(
          row=lineno,
          column=offset,
          text='SyntaxError: {}'.format(text),
          level='E')

    def unexpectedError(self, filename, msg):
      # TODO: extend interface to have range and in this case whole range is wrong ?
      # or use parse with python in that case ?
      # repro: function(a="b", c)
      self.addMessage(
          row=0, column=0, text='Unexpected Error: {}'.format(msg), level='E')

  start = time.time()
  reporter = Reporter()
  pyflakes.api.check(code, script_name, reporter)
  logger.info(
      'pyflakes checked %d lines in %.2f', len(code.splitlines()),
      time.time() - start)

  message_list = reporter.message_list

  import lib2to3.refactor
  import lib2to3.pgen2.parse
  refactoring_tool = lib2to3.refactor.RefactoringTool(
      fixer_names=('lib2to3.fixes.fix_except',))
  old_code = code.decode('utf-8')
  try:
    new_code = unicode(refactoring_tool.refactor_string(old_code, script_name))
  except lib2to3.pgen2.parse.ParseError as e:
    message, (row, column) = e.context
    message_list.append(dict(row=row, column=column, type='E', text=message))
  else:
    if new_code != old_code:
      i = 0
      for new_line, old_line in zip(new_code.splitlines(),
                                    old_code.splitlines()):
        i += 1
        print('new_line', new_line, 'old_line', old_line)
        if new_line != old_line:
          message_list.append(
              dict(
                  row=i,
                  column=0,
                  type='W',
                  text=u'-{}\n+{}'.format(old_line, new_line)))


#  import pdb; pdb.set_trace()
  pylint_message_list = []
  if 0:
    start = time.time()
    pylint_message_list = checkPythonSourceCode(code, data.get('portal_type'))
    logger.info(
        'pylint checked %d lines in %.2f', len(code.splitlines()),
        time.time() - start)
    message_list = pylint_message_list

  import subprocess
  start = time.time()
  mypy_process = subprocess.Popen(
      [
          "/srv/slapgrid/slappart3/srv/runner/software/7ded4ab7e8ec62a2b1ad4312c472eeea/parts/python-language-server/bin/mypy",
          "--python-version=2.7",
          "--allow-redefinition",
          "--allow-untyped-globals",
          "--ignore-missing-imports", # XXX
        #  "--check-untyped-defs",
          "--show-error-codes",
         "-c",
          code,
      #    "--booom"
      ],

      env={
        'MYPYPATH': '/tmp/ahaha/',
        'MYPY_CACHE_DIR': '/tmp/ahaha/.mypy_cache/',
      },
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE)

  mypy_out, mypy_err = mypy_process.communicate()
  logger.info(
      'mypy checked %d lines in %.2f', len(code.splitlines()),
      time.time() - start)

  #import pdb
  #  pdb.set_trace()
  # '<string>:9: error: Type signature has too few arguments\nFound 1 error in 1 file (checked 1 source file)\n'

  for line in mypy_out.splitlines():
    try:
      filename, line_number, error_type, message = line.split(':', 3)
    except ValueError as e:
      logger.info("oops %s / %s", e, line)
    else:
      if filename == '<string>':
        message_list.append(
            dict(
                row=int(line_number),
                column=0,
                type='E',
                text="mypy: " + message,
            ))

  for message_dict in message_list:
    if is_python_script:
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
  