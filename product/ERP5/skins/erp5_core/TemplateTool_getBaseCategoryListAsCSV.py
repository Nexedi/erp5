## Script (Python) "TemplateTool_getBaseCategoryListAsCSV"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
category_dict = {}

for bt in context.portal_templates.contentValues(filter={'portal_type':'Business Template'}):
  category_dict[bt.getTitle()] = {}
  for category in bt.getTemplateBaseCategoryList():
    category_dict[bt.getTitle()][category] = 1

bt_list = category_dict.keys()
bt_list.sort()

category_list = []
for category in context.portal_categories.objectValues():
  category_list.append(category.getId())
category_list.sort()

msg = ','.join([''] + bt_list) + '\n'
for category in category_list:
  msg += category
  for bt in bt_list:
    msg += category in category_dict[bt] and ',X' or ','
  msg += '\n'

return msg
