portal = context.getPortalObject()
software_release = context

software_product = context.getFollowUpValue(portal_type="Software Product")
web_site = software_product.SoftwareProduct_getRelatedWebSite()

web_site.edit(
  configuration_latest_version=software_release.getReference(),
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
