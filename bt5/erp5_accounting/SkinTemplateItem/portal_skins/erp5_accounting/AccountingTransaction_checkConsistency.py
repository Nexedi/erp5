"""Check consistency of an accounting transaction.

This verifies the constraints defined in constraints and also "temporary" constraints,
such as "client is validated" or "accounting period is open" that are currently defined
in workflow script.

This is intentded to be used in custom scripts creating accounting transactions and
validating them.
"""
context.Base_checkConsistency()
accounting_workflow = context.getPortalObject().portal_workflow.accounting_workflow
accounting_workflow.script_validateTransactionLines(
  {
    'object': context,
    'kwargs': {},
    'transition': accounting_workflow.transition_deliver_action
  })
