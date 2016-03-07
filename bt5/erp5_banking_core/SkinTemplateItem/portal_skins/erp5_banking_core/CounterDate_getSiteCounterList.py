site = context.Baobab_getVaultSite(vault=context.getSiteValue())
counter_list = [x.getObject() for x in context.portal_catalog(portal_type="Counter", site_uid = site.getUid())]

def sort_counter(a,b):
  return cmp(a.getTitle(),b.getTitle())

counter_list.sort(sort_counter)

return counter_list
