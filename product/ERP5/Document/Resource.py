# -*- coding: utf-8 -*-
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

from math import log
from warnings import warn

from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Base import Base
from Products.ERP5Type.UnrestrictedMethod import unrestricted_apply

from Products.ERP5Type.Utils import cartesianProduct
from Products.ERP5.mixin.variated import VariatedMixin
from Products.CMFCategory.Renderer import Renderer

from zLOG import LOG, WARNING
import six

class Resource(XMLObject, XMLMatrix, VariatedMixin):
    """
      A Resource
    """

    meta_type = 'ERP5 Resource'
    portal_type = 'Resource'
    add_permission = Permissions.AddPortalContent

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.DublinCore
                      , PropertySheet.Price
                      , PropertySheet.Resource
                      , PropertySheet.Reference
                      , PropertySheet.Comment
                      , PropertySheet.FlowCapacity
                      , PropertySheet.DefaultSupply
                      , PropertySheet.Aggregated
                      )

    _default_edit_order = XMLObject._default_edit_order + VariatedMixin._default_edit_order

    # Is it OK now ?
    # The same method is at about 3 different places
    # Some genericity is needed
    security.declareProtected(Permissions.AccessContentsInformation,
                                           'getVariationRangeCategoryItemList')
    def getVariationRangeCategoryItemList(self, base_category_list=(), base=1,
                                          root=1, display_id='title',
                                          display_base_category=1,
                                          current_category=None,
                                          omit_individual_variation=0, **kw):
        """
          Returns possible variations

          resource.getVariationRangeCategoryItemList
            => [(display, value)]

      ## Variation API (exemple) ##
        Base categories defined:
          - colour
          - morphology
          - size
        Categories defined:
          - colour/blue
          - colour/red
          - size/Man
          - size/Woman
        Resource 'resource' created with variation_base_category_list:
            (colour, morphology, size)

        resource.getVariationRangeCategoryList
        variation   | individual variation | result
        ____________________________________________________________________________________
                    |                      | (colour/blue, colour/red, size/Man, size/Woman)
        size/Man    |                      | (colour/blue, colour/red, size/Man, size/Woman)
        colour/blue |                      | (colour/blue, colour/red, size/Man, size/Woman)
                    |  colour/1            | (colour/1, size/Man, size/Woman)
                    |  morphology/2        | (colour/blue, colour/red, size/Man, size/Woman, morphology/2)
        """
        result = []
        if base_category_list == ():
          base_category_list = self.getVariationBaseCategoryList(
              omit_individual_variation=omit_individual_variation)
        elif isinstance(base_category_list, str):
          base_category_list = (base_category_list,)

        individual_variation_list = self.contentValues(
            portal_type=self.getPortalVariationTypeList(),
            sort_on=[('title','ascending')])
        individual_variation_list = [x.getObject() for x in
            individual_variation_list]
        other_base_category_set = set(base_category_list)

        if not omit_individual_variation:
          for variation in individual_variation_list:
            for base_category in variation.getVariationBaseCategoryList():
              if base_category_list == ()\
                  or base_category in base_category_list:
                other_base_category_set.discard(base_category)
                # XXX now, call Renderer a lot of time.
                # Better implementation needed
                result.extend(Renderer(
                    base_category=base_category,
                    display_base_category=display_base_category,
                    display_none_category=0, base=base,
                    current_category=current_category,
                    display_id=display_id).render([variation]))

        # Get category variation
        if other_base_category_set:
          result.extend(super(Resource, self).getVariationRangeCategoryItemList(
              base_category_list=list(other_base_category_set),
              base=base, display_base_category=display_base_category, **kw))
        # Return result
        return result

    security.declareProtected(Permissions.AccessContentsInformation,
                                           'getVariationCategoryItemList')
    def getVariationCategoryItemList(self, base_category_list=(),
                                     omit_optional_variation=0,
                                     omit_individual_variation=1, base=1,
                                     current_category=None,
                                     display_base_category=1,
                                     display_id='title', **kw):
      """
        Returns variations of the resource.
        If omit_individual_variation==1, does not return individual
        variation.
        Else, returns them.
        Display is on left.
            => [(display, value)]

        *old parameters: base=1, current_category=None,
                         display_id='title' (default value title)
      """
      base_category_list = base_category_list or \
          self.getVariationBaseCategoryList()

      individual_bc_list = self.getIndividualVariationBaseCategoryList()
      other_bc_list = [x for x in base_category_list
          if not x in individual_bc_list]

      if omit_optional_variation:
        optional_bc_list = self.getOptionalVariationBaseCategoryList()\
            or self.getPortalOptionBaseCategoryList()
        if optional_bc_list:
          other_bc_list = [x for x in other_bc_list
              if not x in optional_bc_list]


      result = super(Resource, self).getVariationCategoryItemList(
                            base_category_list=other_bc_list,
                            display_base_category=display_base_category,
                            display_id=display_id, base=base, **kw)

      if not omit_individual_variation:
        individual_variation_list = self.contentValues(
            portal_type=self.getPortalVariationTypeList())
        individual_variation_list = [x.getObject() for x in
            individual_variation_list]

        for variation in individual_variation_list:
          for base_category in variation.getVariationBaseCategoryList():
            # backwards compatbility: if individual_bc_list is empty, allow
            # all individual variation base categories.
            if (base_category_list == ()
                or base_category in base_category_list)\
               and (not len(individual_bc_list)
                    or base_category in individual_bc_list):
              # XXX append object, relative_url ?
              # XXX now, call Renderer a lot of time.
              # Better implementation needed
              result.extend(Renderer(
                  base_category=base_category,
                  display_base_category=display_base_category,
                  display_none_category=0, base=base,
                  current_category=current_category, display_id=display_id,
                  **kw).render([variation]))
      return result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getVariationCategoryList')
    def getVariationCategoryList(self, default=[], base_category_list=(),
                                 omit_individual_variation=1, **kw):
      """
        Returns variations of the resource.
        If omit_individual_variation==1, does not return individual
        variation.
        Else, returns them.

        ## Variation API (exemple) ##
        Base categories defined:
          - colour
          - morphology
          - size
        Categories defined:
          - colour/blue
          - colour/red
          - size/Man
          - size/Woman
        Resource 'resource' created with variation_base_category_list:
            (colour, morphology, size)

        resource.getVariationCategoryList
        variation   | individual variation | result
        _____________________________________________________
                    |                      | ()
        size/Man    |                      | (size/Man, )
        colour/blue |                      | (colour/blue, )
                    |  colour/1            | (colour/1, )
                    |  morphology/2        | (morphology/2, )
      """
      vcil = self.getVariationCategoryItemList(
                    base_category_list=base_category_list,
                    omit_individual_variation=omit_individual_variation,**kw)
      return [x[1] for x in vcil]

# This patch is temporary and allows to circumvent name conflict in ZSQLCatalog process for Coramy
    security.declareProtected(Permissions.AccessContentsInformation,
                                              'getDefaultDestinationAmountBis')
    def getDefaultDestinationAmountBis(self, unit=None, variation=None, REQUEST=None):
      try:
        return self.getDestinationReference()
      except AttributeError:
        return None

# This patch is temporary and allows to circumvent name conflict in ZSQLCatalog process for Coramy
    security.declareProtected(Permissions.AccessContentsInformation,
                                              'getDefaultSourceAmountBis')
    def getDefaultSourceAmountBis(self, unit=None, variation=None, REQUEST=None):
      try:
        return self.getSourceReference()
      except AttributeError:
        return None


    # This patch allows variations to find a resource
    security.declareProtected(Permissions.AccessContentsInformation,
                                              'getDefaultResourceValue')
    def getDefaultResourceValue(self):
      return self


    security.declareProtected(Permissions.AccessContentsInformation,
                              'getDefaultTransformationValue')
    def getDefaultTransformationValue(self, context=None):
      """
      If context is None, returns the first available transformation that
      use self as a Resource. If there are several candidates, return the
      Transformation that has the latest version.

      Otherwise, context is used as a Predicate to match Transformations.
      If the search returns several candidates due to a relaxed Predicate,
      the first item is returned arbitrarily.
      """
      method = self._getTypeBasedMethod('getDefaultTransformationValue')
      if method is not None:
        return method(context)

      if context is None:
        transformation_list = self.portal_catalog(
            portal_type=self.getPortalObject().getPortalTransformationTypeList(),
            default_resource_uid=self.getUid(),
            sort_on=[('version', 'descending')],
            limit=1
        )
        if len(transformation_list) > 0:
          return transformation_list[0].getObject()
        return None

      method = context._getTypeBasedMethod('getDefaultTransformationValue')
      if method is not None:
        return method(context)

      transformation_list = self.portal_domains.searchPredicateList(context,
                                portal_type=self.getPortalObject().getPortalTransformationTypeList(),
                                limit=1)

      if len(transformation_list) > 0:
        return transformation_list[0]

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getDefaultConversionTransformationValue')
    def getDefaultConversionTransformationValue(self):
      """
      Return a Transformation object that should be used to compute
      converted inventories.
      This should be overriden in subclasses, or in the Type Based Method
      of the same name.

      The method can return an existing Transformation object, or a
      temporary Transformation: one might want for example, for conversion
      purposes, to ignore some (packaging, wrapping, labelling) components
      in conversion reports. This method can be used to create a simplified
      transformation from a complex real-world transformation.
      """
      method = self._getTypeBasedMethod(\
                        'getDefaultConversionTransformationValue')
      if method is not None:
        return method()

      return self.getDefaultTransformationValue(context=None)


    security.declareProtected(Permissions.AccessContentsInformation,
                           'getTransformationVariationCategoryCartesianProduct')
    def getTransformationVariationCategoryCartesianProduct(self):
      """
      Defines which variations are of interest when indexing
      Transformations related to this resource.

      By default, this returns the cartesian Product of all
      possible categories using all variation axes.

      Override this to reduce the number of indexed rows, and/or
      if some variation axes do not matter when displaying
      Transformed inventories.

      XXX This should use variated_range mixin when available
      """
      method = self._getTypeBasedMethod(\
          'getTransformationVariationCategoryCartesianProduct')
      if method is not None:
        return method()

      variation_list_list = []
      for base_variation in self.getVariationBaseCategoryList():
        variation_list = self.getVariationCategoryList( \
            base_category_list=(base_variation,))
        if len(variation_list) > 0:
          variation_list_list.append(variation_list)

      return cartesianProduct(variation_list_list)


    ####################################################
    # Stock Management
    ####################################################
    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventory')
    def getInventory(self, **kw):
      """
      Returns inventory
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCurrentInventory')
    def getCurrentInventory(self, **kw):
      """
      Returns current inventory
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getCurrentInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAvailableInventory')
    def getAvailableInventory(self, **kw):
      """
      Returns available inventory
      (current inventory - deliverable)
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getAvailableInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getFutureInventory')
    def getFutureInventory(self, **kw):
      """
      Returns inventory at infinite
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getFutureInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventoryList')
    def getInventoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCurrentInventoryList')
    def getCurrentInventoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getCurrentInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAvailableInventoryList')
    def getAvailableInventoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getAvailableInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getFutureInventoryList')
    def getFutureInventoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getFutureInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventoryStat')
    def getInventoryStat(self, **kw):
      """
      Returns statistics of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getInventoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCurrentInventoryStat')
    def getCurrentInventoryStat(self, **kw):
      """
      Returns statistics of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getCurrentInventoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAvailableInventoryStat')
    def getAvailableInventoryStat(self, **kw):
      """
      Returns statistics of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getAvailableInventoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getFutureInventoryStat')
    def getFutureInventoryStat(self, **kw):
      """
      Returns statistics of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getFutureInventoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventoryChart')
    def getInventoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getInventoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCurrentInventoryChart')
    def getCurrentInventoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getCurrentInventoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getFutureInventoryChart')
    def getFutureInventoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getFutureInventoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventoryHistoryList')
    def getInventoryHistoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getInventoryHistoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventoryHistoryChart')
    def getInventoryHistoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getInventoryHistoryChart(**kw)

    # XXX FIXME
    # Method getCurrentMovementHistoryList,
    # getAvailableMovementHistoryList, getFutureMovementHistoryList
    # can be added
    security.declareProtected(Permissions.AccessContentsInformation,
                              'getMovementHistoryList')
    def getMovementHistoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getMovementHistoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getMovementHistoryStat')
    def getMovementHistoryStat(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getMovementHistoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getNextNegativeInventoryDate')
    def getNextNegativeInventoryDate(self, **kw):
      """
      Returns next date where the inventory will be negative
      """
      return self.getNextAlertInventoryDate(
                  reference_quantity=0, **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getNextAlertInventoryDate')
    def getNextAlertInventoryDate(self, reference_quantity=0, **kw):
      """
      Returns next date where the inventory will be below reference
      quantity
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getNextAlertInventoryDate(
                          reference_quantity=reference_quantity, **kw)

    # Asset Price API
    security.declareProtected(Permissions.AccessContentsInformation,
        'getInventoryAssetPrice')
    def getInventoryAssetPrice(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getInventoryAssetPrice(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
        'getCurrentInventoryAssetPrice')
    def getCurrentInventoryAssetPrice(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getCurrentInventoryAssetPrice(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
        'getAvailableInventoryAssetPrice')
    def getAvailableInventoryAssetPrice(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getAvailableInventoryAssetPrice(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
        'getFutureInventoryAssetPrice')
    def getFutureInventoryAssetPrice(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = self.getPortalObject().portal_simulation
      return portal_simulation.getFutureInventoryAssetPrice(**kw)


    # Industrial price API
    security.declareProtected(Permissions.AccessContentsInformation,
        'getIndustrialPrice')
    def getIndustrialPrice(self, context=None, REQUEST=None, **kw):
      """
        Returns industrial price
      """
      context = self.asContext(context=context, REQUEST=REQUEST, **kw)
      result = self._getIndustrialPrice(context)
      return result

    def _getIndustrialPrice(self, context):
      # Default value is None
      return None

    def _pricingSortKeyMethod(self, a):
      # Simple method : the one that defines a destination section wins
      if a.getDestinationSection():
        return -1 # a defines a destination section and wins
      return 1 # a defines no destination section and loses

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getPriceParameterDict')
    def getPriceParameterDict(self, context=None, REQUEST=None,
                              supply_path_type=None, **kw):
      """
      Get all pricing parameters from Predicate.
      """
      # Search all categories context
      if context is None:
        new_category_list = []
      else:
        new_category_list = context.getCategoryList()
      #XXX This should be 'category_list' instead of 'categories' to respect
      # the naming convention. Must take care of side effects when fixing
      new_category_list += kw.pop('categories', ())
      resource_category = 'resource/' + self.getRelativeUrl()
      if not resource_category in new_category_list:
        new_category_list.append(resource_category)
      # Generate the predicate mapped value
      # to get some price values.
      portal = self.getPortalObject()
      if supply_path_type is None:
        portal_type_list = kw.pop('portal_type',
                                  portal.getPortalSupplyPathTypeList())
      elif isinstance(supply_path_type, (list, tuple)):
        portal_type_list = supply_path_type
      else:
        portal_type_list = (supply_path_type,)

      sort_key_method = kw.pop('sort_key_method', None)
      if sort_key_method is None:
        sort_method = kw.pop('sort_method', None)
        if sort_method is None:
          # use default sort_key_method if neither sort_key_method nor
          # sort_method is specified.
          sort_key_method = self._pricingSortKeyMethod
      else:
        # if sort_key_method is specified, we don't need sort_method.
        sort_method = None
      # Generate the fake context
      tmp_context = self.asContext(context=context,
                                   categories=new_category_list,
                                   REQUEST=REQUEST, **kw)
      # XXX When called for a generated amount, base_application may point
      #     to nonexistant base_amount (e.g. "base_amount/produced_quantity" for
      #     transformations), which would make domain tool return nothing.
      #     Following hack cleans up a category we don't want to test anyway.
      #     Also, do not use '_setBaseApplication' to bypass interactions.
      portal.portal_categories._setCategoryMembership(tmp_context,
        ('base_application',), ())
      mapped_value = portal.portal_domains.generateMultivaluedMappedValue(
                                             tmp_context,
                                             portal_type=portal_type_list,
                                             has_cell_content=0,
                                             sort_key_method=sort_key_method,
                                             sort_method=sort_method, **kw)
      # Get price parameters
      price_parameter_dict = {
        'base_price': None,
        'additional_price': [],
        'surcharge_ratio': [],
        'discount_ratio': [],
        'exclusive_discount_ratio': None,
        'variable_additional_price': [],
        'non_discountable_additional_price': [],
        'priced_quantity': None,
        'base_unit_price': None,
        'slice_base_price': None,
        'slice_quantity_range': None,
      }
      if mapped_value is None:
        return price_parameter_dict
      for mapped_value_property in mapped_value.getMappedValuePropertyList():
        value = getattr(mapped_value, mapped_value_property)
        try:
          price_parameter_dict[mapped_value_property].extend(value)
        except AttributeError:
          price_parameter_dict[mapped_value_property] = max(value) \
            if mapped_value_property == 'exclusive_discount_ratio' \
            else value[0]
        except KeyError:
          price_parameter_dict[mapped_value_property] = value
      return price_parameter_dict

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getPriceCalculationOperandDict')
    def getPriceCalculationOperandDict(self, default=None, context=None,
            REQUEST=None, **kw):
      """Return a dictionary which contains operands for price calculation.
      Consult the doc string in Movement.getPriceCalculationOperandDict
      for more details.
      """
      kw.update(default=default, movement=context, REQUEST=REQUEST)
      return unrestricted_apply(
        self._getTypeBasedMethod('getPriceCalculationOperandDict'), kw=kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getPrice')
    def getPrice(self, default=None, context=None, REQUEST=None, **kw):
      """
      Return the unit price of a resource in a specific context.
      """
      # see Movement.getPrice
      if isinstance(default, Base) and context is None:
        msg = 'getPrice first argument is supposed to be the default value'\
              ' accessor, the context should be passed as with the context='\
              ' keyword argument'
        warn(msg, DeprecationWarning)
        LOG('ERP5', WARNING, msg)
        context = default
        default = None

      operand_dict = self.getPriceCalculationOperandDict(default=default,
              context=context, REQUEST=REQUEST, **kw)
      if operand_dict is not None:
        return operand_dict['price']
      return default

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getQuantityPrecision')
    def getQuantityPrecision(self):
      """Return the floating point precision of a quantity.
      """
      try:
        return int(round(- log(self.getBaseUnitQuantity(), 10),0))
      except TypeError:
        return 0
      return 0


    def _getConversionRatio(self, quantity_unit, variation_list):
      """
      Converts a quantity unit into a ratio in respect to the resource's
      management unit, for the specified variation.
      A quantity can be multiplied by the returned value in order to convert it
      in the management unit.

      'variation_list' parameter may be deprecated:
      cf Measure.getConvertedQuantity
      """
      management_unit = self.getDefaultQuantityUnit()
      if management_unit == quantity_unit:
        return 1.0
      traverse = self.portal_categories['quantity_unit'].unrestrictedTraverse
      quantity = self.getQuantityUnitDefinitionRatio(traverse(quantity_unit))
      if quantity_unit.split('/', 1)[0] != management_unit.split('/', 1)[0]:
        measure = self.getDefaultMeasure(quantity_unit)
        quantity /= measure.getConvertedQuantity(variation_list)
      else:
        quantity /= self.getQuantityUnitDefinitionRatio(traverse(management_unit))
      return quantity

    # Unit conversion
    security.declareProtected(Permissions.AccessContentsInformation, 'convertQuantity')
    def convertQuantity(self, quantity, from_unit, to_unit, variation_list=(),
      transformed_resource=None, transformed_variation_list=()):
      # 'variation_list' parameter may be deprecated:
      # cf Measure.getConvertedQuantity
      try:
        result = quantity * self._getConversionRatio(from_unit, variation_list)\
                        / self._getConversionRatio(to_unit, variation_list)
      except (ArithmeticError, AttributeError, LookupError, TypeError) as error:
        # For compatibility, we only log the error and return None.
        # No exception for the moment.
        LOG('Resource.convertQuantity', WARNING,
            'could not convert quantity for %s (%r)'
            % (self.getRelativeUrl(), error))
        return None

      if transformed_resource is not None:
        variation_text = '\n'.join(variation_list)
        transformed_variation_text = '\n'.join(transformed_variation_list)
        transformed_uid = transformed_resource.getUid()

        query = self.zGetTransformedResourceConversionRatio(\
                    ui = self.getUid(),
                    variation_text = variation_text,
                    transformed_uid = transformed_uid,
                    transformed_variation_text=transformed_variation_text,
                  )
        if len(query) == 0:
          LOG('Resource.convertQuantity', WARNING,
              'could not get Transformation associated to %s -> %s'
              % (transformed_resource.getRelativeUrl(),
                self.getRelativeUrl()))
          return None
        result *= query[0].quantity

      return result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getMeasureList')
    def getMeasureList(self):
      """
      Gets the list of Measure objects describing this resource.
      """
      return self.objectValues(portal_type='Measure')

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getDefaultMeasure')
    def getDefaultMeasure(self, quantity_unit=None):
      """
      Returns the measure object associated to quantity_unit.
      If no quantity_unit is specified, the quantity_unit of the resource is used.
      None is returned if the number of found measures differs from 1.
      """
      if quantity_unit is None:
        quantity_unit = self.getQuantityUnit()
      if quantity_unit:
        top = lambda relative_url: relative_url.split('/', 1)[0]

        quantity = top(quantity_unit)
        generic = []
        default = []
        for measure in self.getMeasureList():
          metric_type = measure.getMetricType()
          if metric_type and quantity == top(metric_type) and \
             measure.getDefaultMetricType():
            default.append(measure)
          if quantity == metric_type:
            generic.append(measure)
        result = default or generic
        if len(result) == 1:
          return result[0]

    def _getQuantityUnitDefinitionDict(self):
      """
      Returns a dictionary representing the Unit Definitions that hold
      for the current resource.
        Keys: quantity_unit categories uids.
        Values: tuple (unit_definition_uid, quantity)
          * unit_definition_uid can be None if the quantity_unit is defined
            as a standard_quantity_unit (no Unit Conversion Definition defines
            it, its definition comes from a Unit Conversion Group)
          * quantity is a float, an amount, expressed in the
            standard_quantity_unit for the base category of the quantity_unit.
            For example, if mass/g is the global standard quantity_unit, all
            definitions for mass/* will be expressed in grams.
      """
      global_definition_dict = self.\
          QuantityUnitConversionModule_getUniversalDefinitionDict()

      # _getUniversalDefinitionDict is a cached function. Copy the object to
      # avoid modifying it
      result = global_definition_dict.copy()
      for definition_group in self.objectValues(portal_type= \
          'Quantity Unit Conversion Group'):
        if definition_group.getValidationState() != "validated":
          continue

        standard_quantity_unit_value = definition_group.getQuantityUnitValue()
        if standard_quantity_unit_value is None:
          continue

        uid = standard_quantity_unit_value.getUid()
        try:
          reference_ratio = global_definition_dict[uid][1]
        except KeyError:
          LOG("Resource", WARNING,
              "could not find a global Unit Definition for '%s' while " \
              "indexing local Definition Group '%s'" % \
                  (standard_quantity_unit_value.getRelativeUrl(),
                   definition_group.getRelativeUrl()))
          continue

        for definition in definition_group.objectValues(portal_type= \
            'Quantity Unit Conversion Definition'):
          if definition.getValidationState() != "validated":
            continue

          unit_uid = definition.getQuantityUnitUid()
          if unit_uid is None:
            continue

          definition_ratio = definition.getConversionRatio()
          if not definition_ratio:
            continue

          result[unit_uid] = (definition.getUid(),
                              definition_ratio*reference_ratio)

      return result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getQuantityUnitConversionDefinitionRowList')
    def getQuantityUnitConversionDefinitionRowList(self):
      """
      Returns a list rows to insert in the quantity_unit_conversion table.
      Used by z_catalog_quantity_unit_conversion_list.
      """
      # XXX If one wanted to add variation-specific Unit Conversion Definitions
      #  he could use an approach very similar to the one used for Measure.
      #  Just add a variation VARCHAR column in quantity_unit_conversion table
      #  (defaulting as "^"). The column would contain the REGEX describing the
      #  variation, exactly as Measure.
      #  Resource_zGetInventoryList would then need expansion to match the
      #  product variation vs the quantity_unit_conversion REGEX.

      uid = self.getUid()
      row_list = []
      for unit_uid, value in six.iteritems(self._getQuantityUnitDefinitionDict()):
        definition_uid, quantity = value
        row_list.append(dict(uid=definition_uid,
                             resource_uid=uid,
                             quantity_unit_uid=unit_uid,
                             quantity=quantity))

      return row_list

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getMeasureRowList')
    def getMeasureRowList(self):
      """
      Returns a list rows to insert in the measure table.
      Used by z_catalog_measure_list.
      """
      quantity_unit_value = self.getQuantityUnitValue()
      if quantity_unit_value is None:
        return ()

      quantity_unit_definition_dict = self._getQuantityUnitDefinitionDict()

      metric_type_map = {} # duplicate metric_type are not valid

      for measure in self.getMeasureList():
        metric_type = measure.getMetricType()
        if metric_type in metric_type_map:
          metric_type_map[metric_type] = None
        else:
          metric_type_map[metric_type] = measure

      insert_list = []
      for measure in six.itervalues(metric_type_map):
        if measure is not None:
          insert_list += measure.asCatalogRowList(quantity_unit_definition_dict)

      quantity_unit = quantity_unit_value.getCategoryRelativeUrl()
      if self.getDefaultMeasure(quantity_unit) is None:
          metric_type = quantity_unit.split('/', 1)[0]
          if metric_type and metric_type not in metric_type_map:
            # At this point, we know there is no default measure and we must add
            # a row for the management unit, with the resource's uid as uid, and
            # a generic metric_type.
            quantity_unit_uid = quantity_unit_value.getUid()
            try:
              quantity = quantity_unit_definition_dict[quantity_unit_uid][1]
            except KeyError:
              LOG("Resource", WARNING,
                  "could not find an Unit Definition for '%s' while " \
                  "indexing Resource '%s'" % \
                     (quantity_unit_value.getRelativeUrl(),
                      self.getRelativeUrl()))
              quantity = None

            metric_type_uid = self.getPortalObject().portal_categories \
                                  .getCategoryUid(metric_type, 'metric_type')
            if quantity and metric_type_uid:
              uid = self.getUid()
              insert_list.append(dict(uid=uid, resource_uid=uid, variation='^',
                                  metric_type_uid=metric_type_uid,
                                  quantity=float(quantity)))

      return insert_list

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getQuantityUnitDefinitionRatio')
    def getQuantityUnitDefinitionRatio(self, quantity_unit_value):
      """
      get the ratio used to define the quantity unit quantity_unit_value.
      If the Resource has a local Quantity Unit conversion Definition,
      return the ratio from that Definition.
      If not, fetch a Definition in the Global Module.
      """
      portal = self.getPortalObject()
      quantity_unit_uid = quantity_unit_value.getUid()

      deprecated_quantity = quantity_unit_value.getProperty('quantity')
      if deprecated_quantity is not None:
        warn('quantity field of quantity_unit categories is deprecated.' \
           ' Please use Quantity Unit Conversion Definitions instead and' \
           ' reset the value of this field.', DeprecationWarning)

        return float(deprecated_quantity)

      query = self.ResourceModule_zGetQuantityUnitDefinitionRatio(
                            quantity_unit_uid=quantity_unit_uid,
                            resource_uid=self.getUid())
      try:
        return query[0].quantity
      except IndexError:
        raise IndexError('Can not find the Quantity Unit Conversion '\
                         'Definition. Please make sure that Unit '\
                         'Conversion Definitions are indexed and validated. '\
                         'quantity_unit_uid: %s, resource_uid: %s' \
                          % (quantity_unit_uid, self.getUid()))
