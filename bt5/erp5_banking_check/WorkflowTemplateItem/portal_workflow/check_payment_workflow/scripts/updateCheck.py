# Note: this script is executed with the proxy role Manager, because this script needs
#       to use checkbook_module.

transaction = state_change['object']
check = transaction.getAggregateValue()
check.deliver()
