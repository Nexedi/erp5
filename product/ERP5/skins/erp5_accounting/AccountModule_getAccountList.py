## Script (Python) "AccountModule_getAccountList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=**kwd
##title=
##
try:
  currency = kwd['accounting_transaction_line_currency']
  id = currency.split('/')[-1]
except:
  id = ''

if not id:
  id = '&nbsp;'

kwd['select_expression'] = "'%s' AS accounting_transaction_line_currency" % id

return context.portal_catalog(**kwd)
