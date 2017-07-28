portal = context.getPortalObject()

if project_id:
  project_list = portal.portal_catalog(portal_type="Project", id=project_id, limit=1)
else:
  project_list = portal.portal_catalog(portal_type="Project", validation_state="validated", limit=1)

try:
  project = project_list[0]
except IndexError:
  project = None

result = []
if project is not None:
  sale_supply_list = portal.portal_catalog(portal_type="Sale Supply", destination_project_uid=project.getUid())
  for sale_supply in sale_supply_list:
    sale_supply_line_list = sale_supply.contentValues(portal_type='Sale Supply Line')
    for supply_line in sale_supply_line_list:
      service = supply_line.getResourceValue()
      if service is not None:
        result.append((service.getTitle(), service.getId()))

if json_flag:
  from json import dumps
  return dumps(result)

return result
