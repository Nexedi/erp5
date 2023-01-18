from erp5.component.module.DateUtils import timeZoneContext

current_timezone_contexts = []

def setTimezone(timezone):
  """Change the default timezone to `timezone`.
  """
  if current_timezone_contexts:
    resetTimeZone()

  tzc = timeZoneContext(timezone)
  tzc.__enter__()
  current_timezone_contexts.append(tzc)

  return "Timezone Updated"


def resetTimeZone():
  """Reset the timezone that might have been set by `setTimezone`
  """
  current_timezone_contexts.pop().__exit__(None, None, None)
