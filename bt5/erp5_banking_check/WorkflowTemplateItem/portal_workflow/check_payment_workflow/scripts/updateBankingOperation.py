# Note: this script is executed with the proxy role Manager, because this script needs
#       to use checkbook_module.
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']
bank_account = transaction.getDestinationPaymentValue()
check_number = transaction.getAggregateFreeText()

# Already done before in validateConsistency
#check = transaction.Base_checkOrCreateCheck(reference=check_number)
#if not check.Check_isValid():
#  raise ValidationFailed, Message(domain='ui', message='Check is in an invalid state')

line = transaction.get('movement')
if line is not None and line.getPortalType() == 'Banking Operation Line':
  # This is a single currency operation, so it is not necessary to convert the price.
  line.setSourceDebit(transaction.getSourceTotalAssetPrice())
