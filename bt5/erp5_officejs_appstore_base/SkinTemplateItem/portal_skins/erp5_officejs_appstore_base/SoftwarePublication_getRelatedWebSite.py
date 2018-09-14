software_release = context.SoftwarePublication_getRelatedSoftwareRelease()
software_product = software_release.getFollowUpValue(portal_type="Software Product")
return software_product.SoftwareProduct_getRelatedWebSite()
