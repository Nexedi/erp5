software_release = context.SoftwarePublication_getRelatedSoftwareRelease()
return software_release.getFollowUpValue(portal_type="Software Product").getRelativeUrl()
