configuration_save = context.restrictedTraverse(configuration_save_url)

context.setGlobalConfigurationAttr(
   categories_spreadsheet_configuration_save_relative_url=configuration_save.getRelativeUrl())

configuration_save.addConfigurationItem("Categories Spreadsheet Configurator Item",
                                 configuration_spreadsheet_file=configuration_spreadsheet)

configuration_save.addConfigurationItem(
    "Standard BT5 Configurator Item",
    title='erp5_configurator_standard_categories',
    bt5_id='erp5_configurator_standard_categories',
    update_catalog=False,
    install_dependency=True,
)
