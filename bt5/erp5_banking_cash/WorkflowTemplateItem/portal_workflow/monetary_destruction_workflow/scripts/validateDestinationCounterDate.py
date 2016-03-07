from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']

source_section = transaction.getSourceSection()

# check again that we are in the good accounting date in site destination
transaction.Baobab_checkCounterDateOpen(site=source_section, date=transaction.getStopDate())
