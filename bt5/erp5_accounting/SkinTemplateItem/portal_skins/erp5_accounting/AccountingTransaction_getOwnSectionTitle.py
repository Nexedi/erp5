if brain is not None:
  transaction = brain.getObject()
else:
  transaction = context

if transaction.AccountingTransaction_isSourceView():
  own_section = transaction.getSourceSectionValue()
else:
  own_section = transaction.getDestinationSectionValue()

if own_section is not None:
  return own_section.getTitle()
