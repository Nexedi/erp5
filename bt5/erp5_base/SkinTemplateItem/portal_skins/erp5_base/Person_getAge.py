"""Returns the age of the person at the current date or at the given `at_date`.
If `year` is true, return the integer value, otherwise returns a translated
string.
"""
from DateTime import DateTime
from erp5.component.module.DateUtils import getIntervalBetweenDates
Base_translateString = context.Base_translateString

birthday = context.getBirthday()
if birthday is None:
  return None

if at_date is None:
  at_date = DateTime()

interval_dict = getIntervalBetweenDates(from_date=birthday,
                                        to_date=at_date)
if year:
  return interval_dict['year']

# mapping contains year, month & day
return Base_translateString("${year} years old", mapping=interval_dict)
