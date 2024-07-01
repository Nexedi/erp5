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
from collections import defaultdict
from math import log
from AccessControl import ClassSecurityInfo
from Products.ERP5.mixin.variated import VariatedMixin
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Base import Base
from Products.CMFCategory.Renderer import Renderer
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from erp5.component.interface.IAmount import IAmount

from zLOG import LOG, ERROR
from warnings import warn
import six


@zope.interface.implementer(IAmount)
class Amount(Base, VariatedMixin):
  """
    A mix-in class which provides some utilities
    (variations, conversions, etc.)


    -
  """

  meta_type = 'ERP5 Amount'
  portal_type = 'Amount'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  property_sheets = ( PropertySheet.SimpleItem
                    , PropertySheet.Amount
                    , PropertySheet.Price
                    , PropertySheet.Reference
                    )

  _default_edit_order = Base._default_edit_order + (
    'resource',
    'resource_value',
    'resource_uid',

    # If variations and resources are set at the same time, resource must be
    # set before any variation.
    'variation_base_category_list',
    'variation_category_list',

    # If (quantity unit, base_contribution, or use) and resource are set at the same time,
    # resource must be set first, because of an interaction that copies quantity unit
    # base contribution and use from resource if not set.
    'quantity_unit_value',
    'quantity_unit',
    'use_value',
    'use',
    'base_contribution_list',
    'base_contribution_value_list',
    'base_contribution_value',
    'base_contribution',
  )

  # A few more mix-in methods which should be relocated
  # THIS MUST BE UPDATE WITH CATEGORY ACQUISITION
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariationCategoryList')
  def getVariationCategoryList(self, default=None, base_category_list=(), # pylint: disable=arguments-differ
      omit_optional_variation=0, omit_option_base_category=None):
    """
      Returns the possible discrete variations
      (as a list of relative urls to categories)
    """
    #XXX backwards compatibility
    if omit_option_base_category is not None:
      warn("Please use omit_optional_variation instead of"\
          " omit_option_base_category.", DeprecationWarning)
      omit_optional_variation = omit_option_base_category

    resource = self.getDefaultResourceValue()
    if resource is None:
      return []
    variation_list = resource.getVariationBaseCategoryList(
        omit_optional_variation=omit_optional_variation)
    # BBB: 'industrial_phase' should be used exclusively for production and
    #      should not appear on resource. But many unit tests still use it.
    #      For the same reason, we treat as an optional variation.
    if ('industrial_phase' not in variation_list
        and not omit_optional_variation):
      variation_list.append('industrial_phase')
    if base_category_list:
      variation_list = [v for v in variation_list if v in base_category_list]
    return self.getAcquiredCategoryMembershipList(variation_list, base=1)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariationCategoryItemList')
  def getVariationCategoryItemList(self, base_category_list=(), base=1,
                                   display_id='logical_path',
                                   current_category=None,**kw):
    """
      Returns the list of possible variations
      XXX Copied and modified from VariatedMixin
      Result is left display.
    """
    variation_category_item_list = []
    category_list = self.getVariationCategoryList()
    if category_list:
      variation_dict = defaultdict(lambda: ([], []))
      resolveCategory = self.getPortalObject().portal_categories.resolveCategory
      for category in category_list:
        resource = resolveCategory(category)
        variation_dict[category.split('/', 1)[0]] \
          [resource.getPortalType() == 'Category'].append(resource)

      kw = dict(is_right_display=0, display_none_category=0, base=base,
                current_category=current_category, **kw)
      render_category_list = Renderer(display_id=display_id, **kw).render
      kw['display_id'] = 'title'
      for base_category, (object_list,
                          category_list) in six.iteritems(variation_dict):
        if base_category_list and base_category not in base_category_list:
          continue
        variation_category_item_list += render_category_list(category_list)
        variation_category_item_list += Renderer(base_category=base_category,
                                                 **kw).render(object_list)
    return variation_category_item_list

  def _setVariationCategoryList(self, value): # pylint: disable=arguments-differ
    resource = self.getDefaultResourceValue()
    if resource is not None:
      variation_list = resource.getVariationBaseCategoryList()
      variation_list.append('industrial_phase')
      self._setCategoryMembership(variation_list, value, base=1)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'setVariationCategoryList')
  def setVariationCategoryList(self, value): # pylint: disable=arguments-differ
    self._setVariationCategoryList(value)
    self.reindexObject()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariationBaseCategoryList')
  def getVariationBaseCategoryList(self, default=None,
      omit_optional_variation=0, omit_option_base_category=None):
    """
      Return the list of base_category from all variation related to
      amount.
      It is maybe a nonsense, but useful for correcting user errors.
    """
    #XXX backwards compatibility
    if omit_option_base_category is not None:
      warn("Please use omit_optional_variation instead of"\
          " omit_option_base_category.", DeprecationWarning)
      omit_optional_variation = omit_option_base_category

    base_category_list = []
    for category in self.getVariationCategoryList(
        omit_optional_variation=omit_optional_variation):
      base_category = category.split('/')[0]
      if base_category not in base_category_list:
        base_category_list.append(base_category)
    return base_category_list

  security.declareProtected(Permissions.ModifyPortalContent,
                            'setVariationBaseCategoryList')
  def setVariationBaseCategoryList(self, node_list):
    """Do nothing in the case of an amount, because variation base category
    list are set on the resource.
    """

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariationBaseCategoryItemList')
  def getVariationBaseCategoryItemList(self,display_id='getTitleOrId',**kw):
    """
    Returns a list of base_category tuples.
    """
    return self.portal_categories.getItemList(
                                    self.getVariationBaseCategoryList(),
                                    display_id=display_id,**kw)

  security.declareProtected(Permissions.AccessContentsInformation, \
                            'getVariationRangeCategoryItemList')
  def getVariationRangeCategoryItemList(self, *args, **kw):
    """
      Returns possible variation category values for the
      order line according to the default resource.
      Possible category values is provided as a list of
      tuples (id, title). This is mostly
      useful in ERP5Form instances to generate selection
      menus.
    """
    resource = self.getResourceValue()
    if resource is None:
      return []
    kw['omit_individual_variation'] = 0
    return resource.getVariationCategoryItemList(*args, **kw)

  security.declareProtected(Permissions.AccessContentsInformation, \
                            'getVariationRangeCategoryList')
  def getVariationRangeCategoryList(self, default=None, base_category_list=(),
      base=1, **kw):
    """
      Returns possible variation category values for the
      order line according to the default resource.
    """
    return [x[1] for x in self.getVariationRangeCategoryItemList(
                                     base_category_list=base_category_list,
                                     base=base, **kw)]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariationRangeBaseCategoryList')
  def getVariationRangeBaseCategoryList(self, default=None, # pylint: disable=arguments-differ
      omit_optional_variation=0, omit_option_base_category=None):
    """
        Returns possible variations base categories for this amount ie.
        the variation base category of the resource (not the
        variation range).

        Should be a range because we shall variate the amount
        into cells (ie. the line into cells) on part of the
        getVariationRangeBaseCategoryList -> notion of
        getVariationBaseCategoryList is different
    """
    #XXX backwards compatibility
    if omit_option_base_category is not None:
      warn("Please use omit_optional_variation instead of"\
          " omit_option_base_category.", DeprecationWarning)
      omit_optional_variation = omit_option_base_category

    resource = self.getDefaultResourceValue()
    if resource is not None:
      result = resource.getVariationBaseCategoryList(
          omit_optional_variation=omit_optional_variation)
    else:
      result = super(Amount, self).getVariationRangeBaseCategoryList()
    return result

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariationRangeBaseCategoryItemList')
  def getVariationRangeBaseCategoryItemList(self, omit_optional_variation=0, # pylint: disable=arguments-differ
      omit_option_base_category=None, display_id="title",
      display_none_category=0):
    """
        Returns possible variations base categories for this amount ie.
        the variation base category of the resource (not the
        variation range).
    """
    #XXX backwards compatibility
    if omit_option_base_category is not None:
      warn("Please use omit_optional_variation instead of"\
          " omit_option_base_category.", DeprecationWarning)
      omit_optional_variation = omit_option_base_category

    return self.portal_categories.getItemList(
        self.getVariationRangeBaseCategoryList(
            omit_optional_variation=omit_optional_variation),
        display_id=display_id,
        display_none_category=display_none_category)

  #####################################################################
  #  Variation property API
  #####################################################################
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariationPropertyDict')
  def getVariationPropertyDict(self):
    """
      Return a dictionary of:
        {property_id: property_value,}
      Each property is a variation of the resource.
      The variation property list is defined on resource,
      with setVariationPropertyList.
    """
    property_dict = {}
    resource = self.getDefaultResourceValue()
    if resource is not None:
      variation_list = resource.getVariationPropertyList()
      for variation_property in variation_list:
        property_dict[variation_property] = \
            self.getProperty(variation_property)
    return property_dict

  security.declareProtected(Permissions.ModifyPortalContent,
                            'setVariationPropertyDict')
  def setVariationPropertyDict(self, property_dict):
    """
      Take a parameter a property dict like:
        {property_id: property_value,}
      Each property is a variation of the resource.
      If one of the property_id is not a variation, a exception
      KeyError is raised.
    """
    resource = self.getDefaultResourceValue()
    if resource is not None:
      variation_list = resource.getVariationPropertyList()
    else:
      variation_list = []
    for property_id, property_value in property_dict.items():
      if property_id not in variation_list:
        raise KeyError("Can not set the property variation %r" % property_id)
      else:
        try:
          self.setProperty(property_id, property_value)
        except KeyError:
          LOG("Amount", ERROR, "Can not set %s with value %s on %s" % \
                    (property_id, property_value, self.getRelativeUrl()))
          raise

  security.declareProtected(Permissions.AccessContentsInformation, 'getResourceDefaultQuantityUnit')
  def getResourceDefaultQuantityUnit(self):
    """
      Return default quantity unit of the resource
    """
    resource = self.getResourceValue()
    resource_quantity_unit = None
    if resource is not None:
      resource_quantity_unit = resource.getDefaultQuantityUnit()
      #LOG("ERP5 WARNING:", 100, 'could not convert quantity for %s' % self.getRelativeUrl())
    return  resource_quantity_unit

  security.declareProtected(Permissions.AccessContentsInformation, 'getResourcePrice')
  def getResourcePrice(self):
    """
      Return price of the resource in the current context

      The price is expressed in the standard unit of the resource (?)
    """
    resource = self.getResourceValue()
    if resource is not None:
      return resource.getPrice(context=self)
    return None

  security.declareProtected(Permissions.AccessContentsInformation, 'getDuration')
  def getDuration(self):
    """
      Return duration in minute
    """
    quantity = self.getQuantity()
    quantity_unit = self.getQuantityUnit()
    if quantity_unit is None:
      return None
    common_time_category = 'time'
    if common_time_category in quantity_unit[:len(common_time_category)]:
      duration = quantity
    else:
      duration = None
    return duration

  security.declareProtected(Permissions.AccessContentsInformation, 'getTotalPrice')
  def getTotalPrice(self, **kw):
    """
      Return total price for the number of items

      Price is defined on

    """
    price = self.getPrice()
    if price is None:
      price = self.getResourcePrice()
    quantity = self.getNetConvertedQuantity()
    if isinstance(price, (int, float)) and isinstance(quantity, (int, float)):
      return quantity * price

  def _getBaseUnitPrice(self, context):
    # Stop any recursive call to this method. This happens when a Path
    # does not have base unit price locally, so it looks it up, and
    # each path of a predicate list does the same again.
    tv = getTransactionalVariable()
    key = '_getBaseUnitPrice'
    if key in tv:
      return
    tv[key] = 1
    try:
      resource = context.getResourceValue()
      if resource is not None:
        operand_dict = resource.getPriceParameterDict(context=context)
        if operand_dict is not None:
          base_unit_price = operand_dict.get('base_unit_price', None)
          return base_unit_price
    finally:
      del tv[key]

  security.declareProtected(Permissions.AccessContentsInformation, 'getBaseUnitPrice')
  def getBaseUnitPrice(self, context=None, **kw):
    """
      Get the base unit price.

      If the property is not stored locally, look up one and store it.
    """
    local_base_unit_price = self._baseGetBaseUnitPrice()
    if local_base_unit_price is None:
      # We must find a base unit price for this movement
      if context is None:
        context = self
      local_base_unit_price = self._getBaseUnitPrice(context=context)
    return local_base_unit_price

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPricePrecision')
  def getPricePrecision(self):
    """Return the floating point precision of a price.
    """
    # First, try to use a base unit price. If not available, use
    # the older way of using a price currency.
    try:
      return int(round(- log(self.getBaseUnitPrice(), 10), 0))
    except TypeError:
      return self.getQuantityPrecisionFromResource(self.getPriceCurrency())

  # Conversion to standard unit
  security.declareProtected(Permissions.AccessContentsInformation, 'getConvertedQuantity')
  def getConvertedQuantity(self):
    """
      Converts quantity to default unit
    """
    resource = self.getResourceValue()
    quantity_unit = self.getQuantityUnit()
    quantity = self.getQuantity()
    if quantity is not None and quantity_unit and resource is not None:
      converted = resource.convertQuantity(quantity, quantity_unit,
                                           resource.getDefaultQuantityUnit(),
                                           self.getVariationCategoryList())
      # For compatibility, return quantity non-converted if conversion fails.
      if converted is not None:
        return converted
    return quantity

  security.declareProtected(Permissions.ModifyPortalContent, 'setConvertedQuantity')
  def setConvertedQuantity(self, value):
    resource = self.getResourceValue()
    quantity_unit = self.getQuantityUnit()
    if value is not None and quantity_unit and resource is not None:
      quantity = resource.convertQuantity(value,
                                          resource.getDefaultQuantityUnit(),
                                          quantity_unit,
                                          self.getVariationCategoryList())
    else:
      quantity = value
    if quantity is not None:
      return self.setQuantity(quantity)

  security.declareProtected(Permissions.AccessContentsInformation, 'getNetQuantity')
  def getNetQuantity(self):
    """
      Take into account efficiency in quantity
    """
    quantity = self.getQuantity()
    efficiency = self.getEfficiency()
    if efficiency in (0, 0.0, None, ''):
      efficiency = 1.0
    return float(quantity) / efficiency

  security.declareProtected(Permissions.AccessContentsInformation, 'getNetTargetQuantity')
  def getNetTargetQuantity(self):
    """
      Take into account efficiency in target quantity
      XXX - dreprecated
    """
    quantity = self.getTargetQuantity()
    efficiency = self.getTargetEfficiency()
    if efficiency in (0, 0.0, None, ''):
      efficiency = 1.0
    return float(quantity) / efficiency

  security.declareProtected(Permissions.AccessContentsInformation, 'getNetConvertedQuantity')
  def getNetConvertedQuantity(self):
    """
      Take into account efficiency in converted quantity
    """
    quantity = self.getConvertedQuantity()
    efficiency = self.getEfficiency()
    if efficiency in (0, 0.0, None, ''):
      efficiency = 1.0
    if quantity not in (None, ''):
      return float(quantity) / efficiency
    else:
      return None

  security.declareProtected(Permissions.ModifyPortalContent, 'setNetConvertedQuantity')
  def setNetConvertedQuantity(self, value):
    """
      Take into account efficiency in converted quantity
    """
    efficiency = self.getEfficiency()
    if efficiency in (0, 0.0, None, ''):
      efficiency = 1.0
    if value not in (None, ''):
      quantity = float(value) * efficiency
    else:
      quantity = value
    self.setConvertedQuantity(quantity)

  security.declareProtected(Permissions.AccessContentsInformation, 'getNetConvertedTargetQuantity')
  def getNetConvertedTargetQuantity(self):
    """
      Take into account efficiency in converted target quantity
    """
    quantity = self.getConvertedTargetQuantity()
    efficiency = self.getTargetEfficiency()
    if efficiency in (0, 0.0, None, ''):
      efficiency = 1.0
    if quantity not in (None, ''):
      return float(quantity) / efficiency
    else:
      return None

  security.declareProtected(Permissions.ModifyPortalContent, 'setNetConvertedTargetQuantity')
  def setNetConvertedTargetQuantity(self, value):
    """
      Take into account efficiency in converted quantity
    """
    efficiency = self.getEfficiency()
    if efficiency in (0, 0.0, None):
      efficiency = 1.0
    if value not in (None, ''):
      quantity = float(value) * efficiency
    else:
      quantity = value
    self.setConvertedTargetQuantity(quantity)

  security.declareProtected(Permissions.AccessContentsInformation, 'getInventoriatedQuantity')
  def getInventoriatedQuantity(self):
    """
      Take into account efficiency in converted target quantity
    """
    return self.getNetConvertedQuantity()

  # Helper methods to display quantities as produced / consumed
  security.declareProtected(Permissions.AccessContentsInformation, 'getProductionQuantity')
  def getProductionQuantity(self,quantity=None):
    """
      Return the produced quantity
    """
    if quantity is None:
      quantity = self.getQuantity()
    source = self.getSource()
    destination = self.getDestination()

    if quantity is not None:
      quantity = float(quantity)
    else:
      quantity = 0.0

    if source in (None, ''):
      if quantity > 0:
        return quantity
      else:
        return 0.0

    if destination in (None, ''):
      if quantity < 0:
        return - quantity  # pylint:disable=invalid-unary-operand-type
      else:
        return 0.0

  security.declareProtected(Permissions.AccessContentsInformation, 'getConsumptionQuantity')
  def getConsumptionQuantity(self,quantity=None):
    """
      Return the consumption quantity
    """
    if quantity is None:
      quantity = self.getQuantity()
    source = self.getSource()
    destination = self.getDestination()

    if quantity is not None:
      quantity = float(quantity)
    else:
      quantity = 0.0

    if destination in (None, ''):
      if quantity > 0:
        return quantity
      else:
        return 0.0

    if source in (None, ''):
      if quantity < 0:
        return - quantity  # pylint:disable=invalid-unary-operand-type
      else:
        return 0.0

  security.declareProtected(Permissions.ModifyPortalContent, 'setProductionQuantity')
  def setProductionQuantity(self, value):
    """
      Return the produced quantity
    """
    source = self.getSource()
    destination = self.getDestination()
    quantity = value

    if quantity is not None:
      quantity = float(quantity)
    else:
      quantity = 0.0

    if source in (None, ''):
      if quantity >= 0:
        self.setQuantity(quantity)

    if destination in (None, ''):
      if quantity >= 0:
        self.setQuantity(- quantity)

  security.declareProtected(Permissions.ModifyPortalContent, 'setConsumptionQuantity')
  def setConsumptionQuantity(self, value):
    """
      Return the produced quantity
    """
    source = self.getSource()
    destination = self.getDestination()
    quantity = value

    if quantity is not None:
      quantity = float(quantity)
    else:
      quantity = 0.0

    if destination in (None, ''):
      if quantity >= 0:
        self.setQuantity(quantity)

    if source in (None, ''):
      if quantity >= 0:
        self.setQuantity(- quantity)

  # Inventory
  security.declareProtected(Permissions.AccessContentsInformation, 'getConvertedInventory')
  def getConvertedInventory(self):
    """
      provides a default inventory value - None since
      no inventory was defined.
    """
    return None

#   # SKU vs. CU
#   security.declareProtected(Permissions.AccessContentsInformation, 'getStandardInventoriatedQuantity')
#   def getStandardInventoriatedQuantity(self):
#     """
#       The inventoriated quantity converted in a default unit
#
#       For assortments, returns the inventoriated quantity in terms of number of items
#       in the assortemnt.
#
#       For accounting, returns the quantity converted in a default unit
#     """
#     resource = self.getResourceValue()
#     result = self.getInventoriatedQuantity()
#     if resource is not None:
#       result = resource.standardiseQuantity(result)
#     return result

  # Profit and Loss
  security.declareProtected(Permissions.AccessContentsInformation, 'getLostQuantity')
  def getLostQuantity(self):
    return - self.getProfitQuantity()

  security.declareProtected(Permissions.ModifyPortalContent, 'setLostQuantity')
  def setLostQuantity(self, value):
    return self.setProfitQuantity(- value)

  def _setLostQuantity(self, value):
    return self._setProfitQuantity(- value)

  ## quantity_unit accessors for backward compatibility:
  ## (we used to acquire quantity_unit from the resources)
  security.declareProtected(Permissions.AccessContentsInformation,
      'getQuantityUnitValue')
  def getQuantityUnitValue(self):
    result = self.getDefaultValue('quantity_unit')
    if result is None:
      resource = self.getResourceValue()
      if resource is not None:
        result = resource.getQuantityUnitValue()
    return result

  security.declareProtected(Permissions.AccessContentsInformation,
      'getQuantityUnit')
  def getQuantityUnit(self, checked_permission=None):
    result = self._getDefaultCategoryMembership('quantity_unit', checked_permission=checked_permission)
    if result is None:
      resource = self.getResourceValue()
      if resource is not None:
        result = resource.getQuantityUnit(checked_permission=checked_permission)
    return result

