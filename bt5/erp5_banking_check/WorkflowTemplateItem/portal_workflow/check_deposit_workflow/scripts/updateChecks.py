transaction = state_change['object']

if not transaction.isCheckLess():
  for check_operation_line in transaction.contentValues(filter = {'portal_type' : 'Check Operation Line'}):
    check = check_operation_line.getAggregateValue()
    check.deliver()
