from Products.ERP5Type.Message import translateString

payment_transaction = context

# initialize accounting_workflow to planned state
if payment_transaction.getSimulationState() == "draft":
  payment_transaction.plan(comment=translateString("Initialised by Delivery Builder."))

sale_invoice_transaction = payment_transaction.getCausalityValue(portal_type='Sale Invoice Transaction')
if sale_invoice_transaction and sale_invoice_transaction.getDestination() == 'person_module/100':
  payment_transaction.setDestination('person_module/100')
payment_transaction.AccountingTransaction_roundDebitCredit()
