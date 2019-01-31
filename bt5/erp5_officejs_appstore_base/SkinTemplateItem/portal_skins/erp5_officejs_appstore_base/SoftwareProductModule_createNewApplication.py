portal = context.getPortalObject()

# Create the software product
software_product = portal.software_product_module.newContent(
  portal_type="Software Product",
  product_line="software/application",
  title=title,
  description=description,
  source_value=portal.ERP5Site_getAuthenticatedMemberPersonValue()
)

return software_product.SoftwareProduct_updateApplication(file, changelog=description)
