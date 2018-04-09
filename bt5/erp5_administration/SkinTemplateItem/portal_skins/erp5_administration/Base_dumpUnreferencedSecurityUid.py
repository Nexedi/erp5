portal = context.getPortalObject()
req = portal.cmf_activity_sql_connection().query

security_uid_field_list = [x + ("_" if x != "" else "") + "security_uid" for x in portal.portal_catalog.getSQLCatalog().getSQLCatalogSecurityUidGroupsColumnsDict().keys()]
referenced_uid_set = set()
all_uid_set = set()
for security_uid_field in security_uid_field_list:
  referenced_uid_set.update([row[0] for row in req("select distinct %s from catalog where %s is not NULL" % (security_uid_field, security_uid_field), max_rows=0)[1]])

print(">> useless uids in roles_and_users table <<\n")
if len(referenced_uid_set) > 0:
  for row in req("select uid, allowedRolesAndUsers from roles_and_users where uid not in %s" % str(tuple(referenced_uid_set)), max_rows=0)[1]:
    print row[0], row[1]

print("\n>> uids that should be in roles_and_users table <<\n")
all_uid_set = set([row[0] for row in req("select * from roles_and_users", max_rows=0)[1]])

for security_uid_field in security_uid_field_list:
  for row in req("select %s, relative_url from catalog where %s not in %s" % (security_uid_field, security_uid_field, str(tuple(all_uid_set))), max_rows=0)[1]:
    print security_uid_field, row

print("\n>> END <<")
return printed
