configuration_save = context.restrictedTraverse(configuration_save_url)

context.setGlobalConfigurationAttr(
   categories_spreadsheet_configuration_save_relative_url=configuration_save.getRelativeUrl())

configuration_save.addConfigurationItem("Categories Spreadsheet Configurator Item",
                                 configuration_spreadsheet_file=configuration_spreadsheet)
