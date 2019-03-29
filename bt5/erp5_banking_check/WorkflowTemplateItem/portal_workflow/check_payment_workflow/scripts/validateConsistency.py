from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message
from DateTime import DateTime

transaction = state_change['object']

site = transaction.Baobab_getUserAssignedSiteList()

if len(site) > 0:
  site = site[0]
else:
  site = None
  # try to guess site from document if source is defined
  # XXX useful for unit test
  site = transaction.getSourceValue()
  while True:
    if not hasattr(site, 'getVaultTypeList'):
      msg = Message(domain = 'ui', message = 'The site value is misconfigured; report this to system administrators.')
      raise ValidationFailed(msg,)
    if 'site' in site.getVaultTypeList():
      break
    site = site.getParentValue()

if site is None:
  msg = Message(domain = 'ui', message = 'Impossible to determine site for the transaction.')
  raise ValidationFailed(msg,)


date = transaction.getStartDate()

# check accounting date
current_date = DateTime().Date()
document_date = DateTime(date).Date()
# Do not check the counter date, not required at this stage
#if not document_date > current_date:
#  transaction.Baobab_checkCounterDateOpen(site=site, date=date)


# Check the amount.
price = transaction.getSourceTotalAssetPrice() 
if price is None or price <= 0:
  msg = Message(domain="ui", message="Amount is not valid.")
  raise ValidationFailed(msg,)

# Check the bank account.
bank_account = transaction.getDestinationPaymentValue()
if bank_account is None:
  msg = Message(domain='ui', message='Bank account is not defined.')
  raise ValidationFailed(msg,)

# Check the check.
check_number = transaction.getAggregateFreeText()

# bind check payment with check model
check_resource = bank_account.BankAccount_getCheckModel(
  unique_per_account=transaction.isUniquePerAccount(),
).getRelativeUrl()
transaction.edit(aggregate_resource=check_resource)

if not check_number:
  msg = Message(domain='ui', message="Check not defined.")
  raise ValidationFailed(msg,)
if check_resource is None:
  msg = Message(domain='ui', message="Check type not defined.")
  raise ValidationFailed(msg,)

check = transaction.Base_checkCheck(reference=check_number, bank_account=bank_account, 
                            resource=check_resource)
transaction.edit(aggregate=check.getRelativeUrl())

context.updateBankingOperation(state_change)

if no_balance_check == 1:
  return

# Test if the account balance is sufficient.
# We do not need to serialize here because we do not make
# reservation yet
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
