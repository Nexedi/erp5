configuration_save = context.restrictedTraverse(configuration_save_url)

bt5_installation_list = ('erp5_ingestion_mysql_innodb_catalog',
                         'erp5_simulation',
                         'erp5_dhtml_style',
                         'erp5_jquery',
                         'erp5_jquery_ui',
                         'erp5_web',
                         'erp5_ingestion',
                         'erp5_dms',
                         'erp5_crm',
                         'erp5_knowledge_pad',
                         'erp5_jquery_plugin_spinbtn',
                         'erp5_jquery_plugin_jgraduate',
                         'erp5_jquery_plugin_svgicon',
                         'erp5_jquery_plugin_hotkey',
                         'erp5_jquery_plugin_jquerybbq',
                         'erp5_jquery_plugin_svg_editor',
                         'erp5_jquery_plugin_sheet',
                         'erp5_jquery_plugin_mbmenu',
                         'erp5_jquery_plugin_jqchart',
                         'erp5_jquery_plugin_colorpicker',
                         'erp5_jquery_plugin_elastic',
                         'erp5_jquery_plugin_wdcalendar',
                         'erp5_jquery_sheet_editor',
                         'erp5_xinha_editor',
                         'erp5_svg_editor',
                         'erp5_email_reader',
                         'erp5_web_ung_core',
                         'erp5_web_ung_theme',
                         'erp5_web_ung_role')

bt5_update_catalog = ('erp5_ingestion_mysql_innodb_catalog', 'erp5_email_reader')

for name in bt5_installation_list:
  configuration_save.addConfigurationItem("Standard BT5 Configurator Item",
                                          title=name, bt5_id=name,
                                          update_catalog=(name in bt5_update_catalog)
                                          )
