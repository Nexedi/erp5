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

from erp5.component.test.testProductionOrder import TestProductionOrderMixin
from Products.ERP5.tests.testInventoryAPI import BaseTestUnitConversion

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


class TestTransformation(TestTransformationMixin, BaseTestUnitConversion):
  QUANTITY_UNIT_DICT = {
    # base: (reference, dict_of_others)
    'mass':   ('kilogram', dict(gram=0.001)),
  }
  METRIC_TYPE_CATEGORY_LIST = (
    'mass/net',
  )

  def afterSetUp(self):
    TestTransformationMixin.afterSetUp(self)
    BaseTestUnitConversion.afterSetUp(self)

  def getBusinessTemplateList(self):
    """
    """
    return TestTransformationMixin.getBusinessTemplateList(self) + (
      'erp5_apparel', 'erp5_dummy_movement', 'erp5_project')

  def test_01_getAggregatedAmountListSimple(self):
    """
    Make sure that getAggregatedAmountList return something
    """
    transformation = self.createTransformation()
    transformed_resource = self.createTransformedResource(transformation)
    component = self.createComponent()
    transformed_resource.edit(
        resource_value=component,
        quantity=2)
    aggregated_amount_list = transformation.getAggregatedAmountList()
    self.assertEqual(len(aggregated_amount_list), 1)
    aggregated_amount = aggregated_amount_list[0]
    self.assertEqual(aggregated_amount.quantity, 2)

  def test_getAggregatedAmountListKeepOrder(self):
    """
    Make sure that getAggregatedAmountList return amounts in the same order as on the transformation
    """
    transformation = self.createTransformation()
    first_transformed_resource = self.createTransformedResource(transformation)
    first_component = self.createComponent()
    first_transformed_resource.edit(
        resource_value=first_component,
        int_index=1,
        quantity=1)
    second_transformed_resource = self.createTransformedResource(transformation)
    second_component = self.createComponent()
    second_transformed_resource.edit(
        resource_value=second_component,
        int_index=2,
        quantity=2)

    aggregated_amount_list = transformation.getAggregatedAmountList()
    self.assertEqual(
        [(a.getQuantity(), a.getResourceValue()) for a in aggregated_amount_list],
        [(1, first_component), (2, second_component)]
    )

  def test_01_getAggregatedAmountListWithVariatedProperty(self):
    """
    Make sure that getAggregatedAmountList is still working properly if we
    have additionnals propertysheets on transformations lines and that used
    variation properties
    """
    ps_id = self._testMethodName
    property_sheet = self.portal.portal_property_sheets.newContent(
      ps_id, portal_type='Property Sheet')
    property_sheet.newContent(portal_type='Standard Property',
                              reference='foo',
                              storage_id='bar',
                              elementary_type='boolean')
    # When one do that, the property sheet should be added to many other types
    # like movements, order lines and so on.
    self._addPropertySheet('Amount', ps_id)
    self._addPropertySheet(self.transformed_resource_portal_type, ps_id)
    # need to force accessor regeneration after portal type changes
    self.commit()

    transformation = self.createTransformation()
    transformed_resource = self.createTransformedResource(transformation)
    component = self.createComponent(variation_property_list=['foo'])
    transformed_resource.edit(
        resource_value=component,
        quantity=1)
    transformed_resource.setFoo(True)
    aggregated_amount, = transformation.getAggregatedAmountList()
    # Make sure that the isFoo method is working properly on the temp object
    self.assertTrue(aggregated_amount.isFoo())

    # XXX aborting a transaction should reset classes
    #     if they were reset during the transaction
    self.abort()
    self.getTypesTool().resetDynamicDocuments()

  def test_variationCategory(self):
    swimcap = self.createResource(
        'Swimming Cap',
        self.swimsuit_variation_base_category_list,
        self.swimsuit_variation_category_list,
    )
    transformation = self.createTransformation()
    transformation.edit(
        title = 'Swimcap Production',
        variation_base_category_list = self.swimsuit_variation_base_category_list
    )
    transformation.setResourceValue(swimcap)

    self.tic()
    self.assertSameSet(swimcap.getVariationCategoryList(),
                       transformation.getVariationCategoryList())

  def test_variationCategoryWithIndividualVariation(self):
    '''Check that individual variation are return when getVariationCategoryList
    is called on a transformation
    '''
    swimcap = self.createResource(
        'Swimming Cap',
        self.swimsuit_variation_base_category_list,
        self.swimsuit_variation_category_list,
    )
    # create individual variation
    individual_variation = swimcap.newContent(portal_type='Product Individual Variation')

    self.tic()
    transformation = self.createTransformation()
    transformation.setResourceValue(swimcap)

    transformation.edit(
        title = 'Swimcap Production',
        variation_base_category_list = \
            self.swimsuit_variation_base_category_list + ['variation',]
    )

    # check the individual variation is returned by the
    # getVariationCategoryList
    individual_url = 'variation/%s' % individual_variation.getRelativeUrl()
    self.assertTrue(individual_url in
        transformation.getVariationCategoryList())


  def test_transformedInventory(self):
    portal = self.getPortal()

    button_number = 3.0

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
    self.commit()

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
      fabric_line.newCell(colour,
                          categories = colour,
                          membership_criterion_base_category= ('colour',),
                          membership_criterion_category= (colour,),
                          base_id = 'variation')

    fabric_line.setQVariationBaseCategoryList(['size'])
    for i, size in enumerate(self.size_category_list):
      # Depending on the size, the quantity of Fabric is different.
      # arbitrarily, we fix the quantity for size s as:
      # self.size_category_list.index(s) + 1
      fabric_line.newCell(size,
                          quantity = i+1,
                          mapped_value_property_list = ('quantity',),
                          membership_criterion_base_category= ('size',),
                          membership_criterion_category= (size,),
                          base_id = 'quantity')

    button = self.createComponent()
    button.edit(
      title = 'Round Button',
      variation_base_category_list = self.button_variation_base_category_list,
    )
    button.setVariationCategoryList(self.button_variation_category_list)

    button_line = self.createTransformedResource(transformation)
    button_line.setResourceValue(button)
    button_line.setQuantity(button_number)

    button_line.setVVariationBaseCategoryList(['size'])
    for size in self.size_category_list:
      # The button used depends on the size
      button_line.newCell(size,
                          categories = size,
                          membership_criterion_base_category= ('size',),
                          membership_criterion_category= (size,),
                          base_id = 'variation')

    sewing_line = transformation.newContent(
        portal_type = self.operation_line_portal_type)
    sewing_line.setResourceValue(
        portal.portal_categories.resolveCategory('operation/sewing'))

    sewing_line.setQVariationBaseCategoryList(['size', 'colour'])
    i = 1
    for size in self.size_category_list:
      for colour in self.colour_category_list:
        sewing_line.newCell(size,
                            colour,
                            mapped_value_property_list = ('quantity',),
                            membership_criterion_base_category= ('size', 'colour'),
                            membership_criterion_category= (size, colour),
                            quantity = i,
                            base_id = 'quantity')
        i += 1

    self.tic()

    self.assertEqual(swimsuit.getDefaultTransformationValue().getRelativeUrl(),
                     transformation.getRelativeUrl())
    self.assertEqual(fabric.getDefaultTransformationValue(), None)
    self.assertEqual(button.getDefaultTransformationValue(), None)

    # Swimming Suit does not use ALL categories in Size category.
    # As a result, transformation lines should restrict their dimensions,
    # using the range induced by the resource, instead of naively
    # using the whole range directly from the variation categories.
    self.assertEqual(
        len(swimsuit.getVariationCategoryList(base_category_list=['size'])),
        len(fabric_line.getCellKeyList(base_id='quantity'))
    )

    swimsuit_quantity = 4.0
    n = 1
    # Check that getAggregatedAmount returns the expected results, a.k.a.
    # that our Transformation is set up correctly.
    for i, size in enumerate(self.size_category_list):
      for colour in self.colour_category_list:
        # id does not matter, just make it unique
        temp_amount = transformation.newContent(temp_object=True,
                                                portal_type='Amount',
                                                id="foo_%s_%s" % (size, colour))
        temp_amount.edit(
            quantity = swimsuit_quantity,
            variation_category_list = [size, colour],
            resource = swimsuit.getRelativeUrl(),
        )
        amount_list = transformation.getAggregatedAmountList(temp_amount)

        # fabric + button + sewing
        self.assertEqual(len(amount_list), 3)
        for amount in amount_list:
          resource = amount.getResource()
          if resource == fabric.getRelativeUrl():
            self.assertEqual(amount.getVariationCategoryList(), [colour])
            self.assertEqual(amount.getQuantity(), (i+1)*swimsuit_quantity)
          elif resource == button.getRelativeUrl():
            self.assertEqual(amount.getVariationCategoryList(), [size])
            self.assertEqual(amount.getQuantity(), button_number*swimsuit_quantity)
          elif resource == "operation/sewing":
            self.assertEqual(amount.getQuantity(), n*swimsuit_quantity)
          else:
            self.fail("Invalid Resource: %s" % resource)
        n += 1


    for size in self.size_category_list:
      for colour in self.colour_category_list:
        self.makeMovement(swimsuit_quantity, swimsuit, size, colour)

    self.tic()

    inv = self.getSimulationTool().getInventoryList(
            node_uid=self.node.getUid(),
            transformed_resource=[fabric.getRelativeUrl(),
                                  button.getRelativeUrl(),
                                  "operation/sewing"],
            )
    self.assertEqual(len(inv),
          len(transformation) * len(self.size_category_list) \
            * len(self.colour_category_list))

    self.assertEqual(len(self.getSimulationTool().getInventoryList(
            node_uid=self.node.getUid(),
            transformed_resource=[fabric.getRelativeUrl(),
                                  button.getRelativeUrl(),
                                  "operation/sewing"],
            variation_text="something_not_existing",
            )), 0)

    n = 1
    for i, size in enumerate(self.size_category_list):
      for colour in self.colour_category_list:
        variation_text = '\n'.join([colour, size])
        inv = self.getSimulationTool().getInventoryList(
                node_uid=self.mirror_node.getUid(),
                transformed_resource=[fabric.getRelativeUrl(),
                                      button.getRelativeUrl(),
                                      "operation/sewing"],
                variation_text=variation_text,
              )
        self.assertEqual(len(inv), len(transformation))
        for line in inv:
          self.assertEqual(line.getVariationText(), variation_text)
          self.assertEqual(line.getResource(), swimsuit.getRelativeUrl())
          transformed_resource = line.transformed_resource_relative_url
          if transformed_resource == fabric.getRelativeUrl():
            self.assertEqual(line.transformed_variation_text, colour)
            self.assertEqual(line.total_quantity, (i+1)*swimsuit_quantity)
          elif transformed_resource == button.getRelativeUrl():
            self.assertEqual(line.transformed_variation_text, size)
            self.assertEqual(line.total_quantity, button_number*swimsuit_quantity)
          elif transformed_resource == "operation/sewing":
            self.assertEqual(line.total_quantity, n*swimsuit_quantity)
            self.assertEqual(line.transformed_variation_text, "")
          else:
            self.fail("Invalid Transformed Resource: %s" % transformed_resource)
        n += 1


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
    self.assertEqual(operation.getResource(), None)

    optional_resource = transformation.newContent(portal_type=\
        'Transformation Optional Resource')
    self.assertEqual(optional_resource.getResource(), None)

    transformed_resource = transformation.newContent(portal_type=\
        'Transformation Transformed Resource')
    self.assertEqual(transformed_resource.getResource(), None)

def test_suite():
  import unittest
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTransformation))
  return suite
