# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 Nexedi SA and Contributors. All Rights Reserved.
#                    Jerome Perrin <jerome@nexedi.com>
#                    Łukasz Nowak <luke@nexedi.com>
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
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces

from Products.ERP5.Document.Movement import Movement

class DummyMovement(Movement):
  """Dummy Movement for testing purposes."""
  meta_type = 'ERP5 Dummy Movement'
  portal_type = 'Dummy Movement'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  isMovement = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  __implements__ = ( interfaces.IVariated, )

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.Amount
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Movement
                    , PropertySheet.Price
                    , PropertySheet.ItemAggregation
                    )

  def isAccountable(self):
    """Our dummy movement are always accountable."""
    return getattr(self, 'is_accountable', 1)

  def _getPropertyDirectlyOrFromDummyDelivery(self, property, default=None):
    """Returns property from delivery, in case if in Dummy Delivery, or movement"""
    if self.getParentValue().getPortalType() == 'Dummy Delivery':
      return self.getParentValue().getSimulationState()
    return getattr(self, property, default)

  def getSimulationState(self):
    return self._getPropertyDirectlyOrFromDummyDelivery(
        'simulation_state', 'draft')

  def setSimulationState(self, state):
    """Directly sets a simulation state if not in Dummy Delivery."""
    if self.getParentValue().getPortalType() != 'Dummy Delivery':
      self.simulation_state = state
    else:
      raise ValueError

  def getCausalityState(self):
    return self._getPropertyDirectlyOrFromDummyDelivery(
        'causality_state', 'draft')

  def setCausalityState(self, state):
    """Directly sets a causality state."""
    if self.getParentValue().getPortalType() != 'Dummy Delivery':
      self.simulation_state = state
    else:
      raise ValueError

  def getDeliveryValue(self):
    """A dummy movement doesn't have a delivery relation, so return self as delivery.
    """
    return self

  def hasCellContent(self):
    return False
