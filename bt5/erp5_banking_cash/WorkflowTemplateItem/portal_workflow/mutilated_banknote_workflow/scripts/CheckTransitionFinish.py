from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

ob = state_change['object']

stop_date = ob.getStopDate()
ob.Baobab_checkCounterDateOpen(site=ob.getSource(), date=stop_date)
context.Baobab_checkCounterOpened(ob.getSource())

for exchanged_line in ob.objectValues(portal_type='Exchanged Mutilated Banknote Line'):
  exchanged_line.setStartDate(stop_date)

if ob.getDestinationTotalAssetPrice() == 0:
  msg = Message(domain = "ui", message="Exchanged amount must be defined on document.")
  raise ValidationFailed(msg,)
if len(ob.objectValues(portal_type='Exchanged Mutilated Banknote Line')) == 0:
  msg = Message(domain = "ui", message="You must defined exchanged banknote line.")
  raise ValidationFailed(msg,)
exchanged_mutilated_banknote_total_price = ob.getTotalPrice(portal_type='Exchanged Mutilated Banknote Line', fast=0)
if exchanged_mutilated_banknote_total_price > ob.getTotalPrice(portal_type='Incoming Mutilated Banknote Line', fast=0):
  msg = Message(domain = "ui", message="Total exchanged greater than total supply.")
  raise ValidationFailed(msg,)
if exchanged_mutilated_banknote_total_price != ob.getDestinationTotalAssetPrice():
  msg = Message(domain = "ui", message="Exchanged amount differ between line and document.")
  raise ValidationFailed(msg,)
