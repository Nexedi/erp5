software_release = context.SoftwarePublication_getRelatedSoftwareRelease()
software_product = software_release.getFollowUpValue(portal_type="Software Product")
web_site = software_product.SoftwareProduct_getRelatedWebSite()
select = ""
if web_site is not None and software_release.getReference() == web_site.getLayoutProperty('configuration_latest_version'):
  select = "1"
return select
