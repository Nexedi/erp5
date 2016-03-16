# Note: this script is executed with the proxy role Manager, because this script needs
#       to use checkbook_module.


transaction = state_change['object']
line = transaction.get('movement')
if line is not None and line.getPortalType() == 'Banking Operation Line':
  # This is a single currency operation, so it is not necessary to convert the price.
  line.setSourceDebit(transaction.getSourceTotalAssetPrice())

#transaction.edit(aggregate = check.getRelativeUrl())
