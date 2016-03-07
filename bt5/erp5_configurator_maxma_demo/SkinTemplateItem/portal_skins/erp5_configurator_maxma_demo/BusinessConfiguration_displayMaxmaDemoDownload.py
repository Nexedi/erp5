configuration_save = context.restrictedTraverse(configuration_save_url)

bt5_installation_list = ('erp5_demo_maxma_sample',)

for name in bt5_installation_list:
  configuration_save.addConfigurationItem("Standard BT5 Configurator Item",
                                          title=name, bt5_id=name,
                                          update_catalog=0)
