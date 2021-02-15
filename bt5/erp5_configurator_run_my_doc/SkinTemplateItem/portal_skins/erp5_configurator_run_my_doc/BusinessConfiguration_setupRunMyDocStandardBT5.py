configuration_save = context.restrictedTraverse(configuration_save_url)

bt5_installation_list = ('erp5_jquery',
                         'erp5_ingestion_mysql_innodb_catalog',
                         'erp5_ingestion',
                         'erp5_web',
                         'erp5_ui_test_core',
                         'erp5_dms',
                         'erp5_jquery_ui',
                         'erp5_slideshow_style',
                         'erp5_knowledge_pad',
                         'erp5_run_my_doc',
                         'erp5_run_my_doc_role')

bt5_update_catalog = ('erp5_ingestion_mysql_innodb_catalog',)

for name in bt5_installation_list:
  configuration_save.addConfigurationItem("Standard BT5 Configurator Item",
                                          title=name, bt5_id=name,
                                          update_catalog=(name in bt5_update_catalog)
                                          )
