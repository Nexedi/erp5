from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

ob = state_change['object']    

source = ob.getSource()

# check we are in an opened accounting day
vault = '%s/encaisse_des_billets_et_monnaies/sortante' % (source, )
date = ob.getStopDate()
ob.Baobab_checkCounterDateOpen(site=vault, date=date)

# check again that the counter is open
context.Baobab_checkCounterOpened(source)

for outgoing_line in ob.objectValues(portal_type="Outgoing Mutilated Banknote Line"):
  outgoing_line.setStartDate(date)

if len(ob.objectValues(portal_type="Outgoing Mutilated Banknote Line")) == 0:
  msg = Message(domain = "ui", message="You must defined returned banknote.")
  raise ValidationFailed(msg,)
if ob.getDestinationTotalAssetPrice() != ob.getTotalPrice(portal_type="Outgoing Mutilated Banknote Line", fast=0):
  msg = Message(domain = "ui", message="Returned value different from exchanged value.")
  raise ValidationFailed(msg,)
# now check balance
resource = ob.CashDelivery_checkCounterInventory(source=vault, portal_type='Outgoing Mutilated Banknote Line', same_source=1)
if resource == 2:
  msg = Message(domain="ui", message="No Returned banknote defined.")
  raise ValidationFailed(msg,)
elif resource != 0 :
  msg = Message(domain="ui", message="Insufficient Balance.")
  raise ValidationFailed(msg,)
