configuration_save = context.restrictedTraverse(configuration_save_url)

context.setGlobalConfigurationAttr(
   categories_spreadsheet_configuration_save_relative_url=configuration_save.getRelativeUrl())

configuration_save.addConfigurationItem("Categories Spreadsheet Configurator Item",
                                 configuration_spreadsheet_file=configuration_spreadsheet)
# l10n
user_preferred_language = kw.get('user_preferred_language')
if user_preferred_language not in ('en', None):
  # english is default lang anyway
  bt5_name = 'erp5_l10n_%s' %user_preferred_language
  configuration_save.addConfigurationItem("Standard BT5 Configurator Item",
                                          title=bt5_name, 
                                          bt5_id=bt5_name,
                                          update_catalog=False,
                                          install_dependency=True)
