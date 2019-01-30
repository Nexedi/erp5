software_publication_line_list = context.objectValues(portal_type="Software Publication Line")
if len(software_publication_line_list) == 0:
  return
software_publication_line = software_publication_line_list[0]

software_release = software_publication_line.getAggregateValue(portal_type="Software Release")
software_product = software_publication_line.getResourceValue(portal_type="Software Product")
if not software_product or not software_release or not software_product.getFollowUpId(portal_type="Web Section"):
  return

portal = context.getPortalObject()
preference_tool = portal.portal_preferences

return "%s://%s.%s/%s/" % (
  preference_tool.getPreferredSystemAppstoreWildcardProtocol(),
  software_product.getFollowUpId(portal_type="Web Section"),
  preference_tool.getPreferredSystemAppstoreWildcardDomain(),
  software_release.getReference(),
)
