configuration_save = context.restrictedTraverse(configuration_save_url)

if kw.get('setup_data_notebook'):
  configuration_save.addConfigurationItem(
    "Standard BT5 Configurator Item",
    title='erp5_data_notebook', 
    bt5_id='erp5_data_notebook',
    update_catalog=False,
    install_dependency=True,
  )
  
# setup "data-lake"
if kw.get('setup_data_lake'):
  configuration_save.addConfigurationItem(
    "Standard BT5 Configurator Item",
    title='erp5_wendelin_data_lake_ingestion', 
    bt5_id='erp5_wendelin_data_lake_ingestion',
    update_catalog=False,
    install_dependency=True,
  )
  configuration_save.addConfigurationItem(
    "Standard BT5 Configurator Item",
    title='erp5_wendelin_data_lake_ui', 
    bt5_id='erp5_wendelin_data_lake_ui',
    update_catalog=False,
    install_dependency=True,
  )
  # add default security model - "open" one
  if kw.get('setup_data_lake_default_security_model'):
    configuration_save.addConfigurationItem(
      "Standard BT5 Configurator Item",
      title='erp5_wendelin_data_lake_ingestion_default_security_model',
      bt5_id='erp5_wendelin_data_lake_ingestion_default_security_model',
      update_catalog=False,
      install_dependency=True,
    )

# setup 'tutorial'
if kw.get('setup_wendelin_tutorial'):
  configuration_save.addConfigurationItem(
    "Standard BT5 Configurator Item",
    title='erp5_wendelin_tutorial', 
    bt5_id='erp5_wendelin_tutorial',
    update_catalog=False,
    install_dependency=True,
  )

if kw.get('setup_data_sample'):
  configuration_save.addConfigurationItem(
    "Standard BT5 Configurator Item",
    title='erp5_wendelin_data_sample', 
    bt5_id='erp5_wendelin_data_sample',
    update_catalog=False,
    install_dependency=True,
  )
