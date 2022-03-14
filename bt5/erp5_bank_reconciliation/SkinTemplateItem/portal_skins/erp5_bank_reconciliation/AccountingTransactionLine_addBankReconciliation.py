"""Adds the bank reconciliation to the already aggregated bank reconciliation on this line.

This script has a proxy role to be able to modify delivered lines
"""
portal = context.getPortalObject()

assert context.getPortalType() in portal.getPortalAccountingMovementTypeList()

context.setAggregateSet(
  context.getAggregateList(portal_type='Bank Reconciliation') + [bank_reconciliation_relative_url],
  portal_type='Bank Reconciliation')

# for traceability
context.getParentValue().Base_addEditWorkflowComment(comment=message)
