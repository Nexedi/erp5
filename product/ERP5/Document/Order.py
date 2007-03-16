##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Base import Base

from Products.ERP5.Document.Delivery import Delivery

from zLOG import LOG

class Order(Delivery):
    # CMF Type Definition
    meta_type = 'ERP5 Order'
    portal_type = 'Order'
    isDelivery = 1
    isAccountable = 0

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Reference
                      , PropertySheet.TradeCondition
                      , PropertySheet.Comment
                      , PropertySheet.Order
                      )

    security.declareProtected(Permissions.AccessContentsInformation, \
                                                   'isAccountable')
    def isAccountable(self):
      """
        Returns 1 if this needs to be accounted
        Only account movements which are not associated to a delivery
        Whenever delivery is there, delivery has priority
      """
      return 0
    
    def getTotalPrice(self, **kw) :
      """Returns the total price for this Order. """
      kw.setdefault('portal_type', self.getPortalOrderMovementTypeList())
      return Delivery.getTotalPrice(self, **kw)
      
    def getTotalQuantity(self, **kw) :
      """Returns the total quantity for this Order. """
      kw.setdefault('portal_type', self.getPortalOrderMovementTypeList())
      return Delivery.getTotalQuantity(self, **kw)
    
    def applyToOrderRelatedMovement(self, portal_type='Simulation Movement', \
                                    method_id = 'expand',**kw):
      """
        Warning: does not work if it was not catalogued immediately
      """
      for my_simulation_movement in self.getOrderRelatedValueList(
                                         portal_type='Simulation Movement'):
          # And apply
          getattr(my_simulation_movement, method_id)(**kw)
      for m in self.contentValues(filter={'portal_type': \
                                          self.getPortalMovementTypeList()}):
        # Find related in simulation
        for my_simulation_movement in m.getOrderRelatedValueList(
                                            portal_type='Simulation Movement'):
          # And apply
          getattr(my_simulation_movement, method_id)(**kw)
        for c in m.contentValues(filter={'portal_type':
            self.getPortalMovementTypeList()}):
          for my_simulation_movement in c.getOrderRelatedValueList(
                                            portal_type='Simulation Movement'):
            # And apply
            getattr(my_simulation_movement, method_id)(**kw)

    def applyToOrderRelatedAppliedRule(self, method_id='expand',**kw):
      my_applied_rule = self.getCausalityRelatedValue( \
                                      portal_type='Applied Rule')
      getattr(my_applied_rule.getObject(), method_id)(**kw)


    security.declareProtected(Permissions.AccessContentsInformation, \
                              'getOrderRelatedMovementList')
    def getOrderRelatedMovementList(self):
      """
        Returns simulation movements related to a cell or line 
        of this order
      """
      result = self.getOrderRelatedValueList(portal_type='Simulation Movement')
      for m in self.contentValues(filter={'portal_type': \
                                          self.getPortalMovementTypeList()}):
        # Find related in simulation
        result += m.getOrderRelatedValueList(portal_type='Simulation Movement')
        for c in m.contentValues(filter={'portal_type': 'Delivery Cell'}):
          result += c.getOrderRelatedValueList( \
                                             portal_type='Simulation Movement')
      return result

    def manage_beforeDelete(self, item, container):
      """
          Delete related Applied Rule
      """
      for o in self.getCausalityRelatedValueList(portal_type='Applied Rule'):
        o.getParentValue().activate().deleteContent(o.getId())
      Delivery.manage_beforeDelete(self, item, container)

    ##########################################################################
    # Applied Rule stuff
    def updateAppliedRule(self, rule_id="default_order_rule",force=0,**kw):
      """
        XXX FIXME: Kept for compatibility
        updateAppliedRule must be call with the rule_id in workflow script
      """
      LOG('Order.updateAppliedRule ',0,'This method this method should not be used anymore.')
      Delivery.updateAppliedRule(self, rule_id, force=force,**kw)

    def recursiveReindexObject(self, activate_kw=None, *k, **kw):
      """
      Reindex children and simulation
      """
      Delivery.recursiveReindexObject(self, activate_kw=activate_kw, *k, **kw)
      self.activate(activate_kw=activate_kw).\
          expandAppliedRuleRelatedToOrder(activate_kw=activate_kw, **kw)

    def expandAppliedRuleRelatedToOrder(self, activate_kw=None,**kw):
      """
      Expand the applied rule related 
      """
      applied_rule_list = self.getCausalityRelatedValueList(
                                           portal_type='Applied Rule')
      for applied_rule in applied_rule_list:
        # XXX Missing activate keys
        applied_rule.activate(activate_kw=activate_kw).expand(**kw)
