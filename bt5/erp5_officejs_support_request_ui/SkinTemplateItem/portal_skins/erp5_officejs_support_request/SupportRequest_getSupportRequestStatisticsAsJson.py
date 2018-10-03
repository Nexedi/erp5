from datetime import timedelta
from json import dumps

portal = context.getPortalObject()

# Get the split date
now_date = DateTime().asdatetime()
date_2_midnight = DateTime(now_date - timedelta(days=2)).earliestTime()
date_7_midnight = DateTime(now_date - timedelta(days=7)).earliestTime()
date_30_midnight = DateTime(now_date - timedelta(days=30)).earliestTime()

support_request_list = portal.portal_catalog(
  portal_type="Support Request",
  select_list=['simulation_state', 'start_date'],
  **{"delivery.start_date": {"query": DateTime(now_date), "range": "ngt"}}
)

count_by_state = {}
count_by_date = {"le2": {}, "2to7": {}, "7to30": {}, "gt30": {}}

for sr in support_request_list:
  sr = sr.getObject()
  sr_date = sr.getStartDate()
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
  elif sr_date >= date_30_midnight:
    count_by_date["7to30"][sr_state] = count_by_date["7to30"][sr_state] + 1
  else:
    count_by_date["gt30"][sr_state] = count_by_date["gt30"][sr_state] + 1
   
  if sr_date < date_30_midnight:
    continue

  count_by_state[sr_state] = count_by_state[sr_state] + 1

result = {}
result.update(count_by_state)
result.update(count_by_date)
return dumps(result)
