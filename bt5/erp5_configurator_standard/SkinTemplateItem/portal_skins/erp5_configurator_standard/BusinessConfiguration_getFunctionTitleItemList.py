# coding: utf-8
import six
from Products.ERP5Type.Message import translateString

if context.getGlobalConfigurationAttr('categories_spreadsheet_configuration_save_relative_url'):
  item_list_from_spreadsheet = context.BusinessConfiguration_getCategoriesSpreadsheetConfiguratorItem().getCategoryTitleItemList('function')
  if item_list_from_spreadsheet != [('', '')]:
    return item_list_from_spreadsheet

function_item_list = [
  (u'Accounting & Finance', None, 0),
  (u'Accounting', None, 1),
  (u'Accounting Agent', 'af/accounting/agent', 2),
  (u'Accounting Manager', 'af/accounting/manager', 2),
  (u'Accounting & Finance Manager', 'af/manager', 1),
  (u'Company', None, 0),
  (u'Company Agent', 'company/agent', 1),
  (u'Company Executive', 'company/executive', 1),
  (u'Company Manager', 'company/manager', 1),
  (u'Headquarters', None, 0),
  (u'Headquarters Agent', 'hq/agent', 1),
  (u'Headquarters Executive', 'hq/executive', 1),
  (u'Headquarters Manager', 'hq/manager', 1),
  (u'Human Resources', None, 0),
  (u'Human Resources Agent', 'hr/agent', 1),
  (u'Human Resources Manager', 'hr/manager', 1),
  (u'Information Systems', None, 0),
  (u'Information Systems Manager', 'is/manager', 1),
  (u'Software Developer', 'is/developer', 1),
  (u'System Administrator', 'is/admin', 1),
  (u'Marketing', None, 0),
  (u'Marketing Agent', 'marketing/agent', 1),
  (u'Marketing Manager', 'marketing/manager', 1),
  (u'Production – Manufacturing', None, 0),
  (u'Production Agent', 'production/agent', 1),
  (u'Production Manager', 'production/manager', 1),
  (u'Project Management & Implementation', None, 0),
  (u'Developer for a Project', 'project/developer', 1),
  (u'Project Manager', 'project/manager', 1),
  (u'Purchase', None, 0),
  (u'Purchase Agent', 'purchase/agent', 1),
  (u'Purchase Manager', 'purchase/manager', 1),
  (u'Research and Development', None, 0),
  (u'Research and Development Agent', 'rd/agent', 1),
  (u'Research and Development Manager', 'rd/manager', 1),
  (u'Sales', None, 0),
  (u'Sales Agent', 'sales/agent', 1),
  (u'Sales Manager', 'sales/manager', 1),
  (u'Subsidiary', None, 0),
  (u'Subsidiary Agent', 'subsidiary/agent', 1),
  (u'Subsidiary Manager', 'subsidiary/manager', 1),
  (u'Warehouse', None, 0),
  (u'Warehouse Agent', 'warehouse/agent', 1),
  (u'Warehouse Manager', 'warehouse/manager', 1),
]


prefix = u"\N{NO-BREAK SPACE}" * 4
if six.PY2:
  prefix = prefix.encode('utf-8')
return [['', '']] + [[
    ( prefix * depth ) + str(translateString(title)),
    relative_url,
  ] for (title, relative_url, depth) in function_item_list]
