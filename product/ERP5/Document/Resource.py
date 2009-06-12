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

import zope.interface
from math import log
from warnings import warn

from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5Type.Base import Base

from Products.ERP5.Variated import Variated
from Products.CMFCategory.Renderer import Renderer
from Products.CMFCore.utils import getToolByName

from zLOG import LOG, WARNING

class Resource(XMLMatrix, Variated):
    """
      A Resource
    """

    meta_type = 'ERP5 Resource'
    portal_type = 'Resource'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative interfaces
    zope.interface.implements( interfaces.IVariated, )

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Price
                      , PropertySheet.Resource
                      , PropertySheet.Reference
                      , PropertySheet.Comment
                      , PropertySheet.FlowCapacity
                      , PropertySheet.VariationRange
                      , PropertySheet.DefaultSupply
                      , PropertySheet.Aggregated
                      )

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
        if base_category_list is ():
          base_category_list = self.getVariationBaseCategoryList(
              omit_individual_variation=omit_individual_variation)
        elif isinstance(base_category_list, str):
          base_category_list = (base_category_list,)

        individual_variation_list = self.searchFolder(
            portal_type=self.getPortalVariationTypeList(),
            sort_on=[('title','ascending')])
        individual_variation_list = [x.getObject() for x in
            individual_variation_list]
        other_base_category_dict = dict([(i,1) for i in base_category_list])
 
        if not omit_individual_variation:              
          for variation in individual_variation_list:
            for base_category in variation.getVariationBaseCategoryList():
              if base_category_list is ()\
                  or base_category in base_category_list:
                other_base_category_dict[base_category] = 0
                # XXX now, call Renderer a lot of time.
                # Better implementation needed
                result.extend(Renderer(
                    base_category=base_category, 
                    display_base_category=display_base_category,
                    display_none_category=0, base=base,
                    current_category=current_category,
                    display_id=display_id).render([variation]))

        other_base_category_list = [x for x, y in
            other_base_category_dict.iteritems() if y == 1]
        # Get category variation
        if other_base_category_list:
          result.extend(Variated.getVariationRangeCategoryItemList(
              self, base_category_list=other_base_category_list,
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
                         display_id='getTitle' (default value getTitleOrId)
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
              
      
      result = Variated.getVariationCategoryItemList(self, 
                            base_category_list=other_bc_list, 
                            display_base_category=display_base_category, 
                            display_id=display_id, base=base, **kw)
      
      if not omit_individual_variation:
        individual_variation_list = self.searchFolder(
            portal_type=self.getPortalVariationTypeList())
        individual_variation_list = [x.getObject() for x in
            individual_variation_list]

        for variation in individual_variation_list:
          for base_category in variation.getVariationBaseCategoryList():
            # backwards compatbility: if individual_bc_list is empty, allow
            # all individual variation base categories.
            if (base_category_list is ()
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
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getCurrentInventory')
    def getCurrentInventory(self, **kw):
      """
      Returns current inventory
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getCurrentInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getAvailableInventory')
    def getAvailableInventory(self, **kw):
      """
      Returns available inventory
      (current inventory - deliverable)
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getAvailableInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getFutureInventory')
    def getFutureInventory(self, **kw):
      """
      Returns inventory at infinite
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getFutureInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getInventoryList')
    def getInventoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getCurrentInventoryList')
    def getCurrentInventoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getCurrentInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getAvailableInventoryList')
    def getAvailableInventoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getAvailableInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getFutureInventoryList')
    def getFutureInventoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getFutureInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getInventoryStat')
    def getInventoryStat(self, **kw):
      """
      Returns statistics of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getInventoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getCurrentInventoryStat')
    def getCurrentInventoryStat(self, **kw):
      """
      Returns statistics of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getCurrentInventoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAvailableInventoryStat')
    def getAvailableInventoryStat(self, **kw):
      """
      Returns statistics of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getAvailableInventoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getFutureInventoryStat')
    def getFutureInventoryStat(self, **kw):
      """
      Returns statistics of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getFutureInventoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getInventoryChart')
    def getInventoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getInventoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getCurrentInventoryChart')
    def getCurrentInventoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getCurrentInventoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getFutureInventoryChart')
    def getFutureInventoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getFutureInventoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getInventoryHistoryList')
    def getInventoryHistoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getInventoryHistoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getInventoryHistoryChart')
    def getInventoryHistoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
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
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getMovementHistoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getMovementHistoryStat')
    def getMovementHistoryStat(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getMovementHistoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getNextNegativeInventoryDate')
    def getNextNegativeInventoryDate(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getNextNegativeInventoryDate(**kw)


    # Asset Price API
    security.declareProtected(Permissions.AccessContentsInformation,
        'getInventoryAssetPrice')
    def getInventoryAssetPrice(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getInventoryAssetPrice(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
        'getCurrentInventoryAssetPrice')
    def getCurrentInventoryAssetPrice(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getCurrentInventoryAssetPrice(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
        'getAvailableInventoryAssetPrice')
    def getAvailableInventoryAssetPrice(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getAvailableInventoryAssetPrice(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
        'getFutureInventoryAssetPrice')
    def getFutureInventoryAssetPrice(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource_uid'] = self.getUid()
      portal_simulation = getToolByName(self, 'portal_simulation')
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

    # Predicate handling
    security.declareProtected(Permissions.AccessContentsInformation, 
                              'asPredicate')
    def asPredicate(self):
      """
      Returns a temporary Predicate based on the Resource properties
      """
      from Products.ERP5 import newTempPredicateGroup as newTempPredicate
      p = newTempPredicate(self.getId(), uid = self.getUid())
      p.setMembershipCriterionBaseCategoryList(('resource',))
      p.setMembershipCriterionCategoryList(('resource/%s'
          % self.getRelativeUrl(),))
      return p

    def _pricingSortMethod(self, a, b):
      # Simple method : the one that defines a destination section wins
      if a.getDestinationSection():
        return -1 # a defines a destination section and wins
      return 1 # a defines no destination section and loses

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getPriceParameterDict')
    def getPriceParameterDict(self, context=None, REQUEST=None, **kw):
      """
      Get all pricing parameters from Predicate.
      """
      # Search all categories context
      new_category_list = []
      if context is not None:
        new_category_list += context.getCategoryList()
      #XXX This should be 'category_list' instead of 'categories' to respect
      # the naming convention. Must take care of side effects when fixing
      if kw.has_key('categories'):
        new_category_list.extend(kw['categories'])
        del kw['categories']
      resource_category = 'resource/' + self.getRelativeUrl()
      if not resource_category in new_category_list:
        new_category_list += (resource_category, )
      # Generate the predicate mapped value
      # to get some price values.
      domain_tool = getToolByName(self,'portal_domains')
      portal_type_list = self.getPortalSupplyPathTypeList()

      # Generate the fake context
      tmp_context = self.asContext(context=context, 
                                   categories=new_category_list,
                                   REQUEST=REQUEST, **kw)
      tmp_kw = kw.copy()
      if 'sort_method' not in tmp_kw:
        tmp_kw['sort_method'] = self._pricingSortMethod
      mapped_value = domain_tool.generateMultivaluedMappedValue(
                                             tmp_context,
                                             portal_type=portal_type_list,
                                             has_cell_content=0, **tmp_kw)
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
      }
      if mapped_value is None:
        return price_parameter_dict
      for price_parameter_name in price_parameter_dict.keys():
        price_parameter_value = \
          mapped_value.getProperty(price_parameter_name,
              d=price_parameter_dict[price_parameter_name])
        if price_parameter_value not in [None, [], '']:
          try:
            price_parameter_dict[price_parameter_name].extend(
                                            price_parameter_value)
          except AttributeError:
            if price_parameter_dict[price_parameter_name] is None:
              if price_parameter_name == 'exclusive_discount_ratio':
                price_parameter_dict[price_parameter_name] = \
                    max(price_parameter_value)
              else:
                price_parameter_dict[price_parameter_name] = \
                    price_parameter_value[0]
      return price_parameter_dict
      
    security.declareProtected(Permissions.AccessContentsInformation,
        'getPricingVariable')
    def getPricingVariable(self, context=None):
      """
      Return the value of the property used to calculate variable pricing
      This basically calls a script like Product_getPricingVariable
      """
      warn('Resource.getPricingVariable is deprecated; Please use' \
           ' a type-based method for getPrice, and call whatever scripts' \
           ' you need to invoke from that method.', DeprecationWarning)
      method = None
      if context is not None:
        method = context._getTypeBasedMethod('getPricingVariable')
      if method is None or context is None:
        method = self._getTypeBasedMethod('getPricingVariable')

      if method is None:
        return 0.0
      return float(method())

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getPriceCalculationOperandDict')
    def getPriceCalculationOperandDict(self, default=None, context=None,
            REQUEST=None, **kw):
      """Return a dictionary which contains operands for price calculation.
      Consult the doc string in Movement.getPriceCalculationOperandDict
      for more details.
      """
      # First, try to use a new type-based method for the calculation.
      # Note that this is based on self (i.e. a resource) instead of context
      # (i.e. a movement).
      method = self._getTypeBasedMethod('getPriceCalculationOperandDict')
      if method is not None:
        return method(default=default, movement=context, REQUEST=REQUEST, **kw)

      # Next, try an old type-based method which returns only a final result.
      method = self._getTypeBasedMethod('getPrice')
      if method is not None:
        price = method(default=default, movement=context, REQUEST=REQUEST, **kw)
        if price is not None:
          return {'price': price}
        return default

      # This below is used only if any type-based method is not
      # available at all. We should provide the default implementation
      # in a Business Template as Resource_getPrice, thus this will not
      # be used in the future. Kept only for backward compatibility in
      # case where the user still uses an older Business Template.

      price_parameter_dict = self.getPriceParameterDict(
                                     context=context, REQUEST=REQUEST, **kw)
      # Calculate the unit price
      unit_base_price = None
      # Calculate
#     ((base_price + SUM(additional_price) +
#     variable_value * SUM(variable_additional_price)) *
#     (1 - MIN(1, MAX(SUM(discount_ratio) , exclusive_discount_ratio ))) +
#     SUM(non_discountable_additional_price)) *
#     (1 + SUM(surcharge_ratio))
      # Or, as (nearly) one single line :
#     ((bp + S(ap) + v * S(vap))
#       * (1 - m(1, M(S(dr), edr)))
#       + S(ndap))
#     * (1 + S(sr))
      # Variable value is dynamically configurable through a python script.
      # It can be anything, depending on business requirements.
      # It can be seen as a way to define a pricing model that not only
      # depends on discrete variations, but also on a continuous property
      # of the object

      base_price = price_parameter_dict['base_price']
      if base_price in [None, '']:
        # XXX Compatibility
        # base_price must not be defined on resource
        base_price = self.getBasePrice()
      if base_price not in [None, '']:
        unit_base_price = base_price
        # Sum additional price
        for additional_price in price_parameter_dict['additional_price']:
          unit_base_price += additional_price
        # Sum variable additional price
        variable_value = self.getPricingVariable(context=context)
        for variable_additional_price in \
            price_parameter_dict['variable_additional_price']:
          unit_base_price += variable_additional_price * variable_value
        # Discount
        sum_discount_ratio = 0
        for discount_ratio in price_parameter_dict['discount_ratio']:
          sum_discount_ratio += discount_ratio
        exclusive_discount_ratio = \
            price_parameter_dict['exclusive_discount_ratio']
        d_ratio = 0
        d_ratio = max(d_ratio, sum_discount_ratio)
        if exclusive_discount_ratio not in [None, '']:
          d_ratio = max(d_ratio, exclusive_discount_ratio)
        if d_ratio != 0:
          d_ratio = 1 - min(1, d_ratio)
          unit_base_price = unit_base_price * d_ratio
        # Sum non discountable additional price
        for non_discountable_additional_price in\
            price_parameter_dict['non_discountable_additional_price']:
          unit_base_price += non_discountable_additional_price
        # Surcharge ratio
        sum_surcharge_ratio = 1
        for surcharge_ratio in price_parameter_dict['surcharge_ratio']:
          sum_surcharge_ratio += surcharge_ratio
        unit_base_price = unit_base_price * sum_surcharge_ratio
      # Divide by the priced quantity if not (None, 0)
      if unit_base_price is not None\
          and price_parameter_dict['priced_quantity']:
        priced_quantity = price_parameter_dict['priced_quantity']
        unit_base_price = unit_base_price / priced_quantity
      # Return result
      if unit_base_price is not None:
        return {'price': unit_base_price}
      return default

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
      quantity = float(traverse(quantity_unit).getProperty('quantity'))
      if quantity_unit.split('/', 1)[0] != management_unit.split('/', 1)[0]:
        measure = self.getDefaultMeasure(quantity_unit)
        quantity /= measure.getConvertedQuantity(variation_list)
      else:
        quantity /= float(traverse(management_unit).getProperty('quantity'))
      return quantity

    # Unit conversion
    security.declareProtected(Permissions.AccessContentsInformation, 'convertQuantity')
    def convertQuantity(self, quantity, from_unit, to_unit, variation_list=()):
      # 'variation_list' parameter may be deprecated:
      # cf Measure.getConvertedQuantity
      try:
        return quantity * self._getConversionRatio(from_unit, variation_list) \
                        / self._getConversionRatio(to_unit, variation_list)
      except (ArithmeticError, AttributeError, LookupError, TypeError), error:
        # For compatibility, we only log the error and return None.
        # No exception for the moment.
        LOG('Resource.convertQuantity', WARNING,
            'could not convert quantity for %s (%r)'
            % (self.getRelativeUrl(), error))

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

      quantity_unit = quantity_unit_value.getCategoryRelativeUrl()
      default = self.getDefaultMeasure(quantity_unit)
      if default is not None:
        default = default.getRelativeUrl()
      metric_type_map = {} # duplicate metric_type are not valid

      for measure in self.getMeasureList():
        metric_type = measure.getMetricType()
        if metric_type in metric_type_map:
          metric_type_map[metric_type] = ()
        else:
          metric_type_map[metric_type] = measure.asCatalogRowList()
        if measure.getRelativeUrl() == default:
          quantity_unit = ''

      insert_list = []
      for measure_list in metric_type_map.itervalues():
        insert_list += measure_list

      metric_type = quantity_unit.split('/', 1)[0]
      if metric_type and metric_type not in metric_type_map:
        # At this point, we know there is no default measure and we must add
        # a row for the management unit, with the resource's uid as uid, and
        # a generic metric_type.
        quantity = quantity_unit_value.getProperty('quantity')
        metric_type_uid = self.getPortalObject().portal_categories \
                              .getCategoryUid(metric_type, 'metric_type')
        if quantity and metric_type_uid:
          uid = self.getUid()
          insert_list += (uid, uid, '^', metric_type_uid, float(quantity)),

      return insert_list
