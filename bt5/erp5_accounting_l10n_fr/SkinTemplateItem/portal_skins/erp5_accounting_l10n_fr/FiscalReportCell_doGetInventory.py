"""
  This scripts add the balance of every gap account in the list 'accounts'
  it use portal_simulation.getInventoryAssetPrice.
  The following REQUEST keys are mandatory:
      at_date

  those are optional:
      gap_base
      simulation_state
      section_category
      ledger

  those are ignored from the request and should explicitely passed as keywords args to this script:
      from_date

  parameters keywords to this script overrides REQUEST keys
"""
request = context.REQUEST

gap_base = request.get("gap_base", "gap/fr/pcg/")
getURL   = lambda gap_id: context.GAPCategory_getURLFromId(gap_id, gap_base)

section        = context.restrictedTraverse(request.get("organisation"))
section_region = section.getRegion()

ledger = request.get("ledger", None)
if ledger is not None:
  portal_categories = context.getPortalObject().portal_categories
  if isinstance(ledger, list) or isinstance(ledger, tuple):
    ledger_uid = [portal_categories.ledger.restrictedTraverse(item).getUid() for item in ledger]
  else:
    ledger_uid = portal_categories.ledger.restrictedTraverse(ledger).getUid()
else:
  ledger_uid = None

# 'getInventory' common parameters
params = { 'omit_simulation' : True
         , 'simulation_state': request.get("simulation_state", ['stopped', 'delivered'])
         , 'section_uid'     : section.getUid()
         , 'precision'       : 2
         , 'at_date'         : request['at_date']
         , 'ledger_uid'      : ledger_uid
         }
params.update(kw)

# 'net_balance' is the sum of balance of all accounts found under the 'gap_id_list' criterion
net_balance = 0.0

ctool = context.getPortalObject().portal_categories
for gap_id in gap_id_list:
  gap_path = getURL(gap_id)

  # Checks the node category exists
  if ctool.restrictedTraverse(gap_path, None) is not None:
    params["node_category"] = gap_path
    new_balance = 0.0

    if not section_region_filtering:
      new_balance = context.portal_simulation.getInventoryAssetPrice(**params) or 0.0

    else:
      # Use section's region membership to decide if a transaction is export or not
      transaction_list = context.portal_simulation.getInventoryList(**params) or []

      # Test each transaction's third party region against section's region
      for transaction in transaction_list:
        transaction_line_path = transaction.path
        line = context.restrictedTraverse(transaction_line_path)

        # Get the third party
        third_party = line.getDestinationSectionValue()
        if third_party in (None, ''):
          # TODO: is this log should be replaced by 'raise' ?
          context.log( 'FiscalReportError'
                     , "'%s' need a third party." % (transaction_line_path)
                     )
          # Skip current transaction
          continue

        # Get the third party region
        region = third_party.getRegion()
        if region in (None, ''):
          # TODO: is this log should be replaced by 'raise' ?
          context.log( 'FiscalReportError'
                     , "'%s' third party (aka '%s') need a region." % ( transaction_line_path
                                                                      , third_party.getPath()
                                                                      )
                     )
          # Skip current transaction
          continue

        # Get the transaction's balance
        if not region.startswith(section_region):
          new_balance = new_balance + transaction.total_price

    # Update the general balance
    net_balance = net_balance + new_balance

return net_balance
