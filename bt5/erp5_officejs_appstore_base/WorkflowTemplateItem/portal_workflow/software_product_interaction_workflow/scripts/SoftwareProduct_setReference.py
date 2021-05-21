software_product = sci['object']
web_site = software_product.getFollowUpValue(portal_type="Web Section")
if web_site:
  software_product.activate(tag="SoftwareProduct_setReference_%s" % software_product.getUid()).reindexObject()
  software_product.activate(priority=2, after_tag="SoftwareProduct_setReference_%s" % software_product.getUid()).SoftwareProduct_fixRelatedWebSite()
