for i in context.portal_catalog(portal_type='Expense Validation Request'):
  sourceReference = i.getSourceReference()
  if sourceReference:
    if i.getReference() != sourceReference:
      if migrate:
        i.setReference(sourceReference)
      print i.getRelativeUrl()

return printed
