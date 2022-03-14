"""
  This script sets all standard (non-movable) holidays for polish calendar
  on context Group Calendar Period.
  Year defaults to current year.
"""
from builtins import str
if year is None:
  year = DateTime().year()
part_holiday_list = ['01-01','05-01','05-03','08-15','11-01','11-11','12-25','12-26']
holiday_list = ['-'.join((str(year),holiday))  for holiday in part_holiday_list]

for day in holiday_list:
   holiday = DateTime(day)
   context.newContent(portal_type = 'Calendar Exception',
                      exception_date = holiday)
