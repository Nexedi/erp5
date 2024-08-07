##############################################################################
#
# Copyright (c) 2020 Nexedi SA and Contributors. All Rights Reserved.
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
Restricted collections module.

From restricted python, use "import collections" (see patches/Restricted.py).
"""
import six

from collections import (
    Counter, defaultdict, deque, OrderedDict, namedtuple as _namedtuple)

if six.PY2:
  def namedtuple(typename, field_names, verbose=False, rename=False):
    ret = _namedtuple(typename, field_names, verbose, rename)
    ret.__allow_access_to_unprotected_subobjects__ = 1
    return ret
else:
  def namedtuple(typename, field_names, rename=False, defaults=None, module=None):
    ret = _namedtuple(
      typename,
      field_names,
      rename=rename,
      defaults=defaults,
      module=module
    )
    ret.__allow_access_to_unprotected_subobjects__ = 1
    return ret

