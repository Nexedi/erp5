##############################################################################
#
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from testProductionOrder import TestProductionOrderMixin
import transaction

class TestTransformationMixin(TestProductionOrderMixin):
  """
  Mixin class for checking transformations
  """

  # Override, let TestProductionOrderMixin define the categories for us
  operation_category_list = ['sewing', 'packing']

  def createTransformation(self):
    module = self.getPortalObject().getDefaultModule(
        self.transformation_portal_type)
    transformation = module.newContent(portal_type=self.transformation_portal_type)
    return transformation

  def createTransformedResource(self, transformation=None):
    transformed_resource = transformation.newContent(
        portal_type=self.transformed_resource_portal_type)
    return transformed_resource

  def createComponent(self, variation_property_list=None):
    module = self.getPortalObject().getDefaultModule(self.component_portal_type)
    component = module.newContent(portal_type=self.component_portal_type)
    if variation_property_list is not None:
      component.setVariationPropertyList(variation_property_list)
    return component

  def createResource(self, title, variation_base_category_list,
      variation_category_list):
    portal = self.getPortal()
    resource_module = portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent(portal_type=self.resource_portal_type)
    resource.edit(
      title = title,
      variation_base_category_list = variation_base_category_list,
    )
    resource.setVariationCategoryList(variation_category_list)
    return resource

  size_category_list = ['size/' + q for q in TestProductionOrderMixin
      .mrp_size_list]
  colour_category_list = ['colour/' + q for q in TestProductionOrderMixin
      .colour_list]

  swimsuit_variation_base_category_list = ['size', 'colour']
  swimsuit_variation_category_list = size_category_list + colour_category_list
  fabric_variation_base_category_list = ['colour']
  fabric_variation_category_list = colour_category_list
  button_variation_base_category_list = ['size']
  button_variation_category_list = size_category_list

  def createButtonComponent(self):
    """
    Buttons, variated by size
    """
    resource = self.createComponent()
    resource.edit(
      title = "Round Button",
      variation_base_category_list = self.button_variation_base_category_list,
    )
    resource.setVariationCategoryList(self.button_variation_category_list)


class TestTransformation(TestTransformationMixin, ERP5TypeTestCase):

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base','erp5_pdm', 'erp5_trade', 'erp5_mrp',)

  def test_01_getAggregatedAmountListWithVariatedProperty(self):
    """
    Make sure that getAggregatedAmountList is still working properly if we
    have additionnals propertysheets on transformations lines and that used
    variation properties
    """
    # Only for testing purpose, use a property sheet that has nothing to
    # do with component. It would have been possible to create a new
    # property sheet for this test
    self._addPropertySheet(self.transformed_resource_portal_type, 'Bug')
    variation_property_list = ['tested']

    transformation = self.createTransformation()
    transformed_resource = self.createTransformedResource(transformation)
    component = self.createComponent(
        variation_property_list=variation_property_list)
    transformed_resource.edit(
        resource_value=component,
        quantity=1)
    transformed_resource.setTested(True)
    aggregated_amount_list = transformation.getAggregatedAmountList()
    self.assertEquals(len(aggregated_amount_list), 1)
    aggregated_amount = aggregated_amount_list[0]
    # Make sure that the isTested method is working properly on the
    # temp object
    self.assertTrue(aggregated_amount.isTested())

  def test_transformedInventory(self):
    portal = self.getPortal()

    swimsuit = self.createResource(
        'Swimming Suit',
        self.swimsuit_variation_base_category_list,
        self.swimsuit_variation_category_list,
    )
    transformation = self.createTransformation()
    transformation.edit(
        title = 'Swimsuit Production',
        variation_base_category_list = self.swimsuit_variation_base_category_list
    )
    transformation.setResourceValue(swimsuit)

    fabric = self.createResource(
        'Fabric',
        self.fabric_variation_base_category_list,
        self.fabric_variation_category_list,
    )
    fabric_line = self.createTransformedResource(transformation)
    fabric_line.setResourceValue(fabric)

    fabric_line.setVVariationBaseCategoryList(['colour'])
    for colour in self.colour_category_list:
      # For a blue swimming suit, we need blue fabric
      fabric_line.newCell(colour, category = colour, base_id = 'variation')

    fabric_line.setQVariationBaseCategoryList(['size'])
    for i, size in enumerate(self.size_category_list):
      # Depending on the size, the quantity of Fabric is different.
      # arbitrarily, we fix the quantity for size s as:
      # self.size_category_list.index(s) + 1
      fabric_line.newCell(size, quantity = i+1, base_id = 'quantity')

    button = self.createComponent()
    button.edit(
      title = 'Round Button',
      variation_base_category_list = self.button_variation_base_category_list,
    )
    button.setVariationCategoryList(self.button_variation_category_list)

    button_line = self.createTransformedResource(transformation)
    button_line.setResourceValue(button)

    button_line.setVVariationBaseCategoryList(['size'])
    for size in self.size_category_list:
      # The button used depends on the size
      button_line.newCell(size, category = size, base_id = 'variation')

    sewing_line = transformation.newContent(
        portal_type = self.operation_line_portal_type)
    sewing_line.setResourceValue(
        portal.portal_categories.resolveCategory('operation/sewing'))

    sewing_line.setQVariationBaseCategoryList(['size', 'colour'])
    i = 1
    for size in self.size_category_list:
      for colour in self.colour_category_list:
        sewing_line.newCell(size, colour, quantity = i, base_id = 'quantity')
        i += 1

    transaction.commit()
    self.tic()

    # Swimming Suit does not use ALL categories in Size category.
    # As a result, transformation lines should restrict their dimensions,
    # using the range induced by the resource, instead of naively
    # using the whole range directly from the variation categories.
    self.assertEqual(
        len(swimsuit.getVariationCategoryList(base_category_list=['size'])),
        len(fabric_line.getCellKeyList(base_id='quantity'))
    )

    # XXX (will be expanded)

  def test_resourceIsNotAcquiredOnTransformationLines(self):
    '''
    We don't want resource define on transformation to be acquired on
    transformation lines
    '''
    transformation = self.createTransformation()

    # create a product
    portal = self.getPortalObject()
    product_module = portal.getDefaultModule('Product')
    product = product_module.newContent(portal_type='Product')

    # set the product as resource of the transformations
    transformation.setResourceValue(product)

    # add transformations lines and check the don't acquire the resource
    operation = transformation.newContent(portal_type='Transformation Operation')
    self.assertEquals(operation.getResource(), None)

    optional_resource = transformation.newContent(portal_type=\
        'Transformation Optional Resource')
    self.assertEquals(optional_resource.getResource(), None)

    transformed_resource = transformation.newContent(portal_type=\
        'Transformation Transformed Resource')
    self.assertEquals(transformed_resource.getResource(), None)
