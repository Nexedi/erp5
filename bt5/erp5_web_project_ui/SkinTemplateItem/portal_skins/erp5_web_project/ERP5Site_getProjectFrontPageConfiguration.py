import json
from DateTime import DateTime

# hardcoded for now, pending a decision on moving these to a System Preference
MILESTONE_OUTDATED_DAY_COUNT = 90
DOCUMENT_OUTDATED_DAY_COUNT = 21
PORTAL_TYPE_LIST = ("Task", "Bug", "Task Report")
SIMULATION_STATE_LIST = ("planned", "auto_planned", "ordered", "confirmed", "ready",
                         "stopped", "started", "submitted", "validated")

now = DateTime()
return json.dumps({
  'milestone_limit_date': (now - MILESTONE_OUTDATED_DAY_COUNT)
                          .toZone("UTC").strftime("%Y-%m-%d %H:%M:%S"),
  'document_limit_date': (now - DOCUMENT_OUTDATED_DAY_COUNT)
                         .toZone("UTC").strftime("%Y-%m-%d %H:%M:%S"),
  'portal_type_list': list(PORTAL_TYPE_LIST),
  'simulation_state_list': list(SIMULATION_STATE_LIST),
})
