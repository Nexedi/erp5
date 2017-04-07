group_calendar = state_change["object"]

while group_calendar.getPortalType() != "Group Calendar":
  group_calendar = group_calendar.getParentValue()

group_calendar.GroupCalendar_updateRelatedAssignment()
