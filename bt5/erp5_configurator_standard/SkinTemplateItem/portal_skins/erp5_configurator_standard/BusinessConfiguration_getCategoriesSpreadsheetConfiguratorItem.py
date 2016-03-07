categories_spreadsheet_configuration_save_relative_url = \
      context.getGlobalConfigurationAttr('categories_spreadsheet_configuration_save_relative_url')

assert categories_spreadsheet_configuration_save_relative_url, \
  "Global attr categories_spreadsheet_configuration_save_relative_url is not set"
categories_spreadsheet_configuration_save = context.getPortalObject().restrictedTraverse(
   categories_spreadsheet_configuration_save_relative_url)

categories_spreadsheet_list = categories_spreadsheet_configuration_save.contentValues(
        filter=dict(portal_type="Categories Spreadsheet Configurator Item"))

assert len(categories_spreadsheet_list) == 1, \
        'Unexpected Categories Spreadsheets: %r' % categories_spreadsheet_list

return categories_spreadsheet_list[0]
