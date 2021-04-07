"""Create a balance transaction
"""
accounting_period = sci['object']

# we only create a balance transaction for top level accounting periods
if accounting_period.getParentValue().getPortalType() == accounting_period.getPortalType():
  return

portal = accounting_period.getPortalObject()
profit_and_loss_account = portal.portal_workflow.getInfoFor(
                            accounting_period, 'profit_and_loss_account')

accounting_period.activate(after_method_id='unindexObject').AccountingPeriod_createBalanceTransaction(
                       profit_and_loss_account=profit_and_loss_account)
