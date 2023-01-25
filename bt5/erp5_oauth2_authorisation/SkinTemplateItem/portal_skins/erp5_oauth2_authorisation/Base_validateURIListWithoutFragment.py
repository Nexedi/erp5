from Products.Formulator.Errors import ValidationError
for uri in uri_list:
  if '#' in uri:
    raise ValidationError(
      'external_validator_failed',
      context, # The field which called us
      error_text='URI must not contain any fragment ("#" followed by anything)',
    )
return True
