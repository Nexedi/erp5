# InvoiceTransaction_postGeneration
accounting_transaction = context

related_packing_list = accounting_transaction.getDefaultCausalityValue()
if not accounting_transaction.hasTitle() and related_packing_list is not None and related_packing_list.hasTitle():
  accounting_transaction.setTitle(related_packing_list.getTitle())

resource = None
ledger = None
for accounting_transaction_line in accounting_transaction.contentValues(portal_type='Accounting Transaction Line'):
  line_resource = accounting_transaction_line.getResource()
  if resource is None:
    resource = line_resource
  else:
    assert resource == line_resource
  accounting_transaction_line.setResource(None)

  line_ledger = accounting_transaction_line.getLedger()
  if ledger is None:
    ledger = line_ledger
  else:
    assert ledger == line_ledger
  accounting_transaction_line.setLedger(None)

accounting_transaction.setResource(resource)
accounting_transaction.setLedger(ledger)
