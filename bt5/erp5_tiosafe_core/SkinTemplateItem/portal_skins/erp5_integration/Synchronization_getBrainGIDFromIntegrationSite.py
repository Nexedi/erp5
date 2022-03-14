configurator = context.getPortalObject().portal_integrations[site_id][module_id]
prefix = configurator.getGidPrefix("")
property_list = configurator.getGidPropertyList([])

if reverse:
  return property_list

gid = prefix
for prop in property_list:
  prop_value = getattr(object, prop)
  if isinstance(prop_value, str):
    prop_value = prop_value.encode('utf-8')
  gid += " %s" %(prop_value,)

return gid
