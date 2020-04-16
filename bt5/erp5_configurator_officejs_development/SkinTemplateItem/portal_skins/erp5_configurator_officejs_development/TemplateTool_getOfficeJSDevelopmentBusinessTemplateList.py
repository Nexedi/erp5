""" Simple place for keep the list of business template to install on this project
"""

keep_bt5_id_list = ['erp5_ui_test',
                    'erp5_ui_test_core',
                    'erp5_forge',
                    'erp5_l10n_fa',
                    'officejs_test']

bt5_update_catalog_list = ('erp5_ingestion_mysql_innodb_catalog', 'erp5_full_text_mroonga_catalog')

bt5_installation_list = bt5_update_catalog_list + ('officejs_appstore_configurator', 'officejs_meta')

return bt5_installation_list, bt5_update_catalog_list, keep_bt5_id_list
