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

STATE_KEY = 'str'

def DateTime__setstate__(self, state):
  if len(state) != 1 or STATE_KEY not in state:
    self.__dict__.update(state)
  else:
    # For backward compatibility
    self._parse_args(state[STATE_KEY])

DateTimeKlass.__setstate__ = DateTime__setstate__
  
# This below is disabled, because this loses information at
# millisecond level, and it breaks the simulation due to
# divergency tests. I will not disable the above for backward
# compatibility. -yo
# 
# def DateTime__getstate__(self):
#   return {STATE_KEY: str(self)}
# 
# DateTimeKlass.__getstate__ = DateTime__getstate__
