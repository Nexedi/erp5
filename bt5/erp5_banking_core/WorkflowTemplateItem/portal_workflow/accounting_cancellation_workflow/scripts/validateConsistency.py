from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']

#context.checkUserPermission(state_change)

site = transaction.getSite()
date = transaction.getStartDate()
# No need to check counter date, only accounting date
transaction.Base_checkConsistency()
transaction.Baobab_checkAccountingDateOpen(site=site, date=date)


# Check some properties of document
price = transaction.getSourceTotalAssetPrice()
if price is None or price <= 0:
  msg = Message(domain='ui', message='Amount is not valid.')
  raise ValidationFailed(msg,)
if transaction.getSiteValue() is None:
  msg = Message(domain='ui', message='Sorry, no site defined.')
  raise ValidationFailed(msg,)
if transaction.getResource() is None:
  msg = Message(domain='ui', message='No resource defined.')
  raise ValidationFailed(msg,)

# Check the source bank account.
source_bank_account = transaction.getSourcePaymentValue()

# test we have account transfer line defined
nb_transfer_line = len(transaction.objectValues(portal_type='Accounting Cancellation Line'))
if  nb_transfer_line == 0:
  msg = Message(domain='ui', message='You must add line before validating the operation')
  raise ValidationFailed(msg,)

# only one line can be defined with SICA/STAR, on order as it can be cancel or reject later
#if transaction.getExternalSoftware() in ('sica', 'star') and nb_transfer_line != 1:
#  msg = Message(domain='ui', message='You can defined only one lines when using SICA')
#  raise ValidationFailed, (msg,)  

# Check each line
total_line_price = 0
for line in transaction.objectValues(portal_type='Accounting Cancellation Line'):
  total_line_price += abs(line.getQuantity())
  # First check there is something defined on line
  if line.getSourcePaymentReference(None) is None and \
         line.getSourceSection() is None:
    msg = Message(domain='ui', message="No account defined on line.")
    raise ValidationFailed(msg,)
  # check we don't have both account and accounting code defined
  if line.getDestinationPayment(None) is not None \
        and line.getDestinationSection() is not None:
    msg = Message(domain='ui', message="You can't defined account and accounting code on line.")
    raise ValidationFailed(msg,)
  # check that at least destination_payment or destination_section is defined
  if line.getDestinationPayment() is None and \
      line.getDestinationSection() is None:
    msg = Message(domain='ui', message="Destination account is not defined.")
    raise ValidationFailed(msg,)
  # Index the banking operation line so it impacts account position
  if line.getSourcePaymentReference() not in (None, ''):
    context.BankingOperationLine_index(line, source=1)

if total_line_price != transaction.getSourceTotalAssetPrice():
  msg = Message(domain='ui', message="Total price doesn't match between line and document.")
  raise ValidationFailed(msg,)
