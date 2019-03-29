from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

ob = state_change['object']

ob.Baobab_checkCounterDateOpen(site=ob.getSource(), date=ob.getStartDate())



# check presence of banknote
if len(ob.objectValues()) == 0:
  msg = Message(domain = "ui", message="No mutilated banknotes defined.")
  raise ValidationFailed(msg,)

# check price defined
if ob.getSourceTotalAssetPrice() != ob.getTotalPrice(portal_type='Incoming Mutilated Banknote Line', fast=0):
  msg = Message(domain = "ui", message="Amount differ between document and line.")
  raise ValidationFailed(msg,)

# check reporter defined
if ob.getDeponent() in (None, ""):
  msg = Message(domain = "ui", message="You must define a reporter.")
  raise ValidationFailed(msg,)

# check original site defined is hq
if "siege" in ob.getSource() and ob.getSourceTrade() is None:
  msg = Message(domain = "ui", message="You must define the original site.")
  raise ValidationFailed(msg,)
