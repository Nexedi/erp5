from json import dumps

portal = context.getPortalObject()

support_request_list = portal.portal_catalog(portal_type="Support Request")


count_by_state = {"validated": 0, "submitted": 0, "suspended": 0, "invalidated": 0, "draft": 0, "cancelled": 0}
count_by_date = {"le2": count_by_state.copy(), "2to7": count_by_state.copy(), "7to30": count_by_state.copy(), "gt30": count_by_state.copy()}

# Get the split date
now_date = DateTime()
date_2 = now_date - 2
date_7 = now_date - 7
date_30 = now_date - 30
# we can not use str.join...
date_2_midnight = DateTime(str(date_2.year()) + "-" + str(date_2.month()) + "-" + str(date_2.day()))
date_7_midnight = DateTime(str(date_7.year()) + "-" + str(date_7.month()) + "-" + str(date_7.day()))
date_30_midnight = DateTime(str(date_30.year()) + "-" + str(date_30.month()) + "-" + str(date_30.day()))


for sr in support_request_list:
  sr_date = sr.getModificationDate()
  sr_state = sr.getSimulationState()

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
