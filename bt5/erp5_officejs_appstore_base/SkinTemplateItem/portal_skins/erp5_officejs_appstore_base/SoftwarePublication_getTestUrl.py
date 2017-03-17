software_publication_line_list = context.objectValues(portal_type="Software Publication Line")
if len(software_publication_line_list) == 0:
  return
software_publication_line = software_publication_line_list[0]

software_release = software_publication_line.getAggregateValue(portal_type="Software Release")
software_product = software_publication_line.getResourceValue(portal_type="Software Product")
if not software_product or not software_release:
  return

software_release_version = software_release.getReference()
#if as_link:
#  return '<a href="%(link)s">%(link)s</a>' % {"link": (software_product.getFollowUpValue(portal_type="Web Site")[software_release_version].absolute_url() + "/")}

return software_product.getFollowUpValue(portal_type="Web Site")[software_release_version].absolute_url() + "/"
