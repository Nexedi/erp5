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

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5Type.Utils import cartesianProduct
from Products.ERP5Type.Base import TempBase

from Products.ERP5.Document.Amount import Amount

from Products.CMFCore.Expression import Expression

from zLOG import LOG

class TransformedResource(XMLObject, XMLMatrix, Amount):
    """
        TransformedResource defines which
        resource is being transformed

        - variation
        - quantity

        Maybe defined by mapped values inside the transformed resource

        WARNING: the notion of category range is quite complex in this case.
           getVariationRangeCategoryList -> possible variations of the transformed
                                            resource ie. getVariationCategoryList
                                            of the resource
           getVariationCategoryList      -> variation value of the transformed
                                            resource (ie. default variation)

           getVariationRangeBaseCategoryList -> possible variation base categories
                                                of the transformed resource
                                                (ie. getVariationBaseCategoryList
                                                of the resource)
           getVariationBaseCategoryList      -> choice of variation base categories
                                                defined by the transformed resource
                          (should be the same as getVariationRangeBaseCategoryList)

           getTransformationVariationRangeBaseCategoryList OK
                                              -> possible variation base categories
                                                  which can be used the the
                                                 transformation matrix
                                                 (based on resource)
           getTransformationVariationBaseCategoryList OK
                                              -> choice of variation base categories
                                                  which can be used the the
                                                 transformation matrix
                                                 (based on resource)

           getTransformationVariationRangeCategoryList OK
                                              -> possible category values
                                                 which can be used in the
                                                 transformation matrix
                                                 (based on resource)
           getTransformationVariationCategoryList OK
                                              -> choice of category values
                                                 which can be used in the
                                                 transformation matrix

           XXX WE HAVE an issue here:
           - the variation range of the transformation
             defines both the variation range of the main resource
             and the variation range for matrices

           - where do we define default variation value
             for the resource produced by the transformation ?
             (probably in the domain fields)

           - where do we define selection parameters ?

           getResourceVariationCategoryList
           getResourceVariationRangeCategoryList

    """

    meta_type = 'ERP5 Transformed Resource'
    portal_type = 'Transformed Resource'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

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

    # Local property sheet
    _properties = (
      { 'id'          : 'variation_base_category',
        'storage_id'  : 'variation_base_category_list', # Coramy Compatibility
        'description' : "",
        'type'        : 'tokens',
        'acquisition_base_category' : ('resource',),
        'acquisition_portal_type'   : Expression('python: portal.getPortalResourceTypeList()'),
        'acquisition_copy_value'    : 0,
        'acquisition_mask_value'    : 0,
        'acquisition_sync_value'    : 0,
        'acquisition_accessor_id'   : 'getVariationBaseCategoryList', ### XXX BUG
        'acquisition_depends'       : None,
        'mode'        : 'w' },
    )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
A bank account number holds a collection of numbers
and codes (ex. SWIFT, RIB, etc.) which may be used to
identify a bank account."""
         , 'icon'           : 'transformed_resource_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addTransformedResource'
         , 'immediate_view' : 'transformed_resource_view'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'transformed_resource_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'transformed_resource_print'
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

    ### Variation matrix definition
    #
    security.declareProtected(Permissions.ModifyPortalContent, '_setQVariationBaseCategoryList')
    def _setQVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Quantity value (Q)
        variate on
      """
      self._baseSetQVariationBaseCategoryList(value)
      kwd = {}
      kwd['base_id'] = 'quantity'
      kw = []
      transformation = self.aq_parent
      line_id = transformation.getVariationBaseCategoryLine()
      column_id = transformation.getVariationBaseCategoryColumn()
      line = [[None]]
      column = [[None]]
      for v in value:
        if v == line_id:
          line = [transformation.getCategoryMembershipList(v,base=1)]
        elif v == column_id:
          column = [transformation.getCategoryMembershipList(v,base=1)]
        else:
          kw += [transformation.getCategoryMembershipList(v,base=1)]
      kw = line + column + kw
      self.setCellRange(*kw, **kwd)
      # Empty cells if no variation
      if line == [[None]] and column == [[None]]:
        self.delCells(base_id='quantity')
      # And fix it in case the cells are not renamed (XXX this will be removed in the future)
      self._checkConsistency(fixit=1)

    security.declareProtected(Permissions.ModifyPortalContent, 'setQVariationBaseCategoryList')
    def setQVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Quantity value (Q)
        variate on and reindex the object
      """
      self._setQVariationBaseCategoryList(value)
      self.reindexObject()

    security.declareProtected(Permissions.ModifyPortalContent, '_setVVariationBaseCategoryList')
    def _setVVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Variation value (V)
        variate on
      """
      self._baseSetVVariationBaseCategoryList(value)
      kwd = {}
      kwd['base_id'] = 'variation'
      kw = []
      transformation = self.aq_parent
      line_id = transformation.getVariationBaseCategoryLine()
      column_id = transformation.getVariationBaseCategoryColumn()
      line = [[None]]
      column = [[None]]
      for v in value:
        if v == line_id:
          line = [transformation.getCategoryMembershipList(v,base=1)]
        elif v == column_id:
          column = [transformation.getCategoryMembershipList(v,base=1)]
        else:
          kw += [transformation.getCategoryMembershipList(v,base=1)]
      kw = line + column + kw
      self.setCellRange(*kw, **kwd)
      # Empty cells if no variation
      if line == [[None]] and column == [[None]]:
        self.delCells(base_id='variation')
      # And fix it in case the cells are not renamed (XXX this will be removed in the future)
      self._checkConsistency(fixit=1)

    security.declareProtected(Permissions.ModifyPortalContent, 'setVVariationBaseCategoryList')
    def setVVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Variation value (V)
        variate on and reindex the object
      """
      self._setVVariationBaseCategoryList(value)
      self.reindexObject()

    # Methods for matrix UI widgets
    security.declareProtected(Permissions.AccessContentsInformation, 'getQLineItemList')
    def getQLineItemList(self):
      base_category = self.aq_parent.getVariationBaseCategoryLine()
      if base_category in self.getQVariationBaseCategoryList():
        clist = self.aq_parent.getCategoryMembershipList(base_category, base=1)
      else:
        clist = [None]
      result = []
      for c in clist:
        result += [(c,c)]

      result.sort() # XXX Temp until set / list issue solved
                    # solution is to use sets in some places and lists in others
                    # default and sets are used together
                    # list overrides default

      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getQColumnItemList')
    def getQColumnItemList(self):
      base_category = self.aq_parent.getVariationBaseCategoryColumn()
      if base_category in self.getQVariationBaseCategoryList():
        clist = self.aq_parent.getCategoryMembershipList(base_category, base=1)
      else:
        clist = [None]
      result = []
      for c in clist:
        result += [(c,c)]

      result.sort() # XXX Temp until set / list issue solved

      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getQTabItemList')
    def getQTabItemList(self):
      """
        Returns a list of items which can be used as index for
        each tab of a matrix or to define a cell range.
      """
      transformation = self.aq_parent
      line_id = transformation.getVariationBaseCategoryLine()
      column_id = transformation.getVariationBaseCategoryColumn()
      base_category_list = transformation.getVariationBaseCategoryList()
      base_category = []
      # Accumulate in base_category a list of list of relative_url
      # which correspond to category memberships not taken into
      # account in lines of columns
      for c in base_category_list:
        if not c in (line_id, column_id):
          if c in self.getQVariationBaseCategoryList():
            base_category += [transformation.getCategoryMembershipList(c, base=1)]
      if len(base_category) > 0:
        # Then make a cartesian product
        # to calculate all possible combinations
        clist = cartesianProduct(base_category)
        result = []
        for c in clist:
          result += [(c,c)]
      else:
        result = [(None,'')]

      result.sort() # XXX Temp until set / list issue solved

      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getVLineItemList')
    def getVLineItemList(self):
      base_category = self.aq_parent.getVariationBaseCategoryLine()
      if base_category in self.getVVariationBaseCategoryList():
        clist = self.aq_parent.getCategoryMembershipList(base_category, base=1)
      else:
        clist = [None]
      result = []
      for c in clist:
        result += [(c,c)]
      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getVColumnItemList')
    def getVColumnItemList(self):
      base_category = self.aq_parent.getVariationBaseCategoryColumn()
      if base_category in self.getVVariationBaseCategoryList():
        clist = self.aq_parent.getCategoryMembershipList(base_category, base=1)
      else:
        clist = [None]
      result = []
      for c in clist:
        result += [(c,c)]

      result.sort() # XXX Temp until set / list issue solved

      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getVTabItemList')
    def getVTabItemList(self):
      transformation = self.aq_parent
      line_id = transformation.getVariationBaseCategoryLine()
      column_id = transformation.getVariationBaseCategoryColumn()
      base_category_list = transformation.getVariationBaseCategoryList()
      base_category = []
      for c in base_category_list:
        if not c in (line_id, column_id):
          if c in self.getVVariationBaseCategoryList():
            base_category += [transformation.getCategoryMembershipList(c, base=1)]
      if len(base_category) > 0:
        clist = cartesianProduct(base_category)
        result = []
        for c in clist:
          result += [(c,c)]
      else:
        result = [(None,'')]

      result.sort() # XXX Temp until set / list issue solved

      return result

    security.declareProtected( Permissions.ModifyPortalContent, 'newCell' )
    def newCell(self, *kw, **kwd):
      result = XMLMatrix.newCell(self, *kw, **kwd)
      result._setPredicateOperator("SUPERSET_OF")
      membership_list = []
      for c in kw:
        if c is not None:
          membership_list += [c]
      result._setPredicateValueList(membership_list)
      base_id = kwd.get('base_id', 'cell')
      if base_id == 'quantity':
        result._setDomainBaseCategoryList(self.getQVariationBaseCategoryList())
      elif base_id == 'variation':
        result._setDomainBaseCategoryList(self.getVVariationBaseCategoryList())

      return result

    security.declareProtected( Permissions.ModifyPortalContent, 'newCellContent' )
    def newCellContent(self, id,**kw):
      """
          This method can be overriden
      """
      self.invokeFactory(type_name="Set Mapped Value",id=id)
      return self.get(id)

    security.declarePrivate('_checkConsistency')
    def _checkConsistency(self, fixit=0):
      """
        Check the constitency of transformation elements
      """
      error_list = XMLMatrix._checkConsistency(self, fixit=fixit)

      # Quantity should be empty if no variation
      q_range = self.getCellRange(base_id = 'quantity')
      if q_range is not None:
        if q_range[0] == [None] and q_range[1] == [None]:
          matrix_is_not_empty = 0
          for k in self.getCellIds(base_id = 'quantity'):
            if hasattr(self, k):matrix_is_not_empty = 1
          if matrix_is_not_empty:
            if fixit:
              self.delCells(base_id = 'quantity')
              error_message =  "Variation cells for quantity should be empty (fixed)"
            else:
              error_message =  "Variation cells for quantity should be empty"
            error_list += [(self.getRelativeUrl(),
                          'TransformedResource inconsistency', 100, error_message)]

      # Quantity should be empty if no variation
      v_range = self.getCellRange(base_id = 'variation')
      if v_range is not None:
        if v_range[0] == [None] and v_range[1] == [None]:
          matrix_is_not_empty = 0
          for k in self.getCellIds(base_id = 'variation'):
            if hasattr(self, k):matrix_is_not_empty = 1
          if matrix_is_not_empty:
            if fixit:
              self.delCells(base_id = 'variation')
              error_message =  "Variation cells for variation should be empty (fixed)"
            else:
              error_message =  "Variation cells for variation should be empty"
            error_list += [(self.getRelativeUrl(),
                          'TransformedResource inconsistency', 100, error_message)]

      # First quantity
      # We build an attribute equality and look at all cells
      q_constraint = Constraint.AttributeEquality(
        domain_base_category_list = self.getQVariationBaseCategoryList(),
        predicate_operator = 'SUPERSET_OF',
        mapped_value_property_list = ['quantity'] )
      for k in self.getCellKeys(base_id = 'quantity'):
        kw={}
        kw['base_id'] = 'quantity'
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

      # Then variation
      # We build an attribute equality and look at all cells
      v_constraint = Constraint.AttributeEquality(
        domain_base_category_list = self.getVVariationBaseCategoryList(),
        predicate_operator = 'SUPERSET_OF',
        mapped_value_base_category_list = self.getVariationBaseCategoryList() )
      LOG("Before checkConsistency", 0, str(self.getVariationBaseCategoryList()))
      for k in self.getCellKeys(base_id = 'variation'):
        kw={}
        kw['base_id'] = 'variation'
        c = self.getCell(*k, **kw)
        if c is not None:
          predicate_value = []
          for p in k:
            if p is not None: predicate_value += [p]
          v_constraint.edit(predicate_value_list = predicate_value)
          if fixit:
            error_list += v_constraint.fixConsistency(c)
          else:
            error_list += v_constraint.checkConsistency(c)

      return error_list

    security.declareProtected(Permissions.AccessContentsInformation, 'getAggregatedAmountList')
    def getAggregatedAmountList(self, REQUEST):
      # First, we set initial values for quantity and variation
      # Currently, we only consider discrete variations
      # Continuous variations will be implemented in a future version of ERP5
      transformation = self.aq_parent
      error_list = []
      variation = []
      quantity = self.getQuantity()
      quantity_unit = self.getQuantityUnit()
      efficiency =  self.getEfficiency()
      # XXXXXXXXXXXXXXXXXX maybe this kind of constraints....
      # should be defined in the property sheet and handled
      # automaticaly
      if efficiency is None or efficiency is '' or efficiency == 0.0:
        efficiency = 1.0
      else:
        efficiency = float(efficiency)
      # We look up the resource involved in this transformed resource
      resource = self.getDefaultResourceValue()
      if resource is not None:
        resource_id = resource.getId()
      else:
        resource_id = None
      # and get some attributed we need for the summary
      priced_quantity = resource.getPricedQuantity()
      # XXXXXXXXXXXXXXXXXX maybe this kind of constraints....
      # should be defined in the property sheet and handled
      # automaticaly
      try:
        priced_quantity = float(priced_quantity)
        if priced_quantity == 0.0: priced_quantity = 1.0
      except:
        priced_quantity = 1.0
        error_list += ["Priced Quantity could not be converted for resource %s" % resource_id]
      # source_base_price is the default base price.
      # base_price is defined according to the destination.
      source_base_price = 0.0
      base_price = 0.0
      duration = 0.0
      is_variated_quantity = 0 # The variated quantity is 0 by default
      # Try to update some attributes based on the resource attributes
      if resource.hasDefaultBasePrice():
        base_price = resource.getBasePrice()
        try:
          base_price = float(base_price)
        except:
          base_price = 0.0
          error_list += ["Default base price could not be converted for resource %s" % resource_id]
      if resource.hasSourceBasePrice():
        source_base_price = resource.getSourceBasePrice()
        try:
          source_base_price = float(source_base_price)
        except:
          source_base_price = 0.0
          error_list += ["Source base price could not be converted for resource %s" % resource_id]
      resource_quantity_unit = resource.getDefaultQuantityUnit()
      # This is very dirty and we must do some real unit conversion here XXXXXXX
      if quantity_unit == "Temps/Minute":
        duration = quantity
      # Start filing the value holder with what we have now
      # Maybe we should define a ValueHolder class XXXXXXXXXXXXXXXXXXXXXX
      # First we create a object which id is the id of the transformed_resource
      line_item = TempBase(self.id)
      # and then call edit to update its attributed
      # XXXXXXXXXXXXX bad: this call will call reindex() which is not needed at all
      # How can we create standard objects which are temporary and not indexed ???
      line_item.edit(
          transformation = transformation,
          transformed_resource = self,
          resource = resource,
          transformation_id = transformation.getId(),
          resource_id = resource.getId(),
          resource_relative_url = resource.getRelativeUrl(),
          specialise_id = transformation.getId(),
          specialise_relative_url = transformation.getRelativeUrl(),
          description =  self.getDescription(),
          quantity_unit = quantity_unit,
          duration = duration,
          quantity = quantity,
          efficiency = efficiency,
          base_price = base_price,
          source_base_price = source_base_price,
          total_source_base_price = 0.0,
          total_base_price = 0.0,
          total_duration = 0.0,
          base_price_defined_by = '',
          source_base_price_defined_by = '',
          quantity_defined_by = '',
          variation_defined_by = '',
          resource_quantity_unit = resource_quantity_unit
        )
      # We are going to try to find which variation applies to the current REQUEST
      # First we initialize variation to the default variation value define by
      # the transformed resource
      variation = self.getVariationCategoryList()
      variation_base_category_list = resource.getVariationBaseCategoryList()
      self.portal_categories.setCategoryMembership(line_item,
                              variation_base_category_list, variation, base=1)
      # and update the price with the variation price if necessary
      for resource_variation in self.getValueList(
                          variation_base_category_list, portal_type=self.getPortalVariationTypeList()):
        if resource_variation.hasDefaultBasePrice():
          new_base_price = resource_variation.getBasePrice()
          try:
            new_base_price = float(new_base_price)
          except:
            new_base_price = 0.0
            error_list += ["Default base price could not be converted for resource variation %s"
                % resource_variation.id]
          if new_base_price > 0.0:
            base_price = new_base_price
            line_item.base_price_defined_by = resource_variation.getId()
          new_source_base_price = resource_variation.getSourceBasePrice()
        if resource_variation.hasSourceBasePrice():
          try:
            new_source_base_price = float(new_source_base_price)
          except:
            new_source_base_price = 0.0
            error_list += ["Source base price could not be converted for resource variation %s"
                  % resource_variation.id]
          if new_source_base_price > 0.0:
            source_base_price = new_source_base_price
            line_item.source_base_price_defined_by = resource_variation.getId()
      # Now, let us update variations and quantities
      # We will browse the mapped values and dermine which apply
      for mapped_value in self.objectValues():
        if mapped_value.test(REQUEST):
          # Update attributes defined by the mapped value
          for attribute in mapped_value.getMappedValuePropertyList():
            setattr(line_item, attribute, mapped_value.get(attribute))
            if attribute == 'quantity':
              line_item.quantity_defined_by = mapped_value.getId()
              # If we have to do this, then there is a problem....
              # We'd better have better API for this, like an update function in the mapped_value
              try:
                quantity = float(mapped_value.quantity)
                is_variated_quantity = 1 # The variated quantity is 1
                #                          when the quantity is defined by a variation matrix
              except:
                error_list += ["Quantity defined by %s is not a float" % mapped_value.id]
          # Update categories defined by the mapped value
          base_category_list = mapped_value.getMappedValueBaseCategoryList()
          if len(base_category_list) > 0:
            line_item.variation_defined_by = mapped_value.getId()
            #LOG('In Transformation prevariation',0,str(mapped_value.getCategoryMembershipList(base_category_list, base=1)))
            self.portal_categories.setCategoryMembership(line_item, base_category_list,
                    mapped_value.getCategoryMembershipList(base_category_list, base=1), base=1)
            for resource_variation in mapped_value.getValueList(base_category_list,
                                                                portal_type=self.getPortalVariationTypeList()):
              if resource_variation.hasDefaultBasePrice():
                new_base_price = resource_variation.getBasePrice()
                try:
                  new_base_price = float(new_base_price)
                except:
                  new_base_price = 0.0
                  error_list += \
                      ["Default base price could not be converted for resource variation %s"
                                                            % resource_variation.id]
                if new_base_price > 0.0:
                  base_price = new_base_price
                  line_item.base_price_defined_by = resource_variation.getId()
              if resource_variation.hasSourceBasePrice():
                new_source_base_price = resource_variation.getSourceBasePrice()
                try:
                  new_source_base_price = float(new_source_base_price)
                except:
                  new_source_base_price = 0.0
                  error_list += \
                      ["Source base price could not be converted for resource variation %s"
                                                            % resource_variation.id]
                if new_source_base_price > 0.0:
                  source_base_price = new_source_base_price
                  line_item.source_base_price_defined_by = resource_variation.getId()
      # Convert Quantities
      converted_quantity = resource.convertQuantity(quantity, quantity_unit,
                                                              resource_quantity_unit)
      try:
        converted_quantity = float(converted_quantity)
      except:
        converted_quantity = 0.0
        error_list += ["Quantity could not be converted for resource %s" % resource.id]
      # Convert price to unit price
      unit_base_price = base_price / priced_quantity
      unit_source_base_price = source_base_price / priced_quantity
      variation = self.portal_categories.getCategoryMembershipList(line_item,
                                            variation_base_category_list, base=1)
      #LOG('In Transformation variation',0,str(variation))
      total_base_price = converted_quantity * unit_base_price / efficiency
      total_source_base_price = converted_quantity * unit_source_base_price / efficiency
      # Define variated price
      if is_variated_quantity:
        total_variated_base_price = total_base_price
        total_variated_source_base_price = total_source_base_price
      else:
        total_variated_base_price = 0.0
        total_variated_source_base_price = 0.0
      # Create a nice presentation of the variation
      pretty_variation = ''
      for variation_item in variation:
        pretty_variation += "<br>%s" % str(variation_item)
      # Update the value and calculate total
      line_item.edit(
        converted_quantity = converted_quantity,
        base_price = base_price,
        unit_base_price = unit_base_price,
        total_base_price = total_base_price,
        source_base_price = source_base_price,
        unit_source_base_price = unit_source_base_price,
        total_source_base_price = total_source_base_price,
        variation = variation,
        variation_category_list = variation,
        quantity = quantity,
        pretty_variation = pretty_variation,
        error_list = error_list
      )
      return [line_item], total_base_price, total_source_base_price, \
            total_variated_base_price, total_variated_source_base_price, duration

