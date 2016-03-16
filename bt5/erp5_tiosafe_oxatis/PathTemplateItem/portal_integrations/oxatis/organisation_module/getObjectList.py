org_list = context.getOrganisationList(*args, **kw)

org_dict = {}

for org in org_list:
  org_gid = "%s %s" %(org.title, org.country)
  if not org_dict.has_key(org_gid):
    org_dict[org_gid] = org

context.log("org_dict", org_dict)

return org_dict.values()
