##############################################################################
#
# Copyright (c) 2004, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from DateTime import DateTime
from Products.ERP5Type.tests.Sequence import SequenceList
from erp5.component.test.testOrder import TestOrderMixin
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod

class TestInventoryModule(TestOrderMixin, ERP5TypeTestCase):
  """
    Test inventory module
  """
  run_all_test = 1
  inventory_portal_type = 'Inventory'
  inventory_line_portal_type = 'Inventory Line'
  inventory_cell_portal_type = 'Inventory Cell'
  item_portal_type = 'Apparel Bath'
  first_date_string = '2005/12/09' # First Inventory
  second_date_string = '2005/12/29' # Next Inventory
  view_stock_date = '2005/12/31' # The day where we are looking for stock
  size_list = ['Child/32','Child/34']

  def getTitle(self):
    return "Inventory Module"

  def getInventoryModule(self):
    return getattr(self.getPortal(), 'inventory_module',None)

  def deliverPackingList(self, packing_list):
    """step through all steps of packing list workflow."""
    packing_list.confirm()
    packing_list.setReady()
    packing_list.start()
    packing_list.stop()
    packing_list.deliver()
    self.assertEqual(packing_list.getSimulationState(), 'delivered')

  def stepCreateInitialMovements(self, sequence=None, **kw):
    """Create movements before this inventory.
    """
    pplm = self.getPortal().purchase_packing_list_module
    splm = self.getPortal().sale_packing_list_module
    iplm = self.getPortal().internal_packing_list_module

    # we create content :
    #   1 purchase packing list
    #   1 sale packing list
    #   1 internal packing list
    for month in range(1, 11):
      ppl = pplm.newContent(
                      portal_type='Purchase Packing List',
                      specialise=self.business_process,
                      source_value = sequence.get('organisation2'),
                      destination_value = sequence.get('organisation1'),
                      start_date=DateTime(2005, month, 1),
                    )
      ppl.newContent( portal_type='Purchase Packing List Line',
                      resource_value=sequence.get('resource'),
                      quantity=month*10) # dummy quantity, it will be
                                         # replaced by inventory
      self.deliverPackingList(ppl)

      spl = splm.newContent(
                      portal_type='Sale Packing List',
                      specialise=self.business_process,
                      source_value = sequence.get('organisation1'),
                      destination_value = sequence.get('organisation2'),
                      start_date=DateTime(2005, month, 1),
                    )
      spl.newContent( portal_type='Sale Packing List Line',
                      resource_value=sequence.get('resource'),
                      quantity=month*10)
      self.deliverPackingList(spl)

      ipl = iplm.newContent(
                      portal_type='Internal Packing List',
                      specialise=self.business_process,
                      source_value = sequence.get('organisation1'),
                      destination_value = sequence.get('organisation1'),
                      start_date=DateTime(2005, month, 1),
                    )
      ipl.newContent( portal_type='Internal Packing List Line',
                      resource_value=sequence.get('resource'),
                      quantity=month*10)
      self.deliverPackingList(ipl)

  def createInventory(self, start_date=None,
                                       sequence=None,**kw):
    """
    We will put default values for an inventory
    """
    organisation =  sequence.get('organisation1')
    inventory = self.getInventoryModule().newContent()
    inventory.edit(start_date=start_date,
                   destination_value=organisation)
    inventory.deliver()
    inventory_list = sequence.get('inventory_list',[])
    inventory_list.append(inventory)
    sequence.edit(inventory_list=inventory_list)
    return inventory

  @UnrestrictedMethod
  def createNotVariatedInventoryLine(self, quantity=None,
                                       sequence=None,**kw):
    """
    We will put default values for an inventory
    """
    inventory = sequence.get('inventory_list')[-1]
    resource = sequence.get('resource_list')[-1]
    inventory_line = inventory.newContent(
           portal_type=self.inventory_line_portal_type)
    inventory_line.edit(inventory=quantity,
                        resource_value = resource)
    return inventory

  def stepCreateFirstNotVariatedInventory(self, sequence=None,
                                          sequence_list=None, **kw):
    """
    We will put default values for an inventory
    """
    date = DateTime(self.first_date_string)
    quantity=self.default_quantity
    self.createInventory(start_date=date,sequence=sequence)
    self.createNotVariatedInventoryLine(sequence=sequence,
                                    quantity=quantity)

  def stepCreateSecondNotVariatedInventory(self, sequence=None,
                                           sequence_list=None, **kw):
    """
    We will put default values for an inventory
    """
    date = DateTime(self.second_date_string)
    quantity=self.default_quantity - 2
    self.createInventory(start_date=date,sequence=sequence)
    self.second_inventory = self.createNotVariatedInventoryLine(sequence=sequence,
                                    quantity=quantity)


  @UnrestrictedMethod
  def stepModifySecondNotVariatedInventory(self, sequence=None,
                                           sequence_list=None, **kw):
    """
    Modify the quantity to have a tmp line with null quantity
    """
    quantity=self.default_quantity
    inventory_line = self.second_inventory.objectValues()[0]
    inventory_line.edit(inventory=quantity)


  def stepCheckFirstNotVariatedInventory(self, start_date=None,quantity=None,
                                             sequence=None,**kw):
    node_uid = sequence.get('organisation1').getUid()
    resource_url = sequence.get('resource').getRelativeUrl()
    date = DateTime(self.view_stock_date)
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                        resource=resource_url,
                        to_date=date,simulation_state='delivered')
    self.assertEqual(self.default_quantity,quantity)

  def stepCheckSecondNotVariatedInventory(self, start_date=None,quantity=None,
                                             sequence=None, **kw):
    node_uid = sequence.get('organisation1').getUid()
    resource_url = sequence.get('resource').getRelativeUrl()
    date = DateTime(self.view_stock_date)
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                        resource=resource_url,
                        to_date=date,simulation_state='delivered')
    self.assertEqual(self.default_quantity-2,quantity)

  def stepCheckSecondNotVariatedInventoryModified(self, start_date=None,quantity=None,
                                             sequence=None,**kw):
    node_uid = sequence.get('organisation1').getUid()
    resource_url = sequence.get('resource').getRelativeUrl()
    date = DateTime(self.view_stock_date)
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                        resource=resource_url,
                        to_date=date,simulation_state='delivered')
    self.assertEqual(self.default_quantity,quantity)


  def test_01_NotVariatedInventory(self, quiet=0, run=run_all_test):
    """
    We will create an inventory with the default quantity for
    a particular resource. Then we will check if the is correct.
    Then we create another inventory and see if we have the new
    stock value
    """
    if not run: return
    self.logMessage('Test Not Variated Inventory')

    sequence_list = SequenceList()

    # Test with a simple inventory without cell
    sequence_string = 'stepCreateNotVariatedResource \
                       stepCreateOrganisation1 \
                       stepCreateInitialMovements \
                       stepTic \
                       stepCreateFirstNotVariatedInventory \
                       stepTic \
                       stepCheckFirstNotVariatedInventory \
                       stepCreateSecondNotVariatedInventory \
                       stepTic \
                       stepCheckSecondNotVariatedInventory \
                       stepModifySecondNotVariatedInventory \
                       stepTic \
                       stepCheckSecondNotVariatedInventoryModified'
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  @UnrestrictedMethod
  def createVariatedInventoryLine(self, sequence=None, sequence_list=None,
                                 start_date=None, quantity=None, item_list=None,
                                 **kw):
    """
    We will put default values for an inventory
    """
    inventory = sequence.get('inventory_list')[-1]
    resource = sequence.get('resource_list')[-1]
    inventory_line = inventory.newContent(
           portal_type=self.inventory_line_portal_type)
    inventory_line.edit(resource_value = resource)
    resource_vcl = list(resource.getVariationCategoryList(
        omit_individual_variation=1, omit_optional_variation=1))
    resource_vcl.sort()
    self.assertEqual(len(resource_vcl),2)
    inventory_line.setVariationCategoryList(resource_vcl)
    base_id = 'movement'
    cell_key_list = list(inventory_line.getCellKeyList(base_id=base_id))
    cell_key_list.sort()
    price = 100
    for cell_key in cell_key_list:
      cell = inventory_line.newCell(base_id=base_id,
                                portal_type=self.inventory_cell_portal_type,
                                *cell_key)
      cell.edit(mapped_value_property_list=['price','inventory'],
                price=price, inventory=quantity,
                predicate_category_list=cell_key,
                variation_category_list=cell_key,)
      if item_list is not None:
        cell.setAggregateValueList(item_list)
      price += 1
      quantity += 1

  def stepCreateFirstVariatedInventory(self, sequence=None, sequence_list=None, \
                                 **kw):
    """
    We will put default values for an inventory
    """
    date = DateTime(self.first_date_string)
    self.createInventory(start_date=date,sequence=sequence)
    quantity = self.default_quantity
    self.createVariatedInventoryLine(start_date=date,
                  sequence=sequence, quantity=quantity)

  def stepCreateSecondVariatedInventory(self, sequence=None, sequence_list=None, \
                                 **kw):
    """
    We will put default values for an inventory
    """
    date = DateTime(self.second_date_string)
    self.createInventory(start_date=date,sequence=sequence)
    quantity = self.default_quantity - 10
    self.createVariatedInventoryLine(start_date=date,
                  sequence=sequence, quantity=quantity)

  @UnrestrictedMethod
  def createVariatedInventory(self, start_date=None,quantity=None,
                                       sequence=None,**kw):
    """
    We will put default values for an inventory
    """
    inventory = self.createNotVariatedInventory(sequence=sequence,
                                                start_date=start_date)
    resource = sequence.get('resource_list')[0]
    organisation =  sequence.get('organisation1')
    inventory = self.getInventoryModule().newContent()
    inventory.edit(start_date=start_date,
                   destination_value=organisation)
    inventory_line = inventory.newContent(
           portal_type=self.inventory_line_portal_type)
    inventory_line.edit(inventory=quantity,
                        resource_value = resource,
                        destination_value=organisation)

  def stepCheckFirstVariatedInventory(self, start_date=None,quantity=None,
                                             sequence=None,**kw):
    node_uid = sequence.get('organisation1').getUid()
    resource_url = sequence.get('resource').getRelativeUrl()
    date = DateTime(self.view_stock_date)
    total_quantity = 99 + 100
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                        resource=resource_url,
                        to_date=date)
    self.assertEqual(total_quantity,quantity)
    variation_text = 'size/Child/32'
    total_quantity = 99
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                        resource=resource_url,
                        variation_text=variation_text,
                        to_date=date,simulation_state='delivered')
    self.assertEqual(total_quantity,quantity)

  def stepCheckSecondVariatedInventory(self, start_date=None,quantity=None,
                                             sequence=None,**kw):
    node_uid = sequence.get('organisation1').getUid()
    resource_url = sequence.get('resource').getRelativeUrl()
    date = DateTime(self.view_stock_date)
    total_quantity = 89 + 90
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                        resource=resource_url,
                        to_date=date)
    self.assertEqual(total_quantity,quantity)
    variation_text = 'size/Child/32'
    total_quantity = 89
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                        resource=resource_url,
                        variation_text=variation_text,
                        to_date=date,simulation_state='delivered')
    self.assertEqual(total_quantity,quantity)

  def test_02_VariatedInventory(self, run=run_all_test):
    """
    Same thing as test_01 with variation
    """
    if not run: return
    self.logMessage('Test Variated Inventory')

    sequence_list = SequenceList()

    # Test with a variated inventory
    sequence_string = 'stepCreateVariatedResource \
                       stepCreateOrganisation1 \
                       stepCreateInitialMovements \
                       stepTic \
                       stepCreateFirstVariatedInventory \
                       stepTic \
                       stepCheckFirstVariatedInventory \
                       stepCreateSecondVariatedInventory \
                       stepTic \
                       stepCheckSecondVariatedInventory'
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def stepCreateItem(self, start_date=None,quantity=None,
                                             sequence=None,**kw):
    """
    Create an Apparel Bath
    """
    portal = self.getPortal()
    item_list = sequence.get('item_list',[])
    item_module = portal.getDefaultModule(self.item_portal_type)
    item = item_module.newContent(portal_type=self.item_portal_type)
    item_list.append(item)
    sequence.edit(item_list=item_list)

  def stepCreateFirstVariatedAggregatedInventory(self, sequence=None, sequence_list=None, \
                                 **kw):
    """
    We will put default values for an inventory
    - size/Child/32 99
    - size/Child/34 100
    - size/Child/32 99    item1,item2
    - size/Child/34 100   item1,item2
    """
    date = DateTime(self.first_date_string)
    self.createInventory(start_date=date,sequence=sequence)
    quantity = self.default_quantity
    self.createVariatedInventoryLine(start_date=date,
                  sequence=sequence, quantity=quantity)
    item_list = sequence.get('item_list')
    self.createVariatedInventoryLine(start_date=date,
                  sequence=sequence, quantity=quantity,
                  item_list=item_list)

  def getAggregateRelativeUrlText(self,item_list):
    relative_url_list = ['aggregate/%s' % x.getRelativeUrl() for x in item_list]
    relative_url_list.sort()
    relative_url_text = '\n'.join(relative_url_list)
    return relative_url_text

  def stepCheckFirstVariatedAggregatedInventory(self, start_date=None,
                                quantity=None, sequence=None, **kw):
    node_uid = sequence.get('organisation1').getUid()
    resource_url = sequence.get('resource').getRelativeUrl()
    date = DateTime(self.view_stock_date)
    total_quantity = (99 + 100) * 2
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                        resource=resource_url,
                        to_date=date)
    self.assertEqual(total_quantity,quantity)
    variation_text = 'size/Child/32'
    total_quantity = (99) * 2
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                        resource=resource_url,
                        variation_text=variation_text,
                        to_date=date)
    self.assertEqual(total_quantity,quantity)
    # Also check when we look stock for a particular aggregate
    sub_variation_text = self.getAggregateRelativeUrlText(
                                            sequence.get('item_list'))
    total_quantity = 99
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                        resource=resource_url,
                        variation_text=variation_text,
                        to_date=date,
                        sub_variation_text=sub_variation_text)
    self.assertEqual(total_quantity,quantity)

  def stepCheckExplanationTextInInventoryList(self, start_date=None,
                                quantity=None, sequence=None, **kw):
    """Tests getExplanationText from InventoryBrain
    """
    # this is rather a test for InventoryBrain
    node_uid = sequence.get('organisation1').getUid()
    resource_url = sequence.get('resource').getRelativeUrl()
    date = DateTime(self.view_stock_date)
    for inventory_brain in self.getSimulationTool().getInventoryList(
                        node_uid=node_uid,
                        resource=resource_url,
                        to_date=date):
      self.assertNotEquals(inventory_brain.getExplanationText(),
                           'Unknown')
      self.assertNotEquals(inventory_brain.getListItemUrl(
                                'getExplanationText',
                                0,
                                'dummy_selection_name'), '')

  def stepCreateSecondVariatedAggregatedInventory(self, sequence=None,
                                      sequence_list=None, **kw):
    """
    We will put default values for an inventory
    - size/Child/32 89    item1,item2
    - size/Child/34 90    item1,item2
    - size/Child/32 89    item1
    - size/Child/34 90    item1
    """
    date = DateTime(self.second_date_string)
    self.createInventory(start_date=date,sequence=sequence)
    quantity = self.default_quantity - 10
    item_list = sequence.get('item_list')
    self.createVariatedInventoryLine(start_date=date,
                  sequence=sequence, quantity=quantity)
    item_list = sequence.get('item_list')[:1]
    self.createVariatedInventoryLine(start_date=date,
                  sequence=sequence, quantity=quantity,
                  item_list=item_list)

  def stepCheckSecondVariatedAggregatedInventory(self, start_date=None,
                                quantity=None, sequence=None, **kw):
    node_uid = sequence.get('organisation1').getUid()
    resource_url = sequence.get('resource').getRelativeUrl()
    date = DateTime(self.view_stock_date)
    total_quantity = (89 + 90) * 2
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                        resource=resource_url,
                        to_date=date)
    self.assertEqual(total_quantity,quantity)
    variation_text = 'size/Child/32'
    total_quantity = (89) * 2
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                        resource=resource_url,
                        variation_text=variation_text,
                        to_date=date,simulation_state='delivered')
    self.assertEqual(total_quantity,quantity)
    # Also check when we look stock for a particular aggregate
    sub_variation_text = self.getAggregateRelativeUrlText(
                                                sequence.get('item_list'))
    total_quantity = 0
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                        resource=resource_url,
                        to_date=date,
                        sub_variation_text=sub_variation_text,
                        simulation_state='delivered')
    self.assertEqual(total_quantity,quantity)
    sub_variation_text = self.getAggregateRelativeUrlText(
                                    sequence.get('item_list')[:1])

  def test_03_VariatedAggregatedInventory(self, run=run_all_test):
    """
    Same thing as test_01 with variation and aggregate
    """
    if not run: return
    self.logMessage('Test Variated Aggregated Inventory')

    sequence_list = SequenceList()

    # Test with a variated inventory with some aggregate
    sequence_string = 'stepCreateVariatedResource \
                       stepCreateOrganisation1 \
                       stepCreateInitialMovements \
                       stepTic \
                       stepCreateItem \
                       stepCreateItem \
                       stepCreateFirstVariatedAggregatedInventory \
                       stepTic \
                       stepCheckFirstVariatedAggregatedInventory \
                       stepCreateSecondVariatedAggregatedInventory \
                       stepTic \
                       stepCheckSecondVariatedAggregatedInventory'
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_04_VariatedAggregatedInventoryGetInventoryList(self, run=run_all_test):
    """
    Same thing as test_03 with testing getInventoryList columns
    """
    if not run: return
    self.logMessage('Test getInventoryList and Variated Aggregated Inventory')

    sequence_list = SequenceList()

    # Test with a variated inventory with some aggregate
    sequence_string = 'stepCreateVariatedResource \
                       stepCreateOrganisation1 \
                       stepCreateInitialMovements \
                       stepTic \
                       stepCreateItem \
                       stepCreateItem \
                       stepCreateFirstVariatedAggregatedInventory \
                       stepTic \
                       stepCheckFirstVariatedAggregatedInventory \
                       stepCheckExplanationTextInInventoryList \
                       stepCreateSecondVariatedAggregatedInventory \
                       stepTic \
                       stepCheckSecondVariatedAggregatedInventory \
                       stepCheckExplanationTextInInventoryList'
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def stepCreateFirstVariatedMultipleQuantityUnitResourceInventory(self, sequence=None, sequence_list=None, \
                                 **kw):
    """
    We will put default values for an inventory
    - size/Child/32 99 drum
    - size/Child/34 100 drum
    - size/Child/32 99 kilogram
    - size/Child/34 100 kiligram
    """
    date = DateTime(self.first_date_string)
    inventory = self.createInventory(start_date=date,sequence=sequence)
    quantity = self.default_quantity
    self.createVariatedInventoryLine(start_date=date,
                  sequence=sequence, quantity=quantity)
    inventory_line = inventory.objectValues(portal_type='Inventory Line')[0]
    # Set non-default quantity unit to make sure that conversion correctly
    # works and converted value is applied to stock.
    inventory_line.setQuantityUnitValue(self.portal.portal_categories.quantity_unit.unit.drum)
    self.createVariatedInventoryLine(start_date=date,
                  sequence=sequence, quantity=quantity)

  def stepCheckFirstVariatedMultipleQuantityUnitResourceInventory(self, sequence=None, sequence_list=None, \
                                 **kw):
    node_uid = sequence.get('organisation1').getUid()
    resource_url = sequence.get('resource').getRelativeUrl()
    date = DateTime(self.view_stock_date)
    inventory = sequence.get('inventory_list')[-1]
    total_quantity = sum([inventory_movement.getInventoriatedQuantity() for inventory_movement in inventory.getMovementList()])
    self.assertEqual(total_quantity, (99*100 + 100*100 + 99 + 100))
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                                                     resource=resource_url,
                                                     to_date=date)
    self.assertEqual(total_quantity, quantity)
    variation_text = 'size/Child/32'
    total_quantity = (99*100 + 99)
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                                                     resource=resource_url,
                                                     variation_text=variation_text,
                                                     to_date=date)
    self.assertEqual(total_quantity,quantity)

  def test_05_VariatedMultipleQuantityUnitResourceInventory(self, run=run_all_test):
    """
    Input inventory for resource which has variation and multiple quantity units
    and make sure that inventory stores correct data.
    """
    if not run: return
    self.logMessage('Test inventory with variated multiple quantity units resource')

    sequence_list = SequenceList()

    sequence_string = 'stepCreateVariatedMultipleQuantityUnitResource \
                       stepCreateOrganisation1 \
                       stepTic \
                       stepCreateFirstVariatedMultipleQuantityUnitResourceInventory \
                       stepTic \
                       stepCheckFirstVariatedMultipleQuantityUnitResourceInventory'
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def createInitialDeliveryForCheckingUselessCorrection(self, sequence=None):
    organisation =  sequence.get('organisation1')
    from_organisation = sequence.get('organsation2')
    delivery = self.getPortal().internal_packing_list_module.newContent(
                    portal_type='Internal Packing List',
                    specialise=self.business_process,
                    source_value = from_organisation,
                    destination_value = organisation,
                    start_date=DateTime(2019, 2, 20),
                  )
    resource_value = sequence.get('resource')
    delivery.newContent( portal_type='Internal Packing List Line',
                    resource_value=resource_value,
                    quantity=2)
    self.deliverPackingList(delivery)
    self.tic()
    return delivery

  def stepCheckInventoryDoesNotKeepUselessCorrectionAtInventoryLevel(self, sequence=None):
    organisation =  sequence.get('organisation1')
    resource_value = sequence.get('resource')
    delivery = self.createInitialDeliveryForCheckingUselessCorrection(sequence=sequence)

    def getInventoryQuantity():
      return self.getSimulationTool().getCurrentInventory(node_uid=organisation.getUid(),
                                                  resource=resource_value.getRelativeUrl())

    self.assertEqual(2, getInventoryQuantity())

    inventory = self.getInventoryModule().newContent()
    inventory.edit(start_date=DateTime(2019, 2, 21),
                   destination_value=organisation,
                   full_inventory=True)
    inventory.deliver()
    self.tic()

    self.assertEqual(0, getInventoryQuantity())

    delattr(delivery, 'workflow_history')
    self.assertEqual('draft', delivery.getSimulationState())
    delivery.reindexObject()
    self.tic()
    inventory.reindexObject()
    self.tic()
    self.assertEqual(0, getInventoryQuantity())

  def test_06_InventoryDoesNotKeepUselessCorrectionAtInventoryLevel(self):
    """
    We will create a movement, then a full inventory setting all stock to 0.
    This will insert a correction line in stock table with uid of inventory.
    But then, if initial movement is cancelled, a reindex of inventory must remove the correction
    """
    sequence_list = SequenceList()

    # Test with a simple inventory without cell
    sequence_string = 'stepCreateNotVariatedResource \
                       stepCreateOrganisation1 \
                       stepTic \
                       stepCheckInventoryDoesNotKeepUselessCorrectionAtInventoryLevel'
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def stepCheckInventoryDoesNotKeepUselessCorrectionAtLineLevel(self, sequence=None):
    organisation =  sequence.get('organisation1')
    resource_value = sequence.get('resource')
    delivery = self.createInitialDeliveryForCheckingUselessCorrection(sequence=sequence)

    def getInventoryQuantity():
      return self.getSimulationTool().getCurrentInventory(node_uid=organisation.getUid(),
                                                  resource=resource_value.getRelativeUrl())

    self.assertEqual(2, getInventoryQuantity())

    inventory = self.getInventoryModule().newContent()
    inventory.edit(start_date=DateTime(2019, 2, 21),
                   destination_value=organisation,
                   full_inventory=True)
    inventory_line = inventory.newContent(portal_type='Inventory Line',
                    resource_value=resource_value,
                    quantity=3)
    inventory.deliver()
    self.tic()

    self.assertEqual(3, getInventoryQuantity())

    delattr(delivery, 'workflow_history')
    self.assertEqual('draft', delivery.getSimulationState())
    delivery.reindexObject()
    self.tic()
    inventory.reindexObject()
    self.tic()
    self.assertEqual(3, getInventoryQuantity())
    # Even though this scenario might not really, happen, make sure the code does not
    # keep a correction line for a resource which is not set any more
    inventory_line.setResourceValue(None)
    inventory.reindexObject()
    self.tic()
    self.assertEqual(0, getInventoryQuantity())
    inventory_line.setResourceValue(resource_value)
    inventory.reindexObject()
    self.tic()
    self.assertEqual(3, getInventoryQuantity())
    # last safety check, make sure deletion of line of inventory has really an impact
    inventory.manage_delObjects(ids=[inventory_line.getId()])
    inventory.reindexObject()
    self.tic()
    self.assertEqual(0, getInventoryQuantity())

  def test_07_InventoryDoesNotKeepUselessCorrectionAtLineLevel(self):
    """
    We will create a movement, then a full inventory changing stock value.
    This will insert a correction line in stock table with uid of inventory line.
    But then, if initial movement is cancelled, a reindex of inventory must remove the correction
    """
    sequence_list = SequenceList()

    # Test with a simple inventory without cell
    sequence_string = 'stepCreateNotVariatedResource \
                       stepCreateOrganisation1 \
                       stepTic \
                       stepCheckInventoryDoesNotKeepUselessCorrectionAtLineLevel'
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestInventoryModule))
  return suite
