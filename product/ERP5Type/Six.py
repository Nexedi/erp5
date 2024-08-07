##############################################################################
#
# Copyright (c) 2022 Nexedi SA and Contributors. All Rights Reserved.
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
Restricted six module.

From restricted python, use "import six" (see patches/Restricted.py).
"""
import six as _six

PY2 = _six.PY2
PY3 = _six.PY3
moves = _six.moves
text_type = _six.text_type
binary_type = _six.binary_type
string_types = _six.string_types
integer_types = _six.integer_types

# ContainerAssertions cannot be used here (like for dict) because the following
# functions are defined on `six` module directly and ContainerAssertions has a
# type() as key
from Products.ERP5Type.patches.Restricted import SafeIterItems
iteritems = lambda d: SafeIterItems(_six.iteritems(d), d)
from AccessControl.ZopeGuards import SafeIter
iterkeys = lambda d: SafeIter(_six.iterkeys(d), d)
itervalues = lambda d: SafeIter(_six.itervalues(d), d)

if PY2:
  from AccessControl.ZopeGuards import safe_builtins as _safe_builtins
  _safe_builtins['xrange'] = _six.moves.xrange
