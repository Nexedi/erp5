person = context.ERP5Site_getAuthenticatedMemberPersonValue()
if person is not None:
  return [login for login in person.objectValues(portal_type='ERP5 Login')]
else:
  return []
