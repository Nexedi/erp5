configuration_save = context.restrictedTraverse(configuration_save_url)

context.BusinessConfiguration_setupSimulation(configuration_save_url, **kw)

# Catalog Keyword Search Keys are for now hardcoded.
configuration_save.addConfigurationItem("Catalog Keyword Key Configurator Item",
    key_list=('description', 'title', 'catalog.description', 'catalog.title'))

# This could be a customer decision option
# configuration_save.addConfigurationItem("Site Property Configurator Item",
#     site_property_list=[[['email_from_address', 'email@example.com', 'string'],]])

# Customize portal type information.
# Include Constraints to some Simulation Objects
for portal_type in ['Purchase Order', 'Sale Order']:
  configuration_save.addConfigurationItem("Portal Type Configurator Item",
                                        target_portal_type=portal_type,
                                        add_propertysheet_list=('TradeOrder',))

for portal_type in ['Purchase Order Line', 'Sale Order Line','Sale Packing List Line']:
  configuration_save.addConfigurationItem("Portal Type Configurator Item",
                                        target_portal_type=portal_type,
                                        add_propertysheet_list=('TradeOrderLine',))

configuration_save.addConfigurationItem("Portal Type Configurator Item",
                                        target_portal_type='Inventory',
                                        add_propertysheet_list=('InventoryConstraint',))

configuration_save.addConfigurationItem("Portal Type Configurator Item",
                                        target_portal_type='Currency',
                                        add_propertysheet_list=('CurrencyConstraint',))

configuration_save.addConfigurationItem("Portal Type Configurator Item",
                                        target_portal_type='Career',
                                        add_propertysheet_list=('CareerConstraint',))
