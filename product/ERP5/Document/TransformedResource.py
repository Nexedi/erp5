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

from warnings import warn
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.XMLMatrix import XMLMatrix

from Products.ERP5.Document.Amount import Amount
from Products.ERP5.AggregatedAmountList import AggregatedAmountList

from Products.ERP5Type.Core.Predicate import Predicate

class TransformedResource(Predicate, XMLObject, XMLMatrix, Amount):
    """
        TransformedResource defines which
        resource is being transformed

        - variation
        - quantity

        Maybe defined by mapped values inside the transformed resource

      XXX Transformation works only for a miximum of 3 variation base category...
      Matrixbox must be rewrite for a clean implementation of n base category


    """

    meta_type = 'ERP5 Transformed Resource'
    portal_type = 'Transformed Resource'

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.CategoryCore
                      , PropertySheet.Amount
                      , PropertySheet.Reference
                      , PropertySheet.TransformedResource
                      )

    # Declarative interfaces
    zope.interface.implements(interfaces.IAmountGenerator,)

    ### Variation matrix definition
    #
    security.declareProtected(Permissions.AccessContentsInformation, 
                              'updateVariationCategoryList')
    def updateVariationCategoryList(self):
      """
        Check if variation category list of the resource changed and 
        update transformed resource by doing a set cell range
      """
      self.setQVariationBaseCategoryList(self.getQVariationBaseCategoryList())
      self.setVVariationBaseCategoryList(self.getVVariationBaseCategoryList())

    security.declareProtected(Permissions.ModifyPortalContent, 
                              '_setQVariationBaseCategoryList')
    def _setQVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Quantity value (Q)
        variate on
      """
      self._baseSetQVariationBaseCategoryList(value)
      self._updateCellRange('quantity')

    security.declareProtected(Permissions.ModifyPortalContent, 
                              'setQVariationBaseCategoryList')
    def setQVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Quantity value (Q)
        variate on and reindex the object
      """
      self._setQVariationBaseCategoryList(value)
      self.reindexObject()

    security.declareProtected(Permissions.ModifyPortalContent, 
                              '_setVVariationBaseCategoryList')
    def _setVVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Variation value (V)
        variate on
      """
      self._baseSetVVariationBaseCategoryList(value)
      self._updateCellRange('variation')

    security.declareProtected(Permissions.ModifyPortalContent, 
                              'setVVariationBaseCategoryList')
    def setVVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Variation value (V)
        variate on and reindex the object
      """
      self._setVVariationBaseCategoryList(value)
      self.reindexObject()

    def updateAggregatedAmountList(self, context, **kw):
      raise NotImplementedError('TODO')

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getAggregatedAmountList')
    def getAggregatedAmountList(self, context, REQUEST=None, **kw):
      """
        Get all interesting amount value and return AggregatedAmountList
      """
      # Create the result object
      aggregated_amount_list = AggregatedAmountList()
      test_result = self.test(context)
      if test_result:
        # The line must match the context
        # If no predicate is defined on line, the result of the test 
        # must be true
        # Create temporary object to store amount
        parent = self.getParentValue()
        # Be careful: this id must be unique, and change when the context is
        # changing. Failure to do so exposes to possible erroneous cache hits
        # for physical path based caching.
        tmp_id = '_'.join((parent.getId(), self.getId(), context.getId()))
        tmp_amount = parent.newContent(id=tmp_id,
                        temp_object=1, portal_type=self.getPortalType())
        # Create error string
        error_string = ''
        # Add resource relation
        resource = self.getDefaultResourceValue()
        if resource is not None:
          tmp_amount.setResourceValue(resource)
        else:
          error_string += 'No resource defined on %s' % self.getRelativeUrl()
        # First, we set initial values for quantity and variation
        # Currently, we only consider discrete variations
        # Continuous variations will be implemented in a future version 
        # of ERP5
        # Set quantity unit
        quantity_unit = self.getQuantityUnit()
        if quantity_unit is not None:
          tmp_amount.setQuantityUnitValue(quantity_unit)
        # Set efficiency
        efficiency =  self.getEfficiency()
        if efficiency is None or efficiency is '' or efficiency == 0.0:
          efficiency = 1.0
        else:
          efficiency = float(efficiency)
### current get quantity comportment exemple ###
# We define on transformation line:
#   default_quantity = q
#   quantity matrix
#     |   Child | Child/32 | Child/34 | Men | Women |
#     |   a     |          |   b      | c   |       |
# Result from getAggregatedAmountList:
#               context   |    quantity
#              _________________________
#               Child     |       a
#               Child/32  |       a      => acquired from Child
#               Child/34  |       a or b => we do not know which cell will be choosed
#               Child/36  |       a      => acquired from Child 
#               Men       |       c
#               Women     |       Error  => no cell found
#               noContext |       Error  => cell exist, but no context given

### comportment that JPS want ?? ###
# We define on transformation line:
#   default_quantity = q
#   quantity matrix
#     |   Child | Child/32 | Child/34 | Men | Women |
#     |   a     |          |   b      | c   |       |
# Result from getAggregatedAmountList:
#               context   |    quantity
#              _________________________
#               Child     |       a
#               Child/32  |       a      => acquired from Child
#               Child/34  |       a or b => we do not know which cell will be choosed
#               Child/36  |       Error  => no such key in matrixbox cell range
#               Men       |       c
#               Women     |       Error  => no cell found
#               noContext |       Error  => cell exist, but no context given

# futur cool get quantity comportment exemple 
# We define on transformation line:
#   default_quantity = q
#   quantity matrix
#     |   Child | Child/32 | Child/34 | Men | Women |
#     |   a     |          |   b      | c   |       |
# Result from getAggregatedAmountList:
#               context   |    quantity
#              _________________________
#               Child     |       a
#               Child/32  |       a      => acquired from Child
#               Child/34  |       b      =>   test method must return a priority to choose between Child and Child/34
#               Child/36  |       Error  => no such key in matrixbox cell range
#               Men       |       c
#               Women     |       q      =>   acquired from default quantity
#               noContext |       q      =>   acquired from default quantity

        # get Quantity
        quantity_defined_by = None
        quantity = None
        # We will browse the mapped values and determine which apply
        cell_key_list = self.getCellKeyList(base_id='quantity')
        if cell_key_list not in [(),[]]:
          if context is None:
            raise KeyError, \
                  "No context defined on TransformedResource '%s'" % \
                      (self.getRelativeUrl(), )
          for key in cell_key_list:
            if self.hasCell(base_id='quantity', *key):
              mapped_value = self.getCell(base_id='quantity', *key)
              if mapped_value.test(context):
                if 'quantity' in mapped_value.getMappedValuePropertyList():
                  quantity = mapped_value.getProperty('quantity')
                  quantity_defined_by = mapped_value.getRelativeUrl()
          if quantity in [None,'']:
            raise KeyError, \
                  "No cell quantity matching on TransformedResource '%s' for "\
                  "current context" % ( self.getRelativeUrl() ,   )
        else:
          quantity = self.getQuantity()
          quantity_defined_by = self.getRelativeUrl()
        if quantity in [None,'']:
          raise KeyError, \
                "No quantity defined on TransformedResource '%s' for "\
                "current context" % (self.getRelativeUrl(), )
        # If we have to do this, then there is a problem....
        # We'd better have better API for this, 
        # like an update function in the mapped_value
        try:
          quantity = float(quantity)
        except ValueError:
          error_string += 'Quantity is not a float.'

        # If IAmount specifies that 4 resources are needed, all quantities
        # need to be multiplicated by 4...
        context_quantity = None
        quantity_getter = getattr(context, "getQuantity", None)
        if quantity_getter is not None:
          _marker = object()
          context_quantity = quantity_getter(_marker)
          if context_quantity is _marker:
            # XXX Backwards compatibility:
            # previously, quantity property of the Amount was completely
            # ignored, and was assumed to be 1.0 . Re-enact this old
            # behavior (quantity default value is 0.0) to avoid breakages
            warn("No quantity was defined on the Amount passed to " \
                 "getAggregatedAmountList, 1.0 was assumed", DeprecationWarning)
            context_quantity = 1.0
        else:
          raise KeyError("No quantity defined on context")
        quantity *= float(context_quantity)

        # Get the variation category list
        variation_category_list_defined_by = None
        variation_category_list = None
        # We will browse the mapped values and determine which apply
        cell_key_list = self.getCellKeyList( base_id = 'variation')
        if cell_key_list not in [(),[]]:
          if context is None:
            raise KeyError, \
                  "No context defined on TransformedResource '%s'" % \
                      (self.getRelativeUrl(), )
          for key in cell_key_list:
            if self.hasCell(base_id='variation', *key):
              mapped_value = self.getCell(base_id='variation', *key)
              if mapped_value.test(context):
                vcl = mapped_value.getCategoryList()
                if vcl != []:
                  variation_category_list = vcl
                  variation_category_list_defined_by = \
                      mapped_value.getRelativeUrl()
          if variation_category_list in [None,'',[], ()]:
            if quantity == 0:
              return aggregated_amount_list
            else:
              raise KeyError, \
                    "No cell variation matching on TransformedResource '%s' "\
                    "for current context" % (self.getRelativeUrl(), )
        else:
          variation_category_list = self._getVariationCategoryList()
          variation_category_list_defined_by = self.getRelativeUrl()
        if hasattr(self,"getTradePhase"):
          # After installing BPM, trade_phase category to be exists
          trade_phase = self.getTradePhase()
        else:
          trade_phase = None
        # Store values in Amount
        tmp_amount._edit(
          # Properties define on transformation line
          title=self.getTitle(),
          description=self.getDescription(),
          efficiency=efficiency,
          quantity=quantity,
          # This fields only store some informations for debugging if necessary
          quantity_defined_by=quantity_defined_by,
          variation_category_list_defined_by=variation_category_list_defined_by,
          trade_phase=trade_phase,
          error_string=error_string
        )
        tmp_amount.setVariationCategoryList(variation_category_list)
        # Variation property dict
        tmp_amount.setVariationPropertyDict(self.getVariationPropertyDict())
        aggregated_amount_list.append(tmp_amount)
      return aggregated_amount_list
