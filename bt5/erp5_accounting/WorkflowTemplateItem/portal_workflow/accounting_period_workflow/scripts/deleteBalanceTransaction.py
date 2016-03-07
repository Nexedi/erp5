"""Deletes a previously created balance transaction
"""
accounting_period = sci['object']

# we only proceed for top level accounting periods
if accounting_period.getParentValue().getPortalType() == accounting_period.getPortalType():
  return

accounting_period.activate().AccountingPeriod_deleteBalanceTransaction()
