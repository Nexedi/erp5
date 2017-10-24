portal = context.getPortalObject()
for title_part in ("001", "002"):
  organisation, = portal.portal_catalog(portal_type="Organisation", title="erp5_simulation_test_configured_organisation_%s" % (title_part,))
  organisation = organisation.getObject()
  organisation.newContent(
    portal_type="Bank Account",
    id="bank",
    title="bank_%s" % (organisation.getTitle(),),
  )

product = portal.product_module.newContent(portal_type="Product")
product.setTitle("erp5_simulation_test_product_%s" % (product.getId(),))

return "Prepared successfully"
