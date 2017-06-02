software_publication_line_list = context.objectValues(portal_type="Software Publication Line")
if len(software_publication_line_list) == 0:
  return
software_publication_line = software_publication_line_list[0]

software_release = software_publication_line.getAggregateValue(portal_type="Software Release")
software_product = software_publication_line.getResourceValue(portal_type="Software Product")
if not software_product or not software_release or not software_product.getFollowUpId(portal_type="Web Section"):
  return

# XXX Hardcoded
return "https://%s.app.officejs.com/%s/" % (
  software_product.getFollowUpId(portal_type="Web Section"),
  software_release.getReference(),
)
