portal = context.getPortalObject()
security_uid_field_list = [x + ("_" if x != "" else "") + "security_uid" for x in portal.portal_catalog.getSQLCatalog().getSQLCatalogSecurityUidGroupsColumnsDict().keys()]
security_uid_set_list = []
for security_uid_field in security_uid_field_list:
  security_uid_set_list.append({getattr(x, security_uid_field) for x in context.z_get_referenced_security_uid_set_for(security_uid_field=security_uid_field)})
security_uid_set = set()
for s in security_uid_set_list:
  security_uid_set = security_uid_set.union(s)
filtered_set = context.Base_filterSecurityUidDict(
  portal.portal_catalog.getSQLCatalog(catalog_id).security_uid_dict,
  security_uid_set
)
if len(filtered_set) > 0:
  context.z_delete_from_roles_and_users(uid=filtered_set)
