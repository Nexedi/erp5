# Fail if domain does not exists
domain = context.getPortalObject().portal_domains[domain_id]
id_list, title_list = [], []

for subdomain in domain.getDomainGeneratorList():
  id_list.append(subdomain.id)
  title_list.append(subdomain.title)
return title_list, id_list
