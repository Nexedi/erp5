portal = context.getPortalObject()
person = context.ERP5Site_getAuthenticatedMemberPersonValue()

# Generate Version Number
# XXX Should Check that version of this software doesn't already exists
import hashlib
version = hashlib.sha224("%s-%s" % (version_title, DateTime())).hexdigest()[:10]
tag = "new_software_publication_" + version

# Create Software Publication
# It carries the software publication process
software_publication = portal.software_publication_module.newContent(
  portal_type="Software Publication",
  description=changelog,
  source=person.getRelativeUrl(),
  # We should probably use a more simple reference using an incremental id generator
  reference="SP-" + version,
  title='publication ' + version_title,
  start_date=DateTime(),
  #Wait for all related documents indexation, to avoid issue with officejs submit alarm.
  activate_kw={"after_tag": tag}
)

# Create Software Release
# This is the result of the publication process. It is an aggregate of the line
software_release = portal.software_release_module.newContent(
  portal_type="Software Release",
  reference=version,
  title='release ' + version_title + '-' + version,
  version=version_title,
  activate_kw={"tag": tag}
)

# Create Software Publication Line
software_publication_line = software_publication.newContent(
  portal_type="Software Publication Line",
  title=software_publication.getTitle() + " Publication",
  aggregate=[
    software_release.getRelativeUrl(),
  ],
  activate_kw={"tag": tag}
)

zip_file = software_publication.Base_contribute(
  file=file,
  attach_document_to_context=True,
  portal_type="File",
  publication_section="publication_section/application/package",
  redirect_to_document=False,
  version=version,
)

return software_publication.SoftwarePublication_attachSoftwareProduct(
  relative_url=software_product,
  title=title,
  description=description,
  product_line=product_line,
  activate_kw={"tag": tag}
)
