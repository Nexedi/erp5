from erp5.component.module.DateUtils import atTheEndOfPeriod
request = container.REQUEST
from_date = request.get('from_date', None)
to_date = request.get('at_date', None)
aggregation_level = request.get('aggregation_level', None)
if to_date is not None:
  to_date = atTheEndOfPeriod(to_date, period=aggregation_level)
career_list = []
if from_date is None and to_date is None:
  career_list = context.contentValues(filter={'portal_type':'Career'})
else:
  for career in context.contentValues(filter={'portal_type':'Career'}):
    if from_date is not None and to_date is not None:
      if career.getStartDate() >= from_date and career.getStartDate() < to_date \
             or career.getStopDate() < to_date and career.getStopDate() >= from_date \
             or career.getStartDate() < from_date and career.getStopDate() > to_date:
        career_list.append(career)
    elif from_date is not None:
      if career.getStartDate() >= from_date \
             or career.getStopDate() >= from_date:
        career_list.append(career)
    elif to_date is not None:
      if career.getStartDate() < to_date \
             or career.getStopDate() < to_date :
        career_list.append(career)

career_list.sort(key=lambda a: a.getStartDate())
return career_list
