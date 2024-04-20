software_product = sci['object']
web_site = software_product.getFollowUpValue(portal_type="Web Section")
if web_site:
  tag = "SoftwareProduct_setReference_%s" % software_product.getUid()
  software_product.reindexObject(activate_kw={"tag": tag})
  software_product.activate(after_tag=tag).SoftwareProduct_fixRelatedWebSite()
