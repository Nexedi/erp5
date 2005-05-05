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
    security.declareObjectProtected(Permissions.View)

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

    def updateAppliedRule(self):
      if self.getSimulationState() not in self.getPortalDraftOrderStateList():
        # Nothing to do
        self._createOrderRule()

    security.declareProtected(Permissions.AccessContentsInformation, \
                                                   'isAccountable')
    def isAccountable(self):
      """
        Returns 1 if this needs to be accounted
        Only account movements which are not associated to a delivery
        Whenever delivery is there, delivery has priority
      """
      return 0

    def _createOrderRule(self):
      # Return if draft or cancelled simulation_state
      if self.getSimulationState() in ('cancelled',):
        # The applied rule should be cleaned up ie. empty all movements 
        # which have no confirmed children
        return
      # Otherwise, expand
      # Look up if existing applied rule
      my_applied_rule_list = \
          self.getCausalityRelatedValueList(portal_type='Applied Rule')
      if len(my_applied_rule_list)==0:
        # Create a new applied order rule (portal_rules.order_rule)
        portal_rules = getToolByName(self, 'portal_rules')
        portal_simulation = getToolByName(self, 'portal_simulation')
        my_applied_rule = \
           portal_rules.default_order_rule.constructNewAppliedRule( \
                                                  portal_simulation)
        # Set causality
        my_applied_rule.setCausalityValue(self)
        # We must make sure this rule is indexed
        # now in order not to create another one later
        my_applied_rule.immediateReindexObject()
      elif len(my_applied_rule_list) == 1:
        # Re expand the rule if possible
        my_applied_rule = my_applied_rule_list[0]
      else:
        raise SimulationError, 'Order %s has more than one applied rule.' %\
                                self.getRelativeUrl()

      # We are now certain we have a single applied rule
      # It is time to expand it
#       LOG('Order._createOrderRule,my_applied_rule.getPhysicalPath()',0, \
#                      my_applied_rule.getPhysicalPath())
      self.activate().expand(my_applied_rule.getId())

    def applyToOrderRelatedMovement(self, portal_type='Simulation Movement', \
                                    method_id = 'expand'):
      """
        Warning: does not work if it was not catalogued immediately
      """
      for my_simulation_movement in self.getOrderRelatedValueList(
                                         portal_type='Simulation Movement'):
          # And apply
          getattr(my_simulation_movement, method_id)()
      for m in self.contentValues(filter={'portal_type': \
                                          self.getPortalMovementTypeList()}):
        # Find related in simulation
        for my_simulation_movement in m.getOrderRelatedValueList(
                                            portal_type='Simulation Movement'):
          # And apply
          getattr(my_simulation_movement, method_id)()
        for c in m.contentValues(filter={'portal_type': 'Delivery Cell'}):
          for my_simulation_movement in c.getOrderRelatedValueList(
                                            portal_type='Simulation Movement'):
            # And apply
            getattr(my_simulation_movement, method_id)()

    def applyToOrderRelatedAppliedRule(self, method_id='expand'):
      my_applied_rule = self.getCausalityRelatedValue( \
                                      portal_type='Applied Rule')
      getattr(my_applied_rule.getObject(), method_id)()


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

    def reindexObject(self, *k, **kw):
      """
        Reindex children and simulation
      """
      if self.isIndexable:
        # Reindex children
        self.activate().recursiveImmediateReindexObject()
        # Make sure expanded simulation is still OK (expand and reindex)
        # self.activate().applyToOrderRelatedMovement(method_id = 'expand')
        # Removed because overkill

    def manage_beforeDelete(self, item, container):
      """
          Delete related Applied Rule
      """
      for o in self.getCausalityRelatedValueList(portal_type='Applied Rule'):
        o.aq_parent.activate().deleteContent(o.getId())
      Delivery.manage_beforeDelete(self, item, container)
