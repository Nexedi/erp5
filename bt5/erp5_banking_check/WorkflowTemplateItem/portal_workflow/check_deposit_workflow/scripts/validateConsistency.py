from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message
from Products.ERP5Type.DateUtils import getIntervalBetweenDates

transaction = state_change['object']

site = transaction.getSite()
date = transaction.getStartDate()
transaction.Baobab_checkAccountingDateOpen(site=site, date=date)

# Check we don't defined accounting code and account
if transaction.getDestinationSection() not in ("", None) and \
       transaction.getDestinationPayment() not in ("", None):
  msg = Message(domain='ui', message="You can't defined both account and accounting code.")
  raise ValidationFailed(msg,)
  
if transaction.getDestinationSection() in ("", None) and \
       transaction.getDestinationPayment() in ("", None):
  msg = Message(domain='ui', message="You must defined an account or and accounting code as destination.")
  raise ValidationFailed(msg,)

if transaction.getSite() in ("", None):
  msg = Message(domain='ui', message="You must defined site on document.")
  raise ValidationFailed(msg,)

# Check the amount.
price = transaction.getSourceTotalAssetPrice()
if price is None or price <= 0:
  msg = Message(domain='ui', message='Amount is not valid.')
  raise ValidationFailed(msg,)

# Check the bank account.
destination_bank_account = transaction.getDestinationPaymentValue()
if destination_bank_account is not None:
  if destination_bank_account.getValidationState() != 'valid':
    msg = Message(domain='ui', message='Destination bank account is not valid.')
    raise ValidationFailed(msg,)

# Check if the total price is equal to the total asset price.
if transaction.getTotalPrice(fast=0, portal_type = 'Check Operation Line') != transaction.getSourceTotalAssetPrice():
  msg = Message(domain='ui', message="Total price doesn't match.")
  raise ValidationFailed(msg,)

seen_check_dict = {}

is_check_less = transaction.isCheckLess()

# Check each check operation line.
for check_operation_line in transaction.contentValues(filter = {'portal_type' : 'Check Operation Line'}):

  if check_operation_line.getDescription() in (None, ''):
    msg = Message(domain='ui', message='The description is not defined on line $line.'
                  , mapping={"line" : check_operation_line.getId()})
    raise ValidationFailed(msg,)

  source_bank_account = check_operation_line.getSourcePaymentValue()
  if source_bank_account is None:
    msg = Message(domain='ui', message='Bank account not defined on line $line.'
                  , mapping={"line" : check_operation_line.getId()})
    raise ValidationFailed(msg,)

  check_number = check_operation_line.getAggregateFreeText()
  check_type = check_operation_line.getAggregateResource()
  if is_check_less:
    if check_number:
      msg = Message(domain='ui', message='Check is defined on line $line.'
                    , mapping={"line" : check_operation_line.getId()})
      raise ValidationFailed(msg,)

    if check_type is not None:
      msg = Message(domain='ui', message='Check type is defined on line $line.'
                    , mapping={"line" : check_operation_line.getId()})
      raise ValidationFailed(msg,)
  else:
    if not check_number:
      msg = Message(domain='ui', message='Check is not defined on line $line.'
                    , mapping={"line" : check_operation_line.getId()})
      raise ValidationFailed(msg,)

    if check_type is None:
      msg = Message(domain='ui', message='Check type is not defined on line $line.'
                    , mapping={"line" : check_operation_line.getId()})
      raise ValidationFailed(msg,)

    seen_check_dict_key = (source_bank_account, check_type, check_number)
    seen_check = seen_check_dict.get(seen_check_dict_key)
    if seen_check is not None:
      msg = Message(domain='ui', message='Check on line $line is already used on line $oldline.'
                    , mapping={"line" : check_operation_line.getId(), "oldline": seen_check})
      raise ValidationFailed(msg,)
    seen_check_dict[seen_check_dict_key] = check_operation_line.getId()

    # Test check is valid based on date
    transaction.Check_checkIntervalBetweenDate(resource=check_operation_line.getAggregateResourceValue(),
                                               start_date=check_operation_line.getIssueDate(),
                                               stop_date=check_operation_line.getStopDate(),
                                               check_nb=check_operation_line.getAggregateFreeText())
    check = transaction.Base_checkCheck(bank_account=source_bank_account, reference=check_number,
                                resource=check_type)
    if check_operation_line.getAggregate() != check.getRelativeUrl():
      check_operation_line.edit(aggregate=check.getRelativeUrl())
