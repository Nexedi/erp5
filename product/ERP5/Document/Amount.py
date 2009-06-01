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
from Products.ERP5.Variated import Variated
from Products.ERP5.VariationValue import VariationValue
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5Type.Base import Base
from Products.ERP5Type.Base import TempBase
from Products.CMFCategory.Renderer import Renderer


from zLOG import LOG, ERROR
from warnings import warn


class Amount(Base, Variated):
  """
    A mix-in class which provides some utilities
    (variations, conversions, etc.)

    Utilities include

    - getVariation accesors (allows to access variations of whatever)

    -
  """

  meta_type = 'ERP5 Amount'
  portal_type = 'Amount'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  __implements__ = (interfaces.IVariated)

  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.Amount
                    , PropertySheet.Price
                    )

  # A few more mix-in methods which should be relocated
  # THIS MUST BE UPDATE WITH CATEGORY ACQUISITION
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariationCategoryList')
  def getVariationCategoryList(self, default=[], base_category_list=(),
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

    result = []
    resource = self.getDefaultResourceValue()
    if resource is not None:
      resource_variation_list = resource.getVariationBaseCategoryList(
          omit_optional_variation=omit_optional_variation)
      if len(base_category_list) > 0 :
        variation_list = filter(lambda x: x in base_category_list,
                                resource_variation_list)
      else :
        variation_list = resource_variation_list
      if len(variation_list) > 0:
        result = self.getAcquiredCategoryMembershipList(variation_list, base=1)
    return result

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariationCategoryItemList')
  def getVariationCategoryItemList(self, base_category_list=(), base=1,
                                   display_id='logical_path',
                                   current_category=None,**kw):
    """
      Returns the list of possible variations
      XXX Copied and modified from Variated
      Result is left display.
    """
    variation_category_item_list = []
    if base_category_list == ():
      base_category_list = self.getVariationRangeBaseCategoryList()

    for base_category in base_category_list:
      variation_category_list = self.getVariationCategoryList(
                                          base_category_list=[base_category])

      resource_list = [self.portal_categories.resolveCategory(x) for x in\
                       variation_category_list]
      category_list = [x for x in resource_list \
                       if x.getPortalType() == 'Category']
      variation_category_item_list.extend(Renderer(
                             is_right_display=0,
                             display_none_category=0, base=base,
                             current_category=current_category,
                             display_id=display_id, **kw).\
                                               render(category_list))
      object_list = [x for x in resource_list \
                       if x.getPortalType() != 'Category']
      variation_category_item_list.extend(Renderer(
                             is_right_display=0,
                             base_category=base_category,
                             display_none_category=0, base=base,
                             current_category=current_category,
                             display_id='title', **kw).\
                                               render(object_list))
    return variation_category_item_list

  security.declareProtected(Permissions.ModifyPortalContent, 
                            '_setVariationCategoryList')
  def _setVariationCategoryList(self, value):
    result = []
    resource = self.getDefaultResourceValue()
    if resource is not None:
      variation_list = resource.getVariationBaseCategoryList()
      if len(variation_list) > 0:
        self._setCategoryMembership(variation_list, value, base = 1)

  security.declareProtected(Permissions.ModifyPortalContent, 
                            'setVariationCategoryList')
  def setVariationCategoryList(self, value):
    self._setVariationCategoryList(value)
    self.reindexObject()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariationBaseCategoryList')
  def getVariationBaseCategoryList(self, default=[],
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

  security.declareProtected(Permissions.AccessContentsInformation, 
                            'getVariationBaseCategoryItemList')
  def getVariationBaseCategoryItemList(self,display_id='getTitleOrId',**kw):
    """
    Returns a list of base_category tuples.
    """
    return self.portal_categories.getItemList(
                                    self.getVariationBaseCategoryList(),
                                    display_id=display_id,**kw)

  security.declareProtected(Permissions.AccessContentsInformation, 
                            'getVariationValue')
  def getVariationValue(self):
    """
      New Method for dicrete and countinuous variations
      using a VariantValue instance

      A new instance of VariationValue is created with categories
      and attributes set to what they should be.

      A this point, we only implement discrete variations
    """
    return VariationValue(context = self)

  security.declareProtected(Permissions.ModifyPortalContent, '_setVariationValue')
  def _setVariationValue(self, variation_value):
    return variation_value.setVariationValue(self)

  security.declareProtected(Permissions.ModifyPortalContent, 'setVariationValue')
  def setVariationValue(self, variation_value):
    self._setVariationValue(variation_value)
    self.reindexObject()

  security.declareProtected(Permissions.AccessContentsInformation, \
                            'getVariationRangeCategoryItemList')
  def getVariationRangeCategoryItemList(self, **kw):
    """
      Returns possible variation category values for the
      order line according to the default resource.
      Possible category values is provided as a list of
      tuples (id, title). This is mostly
      useful in ERP5Form instances to generate selection
      menus.
    """
    resource = self.getResourceValue()
    if resource != None:
      result = resource.getVariationCategoryItemList(
                               omit_individual_variation=0,**kw)
    else:
      result = []
    return result

  security.declareProtected(Permissions.AccessContentsInformation, \
                            'getVariationRangeCategoryList')
  def getVariationRangeCategoryList(self, default=[], base_category_list=(),
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
  def getVariationRangeBaseCategoryList(self, default=[],
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
      result = Variated.getVariationRangeBaseCategoryList(self)
    return result

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariationRangeBaseCategoryItemList')
  def getVariationRangeBaseCategoryItemList(self, omit_optional_variation=0,
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
        raise KeyError, "Can not set the property variation '%s'" % \
                        property_id
      else:
        try:
          self.setProperty(property_id, property_value)
        except KeyError:
          LOG("Amount", ERROR, "Can not set %s with value %s on %s" % \
                    (property_id, property_value, self.getRelativeUrl()))
          raise

  security.declareProtected(Permissions.AccessContentsInformation,
                                                 'getQuantityUnitRangeItemList')
  def getQuantityUnitRangeItemList(self, base_category_list=()):
    resource = self.getDefaultResourceValue()
    if resource is not None:
      result = resource.getQuantityUnitList()
    else:
      result = ()
    if result is ():
      return self.portal_categories.quantity_unit.getFormItemList()
    else:
      return result

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

  def getPrice(self):
    pass
  
  
  security.declareProtected(Permissions.AccessContentsInformation, 'getTotalPrice')
  def getTotalPrice(self, **kw):
    """
      Return total price for the number of items
      
      Price is defined on 
      
    """
    price = self.getResourcePrice()
    quantity = self.getNetConvertedQuantity()
    if isinstance(price, (int, float)) and isinstance(quantity, (int, float)):
      return quantity * price

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
        return - quantity
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
        return - quantity
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
  security.declareProtected(Permissions.ModifyPortalContent, 'getLostQuantity')
  def getLostQuantity(self):
    return - self.getProfitQuantity()

  security.declareProtected(Permissions.AccessContentsInformation, 'setLostQuantity')
  def setLostQuantity(self, value):
    return self.setProfitQuantity(- value)

  def _setLostQuantity(self, value):
    return self._setProfitQuantity(- value)
