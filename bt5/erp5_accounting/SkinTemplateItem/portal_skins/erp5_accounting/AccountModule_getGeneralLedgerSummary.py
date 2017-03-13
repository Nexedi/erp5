from Products.PythonScripts.standard import Object
getInventoryAssetPrice = context.getPortalObject().portal_simulation.getInventoryAssetPrice

inventory_kw = dict(section_uid=section_uid,
                    simulation_state=simulation_state,
                    at_date=at_date,
                    portal_type=context.getPortalAccountingMovementTypeList(),
                    )
if function_category:
  inventory_kw['function_category'] = function_category
if function_uid:
  inventory_kw['function_uid'] = function_uid
if funding_category:
  inventory_kw['funding_category'] = funding_category
if funding_uid:
  inventory_kw['funding_uid'] = funding_uid
if project_uid:
  inventory_kw['project_uid'] = project_uid
if mirror_section_category:
  inventory_kw['mirror_section_category'] = mirror_section_category
if mirror_section_uid:
  inventory_kw['mirror_section_uid'] = mirror_section_uid
if ledger_uid:
  inventory_kw['ledger_uid'] = ledger_uid

if node_uid:
  # XXX if node uid is passed, income or balance accounts are not
  # calculated differently. As a result, the summary doesn't take from_date
  # into account for income accounts.
  return [Object(
            debit_price=getInventoryAssetPrice(omit_asset_decrease=1,
                               node_uid=node_uid,
                               precision=precision,
                               **inventory_kw),
            credit_price=-getInventoryAssetPrice(omit_asset_increase=1,
                               node_uid=node_uid,
                               precision=precision,
                                **inventory_kw) or 0 ) ]

income_node_category = ['account_type/income', 'account_type/expense']
balance_node_category = ['account_type/equity', 'account_type/asset',
                         'account_type/liability']

debit = getInventoryAssetPrice(omit_asset_decrease=1,
                               from_date=period_start_date,
                               node_category=income_node_category,
                               precision=precision,
                               **inventory_kw)

credit = - getInventoryAssetPrice(omit_asset_increase=1,
                               from_date=period_start_date,
                               node_category=income_node_category,
                               precision=precision,
                                **inventory_kw) or 0

debit += getInventoryAssetPrice(omit_asset_decrease=1,
                               node_category=balance_node_category,
                               precision=precision,
                               **inventory_kw)

credit -= getInventoryAssetPrice(omit_asset_increase=1,
                               node_category=balance_node_category,
                               precision=precision,
                                **inventory_kw) or 0

return [Object(debit_price=debit, credit_price=credit)]
