from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

object = state_change['object']

# Check that the destination is not empty
destination = object.getDestination()
if destination is None:
  message = Message(domain="ui",message="Please select a destination")
  raise ValidationFailed(message,)

# Check that the destination is not empty
description = object.getDescription()
if description in (None, ''):
  message = Message(domain="ui",message="Please set a description")
  raise ValidationFailed(message,)

# Check that there is a least one line
if len(object.objectValues())==0:
  message = Message(domain="ui",message="Please enter some check or checkbooks")
  raise ValidationFailed(message,)
