portal = context.getPortalObject()

software_release = context

web_document_list = portal.portal_catalog(
  portal_type=portal.getPortalDocumentTypeList(),
  strict_follow_up_uid=software_release.getUid(),
  validation_state="submitted",
)

for web_document in web_document_list:
  web_document.cancel()

software_product = context.getFollowUpValue(portal_type="Software Product")

web_site = software_product.SoftwareProduct_getRelatedWebSite()
version_web_section = None

if software_release.getReference() in web_site:
  version_web_section = web_site[software_release.getReference()]
#backward compatibily
if not version_web_section and software_release.getVersion() in web_site:
  version_web_section = web_site[software_release.getVersion()]

if not version_web_section:
  return

version_web_section.setCriterion('validation_state', 'cancel')
version_web_section.setTitle("Rejected " + version_web_section.getTitle())
def webSectionUpdatePredicate(current_section):
  current_section.setCriterion('validation_state', 'cancelled')
  for child_section in current_section.objectValues(portal_type="Web Section"):
    webSectionUpdatePredicate(child_section)

webSectionUpdatePredicate(version_web_section)
