# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Danièle Vanbaelinghem <daniele@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################
import six

from OFS.Image import Pdata

def getLastPdata(self):
  """Return the last Pdata chunk"""
  if six.PY2:
    next = self.next
  else:
    next = self.__next__

  while next is not None:
    self = next
    if six.PY2:
      next = self.next
    else:
      next = self.__next__
  return self

Pdata.getLastPdata = getLastPdata

def __nonzero__(self):
  while not self.data:
    if six.PY2:
      self = self.next
    else:
      self = self.__next__
    if self is None:
      return False
  return True

Pdata.__nonzero__ = Pdata.__bool__ = __nonzero__
