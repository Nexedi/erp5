##############################################################################
#
# Copyright (c) 2002 Coramy SAS and Contributors. All Rights Reserved.
#                    Thierry_Faucher <Thierry_Faucher@coramy.com>
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

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Base import TempBase
from Products.ERP5Type.Utils import asList, keepIn, rejectIn

from Products.ERP5.Variated import Variated
from Products.ERP5.ERP5Globals import resource_type_list, variation_type_list

from Domain import Domain

from zLOG import LOG

class Transformation(XMLObject, Domain, Variated):
    """
      Build of material - contains a list of transformed resources

      Use of default_resource... (to define the variation range,
      to ...)


      About ranges:

      getDomainBaseCategoryList -> base categories which allow to select state...

      getDomainRangeBaseCategoryList -> base categories which allow to select state...

      getDomainCategoryList -> bonne idée.... = DomainValue...
                               base category which defines the state
                               (and other things)

      getDomainRangeCategoryList -> bonne idée.... = DomainValue...

    """

    meta_type = 'ERP5 Transformation'
    portal_type = 'Transformation'
    add_permission = Permissions.AddERP5Content
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.VariationRange
                      , PropertySheet.Domain
                      , PropertySheet.Transformation
                      )

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
une gamme..."""
         , 'icon'           : 'transformation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addTransformation'
         , 'immediate_view' : 'transformation_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('Transformed Resource',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'transformation_view'
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
          , 'action'        : 'transformation_print'
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

    security.declareProtected(Permissions.AccessContentsInformation,
                                          'getVariationRangeBaseCategoryList')
    def getVariationRangeBaseCategoryList(self):
        """
          Returns possible variation base_category ids of the
          default resource of this transformation
        """
        resource = self.getDefaultResourceValue()
        if resource is not None:
          result = resource.getVariationBaseCategoryList()
        else:
          result = self.getBaseCategoryIds()
        return result

    security.declareProtected(Permissions.AccessContentsInformation,
                            'getTransformationVariationRangeCategoryList')
    def getTransformationVariationRangeCategoryList(self):
        """
          Possible categories (ie. of the default resource)
        """
        return self.getResourceValue().getVariationCategoryList(base_category_list=
                              self.getTransformationVariationBaseCategoryList())

    security.declareProtected(Permissions.AccessContentsInformation,
                            'getTransformationVariationCategoryList')
    def getTransformationVariationCategoryList(self):
        """
          Possible categories (ie. of the default resource)
        """
        return self.getVariationCategoryList(base_category_list=
                              self.getTransformationVariationBaseCategoryList())

    security.declareProtected(Permissions.AccessContentsInformation,
                            'getTransformationVariationRangeBaseCategoryList')
    def getTransformationVariationRangeBaseCategoryList(self):
        """
          Returns possible variation base_category ids of the
          default resource which can be used a variation axis
          in the transformation (ie. all ids of
          getVariationRangeBaseCategoryList except ids which
          are used as a transformation state as defined in
          domain_base_category)
        """
        result = ['',] + list(self.getVariationRangeBaseCategoryList())
        forbidden_id = self.getDomainBaseCategoryList()
        forbidden_id = asList(forbidden_id) # This will soon be useless
        return rejectIn(result, forbidden_id)

    security.declareProtected(Permissions.AccessContentsInformation,
                                      'getVariationRangeBaseCategoryItemList')
    def getVariationRangeBaseCategoryItemList(self):
        """
          Returns possible variations of the resource
          as a list of tuples (id, title). This is mostly
          useful in ERP5Form instances to generate selection
          menus.
        """
        return self.portal_categories.getItemList(self.getVariationRangeBaseCategoryList())

    security.declareProtected(Permissions.AccessContentsInformation,
                          'getTransformationVariationRangeBaseCategoryItemList')
    def getTransformationVariationRangeBaseCategoryItemList(self):
        """
          Returns possible variations of the transformation
          as a list of tuples (id, title). This is mostly
          useful in ERP5Form instances to generate selection
          menus.
        """
        return self.portal_categories.getItemList(
                    self.getTransformationVariationRangeBaseCategoryList())

    security.declareProtected(Permissions.AccessContentsInformation,
                                        'getVariationRangeCategoryItemList')
    def getVariationRangeCategoryItemList(self, base_category_list = ()):
        """
          Returns possible variation category values for the
          transformation according to the default resource.
          Possible category values is provided as a list of
          tuples (id, title). This is mostly
          useful in ERP5Form instances to generate selection
          menus.
        """
        if base_category_list is ():
          base_category_list = self.getVariationBaseCategoryList()
        try:
          result = self.getDefaultResourceValue(
                    ).getVariationRangeCategoryItemList(base_category_list)
        except:
          result = self.portal_categories.getCategoryChildItemList(base_category_list,
                                               base=1)
        return result

    # Aliases to simplify access to range information for TransformedResources
    security.declareProtected(Permissions.AccessContentsInformation,
                            'getTransformationVariationBaseCategoryList')
    def getTransformationVariationBaseCategoryList(self):
      """
        Returns a list of base_category ids for this tranformation
      """
      return self.getVariationBaseCategoryList()

    security.declareProtected(Permissions.AccessContentsInformation,
                            'getTransformationVariationBaseCategoryItemList')
    def getTransformationVariationBaseCategoryItemList(self):
      """
        Returns a list of base_category tuples for this tranformation
      """
      return self.portal_categories.getItemList(self.getVariationBaseCategoryList())

    # This is the main method to do any BOM related calculation
    security.declareProtected(Permissions.AccessContentsInformation, 'getAggregatedAmountList')
    def getAggregatedAmountList(self, context=None, REQUEST=None, **kw):
      """
        getAggregatedSummary returns a list of dictionaries which can be used
        either to do some calculation (ex. price, BOM) or to display
        a detailed view of a transformation.

        We must update this API to be able to manage context
      """
      # LOG('getAggregatedAmountList',0,str((context, REQUEST, kw)))
      REQUEST = self.asContext(context=context, REQUEST=REQUEST, **kw)
      # First we need to get the list of transformations which this transformation depends on
      # At this moment, we only consider 1 dependency
      transformation_list = [self] + self.getSpecialiseValueList()
      # We consider that the specific parameters to take into account
      # are acquired through the REQUEST parameter
      # The REQUEST can either be a Zope REQUEST or a dictionnary provided by the use
      if REQUEST is None:
        # At this moment XXXXXXXXXXXXXXXXXXXXXXXX
        # we initialize the request to a default value in order
        # to make sure we have something to test MappedValues on
        REQUEST = {'categories': ('taille/enfant/08 ans','coloris/modele/701C402/2')}
      # We define some initial values
      # result holds a list of dictionaries
      # price holds a list of dictionaries
      summary_list = []
      grand_total_variated_source_base_price = 0.0
      grand_total_source_base_price = 0.0
      grand_total_base_price = 0.0
      grand_total_variated_base_price = 0.0
      grand_total_variated_source_base_price = 0.0
      grand_total_duration = 0.0

      # Browse all involved transformations and create one line per line of transformation
      # Currently, we do not consider abstractions, we just add whatever we find in all
      # transformations
      for transformation in transformation_list:
        # Browse each transformed resource of the current transformation
        for transformed_resource in transformation.objectValues():
          # First, we set initial values for quantity and variation
          # Currently, we only consider discrete variations
          # Continuous variations will be implemented in a future version of ERP5
          error_list = []
          variation = []
          quantity = transformed_resource.getQuantity()
          quantity_unit = transformed_resource.getQuantityUnit()
          efficiency =  transformed_resource.getEfficiency()
          # XXXXXXXXXXXXXXXXXX maybe this kind of constraints....
          # should be defined in the property sheet and handled
          # automaticaly
          if efficiency is None or efficiency is '' or efficiency == 0.0:
            efficiency = 1.0
          else:
            efficiency = float(efficiency)
          # We look up the resource involved in this transformed resource
          resource = transformed_resource.getDefaultResourceValue()
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
          line_item = TempBase(transformed_resource.id)
          # and then call edit to update its attributed
          # XXXXXXXXXXXXX bad: this call will call reindex() which is not needed at all
          # How can we create standard objects which are temporary and not indexed ???
          line_item.edit(
              transformation = transformation,
              transformed_resource = transformed_resource,
              resource = resource,
              transformation_id = transformation.getId(),
              resource_id = resource.getId(),
              resource_relative_url = resource.getRelativeUrl(),
              specialise_id = transformation.getId(),
              specialise_relative_url = transformation.getRelativeUrl(),
              description =  transformed_resource.getDescription(),
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
          variation = transformed_resource.getVariationCategoryList()
          variation_base_category_list = resource.getVariationBaseCategoryList()
          self.portal_categories.setCategoryMembership(line_item,
                                  variation_base_category_list, variation, base=1)
          # and update the price with the variation price if necessary
          for resource_variation in transformed_resource.getValueList(
                               variation_base_category_list, portal_type=variation_type_list):
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
          for mapped_value in transformed_resource.objectValues():
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
                                                                     portal_type=variation_type_list):
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
          # Add the line_item to the
          summary_list += [line_item]
          grand_total_base_price += total_base_price
          grand_total_source_base_price += total_source_base_price
          grand_total_variated_base_price += total_variated_base_price
          grand_total_variated_source_base_price += total_variated_source_base_price
          grand_total_duration += duration

      #LOG("Transformation Agg summary",0,
      #        str(map(lambda o: (o.resource_id, o.quantity_defined_by), summary_list)))

      # Return values as a tuple
      return map(lambda x: x.__dict__, summary_list) , grand_total_base_price, \
         grand_total_source_base_price, grand_total_duration, \
         grand_total_variated_base_price, grand_total_variated_source_base_price

    # UPDATED BY JPS

    # XXX This should not be there, but in Document/TransformedResource.py or something like
    # this, but actually this does not work, we should find why.
    security.declareProtected(Permissions.ModifyPortalContent, '_setVariationBaseCategoryList')
    def _setVariationBaseCategoryList(self, new_base_category_list):
      """
        We override the default behaviour generated by Utils.py in order
        to update all TransformedResource contained in this transformation
      """
      # Get the list of previous base_category that have been removed or kept
      removed_base_category = []
      kept_base_category = []
      for cat in self.getVariationBaseCategoryList():
        if cat in new_base_category_list:
          kept_base_category += [cat]
        else:
          removed_base_category += [cat]

      # Update variation_base_category_list
      self.variation_base_category_list = new_base_category_list

      # Make sure there is no reference to categories
      # of removed_base_category
      # in categories
      if len(removed_base_category) > 0:
        self._setCategoryMembership(removed_base_category, [], base=1)

      # Filter all fields which are based on base_category
      if self.getVariationBaseCategoryLine() not in new_base_category_list:
        self._setVariationBaseCategoryLine(None)
      if self.getVariationBaseCategoryColumn() not in new_base_category_list:
        self._setVariationBaseCategoryColumn(None)
      self._setVariationBaseCategoryTabList(keepIn(self.getVariationBaseCategoryTabList(),
                                                      new_base_category_list))

      # Make sure that all sub-objects use a valid range
      # We simply call range functions on each object to force
      # range update in XMLMatrix
      for o in self.objectValues():
        if hasattr(o,'v_variation_base_category_list'):
          o.setVVariationBaseCategoryList(keepIn(o.getVVariationBaseCategoryList(),
                                                              new_base_category_list))
        if hasattr(o,'q_variation_base_category_list'):
          o.setQVariationBaseCategoryList(keepIn(o.getQVariationBaseCategoryList(),
                                                              new_base_category_list))
