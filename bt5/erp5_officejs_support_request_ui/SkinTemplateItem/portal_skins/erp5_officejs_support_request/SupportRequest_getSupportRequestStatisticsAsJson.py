from json import dumps

portal = context.getPortalObject()

# Get the split date
now_date = DateTime()
date_2 = now_date - 2
date_7 = now_date - 7
date_30 = now_date - 30
# we can not use str.join...
date_2_midnight = DateTime(str(date_2.year()) + "-" + str(date_2.month()) + "-" + str(date_2.day()))
date_7_midnight = DateTime(str(date_7.year()) + "-" + str(date_7.month()) + "-" + str(date_7.day()))
date_30_midnight = DateTime(str(date_30.year()) + "-" + str(date_30.month()) + "-" + str(date_30.day()))

support_request_list = portal.portal_catalog(
  portal_type="Support Request",
  modification_date={'query':date_30_midnight,'range':'nlt'}
)

count_by_state = {}
count_by_date = {"le2": {}, "2to7": {}, "7to30": {}}

for sr in support_request_list:
  sr_date = sr.getModificationDate()
  sr_state = sr.getSimulationState()

  if sr_state not in count_by_state:
    count_by_state[sr_state] = 0

  if sr_state not in count_by_date["le2"]:
    for date_category in count_by_date:
      count_by_date[date_category][sr_state] = 0

  if sr_date >= date_2_midnight:
    count_by_date["le2"][sr_state] = count_by_date["le2"][sr_state] + 1
  elif sr_date >= date_7_midnight:
    count_by_date["2to7"][sr_state] = count_by_date["2to7"][sr_state] + 1
  else:
    count_by_date["7to30"][sr_state] = count_by_date["7to30"][sr_state] + 1

  count_by_state[sr_state] = count_by_state[sr_state] + 1

result = {}
result.update(count_by_state)
result.update(count_by_date)
return dumps(result)
