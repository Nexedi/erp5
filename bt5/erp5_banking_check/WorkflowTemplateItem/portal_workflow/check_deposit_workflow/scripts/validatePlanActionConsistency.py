from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']

# Test if the account balance is sufficient.
bank_account_dict = {}
amount_dict = {}
for check_operation_line in transaction.objectValues(portal_type='Check Operation Line'):
  account_value = check_operation_line.getSourcePaymentValue()
  account_path = account_value.getRelativeUrl()
  bank_account_dict[account_path] = account_value
  amount_dict[account_path] = amount_dict.get(account_path, 0) + check_operation_line.getPrice()
for account_path, amount in amount_dict.items():
  error = transaction.BankAccount_checkBalance(account_path, amount)['error_code']
  source_bank_account = bank_account_dict[account_path]
  if error == 1:
    raise ValidationFailed(Message(domain='ui', message="Bank account $account is not sufficient.",
      mapping={"account": source_bank_account.getInternalBankAccountNumber()}),)
  elif error == 2:
    raise ValidationFailed(Message(domain='ui', message="Bank account $account is not valid.",
      mapping={"account": source_bank_account.getInternalBankAccountNumber()}),)
  elif error != 0:
    raise ValidationFailed(Message(domain='ui', message="Unknown error code."),)

context.validateConsistency(state_change)

if transaction.getSimulationState() == "draft":
  context.createCheckDepositLine(state_change)
