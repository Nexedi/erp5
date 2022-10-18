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
from erp5.component.document.Movement import Movement
from six import get_unbound_function

class DummyMovement(Movement):
  """Dummy Movement for testing purposes."""
  meta_type = 'ERP5 Dummy Movement'
  portal_type = 'Dummy Movement'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

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
    """Our dummy movements are always accountable, unless is_accountable
    attribute is set."""
    return getattr(self, 'is_accountable', 1)

  def isMovingItem(self, item):
    """Our dummy movements are always moving items, unless is_moving_item
    attribute is set."""
    return getattr(self, 'is_moving_item', 1)

  # In order to make tests work with dummy movements that are not contained in
  # dummy deliveries, we must borrow a few methods from DummyDelivery.

  def getSimulationState(self):
    from erp5.component.document.DummyDelivery import DummyDelivery
    parent = self.getParentValue()
    if isinstance(parent, DummyDelivery):
      self = parent
    return get_unbound_function(DummyDelivery.getSimulationState)(self)

  def getDeliveryValue(self):
    """
    Deprecated, we should use getRootDeliveryValue instead
    """
    return self.getRootDeliveryValue()

  def getRootDeliveryValue(self):
    """In the tests, dummy movements are not always stored in a delivery, here
    we try to support both cases.
    """
    parent = self.getParentValue()
    if hasattr(parent, 'getDeliveryValue'):
      # we are in a delivery, make getDeliveryValue and therefore
      # getExplanation value work like on real movements.
      return parent.getDeliveryValue()
    # return self, to have minimum support of getDeliveryValue
    return self

  def hasCellContent(self):
    return False
