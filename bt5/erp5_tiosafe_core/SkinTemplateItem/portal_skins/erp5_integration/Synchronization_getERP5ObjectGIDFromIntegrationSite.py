configurator = context.getPortalObject().portal_integrations[site_id][module_id]
prefix = configurator.getGidPrefix("")
property_list = configurator.getGidPropertyList()
mapped_property_list = []

gid = prefix

property_mapping = {"firstname" : "first_name",
                    "lastname" : "last_name",
                    "birthday" :"start_date",
                    "email" : "default_email_text"}

for prop in property_list:
  if prop == "country":
    prop_value = object.contentValues(portal_type="Address")[0].getRegion("")
  else:
    mapped_prop = property_mapping.get(prop, prop)
    if reverse:
      mapped_property_list.append(mapped_prop)
      continue
    prop_value = object.getProperty(mapped_prop)
  if isinstance(prop_value, str):
    prop_value = prop_value.encode('utf-8')
  gid += " %s" %(prop_value,)

if reverse:
  return mapped_property_list

return gid
