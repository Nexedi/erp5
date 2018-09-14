portal = context.getPortalObject()
result = []

software_publication_list = portal.portal_catalog(
  **kw
)
for software_publication in software_publication_list:
  software_publication_line = software_publication.objectValues(
    portal_type="Software Publication Line"
  )[0]
  if context.getRelativeUrl() == software_publication_line.getResource():
    result.append(software_publication)
return result
