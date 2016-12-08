person = context.ERP5Site_getAuthenticatedMemberPersonValue()
if person is None:
  return []
else:
  return [x.getReference() for x in person.objectValues(portal_type=portal_type) \
          if x.getValidationState() == 'validated']
