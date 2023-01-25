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

# round debit / credit on created transaction.
context.AccountingTransaction_roundDebitCredit()
