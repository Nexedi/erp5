# XXX: This script is only kept in case it must be added back as a "Before" script on "_action" transition.
#      But it is not used any longer at the moment.

from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']


date = transaction.getStartDate()
source = transaction.getBaobabSource(None)
if source is None:
  msg = Message(domain='ui', message='No counter defined.')
  raise ValidationFailed(msg,)

destination_payment = transaction.getDestinationPayment()
if destination_payment is None:
  msg = Message(domain='ui', message='No account defined.')
  raise ValidationFailed(msg,)

if sum([len(x.getAggregateList()) for x in transaction.objectValues(portal_type=['Checkbook Delivery Line'])]) == 0:
  msg = Message(domain='ui', message='No checkbook selected for delivery.')
  raise ValidationFailed(msg,)  

at_date = transaction.getStartDate()
transaction.CheckbookDelivery_checkAggregateStockList(at_date=at_date, node_url = source)

# check we are in an opened accounting day (Seb, Not required any more)
# transaction.Baobab_checkCounterDateOpen(site=source, date=date)

#site = transaction.getBaobabSourceValue()

#if 'guichet' in site.getVaultType():
#  if not context.Baobab_checkCounterOpened(site):
#    msg = Message(domain = "ui", message="Counter is not opened")
#    raise ValidationFailed, (msg,)

# Check that all checks are in draft
line_list = transaction.getMovementList()

for line in line_list:
  aggregate_list = line.getAggregateValueList()
  for aggregate in aggregate_list:
    if aggregate.getPortalType()=='Check':
      if aggregate.getSimulationState() != 'draft':
        message = Message(domain='ui', message='Sorry, the check is not new')
        raise ValidationFailed(message,)
    if aggregate.getPortalType()=='Checkbook':
      if aggregate.getValidationState() != 'draft':
        message = Message(domain='ui', message='Sorry, the checkbook is not new')
        raise ValidationFailed(message,)
      for check in aggregate.objectValues(portal_type='Check'):
        if check.getSimulationState() != 'draft':
          message = Message(domain='ui',
            message='Sorry, there is a check wich is not in the new state inside the checkbook')
          raise ValidationFailed(message,)
