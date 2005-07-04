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

from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base

from Products.CMFCore.WorkflowCore import WorkflowAction
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Base import Base

from Products.ERP5.Document.OrderLine import OrderLine
from Products.ERP5.Document.Movement import Movement
from Products.ERP5.Document.MappedValue import MappedValue

from zLOG import LOG

class DeliveryCell(MappedValue, Movement):
    """
      A DeliveryCell allows to define specific quantities
      for each variation of a resource in a delivery line.
    """

    meta_type = 'ERP5 Delivery Cell'
    portal_type = 'Delivery Cell'
    isCell = 1
    isMovement = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )

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

    # Explicit acquisition of aq_dynamic generated method
    security.declareProtected(Permissions.AccessContentsInformation, 'getSimulationState')
    def getSimulationState(self):
      """
        Explicitly acquire simulation_state from parent
      """
      return self.aq_parent.getSimulationState()
    
    
    # MatrixBox methods      
    security.declareProtected( Permissions.ModifyPortalContent, 'hasCellContent' )
    def hasCellContent(self, base_id='movement'):
      """
          This method can be overriden
      """
      return 0

    security.declareProtected(Permissions.AccessContentsInformation, 'isAccountable')
    def isAccountable(self):
      """
        Returns 1 if this needs to be accounted
        Only account movements which are not associated to a delivery
        Whenever delivery is there, delivery has priority
      """
      return self.aq_parent.aq_parent.isAccountable()

    security.declareProtected( Permissions.AccessContentsInformation, 'getProperty' )
    def getProperty(self, key, d=None):
      """
        Generic accessor. First we check if the value
        exists. Else we call the real accessor
      """

      #try:
      if 1:
        # If mapped_value_property_list is not set
        # then it creates an exception
        if key in self.getMappedValuePropertyList([]):
          if getattr(self, key, None) is not None:
            LOG("Found Prop",0,"")
            return getattr(self, key)
          else:
            LOG("Not Found Prop",0,"")
            return self.aq_parent.getProperty(key)
      #except:
      #  LOG("WARNING: ERP5", 0, 'Could not access mapped value property %s' % key)
      #  return None
      # Standard accessor
      try:
        result = Movement.getProperty(self, key, d=d)
      except:
        result = None
      return result

    security.declareProtected( Permissions.ModifyPortalContent, 'updatePrice' )
    def updatePrice(self):
      if 'price' in self.getMappedValuePropertyList([]):
        # Try to compute an average price by accessing simulation movements
        # This should always return 0 in the case of OrderCell
        total_quantity = 0.0
        total_price = 0.0
        for m in self.getDeliveryRelatedValueList(portal_type="Simulation Movement"):
          order = m.getOrderValue()
          if order is not None:
            # Price is defined in an order
            price = m.getPrice()
            quantity = m.getQuantity()
            try:
              price = float(price)
              quantity = float(quantity)
            except:
              price = 0.0
              quantity = 0.0
            total_quantity += quantity
            total_price += quantity * price
        if total_quantity:
          # Update local price
          # self._setPrice(total_price / total_quantity)
          self.setPrice( total_price / total_quantity )

    security.declareProtected( Permissions.AccessContentsInformation, 'getPrice' )
    def getPrice(self, context=None, REQUEST=None, **kw):
      """
        Returns the price if defined on the cell
        or acquire it
      """
      # Call a script on the context
      if 'price' in self.getMappedValuePropertyList([]):
        if getattr(aq_base(self), 'price', None) is not None:
          return getattr(self, 'price') # default returns a price defined by the mapped value
        else:
          return self.aq_parent.getProperty('price') # Price is acquired
      else:
        return None

    security.declareProtected( Permissions.AccessContentsInformation, 'getQuantity' )
    def getQuantity(self):
      """
        Returns the quantity if defined on the cell
        or acquire it
      """
      # Call a script on the context
      if 'quantity' in self.getMappedValuePropertyList([]):
        if getattr(aq_base(self), 'quantity', None) is not None:
          return getattr(self, 'quantity')
        else:
          return self.aq_parent.getProperty('quantity')
      else:
        return self.getQuantity() # We have acquisition here which me should mimic
        # return None

    def _setItemIdList(self, value):
      """
        Computes total_quantity of all given items and stores this total_quantity
        in the quantity attribute of the cell
      """
      previous_item_list = self.getAggregateValueList()
      given_item_id_list = value
      item_object_list = []
      for item in given_item_id_list :
        item_result_list = self.portal_catalog(id = item, portal_type="Piece Tissu")
        if len(item_result_list) == 1 :
          try :
            object = item_result_list[0].getObject()
          except :
            object = None
        else :
          object = None

        if object is not None :
          # if item was in previous_item_list keep it
          if object in previous_item_list :
            # we can add this item to the list of aggregated items
            item_object_list.append(object)
          # if new item verify if variated_resource of item == variated_resource of movement
          elif (self.getResource() == object.getResource()) and (self.getVariationCategoryList() == object.getVariationCategoryList()) :
            # now verify if item can be moved (not already done)
            last_location_title = object.getLastLocationTitle()
            if self.getDestinationTitle() != last_location_title or last_location_title == '' :
              # we can add this item to the list of aggregated items
              item_object_list.append(object)

      # update item_id_list and build relation
      self.setAggregateValueList(item_object_list)

      # update quantity if needed
      if len(item_object_list)>0 :
        quantity = 0

        for object_item in item_object_list :
          if self.aq_parent.aq_parent.getPortalType() in ('Purchase Packing List', ) :
            quantity += object_item.getQuantity()
          else :
            quantity += object_item.getRemainingQuantity()
            # we reset the location of the item
            object_item.setLocation('')

        self.setTargetQuantity(quantity)

#     security.declareProtected(Permissions.ModifyPortalContent, 'applyTargetSolver')
#     def applyTargetSolver(self, solver):
#       for my_simulation_movement in self.getDeliveryRelatedValueList(portal_type = 'Simulation Movement'):
#         self.portal_simulation.applyTargetSolver(my_simulation_movement, solver)

    # Required for indexing
    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoriatedQuantity')
    def getInventoriatedQuantity(self):
      """
      """
      return Movement.getInventoriatedQuantity(self)

    security.declareProtected(Permissions.AccessContentsInformation, 'getStartDate')
    def getStartDate(self):
      """
      """
      return self._baseGetStartDate()

    security.declareProtected(Permissions.AccessContentsInformation, 'getStopDate')
    def getStopDate(self):
      """
      """
      return self._baseGetStopDate()

    security.declareProtected(Permissions.AccessContentsInformation, 'getStopDate')
    def getRootDeliveryValue(self):
      """
      Returns the root delivery responsible of this cell
      """
      return self.getParent().getRootDeliveryValue()

    # Simulation Consistency Check
    def getSimulationQuantity(self):
      """
          Computes the quantities in the simulation
      """
      if isinstance(self, OrderLine):
        result = self.OrderLine_zGetRelatedQuantity(uid=self.getUid())
        if len(result) > 0:
          return result[0].quantity
        return None
      else:
        result = self.DeliveryLine_zGetRelatedQuantity(uid=self.getUid())
        if len(result) > 0:
          return result[0].quantity
        return None

    security.declareProtected( Permissions.ModifyPortalContent, 'notifyAfterUpdateRelatedContent' )
    def notifyAfterUpdateRelatedContent(self, previous_category_url, new_category_url):
      """
        Membership Crirerions and Category List are same in DeliveryCell
        Must update it (or change implementation to remove data duplication)
      """
      update_method = self.portal_categories.updateRelatedCategory
      predicate_value = self.getPredicateValueList()
      new_predicate_value = map(lambda c: update_method(c, previous_category_url, new_category_url), predicate_value)
      self._setPredicateValueList(new_predicate_value) # No reindex needed since uid stable

    security.declarePrivate( '_edit' )
    def _edit(self, REQUEST=None, force_update = 0, reindex_object = 0, **kw):
      """
      """
      MappedValue._edit(self, REQUEST=REQUEST, force_update = force_update,
                           reindex_object=reindex_object, **kw)
#       if self.isSimulated():
#         self.getRootDeliveryValue().activate().propagateResourceToSimulation()
      # This one must be the last
      if kw.has_key('item_id_list'):
        self._setItemIdList( kw['item_id_list'] )

    security.declareProtected(Permissions.ModifyPortalContent, 'updateSimulationDeliveryProperties')
    def updateSimulationDeliveryProperties(self, movement_list = None):
      """
      Set properties delivery_ratio and delivery_error for each simulation movement
      in movement_list (all movements by default), according to this delivery calculated quantity
      """
      parent = self.getParent()
      if parent is not None:
        parent = parent.getParent()
        if parent is not None:
          parent.updateSimulationDeliveryProperties(movement_list, self)
                                                    
