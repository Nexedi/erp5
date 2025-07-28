from Products.ERP5Type.Utils import isValidTALESExpression
from Products.Formulator.Errors import ValidationError
if not value:
  return True

valid, message = isValidTALESExpression("python: getindex[%s]" % value)
if valid:
  return True
raise ValidationError('external_validator_failed', context, error_text=message)
