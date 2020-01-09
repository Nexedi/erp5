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
from AccessControl.PermissionRole import PermissionRole

from Products.ERP5Type import Permissions, PropertySheet, interfaces

from Products.ERP5.Document.OrderLine import OrderLine
from Products.ERP5.Document.Movement import Movement
from Products.ERP5.Document.MappedValue import MappedValue
from Products.ERP5.Document.ImmobilisationMovement import ImmobilisationMovement

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

    # Declarative interfaces
    zope.interface.implements(interfaces.IDivergenceController,)

    security.declareProtected(Permissions.AccessContentsInformation, 'isPredicate')
    def isPredicate(self):
      """Movements are not predicates.
      """
      return False

    # MatrixBox methods
    security.declareProtected( Permissions.AccessContentsInformation,
                               'hasCellContent' )
    def hasCellContent(self, base_id='movement'):
      """A cell cannot have cell content itself.
      """
      return 0

    security.declareProtected(Permissions.AccessContentsInformation, 'isAccountable')
    def isAccountable(self):
      """
        Returns 1 if this needs to be accounted
        Only account movements which are not associated to a delivery
        Whenever delivery is there, delivery has priority
      """
      return self.getParentValue().getParentValue().isAccountable()

    security.declareProtected(Permissions.AccessContentsInformation, 'getPrice')
    def getPrice(self, *args, **kw):
      """
      call Movement.getPrice
      """
      return Movement.getPrice(self, *args, **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getTotalPrice')
    def getTotalPrice(self, default=0.0, *args, **kw):
      """
      call Movement.getTotalPrice
      """
      return Movement.getTotalPrice(self, default=default, *args, **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getRootDeliveryValue')
    def getRootDeliveryValue(self):
      """
      Returns the root delivery responsible of this cell
      """
      return self.getParentValue().getRootDeliveryValue()

    security.declareProtected( Permissions.ModifyPortalContent,
                               'notifyAfterUpdateRelatedContent' )
    def notifyAfterUpdateRelatedContent(self, previous_category_url,
                                              new_category_url):
      """
        Membership Crirerions and Category List are same in DeliveryCell
        Must update it (or change implementation to remove data duplication)
      """
      update_method = self.portal_categories.updateRelatedCategory
      predicate_value = self.getPredicateValueList()
      new_predicate_value = map(lambda c: update_method(c,
              previous_category_url, new_category_url), predicate_value)
      self._setPredicateValueList(new_predicate_value)
      # No reindex needed since uid stable

    # XXX FIXME: option variation are today not well implemented
    # This little hack is needed to make the matrixbox working
    # in DeliveryLine_viewIndustrialPhase
    # Generic form (DeliveryLine_viewOption) is required
    def _edit(self, **kw):
      """
        Store variation_category_list, in order to store new value of
        industrial_phase after.
      """
      edit_order = ['variation_category_list', # edit this one first
                    'item_id_list']            # this one must be the last
      edit_order[1:1] = [x for x in kw.pop('edit_order', ())
                           if x not in edit_order]
      # Base._edit updates unordered properties first
      edit_order[1:1] = [x for x in kw if x not in edit_order]
      MappedValue._edit(self, edit_order=edit_order, **kw)
#       if self.isSimulated():
#         self.getRootDeliveryValue().activate().propagateResourceToSimulation()

    security.declareProtected(Permissions.ModifyPortalContent,
                              'updateSimulationDeliveryProperties')
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

    security.declareProtected(Permissions.AccessContentsInformation, 'isMovement')
    def isMovement(self):
      return 1

    security.declareProtected(Permissions.AccessContentsInformation,
                             'isMovingItem')
    def isMovingItem(self, item):
      type_based_script = self._getTypeBasedMethod('isMovingItem')
      if type_based_script:
        return type_based_script(item)
      return self.isAccountable()

    # Override getQuantityUnitXXX to negate same methods defined in
    # Amount class. Because cell must acquire quantity unit from line
    # not from resource.
    security.declareProtected( Permissions.AccessContentsInformation,
                               'getQuantityUnitValue')
    def getQuantityUnitValue(self):
      return self.getParentValue().getQuantityUnitValue()

    security.declareProtected( Permissions.AccessContentsInformation,
                               'getQuantityUnit')
    def getQuantityUnit(self, checked_permission=None):
      return self.getParentValue().getQuantityUnit(checked_permission=checked_permission)

    # XXX: Dirty but required for erp5_banking_core
    ### Acquire Baobab source / destination uids from parent line
    getBaobabSourceUid = lambda x: x.getSourceUid()
    getBaobabSourceUid__roles__ = PermissionRole(Permissions.View)

    getBaobabDestinationUid = lambda x: x.getDestinationUid()
    getBaobabDestinationUid__roles__ = PermissionRole(Permissions.View)

    getBaobabSourceSectionUid = lambda x: x.getSourceSectionUid()
    getBaobabSourceSectionUid__roles__ = PermissionRole(Permissions.View)

    getBaobabDestinationSectionUid = lambda x: x.getDestinationSectionUid()
    getBaobabDestinationSectionUid__roles__ = PermissionRole(Permissions.View)

    getBaobabSourcePaymentUid = lambda x: x.getSourcePaymentUid()
    getBaobabSourcePaymentUid__roles__ = PermissionRole(Permissions.View)

    getBaobabDestinationPaymentUid = lambda x: x.getDestinationPaymentUid()
    getBaobabDestinationPaymentUid__roles__ = PermissionRole(Permissions.View)

    getBaobabSourceFunctionUid = lambda x: x.getSourceFunctionUid()
    getBaobabSourceFunctionUid__roles__ = PermissionRole(Permissions.View)

    getBaobabDestinationFunctionUid = lambda x: x.getDestinationFunctionUid()
    getBaobabDestinationFunctionUid__roles__ = PermissionRole(Permissions.View)

    getBaobabSourceProjectUid = lambda x: x.getSourceProjectUid()
    getBaobabSourceProjectUid__roles__ = PermissionRole(Permissions.View)

    getBaobabDestinationProjectUid = lambda x: x.getDestinationProjectUid()
    getBaobabDestinationProjectUid__roles__ = PermissionRole(Permissions.View)
