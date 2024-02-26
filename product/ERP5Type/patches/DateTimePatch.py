from __future__ import print_function
##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#                    Vincent Pelletier <vincent@nexedi.com>
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

from DateTime import DateTime as DateTimeKlass
import math
from DateTime.DateTime import _calcSD, _calcDependentSecond, _calcYMDHMS,\
getDefaultDateFormat, _correctYear, _calcHMS, _calcDependentSecond2, DateTimeError,\
SyntaxError, DateError, TimeError, localtime, time
from Products.ERP5Type import IS_ZOPE2

STATE_KEY = 'str'

# DateTime 3 changed the __eq__ behavior and d1 == d2 only if they have the same same
# timezone. With DateTime 2 two dates from different timezones representing the same
# time were equal. This patch keeps the behavior from DateTime 2.
# See zopefoundation/DateTime commit fff6d04 (Various cleanups, improve unpickling
# speed and distinguish between equal representations and references to equal points
# in time., 2011-05-06)
DateTimeKlass.__eq__ = DateTimeKlass.equalTo


# ERP5 Patch for different pickle implementation, to optimize for disk usage.
# We had different __getstate__ implementations, so we need __setstate__ to support
# loading these formats that might be present in ZODBs.
# This patch does not have support for timezone naive flag, because we don't need it
# so far and also probably because we did not notice that it was added in original
# DateTime.
original_DateTime__setstate__ = DateTimeKlass.__setstate__

def DateTime__setstate__(self, state):
  try: # BBB DateTime 2.12.8
    self.__dict__.clear()
  except AttributeError:
    pass
  self._timezone_naive = False
  if isinstance(state, tuple):
    t, tz = state
    ms = (t - math.floor(t))
    s,d = _calcSD(t)
    x = _calcDependentSecond(tz, t)
    yr, mo, dy, hr, mn, sc = _calcYMDHMS(x, ms)
    self._parse_args(yr, mo, dy, hr, mn, sc, tz, t, d, s)
  elif len(state) != 1 or STATE_KEY not in state:
    # For original pickle representation
    original_DateTime__setstate__(self, state)
  else:
    # For r15569 implementation
    self._parse_args(state[STATE_KEY])

DateTimeKlass.__setstate__ = DateTime__setstate__

def DateTime__getstate__(self):
  return (self._t, self._tz)

DateTimeKlass.__getstate__ = DateTime__getstate__


# ERP5 Patch to have different parsing rules.
# We have a patch since e0eba4791a (Authorised date manipulation before
# year 1000, 2008-01-28), which replaced the method with an implementation
# that did not change since, so we don't have new behaviors of DateTime
# the most visible change might be that we don't have "timezone naive"
# support.
def DateTime_parse(self, st, datefmt=getDefaultDateFormat()):
  # Parse date-time components from a string
  month=year=tz=tm=None
  try: # BBB DateTime 2.12
    spaces        =self.space_chars
    intpat        =self.int_pattern
    fltpat        =self.flt_pattern
    wordpat       =self.name_pattern
    delimiters    =self.delimiters
    MonthNumbers  =self._monthmap
    DayOfWeekNames=self._daymap
    ValidZones    =self._tzinfo._zidx
    _MONTH_LEN = self._month_len
  except AttributeError:
    from DateTime.DateTime import (SPACE_CHARS as spaces,
                                   INT_PATTERN as intpat,
                                   FLT_PATTERN as fltpat,
                                   NAME_PATTERN as wordpat,
                                   DELIMITERS as delimiters,
                                   _MONTHMAP as MonthNumbers,
                                   _DAYMAP as DayOfWeekNames,
                                   _TZINFO,
                                   _MONTH_LEN)
    ValidZones = _TZINFO._zidx
  TimeModifiers =['am','pm']
  # Find timezone first, since it should always be the last
  # element, and may contain a slash, confusing the parser.
  st= st.strip()
  sp=st.split()
  tz=sp[-1]
  if tz and (tz.lower() in ValidZones): st=' '.join(sp[:-1])
  else: tz = None  # Decide later, since the default time zone
  # could depend on the date.

  # XXX we don't support timezone naive in this patch
  self._timezone_naive = False

  ints,dels=[],[]
  i,l=0,len(st)
  while i < l:
    while i < l and st[i] in spaces    : i=i+1
    if i < l and st[i] in delimiters:
      d=st[i]
      i=i+1
    else: d=''
    while i < l and st[i] in spaces    : i=i+1

    # The float pattern needs to look back 1 character, because it
    # actually looks for a preceding colon like ':33.33'. This is
    # needed to avoid accidentally matching the date part of a
    # dot-separated date string such as '1999.12.31'.
    if i > 0: b=i-1
    else: b=i

    ts_results = fltpat.match(st, b)
    if ts_results:
      s=ts_results.group(1)
      i=i+len(s)
      ints.append(float(s))
      continue

    #AJ
    ts_results = intpat.match(st, i)
    if ts_results:
      s=ts_results.group(0)

      ls=len(s)
      i=i+ls
      if (ls==4 and d and d in '+-' and
          (len(ints) + bool(month) >= 3)):
          tz='%s%s' % (d,s)
      else:
          v=int(s)
          ints.append(v)
      continue


    ts_results = wordpat.match(st, i)
    if ts_results:
      o,s=ts_results.group(0),ts_results.group(0).lower()
      i=i+len(s)
      if i < l and st[i]=='.': i=i+1
      # Check for month name:
      if s in MonthNumbers:
        v=MonthNumbers[s]
        if month is None:
          month = v
          continue
      # Check for time modifier:
      elif s in TimeModifiers:
        if tm is None:
          tm = s
          continue
      # Check for and skip day of week:
      elif s in DayOfWeekNames:
        continue

    raise SyntaxError(st)

  day=None
  if ints[-1] > 60 and d not in ['.',':','/'] and len(ints) > 2:
    year=ints[-1]
    del ints[-1]
    if month:
      day=ints[0]
      del ints[:1]
    else:
      month=ints[0]
      day=ints[1]
      del ints[:2]
  elif month:
    if len(ints) > 1:
      if ints[0] > 31:
        year=ints[0]
        day=ints[1]
      else:
        year=ints[1]
        day=ints[0]
      del ints[:2]
  elif len(ints) > 2:
    if ints[0] > 31:
      year=ints[0]
      if ints[1] > 12:
        day=ints[1]
        month=ints[2]
      else:
        day=ints[2]
        month=ints[1]
    if ints[1] > 31:
      year=ints[1]
      if ints[0] > 12 and ints[2] <= 12:
        day=ints[0]
        month=ints[2]
      elif ints[2] > 12 and ints[0] <= 12:
        day=ints[2]
        month=ints[0]
    elif ints[2] > 31:
      year=ints[2]
      if ints[0] > 12:
        day=ints[0]
        month=ints[1]
      else:
        if datefmt=="us":
          day=ints[1]
          month=ints[0]
        else:
          day=ints[0]
          month=ints[1]

    elif ints[0] <= 12:
      month=ints[0]
      day=ints[1]
      year=ints[2]
    del ints[:3]

  if day is None:
    # Use today's date.
    year,month,day = localtime(time())[:3]

  year = _correctYear(year)
  #handle dates before year 1000
  #if year < 1000: raise SyntaxError, st
  leap = year%4==0 and (year%100!=0 or year%400==0)
  try:
    if not day or day > _MONTH_LEN[leap][month]:
      raise DateError(st)
  except IndexError:
    raise DateError(st)
  tod=0
  if ints:
    i=ints[0]
    # Modify hour to reflect am/pm
    if tm and (tm=='pm') and i<12:  i=i+12
    if tm and (tm=='am') and i==12: i=0
    if i > 24: raise TimeError(st)
    tod = tod + int(i) * 3600
    del ints[0]
    if ints:
      i=ints[0]
      if i > 60: raise TimeError(st)
      tod = tod + int(i) * 60
      del ints[0]
      if ints:
        i=ints[0]
        if i > 60: raise TimeError(st)
        tod = tod + i
        del ints[0]
        if ints: raise SyntaxError(st)


  tod_int = int(math.floor(tod))
  ms = tod - tod_int
  hr,mn,sc = _calcHMS(tod_int, ms)
  if not tz:
    # Figure out what time zone it is in the local area
    # on the given date.
    x = _calcDependentSecond2(year,month,day,hr,mn,sc)
    tz = self._calcTimezoneName(x, ms)

  return year,month,day,hr,mn,sc,tz

DateTimeKlass._parse = DateTime_parse

# DateTime 3 removed exceptions as class attributes (since
# zopefoundation/DateTime commit 8114618 ), but we have some code expecting
# these attributes, so undo this patch for convenience.
DateTimeKlass.DateTimeError = DateTimeError
DateTimeKlass.SyntaxError = SyntaxError
DateTimeKlass.DateError = DateError
DateTimeKlass.TimeError = TimeError

if IS_ZOPE2: # BBB Zope2
  # BBB undo patch from DateTime 2.12 , which patches
  # copy_reg._reconstructor with a function that appears as
  # `DateTime.DateTime._dt_reconstructor` in pickles.
  # See https://github.com/zopefoundation/DateTime/blob/2.12.8/src/DateTime/DateTime.py#L1863-L1874
  # This patch is no longer needed once we are using DateTime >= 3 so
  # it is not needed on python3 (copy_reg does not exist on python3)
  import copy_reg
  copy_reg._reconstructor.__module__ = 'copy_reg'
  copy_reg._reconstructor.__name__ = '_reconstructor'
