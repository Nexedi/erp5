#############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import warnings

from AccessControl import ModuleSecurityInfo
from DateTime import DateTime
from datetime import datetime
from zLOG import LOG

security = ModuleSecurityInfo('Products.ERP5Type.DateUtils')
security.declarePublic('addToDate', 'getClosestDate',
    'getIntervalBetweenDates', 'getMonthAndDaysBetween',
    'getCompletedMonthBetween', 'getRoundedMonthBetween',
    'getMonthFraction', 'getYearFraction', 'getAccountableYearFraction',
    'getBissextilCompliantYearFraction',
    'getDecimalNumberOfYearsBetween','roundMonthToGreaterEntireYear',
    'roundDate', 'convertDateToHour')

millis = DateTime('2000/01/01 12:00:00.001') - DateTime('2000/01/01 12:00:00')
centis = millis * 10
number_of_months_in_year   = 12.
number_of_hours_in_day     = 24.
number_of_minutes_in_hour  = 60.
number_of_seconds_in_minute = 60.
number_of_days_in_year = 365.
hour = 1/24.
same_movement_interval = hour
  
accountable_days_in_month = 30.
accountable_months_in_year = 12.
number_of_hours_in_year  = 8760

def addToDate(date, to_add=None, **kw):
  """
  Return a new DateTime object with the corresponding added values.
  Values can be negative.
  """
  return_value = {}
  if to_add is not None:
    kw.update(to_add)
  to_add = kw
  for key in ('year', 'month', 'day', 'hour', 'minute', 'second'):
    method = getattr(date, key)
    return_value[key] = method()
  larger_key_dict = { 'second':'minute', 'minute':'hour', 
                      'hour':'day', 'month':'year' }
  number_of_in_dict = { 'second' : number_of_seconds_in_minute,
                        'minute' : number_of_minutes_in_hour,
                        'hour'   : number_of_hours_in_day,
                        'month'  : number_of_months_in_year }
              
  for key in ('second', 'minute', 'hour', 'month'):
    if to_add.get(key, None) is not None:
      return_value[key] = return_value[key] + to_add[key]
    while (key == 'month' and return_value[key] <= 0) or \
          (key != 'month' and return_value[key] < 0):
      return_value[key] = return_value[key] + number_of_in_dict[key]
      return_value[ larger_key_dict[key] ] = return_value[ larger_key_dict[key] ] - 1
    while (key == 'month' and return_value[key] > number_of_in_dict[key]) or \
          (key != 'month' and return_value[key] >= number_of_in_dict[key]):
      return_value[key] = return_value[key] - number_of_in_dict[key]
      return_value[ larger_key_dict[key] ] = return_value[ larger_key_dict[key] ] + 1
      
  if to_add.get('year', None) is not None:
    return_value['year'] = return_value['year'] + to_add['year']
  day_to_add = return_value['day'] - 1
  if to_add.get('day', None) is not None:
    day_to_add += to_add['day']
  return_value['day'] = 1
  return_date = DateTime('%i/%i/%i %i:%i:%d %s' % (return_value['year'],
                                                return_value['month'],
                                                return_value['day'],
                                                return_value['hour'],
                                                return_value['minute'],
                                                return_value['second'],
                                                date.timezone()))
  return_date += day_to_add
  return return_date
  
def getClosestDate(date=None, target_date=None, 
                   precision='month', before=1, strict=1):
  """
  Return the closest date from target_date, at the given precision.
  If date is set, the search is made by making steps of 'precision' duration.
  If target_date is None, it is replaced by current time.
  Precision can be year, month or day
  If before is set to 1, return the closest date before target_date,
  unless the closest date after target_date
  
  
  Example :
  
  date=None, target_date=DateTime('2004/03/12'), precision='month', before=1
    -> return DateTime('2004/03/01')
    
  date=DateTime('2002/12/14'), target_date=DateTime('2004/03/12'), precision='month', before=1
    -> return DateTime('2004/02/14')
  
  """
  if date is None:
    date = DateTime('2000/01/01')
  if target_date is None:
    target_date = DateTime()
    
  earlier_target_date = target_date - millis
        
  to_check = { 'day':{'year':1, 'month':1, 'day':1}, 'month':{'year':1, 'month':1}, 'year':{'year':1} }
  diff_value = {}
  diff_value = getIntervalBetweenDates(from_date = date, to_date = target_date, keys=to_check[precision])
  return_date = addToDate(date = date, to_add = diff_value)
  
  while (strict and return_date - target_date < 0) or \
                      (not strict and \
                      getIntervalBetweenDates(from_date=return_date, to_date=target_date, keys={'day':1})['day'] > 0):
    return_date = addToDate(date = return_date, to_add = { precision:1 })
  if before and DateTime(return_date.Date()) != DateTime(target_date.Date()) :
    return_date = addToDate(date = return_date, to_add = { precision:-1 })
 
  return return_date

        
def getIntervalBetweenDates(from_date=None, to_date=None, 
                            keys={'year':1, 'month':1, 'day':1}):
  """
  Return the number of entire years, months and days (if each is equal to 1 in keys)
  between the both given dates.
  If one of the given dates is None, the date used is the current time.
  """
  if from_date is None:
    from_date = DateTime()
  if to_date is None:
    to_date = DateTime()
  if from_date - to_date > 0:
    from_date, to_date = to_date, from_date
    to_inverse = 1
  else:
    to_inverse = 0  
    
  diff_value = {}
  for key in keys.keys():
    if key:
      diff_value[key] = 0
  
  for current_key in ('year', 'month'):
    if keys.get(current_key, None):
      new_date = addToDate(from_date, to_add={current_key:1})
      while new_date <= to_date:
        from_date = new_date
        diff_value[current_key] = diff_value[current_key] + 1
        new_date = addToDate(from_date, to_add={current_key:1})
  if keys.get('day', None):
    diff_value['day'] = round(to_date - from_date)
    
  returned_value = {}
  for key, value in diff_value.items():
    if to_inverse:
      returned_value[key] = -value
    else:
      returned_value[key] = value
  return returned_value


def getMonthAndDaysBetween(from_date=None, to_date=None):
  """
  Return the number of entire months and days between the both given dates.
  """
  return getIntervalBetweenDates(from_date=from_date, to_date=to_date, keys={'month':1, 'day':1} )


def getCompletedMonthBetween(from_date=None, to_date=None, 
                             reference_date=DateTime('2000/01/01')):
  """
  Return the number of months between the both given dates.
  An incomplete month (at the beginning or the end of the given period)
  is considered as a complete one.
  reference_date is used to know when a month begins.
  
  
  Example :
  
  from_date = 2003/01/02, to_date = 2003/06/30
  Month are Jan, Feb, Mar, Apr, May and Jun -> return 6
  
  from_date = 2003/01/14, to_date = 2003/06/16, reference_date = 2000/01/15
  Month are Dec (2003/01/14), Jan (from 2003/01/15 to 2003/02/14), Feb, Mar, Apr, May and Jun -> return 7
  """
  from_date = getClosestDate(target_date = from_date, date = reference_date)
  to_date = getClosestDate(target_date = to_date, date = reference_date, before = 0)
  return getIntervalBetweenDates(from_date = from_date, to_date = to_date, keys = {'month':1} )

  
def getRoundedMonthBetween(from_date=None, to_date=None, rounded_day=False):
  """
  Return a rounded number of months between the both given dates.
  rounded_day is usefull for accounting, eg:
    the duration between 2000/01/01 23:30 and 2000/01/02 08:00
    is 1 day, not 0.35 day
  """
  return_value = getIntervalBetweenDates(from_date = from_date, to_date = to_date, keys = {'month':1} )['month']
  from_date = addToDate(from_date, {'month': return_value} )
  end_date = addToDate(from_date, {'month':1} )
  days_in_month = end_date - from_date
  if rounded_day:
    from math import ceil
    interval_day = ceil(to_date - from_date)
  else:
    interval_day = to_date - from_date
  if interval_day >= days_in_month / 2.:
    return_value += 1
  return return_value

  
def getMonthFraction(date, days):
  """
  Return a ratio corresponding to the fraction of the month
  represented by the given number of days.
  """
  if (date - days).month() == date.month():
    reference_month_date = date
  else:
    reference_month_date = addToDate(date, {'month':-1} )
    
  number_of_days_in_month = addToDate(reference_month_date, {'month':1}) - reference_month_date + 0.
  return days / number_of_days_in_month
  

def getYearFraction(days=None, months=None, days_in_year=number_of_days_in_year):
  """
  Return a ratio corresponding to the fraction of the year
  represented by the given number of days OR the number of months.
  """
  if days is None and months is not None:
    return months / number_of_months_in_year
  else:
    return days / days_in_year
  
  
def getAccountableYearFraction(from_date=None, to_date=None):
  """
  Returns a year fraction according to accounting rules,
  i.e. 30 days per month
  """
  from_date = from_date.earliestTime()
  to_date = to_date.earliestTime()
  
  months = getMonthAndDaysBetween(from_date, to_date)['month']
  days = getMonthAndDaysBetween(from_date, to_date)['day']
  new_from_date = addToDate(from_date, month=months)
  if days != 0:
    if new_from_date.month() == to_date.month():
      days_before = new_from_date.day() - 1
    else:
      days_before = days_before = (accountable_days_in_month+1) - new_from_date.day()
    days_after = to_date.day() - 1
    if days_before < 0:
      days_before = 0
    if days_after > accountable_days_in_month:
      days_after = accountable_days_in_month
    days = days_before + days_after
  else:
    days = 0
  year_fraction = months / accountable_months_in_year
  year_fraction += (1 / accountable_months_in_year) * ( days / accountable_days_in_month)
  return year_fraction
  
  
def getBissextilCompliantYearFraction(from_date=None, to_date=None, reference_date=DateTime('2000/01/01')):
  """
  Returns a ratio corresponding to the fraction of the year
  represented by the number of days between both of the given dates.
  This method takes care of bissextil years
  reference_date is used to replace the civil year by the financial year

  This method must not be used with a date difference higher than a year
  """
  interval = getIntervalBetweenDates(from_date, to_date, keys={'year':1, 'day':1})
  reference_date = getClosestDate(date=reference_date, target_date=from_date, precision='year', before=1)
  days_in_year = getIntervalBetweenDates(reference_date,
                                         addToDate(reference_date, year=1),
                                         keys={'day':1})['day']
  return_value = interval['year'] + getYearFraction(days=interval['day'], days_in_year=days_in_year)
  return return_value
 
  
def getDecimalNumberOfYearsBetween(from_date, to_date, reference_date=DateTime('2000/01/01')):
  """
  Return a float representing the number of years between
  the both given dates.
  """
  first_date = getClosestDate(target_date = from_date, date = reference_date, before = 0, precision='year')
  last_date = getClosestDate(target_date = to_date, date = reference_date, before = 1, precision='year')
  
  interval_year = getIntervalBetweenDates(first_date, last_date, {'year':1} )['year']
  while interval_year < 0:
    last_date = addToDate(last_date, {'year':1})
    interval_year = getIntervalBetweenDates(first_date, last_date, {'year':1} )['year']
  
  fraction = getYearFraction(days=getIntervalBetweenDates(from_date, first_date, {'day':1})['day'])
  fraction += getYearFraction(days=getIntervalBetweenDates(last_date, to_date, {'day':1})['day'])
  
  fraction += interval_year
  
  return fraction
    

def roundMonthToGreaterEntireYear(months_number):
  """
  Round the given number of months in order to have an entire
  number of years.
  """
  years_number = months_number / number_of_months_in_year
  if int(years_number) != years_number:
    years_number += 1
  return int(years_number) * 12
  

def roundDate(date):
  """
  Returns a date at 0:00
  """
  warnings.warn('ERP5Type.DateUtils.roundDate is deprecated, use'
                ' DateTime.earliestTime instead', DeprecationWarning)
  return date.earliestTime()

def convertDateToHour(date=None):
  """
  converts the date passed as parameter into hours
  """
  if date is None:
    date = DateTime()
  # The Zope DateTime object passed as parameter must be transformed into 
  # python datetime object, to use toordinal method in conversion to hours
  creation_date_dict = {}
  for key in ('year', 'month', 'day'):
    method = getattr(date, key)
    creation_date_dict[key] = method()
  # formating the date from Zope DateTime format to python datetime format
  # and this provides the use of toordinal method.
  formatted_creation_date = datetime(creation_date_dict['year'],creation_date_dict['month'],creation_date_dict['day'])
  # reference date which is the first day of creation date year
  reference_date = datetime(creation_date_dict['year'], 01, 1)
  # calculate the ordinal date of the creation date and the reference date
  ordinal_date = datetime.toordinal(formatted_creation_date)
  ordinal_reference_date = datetime.toordinal(reference_date)
  hour = (ordinal_date - ordinal_reference_date) * number_of_hours_in_day + number_of_hours_in_day + date.hour()
  return int(hour)

def createDateTimeFromMillis(millis):
  """
  Returns a DateTime object, build from the number of milliseconds since epoch.
  Parameter should be a int or long.

  This one should be used by solvers, as DateTime.__cmp__ actually only
  compares the _millis parameter of the two DateTime objects.

  This is currently not perfect: DateTime only supports creating a new object
  from a floating point number of seconds since epoch, so a rounding issue is
  still possible, that's why _millis is explicitely set to the same value
  after the DateTime object has been created from (millis / 1000.)

  A better way would be to compute (yr,mo,dy,hr,mn,sc,tz,t,d,s,millisecs) from
  millis, and then create the DateTime object from it (see "elif ac == 11:" in
  DateTime._parse_args).

  Another solution would be a DateTime implementation that relies exclusively
  on integer values internally.
  """
  millis = long(millis)
  date = DateTime(millis / 1000.)
  date._millis = millis
  return date

