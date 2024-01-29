"""
  This script adds accounts value.
"""

request = context.REQUEST

include_debtor   = True
include_creditor = True
if debtor_only  : include_creditor = False
if creditor_only: include_debtor   = False

gap_base = request.get('gap_base', kwd.get('gap_base', 'gap/fr/pcg/'))
getURL   = lambda gap_id: context.GAPCategory_getURLFromId(gap_id, gap_base)


kw = dict(kwd)
kw['simulation_state'] = kwd.get('simulation_state', request.get('simulation_state', ['stopped', 'delivered']))
kw["section_category"]  = kwd.get("section_category",
                            "group/%s"%context.restrictedTraverse(request.get("organisation")).getGroup())
kw['to_date'] = kwd.get('at_date', request['at_date']) +1
kw['where_expression'] = " section.portal_type = 'Organisation' "

ledger = kw.get('ledger', request.get("ledger", None))
if ledger is not None:
  portal_categories = context.getPortalObject().portal_categories
  if isinstance(ledger, list) or isinstance(ledger, tuple):
    kw['ledger_uid'] = [portal_categories.ledger.restrictedTraverse(item).getUid() for item in ledger]
  else:
    kw['ledger_uid'] = portal_categories.ledger.restrictedTraverse(ledger).getUid()

sum_ = 0.0
for accountNumber in accounts:
  # we get all acounts strict member of this GAP category
  gap = context.restrictedTraverse("portal_categories/" + getURL(accountNumber))
  for account in gap.getGapRelatedValueList(portal_type='Account') :
    result = context.getPortalObject().portal_simulation.getInventoryAssetPrice(node_uid = account.getUid(), **kw)
    if (result < 0 and include_creditor) or \
       (result > 0 and include_debtor):
      sum_ += result

return sum_
