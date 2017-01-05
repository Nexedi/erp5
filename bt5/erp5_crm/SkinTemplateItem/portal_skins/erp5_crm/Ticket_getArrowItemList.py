portal = context.getPortalObject()
arrow = portal.portal_property_sheets.get("Arrow")

result = set([('', ''),])

# add current user
user = portal.portal_membership.getAuthenticatedMember().getUserValue()
if user is not None:
  result.add((user.getTitle(), user.getRelativeUrl()))

for property_value in arrow.contentValues():
  value_list = context.getProperty("%s_value_list" %property_value.getReference(), None)
  if value_list is not None:
    for value in value_list:
      if value is not None and value.getPortalType() in portal.getPortalNodeTypeList():
        result.add((value.getTitle(), value.getRelativeUrl()))

return sorted(result)
