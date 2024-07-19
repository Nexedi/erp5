"""
  This script adds accounts balance, only if they are creditors.
  For accounts that can be expanded by third parties, we calcul the balance
    per third parties to check if the given third party is creditor or not.
  TODO: The "expansion by third party" code come from
          AccountModule_getAccountListForTrialBalance script. Perhaps it's a
          good idea to put it in an external generic script.
"""

request      = context.REQUEST
getInventory = context.getPortalObject().portal_simulation.getInventoryAssetPrice

include_debtor   = True
include_creditor = True
if debtor_only  : include_creditor = False
if creditor_only: include_debtor   = False

gap_base = request.get('gap_base', kwd.get('gap_base', 'gap/fr/pcg/'))
getURL   = lambda gap_id: context.GAPCategory_getURLFromId(gap_id, gap_base)

kw = dict(kwd)
kw['to_date']          = kwd.get('at_date', request['at_date']) + 1
kw['simulation_state'] = kwd.get('simulation_state', request.get('simulation_state', ['stopped', 'delivered']))
kw['section_category'] = kwd.get("section_category", "group/%s" % context.restrictedTraverse(request.get("organisation")).getGroup())
kw['where_expression'] = " section.portal_type = 'Organisation' "

ledger = kwd.get('ledger', request.get("ledger", None))
if ledger is not None:
  portal_categories = context.getPortalObject().portal_categories
  if isinstance(ledger, list) or isinstance(ledger, tuple):
    kw['ledger_uid'] = [portal_categories.ledger.restrictedTraverse(item).getUid() for item in ledger]
  else:
    kw['ledger_uid'] = portal_categories.ledger.restrictedTraverse(ledger).getUid()


# Find accounts that can be expanded according category membership
acc_type = context.portal_categories.account_type
rec_cat  = acc_type.asset.receivable
pay_cat  = acc_type.liability.payable
# We use strict_membership because we do not want VAT
params = { 'portal_type'      : 'Account'
         , 'strict_membership': True
         }
accounts_to_expand_by_tp = rec_cat.getAccountTypeRelatedValueList(**params) + \
                           pay_cat.getAccountTypeRelatedValueList(**params)


total_balance = 0.0
for account_gap_number in accounts:
  # We get all accounts strict member of this GAP category
  gap = context.restrictedTraverse('portal_categories/' + getURL(account_gap_number))

  for account in gap.getGapRelatedValueList(portal_type='Account'):
    account_balance = 0.0

    # This account should be analyzed per third party
    if account in accounts_to_expand_by_tp:
      # get all entities that are destination section related to this account.
      third_party_list  = [o.getObject() for o in \
            context.Account_zDistinctSectionList( node_uid         = account.getUid()
                                                , at_date          = request['at_date']
                                                , simulation_state = kw['simulation_state']
                                                )]
      for tp in third_party_list:
        tp_balance = getInventory( node_uid           = account.getUid()
                                 , mirror_section_uid = tp.getUid()
                                 , omit_simulation    = True
                                 , **kw
                                 )
        if (tp_balance < 0 and include_creditor) or \
           (tp_balance > 0 and include_debtor):
          account_balance += tp_balance

    # Get the balance of the account
    else:
      account_balance = getInventory( node_uid = account.getUid()
                                    , **kw
                                    )

    # Add account final balance to the total sum
    if (account_balance < 0 and include_creditor) or \
       (account_balance > 0 and include_debtor):
      total_balance += account_balance

return total_balance
