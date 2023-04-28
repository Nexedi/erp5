software_release = context.SoftwarePublication_getRelatedSoftwareRelease()
tag = "publish_" + software_release.getRelativeUrl()
software_release.activate(activity='SQLDict', tag=tag).SoftwareRelease_publishRelatedWebDocument()
software_release.activate(activity='SQLDict', after_tag=tag).publish()
software_product = software_release.getFollowUpValue(portal_type="Software Product")
if software_product.getValidationStateTitle() == 'Draft':
  software_product.validate()
