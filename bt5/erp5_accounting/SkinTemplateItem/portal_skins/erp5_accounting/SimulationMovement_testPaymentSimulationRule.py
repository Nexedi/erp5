movement = context

parent = movement.getParentValue()
if parent.getPortalType() != 'Applied Rule':
  return False

if parent.getSpecialiseReference() != 'default_invoice_transaction_rule':
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
