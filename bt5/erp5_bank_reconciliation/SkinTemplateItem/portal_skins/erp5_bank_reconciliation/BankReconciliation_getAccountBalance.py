portal = context.getPortalObject()

kw = {
  'section_uid': context.getSourceSection()
     and portal.Base_getSectionUidListForSectionCategory(
       context.getSourceSectionValue().getGroup(base=True)),
  'payment_uid': context.getSourcePaymentUid(),
  'node_category': 'account_type/asset/cash/bank',
  'simulation_state': ('stopped', 'delivered', ),
  'portal_type': context.getPortalAccountingMovementTypeList()
}

if context.getStopDate():
  kw['at_date'] = context.getStopDate().latestTime()

return context.portal_simulation.getInventory(**kw)
