from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

ob = state_change['object']

# check presence of banknote
if len(ob.objectValues(portal_type="Exchanged Mutilated Banknote Line")) != 0:
  msg = Message(domain = "ui", message="Transition forbidden with exchanged banknote line defined.")
  raise ValidationFailed(msg,)
