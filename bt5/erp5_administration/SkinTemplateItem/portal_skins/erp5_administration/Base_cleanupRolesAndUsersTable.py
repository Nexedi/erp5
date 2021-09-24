portal = context.getPortalObject()
req = portal.cmf_activity_sql_connection().query

security_uid_field_list = [x + ("_" if x != "" else "") + "security_uid" for x in portal.portal_catalog.getSQLCatalog().getSQLCatalogSecurityUidGroupsColumnsDict().keys()]
security_uid_set = set()
for security_uid_field in security_uid_field_list:
  security_uid_set.update([row[0] for row in req("select distinct %s from catalog" % (security_uid_field), max_rows=0)[1]])

filtered_set = context.Base_filterSecurityUidDict(
  portal.portal_catalog.getSQLCatalog(catalog_id).security_uid_dict,
  security_uid_set
)
if len(filtered_set) > 0:
  context.z_delete_from_roles_and_users(uid=filtered_set)
