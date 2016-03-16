if value.strip() or REQUEST.get('field_your_support_request_template'):
  return True
from Products.Formulator.Errors import ValidationError
raise ValidationError('external_validator_failed', context, error_text='Required when no template is used')
