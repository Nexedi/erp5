software_publication = state_change['object']

software_publication_line = software_publication.objectValues(
  portal_type="Software Publication Line",
)[0]

software_release = software_publication_line.getAggregateValue(portal_type="Software Release")

software_product = software_release.getFollowUpValue(portal_type="Software Product")

web_site = software_product.getFollowUpValue(portal_type="Web Section")

# force a site modification date update for service worker
web_site.setReference(web_site.getReference())
