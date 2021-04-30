portal = context.getPortalObject()

kw['section_uid'] = -1
if context.getSourceSection():
  kw['section_uid'] = portal.Base_getSectionUidListForSectionCategory(
       context.getSourceSectionValue().getGroup(base=True))

kw['default_aggregate_uid'] = context.getUid()
kw['parent_portal_type'] = ('Payment Transaction', 'Accounting Transaction')

if context.getSourcePayment():
  precision = context.getQuantityPrecisionFromResource(
    context.getSourcePaymentValue().getPriceCurrency())
  portal.REQUEST.set('precision', precision)
return portal.portal_simulation.getMovementHistoryList(**kw)
