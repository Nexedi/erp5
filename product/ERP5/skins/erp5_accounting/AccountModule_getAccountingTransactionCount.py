## Script (Python) "AccountModule_getAccountingTransactionCount"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=brain, selection, **kw
##title=
##
params = selection.getParams()

url = params.get('accounting_transaction_line_currency') # XXX This should be called resource
if url:
  currency = context.restrictedTraverse(url) # XXX portal_categories.resolveCategory(resource)
else:
  currency = None

kwd = {}

if params.get('from_date'): 
  kwd['from_date'] = params['from_date']
if params.get('to_date'):
  kwd['to_date'] = params['to_date']
if currency is not None:
  kwd['resource_uid'] = [currency.getUid()]
kwd['simulation_state'] = params.get('transaction_simulation_state', ('delivered', 'stopped')) # XXX Why not simulation_state ? choice of state should be in ERP5Globals or equiv.
kwd['section_category'] = params.get('transaction_section_category', 'group/nexedi') # XXX Why not section_category ? also, default value should be defined for now in ERP5Globals and later through ERP5Site method

inventory = context.Resource_zGetInventory(node_uid=context.getUid(), omit_simulation=1,
                                           **kwd) 
inventory = inventory[0]
return str(inventory.stock_uid)

# XXX should be return currency.getInventoryCount(from_date = params.get('from_date'), to_date=params.get('to_date'),  )
# XXX should be actually return currency.getInventoryCount(**params  )
