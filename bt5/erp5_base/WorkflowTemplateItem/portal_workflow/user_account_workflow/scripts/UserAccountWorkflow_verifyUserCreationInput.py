from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import translateString

if len(object.searchFolder(portal_type="ERP5 Login", validation_state="validated", limit=1)):
  raise ValidationFailed(translateString("Account already created."))

kwargs = state_change['kwargs']
password = kwargs['password']
password_confirm = kwargs['password_confirm']
if password != password_confirm:
  raise ValidationFailed(translateString('Passwords do not match.'))

reference = kwargs['reference']
if not reference:
  raise ValidationFailed(translateString('User Login is not specified.'))
