from DateTime import DateTime
from Products.ERP5Type.Document import newTempBase

portal = context.getPortalObject()
selection_params = portal.portal_selections.getSelectionParamsFor(selection_name)
get_inventory_kw = {
    'section_category': selection_params.get('section_category')
  , 'simulation_state': selection_params.get('simulation_state')
  , 'node_category'   : selection_params.get('gap_root')
  , 'omit_simulation' : True
  , 'where_expression': " section.portal_type = 'Organisation' "
}

at_date   = selection_params.get('at_date', None)
from_date = selection_params.get('from_date', None)

getInventory = portal.portal_simulation.getInventoryAssetPrice

# FIXME: Here we do not want to sum all movement < 0, but sum the balances
#        of all nodes whose which have a < 0 balance...
opening_debit_balance  = 0.0
opening_credit_balance = 0.0
closing_debit_balance  = 0.0
closing_credit_balance = 0.0
if from_date not in (None, ''):
  opening_debit_balance = getInventory( at_date     = from_date
                                      , omit_output = True
                                      , **get_inventory_kw
                                      )
  opening_credit_balance = - getInventory( at_date    = from_date
                                         , omit_input = True
                                         , **get_inventory_kw
                                         )
closing_debit_balance = getInventory( at_date     = at_date
                                    , omit_output = True
                                    , **get_inventory_kw
                                    )
closing_credit_balance = - getInventory( at_date    = at_date
                                       , omit_input = True
                                       , **get_inventory_kw
                                       )

list_item = newTempBase(portal, 'xxx')
list_item.setUid('new_000')
list_item.edit(** {
    'total_opening_debit_balance' : opening_debit_balance
  , 'total_closing_debit_balance' : closing_debit_balance
  , 'total_opening_credit_balance': opening_credit_balance
  , 'total_closing_credit_balance': closing_credit_balance
  })

return [list_item]
