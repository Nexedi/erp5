from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message
if reference is None:
  msg = Message(domain='ui', message="Check not defined.")
  raise ValidationFailed(msg,)
model_list = [x
  for x in context.checkbook_model_module.objectValues()
  if x.getReference() == reference
  and x.isUniquePerAccount() == unique_per_account
]
model_list_len = len(model_list)
if model_list_len == 0:
  msg = Message(domain='ui', message="Check not defined.")
  raise ValidationFailed(msg,)
if model_list_len > 1:
  msg = Message(domain='ui', message="Two many check models with this reference.")
  raise ValidationFailed(msg,)
return model_list[0]
