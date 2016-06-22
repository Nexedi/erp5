configuration_save = context.restrictedTraverse(configuration_save_url)

if kw.get('setup_data_notebook'):
  configuration_save.addConfigurationItem(
    "Standard BT5 Configurator Item",
    title='erp5_data_notebook', 
    bt5_id='erp5_data_notebook',
    update_catalog=False,
    install_dependency=True,
  )
