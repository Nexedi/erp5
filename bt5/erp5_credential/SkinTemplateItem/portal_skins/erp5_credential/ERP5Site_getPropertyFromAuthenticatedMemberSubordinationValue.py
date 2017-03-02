"""Get property on the Organisation of current user
Parameter:
  property_name -- property to get, Mandatory (String, Example: 'title')
"""
person = context.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()
if person is not None:
  organisation = person.getDefaultCareerSubordinationValue()
  if organisation is not None:
    return organisation.getProperty(property_name, None)
return None
