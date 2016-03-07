try:
  return date.strftime('%Y-%m-%dT%H:%M:%S')
except ValueError: # *** ValueError: year=XXX is before 1900; the datetime strftime() methods require year >= 1900
  return "%04d-%02d-%02dT%02d:%02d:%02d" % (date.year(), date.month(), date.day(), date.hour(), date.minute(), date.second())
