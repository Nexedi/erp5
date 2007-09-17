##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
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

import unittest

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList


class TestResource(ERP5TypeTestCase):
  """
    Test ERP5 document Resource
  """
  run_all_test = 1

  # Global variables
  resource_portal_type = 'Apparel Model'
  product_portal_type = 'Product'
  node_portal_type = 'Organisation'
  sale_supply_portal_type = 'Sale Supply'
  sale_supply_line_portal_type = 'Sale Supply Line'
  sale_supply_cell_portal_type = 'Sale Supply Cell'
  supply_line_portal_type = 'Supply Line'
  supply_cell_portal_type = 'Supply Cell'
  variation_base_category_list = ['colour', 'size', 'morphology',
                                  'industrial_phase']
  size_list = ['size/Child','size/Man']
  variation_property_list = []

  def getBusinessTemplateList(self):
    """
      Install needed business template
    """
    # Trade is needeed for pricing
    return ('erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_apparel', )

  def getTitle(self):
    return "Resource"

  def enableLightInstall(self):
    """
    You can override this.
    Return if we should do a light install (1) or not (0)
    """
    return 1

  def enableActivityTool(self):
    """
    You can override this.
    Return if we should create (1) or not (0) an activity tool.
    """
    return 1

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('rc', '', ['Manager'], [])
    user = uf.getUserById('rc').__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    self.login()
    self.portal = self.getPortal()
    self.category_tool = self.getCategoryTool()
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_catalogClear()
    self.createCategories()

  def createCategories(self):
    """
      Light install create only base categories, so we create
      some categories for testing them
    """
    size_category_list = ['Baby', 'Child', 'Man', 'Woman']
    if len(self.category_tool.size.contentValues()) == 0 :
      for category_id in size_category_list:
        o = self.category_tool.size.newContent(portal_type='Category',
                                               id=category_id)
    self.size_category_list = map(lambda x: 'size/%s' % x,
                                  size_category_list)

    colour_category_list = ['blue', 'green']
    if len(self.category_tool.colour.contentValues()) == 0 :
      for category_id in colour_category_list:
        o = self.category_tool.colour.newContent(portal_type='Category',
                                               id=category_id)
    self.colour_category_list = map(lambda x: 'colour/%s' % x,
                                    colour_category_list)

    ind_phase_category_list = ['phase1', 'phase2']
    if len(self.category_tool.industrial_phase.contentValues()) == 0:
      for category_id in ind_phase_category_list:
        o = self.category_tool.industrial_phase.newContent(
                                               portal_type='Category',
                                               id=category_id)
    self.industrial_phase_category_list = map(
                                    lambda x: 'industrial_phase/%s' % x,
                                    ind_phase_category_list)

    self.morphology_category_list = []
    self.base_category_content_list = {
      'size':self.size_category_list,
      'colour':self.colour_category_list,
      'morphology':self.morphology_category_list,
      'industrial_phase':self.industrial_phase_category_list
    }

  def stepTic(self,**kw):
    self.tic()

  def stepCreateResource(self, sequence=None, sequence_list=None, **kw):
    """
      Create a resource without variation
    """
    resource_module = self.portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent( \
                                 portal_type=self.resource_portal_type)
    resource.edit(
      title = "Resource"
    )
    sequence.edit(resource=resource,
                  variation_property_list=[])
    self.category_list = []
    # Actually, resource has no individual variation
    for base_category in resource.getVariationBaseCategoryList():
      sequence.edit(**{base_category:None})

  def stepCheckGetVariationBaseCategoryList(self, sequence=None,
                                             sequence_list=None, **kw):
    """
      Check if getVariationBaseCategoryList returns the good result
    """
    resource = sequence.get('resource')
    vbcl = resource.getVariationBaseCategoryList()
    self.failIfDifferentSet(self.variation_base_category_list, vbcl)

  def stepCheckGetVariationRangeCategoryList(self, sequence=None,
                                             sequence_list=None, **kw):
    """
      Check if getVariationRangeCategoryList returns the good result
    """
    resource = sequence.get('resource')
    vbcl = resource.getVariationBaseCategoryList()
    correct_variation_range_category_list = []
    for base_category in vbcl:
      # Check if resource has individual variations
      individual_variation_list = sequence.get(base_category)
      if individual_variation_list is None:
        correct_variation_range_category_list.extend(
                               self.base_category_content_list[base_category])
      else:
        correct_variation_range_category_list.extend(individual_variation_list)

    vrcl = resource.getVariationRangeCategoryList()
    self.failIfDifferentSet(correct_variation_range_category_list, vrcl)

  def stepSetCategoryVariation(self, sequence=None, sequence_list=None, **kw):
    """
      Set category variation to current resource
    """
    resource = sequence.get('resource')
    size_list = map(lambda x: x[len('size/'):], self.size_list)
    resource.setSizeList(size_list)
    self.category_list = self.size_list[:]

  def stepSetIndividualVariationWithEmptyBase(self, sequence=None,
                                              sequence_list=None, **kw):
    """
      Set individual variation to current resource with empty base
      category
    """
    resource = sequence.get('resource')
    morphology_list = []
    morphology_variation_count = 2
    for i in range(morphology_variation_count) :
      variation_portal_type = 'Apparel Model Morphology Variation'
      variation = resource.newContent(portal_type=variation_portal_type)
      variation.edit(
        title = 'MorphologyVariation%s' % str(i)
      )
      morphology_list.append('morphology/%s' %
                                        variation.getRelativeUrl())
    # store individual resource
    sequence.edit(morphology=morphology_list)

  def stepSetIndividualVariationWithFillBase(self, sequence=None,
                                              sequence_list=None, **kw):
    """
      Set individual variation to current resource with fill base
      category
    """
    resource = sequence.get('resource')
    colour_list = []
    colour_variation_count = 1
    for i in range(colour_variation_count) :
      variation_portal_type = 'Apparel Model Colour Variation'
      variation = resource.newContent(portal_type=variation_portal_type)
      variation.edit(
        title = 'ColourVariation%s' % str(i)
      )
      colour_list.append('colour/%s' % variation.getRelativeUrl())
    # store individual resource
    sequence.edit(colour=colour_list)

  def test_01_getVariationBaseCategoryList(self, quiet=0, run=run_all_test):
    """
      Test the method getVariationBaseCategoryList on a resource.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when resource has no variation
    sequence_string = '\
                      CreateResource \
                      CheckGetVariationBaseCategoryList \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def genericTest(self, test_method_name):
    """
      Generic test on a resource.
    """
    sequence_list = SequenceList()
    # Test when resource has no variation
    sequence_string = '\
                      CreateResource \
                      %s \
                      ' % test_method_name
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has category variations
    sequence_string = '\
                      CreateResource \
                      SetCategoryVariation \
                      %s \
                      ' % test_method_name
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has individual variation and base category
    # has no content
    sequence_string = '\
                      CreateResource \
                      SetIndividualVariationWithEmptyBase \
                      Tic \
                      %s \
                      ' % test_method_name
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has individual variation and base category
    # has category content
    sequence_string = '\
                      CreateResource \
                      SetIndividualVariationWithFillBase \
                      Tic \
                      %s \
                      ' % test_method_name
    sequence_list.addSequenceString(sequence_string)
    # Test with all cases
    sequence_string = '\
                      CreateResource \
                      SetCategoryVariation \
                      SetIndividualVariationWithEmptyBase \
                      SetIndividualVariationWithFillBase \
                      Tic \
                      %s \
                      ' % test_method_name
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_02_getVariationRangeCategoryList(self, quiet=0, run=run_all_test):
    """
      Test the method getVariationRangeCategoryList on a resource.
    """
    if not run: return
    self.genericTest('CheckGetVariationRangeCategoryList')

  def stepCheckGetVariationRangeCategoryItemList(self, sequence=None,
                                                 sequence_list=None, **kw):
    """
      Check if getVariationRangeCategoryItemList returns the good result.
      Does not test display...
      Item are left display.
    """
    resource = sequence.get('resource')
    vrcl = resource.getVariationRangeCategoryList()
    vrcil = resource.getVariationRangeCategoryItemList()
    self.failIfDifferentSet(vrcl, map(lambda x: x[1], vrcil))

  def test_03_getVariationRangeCategoryItemList(self, quiet=0,
                                                run=run_all_test):
    """
      Test the method getVariationRangeCategoryItemList on a resource.
    """
    if not run: return
    self.genericTest('CheckGetVariationRangeCategoryItemList')

  def stepCheckGetVariationCategoryList(self, sequence=None,
                                                 sequence_list=None, **kw):
    """
      Check if getVariationCategoryList returns the good result,
      with parameter omit_individual_variation=1.
    """
    resource = sequence.get('resource')
    vcl = resource.getVariationCategoryList()
#    ZopeTestCase._print('\n')
#    ZopeTestCase._print('vcl: %s\n' % str(vcl))
    self.failIfDifferentSet(self.category_list, vcl)

  def test_04_getVariationCategoryList(self, quiet=0, run=run_all_test):
    """
      Test the method getVariationCategoryList on a resource.
    """
    if not run: return
    self.genericTest('CheckGetVariationCategoryList')

  def stepCheckGetVariationCategoryListWithoutOmit(self, sequence=None,
                                                 sequence_list=None, **kw):
    """
      Check if getVariationCategoryList returns the good result,
      with parameter omit_individual_variation=0.
    """
    resource = sequence.get('resource')
    vcl = resource.getVariationCategoryList(omit_individual_variation=0)
    correct_vcl = self.category_list[:]

    for base_category in resource.getVariationBaseCategoryList():
      # Check if resource has individual variations
      individual_variation_list = sequence.get(base_category)
      if individual_variation_list is not None:
        correct_vcl.extend(individual_variation_list)
    self.failIfDifferentSet(correct_vcl, vcl)

  def test_05_getVariationCategoryList(self, quiet=0, run=run_all_test):
    """
      Test the method getVariationCategoryList on a resource
      with parameter omit_individual_variation=0.
    """
    if not run: return
    self.genericTest('CheckGetVariationCategoryListWithoutOmit')

  def stepCheckGetVariationCategoryItemList(self, sequence=None,
                                                 sequence_list=None, **kw):
    """
      Check if getVariationCategoryItemList returns the good result,
      with parameter omit_individual_variation=1.
    """
    resource = sequence.get('resource')
    vcl = resource.getVariationCategoryList()
    vcil = resource.getVariationCategoryItemList()
    self.failIfDifferentSet(vcl, map(lambda x: x[1], vcil))

  def test_06_getVariationCategoryItemList(self, quiet=0, run=run_all_test):
    """
      Test the method getVariationCategoryItemList on a resource.
    """
    if not run: return
    self.genericTest('CheckGetVariationCategoryItemList')

  def stepCheckGetVariationCategoryItemListWithoutOmit(self, sequence=None,
                                                 sequence_list=None, **kw):
    """
      Check if getVariationCategoryItemList returns the good result,
      with parameter omit_individual_variation=0.
    """
    resource = sequence.get('resource')
    vcl = resource.getVariationCategoryList(omit_individual_variation=0)
    vcil = resource.getVariationCategoryItemList(omit_individual_variation=0)
    self.failIfDifferentSet(vcl, map(lambda x: x[1], vcil))

  def test_07_getVariationCategoryItemList(self, quiet=0, run=run_all_test):
    """
      Test the method getVariationCategoryItemList on a resource
      with parameter omit_individual_variation=0.
    """
    if not run: return
    self.genericTest('CheckGetVariationCategoryItemListWithoutOmit')

  def stepCheckGetVariationPropertyList(self, sequence=None,
                                        sequence_list=None, **kw):
    """
      Check if GetVariationPropertyList exists on a resource.
    """
    resource = sequence.get('resource')
    vpl = sequence.get('variation_property_list')
    self.failIfDifferentSet(resource.getVariationPropertyList(),
                            vpl)

  def stepCheckSetVariationPropertyList(self, sequence=None,
                                        sequence_list=None, **kw):
    """
      Check if SetVariationPropertyList exists on a resource.
      And test it.
    """
    resource = sequence.get('resource')
    vpl = ['prop1', 'prop2']
    sequence.edit(variation_property_list=vpl)
    resource.setVariationPropertyList(vpl)
    self.failIfDifferentSet(resource.variation_property_list,
                            vpl)

  def test_08_variationPropertyList(self, quiet=0, run=run_all_test):
    """
      Simply test if method are well generated by the property sheet.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when resource has no variation
    sequence_string = '\
                      CreateResource \
                      CheckGetVariationPropertyList \
                      CheckSetVariationPropertyList \
                      CheckGetVariationPropertyList \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def getPriceConfig(self):
    """
    Define somes cases of pricing configuration to test.
    """
    config = [
      {
        'base_price': None,
        'additional_price': None,
        'surcharge_ratio': None,
        'discount_ratio': None,
        'exclusive_discount_ratio': None,
        'price': None,
      },{
        'base_price': 5,
        'additional_price': None,
        'surcharge_ratio': None,
        'discount_ratio': None,
        'exclusive_discount_ratio': None,
        'price': 5,
      },{
        'base_price': 5,
        'additional_price': 1,
        'surcharge_ratio': None,
        'discount_ratio': None,
        'exclusive_discount_ratio': None,
        'price': 6,
      },{
        'base_price': 5,
        'additional_price': 3,
        'surcharge_ratio': 0.5,
        'discount_ratio': None,
        'exclusive_discount_ratio': None,
        'price': 12,
      },{
        'base_price': 5,
        'additional_price': 3,
        'surcharge_ratio': None,
        'discount_ratio': 0.25,
        'exclusive_discount_ratio': None,
        'price': 6,
      },{
        'base_price': 5,
        'additional_price': 3,
        'surcharge_ratio': None,
        'discount_ratio': None,
        'exclusive_discount_ratio': 0.5,
        'price': 4,
      },{
        'base_price': 5,
        'additional_price': 3,
        'surcharge_ratio': None,
        'discount_ratio': 0.5,
        'exclusive_discount_ratio': 0.75,
        'price': 2,
      },{
        'base_price': 5,
        'additional_price': 3,
        'surcharge_ratio': None,
        'discount_ratio': 0.75,
        'exclusive_discount_ratio': 0.25,
        'price': 2,
      },{
        'base_price': 5,
        'additional_price': 3,
        'surcharge_ratio': 1,
        'discount_ratio': 0.75,
        'exclusive_discount_ratio': 0.25,
        'price': 4,
      },{
        'base_price': None,
        'additional_price': 3,
        'surcharge_ratio': 1,
        'discount_ratio': 0.75,
        'exclusive_discount_ratio': 0.25,
        'price': None,
      }
    ]
    return config

  def logMessage(self, msg, tab=0):
    """
    Log a message.
    """
    if tab:
      msg = '  %s' % msg
    ZopeTestCase._print('\n%s' % msg)
    LOG('testResource.play', 0, msg)

  def test_09_getPrice(self, quiet=0, run=run_all_test):
    """
    Test the pricing model.
    """
    if not run: return
    config_list = self.getPriceConfig()
    for i in range(0, len(config_list)):
      self.logMessage("Starting New Pricing Case %i..." % i)
      config = config_list[i]
      # Create product
      self.logMessage("Creating product...", tab=1)
      product_module = self.portal.getDefaultModule(self.product_portal_type)
      product = product_module.newContent( \
                                   portal_type=self.product_portal_type,
                                   title='Product%i' % i)
      # Configure pricing parameters
      for key, value in config.items():
        if key != 'price':
          if value not in [None, []]:
            if type(value) != type([]):
              value_list = [value]
            else:
              value_list = value
            # Create requested supply line
            for pricing_param in value_list:
              self.logMessage("Creating supply line...", tab=1)
              supply_line = product.newContent(
                    portal_type=self.supply_line_portal_type)
              # Set pricing parameter
              self.logMessage("Set %s on supply line with value %s..." % \
                              (key, str(pricing_param)), tab=1)
              supply_line.setProperty(key, pricing_param)
      # Commit transaction
      self.logMessage("Commit transaction...", tab=1)
      get_transaction().commit()
      # Tic
      self.logMessage("Tic...", tab=1)
      self.tic()
      # Check resource price
      self.logMessage("Check product price...", tab=1)
      self.assertEquals(config['price'], product.getPrice())

  def test_10_getPriceWithOptions(self, quiet=0, run=run_all_test):
    """
    Test the pricing model on a resource with options.
    """
    if not run: return
    i = 1
    self.logMessage("Starting New Option Pricing Case %i..." % i)
    # Create another product/supply, in order to be sure that the
    # nothing will be generated from this supply!
    self.logMessage("Creating fake product...", tab=1)
    product_module = self.portal.getDefaultModule(self.product_portal_type)
    product = product_module.newContent( \
                                 portal_type=self.product_portal_type,
                                 title='FakeProduct%i' % i)
    product.setVariationCategoryList(self.industrial_phase_category_list)
    self.logMessage("Creating supply line...", tab=1)
    supply_line = product.newContent(
          portal_type=self.supply_line_portal_type)
    supply_line.setProperty('base_price', 100)
    supply_line.setSurchargeRatioQuantityStepList([])
    supply_line.getCellKeyList(base_id='path_optional_surcharge_ratio')
    cell1 = supply_line.newCell('industrial_phase/phase1',
        base_id='path_optional_surcharge_ratio', 
        portal_type=self.supply_cell_portal_type)
    cell1.setSurchargeRatio(20)
    cell1.setMappedValuePropertyList(["surcharge_ratio"])
    cell1.setMembershipCriterionBaseCategory('industrial_phase')
    cell1.setMembershipCriterionCategory('industrial_phase/phase1')
    # Create product
    self.logMessage("Creating product...", tab=1)
    product_module = self.portal.getDefaultModule(self.product_portal_type)
    product = product_module.newContent( \
                                 portal_type=self.product_portal_type,
                                 title='Product%i' % i)
    # Select some options on the resource
    product.setVariationCategoryList(self.industrial_phase_category_list)
    # Create requested supply line
    self.logMessage("Creating supply line...", tab=1)
    supply_line = product.newContent(
          portal_type=self.supply_line_portal_type)
    # Set pricing parameter
    supply_line.setProperty('base_price', 1)
    # Define the additional price matrix range
    supply_line.setAdditionalPriceQuantityStepList([])
    supply_line.getCellKeyList(base_id='path_optional_additional_price')
    cell1 = supply_line.newCell('industrial_phase/phase1',
        base_id='path_optional_additional_price', 
        portal_type=self.supply_cell_portal_type)
    cell1.setAdditionalPrice(2)
    cell1.setMappedValuePropertyList(["additional_price"])
    cell1.setMembershipCriterionBaseCategory('industrial_phase')
    cell1.setMembershipCriterionCategory('industrial_phase/phase1')
    cell2 = supply_line.newCell('industrial_phase/phase2',
        base_id='path_optional_additional_price', 
        portal_type=self.supply_cell_portal_type)
    cell2.setAdditionalPrice(7)
    cell2.setMappedValuePropertyList(["additional_price"])
    cell2.setMembershipCriterionBaseCategory('industrial_phase')
    cell2.setMembershipCriterionCategory('industrial_phase/phase2')
    # Commit transaction
    self.logMessage("Commit transaction...", tab=1)
    get_transaction().commit()
    # Tic
    self.logMessage("Tic...", tab=1)
    self.tic()
    # Check resource price
    self.logMessage("Check product price without option...", tab=1)
    self.assertEquals(1, product.getPrice(context=supply_line))
    # Check resource option price
    self.logMessage("Check product price with option: %s..." % \
                    'industrial_phase/phase1', tab=1)
    self.assertEquals(3, product.getPrice(
                                   categories=['industrial_phase/phase1']))
    self.logMessage("Check product price with option: %s..." % \
                    'industrial_phase/phase2', tab=1)
    self.assertEquals(8, product.getPrice(
                                   categories=['industrial_phase/phase2']))
    self.logMessage("Check product price with options: %s..." % \
                    'industrial_phase/phase1 industrial_phase/phase2', tab=1)
    self.assertEquals(10, product.getPrice(
                                   categories=['industrial_phase/phase1',
                                               'industrial_phase/phase2']))

  def test_11_getPriceWithDestination(self, quiet=0, run=run_all_test):
    """
    Test the pricing model with multiple price for 
    differents destinations.
    """
    if not run: return
    # Initialize variables
    test_case_list = []
    # Create product
    product_module = self.portal.getDefaultModule(self.product_portal_type)
    supply_module = self.portal.getDefaultModule(self.sale_supply_portal_type)
    currency_module = self.portal.getDefaultModule("Currency")
    currency = currency_module.newContent(
                     portal_type="Currency",
                     title='A great currency')
    # Create generic supply
    self.logMessage("Creating generic fake supply ...", tab=1)
    generic_supply = supply_module.newContent(
                     portal_type=self.sale_supply_portal_type,
                     title='FakeGenericSupply',
                     price_currency_value=currency)
    # Create empty supply line
    supply_line = generic_supply.newContent(
          portal_type=self.sale_supply_line_portal_type)
    supply_line.setProperty('base_price', 0)
    for j in range(33, 35):
      self.logMessage("Creating fake product %s..." % j, tab=1)
      product = product_module.newContent(
                           portal_type=self.product_portal_type,
                           title='AnotherFakeProduct%s' % j)
      # Create some nodes
      node_module = self.portal.getDefaultModule(self.node_portal_type)
      for i in range(11, 14):
        self.logMessage("Creating fake node %s..." % i, tab=1)
        node = node_module.newContent(
                       portal_type=self.node_portal_type,
                       title='FakeNode%s%s' % (j, i))
        # Create a supply
        self.logMessage("Creating fake supply %s..." % i, tab=1)
        supply = supply_module.newContent(
                                     portal_type=self.sale_supply_portal_type,
                                     title='FakeSupply%s' % i,
                                     price_currency_value=currency,
                                     destination_value=node)
        self.logMessage("Creating fake supply line %s..." % i, tab=1)
        supply_line = supply.newContent(
              portal_type=self.sale_supply_line_portal_type,
              resource_value=product)
        # Set pricing parameter
        base_price = i*j
        supply_line.setProperty('base_price', base_price)
        # Register the case
        test_case_list.append((product, node, base_price))
      # Create generic supply line
      self.logMessage("Creating generic fake supply line ...", tab=1)
      supply_line = generic_supply.newContent(
            portal_type=self.sale_supply_line_portal_type,
            resource_value=product)
      supply_line.setProperty('base_price', j)
      test_case_list.append((product, None, j))
    # Commit transaction
    self.logMessage("Commit transaction...", tab=1)
    get_transaction().commit()
    # Tic
    self.logMessage("Tic...", tab=1)
    self.tic()
    # Test the cases
    for product, node, base_price in test_case_list:
      if node is not None:
        self.logMessage("Check product %s with destination %s" % \
                        (product.getTitle(), node.getTitle()),
                        tab=1)
        self.assertEquals(base_price, 
                          product.getPrice(
                        categories=['destination/%s' % node.getRelativeUrl()]))
      else:
        self.logMessage("Check product %s without destination" % \
                        product.getTitle(),
                        tab=1)
        self.assertEquals(base_price, 
                          product.getPrice())
  
  def testQuantityPrecision(self):
    """test how to define quantity precision on resources.
    """
    resource = self.portal.getDefaultModule(self.product_portal_type)\
                .newContent(portal_type=self.product_portal_type)
    # default is 1
    self.assertEquals(1, resource.getBaseUnitQuantity())
    self.assertEquals(0, resource.getQuantityPrecision())
    # quantity precision is calculated using base quantity unit
    resource.setBaseUnitQuantity(0.001)
    self.assertEquals(3, resource.getQuantityPrecision())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestResource))
  return suite
