##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Products.ERP5.ERP5Globals import current_inventory_state_list
from Products.ERP5.Document.OrderLine import OrderLine
from Products.ERP5.Document.Movement import Movement
from Products.ERP5.Document.SetMappedValue import SetMappedValue

from zLOG import LOG

class DeliveryCell(SetMappedValue, Movement):
    """
      A DeliveryCell allows to define specific quantities
      for each variation of a resource in a delivery line.
    """

    meta_type = 'ERP5 Delivery Cell'
    portal_type = 'Delivery Cell'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1
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
                      , PropertySheet.Domain
                      , PropertySheet.MappedValue
                      , PropertySheet.ItemAggregation
                      )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
Une ligne tarifaire."""
         , 'icon'           : 'order_line_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addDeliveryCell'
         , 'immediate_view' : 'delivery_cell_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'delivery_cell_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'list'
          , 'name'          : 'Object Contents'
          , 'category'      : 'object_action'
          , 'action'        : 'folder_contents'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'delivery_cell_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'translate'
          , 'name'          : 'Translate'
          , 'category'      : 'object_action'
          , 'action'        : 'translation_template_view'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      }

    security.declarePrivate( '_edit' )
    def _edit(self, REQUEST=None, force_update = 0, **kw):
      SetMappedValue._edit(self, REQUEST=REQUEST, force_update = force_update, **kw)
      # This one must be the last
      if kw.has_key('item_id_list'):
        self._setItemIdList( kw['item_id_list'] )

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
        return self.getTargetQuantity() # We have acquisition here which me should mimic
        # return None

    security.declareProtected( Permissions.AccessContentsInformation, 'getTargetQuantity' )
    def getTargetQuantity(self):
      """
        Returns the target quantity if defined on the cell
        or acquire it
      """
      # Call a script on the context
      if 'target_quantity' in self.getMappedValuePropertyList([]):
        if getattr(aq_base(self), 'target_quantity', None) is not None:
          return getattr(self, 'target_quantity')
        else:
          return self.aq_parent.getProperty('target_quantity')
      else:
        return None

    def _setItemIdList(self, value):
      """
        Computes total_quantity of all given items and stores this total_quantity
        in the quantity attribute of the cell
      """
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

        self.setTargetQuantity(quantity)

    security.declareProtected(Permissions.ModifyPortalContent, 'applyTargetSolver')
    def applyTargetSolver(self, solver):
      for my_simulation_movement in self.getDeliveryRelatedValueList(portal_type = 'Simulation Movement'):
        self.portal_simulation.applyTargetSolver(my_simulation_movement, solver)

    # Required for indexing
    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoriatedQuantity')
    def getInventoriatedQuantity(self):
      """
        Take into account efficiency in converted target quantity
      """
      if self.getSimulationState() in current_inventory_state_list:
        # When an order is delivered, the target quantity should be considered
        # rather than the quantity
        return Movement.getNetConvertedTargetQuantity(self)
      else:
        return Movement.getInventoriatedQuantity(self)

    # Simulation Consistency Check
    def getRelatedQuantity(self):
      """
          Computes the quantities in the simulation
      """
      if isinstance(self, OrderLine):
        result = self.OrderLine_zGetRelatedQuantity(uid=self.getUid())
        if len(result) > 0:
          return result[0].target_quantity
        return None
      else:
        result = self.DeliveryLine_zGetRelatedQuantity(uid=self.getUid())
        if len(result) > 0:
          return result[0].quantity
        return None

    def getRelatedTargetQuantity(self):
      """
          Computes the target quantities in the simulation
      """
      if isinstance(self, OrderLine):
        result = self.OrderLine_zGetRelatedQuantity(uid=self.getUid())
        if len(result) > 0:
          return result[0].target_quantity
        return None
      else:
        result = self.DeliveryLine_zGetRelatedQuantity(uid=self.getUid())
        if len(result) > 0:
          return result[0].target_quantity
        return None
