##############################################################################
#
# Copyright (c) 2008 Nexedi SARL and Contributors. All Rights Reserved.
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

from zLOG import LOG, WARNING

from AccessControl import ClassSecurityInfo

from Products.ERP5Type import PropertySheet
from Products.ERP5Type.Permissions import AccessContentsInformation
from Products.ERP5Type.XMLMatrix import XMLMatrix


class Measure(XMLMatrix):
  """
    A Measure
  """

  meta_type = 'ERP5 Measure'
  portal_type = 'Measure'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.Measure
                    )

  security.declareProtected(AccessContentsInformation, 'getResourceValue')
  def getResourceValue(self):
    """
    Gets the resource object described by this measure.
    """
    return self.getDefaultResourceValue()

  ##
  #  Forms.

  security.declareProtected(AccessContentsInformation, 'getVariationRangeCategoryItemList')
  def getVariationRangeCategoryItemList(self, variation):
    """
    Returns possible variation category values for the selected variation.
    variation is a 0-based index and possible category values is provided
    as a list of tuples (id, title). This is mostly useful for matrixbox.
    """
    mvbc_list = self.getMeasureVariationBaseCategoryList()
    if len(mvbc_list) <= variation:
      return ()
    return self.getResourceValue().getVariationCategoryItemList(
      is_right_display=1,
      base_category_list=(mvbc_list[variation],),
      omit_individual_variation=0,
      display_base_category=0,
      sort_id='id')

  security.declareProtected(AccessContentsInformation, 'getQuantityUnitItemList')
  def getQuantityUnitItemList(self):
    """
    Returns the list of possible quantity units for the current metric type.
    This is mostly useful in ERP5Form instances to generate selection menus.
    """
    metric_type = self.getMetricType()
    if not metric_type:
      return ('', ''),
    portal = self.getPortalObject()
    return getattr(
      portal.portal_categories.getCategoryValue(metric_type.split('/', 1)[0],
                                                'quantity_unit'),
      portal.portal_preferences.getPreference(
        'preferred_category_child_item_list_method_id',
        'getCategoryChildCompactLogicalPathItemList')
    )(recursive=0, local_sort_id='quantity', checked_permission='View')

  security.declareProtected(AccessContentsInformation, 'getLocalQuantityUnit')
  def getLocalQuantityUnit(self):
    """
    Returns the 'quantity_unit' category without acquisition.
    Used in Resource_viewMeasure and Measure_view.
    """
    quantity_unit_list = self.getPortalObject().portal_categories \
      .getSingleCategoryMembershipList(self, 'quantity_unit')
    if quantity_unit_list:
      return quantity_unit_list[0]

  ##
  #  Measures associated to a quantity unit of the resource
  #  have a specific behaviour.

  security.declareProtected(AccessContentsInformation, 'isDefaultMeasure')
  def isDefaultMeasure(self, quantity_unit=None):
    """
    Checks if self is a default measure for the associated resource.
    """
    default = self.getResourceValue().getDefaultMeasure(quantity_unit)
    return default is not None \
       and self.getRelativeUrl() == default.getRelativeUrl()

  ##
  #  Conversion.

  security.declareProtected(AccessContentsInformation, 'getConvertedQuantityUnit')
  def getConvertedQuantityUnit(self):
    """
    Gets the quantity unit ratio, in respect to the base quantity unit.
    """
    quantity_unit = self.getQuantityUnitValue()
    metric_type = self.getMetricType()
    if quantity_unit is not None and metric_type and \
        quantity_unit.getParentId() == metric_type.split('/', 1)[0]:
      return self.getQuantityUnitDefinitionRatio(quantity_unit)

  security.declareProtected(AccessContentsInformation, 'getConvertedQuantity')
  def getConvertedQuantity(self, variation_list=()):
    """
    Gets the measure value for a specified variation,
    in respected to the base quantity unit.

    Should it be reimplemented using predicates?
    If so, 'variation_list' parameter is deprecated.
    """
    quantity_unit = self.getConvertedQuantityUnit()
    if not quantity_unit:
      return
    quantity = self.getQuantity()
    if variation_list:
      variation_set = set(variation_list)
      for cell in self.objectValues():
        # if cell.test(context): # XXX
        if variation_set.issuperset(
            cell.getMembershipCriterionCategoryList()):
          quantity = cell.getQuantity()
          break
    return quantity * quantity_unit

  ##
  #  Cataloging.

  security.declareProtected(AccessContentsInformation, 'asCatalogRowList')
  def asCatalogRowList(self, quantity_unit_definition_dict):
    """
    Returns the list of rows to insert in the measure table of the catalog.
    Called by Resource.getMeasureRowList.
    """
    # The only purpose of the defining a default measure explicitly is to
    # set a specific metric_type for the management unit.
    # Therefore, the measure mustn't be variated and the described quantity
    # (quantity * quantity_unit) must match the management unit.
    # If the conditions aren't met, return an empty list.
    default = self.isDefaultMeasure()

    resource = self.getResourceValue()
    resource_uid = resource.getUid()

    quantity_unit_value = self.getQuantityUnitValue()
    if default and quantity_unit_value is None:
      # for default measure candidates, we do not care if the
      # quantity is not set: use the resource quantity unit!
      quantity_unit_value = resource.getQuantityUnitValue()

    metric_type = self.getMetricType()
    if quantity_unit_value is None or not metric_type or \
        quantity_unit_value.getParentId() != metric_type.split('/', 1)[0]:
      return ()

    def getQuantity(quantity_unit_value):
      quantity_unit_uid = quantity_unit_value.getUid()
      try:
        return quantity_unit_definition_dict[quantity_unit_uid][1]
      except KeyError:
        LOG("Measure", WARNING,
            "could not find an Unit Definition for '%s' while " \
            "indexing Measure '%s'" % \
                (quantity_unit_value.getRelativeUrl(),
                 self.getRelativeUrl()))
        return None

    uid = self.getUid()
    metric_type_uid = self.getMetricTypeUid()
    quantity = self.getQuantity()

    quantity_unit = getQuantity(quantity_unit_value)
    if quantity_unit is None:
      return ()

    measure_variation_base_category_list = \
      self.getMeasureVariationBaseCategoryList()
    if not measure_variation_base_category_list:
      # Easy case: there is no variation axe for this metric_type,
      # so we simply return 1 row.
      if quantity is not None:
        quantity *= quantity_unit
        management_unit_value = resource.getQuantityUnitValue()
        management_unit_quantity = None
        if management_unit_value is not None:
          management_unit_quantity = getQuantity(management_unit_value)

        if (not default or quantity == management_unit_quantity):
          return (dict(uid=uid, resource_uid=resource_uid,
                       variation='^', metric_type_uid=metric_type_uid,
                       quantity=quantity)),
      return ()

    if default:
      return ()

    # 1st step: Build a list of possible variation combinations.
    # Each element of the list (variation_list) is a pair of lists, where:
    #  * first list's elements are regex tokens:
    #    they'll be used to build the 'variation' values (in the result).
    #  * the second list is a combination of categories, used to find
    #    the measure cells containing the 'quantity' values.
    #
    # This step is done by starting from a 1-element list (variation_list).
    # For each variation axe (if variation_base_category in
    # measure_variation_base_category_list), we rebuild variation_list entirely
    # and its size is multiplied by the number of categories in this axe.
    # For other variation base categories (variation_base_category not in
    # measure_variation_base_category_list), we simply
    # update variation_list to add 1 regex token to each regex list.
    #
    # Example:
    #  * variation base categories: colour, logo, size
    #  * variation axes: colour, size
    #
    #  variation_list (tokens are simplified for readability):
    # 0. []
    # 1. [([colour/red],   ['colour/red']),
    #     ([colour/green], ['colour/green']),
    #     ([colour/blue],  ['colour/blue'])]
    # 2. [([colour/red,   logo/*], ['colour/red']),
    #     ([colour/green, logo/*], ['colour/green']),
    #     ([colour/blue,  logo/*], ['colour/blue'])]
    # 3. [([colour/red,   logo/*, size/small], ['colour/red',   'size/small']),
    #     ([colour/green, logo/*, size/small], ['colour/green', 'size/small']),
    #     ([colour/blue,  logo/*, size/small], ['colour/blue',  'size/small']),
    #     ([colour/red,   logo/*, size/medium], ['colour/red',   'size/medium']),
    #     ([colour/green, logo/*, size/medium], ['colour/green', 'size/medium']),
    #     ([colour/blue,  logo/*, size/medium], ['colour/blue',  'size/medium']),
    #     ([colour/red,   logo/*, size/big], ['colour/red',   'size/big']),
    #     ([colour/green, logo/*, size/big], ['colour/green', 'size/big']),
    #     ([colour/blue,  logo/*, size/big], ['colour/blue',  'size/big'])]

    # Note that from this point, we always work with sorted lists of
    # categories (or regex tokens).

    variation_list = ([], []),
    optional_variation_base_category_set = \
      set(resource.getOptionalVariationBaseCategoryList())
    for variation_base_category in sorted(
        resource.getVariationBaseCategoryList(omit_optional_variation=0)):
      if variation_base_category in measure_variation_base_category_list:
        # This is where we rebuild variation_list entirely. Size of
        # variation_list is multiplied by len(getVariationCategoryList).
        # The lists of each pairs in variation_list get one more element:
        # variation_category.
        variation_list = [(regex_list + [variation_category, '\n'],
                           variation_base_category_list + [variation_category])
          for regex_list, variation_base_category_list in variation_list
          for variation_category in resource.getVariationCategoryList(
            base_category_list=(variation_base_category,),
            omit_individual_variation=0)]
      else:
        variation_base_category_regex = variation_base_category + '/[^\n]+\n'
        if variation_base_category in optional_variation_base_category_set:
          variation_base_category_regex = \
            '(%s)*' % (variation_base_category_regex, )
        for regex_list, variation_base_category_list in variation_list:
          regex_list.append(variation_base_category_regex)

    # 2nd step: Retrieve all measure cells in a dictionary for fast lookup.
    cell_map = {}
    for cell in self.objectValues():
      cell_map[tuple(sorted(cell.getMembershipCriterionCategoryList()))] \
        = cell.getQuantity()

    # 3rd step: Build the list of rows to return,
    # by merging variation_list (1st step) and cell_map (2nd step).
    row_list = []
    for regex_list, variation_base_category_list in variation_list:
      cell = cell_map.get(tuple(variation_base_category_list))
      if cell is None:
        if quantity is None:
          continue
        cell = quantity
      row_list.append(dict(uid=uid,
                       resource_uid=resource_uid,
                       variation='^%s$' % ''.join(regex_list),
                       metric_type_uid=metric_type_uid,
                       quantity=cell * quantity_unit))

    return row_list
