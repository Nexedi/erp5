# App creation process doesn't set web site "configuration_latest_version" so app isn't redirect to its document
# this script fixes that from corresponding web section
# TODO: move this to proper script

software_release = context

software_product = context.getFollowUpValue(portal_type="Software Product")
print "software_product"
print software_product.getRelativeUrl()

web_site = software_product.SoftwareProduct_getRelatedWebSite()
print "web_site"
print web_site.getRelativeUrl()

print "software_release.getReference()"
print software_release.getReference()

print "web_site configuration_latest_version:"
print web_site.getLayoutProperty('configuration_latest_version')

web_site.edit(
  configuration_latest_version=software_release.getReference()
)

print "web_site configuration_latest_version editted!"
return printed
