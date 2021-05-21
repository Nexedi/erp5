software_product = sci['object']
web_site = software_product.getFollowUpValue(portal_type="Web Section")
if web_site:
  software_product.SoftwareProduct_fixRelatedWebSite()
