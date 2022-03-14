'''Re-calculate capacity when a calendar or an exception is modified.

Possible structures are:

  Leave Request
    Leave Request Period
      Calendar Exception    *

  Presence Request
    Presence Request Period
      Calendar Exception    *

  Group Calendar            *
    Group Presence Period   *
      Calendar Exception    *

This interaction can be triggered at all levels marked with *

For Leave and Presence Request Period, the action is simple, just reindex the period.

For Group Calendar, we reindex all calendar assignments using the group calendar.

'''
calendar = state_change["object"]

def updateLeaveOrPresenceRequestPeriod(calendar):
  calendar.reindexObject()

def updateGroupCalendar(calendar):
  calendar.GroupCalendar_updateRelatedAssignment()

action_mapping = {
  'Leave Request Period': updateLeaveOrPresenceRequestPeriod,
  'Presence Request Period': updateLeaveOrPresenceRequestPeriod,
  'Group Calendar': updateGroupCalendar,
}

while calendar.getPortalType() not in action_mapping:
  calendar = calendar.getParentValue()

action_mapping[calendar.getPortalType()](calendar)
