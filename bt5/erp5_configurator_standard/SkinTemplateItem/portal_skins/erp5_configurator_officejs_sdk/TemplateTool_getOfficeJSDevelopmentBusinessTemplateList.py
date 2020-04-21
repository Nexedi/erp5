""" Simple place for keep the list of business template to install on this project
"""

keep_bt5_id_list = []

bt5_update_catalog_list = ('erp5_ingestion_mysql_innodb_catalog', 'erp5_full_text_mroonga_catalog')

bt5_installation_list = bt5_update_catalog_list + (
  'erp5_configurator_standard',
  'erp5_upgrader_officejs_sdk',
  'erp5_administration',
  'erp5_forge',
  'erp5_monaco_editor',
  'erp5_code_mirror',
  'erp5_officejs_ui_test',
  'officejs_todomvc'
)

return bt5_installation_list, bt5_update_catalog_list, keep_bt5_id_list
