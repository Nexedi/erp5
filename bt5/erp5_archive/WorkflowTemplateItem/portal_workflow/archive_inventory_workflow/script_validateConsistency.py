from Products.ERP5Type.Message import Message
from Products.ERP5Type.Core.Workflow import ValidationFailed

inventory = state_change['object']

# Make sure the start_date is defined
start_date = inventory.getStartDate()
if start_date is None:
  text = "Sorry, you must define the inventory date"
  message = Message(domain='ui', message=text)
  raise ValidationFailed(message)

# Make sure the node is defined
node = inventory.getDestination()
if node is None:
  text = "Sorry, you must define the inventory warehouse"
  message = Message(domain='ui', message=text)
  raise ValidationFailed(message)


# use of the constraint
error_list = inventory.checkConsistency()
if len(error_list) > 0:
  raise ValidationFailed(error_list[0].getTranslatedMessage())
