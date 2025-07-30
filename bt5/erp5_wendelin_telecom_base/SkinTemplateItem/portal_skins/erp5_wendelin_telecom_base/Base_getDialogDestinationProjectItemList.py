portal = context.getPortalObject()

destination_project_list = portal.project_module.objectValues(portal_type='Project')

destination_project_title_list = [['', '']]
for project in destination_project_list:
  destination_project_title_list.append([project.getTitle(), project.getRelativeUrl()])

return destination_project_title_list
