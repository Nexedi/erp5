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
from DateTime.DateTime import _calcSD, _calcDependentSecond, _calcYMDHMS

STATE_KEY = 'str'

def DateTime__setstate__(self, state):
  if isinstance(state, tuple):
    t, tz = state
    ms = (t - math.floor(t))
    s,d = _calcSD(t)
    x = _calcDependentSecond(tz, t)
    yr, mo, dy, hr, mn, sc = _calcYMDHMS(x, ms)
    self._parse_args(yr, mo, dy, hr, mn, sc, tz, t, d, s)
  elif len(state) != 1 or STATE_KEY not in state:
    # For original pickle representation
    self.__dict__.update(state)
  else:
    # For r15569 implementation
    self._parse_args(state[STATE_KEY])

DateTimeKlass.__setstate__ = DateTime__setstate__

def DateTime__getstate__(self):
  return (self._t, self._tz)

DateTimeKlass.__getstate__ = DateTime__getstate__

if __name__ == '__main__':
  for i in ('2007/01/02 12:34:56.789',
            '2007/01/02 12:34:56.789 GMT+0200',
            '2007/01/02 12:34:56.789 JST',
            '2007/01/02 12:34:56.789 +0300',
            '2007/01/02 12:34:56.789 +0430',
            '2007/01/02 12:34:56.789 +1237',
            ):
    a = DateTimeKlass(i)
    b = DateTimeKlass()
    b.__setstate__(a.__getstate__())
    print a, a.__dict__ == b.__dict__
    for i in a.__dict__.keys():
      if a.__dict__[i] != b.__dict__[i]:
        print i, a.__dict__[i], b.__dict__[i]
