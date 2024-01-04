portal = context.getPortalObject()
req = portal.erp5_sql_connection.manage_test

security_uid_field_list = [x + ("_" if x != "" else "") + "security_uid" for x in portal.portal_catalog.getSQLCatalog().getSQLCatalogSecurityUidGroupsColumnsDict().keys()]
referenced_uid_set = set()
all_uid_set = set()
for security_uid_field in security_uid_field_list:
  referenced_uid_set.union({getattr(row, security_uid_field) for row in req("select distinct %s from catalog where %s is not NULL" % (security_uid_field, security_uid_field))})

print(">> useless uids in roles_and_users table <<\n")
if len(referenced_uid_set) > 0:
  for row in req("select * from roles_and_users where uid not in %s" + tuple(referenced_uid_set)):
    print(row.uid, row.local_roles_group_id, row.allowedRolesAndUsers)

print("\n>> uids that should be in roles_and_users table <<\n")
all_uid_set = {row.uid for row in req("select uid from roles_and_users")}

for security_uid_field in security_uid_field_list:
  for row in req("select %s, relative_url from catalog where %s not in %s" % (security_uid_field, security_uid_field, tuple(all_uid_set))):
    print(security_uid_field, getattr(row, security_uid_field, None), row.relative_url)

print("\n>> END <<")
return printed
