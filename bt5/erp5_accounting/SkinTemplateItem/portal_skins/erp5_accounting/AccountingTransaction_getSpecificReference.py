"""Return the 'side-specific' reference, ie. the source reference or
destination reference.
"""
if brain is not None:
  transaction = brain.getObject()
else:
  transaction = context

if transaction.AccountingTransaction_isSourceView():
  return transaction.getSourceReference()
return transaction.getDestinationReference()
