## Script (Python) "TemplateTool_portalTypesAsCSV"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
portal_type_dict = {}

for bt in context.portal_templates.contentValues(filter={'portal_type':'Business Template'}):
  portal_type_dict[bt.getTitle()] = {}
  for id in bt.getTemplatePortalTypeIdList():
    portal_type_dict[bt.getTitle()][id] = 1

bt_list = portal_type_dict.keys()
bt_list.sort()

portal_type_list = []
for t in context.portal_types.objectValues():
  portal_type_list.append(t.id)
portal_type_list.sort()

msg = ','.join([''] + bt_list) + '\n'
for type in portal_type_list:
  msg += type
  for bt in bt_list:
    msg += type in portal_type_dict[bt] and ',X' or ','
  msg += '\n'

return msg
