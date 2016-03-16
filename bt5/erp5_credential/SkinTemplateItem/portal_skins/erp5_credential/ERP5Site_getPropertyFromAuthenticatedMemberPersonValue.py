"""Get property on Person of current user
Parameter:
property_name -- property to get, Mandatory (String, Example: "title")"""
person = context.ERP5Site_getAuthenticatedMemberPersonValue()
if person is not None:
  return person.getProperty(property_name, None)
return None
