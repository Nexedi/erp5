configuration_save = context.restrictedTraverse(configuration_save_url)

context.setGlobalConfigurationAttr(
   portal_type_roles_spreadsheet_configuration_save_relative_url=configuration_save.getRelativeUrl())

configuration_save.setIntIndex(1000)
configuration_save.addConfigurationItem("Portal Type Roles Spreadsheet Configurator Item",
                                        configuration_spreadsheet_file=portal_type_roles_spreadsheet)

# Define standard module security. also.
configuration_save.addConfigurationItem("Permission Configurator Item",
                                        filename="standard_module_permission_access.ods")

# Create ERP5Site_getSecurityCategoryMapping
configuration_save.addConfigurationItem("Security Category Mapping Configurator Item")
