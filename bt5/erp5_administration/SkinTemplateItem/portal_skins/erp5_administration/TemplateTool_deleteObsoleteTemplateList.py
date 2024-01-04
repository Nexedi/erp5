portal_templates = context.getPortalObject().portal_templates
delete_list = []
bt_list = portal_templates.objectValues()
for bt in bt_list:
  bt_id = bt.getId()
  installation_state = bt.getInstallationState()
  if installation_state in ('deleted', 'replaced'):
    delete_list.append(bt_id)
  elif installation_state == 'not_installed':
    title = bt.getTitle()
    modification_date = bt.getModificationDate()
    for x in bt_list:
      if (x.getTitle() == title and
          x.getInstallationState() in ('installed', 'not_installed') and
          x.getModificationDate() > modification_date):
        delete_list.append(bt_id)
        break

print('Deleted id list:%r' % delete_list)
portal_templates.manage_delObjects(delete_list)
return printed
