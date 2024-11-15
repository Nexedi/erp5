# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002, 2004 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
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

import zope.interface

from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet

from erp5.component.document.Movement import Movement
from erp5.component.document.MappedValue import MappedValue
from erp5.component.document.ImmobilisationMovement import ImmobilisationMovement
from erp5.component.interface.IDivergenceController import IDivergenceController

@zope.interface.implementer(IDivergenceController,)
class DeliveryCell(MappedValue, Movement, ImmobilisationMovement):
  """
  A DeliveryCell allows to define specific quantities
  for each variation of a resource in a delivery line.
 """
  meta_type = 'ERP5 Delivery Cell'
  portal_type = 'Delivery Cell'
  isCell = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.CategoryCore
                    , PropertySheet.Arrow
                    , PropertySheet.Amount
                    , PropertySheet.Task
                    , PropertySheet.Movement
                    , PropertySheet.Price
                    , PropertySheet.Predicate
                    , PropertySheet.MappedValue
                    , PropertySheet.ItemAggregation
                    )

  @security.protected(Permissions.AccessContentsInformation)
  def isPredicate(self):
    """Movements are not predicates.
    """
    return False

  # MatrixBox methods
  @security.protected(Permissions.AccessContentsInformation)
  def hasCellContent(self, base_id='movement'):
    """A cell cannot have cell content itself.
    """
    return 0

  @security.protected(Permissions.AccessContentsInformation)
  def isAccountable(self):
    """
    Returns 1 if this needs to be accounted
    Only account movements which are not associated to a delivery
    Whenever delivery is there, delivery has priority
    """
    return self.getParentValue().getParentValue().isAccountable()

  @security.protected(Permissions.AccessContentsInformation)
  def getPrice(self, *args, **kw):
    """
    call Movement.getPrice
    """
    return Movement.getPrice(self, *args, **kw)

  @security.protected(Permissions.AccessContentsInformation)
  def getTotalPrice(self, default=0.0, *args, **kw):
    """
    call Movement.getTotalPrice
    """
    return Movement.getTotalPrice(self, default=default, *args, **kw)

  @security.protected(Permissions.AccessContentsInformation)
  def getRootDeliveryValue(self):
    """
    Returns the root delivery responsible of this cell
    """
    return self.getParentValue().getRootDeliveryValue()

  @security.protected(Permissions.ModifyPortalContent)
  def notifyAfterUpdateRelatedContent(self, previous_category_url, new_category_url):
    """
    Membership Crirerions and Category List are same in DeliveryCell
    Must update it (or change implementation to remove data duplication)
    """
    update_method = self.portal_categories.updateRelatedCategory
    new_predicate_value = [update_method(c, previous_category_url, new_category_url)
                           for c in self.getPredicateValueList()]
    self._setPredicateValueList(new_predicate_value)
    # No reindex needed since uid stable


  @security.protected(Permissions.ModifyPortalContent)
  def updateSimulationDeliveryProperties(self, movement_list = None):
    """
    Set properties delivery_ratio and delivery_error for each
    simulation movement in movement_list (all movements by default),
    according to this delivery calculated quantity
    """
    parent = self.getParentValue()
    if parent is not None:
      parent = parent.getParentValue()
      if parent is not None:
        parent.updateSimulationDeliveryProperties(movement_list, self)

  @security.protected(Permissions.AccessContentsInformation)
  def isMovement(self):
    return 1

  @security.protected(Permissions.AccessContentsInformation)
  def isMovingItem(self, item):
    type_based_script = self._getTypeBasedMethod('isMovingItem')
    if type_based_script is not None:
      return type_based_script(item)
    return self.isAccountable()

  # Override getQuantityUnitXXX to negate same methods defined in
  # Amount class. Because cell must acquire quantity unit from line
  # not from resource.
  @security.protected(Permissions.AccessContentsInformation)
  def getQuantityUnitValue(self):
    return self.getParentValue().getQuantityUnitValue()

  @security.protected(Permissions.AccessContentsInformation)
  def getQuantityUnit(self, checked_permission=None):
    return self.getParentValue().getQuantityUnit(checked_permission=checked_permission)
