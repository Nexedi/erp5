#
#  this script is called on the Invoice Transaction
# after the advanced_invoice_transaction_builder created accounting lines in the invoice
#

# copy title
invoice_transaction = context
related_invoice = invoice_transaction.getDefaultCausalityValue()
if not invoice_transaction.hasTitle() and related_invoice is not None and related_invoice.hasTitle():
  invoice_transaction.setTitle(related_invoice.getTitle())

context.InvoiceTransaction_postTransactionLineGeneration(**kw)
