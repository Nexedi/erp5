portal = context.getPortalObject()
from DateTime import DateTime
request = container.REQUEST

preferences = {}
if not box_relative_url:
  box_relative_url = request.get('box_relative_url', None)
if box_relative_url:
  box = portal.restrictedTraverse(box_relative_url)
  preferences = box.KnowledgeBox_getDefaultPreferencesDict()

mode = preferences.get('mode', 'total_price')
if mode not in ('total_price', 'total_quantity'):
  context.log("Unknown mode %s" % mode)
  return []
from_date = preferences.get('from_date', DateTime(2010, 1, 1))
at_date = preferences.get('from_date', DateTime(2011, 12, 31))
section_category = preferences.get('section_category', 'group/my_group')
if portal.portal_categories.restrictedTraverse(section_category, None) is None:
  return []

limit = preferences.get('limit', 5)
method = preferences.get('method', 'getFutureInventoryList')
if method not in ('getFutureInventoryList', 'getAvailableInventoryList', 'getCurrentInventoryList'):
  context.log("Unknown method %s" % method)
  return []

product_list = []

for brain in getattr(portal.portal_simulation, method)(
                          resource_portal_type="Product",
                          section_category=section_category,
                          from_date=from_date,
                          at_date=at_date,
                          portal_type=portal.getPortalSaleTypeList(), group_by_resource=1
                        # sort_on=((mode, 'ASC'), ), limit=limit, # XXX not working ???
 ):
  resource = portal.portal_catalog.getObject(brain.resource_uid)
  total_price = (brain.total_price or 0) * -1
  total_quantity = (brain.total_quantity or 0) * -1
  product_list.append(resource.asContext(total_price=total_price, total_quantity=total_quantity))

product_list.sort(key=lambda x: -1 * getattr(x, mode))

return product_list[:limit]
