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



#
# Skeleton ZopeTestCase
#

from random import randint

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager, \
                                             noSecurityManager
from DateTime import DateTime
from Acquisition import aq_base, aq_inner
from zLOG import LOG
from Products.ERP5Type.DateUtils import addToDate
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList
import time
import os
from Products.ERP5Type import product_path
from Products.CMFCore.utils import getToolByName

class TestOrder(ERP5TypeTestCase):
  """
    Test business template erp5_trade 
  """
  run_all_test = 1

  default_quantity = 99
  default_price = 555
  resource_portal_type = 'Apparel Model'
  order_portal_type = 'Sale Order'
  order_line_portal_type = 'Sale Order Line'
  cell_portal_type = 'Delivery Cell'
  applied_rule_portal_type = 'Applied Rule'
  datetime = DateTime()

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_apparel_depend','erp5_apparel', 'erp5_trade')

  def getTitle(self):
    return "Trade"

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

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('rc', '', ['Manager'], [])
    user = uf.getUserById('rc').__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self, quiet=1, run=run_all_test):
    self.login()
    portal = self.getPortal()
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
      for category_id in ['32', '34']:
        o = self.category_tool.size.Child.newContent(portal_type='Category',
                                                     id=category_id)

    colour_category_list = ['blue', 'green']
    if len(self.category_tool.colour.contentValues()) == 0 :
      for category_id in colour_category_list:
        o = self.category_tool.colour.newContent(portal_type='Category',
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
      title = "NotVariatedResource"
    )

    sequence.edit( resource = resource )

  def stepCreateVariatedResource(self, sequence=None, sequence_list=None, \
                                 **kw):
    """
      Create a resource with no variation
    """
    portal = self.getPortal()
    resource_module = portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent(portal_type=self.resource_portal_type)
    resource.edit(
      title = "VariatedResource"
    )
    size_list = ['Baby','Child/32','Child/34','Man','Woman'] 
    resource.setSizeList(size_list) 
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

  def stepCreateOrganisation(self,sequence=None, sequence_list=None, **kw):
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
      title = "Orga",
    )
    sequence.edit(organisation=organisation)

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
      order.setSourceValue(organisation)
      order.setSourceSectionValue(organisation)
      order.setDestinationValue(organisation)
      order.setDestinationSectionValue(organisation)

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
    cell_list = order_line.searchFolder(portal_type=self.cell_portal_type)
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
    cell_list = order_line.searchFolder(portal_type=self.cell_portal_type)
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
      ZopeTestCase._print('\n')
      ZopeTestCase._print('vbc: %s' % str(vbc))
      resource_vcl = list(resource.getVariationCategoryList(
                                  base_category_list=[vbc],
                                  omit_individual_variation=0))
      ZopeTestCase._print('resource_vcl: %s' % str(resource_vcl))
      resource_vcl.sort()
      ZopeTestCase._print('split resource_vcl: %s' %\
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
    vcl = order_line.getVariationCategoryList()
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
                                portal_type=self.cell_portal_type, *cell_key)
      cell.edit(mapped_value_property_list=['price','quantity'],
                price=price, quantity=quantity)
      cell.setPredicateCategoryList( cell_key )
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
    cell_list = order_line.searchFolder(portal_type=self.cell_portal_type)
    self.assertEquals(len(cell_list), len(cell_key_list))
    price = 100
    quantity = 200
    for cell_key in cell_key_list:
      self.failUnless(order_line.hasCell(base_id=base_id, *cell_key))
      cell = order_line.getCell(base_id=base_id, *cell_key)
      self.assertEquals(self.cell_portal_type, cell.getPortalType())
      # XXX How can I check the cell content ?
#       self.assertEquals(price , cell.getProperty('price'))
#       self.assertEquals(quantity, cell.getProperty('quantity'))
#       self.failIfDifferentSet(cell.getMembershipCriterionCategoryList(),
#                               cell_key)
      price += 1
      quantity += 1

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

  def test_01_OrderLine_getVariationRangeCategoryList(self, quiet=0, 
                                                      run=run_all_test):
    """
      Test order line getVariationRangeCategoryList.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when resource has no variation
    sequence_string = 'CreateOrder \
                      CreateOrderLine \
                      CheckOrderLineVRCL \
                      CreateNotVariatedResource \
                      Tic \
                      SetOrderLineResource \
                      CheckOrderLineVRCL \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has variation
    sequence_string = 'CreateOrder \
                      CreateOrderLine \
                      CheckOrderLineVRCL \
                      CreateVariatedResource \
                      Tic \
                      SetOrderLineResource \
                      CheckOrderLineVRCL \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

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

  def test_02_OrderLine_getVariationRangeCategoryItemList(self, quiet=0,
                                                          run=run_all_test):
    """
      Test order line getVariationRangeCategoryItemList.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when resource has no variation
    sequence_string = 'CreateOrder \
                      CreateOrderLine \
                      CheckOrderLineVRCIL \
                      CreateNotVariatedResource \
                      Tic \
                      SetOrderLineResource \
                      CheckOrderLineVRCIL \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has variation
    sequence_string = 'CreateOrder \
                      CreateOrderLine \
                      CheckOrderLineVRCIL \
                      CreateVariatedResource \
                      Tic \
                      SetOrderLineResource \
                      CheckOrderLineVRCIL \
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

  def stepCheckOrderLineVCIL(self, sequence=None, sequence_list=None, **kw):
    """
      Check if getVariationCategoryItemList returns the good result.
      Does not test display...
      Item are left display.
    """
    order_line = sequence.get('order_line')
    vcl = order_line.getVariationCategoryList()
    vcil = order_line.getVariationCategoryItemList()
    ZopeTestCase._print('\n')
    ZopeTestCase._print('vcl: %s\n' % str(vcl))
    ZopeTestCase._print('vcil: %s\n' % str(vcil))
    self.failIfDifferentSet(vcl, map(lambda x: x[1], vcil))

  def test_04_OrderLine_getVariationCategoryItemList(self, quiet=0,
                                                     run=run_all_test):
    """
      Test order line getVariationCategoryItemList.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when resource has variation
    sequence_string = 'CreateOrder \
                      CreateOrderLine \
                      CheckOrderLineVCIL \
                      CreateVariatedResource \
                      Tic \
                      SetOrderLineResource \
                      SetOrderLineHalfVCL \
                      Tic \
                      CheckOrderLineVCIL \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_05_OrderLine_Matrix(self, quiet=0, run=run_all_test):
    """
      Test order line movement matrix.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when resource has no variation
    sequence_string = 'CreateOrder \
                      CreateNotVariatedResource \
                      Tic \
                      CreateOrderLine \
                      CheckOrderLineEmptyMatrix \
                      SetOrderLineResource \
                      CheckOrderLineEmptyMatrix \
                      SetOrderLineFullVCL \
                      CheckOrderLineRange \
                      CheckOrderLineEmptyMatrix \
                      CompleteOrderLineMatrix \
                      Tic \
                      CheckOrderLineCompleteMatrix \
                      SetOrderLineHalfVCL \
                      Tic \
                      CheckOrderLineRange \
                      CheckOrderLineCompleteMatrix \
                      SetOrderLineEmptyVCL \
                      Tic \
                      CheckOrderLineEmptyMatrix \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has variations
    sequence_string = 'CreateOrder \
                      CreateVariatedResource \
                      Tic \
                      CreateOrderLine \
                      CheckOrderLineEmptyMatrix \
                      SetOrderLineResource \
                      CheckOrderLineEmptyMatrix \
                      SetOrderLineFullVCL \
                      CheckOrderLineRange \
                      CheckOrderLineEmptyMatrix \
                      CompleteOrderLineMatrix \
                      Tic \
                      CheckOrderLineCompleteMatrix \
                      SetOrderLineHalfVCL \
                      Tic \
                      CheckOrderLineRange \
                      CheckOrderLineCompleteMatrix \
                      SetOrderLineEmptyVCL \
                      Tic \
                      CheckOrderLineRange \
                      CheckOrderLineEmptyMatrix \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepSetOrderLineDefaultValues(self, sequence=None, \
                                    sequence_list=None, **kw):
    """
      Set the default price and quantity on the order line.
    """
    order_line = sequence.get('order_line')
    order_line.setQuantity(self.default_quantity)
    order_line.setPrice(self.default_price)
      
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
    order_line = sequence.get('order_line')
    base_id = 'movement'
    cell_key_list = order_line.getCellKeyList(base_id=base_id)
    if list(cell_key_list) == []:
      self.assertEquals(order_line.getQuantity(), \
                        order_line.getTotalQuantity())
    else:
      total_quantity = 0
      for cell_key in cell_key_list:
        if order_line.hasCell(base_id, *cell_key):
          cell = order_line.getCell(base_id, *cell_key)
          total_quantity += cell.getProperty('quantity')
      self.assertEquals(total_quantity, order_line.getTotalQuantity())
      
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
    sequence_string = '\
                      CreateOrder \
                      CreateNotVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      CheckOrderLineDefaultValues \
                      CheckOrderLineTotalQuantity \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has variations
    sequence_string = '\
                      CreateOrder \
                      CreateVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      CheckOrderLineDefaultValues \
                      CheckOrderLineTotalQuantity \
                      SetOrderLineFullVCL \
                      CompleteOrderLineMatrix \
                      CheckOrderLineTotalQuantity \
                      '
    sequence_list.addSequenceString(sequence_string)
    # XXX test cell modification

    sequence_list.play(self)

  def stepCheckOrderLineTotalPrice(self, sequence=None, \
                                    sequence_list=None, **kw):
    """
      Check the method getTotalPrice on a order line.
    """
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
        if order_line.hasCell(base_id, *cell_key):
          cell = order_line.getCell(base_id, *cell_key)
          total_price +=  ( cell.getProperty('quantity') *
                            cell.getProperty('price'))
      self.assertEquals(total_price, order_line.getTotalPrice())
      
  def test_07_OrderLine_getTotalPrice(self, quiet=0, run=run_all_test):
    """
      Test method getTotalPrice on order line.
    """
    if not run: return
    sequence_list = SequenceList()

    # Test when resource has not variation
    sequence_string = '\
                      CreateOrder \
                      CreateNotVariatedResource \
                      Tic \
                      CreateOrderLine \
                      CheckOrderLineEmptyMatrix \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      CheckOrderLineDefaultValues \
                      CheckOrderLineTotalPrice \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has variations
    sequence_string = '\
                      CreateOrder \
                      CreateVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      CheckOrderLineDefaultValues \
                      CheckOrderLineTotalQuantity \
                      SetOrderLineFullVCL \
                      CompleteOrderLineMatrix \
                      CheckOrderLineTotalPrice \
                      '
    sequence_list.addSequenceString(sequence_string)
    # XXX test cell modification

    sequence_list.play(self)

  def stepCheckOrderTotalQuantity(self, sequence=None, sequence_list=None, \
                                  **kw):
    """
      Check the method getTotalQuantity on a order .
    """
    order = sequence.get('order')
    order_line_list = order.searchFolder( \
                                 portal_type=self.order_line_portal_type)
    order_line_list = map(lambda x: x.getObject(), order_line_list)
    total_quantity = 0
    for order_line in order_line_list:
      total_quantity += order_line.getTotalQuantity()
    self.assertEquals(total_quantity, order.getTotalQuantity())
      
  def test_08_Order_testTotalQuantity(self, quiet=0, run=run_all_test):
    """
      Test method getTotalQuantity on a order
    """
    if not run: return
    sequence_list = SequenceList()
    # Test with no order line
    sequence_string = '\
                      CreateOrder \
                      CheckOrderTotalQuantity \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has not variation
    sequence_string = '\
                      CreateOrder \
                      CreateNotVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      CheckOrderTotalQuantity \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has variations
    sequence_string = '\
                      CreateOrder \
                      CreateVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      SetOrderLineFullVCL \
                      CompleteOrderLineMatrix \
                      CheckOrderTotalQuantity \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test whith multiples order line
    sequence_string = '\
                      CreateOrder \
                      CreateVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      SetOrderLineFullVCL \
                      CompleteOrderLineMatrix \
                      CheckOrderTotalQuantity \
                      CreateNotVariatedResource \
                      CreateOrderLine \
                      Tic \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      Tic \
                      CheckOrderTotalQuantity \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCheckOrderTotalPrice(self, sequence=None, sequence_list=None, \
                                  **kw):
    """
      Check the method getTotalPrice on a order .
    """
    order = sequence.get('order')
    order_line_list = order.searchFolder( \
                                 portal_type=self.order_line_portal_type)
    order_line_list = map(lambda x: x.getObject(), order_line_list)
    total_price = 0
    for order_line in order_line_list:
      total_price += order_line.getTotalPrice()
    self.assertEquals(total_price, order.getTotalPrice())
      
  def test_09_Order_testTotalPrice(self, quiet=0, run=run_all_test):
    """
      Test method getTotalPrice on a order
    """
    if not run: return
    sequence_list = SequenceList()
    # Test with no order line
    sequence_string = '\
                      CreateOrder \
                      CheckOrderTotalPrice\
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has not variation
    sequence_string = '\
                      CreateOrder \
                      CreateNotVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      CheckOrderTotalPrice \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has variations
    sequence_string = '\
                      CreateOrder \
                      CreateVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      SetOrderLineFullVCL \
                      CompleteOrderLineMatrix \
                      CheckOrderTotalPrice \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test with multiples order line
    sequence_string = '\
                      CreateOrder \
                      CreateVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      SetOrderLineFullVCL \
                      CompleteOrderLineMatrix \
                      CreateNotVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      CheckOrderTotalPrice \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

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
    cell_list = order_line.searchFolder(portal_type=self.cell_portal_type)
    for cell in cell_list:
      self.assertEquals(order.getSimulationState(), cell.getSimulationState())

  def stepPlanOrder(self, sequence=None, sequence_list=None, **kw):
    order = sequence.get('order')
    order.portal_workflow.doActionFor(order,'plan_action', \
                                      wf_id='order_workflow')
      
  def stepCheckOrderPlanned(self, sequence=None, sequence_list=None, **kw):
    order = sequence.get('order')
    self.assertEquals('planned', order.getSimulationState())
      
  def test_10_Order_testSimulationState(self, quiet=0, run=run_all_test):
    """
      Test simulation state acquisition on Order
    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = '\
                      CreateOrder \
                      CreateVariatedResource \
                      Tic \
                      CheckOrderInitialState \
                      CreateOrderLine \
                      Tic \
                      CheckOrderLineState \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      SetOrderLineFullVCL \
                      CompleteOrderLineMatrix \
                      Tic \
                      CheckOrderCellState \
                      PlanOrder \
                      Tic \
                      CheckOrderPlanned \
                      CheckOrderLineState \
                      CheckOrderCellState \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def checkAcquisition(self, object, acquired_object):
    """
      Check if properties are well acquired
    """
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

  def test_11_testPropertiesAcquisition(self, quiet=0, run=run_all_test):
    """
      Test if some properties on order line or order 
      cell are well acquired.
    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = '\
                      CreateOrganisation \
                      CreateOrder \
                      CheckOrder \
                      CreateVariatedResource \
                      Tic \
                      CreateOrderLine \
                      CheckOrderLineAcquisition \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      SetOrderLineFullVCL \
                      CompleteOrderLineMatrix \
                      CheckOrderCellAcquisition \
                      Tic \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

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
#       ZopeTestCase._print('\n')
#       ZopeTestCase._print('related_applied_rule_list: %s' %\
#                        str([x.getObject() for x in related_applied_rule_list]))
      self.assertEquals(1, len(related_applied_rule_list))
      applied_rule = related_applied_rule_list[0].getObject()
      self.failUnless(applied_rule is not None)
      self.failUnless(order_state, \
                      applied_rule.getLastExpandSimulationState())
      
      # Test if applied rule has a specialise value with default_order_rule
      portal_rules = getToolByName(order, 'portal_rules')
      self.assertEquals(portal_rules.default_order_rule, \
                        applied_rule.getSpecialiseValue())
      
      simulation_movement_list = applied_rule.objectValues()

      # Count the number of movement in order
      order_line_list = order.searchFolder( \
                                 portal_type=self.order_line_portal_type)
      order_line_list = map(lambda x: x.getObject(), order_line_list)
      movement_list = []
      for order_line in order_line_list:
        if not order_line.hasCellContent():
          movement_list.append(order_line)
        else:
          cell_list = order_line.searchFolder( \
                                 portal_type=self.cell_portal_type)
          movement_list.extend(map(lambda x: x.getObject(), cell_list))
      # Check if number of movement is equal to number of simulation movement
      self.assertEquals(len(movement_list), len(simulation_movement_list))
      # Check if each movement has only one simulation movement related
      order_movement_list = map(lambda x: x.getOrderValue(), \
                                simulation_movement_list)
      self.failIfDifferentSet(movement_list, order_movement_list)

      # Check each simulation movement
      for simulation_movement in simulation_movement_list:
        order_movement = simulation_movement.getOrderValue()
        # Test quantity
        self.assertEquals(order_movement.getQuantity(), \
                          simulation_movement.getQuantity())
        # Test resource
        self.assertEquals(order_movement.getResource(), \
                          simulation_movement.getResource())
        # XXX Test acquisition
        self.checkAcquisition(simulation_movement, order_movement)
        # Test other attributes
        self.assertEquals(1, simulation_movement.deliverable)


  def stepOrderOrder(self, sequence=None, sequence_list=None, **kw):
    order = sequence.get('order')
    order.portal_workflow.doActionFor(order,'order_action', \
                                      wf_id='order_workflow')

  def stepConfirmOrder(self, sequence=None, sequence_list=None, **kw):
    order = sequence.get('order')
    order.portal_workflow.doActionFor(order,'confirm_action', \
                                      wf_id='order_workflow')

  def stepCancelOrder(self, sequence=None, sequence_list=None, **kw):
    order = sequence.get('order')
    order.portal_workflow.doActionFor(order,'cancel_action', \
                                      wf_id='order_workflow')

  def stepCheckPortalMethod(self, sequence=None, sequence_list=None, **kw):
    """
      Test if some portal method are well defined
    """
    order = sequence.get('order')
    self.failUnless('Simulation Movement' in order.getPortalMovementTypeList())
    self.failUnless('Sale Order Line' in order.getPortalMovementTypeList())

  def test_12_testAppliedRuleGeneration(self, quiet=0, run=run_all_test):
    """
      Test generation and update of order applied rule.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test first some portal method
    sequence_string = '\
                      CreateOrder \
                      CheckPortalMethod \
                      '
    sequence_list.addSequenceString(sequence_string)
    
    # Test when order is cancelled
    sequence_string = '\
                      CreateOrganisation \
                      CreateOrder \
                      CreateNotVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      CheckOrderSimulation \
                      PlanOrder \
                      Tic \
                      CheckOrderSimulation \
                      OrderOrder \
                      Tic \
                      CheckOrderSimulation \
                      CancelOrder \
                      Tic \
                      Tic \
                      CheckOrderSimulation \
                      '
    sequence_list.addSequenceString(sequence_string)

    # Test with a simply order without cell
    sequence_string = '\
                      CreateOrganisation \
                      CreateOrder \
                      CreateNotVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      PlanOrder \
                      Tic \
                      CheckOrderSimulation \
                      OrderOrder \
                      Tic \
                      CheckOrderSimulation \
                      '
#                       ConfirmOrder \
#                       Tic \
#                       CheckOrderSimulation \
#                       '
    sequence_list.addSequenceString(sequence_string)

    # Test to confirm order without planned or ordered it
    sequence_string = '\
                      CreateOrganisation \
                      CreateOrder \
                      CreateVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      OrderOrder \
                      Tic \
                      CheckOrderSimulation \
                      '
#                       ConfirmOrder \
#                       Tic \
#                       CheckOrderSimulation \
#                       '
    sequence_list.addSequenceString(sequence_string)

    # Test to confirm order with variated resource
    sequence_string = '\
                      CreateOrganisation \
                      CreateOrder \
                      CreateVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      SetOrderLineFullVCL \
                      CompleteOrderLineMatrix \
                      Tic \
                      OrderOrder \
                      Tic \
                      CheckOrderSimulation \
                      '
#                       ConfirmOrder \
#                       Tic \
#                       CheckOrderSimulation \
#                       '
    sequence_list.addSequenceString(sequence_string)

    # Test to confirm order with multiples lines
    sequence_string = '\
                      CreateOrganisation \
                      CreateOrder \
                      CreateVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      SetOrderLineFullVCL \
                      CompleteOrderLineMatrix \
                      CreateNotVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      Tic \
                      OrderOrder \
                      Tic \
                      CheckOrderSimulation \
                      '
#                       ConfirmOrder \
#                       Tic \
#                       CheckOrderSimulation \
#                       '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

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
    order_line.setStartDate(self.datetime + 88)
      
  def stepModifyOrderCellStartDate(self, sequence=None, sequence_list=None, \
                                   **kw):
    """
      Modify order cell start date
    """
    order_line = sequence.get('order_line')
    cell_list = order_line.searchFolder(portal_type=self.cell_portal_type)
    if len(cell_list) > 0:
      order_cell = cell_list[0].getObject()
    order_cell.setStartDate(self.datetime + 99)
      
  def test_13_testAppliedRuleUpdate(self, quiet=0, run=run_all_test):
    """
      Test update of applied rule when order is modified.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when order is modified
    sequence_string = '\
                      CreateOrganisation \
                      CreateOrder \
                      CreateVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      SetOrderLineFullVCL \
                      CompleteOrderLineMatrix \
                      OrderOrder \
                      Tic \
                      ModifyOrderStartDate \
                      CheckOrderSimulation \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test when order line is modified
    sequence_string = '\
                      CreateOrganisation \
                      CreateOrder \
                      CreateVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      SetOrderLineFullVCL \
                      CompleteOrderLineMatrix \
                      OrderOrder \
                      Tic \
                      ModifyOrderLineStartDate \
                      CheckOrderSimulation \
                      '
    sequence_list.addSequenceString(sequence_string)
    # Test when order cell is modified
    sequence_string = '\
                      CreateOrganisation \
                      CreateOrder \
                      CreateVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      SetOrderLineFullVCL \
                      CompleteOrderLineMatrix \
                      OrderOrder \
                      Tic \
                      ModifyOrderCellStartDate \
                      CheckOrderSimulation \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_14_testBuildDeliveryList(self, quiet=0, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    self.failUnless(1==2)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestOrder))
        return suite

