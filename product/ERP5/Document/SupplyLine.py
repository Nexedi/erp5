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
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5.Document.DeliveryLine import DeliveryLine
from Products.ERP5.Document.Path import Path
from Products.ERP5Type.Utils import convertToUpperCase

from zLOG import LOG

class SupplyLine(DeliveryLine, Path):
    """A Supply Line is a path to define price 
    """

    meta_type = 'ERP5 Supply Line'
    portal_type = 'Supply Line'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1
    isPredicate = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative interfaces
    __implements__ = ( interfaces.IVariated,
                       interfaces.IPredicate )

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.Amount
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      , PropertySheet.Price
                      , PropertySheet.SupplyLine
                      , PropertySheet.VariationRange
                      , PropertySheet.Path
                      , PropertySheet.FlowCapacity
                      , PropertySheet.Predicate
                      , PropertySheet.Comment
                      )

    #############################################
    # Pricing methods
    #############################################
    security.declareProtected(Permissions.AccessContentsInformation,
                              'getPrice')
    def getPrice(self):
      # If price not defined, look up price
      if getattr(self, 'price', None) is None:
        self.price = 0.0
      # Return the price
      return self.price

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getTotalPrice')
    def getTotalPrice(self):
      """
        Returns the totals price for this line
      """
      quantity = self.getQuantity() or 0.0
      price = self.getPrice() or 0.0
      return quantity * price

    def _getPrice(self, context):
       return 0.0

    def _getDefaultPrice(self, context):
       return 0.0

    def _getTotalPrice(self, context):
      return 0.0

    def _getDefaultTotalPrice(self, context):
      return 0.0

    security.declareProtected(Permissions.AccessContentsInformation,
                              'isAccountable')
    def isAccountable(self):
      """Supply Line are not accounted.
      """
      return 0

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getDefaultPrice')
    def getDefaultPrice(self, context=None, REQUEST=None, **kw):
      """
      """
      return self._getDefaultPrice(self.asContext(context=context,
                                                  REQUEST=REQUEST, **kw))

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getDefaultTotalPrice')
    def getDefaultTotalPrice(self, context=None, REQUEST=None, **kw):
      """
      """
      return self._getDefaultTotalPrice(self.asContext(context=context,
                                                       REQUEST=REQUEST, **kw))

    #############################################
    # Predicate method
    #############################################
    asPredicate = Path.asPredicate

    #############################################
    # XMLMatrix methods
    # XXX to be removed if possible
    #############################################
    security.declareProtected(Permissions.AccessContentsInformation,
                              'hasCellContent')
    def hasCellContent(self, base_id='path'):
      """
          This method can be overriden
      """
      return XMLMatrix.hasCellContent(self, base_id=base_id)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCellValueList' )
    def getCellValueList(self, base_id='path'):
      """
          This method can be overriden
      """
      return XMLMatrix.getCellValueList(self, base_id=base_id)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCell')
    def getCell(self, *kw , **kwd):
      """
          This method can be overriden
      """
      if 'base_id' not in kwd:
        kwd['base_id'] = 'path'
      return XMLMatrix.getCell(self, *kw, **kwd)

    security.declareProtected(Permissions.ModifyPortalContent, 'newCell')
    def newCell(self, *kw, **kwd):
      """
          This method creates a new cell
      """
      if 'base_id' not in kwd:
        kwd['base_id'] = 'path'
      return XMLMatrix.newCell(self, *kw, **kwd)

    ############################################################
    # Quantity predicate API
    ############################################################
    security.declareProtected(Permissions.AccessContentsInformation,
                              'getQuantityPredicateIdList')
    def getQuantityPredicateIdList(self, price_parameter):
      """
        Return predicate id related to a price parameter.
      """
      predicate_id_start_with = "quantity_range_"
      if price_parameter != "base_price":
        predicate_id_start_with = "%s_%s" % \
            (price_parameter, predicate_id_start_with)
      # XXX Hardcoded portal type name
      predicate_list = self.contentIds(filter={'portal_type': 'Predicate'})
      # XXX filtering can be done with contentIds ?
      result = [x for x in predicate_list \
              if x.startswith(predicate_id_start_with)]
      return result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getQuantityPredicateValueList')
    def getQuantityPredicateValueList(self, price_parameter):
      """
        Return predicate related to a price parameter.
      """
      result = [getattr(self, x) for x in \
              self.getQuantityPredicateIdList(price_parameter)]
      return result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getQuantityStepList')
    def getQuantityStepList(self, *args, **kw):
      """
        Return predicate step related to a price_parameter
      """
      # We need to keep compatibility with generated accessor
      price_parameter = kw.get('price_parameter', "base_price")
      if price_parameter == "base_price":
        method_name = "_baseGetQuantityStepList"
      else:
        method_name = 'get%sList' % \
                     convertToUpperCase("%s_quantity_step" % price_parameter)
      return getattr(self, method_name)()

    security.declareProtected(Permissions.ModifyPortalContent,
                              'updateQuantityPredicate')
    def updateQuantityPredicate(self, price_parameter):
      """
        Update the quantity predicate for this price parameter
      """
      quantity_step_list = self.getQuantityStepList(price_parameter=price_parameter)
      quantity_step_list.sort()
      
      # remove old predicates
      for pid in self.getQuantityPredicateIdList(price_parameter):
        self.deleteContent(pid)
      
      if quantity_step_list:
        quantity_step_list = [None] + quantity_step_list + [None]
        # With this script, we can change the title of the predicate
        script = getattr(self, 'SupplyLine_getTitle', None)
        predicate_id_start_with = "quantity_range"
        if price_parameter != "base_price":
          predicate_id_start_with = "%s_%s" % \
              (price_parameter, predicate_id_start_with)
        for i in range(0, len(quantity_step_list)-1):
          min_quantity = quantity_step_list[i]
          max_quantity = quantity_step_list[i+1]
          # XXX Hardcoded portal type name
          p = self.newContent(id='%s_%s' % (predicate_id_start_with, str(i)),
                              portal_type = 'Predicate')
          p.setCriterionPropertyList(('quantity', ))
          p.setCriterion('quantity', min=min_quantity, max=max_quantity)
          if script is not None:
            title = script(min=min_quantity, max=max_quantity)
            p.setTitle(title)
          else:
            if min_quantity is None:
              p.setTitle('quantity < %s' % max_quantity)
            elif max_quantity is None:
              p.setTitle('%s <= quantity' % min_quantity)
            else:
              p.setTitle('%s <= quantity < %s' % (min_quantity, max_quantity))


