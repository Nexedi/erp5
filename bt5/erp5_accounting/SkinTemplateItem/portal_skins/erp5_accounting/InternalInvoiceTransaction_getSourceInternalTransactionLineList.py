section = context.getSourceSection()
def isSourceLine(line):
  if line.getSourceSection() != section:
    return False
  if line.getDestination(portal_type='Account') and not line.getSource(portal_type='Account'):
    return False
  return True

return [line for line in
        context.AccountingTransaction_getAccountingTransactionLineList(*args, **kw)
        if isSourceLine(line)]
