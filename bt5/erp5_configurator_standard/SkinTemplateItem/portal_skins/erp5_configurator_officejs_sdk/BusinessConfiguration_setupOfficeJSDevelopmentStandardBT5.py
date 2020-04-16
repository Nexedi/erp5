configuration_save = context.restrictedTraverse(configuration_save_url)

bt5_installation_list, bt5_update_catalog_list, _ = \
  context.TemplateTool_getOfficeJSDevelopmentBusinessTemplateList()

for name in bt5_installation_list:
  configuration_save.addConfigurationItem("Standard BT5 Configurator Item",
                                          title=name, bt5_id=name,
                                          update_catalog=(name in bt5_update_catalog_list))
