"""
Script used by PlanningBox validator to round the bound dates to the
closest full day.
"""
if full_date.hour() > 12: 
  return DateTime(full_date.Date()) + 1
else:
  return DateTime(full_date.Date())

#if axis == 'end':
#    # round to 23:59:59
#    if full_date.hour() > 12:
#      return DateTime(full_date.Date()) + 1  - (1.0/(24*3600))
#    else:
#      return DateTime(full_date.Date())  - (1.0/(24*3600))
