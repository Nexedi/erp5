from Products.Formulator.Errors import ValidationError

if value < 1 or value >= 2:
  raise ValidationError('external_validator_failed', context, context.Base_translateString("The integer you entered was out of range."))
return True
