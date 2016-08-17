portal = context.getPortalObject()
arrow = portal.portal_property_sheets.get("Arrow")

result = [('', ''),]
result_append = result.append

# add current user
user = portal.ERP5Site_getAuthenticatedMemberPersonValue()
if user is not None:
  result_append((user.getTitle(), user.getRelativeUrl()))

for property_value in arrow.contentValues():
  value_list = context.getProperty("%s_value_list" %property_value.getReference(), None)
  if value_list is not None:
    for value in value_list:
      if value and value.getPortalType() in portal.getPortalNodeTypeList():
        value = (value.getTitle(), value.getRelativeUrl())
        if value not in value_list:
          result_append(value)

result.sort(key=lambda x: x[0])

return result
