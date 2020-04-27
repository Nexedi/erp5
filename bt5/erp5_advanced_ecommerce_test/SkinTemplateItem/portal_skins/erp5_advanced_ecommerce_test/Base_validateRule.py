for rule in context.portal_rules.contentValues():
  if rule.getValidationState() == 'draft':
    rule.validate()
return 'Done'
