# This scripts sets the stop date on current cash movement.
# This is done to prevent users from destination site from
# editing the document values, but still allowing them to set that value.
# Hence, this script must have a proxy role to modify what user cannot.
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message
transaction = state_change['object']
stop_date_key = 'stop_date'
if not state_change.kwargs.has_key(stop_date_key):
  msg = Message(domain = "ui", message="No stop date provided")
  raise ValidationFailed(msg,)
transaction.setStopDate(state_change.kwargs[stop_date_key])
context.validateDestinationCounterDate(state_change, **kw)
