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
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Base import Base

from Products.ERP5.Document.Movement import Movement
from Products.ERP5.Variated import Variated

from zLOG import LOG

class DeliveryLine(Movement, XMLObject, XMLMatrix, Variated):
    """
      A DeliveryLine object allows to implement lines in
      Deliveries (packing list, order, invoice, etc.)

      It may include a price (for insurance, for customs, for invoices,
      for orders)
    """

    meta_type = 'ERP5 Delivery Line'
    portal_type = 'Delivery Line'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.Amount
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      , PropertySheet.Price
                      , PropertySheet.VariationRange
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
         , 'factory'        : 'addDeliveryLine'
         , 'immediate_view' : 'delivery_line_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'delivery_line_view'
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
          , 'action'        : 'order_line_print'
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

    # Multiple inheritance definition
    updateRelatedContent = XMLMatrix.updateRelatedContent

    # Explicit acquisition of aq_dynamic generated method
    security.declareProtected(Permissions.AccessContentsInformation, 'getSimulationState')
    def getSimulationState(self):
      """
        Explicitly acquire simulation_state from parent
      """
      return self.aq_parent.getSimulationState()
    
    # Force in _edit to modify variation_base_category_list first
    security.declarePrivate( '_edit' )
    def _edit(self, REQUEST=None, force_update = 0, **kw):
      # We must first prepare the variation_base_category_list before we do the edit of the rest
      #LOG('in edit', 0, str(kw))
      if kw.has_key('variation_base_category_list'):
        self._setVariationBaseCategoryList( kw['variation_base_category_list'] )
      if kw.has_key('variation_category_list'):
        self._setVariationCategoryList( kw['variation_category_list'] )
      Movement._edit(self, REQUEST=REQUEST, force_update = force_update, **kw)
      # This one must be the last
      if kw.has_key('item_id_list'):
        self._setItemIdList( kw['item_id_list'] )
      if self.isSimulated():
        self.getRootDeliveryValue().edit() # So that we make sure that automatic workflow transitions
                                           # will be activated on the delivery
        self.getRootDeliveryValue().activate().propagateResourceToSimulation()

    # We must check if the user has changed the resource of particular line
    security.declareProtected( Permissions.ModifyPortalContent, 'edit' )
    def edit(self, REQUEST=None, force_update = 0, reindex_object=1, **kw):
      return self._edit(REQUEST=REQUEST, force_update=force_update, reindex_object=reindex_object, **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'isAccountable')
    def isAccountable(self):
      """
        Returns 1 if this needs to be accounted
        Only account movements which are not associated to a delivery
        Whenever delivery is there, delivery has priority
      """
      return self.aq_parent.isAccountable() and (not self.hasCellContent())

    # Pricing
    security.declareProtected(Permissions.ModifyPortalContent, 'updatePrice')
    def updatePrice(self):
      """
        Tries to find out a price for this movement
      """
      if not self.hasCellContent():
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
      else:
        for c in self.objectValues():
          if hasattr(aq_base(c), 'updatePrice'):
            c.updatePrice()

    def _getTotalPrice(self, context):
      if not self.hasCellContent():
        price = self.getPrice(context=context)
        if price is None: price = 0.0 # Quick and dirty fix XXX
        return self.getQuantity() * price
      else:
        # Use MySQL
        aggregate = self.DeliveryLine_zGetTotal()[0]
        return aggregate.total_price

    def _getTargetTotalPrice(self, context):
      if not self.hasCellContent():
        target_quantity = self.getTargetQuantity() or 0.0
        price = self.getPrice(context=context) or 0.0
        return target_quantity * price
      else:
        # Use MySQL
        aggregate = self.DeliveryLine_zGetTotal()[0]
        return aggregate.target_total_price

    security.declareProtected(Permissions.AccessContentsInformation, 'getTotalQuantity')
    def getTotalQuantity(self):
      """
        Returns the quantity if no cell or the total quantity if cells
      """
      if not self.hasCellContent():
        return self.getQuantity()
      else:
        # Use MySQL
        aggregate = self.DeliveryLine_zGetTotal()[0]
        return aggregate.total_quantity

    security.declareProtected(Permissions.AccessContentsInformation, 'getTargetTotalQuantity')
    def getTargetTotalQuantity(self):
      """
        Returns the quantity if no cell or the total quantity if cells
      """
      if not self.hasCellContent():
        return self.getTargetQuantity()
      else:
        # Use MySQL
        aggregate = self.DeliveryLine_zGetTotal()[0]
        return aggregate.target_total_quantity

    # Cell Related
    security.declareProtected( Permissions.ModifyPortalContent, 'newCellContent' )
    def newCellContent(self, id):
      """
          This method can be overriden
      """
      self.invokeFactory(type_name="Delivery Cell",id=id)
      return self.get(id)

    security.declareProtected( Permissions.ModifyPortalContent, 'hasCellContent' )
    def hasCellContent(self, base_id='movement'):
      """
          This method can be overriden
      """
      return XMLMatrix.hasCellContent(self, base_id=base_id)
      # If we need it faster, we can use another approach...
      return len(self.contentValues()) > 0

    security.declareProtected( Permissions.AccessContentsInformation, 'getCellValueList' )
    def getCellValueList(self, base_id='movement'):
      """
          This method can be overriden
      """
      return XMLMatrix.getCellValueList(self, base_id=base_id)

    security.declareProtected( Permissions.View, 'getCell' )
    def getCell(self, *kw , **kwd):
      """
          This method can be overriden
      """
      if 'base_id' not in kwd:
        kwd['base_id'] = 'movement'

      return XMLMatrix.getCell(self, *kw, **kwd)

    security.declareProtected( Permissions.ModifyPortalContent, 'newCell' )
    def newCell(self, *kw, **kwd):
      """
          This method creates a new cell
      """
      if 'base_id' not in kwd:
        kwd['base_id'] = 'movement'

      return XMLMatrix.newCell(self, *kw, **kwd)

    # For generation of matrix lines
    security.declareProtected( Permissions.ModifyPortalContent, '_setVariationCategoryList' )
    def _setVariationCategoryList(self, value):
      """
          Define the indices provided
          one list per index (kw)

          Any number of list can be provided
      """
      Movement._setVariationCategoryList(self, value)
      # Update the cell range automatically
      # This is far from easy and requires some specific wizzardry
      base_id = 'movement'
      kwd = {'base_id': base_id}
      new_range = self.DeliveryLine_asCellRange() # This is a site dependent script
      self._setCellRange(*new_range, **kwd )
      #LOG('setCellRange',0,str(new_range))
      cell_range_key_list = self.getCellRangeKeyList(base_id = base_id)
      #LOG('cell_range_key_list',0,str(self.getCellRange(base_id = base_id)))
      if cell_range_key_list <> [[None, None]] :
        for k in cell_range_key_list:
          #LOG('new cell',0,str(k))
          c = self.newCell(*k, **kwd)
          c.edit( domain_base_category_list = self.getVariationBaseCategoryList(),
                  mapped_value_property_list = ('target_quantity', 'quantity', 'price',),
                  #predicate_operator = 'SUPERSET_OF',
                  membership_criterion_category = filter(lambda k_item: k_item is not None, k),
                  variation_category_list = filter(lambda k_item: k_item is not None, k),
                  force_update = 1
                ) # Make sure we do not take aquisition into account
      else:
        # If only one cell, delete it
        cell_range_id_list = self.getCellRangeIdList(base_id = base_id)
        for k in cell_range_id_list:
          if self.get(k) is not None:
            self[k].flushActivity(invoke=0)
            self[k].immediateReindexObject() # We are forced to do this is url is changed (not uid)
            self._delObject(k)

      # TO BE DONE XXX
      # reindex cells when price, quantity or source/dest changes

    security.declareProtected(Permissions.View, 'isDivergent')
    def isDivergent(self):
      """
        Returns 1 if the target is not met according to the current information
        After and edit, the isOutOfTarget will be checked. If it is 1,
        a message is emitted

        emit targetUnreachable !
      """
      if self.hasCellContent():
        for cell in self.contentValues(filter={'portal_type': 'Delivery Cell'}):
          if cell.isDivergent():
            return 1
      else:
         return Movement.isDivergent(self)

    security.declareProtected(Permissions.ModifyPortalContent, 'applyTargetSolver')
    def applyTargetSolver(self, solver):
      for my_simulation_movement in self.getDeliveryRelatedValueList(portal_type = 'Simulation Movement'):
        self.portal_simulation.applyTargetSolver(my_simulation_movement, solver)

    def applyToDeliveryLineRelatedMovement(self, portal_type='Simulation Movement', method_id = 'expand'):
      # Find related in simulation
      for my_simulation_movement in self.getDeliveryRelatedValueList(
                                              portal_type = 'Simulation Movement'):
        # And apply
        getattr(my_simulation_movement.getObject(), method_id)()
      for c in self.contentValues(filter={'portal_type': 'Delivery Cell'}):
        for my_simulation_movement in c.getDeliveryRelatedValueList(
                                              portal_type = 'Simulation Movement'):
          # And apply
          getattr(my_simulation_movement.getObject(), method_id)()

    def reindexObject(self, *k, **kw):
      """
        Reindex children and simulation
      """
      if self.isIndexable:
        # Reindex children
        self.activate().recursiveImmediateReindexObject()
        # NEW: we never rexpand simulation - This is a task for DSolver / TSolver
        # self.activate().applyToDeliveryLineRelatedMovement(method_id = 'expand')

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoriatedQuantity')
    def getInventoriatedQuantity(self):
      """
        Take into account efficiency in converted target quantity
        Maybe we should only use target if isDivergent
      """
      if self.getSimulationState() in self.getPortalTargetInventoryStateList():
        # When an order is delivered, the target quantity should be considered
        # rather than the quantity
        return Movement.getNetConvertedTargetQuantity(self)
      else:
        return Movement.getInventoriatedQuantity(self)

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoriatedStartDate')
    def getInventoriatedStartDate(self):
      """
        Take into account efficiency in converted target quantity
      """
      if self.getSimulationState() in self.getPortalCurrentInventoryStateList():
        # When an order is delivered, the target quantity should be considered
        # rather than the quantity
        return Movement.getTargetStartDate(self)
      else:
        return Movement.getStartDate(self)

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoriatedStopDate')
    def getInventoriatedStopDate(self):
      """
        Take into account efficiency in converted target quantity
      """
      if self.getSimulationState() in self.getPortalCurrentInventoryStateList():
        # When an order is delivered, the target quantity should be considered
        # rather than the quantity
        return Movement.getTargetStopDate(self)
      else:
        return Movement.getStopDate(self)

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
          if self.aq_parent.getPortalType() in ('Purchase Packing List', ) :
            quantity += object_item.getQuantity()
          else :
            quantity += object_item.getRemainingQuantity()
            # we reset the location of the item
            object_item.setLocation('')

        self.setTargetQuantity(quantity)


    security.declarePrivate('_checkConsistency')
    def _checkConsistency(self, fixit=0, mapped_value_property_list = ('target_quantity', 'quantity', 'price')):
      """
        Check the constitency of transformation elements
      """
      error_list = XMLMatrix._checkConsistency(self, fixit=fixit)

      # First quantity
      # We build an attribute equality and look at all cells
      q_constraint = Constraint.AttributeEquality(
        domain_base_category_list = self.getVariationBaseCategoryList(),
        predicate_operator = 'SUPERSET_OF',
        mapped_value_property_list = mapped_value_property_list )
      for k in self.getCellKeys(base_id = 'movement'):
        kw={}
        kw['base_id'] = 'movement'
        c = self.getCell(*k, **kw)
        if c is not None:
          predicate_value = []
          for p in k:
            if p is not None: predicate_value += [p]
          q_constraint.edit(predicate_value_list = predicate_value)
          if fixit:
            error_list += q_constraint.fixConsistency(c)
          else:
            error_list += q_constraint.checkConsistency(c)
          if list(c.getVariationCategoryList()) != predicate_value:
            error_message =  "Variation %s but sould be %s" % (c.getVariationCategoryList(),predicate_value)
            if fixit:
              c.setVariationCategoryList(predicate_value)
              error_message += " (Fixed)"
            error_list += [(c.getRelativeUrl(), 'VariationCategoryList inconsistency', 100, error_message)]

      return error_list

    # Simulation Consistency Check
    def getSimulationQuantity(self):
      """
          Computes the quantities in the simulation
      """
      result = self.DeliveryLine_zGetRelatedQuantity(uid=self.getUid())
      if len(result) > 0:
        return result[0].quantity
      return None

    def getSimulationTargetQuantity(self):
      """
          Computes the target quantities in the simulation
      """
      result = self.DeliveryLine_zGetRelatedQuantity(uid=self.getUid())
      if len(result) > 0:
        return result[0].target_quantity
      return None

    def getSimulationSourceList(self):
      """
          Computes the sources in the simulation
      """
      result = self.DeliveryLine_zGetRelatedSource(uid=self.getUid())
      return map(lambda x: x.source, result)

    def getSimulationDestinationList(self):
      """
          Computes the destinations in the simulation
      """
      result = self.DeliveryLine_zGetRelatedDestination(uid=self.getUid())
      return map(lambda x: x.destination, result)

    def getSimulationSourceSectionList(self):
      """
          Computes the source sections in the simulation
      """
      result = self.DeliveryLine_zGetRelatedSourceSection(uid=self.getUid())
      return map(lambda x: x.source_section, result)

    def getSimulationDestinationSectionList(self):
      """
          Computes the destination sections in the simulation
      """
      result = self.DeliveryLine_zGetRelatedDestinationSection(uid=self.getUid())
      return map(lambda x: x.destination_section, result)

    security.declareProtected(Permissions.AccessContentsInformation, 'getStopDate')
    def getRootDeliveryValue(self):
      """
      Returns the root delivery responsible of this line
      """
      return self.getParent().getRootDeliveryValue()

