##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.XMLObject import XMLObject
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet

class MovementGroup(XMLObject):
  """
  The purpose of MovementGroup is to define how movements are grouped,
  and how values are updated from simulation movements.
  """
  meta_type = 'ERP5 Movement Group'
  portal_type = 'Movement Group'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = (
    PropertySheet.Base,
    PropertySheet.SimpleItem,
    PropertySheet.CategoryCore,
    PropertySheet.MovementGroup,
    PropertySheet.SortIndex,
    )

  def _getPropertyDict(self, movement, **kw):
    # This method should be defined in sub classes.
    raise NotImplementedError

  def test(self, document, property_dict, **kw):
    # This method should be defined in sub classes.
    raise NotImplementedError

  def _separate(self, movement_list):
    # By default, we separate movements by _getPropertyDict() values.
    # You can override this method in each MovementGroup class.
    tmp_dict = {}
    for movement in movement_list:
      property_dict = self._getPropertyDict(movement)
      # XXX it can be wrong. we need a good way to get hash value, or
      # we should compare for all pairs.
      key = repr(property_dict)
      if tmp_dict.has_key(key):
        tmp_dict[key][0].append(movement)
      else:
        tmp_dict[key] = [[movement], property_dict]
    return tmp_dict.values()

  def separate(self, movement_list):
    # We sort group of simulation movements by their IDs.
    # DO NOT OVERRIDE THIS METHOD. Override _separate() instead.
    return sorted([[sorted(x[0], key=lambda x: x.getId()), x[1]] \
                   for x in self._separate(movement_list)],
                  key=lambda x: x[0][0].getId())

  def isBranch(self):
    # self is taken as branch point by the builder if returned value is True.
    return False
