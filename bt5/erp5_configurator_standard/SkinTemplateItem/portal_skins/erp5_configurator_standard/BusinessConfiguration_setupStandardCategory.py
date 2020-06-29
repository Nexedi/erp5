configuration_save = context.restrictedTraverse(configuration_save_url)

context.setGlobalConfigurationAttr(
   categories_spreadsheet_configuration_save_relative_url=configuration_save.getRelativeUrl())

configuration_save.addConfigurationItem("Categories Spreadsheet Configurator Item",
                                 configuration_spreadsheet_data = getattr(context, "standard_category.ods").data)

configuration_save.addConfigurationItem(
    "Standard BT5 Configurator Item",
    title='erp5_configurator_standard_categories',
    bt5_id='erp5_configurator_standard_categories',
    update_catalog=False,
    install_dependency=True,
)
