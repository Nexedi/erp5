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

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5Type.Utils import cartesianProduct
from Products.ERP5Type.Base import TempBase

from Products.ERP5.Document.Amount import Amount
#from Products.ERP5.Document.TempAmount import TempAmount

from Products.CMFCore.Expression import Expression

from zLOG import LOG

class TransformedResource(XMLObject, XMLMatrix, Amount):
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
    security.declareObjectProtected(Permissions.View)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.CategoryCore
                      , PropertySheet.Amount
                      , PropertySheet.TransformedResource
                      )

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )



    ### Variation matrix definition
    #
    security.declareProtected(Permissions.AccessContentsInformation, 'updateVariationCategoryList')
    def updateVariationCategoryList(self):
      """
        Check if variation category list of the resource changed and update transformed resource
        by doing a set cell range
      """
      self.setQVariationBaseCategoryList( self.getQVariationBaseCategoryList() )
      self.setVVariationBaseCategoryList( self.getVVariationBaseCategoryList() )

    security.declareProtected(Permissions.ModifyPortalContent, '_updateQMatrixCellRange')
    def _updateQMatrixCellRange(self):
      cell_range =  self.TransformedResource_asCellRange('quantity')

#      XXX TransformedResource works only for a maximum of 3 variation base category...
#      Matrixbox must be rewrite for a clean implementation of n base category
      if len(cell_range) <= 3:
        self.setCellRange(base_id='quantity', *cell_range)
      else:
        raise MoreThan3VariationBaseCategory

    security.declareProtected(Permissions.ModifyPortalContent, '_setQVariationBaseCategoryList')
    def _setQVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Quantity value (Q)
        variate on
      """
      self._baseSetQVariationBaseCategoryList(value)
      self._updateQMatrixCellRange()

    security.declareProtected(Permissions.ModifyPortalContent, 'setQVariationBaseCategoryList')
    def setQVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Quantity value (Q)
        variate on and reindex the object
      """
      self._setQVariationBaseCategoryList(value)
      self.reindexObject()

    security.declareProtected(Permissions.ModifyPortalContent, '_updateVMatrixCellRange')
    def _updateVMatrixCellRange(self):
      cell_range =  self.TransformedResource_asCellRange('variation')
#      XXX TransformedResource works only for a maximum of 3 variation base category...
#      Matrixbox must be rewrite for a clean implementation of n base category
      if len(cell_range) <= 3:
        self.setCellRange(base_id='variation', *cell_range)
      else:
        raise MoreThan3VariationBaseCategory

    security.declareProtected(Permissions.ModifyPortalContent, '_setVVariationBaseCategoryList')
    def _setVVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Variation value (V)
        variate on
      """
      self._baseSetVVariationBaseCategoryList(value)
      self._updateVMatrixCellRange()

    security.declareProtected(Permissions.ModifyPortalContent, 'setVVariationBaseCategoryList')
    def setVVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Variation value (V)
        variate on and reindex the object
      """
      self._setVVariationBaseCategoryList(value)
      self.reindexObject()


    security.declareProtected(Permissions.AccessContentsInformation,'getVariationRangeCategoryItemList')
    def getVariationRangeCategoryItemList(self, base_category_list = ()):
        """
          Returns possible variation category values for the
          transformation according to the default resource.
          Possible category values is provided as a list of
          tuples (id, title). This is mostly
          useful in ERP5Form instances to generate selection
          menus.
          Display is left...
        """
        resource = self.getResourceValue()
        result = []
        if resource != None:
          if base_category_list is ():
            base_category_list = resource.getVariationBaseCategoryList()

          result = resource.getVariationRangeCategoryItemList(base_category_list=base_category_list )

        return result


    security.declareProtected(Permissions.AccessContentsInformation, 'getAggregatedAmountList')
    def getAggregatedAmountList(self, REQUEST):
      """
        Get all interesting amount value and return TempAmount
      """
      # Start filing the value holder with what we have now
      # Maybe we should define a ValueHolder class XXX
      # First we create a object which id is the id of the transformed_resource
        
      # create temporary object to store result
      tmp_amount = TempAmount(self.getId())

      # First, we set initial values for quantity and variation
      # Currently, we only consider discrete variations
      # Continuous variations will be implemented in a future version of ERP5
      transformation = self.aq_parent
      error_list = []
      variation = []
      quantity = self.getQuantity()
      quantity_unit = self.getQuantityUnit()
      efficiency =  self.getEfficiency()

      # We look up the resource involved in this transformed resource
      resource = self.getDefaultResourceValue()
      if resource == None:
        tmp_amount.addError("No ressource define.")
      else:
        resource_id = resource.getId()

        # XXX maybe this kind of constraints....
        # should be defined in the property sheet and handled
        # automaticaly
        if efficiency is None or efficiency is '' or efficiency == 0.0:
          efficiency = 1.0
        else:
          efficiency = float(efficiency)

        # and get some attributed we need for the summary
        priced_quantity = resource.getPricedQuantity()


        # XXX maybe this kind of constraints....
        # should be defined in the property sheet and handled
        # automaticaly
        try:
          priced_quantity = float(priced_quantity)
          if priced_quantity == 0.0: priced_quantity = 1.0
        except:
          priced_quantity = 1.0
          tmp_amount.addError("Priced Quantity could not be converted for resource %s" % resource_id )


        # source_base_price is the default base price.
        source_base_price = 0.0
        # base_price is defined according to the destination.
        base_price = 0.0
#        duration = 0.0
        is_variated_quantity = 0 # The variated quantity is 0 by default

        # Try to update some attributes based on the resource attributes
        if resource.hasDefaultBasePrice():
          base_price = resource.getBasePrice()
          try:
            base_price = float(base_price)
          except:
            base_price = 0.0
            tmp_amount.addError("Default base price could not be converted for resource %s" % resource_id )

        if resource.hasSourceBasePrice():
          source_base_price = resource.getSourceBasePrice()
          try:
            source_base_price = float(source_base_price)
          except:
            source_base_price = 0.0
            tmp_amount.addError("Source base price could not be converted for resource %s" % resource_id )


#        resource_quantity_unit = resource.getDefaultQuantityUnit()

#        # This is very dirty and we must do some real unit conversion here XXX
#        if quantity_unit == "Temps/Minute":
#          duration = quantity

        transformation_line = self

        # and then call edit to update its attributed
        # We do not want to reindex Temp object
        tmp_amount._edit(

            transformation = transformation,
            transformation_id = transformation.getId(),
            transformation_relative_url = transformation.getRelativeUrl(),

#            transformed_resource = self,
            transformation_line = self,
            transformation_line_id = transformation_line.getId(),
            transformation_line_relative_url = transformation_line.getRelativeUrl(),

            resource = resource,
            resource_id = resource.getId(),
            resource_relative_url = resource.getRelativeUrl(),

            # XXX is this really correct ?
            # Because specialise category on transformation defines template transformation
#            specialise_id = transformation.getId(),
#            specialise_relative_url = transformation.getRelativeUrl(),

            # Properties define on transformation line
            description =  self.getDescription(),
            quantity_unit = quantity_unit,
#            duration = duration,
            quantity = quantity,
            efficiency = efficiency,
            base_price = base_price,

            # Properties define on resource
            source_base_price = source_base_price,
#            resource_quantity_unit = resource_quantity_unit
            resource_quantity_unit = resource.getDefaultQuantityUnit()

#            total_source_base_price = 0.0,
#            total_base_price = 0.0,
#            total_duration = 0.0,
#            base_price_defined_by = '',
#            source_base_price_defined_by = '',
#            quantity_defined_by = '',
#            variation_defined_by = '',
        )


#        return tmp_amount

        # We are going to try to find which variation applies to the current REQUEST
        # First we initialize variation to the default variation value define by
        # the transformed resource
        variation = self.getVariationCategoryList()
        variation_base_category_list = resource.getVariationBaseCategoryList()

        self.portal_categories.setCategoryMembership(tmp_amount, variation_base_category_list, variation, base=1)

        
        # and update the price with the variation price if necessary
        # XXX do not understand why we get the default price define on transformation ?
#        for resource_variation in self.getValueList( variation_base_category_list, portal_type=self.getPortalVariationTypeList() ):
#
#          if resource_variation.hasDefaultBasePrice():
#            new_base_price = resource_variation.getBasePrice()
#            try:
#              new_base_price = float(new_base_price)
#            except:
#              new_base_price = 0.0
#
#              tmp_amount.addError("Default base price could not be converted for resource variation %s" % resource_variation.id )
#
#
#            if new_base_price > 0.0:
#              base_price = new_base_price
#              tmp_amount.base_price_defined_by = resource_variation.getId()
#            new_source_base_price = resource_variation.getSourceBasePrice()
#          if resource_variation.hasSourceBasePrice():
#            try:
#              new_source_base_price = float(new_source_base_price)
#            except:
#              new_source_base_price = 0.0
#
#              tmp_amount.addError("Source base price could not be converted for resource variation %s" % resource_variation.id )
#
#            if new_source_base_price > 0.0:
#
#              source_base_price = new_source_base_price
#              tmp_amount._edit(
#                source_base_price = new_source_base_price,
#                source_base_price_defined_by = resource_variation.getId()
#              )


        # Now, let us update variations and quantities
        # We will browse the mapped values and determine which apply
        for mapped_value in self.objectValues():
          if mapped_value.test(REQUEST):

            # Update attributes defined by the mapped value
            for attribute in mapped_value.getMappedValuePropertyList():

              setattr(tmp_amount, attribute, mapped_value.get(attribute))

              if attribute == 'quantity':
#                tmp_amount.quantity_defined_by = mapped_value.getId()
                tmp_amount._edit( 
                  quantity_defined_by = mapped_value.getId()
                )

                # If we have to do this, then there is a problem....
                # We'd better have better API for this, like an update function in the mapped_value
                try:
                  quantity = float(mapped_value.quantity)
                  is_variated_quantity = 1 # The variated quantity is 1
                  #                          when the quantity is defined by a variation matrix
                except:
                  tmp_amount.addError("Quantity defined by %s is not a float" % mapped_value.getId() )


            # Update categories defined by the mapped value
            base_category_list = mapped_value.getMappedValueBaseCategoryList()
            if len(base_category_list) > 0:
              tmp_amount.variation_defined_by = mapped_value.getId()
              #LOG('In Transformation prevariation',0,str(mapped_value.getCategoryMembershipList(base_category_list, base=1)))
              self.portal_categories.setCategoryMembership(tmp_amount, base_category_list,
                      mapped_value.getCategoryMembershipList(base_category_list, base=1), base=1)
              for resource_variation in mapped_value.getValueList(base_category_list,
                                                                  portal_type=self.getPortalVariationTypeList()):
                if resource_variation.hasDefaultBasePrice():
                  new_base_price = resource_variation.getBasePrice()
                  try:
                    new_base_price = float(new_base_price)
                  except:
                    new_base_price = 0.0
                    tmp_amount.addError("Default base price could not be converted for resource variation %s" % resource_variation.id )

                  if new_base_price > 0.0:
                    base_price = new_base_price
                    tmp_amount.base_price_defined_by = resource_variation.getId()
                if resource_variation.hasSourceBasePrice():
                  new_source_base_price = resource_variation.getSourceBasePrice()
                  try:
                    new_source_base_price = float(new_source_base_price)
                  except:
                    new_source_base_price = 0.0
                    tmp_amount.addError("Source base price could not be converted for resource variation %s" % resource_variation.id )
                  if new_source_base_price > 0.0:
                    source_base_price = new_source_base_price
                    tmp_amount.source_base_price_defined_by = resource_variation.getId()



        # Convert Quantities
        # XXX XXX do not convert anymore ! Convert method must be define on TempAmount
#        converted_quantity = resource.convertQuantity(quantity, quantity_unit,
#                                                                resource_quantity_unit)
#        try:
#          converted_quantity = float(converted_quantity)
#        except:
#          converted_quantity = 0.0
#          error_list += ["Quantity could not be converted for resource %s" % resource.id]
#        # Convert price to unit price
#        unit_base_price = base_price / priced_quantity
#        unit_source_base_price = source_base_price / priced_quantity
#        variation = self.portal_categories.getCategoryMembershipList(tmp_amount,
#                                              variation_base_category_list, base=1)
#        #LOG('In Transformation variation',0,str(variation))
#        total_base_price = converted_quantity * unit_base_price / efficiency
#        total_source_base_price = converted_quantity * unit_source_base_price / efficiency
#        # Define variated price
#        if is_variated_quantity:
#          total_variated_base_price = total_base_price
#          total_variated_source_base_price = total_source_base_price
#        else:
#          total_variated_base_price = 0.0
#          total_variated_source_base_price = 0.0
#        # Create a nice presentation of the variation
#        pretty_variation = ''
#        for variation_item in variation:
#          pretty_variation += "<br>%s" % str(variation_item)
#        # Update the value and calculate total
#        tmp_amount.edit(
#          converted_quantity = converted_quantity,
#          base_price = base_price,
#          unit_base_price = unit_base_price,
#          total_base_price = total_base_price,
#          source_base_price = source_base_price,
#          unit_source_base_price = unit_source_base_price,
#          total_source_base_price = total_source_base_price,
#          variation = variation,
#          variation_category_list = variation,
#          quantity = quantity,
#          pretty_variation = pretty_variation,
#          error_list = error_list
#        )


#        return [tmp_amount], total_base_price, total_source_base_price, \
#              total_variated_base_price, total_variated_source_base_price, duration

        return tmp_amount
