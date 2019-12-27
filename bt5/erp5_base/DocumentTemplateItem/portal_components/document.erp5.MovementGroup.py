# -*- coding: utf-8 -*-
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
from erp5.component.interface.IMovementGroup import IMovementGroup
import zope.interface

class MovementGroup(XMLObject):
  """
  The purpose of MovementGroup is to define how movements
  are grouped.

  REACTORING NEEDED: XXX-JPS
  - the initial docstring was stating that MovementGroup is
    used to know how values are updated from simulation movements
    (to delivery lines). This was wrong because one delivery line
    can be built out of multiple simulation movements through
    differen builders using different movement groups

  - moreover, we need to have something to represent at which
    level movement properties should be stored (ex. in Task
    Report). PropertyGroup could be the name.

  - it is true that during divergence resolution, it will be useful
    to check on PropertyGroup at which level a property can be
    set (ex. cell, line, group of lines, delivery) in order to
    show the appropriate user interface choice to the users.
    This will be achieved by making a union of all PropertyGroup
    of all business path of all simulation movements involved
    in delivery movements to resolve
  """
  meta_type = 'ERP5 Movement Group'
  portal_type = 'Movement Group'

  zope.interface.implements( IMovementGroup, )

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

  def _separate(self, movement_list, merge_delivery=False, **kw):
    # By default, we separate movements by _getPropertyDict() values.
    # You can override this method in each MovementGroup class.
    tmp_dict = {}
    collect_order_group_id = self.getCollectOrderGroupId()
    for movement in movement_list:
      # We are in the case of merging of deliveries, thus if the movement
      # is configured to not split, just take properties of the first movement
      if merge_delivery and collect_order_group_id == "delivery":
        property_dict = {}
      else:
        property_dict = self._getPropertyDict(movement, **kw)
      # XXX it can be wrong. we need a good way to get hash value, or
      # we should compare for all pairs.
      key = repr(property_dict)
      if tmp_dict.has_key(key):
        tmp_dict[key][0].append(movement)
      else:
        tmp_dict[key] = [[movement], property_dict]
    return tmp_dict.values()

  def separate(self, movement_list, **kw):
    # We sort group of simulation movements by their IDs.
    # DO NOT OVERRIDE THIS METHOD. Override _separate() instead.
    return sorted([[sorted(x[0], key=lambda x: x.getId()), x[1]] \
                   for x in self._separate(movement_list, **kw)],
                  key=lambda x: x[0][0].getId())

  def isBranch(self):
    # self is taken as branch point by the builder if returned value is True.
    return False
