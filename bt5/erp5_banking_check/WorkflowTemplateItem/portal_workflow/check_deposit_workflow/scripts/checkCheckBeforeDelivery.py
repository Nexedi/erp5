from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

obj = state_change['object']

wf_h = obj.Base_getWorkflowHistory()
wf_h = wf_h['check_deposit_workflow']['item_list']

manual_validation = 0

for h in wf_h:
  obj.log("state", h[3])
  if h[3] == "plan":
    manual_validation = 0
    break
  if h[3] == "accept":
    manual_validation = 1
    break

bank_account_dict = {}

if manual_validation:
  return
else:
  # check balance for each line
  for check_operation_line in obj.contentValues(filter = {'portal_type' : 'Check Operation Line'}):
    source_bank_account = check_operation_line.getSourcePaymentValue()
    # Test if the account balance is sufficient.
    account_path = source_bank_account.getRelativeUrl()
    if bank_account_dict.has_key(account_path):
      check_price = bank_account_dict[account_path] + check_operation_line.getPrice()      
    else:
      check_price = check_operation_line.getPrice()
    bank_account_dict[account_path] = check_price
    error = obj.BankAccount_checkBalance(account_path, check_operation_line.getPrice())
    
    if error['error_code'] == 1:
      msg = Message(domain='ui', message="Bank account $account is not sufficient on line $line.",
                    mapping={"account": source_bank_account.getInternalBankAccountNumber(), "line" : check_operation_line.getId()})
      raise ValidationFailed(msg,)
    elif error['error_code'] == 2:
      msg = Message(domain='ui', message="Bank account $account is not valid on $line.",
                    mapping={"account": source_bank_account.getInternalBankAccountNumber(), "line" : check_operation_line.getId()})
      raise ValidationFailed(msg,)
    elif error['error_code'] != 0:
      msg = Message(domain='ui', message="Unknown error code.")
      raise ValidationFailed(msg,)


context.validateSourceAndDestination(state_change)
