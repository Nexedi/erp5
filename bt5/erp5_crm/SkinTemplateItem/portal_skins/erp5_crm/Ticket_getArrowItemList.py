portal = context.getPortalObject()
arrow = portal.portal_property_sheets.get("Arrow")

value_list = [('', ''),]
value_list_append = value_list.append

# add current user
user = portal.ERP5Site_getAuthenticatedMemberPersonValue()
if user is not None:
  value_list_append((user.getTitle(), user.getRelativeUrl()))

for property_value in arrow.contentValues():
  value = context.getProperty("%s_value" %property_value.getReference(), None)
  if value and value.getPortalType() in portal.getPortalNodeTypeList():
    value = (value.getTitle(), value.getRelativeUrl())
    if value not in value_list:
      value_list_append(value)

value_list.sort(key=lambda x: x[0])

return value_list
