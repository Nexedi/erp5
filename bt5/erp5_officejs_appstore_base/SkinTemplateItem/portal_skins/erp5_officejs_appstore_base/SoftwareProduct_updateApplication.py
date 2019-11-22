import hashlib
from DateTime import DateTime

portal = context.getPortalObject()
software_product = context

now = DateTime()
version_title = str(now)

# Generate Version Number
# XXX Should Check that version of this software doesn't already exists
version = hashlib.sha224("%s-%s" % (version_title, now)).hexdigest()[:10]
tag = "new_software_publication_" + version

# Create Software Publication
# It carries the software publication process
software_publication = portal.software_publication_module.newContent(
  portal_type="Software Publication",
  description=changelog,
  source=software_product.getSource(),
  # We should probably use a more simple reference using an incremental id generator
  reference="SP-" + version,
  title='%s publication %s' % (software_product.getTitle(), version_title),
  start_date=now,
  #Wait for all related documents indexation, to avoid issue with officejs submit alarm.
  activate_kw={"after_tag": tag}
)

# Create Software Release
# This is the result of the publication process. It is an aggregate of the line
software_release = portal.software_release_module.newContent(
  portal_type="Software Release",
  reference=version,
  title='%s release %s-%s' % (software_product.getTitle(), version_title, version),
  version=version_title,
  follow_up_value=software_product,
  activate_kw={"tag": tag}
)

# Create Software Publication Line
software_publication.newContent(
  portal_type="Software Publication Line",
  title=software_publication.getTitle() + " Publication",
  aggregate_list=[software_release.getRelativeUrl(), software_product.getSaleSupplyLineAggregate()],
  resource_value=software_product,
  activate_kw={"tag": tag}
)

software_publication.Base_contribute(
  file=file,
  attach_document_to_context=True,
  portal_type="File",
  publication_section="publication_section/application/package",
  redirect_to_document=False,
  version=version,
  activate_kw={"tag": tag}
)

return software_publication.Base_redirect(
  "",
  keep_items={
    'portal_status_message': portal.Base_translateString("Your demand is being processed, please wait status to move to 'Submitted' to review your application before final submission")
  }
)
