from Products.ZSQLCatalog.SQLCatalog import Query
from Products.ERP5Type.DateUtils import atTheEndOfPeriod
request = container.REQUEST
portal = context.getPortalObject()
from_date = request.get('from_date', None)
to_date = request.get('at_date', None)
aggregation_level = request.get('aggregation_level', None)
if to_date is not None:
  to_date = atTheEndOfPeriod(to_date, period=aggregation_level)
# build query based on dates
query=None
if from_date is not None and to_date is not None:  
  params = {"delivery.start_date":(from_date, to_date)}
  query = Query(range="minmax", **params)
elif from_date is not None:
  params = {"delivery.start_date":from_date}
  query = Query(range="min", **params)
elif to_date is not None:
  params = {"delivery.start_date":to_date}
  query = Query(range="max", **params)

event_type_list = portal.getPortalEventTypeList()
# get events where user is either source or destination
source_event_list = portal.portal_catalog(portal_type=event_type_list, default_source_uid=context.getUid(),query=query)
dest_event_list = portal.portal_catalog(portal_type=event_type_list, default_destination_uid=context.getUid(),query=query)

event_list = list(source_event_list)+list(dest_event_list)

def sortDate(a, b):
  return cmp(a.getStartDate(), b.getStartDate())

event_list.sort(sortDate)

return event_list
