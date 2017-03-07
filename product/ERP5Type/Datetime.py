##############################################################################
#
# Copyright (c) 2017 Nexedi SA and Contributors. All Rights Reserved.
#                    Klaus Woelfel <klaus@nexedi.com>
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
Restricted datetime module.

From restricted python, use "import datetime" (see patches/Restricted.py).
"""
from AccessControl import allow_class as _allow_class
import datetime as _datetime

MINYEAR = _datetime.MINYEAR
MAXYEAR = _datetime.MAXYEAR

class datetime(_datetime.datetime):
  pass

class date(_datetime.date):
  pass

class time(_datetime.time):
  pass

class timedelta(_datetime.timedelta):
  pass

class tzinfo(_datetime.tzinfo):
  pass

_allow_class(datetime)
_allow_class(date)
_allow_class(time)
_allow_class(timedelta)
_allow_class(tzinfo)