## Script (Python) "AccountingTransactionModule_getAccountingTransactionList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=**params
##title=
##
# XXX workarounds for DTML limitation
# Because DTML cannot do <dtml-if node or resource or...>
# If Python is used, it does not check the existence of a variable automatically
if 'node' not in params:
  params['node'] = []
if 'resource' not in params:
  params['resource'] = []
if 'from_date' not in params:
  params['from_date'] = ''
if 'to_date' not in params:
  params['to_date'] = ''
if 'section_category' not in params:
  params['section_category'] = ''

return context.AccountingTransactionModule_zGetAccountingTransactionList(**params)
