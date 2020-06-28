from Products.ERP5Type.Message import translateString

if context.getGlobalConfigurationAttr('categories_spreadsheet_configuration_save_relative_url'):
  item_list_from_spreadsheet = context.BusinessConfiguration_getCategoriesSpreadsheetConfiguratorItem().getCategoryTitleItemList('function')
  if item_list_from_spreadsheet != [('', '')]:
    return item_list_from_spreadsheet

function_item_list = [
  ('Accounting & Finance', None),
  ('Accounting', 'af/accounting'),
  ('Accounting Agent', 'af/accounting/agent'),
  ('Accounting Manager', 'af/accounting/manager'),
  ('Accounting & Finance Manager', 'af/manager'),
  ('Company', None),
  ('Company Agent', 'company/agent'),
  ('Company Executive', 'company/executive'),
  ('Company Manager', 'company/manager'),
  ('Headquarters', None),
  ('Headquarters Agent', 'hq/agent'),
  ('Headquarters Executive', 'hq/executive'),
  ('Headquarters Manager', 'hq/manager'),
  ('Human Resources', None),
  ('Human Resources Agent', 'hr/agent'),
  ('Human Resources Manager', 'hr/manager'),
  ('Information Systems', None),
  ('Information Systems Manager', 'is/manager'),
  ('Software Developer', 'is/developer'),
  ('System Administrator', 'is/admin'),
  ('Marketing', None),
  ('Marketing Agent', 'marketing/agent'),
  ('Marketing Manager', 'marketing/manager'),
  ('Production \xe2\x80\x93 Manufacturing', None),
  ('Production Agent', 'production/agent'),
  ('Production Manager', 'production/manager'),
  ('Project Management & Implementation', None),
  ('Developer for a Project', 'project/developer'),
  ('Project Manager', 'project/manager'),
  ('Purchase', None),
  ('Purchase Agent', 'purchase/agent'),
  ('Purchase Manager', 'purchase/manager'),
  ('Research and Development', None),
  ('Research and Development Agent', 'rd/agent'),
  ('Research and Development Manager', 'rd/manager'),
  ('Sales', None),
  ('Sales Agent', 'sales/agent'),
  ('Sales Manager', 'sales/manager'),
  ('Subsidiary', None),
  ('Subsidiary Agent', 'subsidiary/agent'),
  ('Subsidiary Manager', 'subsidiary/manager'),
  ('Warehouse', None),
  ('Warehouse Agent', 'warehouse/agent'),
  ('Warehouse Manager', 'warehouse/manager'),
]

return [('', '')] + [(translateString(title), relative_url) for (title, relative_url) in function_item_list]
