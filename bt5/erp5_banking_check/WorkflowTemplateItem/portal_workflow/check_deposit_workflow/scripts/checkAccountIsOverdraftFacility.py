from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

txn = state_change['object']

for line in  txn.contentValues(filter = {'portal_type' : 'Check Operation Line'}):
  
  account = line.getSourcePaymentValue()

  if account is None:
    msg = Message(domain='ui', message="No account defined on line")
    raise ValidationFailed(msg,)

  if not account.isOverdraftFacility():
    msg = Message(domain='ui', message="Can't sent to manual validation because of not overdraft facility for this bank account")
    raise ValidationFailed(msg,)
