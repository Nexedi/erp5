movement = context

parent = movement.getParentValue()
if parent.getPortalType() != 'Applied Rule':
  return False

if parent.getSpecialiseReference() != 'default_invoice_transaction_rule':
  return False

# For shop sale
if 'business_process_module/5/accounting_credit_path' in movement.getCausalityList() and parent.getParentValue().getDestination() != 'person_module/100':
  return False

# XXX hardcoded
receivable_account_type_list = ('asset/receivable',)
payable_account_type_list = ('liability/payable',)

for account in (movement.getSourceValue(portal_type='Account'),
                movement.getDestinationValue(portal_type='Account')):
  if account is not None:
    account_type = account.getAccountType()
    if account_type in receivable_account_type_list or \
        account_type in payable_account_type_list:
      return True

return False
