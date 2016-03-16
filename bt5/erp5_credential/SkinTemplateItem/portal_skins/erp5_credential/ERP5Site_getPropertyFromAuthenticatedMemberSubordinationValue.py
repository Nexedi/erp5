"""Get property on the Organisation of current user
Parameter:
  property_name -- property to get, Mandatory (String, Example: 'title')
"""
person = context.ERP5Site_getAuthenticatedMemberPersonValue()
if person is not None:
  organisation = person.getDefaultCareerSubordinationValue()
  if organisation is not None:
    return organisation.getProperty(property_name, None)
return None
