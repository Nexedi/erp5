from datetime import timedelta

duration = context.getProperty('duration')
if duration is None:
  return ''

return str(timedelta(seconds=int(duration)))
