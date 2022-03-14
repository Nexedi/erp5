obj = state_change['object']
from DateTime import DateTime
# we set h/m/s on min date and max date
date = obj.getStopDateRangeMax()
if date is not None:
  date = DateTime("%8s 23:59:59" %(date.Date(),))
  obj.setStopDateRangeMax(date)

date = obj.getStopDateRangeMin()
if date is not None:
  date = DateTime("%8s 23:59:59" %(date.Date(),))
  obj.setStopDateRangeMin(date)
