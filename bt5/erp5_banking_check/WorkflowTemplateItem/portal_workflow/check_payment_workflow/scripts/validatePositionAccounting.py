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

transaction.Baobab_checkCounterOpened(site)

# For safety, check the consistency again.
context.validateConsistency(state_change, no_balance_check=1)

line = transaction.movement
bank_account = transaction.getDestinationPaymentValue()
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

# Test if the account balance is sufficient.
if state_change['transition'].getId() != "agree_action":
  error = transaction.BankAccount_checkAvailableBalance(bank_account.getRelativeUrl(), price)
  if error['error_code'] == 1:
    msg = Message(domain='ui', message="Bank account is not sufficient.")
    raise ValidationFailed(msg,)
  elif error['error_code'] == 2:
    msg = Message(domain='ui', message="Bank account is not valid.")
    raise ValidationFailed(msg,)
  elif error['error_code'] != 0:
    msg = Message(domain='ui', message="Unknown error code.")
    raise ValidationFailed(msg,)
