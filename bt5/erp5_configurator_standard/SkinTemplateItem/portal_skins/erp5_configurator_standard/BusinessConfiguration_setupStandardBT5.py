configuration_save = context.restrictedTraverse(configuration_save_url)

bt5_installation_list = ('erp5_dhtml_style',
                         'erp5_jquery_ui',
                         'erp5_ingestion_mysql_innodb_catalog',
                         'erp5_dms',
                         'erp5_accounting',
                         'erp5_crm',
                         'erp5_simplified_invoicing',
                         'erp5_trade_knowledge_pad',
                         'erp5_crm_knowledge_pad',
                         'erp5_configurator_standard_solver',
                         'erp5_configurator_standard_trade_template',
                         'erp5_configurator_standard_accounting_template',
                         'erp5_configurator_standard_invoicing_template',
                         'erp5_ods_style',
                         'erp5_odt_style',
                         'erp5_ooo_import',
                         'erp5_osoe_web_renderjs_ui',
                        )

bt5_update_catalog = ('erp5_ingestion_mysql_innodb_catalog', 'erp5_accounting', )

for name in bt5_installation_list:
  configuration_save.addConfigurationItem("Standard BT5 Configurator Item",
                                          title=name, bt5_id=name,
                                          update_catalog=(name in bt5_update_catalog),
                                          install_dependency=True,
                                          )
