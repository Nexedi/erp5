## Script (Python) "TemplateTool_getModuleListAsCSV"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
module_dict = {}

for bt in context.portal_templates.contentValues(filter={'portal_type':'Business Template'}):
  module_dict[bt.getTitle()] = {}
  for id in bt.getTemplateModuleIdList():
    module_dict[bt.getTitle()][id] = 1

bt_list = module_dict.keys()
bt_list.sort()

module_list = []
for module in context.getPortalObject().contentValues(filter={'meta_type':'ERP5 Folder'}):
  module_list.append(module.getId())
module_list.sort()

msg = ','.join([''] + bt_list) + '\n'
for module in module_list:
  msg += module
  for bt in bt_list:
    msg += module in module_dict[bt] and ',X' or ','
  msg += '\n'

return msg
