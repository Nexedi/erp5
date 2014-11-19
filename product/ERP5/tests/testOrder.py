# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2008 Nexedi SA and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
#          Romain Courteaud <romain@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
import os

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import FileUpload,\
    SubcontentReindexingWrapper
from AccessControl.SecurityManagement import newSecurityManager
from DateTime import DateTime
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.CMFCore.utils import getToolByName

class TestOrderMixin(SubcontentReindexingWrapper):

  default_quantity = 99
  default_price = 555
  default_negative_price = -5550
  resource_portal_type = 'Apparel Model'
  order_portal_type = 'Sale Order'
  order_line_portal_type = 'Sale Order Line'
  order_cell_portal_type = 'Sale Order Cell'
  applied_rule_portal_type = 'Applied Rule'
  simulation_movement_portal_type = 'Simulation Movement'
  # see comment about self.datetime on afterSetUp() below
  datetime = DateTime() - 2
  packing_list_portal_type = 'Sale Packing List'
  packing_list_line_portal_type = 'Sale Packing List Line'
  packing_list_cell_portal_type = 'Sale Packing List Cell'
  delivery_builder_id = 'sale_packing_list_builder'
  size_list = ['Baby','Child/32','Child/34','Man','Woman']
  business_process = 'business_process_module/erp5_default_business_process'

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_core_proxy_field_legacy', 'erp5_base','erp5_pdm',
            'erp5_simulation', 'erp5_trade', 'erp5_apparel', 'erp5_project',
            'erp5_configurator_standard_solver',
            'erp5_configurator_standard_trade_template',
            'erp5_simulation_test', 'erp5_administration', 'erp5_dummy_movement')

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

  def createUser(self, name, role_list):
    user_folder = self.getPortal().acl_users
    user_folder._doAddUser(name, 'password', role_list, [])

  def afterSetUp(self):
    # XXX-Leo: cannot call super here, because other classes call
    # SuperClass.afterSetUp(self) directly... this needs to be cleaned
    # up, including consolidating all conflicting definitions of
    # .createCategories()
    #super(TestOrderMixin, self).afterSetUp()
    self.createUser('test_user',
                    ['Assignee', 'Assignor', 'Member',
                     'Associate', 'Auditor', 'Author'])
    self.createUser('manager', ['Manager'])
    self.loginByUserName('manager')
    self.category_tool = self.getCategoryTool()
    portal_catalog = self.getCatalogTool()
    #portal_catalog.manage_catalogClear()
    self.createCategories()
    self.validateRules()
    self.setUpPreferences()
    # pin datetime on the day before yesterday, to make sure that:
    #
    # 1. All calculations are done relative to the same time
    # 2. We don't get random failures when tests run close to midnight
    self.datetime = DateTime() - 2
    self.pinDateTime(self.datetime)
    self.loginByUserName('test_user')
    self.begin = self.datetime

  def beforeTearDown(self):
    self.unpinDateTime()
    super(TestOrderMixin, self).beforeTearDown()

  def createCurrency(self):
    currency_module = self.getPortal().currency_module
    if currency_module._getOb('euro', None) is None:
      currency_module.newContent(id='euro', reference='EUR', title='EURO')

  def createCategories(self):
    """
      Light install create only base categories, so we create
      some categories for testing them
    """
    category_tool = self.portal.portal_categories
    size_category_list = ['Baby', 'Child', 'Man', 'Woman']
    if len(category_tool.size.contentValues()) == 0 :
      for category_id in size_category_list:
        o = category_tool.size.newContent(portal_type='Category',
                                               id=category_id)
      for category_id in ['32', '34']:
        o = category_tool.size.Child.newContent(portal_type='Category',
                                                     id=category_id)

    colour_category_list = ['blue', 'green']
    if len(category_tool.colour.contentValues()) == 0 :
      for category_id in colour_category_list:
        o = category_tool.colour.newContent(portal_type='Category',
                                                 id=category_id)

    industrial_phase_category_list = ['phase1', 'phase2',
                                      'supply_phase1', 'supply_phase2']
    if len(category_tool.industrial_phase.contentValues()) == 0:
      for category_id in industrial_phase_category_list:
        o = category_tool.industrial_phase.newContent(
                                                 portal_type='Category',
                                                 id=category_id)

    product_line_category_list = ['apparel', 'cancel']
    if len(category_tool.product_line.contentValues()) == 0:
      for category_id in product_line_category_list:
        o = category_tool.product_line.newContent(
                                                 portal_type='Category',
                                                 id=category_id)

  def getTwoRelatedPackingList(self, sequence):
    order = sequence.get('order')
    packing_list_list = order.getCausalityRelatedValueList(
                               portal_type=self.packing_list_portal_type)
    self.assertEqual(2,len(packing_list_list))
    packing_list1 = None
    packing_list2 = None
    for packing_list in packing_list_list:
      if packing_list.getUid() == sequence.get('packing_list').getUid():
        packing_list1 = packing_list
      else:
        packing_list2 = packing_list
    sequence.edit(new_packing_list=packing_list2)
    return packing_list1, packing_list2

  def stepCreateNotVariatedResource(self,sequence=None, sequence_list=None, \
                                    **kw):
    """
      Create a resource with no variation
    """
    portal = self.getPortal()
    resource_module = portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent(portal_type=self.resource_portal_type)
    resource.edit(
      title = "NotVariatedResource%s" % resource.getId(),
      industrial_phase_list=["phase1", "phase2"],
      product_line = 'apparel'
    )

    sequence.edit( resource = resource )
    resource_list = sequence.get('resource_list',default=[])
    resource_list.append(resource)
    sequence.edit( resource_list = resource_list )

  def stepCreateNotVariatedResourceForNegativePriceOrderLine(self, sequence=None, sequence_list=None, **kw):
    """
      Create a resource with no variation for negative price order line.
    """
    portal = self.getPortal()
    resource_module = portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent(portal_type=self.resource_portal_type)
    resource.edit(
      title = "NotVariatedResourceForNegativePriceOrderLine%s" % resource.getId(),
      product_line = 'cancel'
    )

    sequence.edit( resource = resource )
    resource_list = sequence.get('resource_list',default=[])
    resource_list.append(resource)
    sequence.edit( resource_list = resource_list )

  def stepCreateVariatedResource(self, sequence=None, sequence_list=None, \
                                 **kw):
    """
      Create a resource with variation
    """
    portal = self.getPortal()
    resource_module = portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent(portal_type=self.resource_portal_type)
    resource.edit(
      title = "VariatedResource%s" % resource.getId(),
      industrial_phase_list=["phase1", "phase2"],
      product_line = 'apparel'
    )
    resource.setSizeList(self.size_list)
    # Add colour variation
    colour_variation_count = 3
    for i in range(colour_variation_count):
      variation_portal_type = 'Apparel Model Colour Variation'
      variation = resource.newContent(portal_type = variation_portal_type)
      variation.edit(
        title = 'ColourVariation%s' % str(i)
      )
    # Add morphology variation
    morphology_variation_count = 2
    for i in range(morphology_variation_count) :
      variation_portal_type = 'Apparel Model Morphology Variation'
      variation = resource.newContent(portal_type=variation_portal_type)
      variation.edit(
        title = 'MorphologyVariation%s' % str(i)
      )

    sequence.edit( resource = resource )
    resource_list = sequence.get('resource_list',default=[])
    resource_list.append(resource)
    sequence.edit( resource_list = resource_list )

  @UnrestrictedMethod
  def stepCreateVariatedMultipleQuantityUnitResource(self, sequence=None, sequence_list=None, **kw):
    """
    Create a resource with variation and multiple quantity units
    """
    # Extend quantity_unit category if needed
    quantity_unit = self.portal.portal_categories.quantity_unit
    if not 'unit' in quantity_unit.objectIds():
      quantity_unit.newContent(id='unit')
    if not 'drum' in quantity_unit.unit.objectIds():
      quantity_unit.unit.newContent(id='drum', quantity=1)
    if not 'mass' in quantity_unit.objectIds():
      quantity_unit.newContent(id='mass')
    if not 'kilogram' in quantity_unit.mass.objectIds():
      quantity_unit.mass.newContent(id='kilogram', quantity=1)
    # Extend metric_type category if needed
    metric_type = self.portal.portal_categories.metric_type
    if not 'unit' in metric_type.objectIds():
      metric_type.newContent(id='unit')
    if not 'mass' in metric_type.objectIds():
      metric_type.newContent(id='mass')

    # Create resource
    self.stepCreateVariatedResource(sequence, sequence_list, **kw)
    resource = sequence.get('resource')

    # Extend resource portal type
    resource_portal_type = getattr(self.portal.portal_types, resource.portal_type)
    type_allowed_content_type_list = resource_portal_type.getTypeAllowedContentTypeList()
    if not 'Measure' in type_allowed_content_type_list:
      type_allowed_content_type_list.append('Measure')
      resource_portal_type.setTypeAllowedContentTypeList(type_allowed_content_type_list)

    # Set quantity units to product
    resource.setQuantityUnitValueList([quantity_unit.mass.kilogram,
                                       quantity_unit.unit.drum])
    # Set measures to products
    resource.newContent(portal_type='Measure',
                        metric_type_value=metric_type.mass,
                        default_metric_type=True,
                        quantity_unit_value=quantity_unit.mass.kilogram,
                        quantity=1)
    resource.newContent(portal_type='Measure',
                        metric_type_value=metric_type.unit,
                        quantity_unit_value=quantity_unit.unit.drum,
                        quantity=0.01)

  def stepCreateOrganisation(self, sequence=None, sequence_list=None,
                             title=None, **kw):
    """
      Create a empty organisation
    """
    organisation = sequence.get('organisation')
    organisation_portal_type = 'Organisation'
    portal = self.getPortal()
    organisation_module = portal.getDefaultModule( \
                                   portal_type=organisation_portal_type)
    organisation = organisation_module.newContent( \
                                   portal_type=organisation_portal_type)
    bank_account = organisation.newContent(id='bank',
                                           portal_type='Bank Account',
                                           title='bank%s' % organisation.getId())
    organisation.setDefaultAddressStreetAddress('rue xv')
    organisation.setDefaultAddressZipCode('12345')
    if title is None:
      organisation.edit(title='organisation%s' % organisation.getId())
      sequence.edit(organisation=organisation)
    else:
      organisation.edit(title=title)
      sequence.edit(**{title:organisation})

  def stepCreateProject(self, sequence=None, sequence_list=None,
                        title=None, **kw):
    """
      Create a project
    """
    project = sequence.get('project')
    project_portal_type = 'Project'
    portal = self.getPortal()
    project_module = portal.getDefaultModule( \
                                   portal_type=project_portal_type)
    project = project_module.newContent( \
                                   portal_type=project_portal_type)
    if title is None:
      project.edit(title='project%s' % project.getId())
      sequence.edit(project=project)
    else:
      project.edit(title=title)
      sequence.edit(**{title:project})

  def stepCreateOrder(self,sequence=None, sequence_list=None, **kw):
    """
      Create a empty order
    """
    organisation = sequence.get('organisation')
    project = sequence.get('project')
#     person = sequence.get('person')
    portal = self.getPortal()
    order_module = portal.getDefaultModule(portal_type=self.order_portal_type)
    order = order_module.newContent(portal_type=self.order_portal_type)
    order.edit(
      title = "Order%s (%s)" % (order.getId(), self.id()),
      start_date = self.datetime + 10,
      stop_date = self.datetime + 20,
      specialise = self.business_process,
    )
    if organisation is not None:
      order.edit(source_value=organisation,
                 source_section_value=organisation,
                 destination_value=organisation,
                 destination_section_value=organisation,
                 # Added for test Packing List Copy
                 source_decision_value=organisation,
                 destination_decision_value=organisation,
                 source_administration_value=organisation,
                 destination_administration_value=organisation,
                 )
    if project is not None:
      order.edit(source_project_value=project,
                 destination_project_value=project,
                 )
    sequence.edit( order = order )

  def stepCheckOrder(self, sequence=None, sequence_list=None, **kw):
    """
      Check if order was well created, either by stepCreateOrder of
      stepSetOrderProfile
    """
    source_organisation = sequence.get('organisation1')
    if source_organisation is None:
      source_organisation = sequence.get('organisation')
    destination_organisation = sequence.get('organisation2')
    if destination_organisation is None:
      destination_organisation = sequence.get('organisation')
    source_project = sequence.get('project1')
    if source_project is None:
      source_project = sequence.get('project')
    destination_project = sequence.get('project2')
    if destination_project is None:
      destination_project = sequence.get('project')
    order = sequence.get('order')
    self.assertEqual(self.datetime+10, order.getStartDate())
    self.assertEqual(self.datetime+20, order.getStopDate())
    self.assertEqual(source_organisation, order.getSourceValue())
    self.assertEqual(destination_organisation, order.getDestinationValue())
    self.assertEqual(source_organisation, order.getSourceSectionValue())
    self.assertEqual(destination_organisation, order.getDestinationSectionValue())
    self.assertEqual(source_project, order.getSourceProjectValue())
    self.assertEqual(destination_project, order.getDestinationProjectValue())


  def stepCreateOrderLine(self,sequence=None, sequence_list=None, **kw):
    """
      Create a empty order line
    """
    order = sequence.get('order')
    order_line = order.newContent(portal_type=self.order_line_portal_type)
    order_line.edit(
      title = "Order Line"
    )
    sequence.edit(order_line=order_line)

  def stepCheckOrderLineEmptyMatrix(self, sequence=None, \
                                    sequence_list=None, **kw):
    """
      Check if the matrix of the current order line is empty.
    """
    order_line = sequence.get('order_line')
    base_id = 'movement'
#     vcl = list(order_line.getVariationCategoryList())
#     cell_key_list = order_line.getCellKeyList(base_id=base_id)
    cell_list = order_line.objectValues(portal_type=self.order_cell_portal_type)
#     self.failIfDifferentSet( vcl , [] )
#     self.failIfDifferentSet( cell_key_list , [] )
    self.failIfDifferentSet( cell_list , [] )

  def stepSetOrderLineResource(self, sequence=None, sequence_list=None, **kw):
    """
      Set order line resource with the current resource
    """
    order_line = sequence.get('order_line')
    resource = sequence.get('resource')
    order_line.setResourceValue(resource)

  def stepDeleteOrderLineResource(self, sequence=None, \
                                  sequence_list=None, **kw):
    """
      Set order line resource to None
    """
    order_line = sequence.get('order_line')
    order_line.setResource(None)

  def stepEmptyOrderLineMatrix(self,sequence=None, sequence_list=None, **kw):
    """
      Delete the current order line matrix
    """
    order_line = sequence.get('order_line')
    cell_list = order_line.objectValues(portal_type=self.order_cell_portal_type)
    order_line.deleteContent( map(lambda x: x.getId(), cell_list) )

  def stepSetOrderLineEmptyVCL(self,sequence=None, sequence_list=None, **kw):
    """
      Delete the current order line's variation category list
    """
    order_line = sequence.get('order_line')
    resource = sequence.get('resource')
    order_line.setVariationCategoryList([])

  def splitList(self, list):
    """
      Split a list and return tuple with the 2 half
    """
    middle = len(list)/2 + len(list)%2
    return ( list[:middle] , list[middle:] )

  def stepSetOrderLineHalfVCL(self,sequence=None, sequence_list=None, **kw):
    """
      Delete the current order line variation category list
    """
    order_line = sequence.get('order_line')
    resource = sequence.get('resource')
    order_line_vcl = []
    resource_vbcl = resource.getVariationBaseCategoryList()
    for vbc in resource_vbcl:
      LOG('stepSetOrderLineHalfVCL', 0, 'vbc: %s' % str(vbc))
      resource_vcl = list(resource.getVariationCategoryList(
                                  base_category_list=[vbc],
                                  omit_individual_variation=0))
      LOG('stepSetOrderLineHalfVCL', 0,
                        'resource_vcl: %s' % str(resource_vcl))
      resource_vcl.sort()
      LOG('stepSetOrderLineHalfVCL', 0, 'split resource_vcl: %s' %
                           str(self.splitList(resource_vcl)[0]))
      order_line_vcl.extend(self.splitList(resource_vcl)[0])
    order_line.setVariationCategoryList(order_line_vcl)

  def stepSetOrderLineFullVCL(self,sequence=None, sequence_list=None, **kw):
    """
      Complete the order line's variation category list
    """
    order_line = sequence.get('order_line')
    resource = sequence.get('resource')
    resource_vcl = list(resource.getVariationCategoryList(
                                   omit_individual_variation=0))
    resource_vcl.sort()
    order_line.setVariationCategoryList(resource_vcl)

  def stepCheckOrderLineRange(self,sequence=None, sequence_list=None, **kw):
    """
      Check order line matrix range
    """
    order_line = sequence.get('order_line')
    base_id = 'movement'
    vcl = order_line.getVariationCategoryList(omit_optional_variation=1)
    cell_range = order_line.OrderLine_asCellRange(matrixbox=0)

    l = len(vcl)
    s = sum(map(lambda x: len(x), cell_range))
    self.assertEqual(l,s)
    cell_key_list = order_line.getCellKeyList(base_id=base_id)
    if cell_range == []:
      self.assertEqual(len(cell_key_list), 0)
    else:
      len_range = map(lambda x: len(x), cell_range)
      self.assertEqual(len(cell_key_list), reduce(lambda x,y: x*y, len_range))

  def stepCompleteOrderLineMatrix(self,sequence=None, sequence_list=None, \
                                  **kw):
    """
      Complete the current order line matrix.
    """
    order_line = sequence.get('order_line')
    base_id = 'movement'
    cell_key_list = list(order_line.getCellKeyList(base_id=base_id))
    cell_key_list.sort()
    price = 100
    quantity = 200
    for cell_key in cell_key_list:
      cell = order_line.newCell(base_id=base_id, \
                                portal_type=self.order_cell_portal_type, *cell_key)
      cell.edit(mapped_value_property_list=['price','quantity'],
                price=price, quantity=quantity,
                predicate_category_list=cell_key,
                variation_category_list=cell_key)
      price += 1
      quantity += 1

  def stepCheckOrderLineCompleteMatrix(self, sequence=None, \
                                       sequence_list=None, **kw):
    """
      Check if the matrix of the current order line is complete.
    """
    order_line = sequence.get('order_line')
    base_id = 'movement'
    cell_key_list = list(order_line.getCellKeyList(base_id=base_id))
    cell_key_list.sort()
    cell_list = order_line.objectValues(portal_type=self.order_cell_portal_type)
    self.assertEqual(len(cell_list), len(cell_key_list))
    price = 100
    quantity = 200
    for cell_key in cell_key_list:
      self.assertTrue(order_line.hasCell(base_id=base_id, *cell_key))
      cell = order_line.getCell(base_id=base_id, *cell_key)
      self.assertEqual(self.order_cell_portal_type, cell.getPortalType())
      # XXX How can I check the cell content ?
#       self.assertEqual(price , cell.getProperty('price'))
#       self.assertEqual(quantity, cell.getProperty('quantity'))
#       self.failIfDifferentSet(cell.getMembershipCriterionCategoryList(),
#                               cell_key)
      price += 1
      quantity += 1

  def stepCheckOrderLineVRCL(self, sequence=None, sequence_list=None, **kw):
    """
      Check if getVariationRangeCategoryList returns the good result.
    """
    order_line = sequence.get('order_line')
    resource = order_line.getResourceValue()
    vrcl = order_line.getVariationRangeCategoryList()
    if resource == None:
      self.failIfDifferentSet([], list(vrcl))
    else:
      resource_vcl = resource.getVariationCategoryList(omit_individual_variation=0)
      self.failIfDifferentSet(resource_vcl, vrcl)

  def stepCheckOrderLineVRCIL(self, sequence=None, sequence_list=None, **kw):
    """
      Check if getVariationRangeCategoryItemList returns the good result.
      Does not test display...
      Item are left display.
    """
    order_line = sequence.get('order_line')
    vrcl = order_line.getVariationRangeCategoryList()
    vrcil = order_line.getVariationRangeCategoryItemList()
    self.failIfDifferentSet(vrcl, map(lambda x: x[1], vrcil))

  def stepSetOrderLineDefaultValues(self, sequence=None, \
                                    sequence_list=None, **kw):
    """
      Set the default price and quantity on the order line.
    """
    order_line = sequence.get('order_line')
    order_line.edit(quantity=self.default_quantity,
                    price=self.default_price)

  def stepSetOrderLineDefaultNegativePriceValue(self, sequence=None, \
                                           sequence_list=None, **kw):
    """
      Set the default negative price and 1 to quantity on the order line.
    """
    order_line = sequence.get('order_line')
    order_line.edit(quantity=1,
                    price=self.default_negative_price)

  def stepCheckOrderLineDefaultValues(self, sequence=None, \
                                    sequence_list=None, **kw):
    """
      Check the default price and quantity on the order line.
    """
    order_line = sequence.get('order_line')
    self.assertEqual(self.default_quantity, order_line.getQuantity())
    self.assertEqual(self.default_price, order_line.getPrice())

  def stepCheckOrderLineTotalQuantity(self, sequence=None, \
                                    sequence_list=None, **kw):
    """
      Check the method getTotalQuantity on a order line.
    """

    # order_line needs to be indexed for 'fast' calculation to work as expected
    self.tic()

    order_line = sequence.get('order_line')
    base_id = 'movement'
    cell_key_list = order_line.getCellKeyList(base_id=base_id)
    if list(cell_key_list) == []:
      self.assertEqual(order_line.getQuantity(), \
                        order_line.getTotalQuantity())
    else:
      total_quantity = 0
      for cell_key in cell_key_list:
        if order_line.hasCell(base_id = base_id, *cell_key):
          cell = order_line.getCell(base_id = base_id, *cell_key)
          total_quantity += cell.getProperty('quantity')
      self.assertEqual(total_quantity, order_line.getTotalQuantity())
    self.assertEqual( order_line.getTotalQuantity(fast = 0),
                       order_line.getTotalQuantity(fast = 1) )
    self.assertNotEquals(order_line.getTotalQuantity(fast = 1),0)

  def stepCheckOrderLineTotalPrice(self, sequence=None, \
                                    sequence_list=None, **kw):
    """
      Check the method getTotalPrice on a order line.
    """

    # order_line needs to be indexed for 'fast' calculation to work as expected
    self.tic()

    order_line = sequence.get('order_line')
    base_id = 'movement'
    cell_key_list = order_line.getCellKeyList(base_id=base_id)
    if list(cell_key_list) == []:
      self.assertEqual(order_line.getProperty('price') *
                        order_line.getProperty('quantity'),
                        order_line.getTotalPrice())
    else:
      total_price = 0
      for cell_key in cell_key_list:
        if order_line.hasCell(base_id = base_id, *cell_key):
          cell = order_line.getCell(base_id = base_id, *cell_key)
          total_price +=  ( cell.getProperty('quantity') *
                            cell.getProperty('price'))
      self.assertEqual(total_price, order_line.getTotalPrice())
    self.assertEqual( order_line.getTotalPrice(fast = 0),
                       order_line.getTotalPrice(fast = 1) )
    self.assertNotEquals(order_line.getTotalPrice(fast = 1),0)

  def stepCheckOrderLineTotalPriceAndQuantityFastParameter(self, sequence=None, \
                                    sequence_list=None, **kw):
    """
      Check the method getTotalPrice on a order line.

      Here we will check that very carefully ther parameter fast
    """
    portal_catalog = self.getCatalogTool()
    total_price = 0
    total_quantity = 0
    order_line = sequence.get('order_line')
    base_id = 'movement'
    cell_key_list = order_line.getCellKeyList(base_id=base_id)
    for cell_key in cell_key_list:
      if order_line.hasCell(base_id = base_id, *cell_key):
        cell = order_line.getCell(base_id = base_id, *cell_key)
        total_price +=  ( cell.getProperty('quantity') *
                          cell.getProperty('price'))
        total_quantity += (cell.getProperty('quantity'))
    self.assertEqual(len(portal_catalog(
                          relative_url=order_line.getRelativeUrl())),0)
    self.assertEqual(total_price, order_line.getTotalPrice(fast=0))
    self.assertEqual(total_quantity, order_line.getTotalQuantity(fast=0))
    self.assertEqual(0, order_line.getTotalPrice(fast=1))
    self.assertEqual(0, order_line.getTotalQuantity(fast=1))
    self.assertNotEquals(total_price, 0)
    self.tic()
    self.assertEqual(len(portal_catalog(relative_url=
                                         order_line.getRelativeUrl())),1)
    self.assertEqual(total_price, order_line.getTotalPrice(fast=1))
    self.assertEqual(total_price, order_line.getTotalPrice(fast=0))
    self.assertEqual(total_quantity, order_line.getTotalQuantity(fast=1))
    self.assertEqual(total_quantity, order_line.getTotalQuantity(fast=0))

  def stepCheckOrderTotalQuantity(self, sequence=None, sequence_list=None, \
                                  **kw):
    """
      Check the method getTotalQuantity on a order .
    """

    # order needs to be indexed for 'fast' calculation to work as expected
    self.tic()

    order = sequence.get('order')
    order_line_list = order.objectValues( \
                                 portal_type=self.order_line_portal_type)
    order_line_list = map(lambda x: x.getObject(), order_line_list)
    total_quantity = 0
    for order_line in order_line_list:
      total_quantity += order_line.getTotalQuantity()
    self.assertEqual(total_quantity, order.getTotalQuantity())
    self.assertEqual( order.getTotalQuantity(fast = 0),
                       order.getTotalQuantity(fast = 1) )

  def stepCheckOrderTotalPrice(self, sequence=None, sequence_list=None, \
                                  **kw):
    """
      Check the method getTotalPrice on a order .
    """

    # order needs to be indexed for 'fast' calculation to work as expected
    self.tic()

    order = sequence.get('order')
    order_line_list = order.objectValues( \
                                 portal_type=self.order_line_portal_type)
    order_line_list = map(lambda x: x.getObject(), order_line_list)
    total_price = 0
    for order_line in order_line_list:
      total_price += order_line.getTotalPrice()
    self.assertEqual(total_price, order.getTotalPrice())
    self.assertEqual( order.getTotalPrice(fast = 0),
                       order.getTotalPrice(fast = 1) )

  def stepCheckOrderTotalPriceAndQuantityFastParameter(self,
                                  sequence=None, sequence_list=None, **kw):
    """
      Check the method getTotalPrice on a order .

      Here we will look carefully at the parameter fast
    """
    portal_catalog = self.getCatalogTool()

    order = sequence.get('order')
    order_line_list = order.objectValues( \
                                 portal_type=self.order_line_portal_type)
    order_line_list = map(lambda x: x.getObject(), order_line_list)
    total_price = 0
    for order_line in order_line_list:
      total_price += order_line.getTotalPrice()
    self.assertEqual(0, len(portal_catalog(relative_url=order.getRelativeUrl())))
    self.assertEqual(total_price, order.getTotalPrice(fast=0))
    self.assertNotEquals(total_price, 0)
    self.assertEqual(0, order.getTotalPrice(fast=1))
    self.tic()
    self.assertEqual(1, len(portal_catalog(relative_url=order.getRelativeUrl())))
    self.assertEqual(total_price, order.getTotalPrice(fast=1))
    self.assertEqual(total_price, order.getTotalPrice(fast=0))

  def stepCheckOrderInitialState(self, sequence=None, sequence_list=None, \
                                  **kw):
    """
      Check if the first state of a order is draft.
    """
    order = sequence.get('order')
    self.assertEqual('draft', order.getSimulationState())

  def stepCheckOrderLineState(self, sequence=None, sequence_list=None, \
                                  **kw):
    """
      Check if the state of a order line is the same as parent order.
    """
    order = sequence.get('order')
    order_line = sequence.get('order_line')
    self.assertEqual(order.getSimulationState(), order_line.getSimulationState())

  def stepCheckOrderCellState(self, sequence=None, sequence_list=None, \
                                  **kw):
    """
      Check if the state of a order line is the same as parent order.
    """
    order = sequence.get('order')
    order_line = sequence.get('order_line')
    cell_list = order_line.objectValues(portal_type=self.order_cell_portal_type)
    for cell in cell_list:
      self.assertEqual(order.getSimulationState(), cell.getSimulationState())

  def stepCheckOrderPlanned(self, sequence=None, sequence_list=None, **kw):
    order = sequence.get('order')
    self.assertEqual('planned', order.getSimulationState())

  def checkAcquisition(self, object, acquired_object):
    """
      Check if properties are well acquired
    """
    # packing_list_movement, simulation_movement

    self.assertEqual(acquired_object.getStartDate(), object.getStartDate())
    self.assertEqual(acquired_object.getStopDate(), object.getStopDate())
    self.assertEqual(acquired_object.getSourceValue(), \
                      object.getSourceValue())
    self.assertEqual(acquired_object.getDestinationValue(), \
                      object.getDestinationValue())


    self.assertEqual(acquired_object.getSourceSectionValue(), \
                      object.getSourceSectionValue())
    self.assertEqual(acquired_object.getDestinationSectionValue(), \
                      object.getDestinationSectionValue())

  def stepCheckOrderLineAcquisition(self, sequence=None, \
                                    sequence_list=None, **kw):
    """
      Test if order line acquired some order properties
    """
    order = sequence.get('order')
    order_line = sequence.get('order_line')
    self.checkAcquisition(order_line, order)

  def stepCheckOrderCellAcquisition(self, sequence=None, \
                                    sequence_list=None, **kw):
    """
      Test if order cell acquired some order line properties
    """
    order_line = sequence.get('order_line')
    cell_list = order_line.getCellValueList()
    self.assertTrue(len(cell_list) > 0)
    cell = cell_list[0]

    self.checkAcquisition(cell, order_line)
    # Test resource
    self.assertEqual(order_line.getResource(), \
                      cell.getResource())
    # Test resource variation
    cvcl = cell.getVariationCategoryList()
    olvcl = order_line.getVariationCategoryList()
    # This test is not valide anymore, because of option variation
#     self.assertEqual(len(order_line.getVariationRangeBaseCategoryList()), \
#                       len(cvcl))
    for variation_category in cvcl:
      self.assertTrue(variation_category in olvcl)

  def stepCheckOrderSimulation(self, sequence=None, sequence_list=None, **kw):
    """
      Test if simulation is matching order
    """
    self.checkOrderRuleSimulation(rule_reference='default_order_rule', sequence=sequence, \
        sequence_list=sequence_list, **kw)

  def checkOrderRuleSimulation(self, rule_reference, sequence=None, sequence_list=None, **kw):
    """
      Test if simulation is matching order, be sure that rule_reference is used
      to expand simulation for order
    """
    order = sequence.get('order')
    related_applied_rule_list = order.getCausalityRelatedValueList( \
                                   portal_type=self.applied_rule_portal_type)
    no_applied_rule_state = ('draft', 'auto_planned')
    order_state = order.getSimulationState()

    if order_state in no_applied_rule_state:
      self.assertEqual(0, len(related_applied_rule_list))
    else:
      LOG('stepCheckOrderRuleSimulation', 0, 'related_applied_rule_list: %s' %
                   str([x.getObject() for x in related_applied_rule_list]))
      self.assertEqual(1, len(related_applied_rule_list))
      applied_rule = related_applied_rule_list[0].getObject()
      sequence.edit(applied_rule=applied_rule)
      self.assertTrue(applied_rule is not None)

      # Test if applied rule has a specialise value with passed rule_reference
      portal_rules = getToolByName(order, 'portal_rules')
      self.assertEqual(rule_reference,
                        applied_rule.getSpecialiseReference())

      simulation_movement_list = applied_rule.objectValues()
      sequence.edit(simulation_movement_list=simulation_movement_list)

      # Count the number of movement in order
      movement_list = order.getMovementList()
      # Check if number of movement is equal to number of simulation movement
      self.assertEqual(len(movement_list), len(simulation_movement_list))
      # Check if each movement has only one simulation movement related
      order_movement_list = [x.getDeliveryValue() for x in \
                             simulation_movement_list]
      self.failIfDifferentSet(movement_list, order_movement_list)

      # Check each simulation movement
      for simulation_movement in simulation_movement_list:
        order_movement = simulation_movement.getDeliveryValue()
        # Test quantity
        self.assertEqual(order_movement.getQuantity(), \
                          simulation_movement.getQuantity())
        # Test price
        self.assertEqual(order_movement.getPrice(), \
                          simulation_movement.getPrice())
        # Test resource
        self.assertEqual(order_movement.getResource(), \
                          simulation_movement.getResource())
        # Test resource variation
        self.assertEqual(order_movement.getVariationText(), \
                          simulation_movement.getVariationText())
        self.assertEqual(order_movement.getVariationCategoryList(), \
                          simulation_movement.getVariationCategoryList())
        # XXX Test acquisition
        self.checkAcquisition(simulation_movement, order_movement)

  def modifyOrderState(self, transition_name, sequence=None,
                       sequence_list=None):
    order = sequence.get('order')
    order.portal_workflow.doActionFor(order, transition_name)

  def stepPlanOrder(self, sequence=None, sequence_list=None, **kw):
    self.modifyOrderState('plan_action', sequence=sequence)

  def stepOrderOrder(self, sequence=None, sequence_list=None, **kw):
    self.modifyOrderState('order_action', sequence=sequence)

  def stepConfirmOrder(self, sequence=None, sequence_list=None, **kw):
    self.modifyOrderState('confirm_action', sequence=sequence)

  def stepCancelOrder(self, sequence=None, sequence_list=None, **kw):
    self.modifyOrderState('cancel_action', sequence=sequence)

  def stepCheckPortalMethod(self, sequence=None, sequence_list=None, **kw):
    """
      Test if some portal method are well defined
    """
    order = sequence.get('order')
    self.assertTrue('Simulation Movement' in order.getPortalMovementTypeList())
    self.assertTrue(self.order_line_portal_type in order.getPortalMovementTypeList())

  def stepCheckDeliveryBuilderPresence(self, sequence=None,
                                       sequence_list=None, **kw):
    """
      Test if delivery builder exists
    """
    delivery_builder = getattr(self.getPortal().portal_deliveries,
                               self.delivery_builder_id)
    self.assertEqual('Delivery Builder', delivery_builder.getPortalType())

  def stepCreateOrganisation1(self,sequence=None, sequence_list=None, **kw):
    """
      Create a empty organisation
    """
    self.stepCreateOrganisation(sequence=sequence, sequence_list=sequence_list,
                                **kw)
    organisation = sequence.get('organisation')
    sequence.edit(organisation1=organisation)

  def stepCreateOrganisation2(self,sequence=None, sequence_list=None, **kw):
    """
      Create a empty organisation
    """
    self.stepCreateOrganisation(sequence=sequence, sequence_list=sequence_list,
                                **kw)
    organisation = sequence.get('organisation')
    sequence.edit(organisation2=organisation)

  def stepCreateProject1(self,sequence=None, sequence_list=None, **kw):
    """
      Create a project
    """
    self.stepCreateProject(sequence=sequence, sequence_list=sequence_list,
                           **kw)
    project = sequence.get('project')
    sequence.edit(project1=project)

  def stepCreateProject2(self,sequence=None, sequence_list=None, **kw):
    """
      Create a project
    """
    self.stepCreateProject(sequence=sequence, sequence_list=sequence_list,
                           **kw)
    project = sequence.get('project')
    sequence.edit(project2=project)

  def stepSetOrderProfile(self,sequence=None, sequence_list=None, **kw):
    """
      Set different source and destination on the order
    """
    organisation1 = sequence.get('organisation1')
    organisation2 = sequence.get('organisation2')
    project1 = sequence.get('project1')
    project2 = sequence.get('project2')
    order = sequence.get('order')
    order.edit( source_value = organisation1,
                source_section_value = organisation1,
                source_payment_value = organisation1['bank'],
                destination_value = organisation2,
                destination_section_value = organisation2,
                destination_payment_value = organisation2['bank'],
                source_project_value = project1,
                destination_project_value = project2 )
    order.setPaymentConditionEfficiency(1.0)
    self.assertTrue('Site Error' not in order.view())

  def stepCheckDeliveryBuilding(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is well created.
    """
    order = sequence.get('order')
    related_applied_rule_list = order.getCausalityRelatedValueList( \
                                   portal_type=self.applied_rule_portal_type)
    related_packing_list_list = order.getCausalityRelatedValueList( \
                                   portal_type=self.packing_list_portal_type)
    packing_list_building_state = 'confirmed'
    order_state = order.getSimulationState()
    if order_state != packing_list_building_state:
      self.assertEqual(0, len(related_packing_list_list))
    else:
      self.assertEqual(1, len(related_packing_list_list))

      packing_list = related_packing_list_list[0].getObject()
      self.assertTrue(packing_list is not None)
      sequence.edit(packing_list = packing_list)

      applied_rule = related_applied_rule_list[0].getObject()
      simulation_movement_list = applied_rule.objectValues()

      # Test that packing list is confirmed
      packing_list_state = packing_list.getSimulationState()
      self.assertEqual(packing_list_building_state, packing_list_state)

      # First, test if each Simulation Movement is related to a Packing List
      # Movement
      order_relative_url = order.getRelativeUrl()
      packing_list_relative_url = packing_list.getRelativeUrl()
      for simulation_movement in simulation_movement_list:
        order_movement_list = simulation_movement.getDeliveryValueList()
        self.assertTrue(len(order_movement_list), 1)
        order_movement = order_movement_list[0]
        self.assertTrue(order_movement is not None)
        self.assertTrue(order_movement.getRelativeUrl().\
                                      startswith(order_relative_url))
        rule_list = simulation_movement.objectValues()
        self.assertTrue(len(rule_list), 1)
        delivering_rule = rule_list[0]
        self.assertTrue(delivering_rule.getSpecialiseValue().getPortalType(),
                        'Delivering Rule')
        child_simulation_movement_list = delivering_rule.objectValues()
        self.assertTrue(len(child_simulation_movement_list), 1)
        packing_list_movement_list = child_simulation_movement_list[0].getDeliveryValueList()
        self.assertTrue(len(packing_list_movement_list), 1)
        packing_list_movement = packing_list_movement_list[0]
        self.assertTrue(packing_list_movement is not None)
        self.assertTrue(packing_list_movement.getRelativeUrl().\
                                      startswith(packing_list_relative_url))

      # Then, test if each packing list movement is equals to the sum of somes
      # Simulation Movement
      packing_list_movement_list = []
      for packing_list_line in packing_list.objectValues(
                               portal_type=self.packing_list_line_portal_type):
        packing_list_line = packing_list_line.getObject()
        sequence.edit(packing_list_line=packing_list_line)
        cell_list = [x.getObject() for x in packing_list_line.objectValues(
                               portal_type=self.packing_list_cell_portal_type)]
        if len(cell_list) == 0:
          packing_list_movement_list.append(packing_list_line)
        else:
          packing_list_movement_list.extend(cell_list)

      for packing_list_movement in packing_list_movement_list:
        related_simulation_movement_list = packing_list_movement.\
                 getDeliveryRelatedValueList(portal_type='Simulation Movement')
        self.assertTrue(len(related_simulation_movement_list)>0)
        quantity = 0
        total_price = 0
        packing_list_movement_quantity = packing_list_movement.getQuantity()
        for related_simulation_movement in related_simulation_movement_list:
          quantity += related_simulation_movement.getQuantity()
          total_price += related_simulation_movement.getPrice() *\
                         related_simulation_movement.getQuantity()
          # Test resource
          self.assertEqual(packing_list_movement.getResource(), \
                            related_simulation_movement.getResource())
          # Test resource variation
          self.assertEqual(packing_list_movement.getVariationText(), \
                            related_simulation_movement.getVariationText())
          self.assertEqual(packing_list_movement.getVariationCategoryList(), \
                        related_simulation_movement.getVariationCategoryList())
          # Test acquisition
          self.checkAcquisition(packing_list_movement,
                                related_simulation_movement)
          # Test delivery ratio
          self.assertEqual(related_simulation_movement.getQuantity() /\
                            packing_list_movement_quantity, \
                            related_simulation_movement.getDeliveryRatio())


        self.assertEqual(quantity, packing_list_movement.getQuantity())
        # Test price
        self.assertEqual(total_price / quantity, packing_list_movement.getPrice())

      sequence.edit(packing_list=packing_list)

      # Finally, test Packing List getTotalQuantity and getTotalPrice
      self.assertEqual(order.getTotalQuantity(), packing_list.getTotalQuantity())
      self.assertEqual(order.getTotalPrice(), packing_list.getTotalPrice())

  def stepModifyOrderStartDate(self, sequence=None, sequence_list=None, \
                               **kw):
    """
      Modify order start date
    """
    order = sequence.get('order')
    order.setStartDate(self.datetime + 77)

  def stepModifyOrderLineStartDate(self, sequence=None, sequence_list=None, \
                                   **kw):
    """
      Modify order line start date
    """
    order_line = sequence.get('order_line')
    order_line._setStartDate(self.datetime + 88)

  def stepModifyOrderCellStartDate(self, sequence=None, sequence_list=None, \
      **kw):
    """
      Modify order cell start date
    """
    order_line = sequence.get('order_line')
    cell_list = order_line.objectValues(portal_type=self.order_cell_portal_type)
    self.assertTrue(len(cell_list) > 0)
    order_cell = cell_list[0].getObject()
    order_cell.setStartDate(self.datetime + 99)

  def stepModifyOrderLineQuantity(self, sequence=None, sequence_list=None, \
      **kw):
    """
    Modify order line quantity
    """
    order_line = sequence.get('order_line')
    order_line.setQuantity(order_line.getQuantity() + 111)

  def stepDeleteOrderLine(self, sequence=None, sequence_list=None, **kw):
    """
      Delete order line
    """
    order_line = sequence.get('order_line')
    order_line.getParentValue().manage_delObjects([order_line.getId()])

  def stepCheckOrderConvergent(self, sequence=None, sequence_list=None, **kw):
    """
    Tests that the simulation related to the order is stable and not
    divergent
    """
    order = sequence.get('order')
    self.assertTrue(order.isConvergent())

  def stepPackingListAdoptPrevision(self,sequence=None, sequence_list=None,
                                    **kw):
    """
    Check if simulation movement are disconnected
    """
    packing_list = sequence.get('packing_list')
    packing_list.portal_workflow.doActionFor(packing_list,
                                             'adopt_prevision_action')

  non_variated_order_creation = '\
      stepCreateOrganisation1 \
      stepCreateOrganisation2 \
      stepCreateProject1 \
      stepCreateProject2 \
      stepCreateOrder \
      stepSetOrderProfile \
      stepCreateNotVariatedResource \
      stepCreateOrderLine \
      stepCheckOrderLineEmptyMatrix \
      stepSetOrderLineResource \
      stepSetOrderLineDefaultValues \
      stepCheckOrderLineDefaultValues \
      '

  variated_order_line_creation = '\
      stepCreateOrganisation1 \
      stepCreateOrganisation2 \
      stepCreateProject1 \
      stepCreateProject2 \
      stepCreateOrder \
      stepSetOrderProfile \
      stepCreateVariatedResource \
      stepCreateOrderLine \
      '
  variated_line_completion = '\
      stepSetOrderLineResource \
      stepSetOrderLineDefaultValues \
      stepCheckOrderLineDefaultValues \
      stepCheckOrderLineTotalQuantity \
      stepSetOrderLineFullVCL \
      stepCompleteOrderLineMatrix \
      '
  variated_order_creation = variated_order_line_creation + \
      variated_line_completion

  variated_line_completion_without_tic = '\
    stepSetOrderLineResource \
    stepSetOrderLineDefaultValues \
    stepCheckOrderLineDefaultValues \
    stepSetOrderLineFullVCL \
    stepCompleteOrderLineMatrix \
    '
  variated_order_creation_without_tic = variated_order_line_creation + \
    variated_line_completion_without_tic

  def stepCheckCatalogued(self, sequence=None,
                          sequence_list=None, **kw):
    """
    Check that order is catalogued
    """
    order = sequence.get('order')
    sql_connection = self.getSQLConnection()
    sql = 'SELECT simulation_state FROM catalog WHERE uid=%s' % \
                      order.getUid()
    result = sql_connection.manage_test(sql)
    simulation_state_list = [x['simulation_state'] for x in result]
    self.assertEqual(1, len(simulation_state_list))
    self.assertEqual(order.getSimulationState(),
                      simulation_state_list[0])

  def stepCheckCataloguedSimulation(self, sequence=None,
                                    sequence_list=None, **kw):
    """
    Check that simulation is catalogued
    """
    order = sequence.get('order')
    for order_movement in order.getMovementList():
      for sim_mvt in order_movement.getOrderRelatedValueList():
        sql_connection = self.getSQLConnection()
        sql = 'SELECT simulation_state FROM catalog WHERE uid=%s' % \
                          sim_mvt.getUid()
        result = sql_connection.manage_test(sql)
        simulation_state_list = [x['simulation_state'] for x in result]
        self.assertEqual(1, len(simulation_state_list))
        self.assertEqual(order.getSimulationState(),
                          simulation_state_list[0])

  def stepPackingListBuilderAlarm(self, sequence=None,
                                  sequence_list=None, **kw):
    # global builder alarm does not exist in legacy simulation
    # business templates.
    alarm = getattr(self.portal.portal_alarms, 'packing_list_builder_alarm', None)
    if alarm is not None:
      alarm.activeSense()

class TestOrder(TestOrderMixin, ERP5TypeTestCase):
  """
    Test business template erp5_trade
  """
  run_all_test = 1

  def getTitle(self):
    return "Order"

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


#   def stepCheckOrderLineCell(self, sequence=None, sequence_list=None, **kw):
#     """
#       Check cell comportment when some properties are not defined.
#     """
#     order_line = sequence.get('order_line')
#     base_id = 'movement'
#     cell_key_list = order_line.getCellKeyList(base_id=base_id)
#     # First, search a cell to test
#     for cell_key in cell_key_list:
#       if order_line.hasCell(base_id=base_id, *cell_key):
#         cell = order_line.getCell(base_id=base_id, *cell_key)
#         break
#     # Then, store his properties
#     price = cell.getProperty('price')
#     quantity = cell.getProperty('quantity')
#     # Modify, test, and restore old values
#     for new_quantity, new_price in [(None, 346), (123, None), (None, None), \
#                                     (quantity, price)]:
#       cell.edit(quantity=new_quantity, price=new_price)
#       if new_quantity == None:
#         new_quantity = 0.0
#       if new_price == None:
#         new_price = 0.0
#       self.assertEqual(new_quantity, cell.getProperty('quantity'))
#       self.assertEqual(new_price, cell.getProperty('price'))
#
#       # XXX test getTotalPrice on OrderLine

  def test_01_OrderLine_getVariationRangeCategoryList(self, quiet=0,
                                                      run=run_all_test):
    """
      Test order line getVariationRangeCategoryList.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when resource has no variation
    sequence_string = 'stepCreateOrder \
                       stepCreateOrderLine \
                       stepCheckOrderLineVRCL \
                       stepCreateNotVariatedResource \
                       stepTic \
                       stepSetOrderLineResource \
                       stepCheckOrderLineVRCL \
                       '
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has variation
    sequence_string = 'stepCreateOrder \
                       stepCreateOrderLine \
                       stepCheckOrderLineVRCL \
                       stepCreateVariatedResource \
                       stepTic \
                       stepSetOrderLineResource \
                       stepCheckOrderLineVRCL \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_02_OrderLine_getVariationRangeCategoryItemList(self, quiet=0,
                                                          run=run_all_test):
    """
      Test order line getVariationRangeCategoryItemList.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when resource has no variation
    sequence_string = 'stepCreateOrder \
                       stepCreateOrderLine \
                       stepCheckOrderLineVRCIL \
                       stepCreateNotVariatedResource \
                       stepTic \
                       stepSetOrderLineResource \
                       stepCheckOrderLineVRCIL \
                       '
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has variation
    sequence_string = 'stepCreateOrder \
                       stepCreateOrderLine \
                       stepCheckOrderLineVRCIL \
                       stepCreateVariatedResource \
                       stepTic \
                       stepSetOrderLineResource \
                       stepCheckOrderLineVRCIL \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_OrderLine_getVariationCategoryList(self):
    order_module = self.portal.getDefaultModule(portal_type=self.order_portal_type)
    order = order_module.newContent(portal_type=self.order_portal_type,
                                    specialise=self.business_process)

    resource_module = self.portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent(portal_type=self.resource_portal_type)
    resource.edit(
      industrial_phase_list=["phase1", "phase2"],
      size_list=['Baby', 'Woman']
    )
    order_line = order.newContent(
        portal_type=self.order_line_portal_type,
        resource_value=resource)

    order_line.setVariationCategoryList(['size/Baby'])
    self.assertEqual(['size/Baby'], order_line.getVariationCategoryList())
    self.assertEqual(sorted(['size']),
        sorted(order_line.getVariationBaseCategoryList()))

    order_line.setVariationCategoryList(['size/Baby', 'industrial_phase/phase1'])
    self.assertEqual(sorted(['size/Baby', 'industrial_phase/phase1']),
        sorted(order_line.getVariationCategoryList()))
    self.assertEqual(sorted(['industrial_phase', 'size']),
        sorted(order_line.getVariationBaseCategoryList()))

    self.assertEqual(['size/Baby'],
        order_line.getVariationCategoryList(base_category_list=('size',)))
    self.assertEqual([],
        order_line.getVariationCategoryList(base_category_list=('other',)))


  def test_OrderLine_getVariationCategoryItemList(self):
    order_module = self.portal.getDefaultModule(portal_type=self.order_portal_type)
    order = order_module.newContent(portal_type=self.order_portal_type,
                                    specialise=self.business_process)

    resource_module = self.portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent(portal_type=self.resource_portal_type)
    resource.edit(
      industrial_phase_list=["phase1", "phase2"],
      size_list=['Baby', 'Woman']
    )
    self.assertEqual(sorted([
        ['Industrial Phase/phase1', 'industrial_phase/phase1'],
        ['Industrial Phase/phase2', 'industrial_phase/phase2'],
        ['Size/Baby', 'size/Baby'],
        ['Size/Woman', 'size/Woman'], ]),
        sorted(resource.getVariationCategoryItemList()))

    order_line = order.newContent(
        portal_type=self.order_line_portal_type,
        resource_value=resource)

    order_line.setVariationCategoryList(['size/Baby'])
    self.assertEqual(
        [['Baby', 'size/Baby']],
        order_line.getVariationCategoryItemList())

    self.assertEqual(sorted(['size']),
        sorted(order_line.getVariationBaseCategoryList()))

    order_line.setVariationCategoryList(['size/Baby', 'industrial_phase/phase1'])
    self.assertEqual(sorted([
        ['Baby', 'size/Baby'],
        ['phase1', 'industrial_phase/phase1'], ]),
        sorted(order_line.getVariationCategoryItemList()))
    self.assertEqual(sorted(['size', 'industrial_phase']),
        sorted(order_line.getVariationBaseCategoryList()))
    self.assertEqual([['Baby', 'size/Baby']],
        order_line.getVariationCategoryItemList(base_category_list=('size',)))
    self.assertEqual([],
        order_line.getVariationCategoryItemList(base_category_list=('other',)))

  def test_05_OrderLine_Matrix(self, quiet=0, run=run_all_test):
    """
      Test order line movement matrix.
    """
    if not run: return
    sequence_list = SequenceList()
    # common part of sequence
    base_sequence  = 'stepTic \
                      stepCreateOrderLine \
                      stepCheckOrderLineEmptyMatrix \
                      stepSetOrderLineResource \
                      stepCheckOrderLineEmptyMatrix \
                      stepSetOrderLineFullVCL \
                      stepCheckOrderLineRange \
                      stepCheckOrderLineEmptyMatrix \
                      stepCompleteOrderLineMatrix \
                      stepTic \
                      stepCheckOrderLineCompleteMatrix \
                      stepSetOrderLineHalfVCL \
                      stepTic \
                      stepCheckOrderLineRange \
                      stepCheckOrderLineCompleteMatrix \
                      stepSetOrderLineEmptyVCL \
                      stepTic \
                      stepCheckOrderLineEmptyMatrix \
                      '
    # Test when resource has no variation
    sequence_string = 'stepCreateOrder \
                       stepCreateNotVariatedResource \
                      ' + base_sequence
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has variations
    sequence_string = 'stepCreateOrder \
                       stepCreateVariatedResource \
                      ' + base_sequence + \
                      'stepCheckOrderLineRange \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

#   def modifyOrderLineCellPrice(self, price):
#     """
#       Modify the properties of the first cell founded on the current
#       order line.
#     """
#     order_line = sequence.get('order_line')
#     base_id = 'movement'
#     cell_key_list = order_line.getCellKeyList(base_id=base_id)
#     # First, search a cell to test
#     cell = None
#     for cell_key in cell_key_list:
#       if order_line.hasCell(base_id=base_id, *cell_key):
#         cell = order_line.getCell(base_id=base_id, *cell_key)
#         break
#     if cell is not None:
#       # Then, store new properties
#       cell.edit(price=price)
#       self.assertEqual(price, cell.getProperty('price'))
#
# #     for new_quantity, new_price in [(None, 346), (123, None), (None, None), \
# #                                     (quantity, price)]:
#   def stepSetCellPriceToNone(self, sequence=None, sequence_list=None, **kw):
#     """
#       Set the cell price to None
#     """
#       self.modifyOrderLineCellPrice(None)
#
#   def stepSetCellQuantityToNone(self, sequence=None, sequence_list=None, **kw):
#     """
#       Set the cell price to None
#     """
#       self.modifyOrderLineCellQuantity(None)

  def test_06_OrderLine_getTotalQuantity(self, quiet=0, run=run_all_test):
    """
      Test the method getTotalQuantity on a order line.
    """
    if not run: return
    sequence_list = SequenceList()

    # Test when resource has no variation
    sequence_string = self.non_variated_order_creation + '\
                      stepCheckOrderLineTotalQuantity \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has variations
    sequence_string = self.variated_order_creation + '\
                      stepCheckOrderLineTotalQuantity \
                      '
    sequence_list.addSequenceString(sequence_string)
    # XXX test cell modification

    sequence_list.play(self)

  def test_07_OrderLine_getTotalPrice(self, quiet=0, run=run_all_test):
    """
      Test method getTotalPrice on order line.
    """
    if not run: return
    sequence_list = SequenceList()

    # Test when resource has not variation
    sequence_string = self.non_variated_order_creation + '\
                      stepCheckOrderLineTotalPrice \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has variations
    sequence_string = self.variated_order_creation + '\
                      stepCheckOrderLineTotalPrice \
                      '
    sequence_list.addSequenceString(sequence_string)
    # XXX test cell modification

    sequence_list.play(self)

  def test_07b_OrderLine_getTotalPriceAndQuantityFastParameter(self, quiet=0, run=run_all_test):
    """
      Test method getTotalPrice on order line.
    """
    if not run: return
    sequence_list = SequenceList()

    # Test when resource has variations
    sequence_string = self.variated_order_creation_without_tic + '\
                      stepCheckOrderLineTotalPriceAndQuantityFastParameter \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_08_Order_testTotalQuantity(self, quiet=0, run=run_all_test):
    """
      Test method getTotalQuantity on a order
    """
    if not run: return
    sequence_list = SequenceList()
    # Test with no order line
    sequence_string = '\
                      stepCreateOrder \
                      stepCheckOrderTotalQuantity \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has not variation
    sequence_string = self.non_variated_order_creation + '\
                      stepCheckOrderTotalQuantity \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has variations
    sequence_string = self.variated_order_creation + '\
                      stepCheckOrderTotalQuantity \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test whith multiples order line
    sequence_string = self.variated_order_creation + '\
                      stepCheckOrderTotalQuantity \
                      stepCreateNotVariatedResource \
                      stepCreateOrderLine \
                      stepTic \
                      stepSetOrderLineResource \
                      stepSetOrderLineDefaultValues \
                      stepTic \
                      stepCheckOrderTotalQuantity \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_08b_Order_testTotalPriceAndQuantityFastParameter(self, quiet=0, run=run_all_test):
    """
      Test method getTotalQuantity on a order
    """
    if not run: return
    sequence_list = SequenceList()
    # Test whith multiples order line
    sequence_string = self.variated_order_creation_without_tic + '\
                      stepCreateNotVariatedResource \
                      stepCreateOrderLine \
                      stepSetOrderLineResource \
                      stepSetOrderLineDefaultValues \
                      stepCheckOrderTotalPriceAndQuantityFastParameter \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_09_Order_testTotalPrice(self, quiet=0, run=run_all_test):
    """
      Test method getTotalPrice on a order
    """
    if not run: return
    sequence_list = SequenceList()
    # Test with no order line
    sequence_string = '\
                      stepCreateOrder \
                      stepCheckOrderTotalPrice\
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has not variation
    sequence_string = self.non_variated_order_creation + '\
                      stepCheckOrderTotalPrice \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has variations
    sequence_string = self.variated_order_creation + '\
                      stepCheckOrderTotalPrice \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test with multiples order line
    sequence_string = self.variated_order_creation + '\
                      stepCheckOrderTotalQuantity \
                      stepCreateNotVariatedResource \
                      stepCreateOrderLine \
                      stepTic \
                      stepSetOrderLineResource \
                      stepSetOrderLineDefaultValues \
                      stepTic \
                      stepCheckOrderTotalPrice \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_09b_Order_testTotalPriceWithNegativePriceOrderLine(self, quiet=0, run=run_all_test):
    """
      Test method getTotalPrice on a order
    """
    if not run: return
    sequence_list = SequenceList()
    # Test with positive price order line and negative price order line.
    sequence_string = '\
                      stepCreateOrganisation1 \
                      stepCreateOrganisation2 \
                      stepCreateProject1 \
                      stepCreateProject2 \
                      stepCreateOrder \
                      stepSetOrderProfile \
                      stepCheckOrderTotalQuantity \
                      stepCreateNotVariatedResource \
                      stepCreateOrderLine \
                      stepTic \
                      stepSetOrderLineResource \
                      stepSetOrderLineDefaultValues \
                      stepTic \
                      stepCreateNotVariatedResourceForNegativePriceOrderLine \
                      stepCreateOrderLine \
                      stepTic \
                      stepSetOrderLineResource \
                      stepSetOrderLineDefaultNegativePriceValue \
                      stepTic \
                      stepCheckOrderTotalPrice \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_10_Order_testSimulationState(self, quiet=0, run=run_all_test):
    """
      Test simulation state acquisition on Order
    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = '\
                      stepCreateOrganisation \
                      stepCreateProject \
                      ' + self.variated_order_line_creation + '\
                      stepCheckOrder \
                      stepCheckOrderInitialState \
                      stepTic \
                      stepCheckOrderLineState \
                      ' + self.variated_line_completion + '\
                      stepTic \
                      stepCheckOrderCellState \
                      stepPlanOrder \
                      stepTic \
                      stepCheckOrderPlanned \
                      stepCheckOrderLineState \
                      stepCheckOrderCellState \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_11_testPropertiesAcquisition(self, quiet=0, run=run_all_test):
    """
      Test if some properties on order line or order
      cell are well acquired.
    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = '\
                      stepCreateOrganisation \
                      stepCreateProject \
                      ' + self.variated_order_line_creation + '\
                      stepCheckOrder \
                      stepCheckOrderInitialState \
                      stepCheckOrderLineAcquisition \
                      ' + self.variated_line_completion + '\
                      stepCheckOrderCellAcquisition \
                      stepTic \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_12_testAppliedRuleGeneration(self, quiet=0, run=run_all_test):
    """
      Test generation and update of order applied rule.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test first some portal method
    sequence_string = '\
                      stepCreateOrder \
                      stepCheckPortalMethod \
                      '
    sequence_list.addSequenceString(sequence_string)

    # Test when order is cancelled
    sequence_string = '\
                      stepCreateOrganisation \
                      stepCreateProject \
                      ' + self.non_variated_order_creation + '\
                      stepCheckOrderSimulation \
                      stepPlanOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      stepOrderOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      stepCancelOrder \
                      stepTic \
                      stepTic \
                      stepCheckOrderSimulation \
                      '
    sequence_list.addSequenceString(sequence_string)

    # Test with a simply order without cell
    sequence_string = '\
                      stepCreateOrganisation \
                      stepCreateProject \
                      ' + self.non_variated_order_creation + '\
                      stepPlanOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      stepOrderOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      stepConfirmOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      '
    sequence_list.addSequenceString(sequence_string)

    # Test to confirm order without planned or ordered it
    sequence_string = '\
                      stepCreateOrganisation \
                      stepCreateProject \
                      ' + self.variated_order_line_creation + '\
                      stepSetOrderLineResource \
                      stepSetOrderLineDefaultValues \
                      stepOrderOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      stepConfirmOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      '
    sequence_list.addSequenceString(sequence_string)

    # Test to confirm order with variated resource
    sequence_string = '\
                      stepCreateOrganisation \
                      stepCreateProject \
                      ' + self.variated_order_creation + '\
                      stepTic \
                      stepOrderOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      stepConfirmOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      '
    sequence_list.addSequenceString(sequence_string)

    # Test to confirm order with multiples lines
    sequence_string = '\
                      stepCreateOrganisation \
                      stepCreateProject \
                      ' + self.variated_order_creation + '\
                      stepCreateNotVariatedResource \
                      stepTic \
                      stepCreateOrderLine \
                      stepSetOrderLineResource \
                      stepSetOrderLineDefaultValues \
                      stepTic \
                      stepOrderOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      stepConfirmOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_13_testAppliedRuleUpdate(self, quiet=0, run=run_all_test):
    """
      Test update of applied rule when order is modified.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when order is modified
    sequence_string = '\
                      stepCreateOrganisation \
                      stepCreateProject \
                      ' + self.variated_order_creation + '\
                      stepOrderOrder \
                      stepTic \
                      stepModifyOrderStartDate \
                      stepTic \
                      stepCheckOrderSimulation \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test when order line is modified
    sequence_string = '\
                      stepCreateOrganisation \
                      stepCreateProject \
                      ' + self.variated_order_creation + '\
                      stepOrderOrder \
                      stepTic \
                      stepModifyOrderLineStartDate \
                      stepTic \
                      stepCheckOrderSimulation \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test when order cell is modified
    sequence_string = '\
                      stepCreateOrganisation \
                      stepCreateProject \
                      ' + self.variated_order_creation + '\
                      stepOrderOrder \
                      stepTic \
                      stepModifyOrderCellStartDate \
                      stepTic \
                      stepCheckOrderSimulation \
                      '
    sequence_list.addSequenceString(sequence_string)

    # Test when workflow state is modified
    sequence_string = '\
                      stepCreateOrganisation \
                      stepCreateProject \
                      ' + self.variated_order_creation + '\
                      stepPlanOrder \
                      stepTic \
                      stepOrderOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      '
    sequence_list.addSequenceString(sequence_string)

    # Test when order line is deleted
    sequence_string = '\
                      stepCreateOrganisation \
                      stepCreateProject \
                      ' + self.non_variated_order_creation + '\
                      stepOrderOrder \
                      stepTic \
                      stepDeleteOrderLine \
                      stepTic \
                      stepConfirmOrder \
                      stepTic \
                      stepPackingListBuilderAlarm \
                      stepTic \
                      stepCheckOrderSimulation \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

# XXX
#   def test_14_readOnlyConfirmedOrder(self, quiet=0, run=run_all_test):
#     """
#       Test if confirmed order can not be modificated anymore.
#     """
#     if not run: return
#     self.assertTrue(1==2)

  def test_15_deliveryBuilder(self, quiet=0, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    sequence_list = SequenceList()
    # First, test if delivery buider exists
    sequence_string = '\
                      stepCheckDeliveryBuilderPresence \
                      '
    sequence_list.addSequenceString(sequence_string)

    # Test with a simply order without cell
    sequence_string = '\
                      stepCreateOrganisation1 \
                      stepCreateOrganisation2 \
                      stepCreateProject1 \
                      stepCreateProject2 \
                      stepCreateOrder \
                      stepSetOrderProfile \
                      stepCreateNotVariatedResource \
                      stepTic \
                      stepCreateOrderLine \
                      stepSetOrderLineResource \
                      stepSetOrderLineDefaultValues \
                      stepOrderOrder \
                      stepTic \
                      stepCheckDeliveryBuilding \
                      stepConfirmOrder \
                      stepTic \
                      stepPackingListBuilderAlarm \
                      stepTic \
                      stepCheckDeliveryBuilding \
                      '
    sequence_list.addSequenceString(sequence_string)

    # Test to confirm order with variated resource
    sequence_string = '\
                      stepCreateOrganisation1 \
                      stepCreateOrganisation2 \
                      stepCreateProject1 \
                      stepCreateProject2 \
                      stepCreateOrder \
                      stepSetOrderProfile \
                      stepCreateVariatedResource \
                      stepTic \
                      stepCreateOrderLine \
                      ' + self.variated_line_completion + '\
                      stepTic \
                      stepOrderOrder \
                      stepTic \
                      stepCheckDeliveryBuilding \
                      stepConfirmOrder \
                      stepTic \
                      stepPackingListBuilderAlarm \
                      stepTic \
                      stepCheckDeliveryBuilding \
                      '
    sequence_list.addSequenceString(sequence_string)

    # Test to confirm order with multiples lines
    sequence_string = '\
                      stepCreateOrganisation1 \
                      stepCreateOrganisation2 \
                      stepCreateProject1 \
                      stepCreateProject2 \
                      stepCreateOrder \
                      stepSetOrderProfile \
                      stepCreateVariatedResource \
                      stepTic \
                      stepCreateOrderLine \
                      ' + self.variated_line_completion + '\
                      stepCreateNotVariatedResource \
                      stepTic \
                      stepCreateOrderLine \
                      stepSetOrderLineResource \
                      stepSetOrderLineDefaultValues \
                      stepTic \
                      stepOrderOrder \
                      stepTic \
                      stepCheckDeliveryBuilding \
                      stepConfirmOrder \
                      stepTic \
                      stepPackingListBuilderAlarm \
                      stepTic \
                      stepCheckDeliveryBuilding \
                      '
    sequence_list.addSequenceString(sequence_string)

    # Test with a order with 2 lines and the same not variated resource
    sequence_string = '\
                      stepCreateOrganisation1 \
                      stepCreateOrganisation2 \
                      stepCreateProject1 \
                      stepCreateProject2 \
                      stepCreateOrder \
                      stepSetOrderProfile \
                      stepCreateNotVariatedResource \
                      stepTic \
                      stepCreateOrderLine \
                      stepSetOrderLineResource \
                      stepSetOrderLineDefaultValues \
                      stepCreateOrderLine \
                      stepSetOrderLineResource \
                      stepSetOrderLineDefaultValues \
                      stepOrderOrder \
                      stepTic \
                      stepCheckDeliveryBuilding \
                      stepConfirmOrder \
                      stepTic \
                      stepPackingListBuilderAlarm \
                      stepTic \
                      stepCheckDeliveryBuilding \
                      '
    sequence_list.addSequenceString(sequence_string)

    # Test with a order with 2 lines and the same variated resource
    sequence_string = '\
                      stepCreateOrganisation1 \
                      stepCreateOrganisation2 \
                      stepCreateProject1 \
                      stepCreateProject2 \
                      stepCreateOrder \
                      stepSetOrderProfile \
                      stepCreateVariatedResource \
                      stepTic \
                      stepCreateOrderLine \
                      ' + self.variated_line_completion + '\
                      stepCreateOrderLine \
                      ' + self.variated_line_completion + '\
                      stepTic \
                      stepOrderOrder \
                      stepTic \
                      stepCheckDeliveryBuilding \
                      stepConfirmOrder \
                      stepTic \
                      stepPackingListBuilderAlarm \
                      stepTic \
                      stepCheckDeliveryBuilding \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_16_deliveryBuilderWithNoTic(self, quiet=0, run=run_all_test):
    """
      Test generation of delivery list with
      only a few tic
    """
    if not run: return
    sequence_list = SequenceList()

    # XXX Does not work yet
    # Test to confirm order without doing any tic
    # Except after creating organisations

    sequence_string = '\
                      stepCreateOrganisation1 \
                      stepCreateOrganisation2 \
                      stepCreateProject1 \
                      stepCreateProject2 \
                      stepTic \
                      stepCreateOrder \
                      stepSetOrderProfile \
                      stepCreateVariatedResource \
                      stepCreateOrderLine \
                      ' + self.variated_line_completion + '\
                      stepCreateNotVariatedResource \
                      stepCreateOrderLine \
                      stepSetOrderLineResource \
                      stepSetOrderLineDefaultValues \
                      stepOrderOrder \
                      stepCheckDeliveryBuilding \
                      stepConfirmOrder \
                      stepTic \
                      stepPackingListBuilderAlarm \
                      stepTic \
                      stepCheckDeliveryBuilding \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_17_orderExpand(self, quiet=0, run=run_all_test):
    """
    This tests the behaviour of expand.
    First, without delivery:
      - create an order, apply a rule
      - modify the order line, expand the rule
      - check that the simulation is not Divergent and Stable (simulation must
        match order value)

    Second, with delivery:
      - create an order, apply a rule
      - build a packing list
      - modify the order line, expand the rule
      - adopt prevision to fix the delivery
      - check that the simulation is not Divergent and Stable (simulation must
        match delivery value)
    """
    if not run: return
    sequence_list = SequenceList()

    sequence_string = '\
                      stepCreateOrganisation1 \
                      stepCreateOrganisation2 \
                      stepCreateProject1 \
                      stepCreateProject2 \
                      stepCreateOrder \
                      stepSetOrderProfile \
                      stepCreateNotVariatedResource \
                      stepTic \
                      stepCreateOrderLine \
                      stepSetOrderLineResource \
                      stepSetOrderLineDefaultValues \
                      stepOrderOrder \
                      stepTic \
                      stepModifyOrderLineQuantity \
                      stepTic \
                      stepCheckDeliveryBuilding \
                      stepConfirmOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      stepCheckOrderConvergent \
                      '
    sequence_list.addSequenceString(sequence_string)
    # XXX XXX FIXME
    # The idea of this test is to create a PackingList
    # Before the Order is in state confirmed.
    # And then, check the behaviour of isDivergent
    # when the Order is modified
    sequence_string = '\
                      stepCreateOrganisation1 \
                      stepCreateOrganisation2 \
                      stepCreateProject1 \
                      stepCreateProject2 \
                      stepCreateOrder \
                      stepSetOrderProfile \
                      stepCreateNotVariatedResource \
                      stepTic \
                      stepCreateOrderLine \
                      stepSetOrderLineResource \
                      stepSetOrderLineDefaultValues \
                      stepOrderOrder \
                      stepTic \
                      stepConfirmOrder \
                      stepTic \
                      stepCheckDeliveryBuilding \
                      stepModifyOrderLineQuantity \
                      stepTic \
                      stepPackingListAdoptPrevision \
                      stepTic \
                      stepCheckOrderSimulation \
                      stepCheckDeliveryBuilding \
                      stepCheckOrderConvergent \
                      '
#     sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

#   def test_16_packingListOrderAcquisition(self, quiet=0, run=run_all_test):
#     """
#       Test if packing list get some properties from order.
#     """
#     if not run: return
#     self.assertTrue(1==2)

  def test_18_SimulationStateIndexation(self, quiet=0, run=run_all_test):
    """
    Test that the simulation state is well indexed.
    """
    if not run: return

    sequence_list = SequenceList()

    sequence_string = '\
                      stepCreateOrganisation \
                      stepCreateProject \
                      ' + self.non_variated_order_creation + '\
                      stepTic \
                      stepCheckCatalogued \
                      stepCheckCataloguedSimulation \
                      stepPlanOrder \
                      stepTic \
                      stepCheckCatalogued \
                      stepCheckCataloguedSimulation \
                      stepOrderOrder \
                      stepTic \
                      stepCheckCatalogued \
                      stepCheckCataloguedSimulation \
                      stepCancelOrder \
                      stepTic \
                      stepCheckCatalogued \
                      stepCheckCataloguedSimulation \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_19_getMovementList(self, quiet=0, run=run_all_test):
    """
    Check getMovementList.
    Verify that it supports hierarchical order lines.
    Check that order cells are returned when defined on a leaf line, and not
    returned when defined on a non leaf line.
    """
    if not run: return

    portal = self.getPortal()
    order_module = portal.getDefaultModule(portal_type=self.order_portal_type)
    order = order_module.newContent(portal_type=self.order_portal_type,
                                    specialise=self.business_process)
    # No line, no movement
    self.assertEqual(0, len(order.getMovementList()))

    # One line is considered as a movement
    order_line = order.newContent(portal_type=self.order_line_portal_type)
    self.assertEqual(1, len(order.getMovementList()))

    # If a sub line is created, its parent should not be considered
    # as a movement
    sub_order_line = order_line.newContent(
               portal_type=self.order_line_portal_type)
    self.assertEqual(1, len(order.getMovementList()))

    # Create another subline to be sure it increases the line count
    sub_order_line = order_line.newContent(
               portal_type=self.order_line_portal_type)
    self.assertEqual(2, len(order.getMovementList()))

    # Create recursively sub lines, and check that the ovement number
    # is still the same.
    for i in range(5):
      sub_order_line = sub_order_line.newContent(
          portal_type=self.order_line_portal_type)
      self.assertEqual(2, len(order.getMovementList()))

    # Create a variated resource
    resource_module = portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent(portal_type=self.resource_portal_type)
    resource.edit(
      industrial_phase_list=["phase1", "phase2"],
      size_list=self.size_list,
    )

    # Prepare line variation category list
    order_line_vcl = []
    resource_vbcl = resource.getVariationBaseCategoryList()
    for vbc in resource_vbcl:
      resource_vcl = list(resource.getVariationCategoryList(
                                  base_category_list=[vbc],
                                  omit_individual_variation=0))
      resource_vcl.sort()
      order_line_vcl.extend(self.splitList(resource_vcl)[0])

    # Create cell on the deepest sub line.
    # Check that those cells increase the movement count
    sub_order_line.setResourceValue(resource)
    sub_order_line.setVariationCategoryList(order_line_vcl)
    self.assertEqual(1, len(order.getMovementList()))

    base_id = 'movement'
    cell_key_list = list(sub_order_line.getCellKeyList(base_id=base_id))
    cell_key_list.sort()
    for cell_key in cell_key_list:
      cell = sub_order_line.newCell(base_id=base_id,
                                portal_type=self.order_cell_portal_type,
                                *cell_key)
    self.assertEqual(2-1+len(cell_key_list), len(order.getMovementList()))

    # Check that cells defined on a non leaf line are not returned.
    order_line.setResourceValue(resource)
    order_line.setVariationCategoryList(order_line_vcl)
    self.assertEqual(2-1+len(cell_key_list), len(order.getMovementList()))

    base_id = 'movement'
    cell_key_list = list(order_line.getCellKeyList(base_id=base_id))
    cell_key_list.sort()
    for cell_key in cell_key_list:
      cell = order_line.newCell(base_id=base_id,
                                portal_type=self.order_cell_portal_type,
                                *cell_key)
    self.assertEqual(2-1+len(cell_key_list), len(order.getMovementList()))

    # Make sure that portal_type argument works correctly.
    self.assertEqual(len(order.getMovementList(portal_type='Sale Order Line')),
                     len([movement
                          for movement in order.getMovementList()
                          if movement.portal_type=='Sale Order Line']))
    self.assertEqual(len(order.getMovementList(portal_type='Sale Order Cell')),
                     len([movement
                          for movement in order.getMovementList()
                          if movement.portal_type=='Sale Order Cell']))
    self.assertEqual(len(order.getMovementList(portal_type=['Sale Order Line',
                                                            'Sale Order Cell'])),
                     len([movement
                          for movement in order.getMovementList()
                          if movement.portal_type in ('Sale Order Line',
                                                      'Sale Order Cell')]))

  def test_19b_getTotalQuantityAndPrice(self, quiet=0, run=run_all_test):
    """
    Check getTotalQuantity and getTotalPrice.
    Check isMovement.
    Verify that it supports hierarchical order lines.
    Note that this depends on isMovement and Order Line reindexation
    """
    if not run: return

    portal = self.portal
    base_id = 'movement'
    order_line_vcl=['size/Baby']
    section = portal.organisation_module.newContent(
      portal_type='Organisation')
    order_module = portal.getDefaultModule(portal_type=self.order_portal_type)
    order = order_module.newContent(portal_type=self.order_portal_type,
                                    destination_section_value=section,
                                    destination_value=section,
                                    specialise=self.business_process)
    # No line, no movement
    self.assertEqual(order.getTotalQuantity(fast=0), 0)
    self.assertEqual(order.getTotalQuantity(fast=1), 0)
    self.assertEqual(order.getTotalPrice(fast=0), 0)
    self.assertEqual(order.getTotalPrice(fast=1), 0)

    # Create a variated resource
    resource_module = portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent(
        portal_type=self.resource_portal_type,
        variation_base_category_list=['size'],
        size_list=self.size_list)

    # One line is considered as a movement
    order_line = order.newContent(
        portal_type=self.order_line_portal_type,
        resource_value=resource,
        price=2,
        quantity=3)
    self.tic()

    self.assertEqual(order_line.isMovement(), True)

    self.assertEqual(order.getTotalQuantity(fast=0), 3)
    self.assertEqual(order.getTotalQuantity(fast=1), 3)
    self.assertEqual(order.getTotalPrice(fast=0), 6)
    self.assertEqual(order.getTotalPrice(fast=1), 6)

    self.assertEqual(order_line.getTotalQuantity(fast=0), 3)
    self.assertEqual(order_line.getTotalQuantity(fast=1), 3)
    self.assertEqual(order_line.getTotalPrice(fast=0), 6)
    self.assertEqual(order_line.getTotalPrice(fast=1), 6)

    # add cell to line, line is not a movement anymore
    order_line.setVariationCategoryList(order_line_vcl)
    cell_key_list = order_line.getCellKeyList(base_id=base_id)
    self.assertTrue(len(cell_key_list) > 0)
    cell_key = cell_key_list[0]
    cell = order_line.newCell(
        base_id=base_id,
        portal_type=self.order_cell_portal_type,
        *cell_key)
    cell.edit(mapped_value_property_list=['price', 'quantity'],
        price=3, quantity=4,
        predicate_category_list=cell_key,
        variation_category_list=cell_key)
    self.tic()

    self.assertEqual(order_line.isMovement(), False)
    self.assertEqual(cell.isMovement(), True)

    self.assertEqual(order.getTotalQuantity(fast=0), 4)
    self.assertEqual(order.getTotalQuantity(fast=1), 4)
    self.assertEqual(order.getTotalPrice(fast=0), 12)
    self.assertEqual(order.getTotalPrice(fast=1), 12)

    self.assertEqual(order_line.getTotalQuantity(fast=0), 4)
    self.assertEqual(order_line.getTotalQuantity(fast=1), 4)
    self.assertEqual(order_line.getTotalPrice(fast=0), 12)
    self.assertEqual(order_line.getTotalPrice(fast=1), 12)

    self.assertEqual(cell.getTotalQuantity(), 4)
    self.assertEqual(cell.getTotalPrice(), 12)

    # if cell has no price, the total price is None, but a default value can be
    # provided
    cell.setPrice(None)
    self.tic()

    self.assertEqual(order_line.isMovement(), False)
    self.assertEqual(cell.isMovement(), True)

    self.assertEqual(order.getTotalQuantity(fast=0), 4)
    self.assertEqual(order.getTotalQuantity(fast=1), 4)
    self.assertEqual(order.getTotalPrice(fast=0), 0)
    self.assertEqual(order.getTotalPrice(fast=1), 0)

    self.assertEqual(order_line.getTotalQuantity(fast=0), 4)
    self.assertEqual(order_line.getTotalQuantity(fast=1), 4)
    self.assertEqual(order_line.getTotalPrice(fast=0), 0)
    self.assertEqual(order_line.getTotalPrice(fast=1), 0)

    self.assertEqual(cell.getTotalQuantity(), 4)
    self.assertEqual(cell.getTotalPrice(), 0)

    # restore the price on the line
    cell.setPrice(3)
    self.tic()

    # add sub_line to line, cell and line are not movements
    sub_order_line = order_line.newContent(
        portal_type=self.order_line_portal_type,
        price=4,
        quantity=5)
    self.tic()

    self.assertEqual(order_line.isMovement(), False)
    self.assertEqual(cell.isMovement(), False)
    self.assertEqual(sub_order_line.isMovement(), True)

    self.assertEqual(order.getTotalQuantity(fast=0), 5)
    self.assertEqual(order.getTotalQuantity(fast=1), 5)
    self.assertEqual(order.getTotalPrice(fast=0), 20)
    self.assertEqual(order.getTotalPrice(fast=1), 20)

    self.assertEqual(order_line.getTotalQuantity(fast=0), 5)
    self.assertEqual(order_line.getTotalQuantity(fast=1), 5)
    self.assertEqual(order_line.getTotalPrice(fast=0), 20)
    self.assertEqual(order_line.getTotalPrice(fast=1), 20)

    self.assertEqual(cell.getTotalQuantity(), 0)
    self.assertEqual(cell.getTotalPrice(), 0)

    self.assertEqual(sub_order_line.getTotalQuantity(fast=0), 5)
    self.assertEqual(sub_order_line.getTotalQuantity(fast=1), 5)
    self.assertEqual(sub_order_line.getTotalPrice(fast=0), 20)
    self.assertEqual(sub_order_line.getTotalPrice(fast=1), 20)

    # if this line has no price, getTotalPrice returns 0
    sub_order_line.setPrice(None)
    self.tic()
    self.assertEqual(order_line.isMovement(), False)
    self.assertEqual(cell.isMovement(), False)
    self.assertEqual(sub_order_line.isMovement(), True)

    self.assertEqual(order.getTotalQuantity(fast=0), 5)
    self.assertEqual(order.getTotalQuantity(fast=1), 5)
    self.assertEqual(order.getTotalPrice(fast=0), 0)
    self.assertEqual(order.getTotalPrice(fast=1), 0)

    self.assertEqual(order_line.getTotalQuantity(fast=0), 5)
    self.assertEqual(order_line.getTotalQuantity(fast=1), 5)
    self.assertEqual(order_line.getTotalPrice(fast=0), 0)
    self.assertEqual(order_line.getTotalPrice(fast=1), 0)

    self.assertEqual(cell.getTotalQuantity(), 0)
    self.assertEqual(cell.getTotalPrice(), 0)

    self.assertEqual(sub_order_line.getTotalQuantity(fast=0), 5)
    self.assertEqual(sub_order_line.getTotalQuantity(fast=1), 5)
    self.assertEqual(sub_order_line.getTotalPrice(fast=0), 0)
    self.assertEqual(sub_order_line.getTotalPrice(fast=1), 0)

    # restore price on the sub line
    sub_order_line.setPrice(4)
    self.tic()


    # add sub_cell to sub_line, only sub_cell is movement
    sub_order_line.setVariationCategoryList(order_line_vcl)
    sub_cell_key = sub_order_line.getCellKeyList(base_id=base_id)[0]
    sub_cell = sub_order_line.newCell(
        base_id=base_id,
        portal_type=self.order_cell_portal_type,
        *cell_key)
    sub_cell.edit(mapped_value_property_list=['price', 'quantity'],
        price=5, quantity=6,
        predicate_category_list=cell_key,
        variation_category_list=cell_key)
    self.tic()

    self.assertEqual(order_line.isMovement(), False)
    self.assertEqual(cell.isMovement(), False)
    self.assertEqual(sub_order_line.isMovement(), False)
    self.assertEqual(sub_cell.isMovement(), True)

    self.assertEqual(order.getTotalQuantity(fast=0), 6)
    self.assertEqual(order.getTotalQuantity(fast=1), 6)
    self.assertEqual(order.getTotalPrice(fast=0), 30)
    self.assertEqual(order.getTotalPrice(fast=1), 30)

    self.assertEqual(order_line.getTotalQuantity(fast=0), 6)
    self.assertEqual(order_line.getTotalQuantity(fast=1), 6)
    self.assertEqual(order_line.getTotalPrice(fast=0), 30)
    self.assertEqual(order_line.getTotalPrice(fast=1), 30)

    self.assertEqual(cell.getTotalQuantity(), 0)
    self.assertEqual(cell.getTotalPrice(), 0)

    self.assertEqual(sub_order_line.getTotalQuantity(fast=0), 6)
    self.assertEqual(sub_order_line.getTotalQuantity(fast=1), 6)
    self.assertEqual(sub_order_line.getTotalPrice(fast=0), 30)
    self.assertEqual(sub_order_line.getTotalPrice(fast=1), 30)

    self.assertEqual(sub_cell.getTotalQuantity(), 6)
    self.assertEqual(sub_cell.getTotalPrice(), 30)

    # delete sub_line, cell is movement again
    order_line.manage_delObjects([sub_order_line.getId()])
    self.tic()

    self.assertEqual(order_line.isMovement(), False)
    self.assertEqual(cell.isMovement(), True)

    self.assertEqual(order.getTotalQuantity(fast=0), 4)
    self.assertEqual(order.getTotalQuantity(fast=1), 4)
    self.assertEqual(order.getTotalPrice(fast=0), 12)
    self.assertEqual(order.getTotalPrice(fast=1), 12)

    self.assertEqual(order_line.getTotalQuantity(fast=0), 4)
    self.assertEqual(order_line.getTotalQuantity(fast=1), 4)
    self.assertEqual(order_line.getTotalPrice(fast=0), 12)
    self.assertEqual(order_line.getTotalPrice(fast=1), 12)

    self.assertEqual(cell.getTotalQuantity(), 4)
    self.assertEqual(cell.getTotalPrice(), 12)

    # delete cell, line is movement again
    order_line.manage_delObjects([cell.getId()])
    order_line.setVariationCategoryList([])
    self.tic()

    self.assertEqual(order_line.isMovement(), True)

    self.assertEqual(order.getTotalQuantity(fast=0), 3)
    self.assertEqual(order.getTotalQuantity(fast=1), 3)
    self.assertEqual(order.getTotalPrice(fast=0), 6)
    self.assertEqual(order.getTotalPrice(fast=1), 6)

    self.assertEqual(order_line.getTotalQuantity(fast=0), 3)
    self.assertEqual(order_line.getTotalQuantity(fast=1), 3)
    self.assertEqual(order_line.getTotalPrice(fast=0), 6)
    self.assertEqual(order_line.getTotalPrice(fast=1), 6)

  def stepCreateSubOrderLine(self,sequence=None, sequence_list=None, **kw):
    """
      Create a empty order line
    """
    order = sequence.get('order')
    # Create sub line in the first order line
    order_line = \
        order.contentValues(portal_type=self.order_line_portal_type)[0]
    sub_order_line = order_line.newContent(
        portal_type=self.order_line_portal_type,
        title="Sub Order Line")
    sequence.edit(order_line=sub_order_line,
                  sub_order_line=sub_order_line)

  def stepCreateSubSubOrderLine(self,sequence=None, sequence_list=None, **kw):
    """
      Create a empty order line
    """
    sub_order_line = sequence.get('sub_order_line')
    # Create sub line in the first sub order line
    order_line = sub_order_line.newContent(
        portal_type=self.order_line_portal_type,
        title="Sub Order Line")
    sequence.edit(order_line=order_line)

  def test_20_testHierarchicalOrderAppliedRuleGeneration(self, quiet=0,
                                                         run=run_all_test):
    """
    Test generation and update of an hierarchical order applied rule.
    """
    if not run: return
    sequence_list = SequenceList()

    hierarchical_order_creation = '\
        stepCreateOrder \
        stepCreateNotVariatedResource \
        stepCreateOrderLine \
        stepCheckOrderLineEmptyMatrix \
        stepSetOrderLineResource \
        stepSetOrderLineDefaultValues \
        stepCheckOrderLineDefaultValues \
        \
        stepCreateSubOrderLine \
        stepCheckOrderLineEmptyMatrix \
        stepSetOrderLineResource \
        stepSetOrderLineDefaultValues \
        stepCheckOrderLineDefaultValues \
        \
        stepCreateSubSubOrderLine \
        stepCheckOrderLineEmptyMatrix \
        stepSetOrderLineResource \
        stepSetOrderLineDefaultValues \
        stepCheckOrderLineDefaultValues \
        \
        stepCreateSubSubOrderLine \
        stepCheckOrderLineEmptyMatrix \
        stepSetOrderLineResource \
        stepSetOrderLineDefaultValues \
        stepCheckOrderLineDefaultValues \
        \
        stepCreateSubOrderLine \
        stepCheckOrderLineEmptyMatrix \
        stepSetOrderLineResource \
        stepSetOrderLineDefaultValues \
        stepCheckOrderLineDefaultValues \
        \
        stepCreateOrderLine \
        stepCheckOrderLineEmptyMatrix \
        stepSetOrderLineResource \
        stepSetOrderLineDefaultValues \
        stepCheckOrderLineDefaultValues \
        '

    # Test when order is cancelled
    sequence_string = '\
                      stepCreateOrganisation \
                      stepCreateProject \
                      ' + hierarchical_order_creation + '\
                      stepCheckOrderSimulation \
                      stepPlanOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      stepOrderOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      stepCancelOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)


  def test_order_cell_getTotalPrice(self):
    # test getTotalPrice and getTotalQuantity on a line with cells
    # More precisely, it tests a previous bug where creating a line with
    # quantity X and then adding a cell with quantity, cell.edit where
    # comparing quantities (X and X) and didn't really edit the quantity.
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',
                    variation_base_category_list=['size'])

    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              title='Order')
    line = order.newContent(portal_type=self.order_line_portal_type,
                            resource_value=resource,
                            quantity=10,
                            price=3)
    self.assertEqual(10, line.getTotalQuantity())
    self.assertEqual(10 * 3, line.getTotalPrice())
    self.assertEqual(10, order.getTotalQuantity())
    self.assertEqual(10 * 3, order.getTotalPrice())

    line.setVariationCategoryList(['size/Baby', 'size/Child/32'])
    self.assertEqual(0, line.getTotalQuantity())
    self.assertEqual(0, line.getTotalPrice())
    self.assertEqual(0, order.getTotalQuantity())
    self.assertEqual(0, order.getTotalPrice())

    self.assertTrue(line.hasInRange('size/Baby', base_id='movement'))
    cell_baby = line.newCell('size/Baby', base_id='movement',
                             portal_type=self.order_cell_portal_type)
    self.assertEqual(0, cell_baby.getProperty("quantity"))
    self.assertEqual(0, cell_baby.getQuantity())
    self.assertFalse(cell_baby.hasProperty('quantity'))
    cell_baby.edit(quantity=10,
                   price=4,
                   variation_category_list=['size/Baby'],
                   mapped_value_property_list=['quantity', 'price'],
                   edit_order=[])
    self.assertEqual(10, cell_baby.getQuantity())
    self.assertEqual(4, cell_baby.getPrice())

    self.assertTrue(line.hasInRange('size/Child/32', base_id='movement'))
    cell_child_32 = line.newCell('size/Child/32', base_id='movement',
                                 portal_type=self.order_cell_portal_type)
    self.assertEqual(0, cell_child_32.getQuantity())
    cell_child_32.edit(quantity=20,
                       price=5,
                       variation_category_list=['size/Child/32'],
                       mapped_value_property_list=['quantity', 'price'],
                       edit_order=[])
    self.assertEqual(20, cell_child_32.getQuantity())
    self.assertEqual(5, cell_child_32.getPrice())

    self.assertEqual(10 + 20, line.getTotalQuantity())
    self.assertEqual(10*4 + 20*5, line.getTotalPrice())

    self.assertEqual(10 + 20, order.getTotalQuantity())
    self.assertEqual(10*4 + 20*5, order.getTotalPrice())

  def test_order_payment_condition_copied(self):
    # Payment Condition should be copied in the packing list
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',)
    client = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Client')
    vendor = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Vendor')
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              title='Order',
                              start_date=self.datetime,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client)
    line = order.newContent(portal_type=self.order_line_portal_type,
                            resource_value=resource,
                            quantity=10,
                            price=3)
    # set properties, on the default payment condition
    order.setDefaultPaymentConditionQuantity(10)
    self.assertEqual(1, len(order.contentValues(
                              portal_type='Payment Condition')))

    order.confirm()
    self.tic()
    self.stepPackingListBuilderAlarm()
    self.tic()
    related_packing_list = order.getCausalityRelatedValue(
                                   portal_type=self.packing_list_portal_type)
    self.assertNotEquals(related_packing_list, None)
    self.assertEqual(1, len(related_packing_list.contentValues(
                                          portal_type='Payment Condition')))

  def test_Order_viewAsODT(self):
    # tests order printout
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',)
    client = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Client')
    vendor = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Vendor')
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              title='Order',
                              start_date=self.datetime,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client)
    order.setReference('OrderReference')
    line = order.newContent(portal_type=self.order_line_portal_type,
                            resource_value=resource,
                            quantity=10,
                            price=3)
    order.confirm()
    self.tic()

    odt = order.Order_viewAsODT()
    from Products.ERP5OOo.tests.utils import Validator
    odf_validator = Validator()
    err_list = odf_validator.validate(odt)
    if err_list:
      self.fail(''.join(err_list))
    # The name of the printout is the reference of the order
    content_disposition = self.portal.REQUEST.RESPONSE.getHeader('content-disposition')
    self.assertEqual(content_disposition, 'attachment; filename="OrderReference.odt"')

  def test_Order_viewAsODT_person(self):
    # test order printout with a person as destination
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',)
    client = self.portal.person_module.newContent(
                              portal_type='Person', title='Client')
    vendor = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Vendor')
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              title='Order',
                              start_date=self.datetime,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client)
    line = order.newContent(portal_type=self.order_line_portal_type,
                            resource_value=resource,
                            quantity=10,
                            price=3)
    order.confirm()
    self.tic()

    odt = order.Order_viewAsODT()
    from Products.ERP5OOo.tests.utils import Validator
    odf_validator = Validator()
    err_list = odf_validator.validate(odt)
    if err_list:
      self.fail(''.join(err_list))


  def test_Order_viewAsODT_image(self):
    # tests order printout with images
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',)
    image = FileUpload(os.path.join(os.path.dirname(__file__),
                      'test_data', 'images', 'erp5_logo.png'))
    client = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Client',
                              default_image_file=image)
    vendor = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Vendor',
                              default_image_file=image)
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              title='Order',
                              start_date=self.datetime,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client)
    line = order.newContent(portal_type=self.order_line_portal_type,
                            resource_value=resource,
                            quantity=10,
                            price=3)
    order.confirm()
    self.tic()

    odt = order.Order_viewAsODT()
    from Products.ERP5OOo.tests.utils import Validator
    odf_validator = Validator()
    err_list = odf_validator.validate(odt)
    if err_list:
      self.fail(''.join(err_list))

  def test_Order_viewAsODT_big_image(self):
    # tests order printout with big images (that has Pdata)
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',)
    image = FileUpload(os.path.join(os.path.dirname(__file__),
                      'test_data', 'images', 'erp5_logo.bmp'))
    client = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Client',
                              default_image_file=image)
    from OFS.Image import Pdata
    self.assertTrue(isinstance(client.getDefaultImageValue().data, Pdata))
    vendor = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Vendor',
                              default_image_file=image)
    from OFS.Image import Pdata
    self.assertTrue(isinstance(vendor.getDefaultImageValue().data, Pdata))
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              title='Order',
                              start_date=self.datetime,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client)
    line = order.newContent(portal_type=self.order_line_portal_type,
                            resource_value=resource,
                            quantity=10,
                            price=3)
    order.confirm()
    self.tic()

    odt = order.Order_viewAsODT()
    from Products.ERP5OOo.tests.utils import Validator
    odf_validator = Validator()
    err_list = odf_validator.validate(odt)
    if err_list:
      self.fail(''.join(err_list))

  def test_Order_viewAsODT_non_ascii(self):
    # test order printout with non ascii characters
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Résource',)

    # TODO: once we have updated order printout to use trade model lines, test
    # the case of a trade model line with non ascii title on resource.

    # tax = self.portal.tax_module.newContent(portal_type='Tax', title='tàx')

    client = self.portal.organisation_module.newContent(
                              portal_type='Organisation',
                              title='Cliént',
                              default_address_city='Vïllà')
    vendor = self.portal.organisation_module.newContent(
                              portal_type='Organisation',
                              title='Vendœr',
                              default_address_city='Vïllà')
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              title='Ordàr',
                              start_date=self.datetime,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client)
    line = order.newContent(portal_type=self.order_line_portal_type,
                            reference='à',
                            resource_value=resource,
                            quantity=10,
                            price=3)

    # see TODO above
    #tax_line = order.newContent(portal_type='Tax Line',
    #                            resource_value=tax,
    #                            quantity=30,
    #                            price=.26)

    order.confirm()
    self.tic()

    odt = order.Order_viewAsODT()
    from Products.ERP5OOo.tests.utils import Validator
    odf_validator = Validator()
    err_list = odf_validator.validate(odt)
    if err_list:
      self.fail(''.join(err_list))

  def test_Order_viewAsODT_hierarchical(self):
    # tests order printout with hierearchical order (with lines inside lines)
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',)
    client = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Client')
    vendor = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Vendor')
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              title='Order',
                              start_date=self.datetime,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client)
    line = order.newContent(portal_type=self.order_line_portal_type,
                            description='Content')
    if self.order_line_portal_type not in [x.getId() for x in
                                           line.allowedContentTypes()]:
      return # skip this test if hierarchical orders are not available (eg.
             # for Purchase Order)

    line = line.newContent(portal_type=self.order_line_portal_type,
                            resource_value=resource,
                            quantity=10,
                            price=3)
    order.confirm()
    self.tic()

    odt = order.Order_viewAsODT()
    from Products.ERP5OOo.tests.utils import Validator
    odf_validator = Validator()
    err_list = odf_validator.validate(odt)
    if err_list:
      self.fail(''.join(err_list))

  # TODO: test with cells ?

  def test_subcontent_reindexing(self):
    """Tests, that modification on Order are propagated to lines and cells
    during reindxation"""
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process)
    order_line = order.newContent(portal_type=self.order_line_portal_type)
    inner_order_line = order_line.newContent(
            portal_type=self.order_line_portal_type,
            start_date=self.datetime)
    order_cell = order_line.newContent(
        portal_type=self.order_cell_portal_type)
    self._testSubContentReindexing(order, [order_line, inner_order_line,
      order_cell])

  def test_sale_order_view_parent_domain(self):
    # test that arent domain can be used by non manager users
    uf = self.portal.acl_users
    uf._doAddUser(self.id(), '', ['Author', 'Member', 'Assignee'], [])
    user = uf.getUserById(self.id()).__of__(uf)

    newSecurityManager(None, user)
    sale_order = self.portal.sale_order_module.newContent(
                              portal_type='Sale Order')
    sale_order.newContent(portal_type='Sale Order Line')

    # XXX: hard coding a selection_name is bad
    selection_name = 'SaleOrder_view_listbox_selection'
    self.assertEqual(selection_name,
        sale_order.SaleOrder_view.listbox.get_value('selection_name'))

    # activate report tree
    self.portal.portal_selections.setListboxDisplayMode(
        self.portal.REQUEST, 'ReportTreeMode', selection_name)
    self.portal.portal_selections.setSelectionParamsFor(
        selection_name=selection_name,
        params=dict(report_path="parent_domain",
                    report_opened=1,
                    report_tree_mode=1))

    html = sale_order.view()
    # report tree is used, and we had no error
    self.assertTrue('listbox-table-report-tree-selection-cell' in html)
    self.assertTrue('Object Tree' in html)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestOrder))
  return suite
