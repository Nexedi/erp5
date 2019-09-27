configuration_save = context.restrictedTraverse(configuration_save_url)

configuration_save.addConfigurationItem("Portal Type Roles Spreadsheet Configurator Item",
                   configuration_spreadsheet_data = getattr(context, "standard_wendelin_portal_types_roles.ods").data)

# Create ERP5Site_getSecurityCategoryMapping
configuration_save.addConfigurationItem("Security Category Mapping Configurator Item")
