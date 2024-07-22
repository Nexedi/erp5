request = container.REQUEST
portal = context.getPortalObject()
stool = portal.portal_simulation

from_date = request['from_date']
to_date = request['to_date']

# get all resources used for leave requests
resource_list = []
for inventory in stool.getInventoryList(
                          from_date=from_date,
                          to_date=to_date,
                          portal_type='Leave Request Period',
                          group_by_resource=1):
  resource_list.append(
          (inventory.resource_relative_url,
           portal.portal_categories.restrictedTraverse(
                inventory.resource_relative_url).getTranslatedTitle()))

return resource_list
