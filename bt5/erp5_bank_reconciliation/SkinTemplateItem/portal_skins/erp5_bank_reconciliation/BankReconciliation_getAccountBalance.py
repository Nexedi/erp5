kw = {
  'section_uid': context.getSourceSectionUid(),
  'payment_uid': context.getSourcePaymentUid(),
  'node_category': 'account_type/asset/cash/bank',
  'simulation_state': ('stopped', 'delivered', ),
  'portal_type': context.getPortalAccountingMovementTypeList()
}

if context.getStopDate():
  kw['at_date'] = context.getStopDate().latestTime()

return context.portal_simulation.getInventory(**kw)
