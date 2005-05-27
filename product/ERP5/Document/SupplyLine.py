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
    isPredicate = 1
    isAccountable = 0

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
                      , PropertySheet.Predicate
                      )

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

    def _getTotalPrice(self, context):
      return 0.0

    def _getDefaultTotalPrice(self, context):
      return 0.0

    security.declareProtected(Permissions.AccessContentsInformation, 'isAccountable')
    def isAccountable(self):
      """
        Returns 1 if this needs to be accounted
      """
      return 0

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

    security.declareProtected( Permissions.ModifyPortalContent, 'hasCellContent' )
    def hasCellContent(self, base_id='path'):
      """
          This method can be overriden
      """
      return int(XMLMatrix.getCellRange(self, base_id=base_id) != [])

    asPredicate = Path.asPredicate

    # For generation of matrix lines
    security.declareProtected( Permissions.ModifyPortalContent, '_setQuantityStepList' )
    def _setQuantityStepList(self, value):

      self._baseSetQuantityStepList(value)
      value = self.getQuantityStepList()
      value.sort()

      for pid in self.contentIds(filter={'portal_type': 'Predicate Group'}):
        self.deleteContent(pid)
      if len(value) > 0:
        #value = value
        value = [None] + value + [None]

        # With this script, we canc change customize the title of the predicate
        script = getattr(self,'SupplyLine_getTitle',None)

        for i in range(0, len(value) -1  ):
          min = value[i]
          max = value[i+1]
          p = self.newContent(id = 'quantity_range_%s' % str(i), portal_type = 'Predicate Group')
          p.setCriterionPropertyList(('quantity', ))
          p.setCriterion('quantity', min=min, max=max)
          if script is not None:
            title = script(min=min,max=max)
            p.setTitle(title)
          else:
            if min is None:
              p.setTitle(' quantity < %s' % repr(max))
            elif max is None:
              p.setTitle('%s <= quantity' % repr(min))
            else:
              p.setTitle('%s <= quantity < %s' % (repr(min),repr(max)))

      self.updateCellRange(base_id='path')

from Products.ERP5Type.Utils import monkeyPatch
monkeyPatch(SupplyLineMixin,SupplyLine)
