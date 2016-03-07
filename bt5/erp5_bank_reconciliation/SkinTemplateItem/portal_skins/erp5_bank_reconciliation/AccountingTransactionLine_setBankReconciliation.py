"""Set the aggregate relation to a payment request on this line.

This script has a proxy role to be able to modify delivered lines
"""
portal = context.getPortalObject()

assert context.getPortalType() in portal.getPortalAccountingMovementTypeList()

context.setAggregateValue(payment_request_value, portal_type='Bank Reconciliation')
# for traceability
portal.portal_workflow.doActionFor(
  context.getParentValue(),
  "edit_action",
  comment=message)
