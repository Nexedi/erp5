## Script (Python) "AccountModule_getTotalSourceDebit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=brain=None, selection=None, **kw
##title=
##
params = selection.getParams()

url = params.get('accounting_transaction_line_currency')
if url:
  currency = context.restrictedTraverse(url)
else:
  currency = None

kwd = {}

if params.get('from_date'):
  kwd['from_date'] = params['from_date']
if params.get('to_date'):
  kwd['to_date'] = params['to_date']
if currency is not None:
  kwd['resource_uid'] = [currency.getUid()]
kwd['simulation_state'] = params.get('transaction_simulation_state', ('delivered', 'stopped'))
kwd['section_category'] = params.get('transaction_section_category', 'group/nexedi')

total = 0.0
try:
  inventory = context.Resource_zGetInventory(node_uid=context.getUid(), omit_input=1, omit_simulation=1,
                                             **kwd) # XXX Choice of omit_input is very good.
  total = - inventory[0].inventory or 0.0
except:
  pass

return '%.02f' % total
