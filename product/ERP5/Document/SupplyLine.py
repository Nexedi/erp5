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

from Products.CMFCore.WorkflowCore import WorkflowAction
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLMatrix import XMLMatrix

from Products.ERP5.Document.DeliveryLine import DeliveryLine
from Products.ERP5.Document.Movement import Movement
from Products.ERP5.Document.Path import Path

class SupplyLine(DeliveryLine, Path):
    """
      A DeliveryLine object allows to implement lines in
      Deliveries (packing list, order, invoice, etc.)

      It may include a price (for insurance, for customs, for invoices,
      for orders)
    """

    meta_type = 'ERP5 Supply Line'
    portal_type = 'Supply Line'
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
                      , PropertySheet.Path
                      , PropertySheet.FlowCapacity
                      )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
Une ligne tarifaire."""
         , 'icon'           : 'order_line_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addSupplyLine'
         , 'immediate_view' : 'supply_line_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'supply_line_view'
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

    # Cell Related
    security.declareProtected( Permissions.ModifyPortalContent, 'newCellContent' )
    def newCellContent(self, id):
      """
          This method can be overriden
      """
      self.invokeFactory(type_name="Delivery Cell",id=id)
      return self.get(id)

    security.declareProtected( Permissions.ModifyPortalContent, 'hasCellContent' )
    def hasCellContent(self, base_id='path'):
      """
          This method can be overriden
      """
      return XMLMatrix.hasCellContent(self, base_id=base_id)
      # If we need it faster, we can use another approach...
      return len(self.contentValues()) > 0

    security.declareProtected( Permissions.AccessContentsInformation, 'getCellValueList' )
    def getCellValueList(self, base_id='path'):
      """
          This method can be overriden
      """
      return XMLMatrix.getCellValueList(self, base_id=base_id)

    # Pricing methods
    security.declareProtected(Permissions.AccessContentsInformation, 'getPrice')
    def getPrice(self):
      # If price not defined, look up price
      if getattr(self, 'price', None) is None:
        self.price = 0.0
      # Return the price
      return self.price

    security.declareProtected(Permissions.AccessContentsInformation, 'getTotalPrice')
    def getTotalPrice(self):
      """
        Returns the totals price for this line
      """
      return self.getQuantity() * self.getPrice()

    def _getPrice(self, context):
       return 0.0

    def _getDefaultPrice(self, context):
       return 0.0

    def _getSourcePrice(self, context):
       return 0.0

    def _getDestinationPrice(self, context):
       return 0.0

    def _getTotalPrice(self, context):
      return 0.0

    def _getDefaultTotalPrice(self, context):
      return 0.0

    def _getSourceTotalPrice(self, context):
      return 0.0

    def _getDestinationTotalPrice(self, context):
      return 0.0

#     security.declareProtected(Permissions.AccessContentsInformation, 'getPrice')
#     def getPrice(self, context=None, REQUEST=None, **kw):
#       """
#       """
#       return self._getPrice(self.asContext(context=context, REQUEST=REQUEST, **kw))

    security.declareProtected(Permissions.AccessContentsInformation, 'getDefaultPrice')
    def getDefaultPrice(self, context=None, REQUEST=None, **kw):
      """
      """
      return self._getDefaultPrice(self.asContext(context=context, REQUEST=REQUEST, **kw))

    security.declareProtected(Permissions.AccessContentsInformation, 'getSourcePrice')
    def getSourcePrice(self, context=None, REQUEST=None, **kw):
      """
      """
      return self._getSourcePrice(self.asContext(context=context, REQUEST=REQUEST, **kw))

    security.declareProtected(Permissions.AccessContentsInformation, 'getDestinationPrice')
    def getDestinationPrice(self, context=None, REQUEST=None, **kw):
      """
      """
      return self._getDestinationPrice(self.asContext(context=context, REQUEST=REQUEST, **kw))

#     security.declareProtected(Permissions.AccessContentsInformation, 'getTotalPrice')
#     def getTotalPrice(self, context=None, REQUEST=None, **kw):
#       """
#       """
#       return self._getTotalPrice(self.asContext(context=context, REQUEST=REQUEST, **kw))

    security.declareProtected(Permissions.AccessContentsInformation, 'getDefaultTotalPrice')
    def getDefaultTotalPrice(self, context=None, REQUEST=None, **kw):
      """
      """
      return self._getDefaultTotalPrice(self.asContext(context=context, REQUEST=REQUEST, **kw))

    security.declareProtected(Permissions.AccessContentsInformation, 'getSourceTotalPrice')
    def getSourceTotalPrice(self, context=None, REQUEST=None, **kw):
      """
      """
      return self._getSourceTotalPrice(self.asContext(context=context, REQUEST=REQUEST, **kw))

    security.declareProtected(Permissions.AccessContentsInformation, 'getDestinationTotalPrice')
    def getDestinationTotalPrice(self, context=None, REQUEST=None, **kw):
      """
      """
      return self._getDestinationTotalPrice(self.asContext(context=context, REQUEST=REQUEST, **kw))


    # Cell Related
    security.declareProtected( Permissions.ModifyPortalContent, 'newCellContent' )
    def newCellContent(self, id):
      """
          This method can be overriden
      """
      self.invokeFactory(type_name="Supply Cell",id=id)
      return self.get(id)

    security.declareProtected( Permissions.ModifyPortalContent, 'hasCellContent' )
    def hasCellContent(self, base_id='path'):
      """
          This method can be overriden
      """
      return XMLMatrix.hasCellContent(self, base_id=base_id)
      # If we need it faster, we can use another approach...
      return len(self.contentValues()) > 0

    security.declareProtected( Permissions.AccessContentsInformation, 'getCellValueList' )
    def getCellValueList(self, base_id='path'):
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
        kwd['base_id'] = 'path'

      return XMLMatrix.newCell(self, *kw, **kwd)

    # For generation of matrix lines
    security.declareProtected( Permissions.ModifyPortalContent, '_setQuantityRangeList' )
    def _setQuantityRangeList(self, value):        
      self._baseSetQuantityRangeList(value)
      value = self.getQuantityRangeList()
      value.sort()
      for pid in self.contentIds(filter={'portal_type': 'Predicate'}):
        self.deleteContent(pid)
      value = value + [None]
      for i in range(0, len(value) - 1):
        p = self.newContent(id = 'quantity_range_%s' % i, portal_type = 'Predicate')
        p.setCriterionPropertyList(('quantity', ))
        p.setCriterion('quantity', min=value[i], max=value[i+1])              
      self._setVariationCategoryList(self.getVariationCategoryList())
    
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
      base_id = 'path'
      kwd = {'base_id': base_id}
      new_range = self.SupplyLine_asCellRange() # This is a site dependent script
      self._setCellRange(*new_range, **kwd )
      #LOG('setCellRange',0,str(new_range))
      cell_range_key_list = self.getCellRangeKeyList(base_id = base_id)
      #LOG('cell_range_key_list',0,str(self.getCellRange(base_id = base_id)))
      if cell_range_key_list <> [[None, None]] :
        for k in cell_range_key_list:
          #LOG('new cell',0,str(k))
          c = self.newCell(*k, **kwd)
          c.edit( domain_base_category_list = self.getVariationBaseCategoryList(),
                  mapped_value_property_list = ( 'price',),
                  predicate_operator = 'SUPERSET_OF',
                  predicate_value = filter(lambda k_item: k_item is not None, k),
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
