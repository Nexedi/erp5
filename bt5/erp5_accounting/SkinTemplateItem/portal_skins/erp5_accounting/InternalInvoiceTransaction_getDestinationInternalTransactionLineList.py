section = context.getDestinationSection()
def isDestinationLine(line):
  if line.getDestinationSection() != section:
    return False
  if line.getSource(portal_type='Account') and not line.getDestination(portal_type='Account'):
    return False
  return True

return [line for line in
        context.AccountingTransaction_getAccountingTransactionLineList(*args, **kw)
        if isDestinationLine(line)]
