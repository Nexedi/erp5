portal = context.getPortalObject()
software_release = context

# Publish Web Document
web_document_list = portal.portal_catalog(
  portal_type=portal.getPortalDocumentTypeList(),
  strict_follow_up_uid=software_release.getUid(),
  validation_state="submitted",
)

today = DateTime().earliestTime()
for web_document in web_document_list:
  web_document.setEffectiveDate(today)
  web_document.publish()

software_product = context.getFollowUpValue(portal_type="Software Product")
web_site = software_product.SoftwareProduct_getRelatedWebSite()

# Publish Web Site, Websection and update version
today = DateTime().earliestTime()
if web_site.getValidationState() != 'published':
  web_site.setEffectiveDate(today)
  web_site.publish()

version_web_section = web_site[software_release.getVersion()]
version_web_section.setCriterion('validation_state', 'published')
version_web_section.publish()

def webSectionUpdatePredicate(current_section):
  current_section.setCriterion('validation_state', 'published')
  for child_section in current_section.objectValues(portal_type="Web Section"):
    webSectionUpdatePredicate(child_section)

webSectionUpdatePredicate(version_web_section)


web_site.edit(
  configuration_latest_version=software_release.getVersion(),
)

# Update appcache
web_manifest_reference = web_site.getId() + ".appcache"
web_manifest = portal.portal_catalog.getResultValue(
  portal_type="Web Manifest",
  reference=web_manifest_reference,
  )

if not web_manifest:
  web_manifest = portal.web_page_module.newContent(
    portal_type="Web Manifest",
    reference=web_manifest_reference,
    title=web_site.getTitle() + " Manifest",
    )
  web_manifest.publishAlive()

web_manifest.setData("""CACHE MANIFEST
# generated on %s
CACHE:
NETWORK:
*""" % (DateTime().rfc822()))


# Is latest Websection what we want?
if "latest" not in web_site.objectIds():
  latest_web_section = version_web_section.Base_createCloneDocument(batch_mode=True)
  latest_web_section.setId("latest")
  latest_web_section.publish()
else:
  latest_web_section = web_site['latest']
  # Update Aggregate, Version and Title
  latest_web_section.setCriterion('version', software_release.getVersion())
  latest_web_section.setTitle(version_web_section.getTitle())
  latest_web_section.setAggregate(version_web_section.getAggregate())
