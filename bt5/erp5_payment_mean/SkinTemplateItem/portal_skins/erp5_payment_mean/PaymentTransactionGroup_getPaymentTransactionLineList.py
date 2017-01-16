portal = context.getPortalObject()

kw['section_uid'] = context.getSourceSectionUid()
kw['default_aggregate_uid'] = context.getUid()
kw['parent_portal_type'] = ('Payment Transaction', 'Accounting Transaction')

if context.getSourcePayment():
  precision = context.getQuantityPrecisionFromResource(
    context.getSourcePaymentValue().getPriceCurrency())
  portal.REQUEST.set('precision', precision)
return portal.portal_simulation.getMovementHistoryList(**kw)
