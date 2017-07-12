portal = context.getPortalObject()

sale_supply_list = portal.portal_catalog(portal_type="Sale Supply")

if project_id:
  project_list = context.getPortalObject().portal_catalog(portal_type="Project", id=project_id)
else:
  project_list = context.getPortalObject().portal_catalog(portal_type="Project", validation_state="validated")

project = project_list[0]
service_pairs = []

for sale_supply_obj in sale_supply_list:
  sale_supply_lines = sale_supply_obj.contentValues(portal_type='Sale Supply Line')
  if sale_supply_obj.getDestinationProjectValue().getTitle() == project.getTitle():
    for supply_line in sale_supply_lines:
      service_obj = supply_line.getResourceValue()
      service_pairs.append((service_obj.getTitle(), service_obj.getId()))

result = [list(item) for item in set(service_pairs)]

if json_flag:
  from json import dumps
  return dumps(result)
  
return result
