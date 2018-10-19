"""Returns the services that can be used on support request for this project.
"""
# /!\ proxy role !

portal = context.getPortalObject()
item_list = portal.Ticket_getResourceItemList(
    portal_type='Support Request',
    include_context=False,
)

allowed_resource_relative_url_set = set([])
# if this project has supplies, only allow projects from the supplies.
if project_value is not None:
  sale_supply_list = portal.portal_catalog(portal_type="Sale Supply", destination_project_uid=project_value.getUid())
  for sale_supply in sale_supply_list:
    sale_supply_line_list = sale_supply.contentValues(portal_type='Sale Supply Line')
    for supply_line in sale_supply_line_list:
      service = supply_line.getResourceValue()
      if service is not None:
        allowed_resource_relative_url_set.add(service.getRelativeUrl())
if allowed_resource_relative_url_set:
  return [('', '')] + [item for item in item_list if item[1] in allowed_resource_relative_url_set]

# otherwise return all support request services
return item_list
