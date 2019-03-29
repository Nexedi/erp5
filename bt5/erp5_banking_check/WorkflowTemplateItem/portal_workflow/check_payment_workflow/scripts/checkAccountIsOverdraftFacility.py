from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']
date = transaction.getStartDate()
source = transaction.getSource(None)
if source is None:
  msg = Message(domain='ui', message='No counter defined.')
  raise ValidationFailed(msg,)

# check we are in an opened accounting day
transaction.Baobab_checkCounterDateOpen(site=source, date=date)

site = transaction.getSourceValue()

# For safety, check the consistency again.
context.validateConsistency(state_change, no_balance_check=1)

line = transaction.movement
bank_account = transaction.getDestinationPaymentValue()

if not bank_account.isOverdraftFacility():
  msg = Message(domain='ui', message="Can't sent to manual validation because of not overdraft facility for this bank account")
  raise ValidationFailed(msg,)

price = transaction.getSourceTotalAssetPrice()

# this prevents multiple transactions from being committed at the same time for this bank account.
bank_account.serialize()

# Make sure there are no other operations pending for this account
if transaction.BankAccount_isMessagePending(bank_account):
  msg = Message(domain='ui', message="There are operations pending for this account that prevent form calculating its position. Please try again later.")
  raise ValidationFailed(msg,)

# Index the banking operation line so it impacts account position
transaction.BankingOperationLine_index(line)

# Check if the banking operation is correct. Do not depend on catalog because line might not be indexed immediatelly.
if - price != (line.getPrice() * line.getQuantity()):
  msg = Message(domain='ui', message='Banking operation and check payment price do not match.')
  raise ValidationFailed(msg,)
