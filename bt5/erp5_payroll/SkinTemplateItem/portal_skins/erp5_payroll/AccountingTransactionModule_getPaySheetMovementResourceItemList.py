item_list = [('', '')]
portal = context.getPortalObject()
getobject = portal.portal_catalog.getobject

for x in portal.portal_simulation.getInventoryList(
                              portal_type=('Pay Sheet Cell',
                                           'Pay Sheet Line'),
                              group_by_resource=1):
  resource_uid = x.resource_uid
  if resource_uid:
    resource = getobject(resource_uid)
    item_list.append((resource.getTitle(),
                      resource.getRelativeUrl()))

item_list.sort(key=lambda x: x[0])
return item_list
