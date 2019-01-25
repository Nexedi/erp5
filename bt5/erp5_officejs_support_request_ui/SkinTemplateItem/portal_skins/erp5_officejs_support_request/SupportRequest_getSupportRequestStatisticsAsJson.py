from datetime import timedelta
from collections import defaultdict
from json import dumps

portal = context.getPortalObject()

# Get the split date
now_date = DateTime().asdatetime()
date_2_midnight = DateTime(now_date - timedelta(days=2)).earliestTime()
date_7_midnight = DateTime(now_date - timedelta(days=7)).earliestTime()
date_30_midnight = DateTime(now_date - timedelta(days=30)).earliestTime()


# Count the "pipe" of current support requests by state and date
# this catalog search is not limited in time, but it only selects the
# currently active support requests by state. Unless CRM agents are late
# in the processing of these support requests, they should not be too many.
count_by_state_and_date_range = defaultdict(lambda:defaultdict(int))

for brain in portal.portal_catalog(
    portal_type="Support Request",
    simulation_state=("submitted", "suspended", "validated",),
    select_dict={"simulation_state": None, "start_date": "delivery.start_date"},):
  sr_date = brain.start_date
  sr_state = brain.simulation_state

  if sr_date >= date_2_midnight:
    count_by_state_and_date_range[sr_state]["< 2"] = \
      count_by_state_and_date_range[sr_state]["< 2"] + 1
  elif sr_date >= date_7_midnight:
    count_by_state_and_date_range[sr_state]["2-7"] = \
      count_by_state_and_date_range[sr_state]["2-7"] + 1
  elif sr_date >= date_30_midnight:
    count_by_state_and_date_range[sr_state]["7-30"] = \
      count_by_state_and_date_range[sr_state]["7-30"] + 1
  else:
    count_by_state_and_date_range[sr_state]["> 30"] = \
      count_by_state_and_date_range[sr_state]["> 30"] + 1

# We have
#  { state: { date_range: count } }
# but we need to turn it into:
#  { state : {date_range_list: [date_range], count_list: [count], }
# with the date range sorted as `date_step_list`
date_range_list = ("< 2", "2-7", "7-30", "> 30")
count_by_state_and_date_range = {
  state: {
    "date_range_list": date_range_list,
    "count_list": [count_by_state_and_date_range[state][date_range]
                      for date_range in date_range_list ]
  } for state in count_by_state_and_date_range }

# XXX
state_title_by_state_id = portal.ERP5Site_getTicketWorkflowStateInfoDict()
for c in state_title_by_state_id.keys():
  if c not in count_by_state_and_date_range:
    count_by_state_and_date_range[c] = {
    "date_range_list": date_range_list,
    "count_list": [0, 0, 0, 0],
  }

# Count last month activity by state
# we only select support requests from last 30 days, so there should not be too many.
count_by_state = defaultdict(int)
for brain in portal.portal_catalog(
    portal_type="Support Request",
    select_dict={"simulation_state": None},
    **{"delivery.start_date": {"query": date_30_midnight, "range": ">="}}):
  sr_state = brain.simulation_state
  count_by_state[sr_state] = count_by_state[sr_state] + 1


return dumps({
  "count_by_state": count_by_state,
  "count_by_state_and_date_range": count_by_state_and_date_range,
  "state_title_by_state_id": portal.ERP5Site_getTicketWorkflowStateInfoDict()
})

