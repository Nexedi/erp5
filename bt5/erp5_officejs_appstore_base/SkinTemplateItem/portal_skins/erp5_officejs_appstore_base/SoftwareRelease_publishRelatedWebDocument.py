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

version_web_section = web_site[software_release.getReference()]
version_web_section.setCriterion('validation_state', 'published')
if portal.portal_workflow.isTransitionPossible(version_web_section, 'publish'):
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
