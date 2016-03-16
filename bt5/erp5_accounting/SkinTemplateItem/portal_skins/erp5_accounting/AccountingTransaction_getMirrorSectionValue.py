if context.AccountingTransaction_isSourceView():
  return context.getDestinationSectionValue()
return context.getSourceSectionValue()
