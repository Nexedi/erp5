portal = context.getPortalObject()

# default_field_your_resource,field_your_title, field_your_project, default_field_your_project, form_id, field_your_resource, dialog_id, title, project, resource, dialog_method
# Create a new object
project_list = portal.portal_catalog(portal_type="Project")

# get project name list
project_id_pair = []
for project in project_list:
  project_id_pair.append([project.getTitle(), project.getId()])

return (project_id_pair)
