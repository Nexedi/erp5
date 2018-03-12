# /!\ proxy role !
portal = context.getPortalObject()
result = []
if project_value is not None:
  sale_supply_list = portal.portal_catalog(portal_type="Sale Supply", destination_project_uid=project_value.getUid())
  for sale_supply in sale_supply_list:
    sale_supply_line_list = sale_supply.contentValues(portal_type='Sale Supply Line')
    for supply_line in sale_supply_line_list:
      service = supply_line.getResourceValue()
      if service is not None:
        result.append((service.getTitle(), service.getId()))

return result
