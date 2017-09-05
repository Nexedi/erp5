# Context *must* be portal_templates
portal_templates = context
p = context.getPortalObject()

# Get the selected Business Managers for installation
selection_name = 'business_manager_selection'
selected_uid_list = p.portal_selections.getSelectionCheckedUidsFor(selection_name)

# Business Managers to be installed
manager_list = []
for uid in selected_uid_list:
   manager_list.append(p.portal_catalog.getObject(uid))

# Install Multiple Business Managers all together
portal_templates.updateInstallationState(manager_list)

return p.REQUEST.RESPONSE.redirect(
  portal_templates.absolute_url_path() +
  '?portal_status_message=Successfull Installation of Business Managers')
