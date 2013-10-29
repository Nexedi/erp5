##############################################################################
#
# Copyright (c) 2013 Nexedi SARL and Contributors. All Rights Reserved.
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
"""
Restricted calendar module.
Disable functions writing to stdout:
- TextCalendar.prweek
- TextCalendar.prmonth
- TextCalendar.pryear
- prcal
- prmonth
Do not provide access to locale-dependent representations, as it's not the
right way to handle l10n in Zope:
- day_name
- day_abbr
- month_name
- month_abbr
- LocaleTextCalendar
- LocaleHTMLCalendar
Provide access to HTMLCalendar, although it's probably not a good idea to use
it.

From restricted python, use "import calendar" (see patches/Restricted.py).
"""
from AccessControl import allow_class as _allow_class
from zExceptions import Unauthorized
import calendar as _calendar

def _disallowed(*args, **kw):
  raise Unauthorized

prcal = _disallowed
prmonth = _disallowed

IllegalMonthError = _calendar.IllegalMonthError
IllegalWeekdayError = _calendar.IllegalWeekdayError
calendar = _calendar.calendar
firstweekday = _calendar.firstweekday
isleap = _calendar.isleap
leapdays = _calendar.leapdays
month = _calendar.month
monthcalendar = _calendar.monthcalendar
monthrange = _calendar.monthrange
setfirstweekday = _calendar.setfirstweekday
timegm = _calendar.timegm
weekday = _calendar.weekday

Calendar = _calendar.Calendar
_allow_class(Calendar)

HTMLCalendar = _calendar.HTMLCalendar
_allow_class(HTMLCalendar)

class TextCalendar(_calendar.TextCalendar):
  prweek = _disallowed
  prmonth = _disallowed
  pryear = _disallowed
_allow_class(TextCalendar)
