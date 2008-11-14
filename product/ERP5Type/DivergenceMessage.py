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

from Products.PythonScripts.Utility import allow_class
from Products.ERP5Type.ObjectMessage import ObjectMessage
from zLOG import LOG, PROBLEM, INFO

class DivergenceMessage(ObjectMessage):
  """
  Divergence Message is used for notifications to user about divergences.
  """
  def getMovementGroup(self):
    divergence_scope = getattr(self, 'divergence_scope', None)
    if divergence_scope is None:
      return []
    tested_property = getattr(self, 'tested_property', None)
    movement_group_list = []
    delivery = self.simulation_movement.getDeliveryValue().getParentValue()
    for builder in delivery.getBuilderList():
      for movement_group in builder.getMovementGroupList():
        if movement_group.getDivergenceScope() == divergence_scope:
          if tested_property is None or \
             tested_property in movement_group.getTestedPropertyList():
            return movement_group

  def getCollectOrderGroup(self):
    movement_group = self.getMovementGroup()
    if movement_group is not None:
      return movement_group.getCollectOrderGroup()
    elif getattr(self, 'divergence_scope', None) == 'quantity':
      # We have no MovementGroup for quantity, so try to guess from the
      # portal_type.
      portal_type = self.getObject().getPortalType()
      if 'Line' in portal_type:
        return 'line'
      elif 'Cell' in portal_type:
        return 'cell'
    return None

  def __eq__(self, other):
    return self.__dict__ == other.__dict__

  def __ne__(self, other):
    return self.__dict__ != other.__dict__

allow_class(DivergenceMessage)
