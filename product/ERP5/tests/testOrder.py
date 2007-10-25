##############################################################################
#
# Copyright (c) 2004, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from DateTime import DateTime
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.CMFCore.utils import getToolByName

class TestOrderMixin:

  default_quantity = 99
  default_price = 555
  resource_portal_type = 'Apparel Model'
  order_portal_type = 'Sale Order'
  order_line_portal_type = 'Sale Order Line'
  order_cell_portal_type = 'Sale Order Cell'
  applied_rule_portal_type = 'Applied Rule'
  datetime = DateTime()
  packing_list_portal_type = 'Sale Packing List'
  packing_list_line_portal_type = 'Sale Packing List Line'
  packing_list_cell_portal_type = 'Sale Packing List Cell'
  delivery_builder_id = 'sale_packing_list_builder'
  order_workflow_id='order_workflow'
  size_list = ['Baby','Child/32','Child/34','Man','Woman']

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base','erp5_pdm', 'erp5_trade', 'erp5_apparel',)

  def login(self, quiet=0, run=1):
    uf = self.getPortal().acl_users
    uf._doAddUser('rc', '', ['Manager', 'Member'], [])
    user = uf.getUserById('rc').__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self, quiet=1, run=1):
    self.login()
    portal = self.getPortal()
    self.category_tool = self.getCategoryTool()
    portal_catalog = self.getCatalogTool()
    #portal_catalog.manage_catalogClear()
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
      for category_id in ['32', '34']:
        o = self.category_tool.size.Child.newContent(portal_type='Category',
                                                     id=category_id)

    colour_category_list = ['blue', 'green']
    if len(self.category_tool.colour.contentValues()) == 0 :
      for category_id in colour_category_list:
        o = self.category_tool.colour.newContent(portal_type='Category',
                                                 id=category_id)

    industrial_phase_category_list = ['phase1', 'phase2',
                                      'supply_phase1', 'supply_phase2']
    if len(self.category_tool.industrial_phase.contentValues()) == 0:
      for category_id in industrial_phase_category_list:
        o = self.category_tool.industrial_phase.newContent(
                                                 portal_type='Category',
                                                 id=category_id)

    product_line_category_list = ['apparel', ]
    if len(self.category_tool.product_line.contentValues()) == 0:
      for category_id in product_line_category_list:
        o = self.category_tool.product_line.newContent(
                                                 portal_type='Category',
                                                 id=category_id)

  def stepTic(self,**kw):
    self.tic()

  def stepCreateNotVariatedResource(self,sequence=None, sequence_list=None, \
                                    **kw):
    """
      Create a resource with no variation
    """
    portal = self.getPortal()
    resource_module = portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent(portal_type=self.resource_portal_type)
    resource.edit(
      title = "NotVariatedResource",
      industrial_phase_list=["phase1", "phase2"],
      product_line = 'apparel'
    )

    sequence.edit( resource = resource )
    resource_list = sequence.get('resource_list',default=[])
    resource_list.append(resource)
    sequence.edit( resource_list = resource_list )

  def stepCreateVariatedResource(self, sequence=None, sequence_list=None, \
                                 **kw):
    """
      Create a resource with no variation
    """
    portal = self.getPortal()
    resource_module = portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent(portal_type=self.resource_portal_type)
    resource.edit(
      title = "VariatedResource",
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

  def stepCreateOrganisation(self, sequence=None, sequence_list=None,
                             title='organisation', **kw):
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
    organisation.edit(
      title=title,
    )
    #sequence.edit(organisation=organisation)
    sequence.edit(**{title:organisation})

  def stepCreateOrder(self,sequence=None, sequence_list=None, **kw):
    """
      Create a empty order
    """
    organisation = sequence.get('organisation')
#     person = sequence.get('person')
    portal = self.getPortal()
    order_module = portal.getDefaultModule(portal_type=self.order_portal_type)
    order = order_module.newContent(portal_type=self.order_portal_type)
    order.edit(
      title = "Order",
      start_date = self.datetime + 10,
      stop_date = self.datetime + 20,
    )
    if organisation is not None:
      order.edit(source_value=organisation,
                 source_section_value=organisation,
                 destination_value=organisation,
                 destination_section_value=organisation)
    sequence.edit( order = order )

  def stepCheckOrder(self, sequence=None, sequence_list=None, **kw):
    """
      Check if order was well created
    """
    organisation = sequence.get('organisation')
    order = sequence.get('order')
    self.assertEquals(self.datetime+10, order.getStartDate())
    self.assertEquals(self.datetime+20, order.getStopDate())
    self.assertEquals(organisation, order.getSourceValue())
    self.assertEquals(organisation, order.getDestinationValue())
    self.assertEquals(organisation, order.getSourceSectionValue())
    self.assertEquals(organisation, order.getDestinationSectionValue())

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
    vcl = order_line.getVariationCategoryList(omit_option_base_category=1)
    cell_range = order_line.OrderLine_asCellRange(matrixbox=0)

    l = len(vcl)
    s = sum(map(lambda x: len(x), cell_range))
    self.assertEquals(l,s)
    cell_key_list = order_line.getCellKeyList(base_id=base_id)
    if cell_range == []:
      self.assertEquals(len(cell_key_list), 0)
    else:
      len_range = map(lambda x: len(x), cell_range)
      self.assertEquals(len(cell_key_list), reduce(lambda x,y: x*y, len_range))

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
    self.assertEquals(len(cell_list), len(cell_key_list))
    price = 100
    quantity = 200
    for cell_key in cell_key_list:
      self.failUnless(order_line.hasCell(base_id=base_id, *cell_key))
      cell = order_line.getCell(base_id=base_id, *cell_key)
      self.assertEquals(self.order_cell_portal_type, cell.getPortalType())
      # XXX How can I check the cell content ?
#       self.assertEquals(price , cell.getProperty('price'))
#       self.assertEquals(quantity, cell.getProperty('quantity'))
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

  def stepCheckOrderLineVCIL(self, sequence=None, sequence_list=None, **kw):
    """
      Check if getVariationCategoryItemList returns the good result.
      Does not test display...
      Item are left display.
    """
    order_line = sequence.get('order_line')
    vcl = order_line.getVariationCategoryList()
    vcil = order_line.getVariationCategoryItemList()
    LOG('stepCheckOrderLineVCIL', 0, 'vcl: %s\n' % str(vcl))
    LOG('stepCheckOrderLineVCIL', 0, 'vcil: %s\n' % str(vcil))
    self.failIfDifferentSet(vcl, map(lambda x: x[1], vcil))

  def stepSetOrderLineDefaultValues(self, sequence=None, \
                                    sequence_list=None, **kw):
    """
      Set the default price and quantity on the order line.
    """
    order_line = sequence.get('order_line')
    order_line.edit(quantity=self.default_quantity,
                    price=self.default_price)

  def stepCheckOrderLineDefaultValues(self, sequence=None, \
                                    sequence_list=None, **kw):
    """
      Check the default price and quantity on the order line.
    """
    order_line = sequence.get('order_line')
    self.assertEquals(self.default_quantity, order_line.getQuantity())
    self.assertEquals(self.default_price, order_line.getPrice())

  def stepCheckOrderLineTotalQuantity(self, sequence=None, \
                                    sequence_list=None, **kw):
    """
      Check the method getTotalQuantity on a order line.
    """

    # order_line needs to be indexed for 'fast' calculation to work as expected
    self.stepTic()

    order_line = sequence.get('order_line')
    base_id = 'movement'
    cell_key_list = order_line.getCellKeyList(base_id=base_id)
    if list(cell_key_list) == []:
      self.assertEquals(order_line.getQuantity(), \
                        order_line.getTotalQuantity())
    else:
      total_quantity = 0
      for cell_key in cell_key_list:
        if order_line.hasCell(base_id = base_id, *cell_key):
          cell = order_line.getCell(base_id = base_id, *cell_key)
          total_quantity += cell.getProperty('quantity')
      self.assertEquals(total_quantity, order_line.getTotalQuantity())
    self.assertEquals( order_line.getTotalQuantity(fast = 0),
                       order_line.getTotalQuantity(fast = 1) )
    self.assertNotEquals(order_line.getTotalQuantity(fast = 1),0)

  def stepCheckOrderLineTotalPrice(self, sequence=None, \
                                    sequence_list=None, **kw):
    """
      Check the method getTotalPrice on a order line.
    """

    # order_line needs to be indexed for 'fast' calculation to work as expected
    self.stepTic()

    order_line = sequence.get('order_line')
    base_id = 'movement'
    cell_key_list = order_line.getCellKeyList(base_id=base_id)
    if list(cell_key_list) == []:
      self.assertEquals(order_line.getProperty('price') *
                        order_line.getProperty('quantity'),
                        order_line.getTotalPrice())
    else:
      total_price = 0
      for cell_key in cell_key_list:
        if order_line.hasCell(base_id = base_id, *cell_key):
          cell = order_line.getCell(base_id = base_id, *cell_key)
          total_price +=  ( cell.getProperty('quantity') *
                            cell.getProperty('price'))
      self.assertEquals(total_price, order_line.getTotalPrice())
    self.assertEquals( order_line.getTotalPrice(fast = 0),
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
    self.assertEquals(len(portal_catalog(
                          relative_url=order_line.getRelativeUrl())),0)
    self.assertEquals(total_price, order_line.getTotalPrice(fast=0))
    self.assertEquals(total_quantity, order_line.getTotalQuantity(fast=0))
    self.assertEquals(0, order_line.getTotalPrice(fast=1))
    self.assertEquals(0, order_line.getTotalQuantity(fast=1))
    self.assertNotEquals(total_price, 0)
    self.stepTic()
    self.assertEquals(len(portal_catalog(relative_url=
                                         order_line.getRelativeUrl())),1)
    self.assertEquals(total_price, order_line.getTotalPrice(fast=1))
    self.assertEquals(total_price, order_line.getTotalPrice(fast=0))
    self.assertEquals(total_quantity, order_line.getTotalQuantity(fast=1))
    self.assertEquals(total_quantity, order_line.getTotalQuantity(fast=0))

  def stepCheckOrderTotalQuantity(self, sequence=None, sequence_list=None, \
                                  **kw):
    """
      Check the method getTotalQuantity on a order .
    """

    # order needs to be indexed for 'fast' calculation to work as expected
    self.stepTic()

    order = sequence.get('order')
    order_line_list = order.objectValues( \
                                 portal_type=self.order_line_portal_type)
    order_line_list = map(lambda x: x.getObject(), order_line_list)
    total_quantity = 0
    for order_line in order_line_list:
      total_quantity += order_line.getTotalQuantity()
    self.assertEquals(total_quantity, order.getTotalQuantity())
    self.assertEquals( order.getTotalQuantity(fast = 0),
                       order.getTotalQuantity(fast = 1) )

  def stepCheckOrderTotalPrice(self, sequence=None, sequence_list=None, \
                                  **kw):
    """
      Check the method getTotalPrice on a order .
    """

    # order needs to be indexed for 'fast' calculation to work as expected
    self.stepTic()

    order = sequence.get('order')
    order_line_list = order.objectValues( \
                                 portal_type=self.order_line_portal_type)
    order_line_list = map(lambda x: x.getObject(), order_line_list)
    total_price = 0
    for order_line in order_line_list:
      total_price += order_line.getTotalPrice()
    self.assertEquals(total_price, order.getTotalPrice())
    self.assertEquals( order.getTotalPrice(fast = 0),
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
      total_price += order_line.getTotalPrice(fast=0)
    self.assertEquals(0, len(portal_catalog(relative_url=order.getRelativeUrl())))
    self.assertEquals(total_price, order.getTotalPrice(fast=0))
    self.assertNotEquals(total_price, 0)
    self.assertEquals(0, order.getTotalPrice(fast=1))
    self.stepTic()
    self.assertEquals(1, len(portal_catalog(relative_url=order.getRelativeUrl())))
    self.assertEquals(total_price, order.getTotalPrice(fast=1))
    self.assertEquals(total_price, order.getTotalPrice(fast=0))

  def stepCheckOrderInitialState(self, sequence=None, sequence_list=None, \
                                  **kw):
    """
      Check if the first state of a order is draft.
    """
    order = sequence.get('order')
    self.assertEquals('draft', order.getSimulationState())

  def stepCheckOrderLineState(self, sequence=None, sequence_list=None, \
                                  **kw):
    """
      Check if the state of a order line is the same as parent order.
    """
    order = sequence.get('order')
    order_line = sequence.get('order_line')
    self.assertEquals(order.getSimulationState(), order_line.getSimulationState())

  def stepCheckOrderCellState(self, sequence=None, sequence_list=None, \
                                  **kw):
    """
      Check if the state of a order line is the same as parent order.
    """
    order = sequence.get('order')
    order_line = sequence.get('order_line')
    cell_list = order_line.objectValues(portal_type=self.order_cell_portal_type)
    for cell in cell_list:
      self.assertEquals(order.getSimulationState(), cell.getSimulationState())

  def stepCheckOrderPlanned(self, sequence=None, sequence_list=None, **kw):
    order = sequence.get('order')
    self.assertEquals('planned', order.getSimulationState())

  def checkAcquisition(self, object, acquired_object):
    """
      Check if properties are well acquired
    """
    # packing_list_movement, simulation_movement

    self.assertEquals(acquired_object.getStartDate(), object.getStartDate())
    self.assertEquals(acquired_object.getStopDate(), object.getStopDate())
    self.assertEquals(acquired_object.getSourceValue(), \
                      object.getSourceValue())
    self.assertEquals(acquired_object.getDestinationValue(), \
                      object.getDestinationValue())


    self.assertEquals(acquired_object.getSourceSectionValue(), \
                      object.getSourceSectionValue())
    self.assertEquals(acquired_object.getDestinationSectionValue(), \
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
    cell = order_line.getCellValueList()[0]
    self.checkAcquisition(cell, order_line)
    # Test resource
    self.assertEquals(order_line.getResource(), \
                      cell.getResource())
    # Test resource variation
    cvcl = cell.getVariationCategoryList()
    olvcl = order_line.getVariationCategoryList()
    # This test is not valide anymore, because of option variation
#     self.assertEquals(len(order_line.getVariationRangeBaseCategoryList()), \
#                       len(cvcl))
    for variation_category in cvcl:
      self.failUnless(variation_category in olvcl)

  def stepCheckOrderSimulation(self, sequence=None, sequence_list=None, **kw):
    """
      Test if simulation is matching order
    """
    order = sequence.get('order')
    related_applied_rule_list = order.getCausalityRelatedValueList( \
                                   portal_type=self.applied_rule_portal_type)
    no_applied_rule_state = ('draft', 'auto_planned')
    order_state = order.getSimulationState()

    if order_state in no_applied_rule_state:
      self.assertEquals(0, len(related_applied_rule_list))
    else:
      LOG('stepCheckOrderSimulation', 0, 'related_applied_rule_list: %s' %
                   str([x.getObject() for x in related_applied_rule_list]))
      self.assertEquals(1, len(related_applied_rule_list))
      applied_rule = related_applied_rule_list[0].getObject()
      sequence.edit(applied_rule=applied_rule)
      self.failUnless(applied_rule is not None)
      self.failUnless(order_state, \
                      applied_rule.getLastExpandSimulationState())

      # Test if applied rule has a specialise value with default_order_rule
      portal_rules = getToolByName(order, 'portal_rules')
      self.assertEquals(portal_rules.default_order_rule, \
                        applied_rule.getSpecialiseValue())

      simulation_movement_list = applied_rule.objectValues()
      sequence.edit(simulation_movement_list=simulation_movement_list)

      # Count the number of movement in order
      order_line_list = order.objectValues( \
                                 portal_type=self.order_line_portal_type)
      order_line_list = [x.getObject() for x in order_line_list]
      movement_list = []
      for order_line in order_line_list:
        if not order_line.hasCellContent():
          movement_list.append(order_line)
        else:
          cell_list = order_line.objectValues( \
                                 portal_type=self.order_cell_portal_type)
          movement_list.extend([x.getObject() for x in cell_list])
      # Check if number of movement is equal to number of simulation movement
      self.assertEquals(len(movement_list), len(simulation_movement_list))
      # Check if each movement has only one simulation movement related
      order_movement_list = [x.getOrderValue() for x in \
                             simulation_movement_list]
      self.failIfDifferentSet(movement_list, order_movement_list)

      # Check each simulation movement
      for simulation_movement in simulation_movement_list:
        order_movement = simulation_movement.getOrderValue()
        # Test quantity
        self.assertEquals(order_movement.getQuantity(), \
                          simulation_movement.getQuantity())
        # Test price
        self.assertEquals(order_movement.getPrice(), \
                          simulation_movement.getPrice())
        # Test resource
        self.assertEquals(order_movement.getResource(), \
                          simulation_movement.getResource())
        # Test resource variation
        self.assertEquals(order_movement.getVariationText(), \
                          simulation_movement.getVariationText())
        self.assertEquals(order_movement.getVariationCategoryList(), \
                          simulation_movement.getVariationCategoryList())
        # XXX Test acquisition
        self.checkAcquisition(simulation_movement, order_movement)
        # Test other attributes
        self.assertEquals(1, simulation_movement.deliverable)

  def modifyOrderState(self, transition_name, sequence=None,
                       sequence_list=None):
    order = sequence.get('order')
    order.portal_workflow.doActionFor(order, transition_name, \
                                      wf_id=self.order_workflow_id)

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
    self.failUnless('Simulation Movement' in order.getPortalMovementTypeList())
    self.failUnless(self.order_line_portal_type in order.getPortalMovementTypeList())

  def stepCheckDeliveryBuilderPresence(self, sequence=None,
                                       sequence_list=None, **kw):
    """
      Test if delivery builder exists
    """
    delivery_builder = getattr(self.getPortal().portal_deliveries,
                               self.delivery_builder_id)
    self.assertEquals('Delivery Builder', delivery_builder.getPortalType())

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

  def stepSetOrderProfile(self,sequence=None, sequence_list=None, **kw):
    """
      Set different source and destination on the order
    """
    organisation1 = sequence.get('organisation1')
    organisation2 = sequence.get('organisation2')
    order = sequence.get('order')
    order.edit( source_value = organisation1,
                source_section_value = organisation1,
                destination_value = organisation2,
                destination_section_value = organisation2 )
    self.failUnless('Site Error' not in order.view())

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
      self.assertEquals(0, len(related_packing_list_list))
    else:
      self.assertEquals(1, len(related_packing_list_list))

      packing_list = related_packing_list_list[0].getObject()
      self.failUnless(packing_list is not None)
      sequence.edit(packing_list = packing_list)

      applied_rule = related_applied_rule_list[0].getObject()
      simulation_movement_list = applied_rule.objectValues()

      # Test that packing list is confirmed
      packing_list_state = packing_list.getSimulationState()
      self.assertEquals(packing_list_building_state, packing_list_state)

      # First, test if each Simulation Movement is related to a Packing List
      # Movement
      packing_list_relative_url = packing_list.getRelativeUrl()
      for simulation_movement in simulation_movement_list:
        packing_list_movement_list = simulation_movement.getDeliveryValueList()
        self.failUnless(len(packing_list_movement_list), 1)
        packing_list_movement = packing_list_movement_list[0]
        self.failUnless(packing_list_movement is not None)
        self.failUnless(packing_list_movement.getRelativeUrl().\
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
        self.failUnless(len(related_simulation_movement_list)>0)
        quantity = 0
        total_price = 0
        packing_list_movement_quantity = packing_list_movement.getQuantity()
        for related_simulation_movement in related_simulation_movement_list:
          quantity += related_simulation_movement.getQuantity()
          total_price += related_simulation_movement.getPrice() *\
                         related_simulation_movement.getQuantity()
          # Test resource
          self.assertEquals(packing_list_movement.getResource(), \
                            related_simulation_movement.getResource())
          # Test resource variation
          self.assertEquals(packing_list_movement.getVariationText(), \
                            related_simulation_movement.getVariationText())
          self.assertEquals(packing_list_movement.getVariationCategoryList(), \
                        related_simulation_movement.getVariationCategoryList())
          # Test acquisition
          self.checkAcquisition(packing_list_movement,
                                related_simulation_movement)
          # Test delivery ratio
          self.assertEquals(related_simulation_movement.getQuantity() /\
                            packing_list_movement_quantity, \
                            related_simulation_movement.getDeliveryRatio())


        self.assertEquals(quantity, packing_list_movement.getQuantity())
        # Test price
        self.assertEquals(total_price / quantity, packing_list_movement.getPrice())

      sequence.edit(packing_list=packing_list)

      # Finally, test Packing List getTotalQuantity and getTotalPrice
      self.assertEquals(order.getTotalQuantity(), packing_list.getTotalQuantity())
      self.assertEquals(order.getTotalPrice(), packing_list.getTotalPrice())

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
    if len(cell_list) > 0:
      order_cell = cell_list[0].getObject()
    order_cell.setStartDate(self.datetime + 99)

  def stepModifyOrderLineQuantity(self, sequence=None, sequence_list=None, \
      **kw):
    """
    Modify order line quantity
    """
    order_line = sequence.get('order_line')
    order_line.setQuantity(order_line.getQuantity() + 111)

  def stepCheckOrderSimulationStable(self, sequence=None, \
      sequence_list=None, **kw):
    """
    Tests that the simulation related to the order is stable and not
    divergent
    """
    order = sequence.get('order')
    order_movement_list = order.getMovementList()
    related_simulation_list = []
    for order_movement in order_movement_list:
      related_simulation_list.extend(order_movement.getOrderRelatedValueList())
    related_applied_rule_list = {}
    for simulation_mvt in related_simulation_list:
      self.assertFalse(simulation_mvt.isDivergent())
      related_applied_rule_list[simulation_mvt.getParentValue()]=1
    for applied_rule in related_applied_rule_list.keys():
      self.assertTrue(applied_rule.isStable())

  def stepPackingListAdoptPrevision(self,sequence=None, sequence_list=None, 
                                    **kw):
    """
    Check if simulation movement are disconnected
    """
    packing_list = sequence.get('packing_list')
    packing_list.portal_workflow.doActionFor(packing_list,
                                             'adopt_prevision_action')

  non_variated_order_creation = '\
      stepCreateOrder \
      stepCreateNotVariatedResource \
      stepCreateOrderLine \
      stepCheckOrderLineEmptyMatrix \
      stepSetOrderLineResource \
      stepSetOrderLineDefaultValues \
      stepCheckOrderLineDefaultValues \
      '

  variated_order_line_creation = '\
      stepCreateOrder \
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
    self.assertEquals(1, len(simulation_state_list))
    self.assertEquals(order.getSimulationState(), 
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
        self.assertEquals(1, len(simulation_state_list))
        self.assertEquals(order.getSimulationState(), 
                          simulation_state_list[0])

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
#       self.assertEquals(new_quantity, cell.getProperty('quantity'))
#       self.assertEquals(new_price, cell.getProperty('price'))
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

  def test_03_OrderLine_getVariationCategoryList(self, quiet=0,
                                                 run=run_all_test):
    """
      Test order line getVariationCategoryList.
      Not yet tested....
    """
    if not run: return
    pass

  def test_04_OrderLine_getVariationCategoryItemList(self, quiet=0,
                                                     run=run_all_test):
    """
      Test order line getVariationCategoryItemList.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when resource has variation
    sequence_string = 'stepCreateOrder \
                       stepCreateOrderLine \
                       stepCheckOrderLineVCIL \
                       stepCreateVariatedResource \
                       stepTic \
                       stepSetOrderLineResource \
                       stepSetOrderLineHalfVCL \
                       stepTic \
                       stepCheckOrderLineVCIL \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

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
#       self.assertEquals(price, cell.getProperty('price'))
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

  def test_10_Order_testSimulationState(self, quiet=0, run=run_all_test):
    """
      Test simulation state acquisition on Order
    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = '\
                      stepCreateOrganisation \
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
                      ' + self.variated_order_creation + '\
                      stepPlanOrder \
                      stepTic \
                      stepOrderOrder \
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
#     self.failUnless(1==2)

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
                      stepCheckDeliveryBuilding \
                      '
    sequence_list.addSequenceString(sequence_string)

    # Test to confirm order with variated resource
    sequence_string = '\
                      stepCreateOrganisation1 \
                      stepCreateOrganisation2 \
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
                      stepCheckDeliveryBuilding \
                      '
    sequence_list.addSequenceString(sequence_string)

    # Test to confirm order with multiples lines
    sequence_string = '\
                      stepCreateOrganisation1 \
                      stepCreateOrganisation2 \
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
                      stepCheckDeliveryBuilding \
                      '
    sequence_list.addSequenceString(sequence_string)

    # Test with a order with 2 lines and the same not variated resource
    sequence_string = '\
                      stepCreateOrganisation1 \
                      stepCreateOrganisation2 \
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
                      stepCheckDeliveryBuilding \
                      '
    sequence_list.addSequenceString(sequence_string)

    # Test with a order with 2 lines and the same variated resource
    sequence_string = '\
                      stepCreateOrganisation1 \
                      stepCreateOrganisation2 \
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
                      stepCheckOrderSimulationStable \
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
                      stepCheckOrderSimulationStable \
                      '
#     sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

#   def test_16_packingListOrderAcquisition(self, quiet=0, run=run_all_test):
#     """
#       Test if packing list get some properties from order.
#     """
#     if not run: return
#     self.failUnless(1==2)

  def test_18_SimulationStateIndexation(self, quiet=0, run=run_all_test):
    """
    Test that the simulation state is well indexed.
    """
    if not run: return

    sequence_list = SequenceList()

    sequence_string = '\
                      stepCreateOrganisation \
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

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestOrder))
  return suite
