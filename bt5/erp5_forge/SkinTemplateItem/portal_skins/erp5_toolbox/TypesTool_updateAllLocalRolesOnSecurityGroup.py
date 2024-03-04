portal = context.getPortalObject()
type_list = []
for erp5_type in portal.portal_catalog(
  children_portal_type="Role Information",
  portal_type=portal.portal_types["Types Tool"].getTypeAllowedContentTypeList()):
  type_list.append(erp5_type.getId())
  erp5_type.getObject().updateRoleMapping(priority=4)

return context.Base_redirect('view', keep_items={
  "portal_status_message": "Updated Role Mapping on for all portal types with Roles"})
