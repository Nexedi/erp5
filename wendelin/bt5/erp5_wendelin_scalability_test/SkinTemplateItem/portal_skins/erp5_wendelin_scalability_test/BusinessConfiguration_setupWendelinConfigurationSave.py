"""
  This script creates a Business Configuration as if user selected it during configuration process.
  In case of Wendelin 
  configuration_save_url = business_configuration_module/default_wendelin_configuration/1
"""
configuration_save = context.restrictedTraverse(configuration_save_url)

# bt5 setup
bt5_installation_list = ('erp5_full_text_mroonga_catalog',
                         'erp5_base',
                         'erp5_jquery_ui',
                         'erp5_ingestion_mysql_innodb_catalog',
                         'erp5_ingestion',
                         'erp5_stock_cache',
                         'erp5_web',
                         'erp5_dms',
                         'erp5_pdm',
                         'erp5_knowledge_pad',
                         'erp5_trade',
                         'erp5_project',
                         'erp5_simulation',
                         'erp5_ods_style',
                         'erp5_odt_style',
                         'erp5_rss_style',
                         'erp5_trade',
                         # to develop faster
                         'erp5_code_mirror',
                         'erp5_forge',
                         'erp5_development_wizard',
                         'erp5_dhtml_style',
                         'erp5_hal_json_style',
                         'erp5_web_renderjs_ui',
                         'erp5_wendelin',
                         'erp5_wendelin_examples',
                         'erp5_wendelin_data_sample',
                         'erp5_wendelin_development',
                         'erp5_notebook',
                         'erp5_data_notebook',
                         # data lake
                         'erp5_wendelin_data_lake_ingestion',
                         'erp5_wendelin_data_lake_ingestion_default_security_model',
                         'erp5_wendelin_data_lake_ui'
                        )

bt5_update_catalog = ('erp5_ingestion_mysql_innodb_catalog', 'erp5_wendelin',)

for name in bt5_installation_list:
  configuration_save.addConfigurationItem("Standard BT5 Configurator Item",
                                          title=name, bt5_id=name,
                                          update_catalog=(name in bt5_update_catalog),
                                          install_dependency=True,
                                          )



# categories setup
configuration_save.addConfigurationItem("Categories Spreadsheet Configurator Item",
                                 configuration_spreadsheet_data = getattr(context, "standard_wendelin_category.ods").data)


# security setup
configuration_save.addConfigurationItem("Portal Type Roles Spreadsheet Configurator Item",
                   configuration_spreadsheet_data = getattr(context, "standard_wendelin_portal_types_roles.ods").data)

# Create ERP5Site_getSecurityCategoryMapping
configuration_save.addConfigurationItem("Security Category Mapping Configurator Item")

print "Created."
return printed
