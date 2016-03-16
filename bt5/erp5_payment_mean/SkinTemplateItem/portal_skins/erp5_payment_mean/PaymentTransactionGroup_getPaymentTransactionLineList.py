portal = context.getPortalObject()

search_kw = dict(
  parent_portal_type='Payment Transaction',
  section_uid=context.getSourceSectionUid(),
  default_aggregate_uid=context.getUid(),
)

if context.getSourcePayment():
  precision = context.getQuantityPrecisionFromResource(
    context.getSourcePaymentValue().getPriceCurrency())
  portal.REQUEST.set('precision', precision)

return portal.portal_simulation.getMovementHistoryList(**search_kw)
