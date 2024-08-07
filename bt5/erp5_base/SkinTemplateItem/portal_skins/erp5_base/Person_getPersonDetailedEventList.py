from erp5.component.module.DateUtils import atTheEndOfPeriod
request = container.REQUEST
portal = context.getPortalObject()
from_date = request.get('from_date', None)
to_date = request.get('at_date', None)
aggregation_level = request.get('aggregation_level', None)
if to_date is not None:
  to_date = atTheEndOfPeriod(to_date, period=aggregation_level)
# build query based on dates
catalog_kw = {}
if from_date is not None and to_date is not None:
  catalog_kw['delivery.start_date'] = {
    'range': 'minmax',
    'query': (from_date, to_date),
  }
elif from_date is not None:
  catalog_kw['delivery.start_date'] = {
    'range': 'min',
    'query': from_date,
  }
elif to_date is not None:
  catalog_kw['delivery.start_date'] = {
    'range': 'max',
    'query': to_date,
  }

event_type_list = portal.getPortalEventTypeList()
# get events where user is either source or destination
source_event_list = portal.portal_catalog(portal_type=event_type_list, default_source_uid=context.getUid(), **catalog_kw)
dest_event_list = portal.portal_catalog(portal_type=event_type_list, default_destination_uid=context.getUid(), **catalog_kw)

event_list = list(source_event_list)+list(dest_event_list)

event_list.sort(key=lambda a: a.getStartDate())

return event_list
