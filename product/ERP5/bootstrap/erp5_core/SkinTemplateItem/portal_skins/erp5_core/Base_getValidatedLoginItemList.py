person = context.ERP5Site_getAuthenticatedMemberPersonValue()
if person is None:
  return []
else:
  return [(x.getReference(), x.getRelativeUrl()) for x in \
          person.objectValues(portal_type='ERP5 Login') \
          if x.getValidationState() == 'validated']
