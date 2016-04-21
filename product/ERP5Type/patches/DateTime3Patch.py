# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2016 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from DateTime import DateTime as DateTimeKlass

STATE_KEY = 'str'

if True:
    original_DateTime__setstate__ = DateTimeKlass.__setstate__

    def DateTime__setstate__(self, state):
        if isinstance(state, tuple):
            if len(state) == 2:
                # [PATCH] We assume _timezone_naive is always False
                # thus we don't store it to minimise pickle size.
                state = (state[0], False, state[1])
            original_DateTime__setstate__(self, state)
        elif len(state) != 1 or STATE_KEY not in state:
            # For original 2.x pickle representation
            original_DateTime__setstate__(self, state)
        else:
            # For r15569 implementation
            self._parse_args(state[STATE_KEY])

    DateTimeKlass.__setstate__ = DateTime__setstate__

    def DateTime__getstate__(self):
        # We store a float of _micros, instead of the _micros long, as we most
        # often don't have any sub-second resolution and can save those bytes
        #
        # [PATCH] We assume _timezone_naive is always False thus we don't store
        # it to minimise pickle size.
        return (self._micros / 1000000.0,
            self._tz)

    DateTimeKlass.__getstate__ = DateTime__getstate__

    # Revert: distinguish between equal representations and references to
    # equal points in time, because at least test_DateTimeKey in
    # testSQLCatalog depends on this behaviour.
    DateTimeKlass.__eq__ = DateTimeKlass.equalTo

if __name__ == '__main__':
    for i in ('2007/01/02 12:34:56.789',
              '2007/01/02 12:34:56.789 GMT+0200',
              '2007/01/02 12:34:56.789 JST',
              '2007/01/02 12:34:56.789 +0300',
              '2007/01/02 12:34:56.789 +0430',
              '2007/01/02 12:34:56.789 +1237',
              ):
        print i
        a = DateTimeKlass(i)
        b = DateTimeKlass()
        b.__setstate__(a.__getstate__())
        is_same = True
        for j in a.__slots__:
            if getattr(a, j) != getattr(b, j):
                print j, getattr(a, j), getattr(b, j)
                is_same = False
        print is_same
