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

import random, unittest
from unittest import expectedFailure
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from DateTime import DateTime

class TestResource(ERP5TypeTestCase):
  """
    Test ERP5 document Resource
  """
  run_all_test = 1
  quiet = 0

  # Global variables
  resource_portal_type = 'Apparel Model'
  product_portal_type = 'Product'
  node_portal_type = 'Organisation'
  sale_supply_portal_type = 'Sale Supply'
  sale_order_line_portal_type = 'Sale Order Line'
  sale_supply_line_portal_type = 'Sale Supply Line'
  purchase_supply_line_portal_type = 'Purchase Supply Line'
  internal_supply_line_portal_type = 'Internal Supply Line'
  sale_supply_cell_portal_type = 'Sale Supply Cell'
  variation_base_category_list = ['size', 'industrial_phase', 'colour',
                                  'morphology']
  size_list = ['size/Child','size/Man']
  variation_property_list = []

  def getBusinessTemplateList(self):
    """
      Install needed business template
    """
    # Trade is needeed for pricing
    return ('erp5_base', 'erp5_pdm', 'erp5_simulation', 'erp5_trade',
            'erp5_configurator_standard_trade_template',
            'erp5_configurator_standard_solver',
            'erp5_apparel', 'erp5_simulation_test')

  def getTitle(self):
    return "Resource"

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('rc', '', ['Manager'], [])
    user = uf.getUserById('rc').__of__(uf)
    newSecurityManager(None, user)

  def setUpPreferences(self):
    #create apparel variation preferences
    portal_preferences = self.getPreferenceTool()
    preference = getattr(portal_preferences, 'test_site_preference', None)
    if preference is None:
      preference = portal_preferences.newContent(portal_type='System Preference',
                                title='Default Site Preference',
                                id='test_site_preference')
      if preference.getPreferenceState() == 'disabled':
        preference.enable()

    preference.setPreferredApparelModelVariationBaseCategoryList(('size', 'industrial_phase',))
    preference.setPreferredApparelClothVariationBaseCategoryList(('size',))
    preference.setPreferredApparelComponentVariationBaseCategoryList(('variation',))
    preference.setPreferredApparelModelIndividualVariationBaseCategoryList(('colour', 'morphology'))
    if preference.getPreferenceState() == 'disabled':
      preference.enable()
    self.tic()

  def afterSetUp(self):
    self.login()
    self.portal = self.getPortal()
    self.category_tool = self.getCategoryTool()
    self.createCategories()
    self.setUpPreferences()

  def beforeTearDown(self):
    self.abort()
    for folder in (
          self.portal.getDefaultModule(self.resource_portal_type),
          self.portal.getDefaultModule(self.sale_supply_portal_type),
          self.portal.getDefaultModule("Currency"),
          self.portal.getDefaultModule(self.node_portal_type),
          self.portal.getDefaultModule("Sale Order"),
          self.portal.getDefaultModule("Purchase Order"),):
      folder.manage_delObjects([i for i in folder.objectIds()])
    self.tic()

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

    quantity_unit_weight = self.portal.portal_categories.quantity_unit._getOb(
                                        'weight', None)
    if quantity_unit_weight is None:
      quantity_unit_weight = self.portal.portal_categories.quantity_unit\
                                  .newContent(id='weight',
                                              portal_type='Category')
    self.quantity_unit_gram = quantity_unit_weight._getOb('gram', None)
    if self.quantity_unit_gram is None:
      self.quantity_unit_gram = quantity_unit_weight.newContent(
                                      portal_type='Category',
                                      id='gram')
    self.quantity_unit_kilo = quantity_unit_weight._getOb('kilo', None)
    if self.quantity_unit_kilo is None:
      self.quantity_unit_kilo = quantity_unit_weight.newContent(
                                      portal_type='Category',
                                      id='kilo')

    unit_conversion_module = self.portal.quantity_unit_conversion_module
    weight_group = unit_conversion_module._getOb('weight', None)
    if weight_group is None:
      weight_group = unit_conversion_module.newContent(id='weight',
                                  portal_type='Quantity Unit Conversion Group',
                                  quantity_unit='weight/kilo')
      weight_group.validate()

    gram_definition = weight_group._getOb('gram', None)
    if gram_definition is None:
      gram_definition = weight_group.newContent(id='gram',
                              portal_type='Quantity Unit Conversion Definition',
                              quantity_unit='weight/gram',
                              quantity=0.001)
      gram_definition.validate()

    # create some product line categories
    product_line = self.portal.portal_categories.product_line
    if product_line._getOb('a', None) is None:
      product_line.newContent(
          id='a',
          portal_type='Category')
      product_line.a.newContent(
          id='a1',
          portal_type='Category')
    if product_line._getOb('b', None) is None:
      product_line.newContent(
          id='b',
          portal_type='Category')

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
    Set the individual variation of the current resource to a base category
    that contains no subobjects.
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
    Set the individual variation of the current resource to a base category
    that contains some subobjects.
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

  def test_01_getVariationBaseCategoryList(self, quiet=quiet, run=run_all_test):
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
    sequence_list.play(self, quiet=quiet)

  def genericTest(self, test_method_name, quiet=quiet):
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
    sequence_list.play(self, quiet=quiet)

  def test_02_getVariationRangeCategoryList(self, quiet=quiet, run=run_all_test):
    """
      Test the method getVariationRangeCategoryList on a resource.
    """
    if not run: return
    self.genericTest('CheckGetVariationRangeCategoryList', quiet=quiet)

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

  def test_03_getVariationRangeCategoryItemList(self, quiet=quiet,
                                                run=run_all_test):
    """
      Test the method getVariationRangeCategoryItemList on a resource.
    """
    if not run: return
    self.genericTest('CheckGetVariationRangeCategoryItemList', quiet=quiet)

  def stepCheckGetVariationCategoryList(self, sequence=None,
                                                 sequence_list=None, **kw):
    """
    Check if getVariationCategoryList returns the good result, with default
    value for omit_individual_variation parameter
    """
    resource = sequence.get('resource')
    vcl = resource.getVariationCategoryList()
    self.failIfDifferentSet(self.category_list, vcl)

  def test_04_getVariationCategoryList(self, quiet=quiet, run=run_all_test):
    """
      Test the method getVariationCategoryList on a resource.
    """
    if not run: return
    self.genericTest('CheckGetVariationCategoryList', quiet=quiet)

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

  def test_05_getVariationCategoryList(self, quiet=quiet, run=run_all_test):
    """
      Test the method getVariationCategoryList on a resource
      with parameter omit_individual_variation=0.
    """
    if not run: return
    self.genericTest('CheckGetVariationCategoryListWithoutOmit', quiet)

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

  def test_06_getVariationCategoryItemList(self, quiet=quiet, run=run_all_test):
    """
      Test the method getVariationCategoryItemList on a resource.
    """
    if not run: return
    self.genericTest('CheckGetVariationCategoryItemList', quiet)

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

  def test_07_getVariationCategoryItemList(self, quiet=quiet, run=run_all_test):
    """
      Test the method getVariationCategoryItemList on a resource
      with parameter omit_individual_variation=0.
    """
    if not run: return
    self.genericTest('CheckGetVariationCategoryItemListWithoutOmit',
        quiet=quiet)

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

  def test_08_variationPropertyList(self, quiet=quiet, run=run_all_test):
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
    sequence_list.play(self, quiet=quiet)

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
    if self.quiet:
      return
    if tab:
      msg = '  %s' % msg
    ZopeTestCase._print('\n%s' % msg)
    LOG('testResource.play', 0, msg)

  def test_09_getPrice(self, quiet=quiet, run=run_all_test):
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
                    portal_type=self.sale_supply_line_portal_type)
              # Set pricing parameter
              self.logMessage("Set %s on supply line with value %s..." % \
                              (key, str(pricing_param)), tab=1)
              supply_line.setProperty(key, pricing_param)
      # Commit transaction
      self.logMessage("Commit transaction...", tab=1)
      self.commit()
      # Tic
      self.logMessage("Tic...", tab=1)
      self.tic()
      # Check resource price
      self.logMessage("Check product price...", tab=1)
      self.assertEqual(config['price'], product.getPrice())

  def test_10_getPriceWithOptions(self, quiet=quiet, run=run_all_test):
    """
    Test the pricing model on a resource with options.
    """
    if not run: return
    i = 1
    self.logMessage("Starting New Option Pricing Case %i..." % i)
    # Fill the PDM preferences
    preference = self.portal.portal_preferences.default_site_preference
    preference.setPreferredProductOptionalVariationBaseCategoryList(['industrial_phase'])
    if preference.getPreferenceState() == 'disabled':
      preference.enable()
    self.tic()
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
          portal_type=self.sale_supply_line_portal_type)
    supply_line.setProperty('base_price', 100)
    supply_line.setSurchargeRatioQuantityStepList([])
    supply_line.getCellKeyList(base_id='path_optional_surcharge_ratio')
    cell1 = supply_line.newCell('industrial_phase/phase1',
        base_id='path_optional_surcharge_ratio',
        portal_type=self.sale_supply_cell_portal_type)
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
          portal_type=self.sale_supply_line_portal_type)
    # Set pricing parameter
    supply_line.setProperty('base_price', 1)
    # Define the additional price matrix range
    supply_line.setAdditionalPriceQuantityStepList([])
    supply_line.getCellKeyList(base_id='path_optional_additional_price')
    cell1 = supply_line.newCell('industrial_phase/phase1',
        base_id='path_optional_additional_price',
        portal_type=self.sale_supply_cell_portal_type)
    cell1.setAdditionalPrice(2)
    cell1.setMappedValuePropertyList(["additional_price"])
    cell1.setMembershipCriterionBaseCategory('industrial_phase')
    cell1.setMembershipCriterionCategory('industrial_phase/phase1')
    cell2 = supply_line.newCell('industrial_phase/phase2',
        base_id='path_optional_additional_price',
        portal_type=self.sale_supply_cell_portal_type)
    cell2.setAdditionalPrice(7)
    cell2.setMappedValuePropertyList(["additional_price"])
    cell2.setMembershipCriterionBaseCategory('industrial_phase')
    cell2.setMembershipCriterionCategory('industrial_phase/phase2')
    # Commit transaction
    self.logMessage("Commit transaction...", tab=1)
    self.commit()
    # Tic
    self.logMessage("Tic...", tab=1)
    self.tic()
    # Check resource price
    self.logMessage("Check product price without option...", tab=1)
    self.assertEqual(1, product.getPrice(context=supply_line))
    # Check resource option price
    self.logMessage("Check product price with option: %s..." % \
                    'industrial_phase/phase1', tab=1)
    self.assertEqual(3, product.getPrice(
                                   categories=['industrial_phase/phase1']))
    self.logMessage("Check product price with option: %s..." % \
                    'industrial_phase/phase2', tab=1)
    self.assertEqual(8, product.getPrice(
                                   categories=['industrial_phase/phase2']))
    self.logMessage("Check product price with options: %s..." % \
                    'industrial_phase/phase1 industrial_phase/phase2', tab=1)
    self.assertEqual(10, product.getPrice(
                                   categories=['industrial_phase/phase1',
                                               'industrial_phase/phase2']))

  def test_11_getPriceWithDestinationSection(self, quiet=quiet, run=run_all_test):
    """
    Test the pricing model with multiple price for
    differents destination sections.
    """
    if not run: return
    # Initialize variables
    test_case_list = []
    # Create product
    product_module = self.portal.getDefaultModule(self.product_portal_type)
    supply_module = self.portal.getDefaultModule(self.sale_supply_portal_type)
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
                                     destination_section_value=node)
        supply.validate()
        self.logMessage("Creating fake supply line %s..." % i, tab=1)
        supply_line = supply.newContent(
              portal_type=self.sale_supply_line_portal_type,
              resource_value=product)
        # Set pricing parameter
        base_price = i*j
        supply_line.setProperty('base_price', base_price)
        # Register the case
        test_case_list.append((product, node, base_price))
    # Commit transaction
    self.logMessage("Commit transaction...", tab=1)
    self.commit()
    # Tic
    self.logMessage("Tic...", tab=1)
    self.tic()
    # Test the cases
    for product, node, base_price in test_case_list:
      self.logMessage("Check product %s with destination section %s" % \
                      (product.getTitle(), node.getTitle()),
                      tab=1)
      self.assertEqual(base_price,
                        product.getPrice(
                  categories=['destination_section/%s' % node.getRelativeUrl()]))

  def test_11b_getPriceWithCells(self, quiet=quiet, run=run_all_test):
    """
    Test the pricing model with multiple price for
    differents destination sections, using supply cells
    """
    if not run: return
    # Initialize variables
    test_case_list = []
    # Create product
    product_module = self.portal.getDefaultModule(self.product_portal_type)
    supply_module = self.portal.getDefaultModule(self.sale_supply_portal_type)
    # Create generic supply
    self.logMessage("Creating generic fake supply ...", tab=1)
    generic_supply = supply_module.newContent(
                     portal_type=self.sale_supply_portal_type,
                     title='FakeGenericSupply',)
    generic_supply.validate()
    # Create empty supply line
    supply_line = generic_supply.newContent(
          portal_type=self.sale_supply_line_portal_type)
    supply_line.setProperty('base_price', 0)
    for j in range(33, 35):
      self.logMessage("Creating fake product %s..." % j, tab=1)
      product = product_module.newContent(
                           portal_type=self.product_portal_type,
                           title='AnotherFakeProduct%s' % j)
      product.setVariationBaseCategoryList(['size'])
      product.setVariationCategoryList(['size/Baby', 'size/Man'])
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
                                     destination_section_value=node)
        supply.validate()

        if 0:
          # XXX if both a supply line for the resource and a supply cell for
          # the resource with the exact variation can be applied, one of them
          # is choosen randomly. It looks like a bug, but I'm not sure we
          # should handle such situation.
          self.logMessage("Creating wrong supply line %s..." % i, tab=1)
          wrong_supply_line = supply.newContent(
                portal_type=self.sale_supply_line_portal_type,
                resource_value=product)
          wrong_supply_line.setBasePrice(12454326)

        self.logMessage("Creating fake supply line %s..." % i, tab=1)
        supply_line = supply.newContent(
              portal_type=self.sale_supply_line_portal_type,
              resource_value=product)
        supply_line.setPVariationBaseCategoryList(['size'])
        supply_line.updateCellRange(base_id='path')

        baby_cell = supply_line.newCell('size/Baby',
                           portal_type=self.sale_supply_cell_portal_type)
        baby_cell.setVariationCategoryList(['size/Baby'])
        baby_cell.setPredicateCategoryList(['size/Baby'])
        baby_cell.setMappedValuePropertyList(['base_price'])
        baby_cell.setMembershipCriterionBaseCategory('size')
        baby_cell.setMembershipCriterionCategory('size/Baby')
        base_price = i*j
        baby_cell.setProperty('base_price', base_price)
        # Register the case
        test_case_list.append((product, 'size/Baby', node, base_price))

        man_cell = supply_line.newCell('size/Man',
                        portal_type=self.sale_supply_cell_portal_type)
        man_cell.setVariationCategoryList(['size/Man'])
        man_cell.setPredicateCategoryList(['size/Man'])
        man_cell.setMappedValuePropertyList(['base_price'])
        man_cell.setMembershipCriterionBaseCategory('size')
        man_cell.setMembershipCriterionCategory('size/Man')
        base_price = i*j+3
        man_cell.setProperty('base_price', base_price)
        # Register the case
        test_case_list.append((product, 'size/Man', node, base_price))

      # Create generic supply line
      self.logMessage("Creating generic fake supply line ...", tab=1)
      supply_line = generic_supply.newContent(
            portal_type=self.sale_supply_line_portal_type,
            resource_value=product)
      supply_line.setProperty('base_price', j)
      test_case_list.append((product, None, None, j))

    # Commit transaction
    self.logMessage("Commit transaction...", tab=1)
    self.commit()
    # Tic
    self.logMessage("Tic...", tab=1)
    self.tic()
    # Test the cases
    for product, variation, node, base_price in test_case_list:
      categories = []
      if node is not None:
        self.logMessage("Check product %s with destination section %s" % \
                        (product.getTitle(), node.getTitle()),
                        tab=1)
        categories.append('destination_section/' + node.getRelativeUrl())
      else:
        self.logMessage("Check product %s without destination section" % \
                        product.getTitle(),
                        tab=1)
      if variation:
        categories.append(variation)

      def sort_key(supply_line):
        return (
          # same as in Resource._pricingSortKeyMethod
          not supply_line.getDestinationSection(),
          ###
          # now sort based on resource definition
          supply_line.getResourceValue() is None,
          # and make sure this is enough
          random.random(),
        )

      self.assertEqual(base_price, product.getPrice(categories=categories,
                                                    sort_key_method=sort_key))


  # The following test tests Movement.getPrice, which is based on the movement
  # context.

  def test_12_getInternalVsPurchaseVsSalePrice(self, quiet=quiet, run=run_all_test):
    """
    Test the pricing model with internal, purchase and sale supply
    lines, and with source_section/destination_section.
    """
    if not run: return
    # Initialize variables
    product_module = self.portal.getDefaultModule(self.product_portal_type)
    organisation_module = self.getOrganisationModule()
    currency_module = self.getCurrencyModule()
    sale_order_module = self.portal.getDefaultModule("Sale Order")
    purchase_order_module = self.portal.getDefaultModule("Purchase Order")
    internal_packing_list_module = self.portal.getDefaultModule("Internal Packing List")
    # Create product
    product = product_module.newContent(
        portal_type=self.product_portal_type,
        title="yet another product")
    # Create organisations
    orga1 = organisation_module.newContent(
        portal_type="Organisation",
        title="orga1")
    orga2 = organisation_module.newContent(
        portal_type="Organisation",
        title="orga2")
    # Create sale supply lines
    product.newContent(
        portal_type=self.sale_supply_line_portal_type,
        base_price=100.0,
        destination_section_value=orga1)
    product.newContent(
        portal_type=self.sale_supply_line_portal_type,
        base_price=200.0,
        destination_section_value=orga2)
    product.newContent(
        portal_type=self.sale_supply_line_portal_type,
        base_price=400.0)
    # Create purchase supply lines
    product.newContent(
        portal_type=self.purchase_supply_line_portal_type,
        base_price=10.0,
        source_section_value=orga1)
    product.newContent(
        portal_type=self.purchase_supply_line_portal_type,
        base_price=20.0,
        source_section_value=orga2)
    product.newContent(
        portal_type=self.purchase_supply_line_portal_type,
        base_price=40.0)
    # Create internal supply lines
    product.newContent(
        portal_type=self.internal_supply_line_portal_type,
        base_price=1.0,
        destination_section_value=orga1)
    product.newContent(
        portal_type=self.internal_supply_line_portal_type,
        base_price=2.0,
        destination_section_value=orga2)
    product.newContent(
        portal_type=self.internal_supply_line_portal_type,
        base_price=4.0)
    # Create sale order and check price
    sale_order = sale_order_module.newContent(
        portal_type="Sale Order",
        start_date=DateTime(),
        stop_date=DateTime())
    sale_order_line = sale_order.newContent(
        portal_type=self.sale_order_line_portal_type,
        resource_value=product)
    self.tic()
    self.assertEqual(sale_order_line.getPrice(), 400.0)
    sale_order.setDestinationSectionValue(orga2)
    self.tic()
    sale_order_line.setPrice(None)
    self.assertEqual(sale_order_line.getPrice(), 200.0)
    # Create purchase order and check price
    purchase_order = purchase_order_module.newContent(
        portal_type="Purchase Order",
        start_date=DateTime(),
        stop_date=DateTime())
    purchase_order_line = purchase_order.newContent(
        portal_type="Purchase Order Line",
        resource_value=product)
    self.tic()
    self.assertEqual(purchase_order_line.getPrice(), 40.0)
    purchase_order.setSourceSectionValue(orga2)
    self.tic()
    purchase_order_line.setPrice(None)
    self.assertEqual(purchase_order_line.getPrice(), 20.0)
    # Create internal packing list and check price
    internal_packing_list = internal_packing_list_module.newContent(
        portal_type="Internal Packing List",
        start_date=DateTime(),
        stop_date=DateTime())
    internal_packing_list_line = internal_packing_list.newContent(
        portal_type="Internal Packing List Line",
        resource_value=product)
    self.tic()
    self.assertEqual(internal_packing_list_line.getPrice(), 4.0)
    internal_packing_list.setDestinationSectionValue(orga2)
    self.tic()
    internal_packing_list_line.setPrice(None)
    self.assertEqual(internal_packing_list_line.getPrice(), 2.0)

  def testGetPriceWithQuantityUnit(self):
    resource = self.portal.getDefaultModule(self.product_portal_type)\
                .newContent(portal_type=self.product_portal_type)
    resource.setDefaultQuantityUnitValue(self.quantity_unit_kilo)
    supply_line = resource.newContent(
                    portal_type=self.sale_supply_line_portal_type)
    supply_line.setBasePrice(1000)
    self.tic()
    sale_order = self.portal.getDefaultModule("Sale Order").newContent(
                              portal_type='Sale Order',)
    sale_order_line = sale_order.newContent(
                          portal_type=self.sale_order_line_portal_type,
                          resource_value=resource,
                          quantity=5)
    self.assertEqual(1000, sale_order_line.getPrice())
    self.assertEqual(5000, sale_order_line.getTotalPrice())

    # if we give the quantity unit in grams
    sale_order_line = sale_order.newContent(
                          portal_type=self.sale_order_line_portal_type,
                          resource_value=resource,
                          quantity=5000,
                          quantity_unit_value=self.quantity_unit_gram)
    self.assertEqual(1, sale_order_line.getPrice())
    self.assertEqual(5000, sale_order_line.getTotalPrice())

  def testGetPriceWithPriceCurrency(self):
    currency_module = self.portal.getDefaultModule("Currency")
    currency = currency_module.newContent(
                     portal_type="Currency",
                     title='A great currency')
    other_currency = currency_module.newContent(
                     portal_type="Currency",
                     title='Another currency')

    resource = self.portal.getDefaultModule(self.product_portal_type)\
                .newContent(portal_type=self.product_portal_type)
    resource.setDefaultQuantityUnitValue(self.quantity_unit_kilo)
    supply_line = resource.newContent(
                    portal_type=self.sale_supply_line_portal_type)
    supply_line.setBasePrice(1000)
    supply_line.setPriceCurrencyValue(currency)
    self.tic()
    sale_order = self.portal.getDefaultModule("Sale Order").newContent(
                              portal_type='Sale Order',
                              price_currency_value=other_currency)
    sale_order_line = sale_order.newContent(
                          portal_type=self.sale_order_line_portal_type,
                          resource_value=resource,
                          quantity=5)
    # order and supply lines uses different currency, price does not apply
    self.assertEqual(None, sale_order_line.getPrice())

    # set the same currency
    sale_order.setPriceCurrencyValue(currency)

    # price applies
    self.assertEqual(1000, sale_order_line.getPrice())
    self.assertEqual(5000, sale_order_line.getTotalPrice())

  def testGetPriceProductLine(self):
    """Test supply line set for a product line.
    """
    # This supply line defines a price applicable for all resources member
    # of product line a
    supply = self.portal.getDefaultModule(self.sale_supply_portal_type).newContent(
                     portal_type=self.sale_supply_portal_type)
    supply_line = supply.newContent(portal_type=self.sale_supply_line_portal_type)
    supply_line.setProductLineValue(self.portal.portal_categories.product_line.a)
    supply_line.setBasePrice(1000)
    supply.validate()

    resource_a = self.portal.getDefaultModule(self.product_portal_type)\
                .newContent(portal_type=self.product_portal_type)
    resource_a.setProductLineValue(self.portal.portal_categories.product_line.a)
    resource_a_1 = self.portal.getDefaultModule(self.product_portal_type)\
                .newContent(portal_type=self.product_portal_type)
    resource_a_1.setProductLineValue(self.portal.portal_categories.product_line.a.a1)
    resource_b = self.portal.getDefaultModule(self.product_portal_type)\
                .newContent(portal_type=self.product_portal_type)
    resource_b.setProductLineValue(self.portal.portal_categories.product_line.b)

    self.tic()
    sale_order_line = self.portal.getDefaultModule("Sale Order").newContent(
                              portal_type='Sale Order').newContent(
                          portal_type=self.sale_order_line_portal_type,
                          resource_value=resource_a,
                          quantity=1)
    # resource_a is member of product_line/a, so our supply line applies.
    self.assertEqual(1000, sale_order_line.getPrice())

    sale_order_line = self.portal.getDefaultModule("Sale Order").newContent(
                              portal_type='Sale Order').newContent(
                          portal_type=self.sale_order_line_portal_type,
                          resource_value=resource_a_1,
                          quantity=1)
    # resource_a_1 is member of product_line/a/a1, so our supply line applies.
    self.assertEqual(1000, sale_order_line.getPrice())

    sale_order_line = self.portal.getDefaultModule("Sale Order").newContent(
                              portal_type='Sale Order').newContent(
                          portal_type=self.sale_order_line_portal_type,
                          resource_value=resource_b,
                          quantity=1)
    # resource_b is member of product_line/b, so our supply line does not apply.
    self.assertEqual(None, sale_order_line.getPrice())

  def testGetPriceWithBasePriceDefinedPerSlice(self):
    """
    Slices allow to apply a different price per item given the quantity of this
    item ordered. See exemple
    [unit quantity]   [price defined for the units of this slice]
     0 -> 10        = 10 currency/unit
    11 -> 20        =  9 currency/unit
    21 -> inf       =  8 currency/unit

    So the price for an order of X unit is :
    unit -> total order price             -> price / unit
     9   -> 90 currency                   -> 10      currency/unit
    15   -> 10*10+5*9 = 145 currency      -> 9.66667 currency/unit
    25   -> 20*10+10*9+5*8 = 230 currency -> 9.2     currency/unit
    """
    product_module = self.portal.getDefaultModule(self.product_portal_type)
    product = product_module.newContent(
      portal_type=self.product_portal_type,
      title='FakeProduct'
    )
    product.validate()

    sale_supply = self.portal.getDefaultModule(
      self.sale_supply_portal_type
    ).newContent(
      self.sale_supply_portal_type,
      base_price_per_slice=True,
    )

    supply_line = sale_supply.newContent(
      portal_type=self.sale_supply_line_portal_type,
      resource_value=product,
      base_unit_price=0.00001,
    )
    supply_line.setQuantityStepList((11, 21))
    supply_line.updateCellRange()

    cell0 = supply_line.newContent(
      portal_type=self.sale_supply_cell_portal_type,
      id='path_0',
      slice_base_price=10.,
      slice_quantity_range=(1, 11),
    )
    cell0.setCriterionPropertyList(('quantity', ))
    cell0.setCriterion('quantity', min=1, max=None)
    cell0.setMappedValuePropertyList(
      ["slice_base_price", "slice_quantity_range", "base_price", "base_unit_price"]
    )

    cell1 = supply_line.newContent(
      portal_type=self.sale_supply_cell_portal_type,
      id='path_1',
      slice_base_price=9.,
      slice_quantity_range=(11, 21),
    )
    cell1.setCriterionPropertyList(('quantity', ))
    cell1.setCriterion('quantity', min=11, max=None)
    cell1.setMappedValuePropertyList(
      ["slice_base_price", "slice_quantity_range", "base_price", "base_unit_price"]
    )

    cell2 = supply_line.newContent(
      portal_type=self.sale_supply_cell_portal_type,
      id='path_2',
      slice_base_price=8.,
      slice_quantity_range=(21, None),
    )
    cell2.setCriterionPropertyList(('quantity', ))
    cell2.setCriterion('quantity', min=21, max=None)
    cell2.setMappedValuePropertyList(
      ["slice_base_price", "slice_quantity_range", "base_price", "base_unit_price"]
    )

    sale_supply.validate()
    self.tic()

    currency_module = self.portal.getDefaultModule("Currency")
    currency = currency_module.newContent(
      portal_type="Currency",
      title='Euro',
      base_unit_quantity=0.01,
    )

    sale_order = self.portal.getDefaultModule("Sale Order").newContent(
      portal_type='Sale Order',
      specialise_value=sale_supply,
      resource_value=currency,
    )

    def _test(quantity, price, total_price):
      sale_order_line = sale_order.newContent(
        portal_type=self.sale_order_line_portal_type,
        resource_value=product,
        quantity=quantity,
      )
      self.assertEqual(price, sale_order_line.getPrice())
      self.assertEqual(
        total_price,
        round(sale_order_line.getTotalPrice(), currency.getQuantityPrecision())
      )

    for case in [
       {'quantity': 9, 'price': 90./9, 'total_price': 90.},
       {'quantity': 11, 'price': 109./11, 'total_price': 109.},
       {'quantity': 15, 'price': 145./15, 'total_price': 145.},
       {'quantity': 19, 'price': 181./19, 'total_price': 181.},
       {'quantity': 25, 'price': 230./25, 'total_price': 230.},
    ]:
      _test(**case)

  def testQuantityPrecision(self):
    """test how to define quantity precision on resources.
    """
    resource = self.portal.getDefaultModule(self.product_portal_type)\
                .newContent(portal_type=self.product_portal_type)
    # default is 1
    self.assertEqual(1, resource.getBaseUnitQuantity())
    self.assertEqual(0, resource.getQuantityPrecision())
    # quantity precision is calculated using base quantity unit
    resource.setBaseUnitQuantity(0.001)
    self.assertEqual(3, resource.getQuantityPrecision())

  def test_defaultSupplyLineAfterClone(self):
    """Check that default supply line is properly set up after clone"""
    resource = self.portal.getDefaultModule(self.product_portal_type)\
                .newContent(portal_type=self.product_portal_type)

    resource.edit( purchase_supply_line_base_price=1.0,
      sale_supply_line_base_price=1.0,
    )

    self.assertEqual( resource,
        resource.getDefaultPurchaseSupplyLineValue().getResourceValue() )
    self.assertEqual( resource,
        resource.getDefaultSaleSupplyLineValue().getResourceValue() )

    module = resource.getParentValue()

    cb_data = module.manage_copyObjects(ids=[resource.getId()])
    p_data = module.manage_pasteObjects(cb_data)

    new_resource = module._getOb(p_data[0]['new_id'])

    self.assertEqual(
      new_resource,
      new_resource.getDefaultPurchaseSupplyLineValue().getResourceValue()
    )

    self.assertEqual(
      new_resource,
      new_resource.getDefaultSaleSupplyLineValue().getResourceValue()
    )

  def test_sourceDestinationReferenceOnSupplyLineOnDefaultSupplyLine(self):
    '''Check that it's possible to set and get a source/destination_reference
    on default supply line
    '''
    resource = self.portal.getDefaultModule(self.product_portal_type)\
                .newContent(portal_type=self.product_portal_type)

    resource.edit(\
        purchase_supply_line_source_reference='test_source_reference_on_purchase_supply_line',
        purchase_supply_line_destination_reference='test_destination_reference_on_purchase_supply_line',
        sale_supply_line_source_reference='test_source_reference_on_sale_supply_line',
        sale_supply_line_destination_reference='test_destination_reference_on_sale_supply_line',
        internal_supply_line_source_reference='test_source_reference_on_internal_supply_line',
        internal_supply_line_destination_reference='test_destination_reference_on_internal_supply_line',
    )
    self.assertEqual(resource.getPurchaseSupplyLineSourceReference(),
        'test_source_reference_on_purchase_supply_line')
    self.assertEqual(resource.getPurchaseSupplyLineDestinationReference(),
        'test_destination_reference_on_purchase_supply_line')
    self.assertEqual(resource.getSaleSupplyLineSourceReference(),
        'test_source_reference_on_sale_supply_line')
    self.assertEqual(resource.getSaleSupplyLineDestinationReference(),
        'test_destination_reference_on_sale_supply_line')
    self.assertEqual(resource.getInternalSupplyLineSourceReference(),
        'test_source_reference_on_internal_supply_line')
    self.assertEqual(resource.getInternalSupplyLineDestinationReference(),
        'test_destination_reference_on_internal_supply_line')

  def testQuantityUnitOnMovement(self):
    """Make sure that changing default quantity unit on resource does not
       affect to movement.
       In this test, always use Base.edit method. Because Base.edit is
       used when real user edit document through edit form.
    """
    # Set up quantity unit categories
    # weight
    quantity_unit_category_value = self.portal.portal_categories.quantity_unit
    quantity_unit_weight = quantity_unit_category_value._getOb('weight', None)
    if quantity_unit_weight is None:
      quantity_unit_weight = quantity_unit_category_value.newContent(
        id='weight', portal_type='Category')
    quantity_unit_gram = quantity_unit_weight._getOb('gram', None)
    if quantity_unit_gram is None:
      quantity_unit_gram = quantity_unit_weight.newContent(
        portal_type='Category', id='gram')
    # volume
    quantity_unit_volume = quantity_unit_category_value._getOb('volume', None)
    if quantity_unit_volume is None:
      quantity_unit_volume = quantity_unit_category_value.newContent(
        id='volume', portal_type='Category')
    quantity_unit_liter = quantity_unit_volume._getOb('liter', None)
    if quantity_unit_liter is None:
      quantity_unit_liter = quantity_unit_volume.newContent(
        portal_type='Category', id='liter')
    self.commit()

    # Create resource
    resource_value = self.portal.getDefaultModule(
      self.product_portal_type).newContent(portal_type=self.product_portal_type)
    resource_value.edit(quantity_unit_value_list=[
        quantity_unit_gram, quantity_unit_liter])
    self.commit()
    self.assertEqual(resource_value.getDefaultQuantityUnitValue(),
                     quantity_unit_gram)

    # Create sale order line
    sale_order = self.portal.getDefaultModule('Sale Order').newContent(
      portal_type='Sale Order')
    sale_order_line = sale_order.newContent(
      portal_type=self.sale_order_line_portal_type)
    self.commit()

    # Set resource to movement
    sale_order_line.edit(resource_value=resource_value)
    self.commit()
    self.assertEqual(sale_order_line.getQuantityUnitValue(),
                     quantity_unit_gram)

    # Select different quantity unit
    sale_order_line.edit(quantity_unit_value=quantity_unit_liter)
    self.commit()
    self.assertEqual(sale_order_line.getQuantityUnitValue(),
                     quantity_unit_liter)

    # Select empty(no quantity unit)
    sale_order_line.edit(quantity_unit_value=None)
    self.commit()

    # Select default quantity unit again
    sale_order_line.edit(quantity_unit_value=quantity_unit_gram)
    self.commit()
    self.assertEqual(sale_order_line.getQuantityUnitValue(),
                     quantity_unit_gram)

    # Change default quantity unit on resource
    # Now liter is default quantity unit.
    resource_value.edit(quantity_unit_value_list=[
        quantity_unit_liter, quantity_unit_gram])
    self.commit()

    # Check existing movement again and make sure that quantity
    # unit is not changed.
    expectedFailure(self.assertEqual)(
      sale_order_line.getQuantityUnitValue(),
      quantity_unit_gram)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestResource))
  return suite
