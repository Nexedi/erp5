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
from Products.ERP5Type.Base import Base
from Products.ERP5.VariationValue import VariationValue
from Products.ERP5.Variated import Variated

from zLOG import LOG


class Amount(Base, Variated):
  """
    A mix-in class which provides some utilities
    (variations, conversions, etc.)

    Utilities include

    - getVariation accesors (allows to access variations of whatever)

    -
  """

  # Declarative security
  security = ClassSecurityInfo()

  # Declarative interfaces
  __implements__ = (Interface.Variated)

  # A few more mix-in methods which should be relocated
  # THIS MUST BE UPDATE WITH CATEGORY ACQUISITION
  security.declareProtected(Permissions.AccessContentsInformation, 'getVariationCategoryList')
  def getVariationCategoryList(self, base_category_list = ()):
    """
      Returns the possible discrete variations
      (as a list of relative urls to categories)
    """
    result = []
    resource = self.getDefaultResourceValue()
    if resource is not None:
      resource_variation_list = resource.getVariationBaseCategoryList()
      if len(base_category_list) > 0 :
        variation_list = []
        for base_category in resource_variation_list :
          if base_category in base_category_list :
            variation_list.append(base_category)
      else :
        variation_list = resource_variation_list
      #LOG('in getVariationCategoryList', 0, str(variation_list))
      if len(variation_list) > 0:
        result = self.getAcquiredCategoryMembershipList(variation_list, base = 1)
    return result

  security.declareProtected(Permissions.ModifyPortalContent, '_setVariationCategoryList')
  def _setVariationCategoryList(self, value):
    result = []
    resource = self.getDefaultResourceValue()
    if resource is not None:
      variation_list = resource.getVariationBaseCategoryList()
      #LOG("_setVariationCategoryList",0,str(variation_list))
      #LOG("_setVariationCategoryList",0,str(value))
      if len(variation_list) > 0:
        self._setCategoryMembership(variation_list, value, base = 1)

  security.declareProtected(Permissions.ModifyPortalContent, 'setVariationCategoryList')
  def setVariationCategoryList(self, value):
    self._setVariationCategoryList(value)
    self.reindexObject()

  security.declareProtected(Permissions.AccessContentsInformation, 'getVariationValue')
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


  security.declareProtected(Permissions.AccessContentsInformation,
                                                'getVariationRangeCategoryItemList')
  def getVariationRangeCategoryItemList(self, base_category_list = (),
                                        display_id='getTitle', base=1,  current_category=None):
    """
      Returns possible category items for this amount ie.
      the variation of the resource (not the variation range)
    """
    try:
      return self.getDefaultResourceValue().getVariationCategoryItemList(
               base_category_list, display_id=display_id, base=base, current_category=current_category)
    except:
      # FIXME: method_name vs. method_id, current_category vs. start_with_empty, etc. -yo
      return self.portal_categories.getCategoryChildItemList(base=base, display_id=display_id)

  security.declareProtected(Permissions.AccessContentsInformation,
                                              'getVariationRangeCategoryList')
  def getVariationRangeCategoryList(self, base_category_list = (), base=1):
    """
      Returns possible categories for this amount ie.
      the variation of the resource (not the variation range)
    """
    try:
      # FIXME: no base argument in getVariationCategoryList -yo
      return self.getDefaultResourceValue().getVariationCategoryList(base_category_list=base_category_list)
    except:
      # FIXME: method_name vs. method_id, etc. -yo
      return self.portal_categories.getCategoryChildList()

  security.declareProtected(Permissions.AccessContentsInformation,
                                            'getVariationRangeBaseCategoryList')
  def getVariationRangeBaseCategoryList(self):
    """
        Returns possible variations base categories for this amount ie.
        the variation base category of the resource (not the
        variation range).

        Should be a range because we shall variate the amount
        into cells (ie. the line into cells) on part of the
        getVariationRangeBaseCategoryList -> notion of
        getVariationBaseCategoryList is different
    """
    try:
      return self.getDefaultResourceValue().getVariationBaseCategoryList()
    except:
      return self.portal_categories.getBaseCategoryList()

  security.declareProtected(Permissions.AccessContentsInformation,
                                                 'getQuantityUnitRangeItemList')
  def getQuantityUnitRangeItemList(self, base_category_list=()):
    try:
      result = self.getDefaultResourceValue().getQuantityUnitList()
    except:
      result = ()
    if result is ():
      return self.portal_categories.quantity_unit.getFormItemList()
    else:
      return result

  # Conversion to standard unit
  security.declareProtected(Permissions.AccessContentsInformation, 'getConvertedQuantity')
  def getConvertedQuantity(self):
    """
      Converts quantity to default unit
    """
    try:
    #if 1:
      resource = self.getResourceValue()
      resource_quantity_unit = resource.getDefaultQuantityUnit()
      quantity_unit = self.getQuantityUnit()
      quantity = self.getQuantity()
      converted_quantity = resource.convertQuantity(quantity, quantity_unit, resource_quantity_unit)
    except:
      LOG("ERP5 WARNING:", 100, 'could not convert quantity for %s' % self.getRelativeUrl())
      converted_quantity = None
    return converted_quantity

  security.declareProtected(Permissions.ModifyPortalContent, 'setConvertedQuantity')
  def setConvertedQuantity(self, value):
    try:
    #if 1:
      resource = self.getResourceValue()
      resource_quantity_unit = resource.getDefaultQuantityUnit()
      quantity_unit = self.getQuantityUnit()
      quantity = resource.convertQuantity(value, resource_quantity_unit, quantity_unit)
      self.setQuantity(quantity)
    except:
      LOG("ERP5 WARNING:", 100, 'could not set converted quantity for %s' % self.getRelativeUrl())

  security.declareProtected(Permissions.AccessContentsInformation, 'getConvertedTargetQuantity')
  def getConvertedTargetQuantity(self):
    """
      Converts target_quantity to default unit
    """
    #if 1:
    try:
    #if 1:
      resource = self.getResourceValue()
      resource_quantity_unit = resource.getDefaultQuantityUnit()
      quantity_unit = self.getQuantityUnit()
      quantity = self.getTargetQuantity()
      converted_quantity = resource.convertQuantity(quantity, quantity_unit, resource_quantity_unit)
    #else:
    except:
    #else:
      LOG("ERP5 WARNING:", 100, 'could not convert target_quantity for %s' % self.getRelativeUrl())
      converted_quantity = None
    return converted_quantity

  security.declareProtected(Permissions.ModifyPortalContent, 'setConvertedTargetQuantity')
  def setConvertedTargetQuantity(self, value):
    try:
    #if 1:
      resource = self.getResourceValue()
      resource_quantity_unit = resource.getDefaultQuantityUnit()
      quantity_unit = self.getQuantityUnit()
      quantity = resource.convertQuantity(value, resource_quantity_unit, quantity_unit)
      self.setTargetQuantity(quantity)
    except:
      LOG("ERP5 WARNING:", 100, 'could not set converted quantity for %s' % self.getRelativeUrl())

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
  def getProductionQuantity(self):
    """
      Return the produced quantity
    """
    quantity = self.getQuantity()
    source = self.getSource()
    destination = self.getDestination()

    try:
      quantity = float(quantity)
    except:
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
  def getConsumptionQuantity(self):
    """
      Return the produced quantity
    """
    quantity = self.getQuantity()
    source = self.getSource()
    destination = self.getDestination()

    try:
      quantity = float(quantity)
    except:
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

    try:
      quantity = float(value)
    except:
      quantity = 0.0

    if source in (None, ''):
      if quantity >= 0:
        self.setQuantity(quantity)
      else:
        return 0.0

    if destination in (None, ''):
      if quantity >= 0:
        self.setQuantity(- quantity)
      else:
        return 0.0

  security.declareProtected(Permissions.ModifyPortalContent, 'setConsumptionQuantity')
  def setConsumptionQuantity(self, value):
    """
      Return the produced quantity
    """
    source = self.getSource()
    destination = self.getDestination()

    try:
      quantity = float(value)
    except:
      quantity = 0.0

    if destination in (None, ''):
      if quantity >= 0:
        self.setQuantity(quantity)
      else:
        return 0.0

    if source in (None, ''):
      if quantity >= 0:
        self.setQuantity(- quantity)
      else:
        return 0.0

  # Inventory
  security.declareProtected(Permissions.AccessContentsInformation, 'getConvertedInventory')
  def getConvertedInventory(self):
    """
      provides a default inventory value - None since
      no inventory was defined.
    """
    return None

  # Profit and Loss
  security.declareProtected(Permissions.ModifyPortalContent, 'getLostQuantity')
  def getLostQuantity(self):
    return - self.getProfitQuantity()

  security.declareProtected(Permissions.AccessContentsInformation, 'setLostQuantity')
  def setLostQuantity(self, value):
    return self.setProfitQuantity(- value)

  def _setLostQuantity(self, value):
    return self._setProfitQuantity(- value)
