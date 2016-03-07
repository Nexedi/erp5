from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']

vaultDestination = transaction.getDestination()

if not transaction.isCurrencyHandover():
  # check again that we are in the good accounting date in site destination
  transaction.Baobab_checkCounterDateOpen(site=vaultDestination, date=transaction.getStopDate())
