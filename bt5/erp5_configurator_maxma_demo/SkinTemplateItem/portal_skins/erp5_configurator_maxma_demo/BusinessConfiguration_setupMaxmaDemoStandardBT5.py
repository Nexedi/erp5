configuration_save = context.restrictedTraverse(configuration_save_url)

bt5_installation_list = ('erp5_simulation',
                         'erp5_dhtml_style',
                         'erp5_jquery',
                         'erp5_jquery_ui',
                         'erp5_ingestion_mysql_innodb_catalog',
                         'erp5_ingestion',
                         'erp5_web',
                         'erp5_dms',
                         'erp5_crm',
                         'erp5_pdm',
                         'erp5_trade',
                         'erp5_knowledge_pad',
                         'erp5_accounting',
                         'erp5_tax_resource',
                         'erp5_discount_resource',
                         'erp5_invoicing',
                         'erp5_configurator_standard_categories',
                         'erp5_trade_knowledge_pad',
                         'erp5_simulation_test',
                         'erp5_crm_knowledge_pad',
                         'erp5_simplified_invoicing',
                         'erp5_ods_style',
                         'erp5_odt_style',
                         'erp5_ooo_import',
                         'erp5_demo_maxma_rule',
                         'erp5_accounting_l10n_fr',
                         'erp5_l10n_fr',
                         'erp5_l10n_pt-BR',
                        )

bt5_update_catalog = ('erp5_ingestion_mysql_innodb_catalog', )

for name in bt5_installation_list:
  configuration_save.addConfigurationItem("Standard BT5 Configurator Item",
                                          title=name, bt5_id=name,
                                          update_catalog=(name in bt5_update_catalog)
                                          )
