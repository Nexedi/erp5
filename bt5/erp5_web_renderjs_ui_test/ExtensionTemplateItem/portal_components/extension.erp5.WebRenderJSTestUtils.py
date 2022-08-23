import os, time
from DateTime import DateTime

def setTimezone(timezone):
  # timezone must be for example GMT-7
  os.environ['TZ'] = timezone
  time.tzset()
  DateTime._isDST = False
  DateTime._localzone = DateTime._localzone0 = DateTime._localzone1 = timezone
  return "Timezone Updated"
