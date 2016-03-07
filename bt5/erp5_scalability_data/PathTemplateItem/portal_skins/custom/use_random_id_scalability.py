portal = context.getPortalObject()

# Set id generator
portal.portal_simulation.setIdGenerator("_generatePerDayId")
portal.web_page_module.setIdGenerator("_generatePerDayId")
portal.sale_order_module.setIdGenerator("_generatePerDayId")
portal.person_module.setIdGenerator("_generatePerDayId")

return 1
