software_release = context.SoftwarePublication_getRelatedSoftwareRelease()
tag = "publish_" + software_release.getRelativeUrl()
software_release.activate(tag=tag).SoftwareRelease_publishRelatedWebDocument()
software_release.activate(after_tag=tag).publish()
