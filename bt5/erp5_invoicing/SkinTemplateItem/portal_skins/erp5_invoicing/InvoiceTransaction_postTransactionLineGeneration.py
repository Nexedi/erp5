#
#  this script is called on the Invoice Transaction
# after the invoice_transaction_builder delivery builder
# created accounting lines in the invoice
# 

# Accounting specific: 
#  if every lines have the same resource, then copy the resource 
# on the Transaction and delete resource on the lines.
# TODO: this is a Property Assignment Movement Group

line_list = context.objectValues(
  portal_type=context.getPortalAccountingMovementTypeList())
resource_set = set(line.getResource() for line in line_list)
try:
  resource, = resource_set
except ValueError:
  raise ValueError("%s doesn't have only one resource %s" % (
              context.getPath(), list(resource_set)))
if context.getResource() != resource:
  # set the resource on the transaction
  context.setResource(resource)
# and delete on the invoice lines, so that if the user changes
# the ressource on the transaction, it also change on the lines.
for line in line_list:
  line.setResource(None)
  assert line.getResource() == resource


# XXX Jérome: this is not backported yet.
# If payments transactions were already built, we update these
# payment transactions causalities to add this new invoice.
payment_transaction_set = set([])
for delivery in context.getCausalityValueList():
  payment_transaction_set.update(
    delivery.getCausalityRelatedValueList(portal_type='Payment Transaction'))
  for order in delivery.getCausalityValueList():
    payment_transaction_set.update(
      order.getCausalityRelatedValueList(portal_type='Payment Transaction'))
for payment_transaction in payment_transaction_set:
  if context not in payment_transaction.getCausalityValueList():
    payment_transaction.setCausalityValueList(payment_transaction.getCausalityValueList() + [context])

# round debit / credit on created transaction.
context.AccountingTransaction_roundDebitCredit()
