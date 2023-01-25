configuration_save = context.restrictedTraverse(configuration_save_url)

group_id = 'my_group'
price_currency = 'EUR;0.01;Euro'

# Setup Categories
context.BusinessConfiguration_setupStandardCategory(configuration_save_url)

# Setup Portal Type Role
context.BusinessConfiguration_setupPortalTypeRole(configuration_save_url)

# Setup Organisation
context.BusinessConfiguration_setupOrganisation(
  configuration_save_url = configuration_save_url,
  title = 'ISIH GmbH',
  default_email_text = 'mail@isih-gmbh.de',
  default_telephone_text = '555-5555',
  default_address_street_address = 'Musterstr. 1',
  default_address_zip_code = '00001',
  default_address_city = 'Dresden',
  default_address_region = 'region/europe/western_europe/germany',
  price_currency = price_currency
  )

# Setup Bank Account
configuration_save.addConfigurationItem(
  "Bank Account Configurator Item",
  title = 'ISIH Bank',
  )

# Setup Employee
configuration_save.addConfigurationItem(
  "Person Configurator Item",
  organisation_id = context.getGlobalConfigurationAttr('organisation_id'),
  group_id = group_id,
  first_name = 'Herr',
  last_name = 'Admin',
  reference = 'user',
  password = 'test',
  default_email_text = 'herradmin@isih-gmbh.de',
  default_telephone_text = '',
  function = 'function/company',
  )

# Setup Accounting
context.BusinessConfiguration_setupAccounting(
  configuration_save_url = configuration_save_url,
  accounting_plan = 'de',
  period_start_date = DateTime(DateTime().year(), 1, 1),
  period_stop_date = DateTime(DateTime().year(), 12, 31),
  period_title = DateTime().year()
  )

# Setup Preferences
context.BusinessConfiguration_setupPreferences(
  configuration_save_url = configuration_save_url,
  preferred_event_sender_email = '',
  preferred_date_order = 'dmy',
  lang = ['erp5_l10n_de'],
  price_currency = price_currency,
  )

# Setup Simulation
context.BusinessConfiguration_setupEBusinessLotseSimulation(
                                                  configuration_save_url, **kw)

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
