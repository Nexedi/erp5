portal = context.getPortalObject()

translateString = context.Base_translateString

message_list = []

kw = {
  'section_uid': context.getSourceSection()
     and portal.Base_getSectionUidListForSectionCategory(
       context.getSourceSectionValue().getGroup(base=True)),
  'payment_uid': context.getSourcePaymentUid(),
  'node_category': 'account_type/asset/cash/bank',
  'simulation_state': \
    portal.getPortalPlannedTransactionStateList() + \
    ('confirmed',) + \
    portal.getPortalAccountedTransactionStateList(),
  'portal_type': context.getPortalAccountingMovementTypeList(),
  'aggregate_bank_reconciliation_uid': context.getUid(),
}

for movement in portal.portal_simulation.getMovementHistoryList(**kw):
  transaction = movement.getParentValue()
  if transaction.getSimulationState() not in ("stopped", "delivered"):
    message_list.append(translateString("Related ${portal_type} \"${title}\" is not closed", mapping={
      "portal_type": transaction.getPortalType(),
      "title": transaction.getTitle(),
    }))

return message_list
