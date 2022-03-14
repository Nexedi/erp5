from builtins import str
number_of_activities = len(context.portal_activities.getMessageList())
if number_of_activities == 1: # ignore alarms activities
  number_of_activities = 0
return str(number_of_activities)
