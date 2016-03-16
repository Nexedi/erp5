from Products.ERP5Type.Message import Message
from Products.DCWorkflow.DCWorkflow import ValidationFailed

inventory = state_change['object']

# use of the constraint
inventory.Base_checkConsistency()
