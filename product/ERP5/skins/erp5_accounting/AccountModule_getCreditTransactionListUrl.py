## Script (Python) "AccountModule_getCreditTransactionListUrl"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=brain=None, selection=None, **kwd
##title=
##
from ZTUtils import make_query

index = selection.getIndex()
name = selection.getName()
object = brain.getObject()

url = object.absolute_url()
method = 'Account_viewAccountingTransactionList'
kw = { 'selection_index': str(index),
       'selection_name' : name, 
       'reset' : '1', 
       'omit_output' : '1',
     }

params = selection.getParams()

try:
  path = params.get('accounting_transaction_line_currency')
  if path:
    currency = context.restrictedTraverse(path)
  else:
    currency = None
except:
  currency = None

if params.get('from_date'):
  kw['from_date'] = params['from_date']
if params.get('to_date'):
  kw['to_date'] = params['to_date']
if currency is not None:
  kw['resource_uid'] = [currency.getUid()]
if params.get('transaction_simulation_state'):
  kw['transaction_simulation_state'] = params['transaction_simulation_state']
if params.get('transaction_section_category'):
  kw['transaction_section_category'] = params['transaction_section_category']

return url + '/' + method + '?' + make_query(kw)
