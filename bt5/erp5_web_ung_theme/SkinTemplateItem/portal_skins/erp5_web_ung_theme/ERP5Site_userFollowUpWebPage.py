portal = context.getPortalObject()
person = portal.ERP5Site_getAuthenticatedMemberPersonValue()

if not person:
  return None

web_page = portal.portal_catalog.getResultValue(reference=reference)

follow_up_list = web_page.getFollowUpList()
if person.getRelativeUrl() not in follow_up_list:
  value_list = follow_up_list
  value_list.append(person)
  web_page.setFollowUpValueList(value_list)

return web_page
