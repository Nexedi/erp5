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

import ExtensionClass

from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLMatrix import XMLMatrix

from Products.ERP5.Document.DeliveryLine import DeliveryLine
from Products.ERP5.Document.Movement import Movement
from Products.ERP5.Document.Path import Path

from zLOG import LOG

class SupplyLineMixin(ExtensionClass.Base):
    
    security = ClassSecurityInfo()
  
    # Cell Related
#    security.declareProtected( Permissions.ModifyPortalContent, 'newCellContent' )
#    def newCellContent(self, id):
#      """
#          This method can be overriden
#      """
#      self.invokeFactory(type_name="Supply Cell",id=id)
#      return self.get(id)

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
        kwd['base_id'] = 'path'

      return XMLMatrix.getCell(self, *kw, **kwd)

    security.declareProtected( Permissions.ModifyPortalContent, 'newCell' )
    def newCell(self, *kw, **kwd):
      """
          This method creates a new cell
      """
      if 'base_id' not in kwd:
        kwd['base_id'] = 'path'

      return XMLMatrix.newCell(self, *kw, **kwd)
    
    security.declareProtected(Permissions.AccessContentsInformation, 'getUnitBasePrice')
    def getUnitBasePrice(self, context=None, REQUEST=None, **kw):
      """
      """
      tmp_context = self.asContext(context=context, REQUEST=REQUEST, **kw)

      base_id = 'path'
      # get Quantity
      base_price = None
      if tmp_context != None:
        # We will browse the mapped values and determine which apply
        cell_key_list = self.getCellKeyList( base_id = base_id )
        for key in cell_key_list:
          if self.hasCell(base_id=base_id, *key):
            mapped_value = self.getCell(base_id=base_id, *key)
            if mapped_value.test(tmp_context): 
              if 'price' in mapped_value.getMappedValuePropertyList():
                base_price = mapped_value.getProperty('price')

      if base_price in [None,'']:
        base_price = self.getBasePrice()

      priced_quantity = self.getPricedQuantity()

      try:
        unit_base_price = base_price / priced_quantity
      except: 
        unit_base_price = None

      return unit_base_price 
      
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

    # For generation of matrix lines
    security.declareProtected( Permissions.ModifyPortalContent, '_setQuantityStepList' )
    def _setQuantityStepList(self, value):        
      self._baseSetQuantityStepList(value)
      value = self.getQuantityStepList()
      value.sort()
      for pid in self.contentIds(filter={'portal_type': 'Predicate Group'}):
        self.deleteContent(pid)
      value = [None] + value + [None]
      for i in range(0, len(value) - 1):
        p = self.newContent(id = 'quantity_range_%s' % i, portal_type = 'Predicate Group')
        p.setCriterionPropertyList(('quantity', ))
        p.setCriterion('quantity', min=value[i], max=value[i+1])              
        p.setTitle('%s <= quantity < %s' % (repr(value[i]),repr(value[i+1])))
      self._setVariationCategoryList(self.getVariationCategoryList())


from Products.ERP5Type.Utils import monkeyPatch
monkeyPatch(SupplyLineMixin,SupplyLine)        
