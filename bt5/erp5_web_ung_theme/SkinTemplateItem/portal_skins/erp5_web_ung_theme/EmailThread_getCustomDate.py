"""
  Script to custom the date using, for example, abbreviated months
  i.e
    Feb 7
  XXX - check if it is possible with DateField
"""
date = context.getStartDate()
if not date:
  return None
if date.isCurrentDay():
  return date.AMPMMinutes()
else:
  return "%s %s" % (date.aMonth(), date.day())
