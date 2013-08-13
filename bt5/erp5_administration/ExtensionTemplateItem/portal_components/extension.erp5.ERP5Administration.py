# -*- coding: utf-8 -*-
import sys
from ZODB.POSException import ConflictError
from zExceptions import ExceptionFormatter

from Products.CMFActivity.ActiveResult import ActiveResult
from Products.ERP5Type.Document import newTempOOoDocument
from zLOG import LOG, INFO

def dumpWorkflowChain(self):
  # This method outputs the workflow chain in the format that you can
  # easily get diff like the following:
  # ---
  # Account,account_workflow
  # Account,edit_workflow
  # ...
  # ---
  workflow_tool = self.getPortalObject().portal_workflow
  cbt = workflow_tool._chains_by_type
  ti = workflow_tool._listTypeInfo()
  types_info = []
  for t in ti:
    id = t.getId()
    title = t.Title()
    if title == id:
      title = None
    if cbt is not None and cbt.has_key(id):
      chain = sorted(cbt[id])
    else:
      chain = ['(Default)']
    types_info.append({'id': id,
                       'title': title,
                       'chain': chain})
  output = []
  for i in sorted(types_info, key=lambda x:x['id']):
    for chain in i['chain']:
      output.append('%s,%s' % (i['id'], chain))
  return '\n'.join(output)

def checkFolderHandler(self, fixit=0, **kw):
  error_list = []
  try:
    is_btree = self.isBTree()
    is_hbtree = self.isHBTree()
  except AttributeError:
    return error_list
  message = '%s' % self.absolute_url_path()
  problem = False
  if not is_btree and not is_hbtree:
    problem = True
    message = '%s is NOT BTree NOR HBTree' % message
    if fixit:
      try:
        result = self._fixFolderHandler()
      except AttributeError:
        result = False
      if result:
        message = '%s fixed' % message
      else:
        message = '%s CANNOT FIX' % message
  if is_btree and is_hbtree:
    problem = True
    message = '%s is BTree and HBTree' % message
    if fixit:
      message = '%s CANNOT FIX' % message
  if problem:
    error_list.append(message)
    LOG('checkFolderHandler', INFO, message)
  return error_list


def MessageCatalog_getMessageDict(self):
  """
    Get Localizer's MessageCatalog instance messages.
  """
  d = {}
  for k,v in self._messages.iteritems():
    d[k] = v
  return d

def MessageCatalog_getNotTranslatedMessageDict(self):
  """
    Get Localizer's MessageCatalog instance messages that are NOT translated.
  """
  not_translated_message_dict = {}
  messages = MessageCatalog_getMessageDict(self)
  for k,v in messages.iteritems():
    if not len(v) or not len(filter(lambda x:x, v.values())):
      not_translated_message_dict[k] = v
  return not_translated_message_dict

def MessageCatalog_deleteNotTranslatedMessageDict(self):
  """
    Delete from  Localizer's MessageCatalog instance messages that are NOT translated.
  """
  not_translated_message_dict = MessageCatalog_getNotTranslatedMessageDict(self)
  for k,v in not_translated_message_dict.iteritems():
    # delete message from dict
    del(self._messages[k])
  return len(not_translated_message_dict.keys())


def checkConversionToolAvailability(self):
  """
  Check conversion tool (oood) is available for erp5.
  This script convert an odt document into HTML and try to read
  the returned string and find out expected string
  """
  portal = self.getPortalObject()
  document_id = 'P-ERP5-TEST.Conversion.Tool.Availability-001-en.odt'
  document_path = 'portal_skins/erp5_administration/%s' % (document_id,)
  document_file = portal.restrictedTraverse(document_path)

  message = None
  severity = 0

  try:
    temp_document = newTempOOoDocument(self, document_id, data=document_file.data, source_reference=document_id)
    temp_document.convertToBaseFormat()
    mimetype, html_result = temp_document.convert(format='html')
  except ConflictError:
    raise
  except: #Which Errors should we catch ?
    #Transformation failed
    message = 'Conversion tool got unexpected error:\n%s' % ''.join(ExceptionFormatter.format_exception(*sys.exc_info()))
  else:
    #Everything goes fine, Check that expected string is present in HTML conversion
    if 'AZERTYUIOPMQ' not in html_result:
      message = 'Conversion to HTML Failed:\n%s' % (html_result,)

  active_process = self.newActiveProcess()
  result = ActiveResult()
  if message:
    severity = 1
    result.edit(detail=message)
  result.edit(severity=severity)
  active_process.activateResult(result)

def runPyflakes(script_code, script_path):
  # TODO: reuse _runPyflakes ...
  from pyflakes.api import check
  from pyflakes import reporter
  from StringIO import StringIO
  stream = StringIO()
  check(script_code, script_path, reporter.Reporter(stream, stream))
  return stream.getvalue()

def runPyflakesOnPythonScript(self, data):
  import json

  # XXX data is encoded as json, because jQuery serialize lists as []
  if isinstance(data, basestring):
    data = json.loads(data)

  # data contains the code, the bound names and the script params. From this
  # we reconstruct a function that can be parsed with pyflakes.
  code = data
  def indent(text):
    return ''.join(("  " + line) for line in text.splitlines(True))

  bound_names = data['bound_names']
  signature_parts = data['bound_names']
  if data['params']:
    signature_parts += [data['params']]
  signature = ", ".join(signature_parts)

  function_name = "function_name"
  body = "def %s(%s):\n%s" % (function_name,
                              signature,
                              indent(data['code']) or "  pass")

  error_list = _runPyflakes(body, lineno_offset=-1)

  self.REQUEST.RESPONSE.setHeader('content-type', 'application/json')
  return json.dumps(dict(annotations=error_list))


def _runPyflakes(code, lineno_offset=0):
  import pyflakes.api
  error_list = []

  class Reporter(object):
    def unexpectedError(self, filename, msg):
        error_list.append(
         { 'row': 0,
           'column': 0,
           'text': msg,
           'type': 'error' }
        )

    def syntaxError(self, filename, msg, lineno, offset, text):
        error_list.append(
         { 'row': lineno - 1 + lineno_offset,
           'column': offset,
           'text': msg + (text and ": " + text or ''),
           'type': 'error' }
        )

    def flake(self, message):
      error_list.append(
         { 'row': message.lineno - 1 + lineno_offset,
           'column': getattr(message, 'col', 0),
           'text': message.message % message.message_args,
           'type': 'warning' }
      )

  pyflakes.api.check(code, '', Reporter())
  return error_list
