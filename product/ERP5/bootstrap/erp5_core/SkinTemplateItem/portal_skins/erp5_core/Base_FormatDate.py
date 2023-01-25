""" Format the date according to current user preferences."""

if not date:
  return ''

try:
  order = context.getPortalObject().portal_preferences.getPreferredDateOrder()
except AttributeError:
  order = 'ymd'

y = date.year()
m = date.month()
d = date.day()

if order == 'dmy':
  result = "%02d/%02d/%04d" % (d, m, y)
elif order == 'mdy':
  result = "%02d/%02d/%04d" % (m, d, y)
else: # ymd is default
  result = "%04d/%02d/%02d" % (y, m, d)

if hour_minute or seconds:
  if seconds:
    hour_minute_text = "%02dh%02dmn%02ds" % (date.hour(), date.minute(), date.second())
  else:
    hour_minute_text = "%02dh%02dmn" % (date.hour(), date.minute())
  result = context.Base_translateString("${date} at ${hour_minute_text}",
              mapping = {'date' : result, 'hour_minute_text' : hour_minute_text  })


return result
