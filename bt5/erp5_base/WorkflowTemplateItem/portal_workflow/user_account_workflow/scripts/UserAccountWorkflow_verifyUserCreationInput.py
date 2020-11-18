from Products.ERP5Type.Core.Workflow import ValidationFailed
from Products.ERP5Type.Message import translateString

kwargs = state_change['kwargs']
password = kwargs['password']
password_confirm = kwargs['password_confirm']
if password != password_confirm:
  raise ValidationFailed(translateString('Passwords do not match.'))

reference = kwargs['reference']
if not reference:
  raise ValidationFailed(translateString('User Login is not specified.'))
