## Script (Python) "AccountModule_statTotalSourceDebit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=**kw
##title=
##
try:
  url = kw['accounting_transaction_line_currency']
  if url:
    currency = context.restrictedTraverse(url)
  else:
    currency = None
except:
  currency = None

params = {}
if kw.get('query'):
  params['query'] = kw['query']
if kw.get('from_date'):
  params['from_date'] = kw['from_date']
if kw.get('to_date'):
  params['to_date'] = kw['to_date']
if currency is not None:
  params['resource_uid'] = [currency.getUid()]
params['simulation_state'] = kw.get('transaction_simulation_state', ('delivered', 'stopped'))
params['section_category'] = kw.get('transaction_section_category', 'group/nexedi')

result = context.Resource_zStatInventory(omit_simulation=1,
                                         omit_input=1,
                                         **params)

row = result[0]
try:
  quantity = - row.quantity
except:
  quantity = 0.0
return '%.02f' % quantity
