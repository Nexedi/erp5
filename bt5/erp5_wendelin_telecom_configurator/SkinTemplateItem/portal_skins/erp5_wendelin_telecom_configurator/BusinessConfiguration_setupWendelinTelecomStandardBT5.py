configuration_save = context.restrictedTraverse(configuration_save_url)

bt5_installation_list = (
  'erp5_full_text_mroonga_catalog',
  'erp5_ingestion_mysql_innodb_catalog',
  'erp5_code_mirror',
  'erp5_forge',
  'erp5_wendelin',
  'erp5_wendelin_telecom_base',
  'erp5_wendelin_telecom_web',
  'erp5_wendelin_telecom_security'
)

bt5_update_catalog = ('erp5_ingestion_mysql_innodb_catalog', 'erp5_wendelin',)

for name in bt5_installation_list:
  configuration_save.addConfigurationItem(
    "Standard BT5 Configurator Item",
    title=name, bt5_id=name,
    update_catalog=(name in bt5_update_catalog),
    install_dependency=True,
  )
