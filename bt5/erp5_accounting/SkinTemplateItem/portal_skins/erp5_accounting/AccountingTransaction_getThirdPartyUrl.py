# XXX bad name: AccountingTransaction_getMirrorSectionUrl sounds more consistent
view_name = 'Entity_viewAccountingTransactionList?reset:int=1'

if brain is not None:
  transaction = brain.getObject()
else:
  transaction = context

if transaction.AccountingTransaction_isSourceView():
  mirror_section = transaction.getDestinationSectionValue()
else:
  mirror_section = transaction.getSourceSectionValue()

if mirror_section is not None:
  return '%s/%s' % (mirror_section.absolute_url(), view_name)
