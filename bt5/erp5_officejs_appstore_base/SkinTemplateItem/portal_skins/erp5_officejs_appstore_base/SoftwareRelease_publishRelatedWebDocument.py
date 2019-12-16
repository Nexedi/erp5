software_release = context

software_product = context.getFollowUpValue(portal_type="Software Product")
web_site = software_product.SoftwareProduct_getRelatedWebSite()

web_site.edit(
  configuration_latest_version=software_release.getReference()
)
