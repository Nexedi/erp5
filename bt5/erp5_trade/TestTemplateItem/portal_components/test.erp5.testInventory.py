##############################################################################
#
# Copyright (c) 2004, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#          Guillaume Michon <guillaume.michon@e-asc.com>
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

# XXX test 1 :
#   - stepTestGetInventoryWithSelectionReport is not launched yet,
#       since it tests a behavior which does not exist yet
# XXX test 2 :
#   - There is an issue about inventory in inventory module :
#       if a movement which is older than the inventory is modified by quantity,
#       the inventory (and the following ones) must be automatically reindexed
#       (and sorted by date). It is not the case now
#   - If an aggregated item is modified by quantity, the same problem appears, but
#       should the inventory be updated by a later quantity modification on an
#       aggregated item ?


import unittest
from unittest import expectedFailure

from Products.ERP5Type.Utils import cartesianProduct
from copy import copy


from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from DateTime import DateTime
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from erp5.component.test.testOrder import TestOrderMixin
from Products.ERP5Form.Selection import DomainSelection
from Products.ERP5Type.tests.utils import createZODBPythonScript
from textwrap import dedent
from zExceptions import BadRequest

class TestInventory(TestOrderMixin, ERP5TypeTestCase):
  """
    Test Inventory API
  """
  run_all_test = 1
  packing_list_portal_type = 'Sale Packing List'
  packing_list_line_portal_type = packing_list_portal_type + ' Line'
  item_portal_type = "Apparel Fabric Item"
  inventory_portal_type = "Inventory"
  inventory_line_portal_type = inventory_portal_type + ' Line'
  inventory_cell_portal_type = inventory_portal_type + ' Cell'
  price_currency =  'currency_module/euro'

  def getTitle(self):
    return "Inventory"

  def getBusinessTemplateList(self):
    """Business Templates required for this test.
    """
    return ('erp5_base', 'erp5_pdm', 'erp5_simulation', 'erp5_trade',
            'erp5_configurator_standard_trade_template',
            'erp5_apparel', 'erp5_simulation_test', 'erp5_mrp')

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

    preference.setPreferredApparelModelVariationBaseCategoryList(('colour', 'size', 'morphology', 'industrial_phase',))
    preference.setPreferredApparelClothVariationBaseCategoryList(('size',))
    preference.setPreferredApparelComponentVariationBaseCategoryList(('variation',))
    if preference.getPreferenceState() == 'disabled':
      preference.enable()
    self.tic()

  def afterSetUp(self):
    self.login()
    self.category_tool = self.getCategoryTool()
    self.createCategories()
    self.validateRules()
    # Patch PackingList.asPacked so that we do not need
    # to manage containers here, this not the job of this test
    def isPacked(self):
      return 1
    from erp5.component.document.PackingList import PackingList
    PackingList.isPacked = isPacked
    self.createCurrency()
    self.setUpPreferences()

  def beforeTearDown(self):
    """Clear everything for next test."""
    for module in [ 'portal_simulation',
                    'inventory_module']:
      folder = self.portal[module]
      try:
        folder.manage_delObjects(list(folder.objectIds()))
      except BadRequest:
        pass
    try:
      self.portal.portal_skins.custom.manage_delObjects(
        list(self.portal.portal_skins.custom.objectIds()))
    except BadRequest:
      pass
    self.tic()

  def createCategory(self, parent, id_list):
    last_category = None
    for category_id in id_list:
      if isinstance(category_id, str):
        last_category = parent.newContent(portal_type='Category',
                                          id=category_id)
      else:
        self.createCategory(last_category, category_id)

  def stepCreateItemList(self, sequence=None, sequence_list=None, **kw):
    """
      Create some items to manipulate during the module test
    """
    item_list = []
    portal = self.getPortal()
    item_module = portal.getDefaultModule(portal_type=self.item_portal_type)
    for i in range(5):
      item = item_module.newContent(portal_type=self.item_portal_type)
      item_list.append(item)
      item.edit(quantity = (i+1)*10)
    sequence.edit(item_list = item_list)

  def stepCreateOrganisationsForModule(self, sequence=None,
                                        sequence_list=None, **kw):
    """
      Create sections and nodes.
    """
    self.stepCreateOrganisation(sequence=sequence,
                        sequence_list=sequence_list, **kw)
    node = sequence.get('organisation')
    self.stepCreateOrganisation(sequence=sequence,
                        sequence_list=sequence_list, **kw)
    mirror_node = sequence.get('organisation')
    self.stepCreateOrganisation(sequence=sequence,
                        sequence_list=sequence_list, **kw)
    section = sequence.get('organisation')
    self.stepCreateOrganisation(sequence=sequence,
                        sequence_list=sequence_list, **kw)
    mirror_section = sequence.get('organisation')
    self.stepCreateOrganisation(sequence=sequence,
                        sequence_list=sequence_list, **kw)
    other_section = sequence.get('organisation')
    self.stepCreateOrganisation(sequence=sequence,
                        sequence_list=sequence_list, **kw)
    other_node = sequence.get('organisation')
    sequence.edit(
          node = node,
          section = section,
          mirror_node = mirror_node,
          mirror_section = mirror_section,
          other_section = other_section,
          other_node = other_node,
        )

  def stepCreateAggregatingInventory(self, sequence=None, sequence_list=None, **kw):
    """
      Create a Inventory object, with a line which aggregates Items
    """
    inventory_list = sequence.get('inventory_list')
    if inventory_list is None:
      inventory_list = []
    portal = self.getPortal()
    node = sequence.get('node')
    section = sequence.get('section')
    item_list = sequence.get('item_list')
    resource = sequence.get('resource')
    inventory_module = portal.getDefaultModule(portal_type = self.inventory_portal_type)
    inventory = inventory_module.newContent(portal_type = self.inventory_portal_type)
    inventory.edit(destination_value = node,
                   destination_section_value = section,
                   start_date = DateTime(),
                  )
    aggregate_value_list = [item_list[0], item_list[2]]
    inventory_line = inventory.newContent(portal_type = self.inventory_line_portal_type)
    inventory_line.edit(resource_value = resource,
                        aggregate_value_list = aggregate_value_list)
    # Now, quantity is not defined any more automatically.
    inventory_line.edit(quantity=sum([x.getQuantity() for x in \
        aggregate_value_list]))
    inventory.deliver()
    inventory_list.append(inventory)
    sequence.edit(inventory_list = inventory_list)

  def createInventory(self, sequence=None, full=False, **kw):
    """
    """
    portal = self.getPortal()
    if kw.get('start_date', None) is not None:
      start_date = kw['start_date']
    else:
      start_date = DateTime() + 1
    inventory_list = sequence.get('inventory_list',[])
    inventory_module = portal.getDefaultModule(portal_type = self.inventory_portal_type)
    inventory = inventory_module.newContent(portal_type = self.inventory_portal_type)
    inventory.edit(destination_value = sequence.get('node'),
                   destination_section_value = sequence.get('section'),
                   start_date = start_date,
                   full_inventory=full,
                  )
    inventory_list.append(inventory)
    sequence.edit(inventory_list=inventory_list)
    return inventory

  def stepCreateSingleInventory(self, sequence=None, sequence_list=None, **kw):
    """
      Create a single Inventory object for Inventory Module testing
    """
    inventory = self.createInventory(sequence=sequence)
    inventory_list = sequence.get('inventory_list',[])
    inventory_line = inventory.newContent(portal_type = self.inventory_line_portal_type)
    inventory_line.edit(resource_value = sequence.get('resource'),
                        inventory = 24.
                       )
    inventory.deliver()
    inventory_list.append(inventory)
    sequence.edit(inventory_list=inventory_list)

  def stepCreateFullInventory(self, sequence=None, sequence_list=None, **kw):
    """
      Create a full Inventory object for Inventory Module testing
    """
    inventory = self.createInventory(sequence=sequence)
    inventory_list = sequence.get('inventory_list',[])
    inventory.edit(full_inventory=True)
    inventory.newContent(
      portal_type = self.inventory_line_portal_type,
      resource_value = sequence.get("second_resource"),
      inventory = 101)
    inventory.deliver()
    inventory_list.append(inventory)
    sequence.edit(inventory_list=inventory_list)

  def stepCreatePartialInventoryMultipleResource(self, sequence=None, sequence_list=None, **kw):
    """
      Create a partial inventory object for one resource
    """
    inventory = self.createInventory(sequence=sequence)
    inventory_list = sequence.get('inventory_list',[])
    inventory.edit(full_inventory=False)
    inventory.newContent(
      portal_type = self.inventory_line_portal_type,
      resource_value = sequence.get("second_resource"),
      inventory = 101)
    inventory.deliver()
    inventory_list.append(inventory)
    sequence.edit(inventory_list=inventory_list)

  def stepTestPartialInventoryMultipleResource(self, sequence=None, sequence_list=None, **kw):
    """
      Test partial inventory behavior with multiple resource
    """
    simulation = self.getPortal().portal_simulation

    # First resource, must not have changed
    inventory = simulation.getCurrentInventory(
      resource = sequence.get("resource").getRelativeUrl(),
      section = sequence.get('section').getRelativeUrl(),
      node = sequence.get('node').getRelativeUrl(),
      )
    self.assertEqual(inventory, 100.,
                    'section=%s, node=%s' % (
                    sequence.get('section').getRelativeUrl(),
                    sequence.get('node').getRelativeUrl()))
    # second resource, must be 101
    inventory = simulation.getCurrentInventory(
      resource = sequence.get("second_resource").getRelativeUrl(),
      section = sequence.get('section').getRelativeUrl(),
      node = sequence.get('node').getRelativeUrl(),
      )
    self.assertEqual(inventory, 101.,
                    'section=%s, node=%s' % (
                    sequence.get('section').getRelativeUrl(),
                    sequence.get('node').getRelativeUrl()))



  def stepCreateSingleVariatedInventory(self, sequence=None, sequence_list=None, **kw):
    """
      Create a single Inventory object for Inventory Module testing
    """
    inventory = self.createInventory(sequence=sequence)
    inventory_line = inventory.newContent(portal_type = self.inventory_line_portal_type)
    category_list = sequence.get('variation_1')
    inventory_line.edit(resource_value = sequence.get('resource'),
                        variation_category_list=category_list
                       )
    cell = inventory_line.newCell(base_id='movement',*category_list)
    quantity=5
    cell.edit(
        quantity = quantity,
        predicate_category_list = category_list,
        variation_category_list = category_list,
        mapped_value_property_list = ['quantity'],
        )
    # When checking the not full inventory function, quantity must remain the same if
    # no inventory line defined for a variation
    inventory.deliver()


  def stepCreateFullVariatedInventory(self, sequence=None, sequence_list=None, **kw):
    """
      Create a single full Inventory object for Inventory Module testing
    """
    inventory = self.createInventory(sequence=sequence, full=True)
    inventory_line = inventory.newContent(portal_type = self.inventory_line_portal_type)
    category_list = sequence.get('variation_1')
    inventory_line.edit(resource_value = sequence.get('resource'),
                        variation_category_list=category_list
                       )
    cell = inventory_line.newCell(base_id='movement',*category_list)
    cell.edit(
        quantity = 55,
        predicate_category_list = category_list,
        variation_category_list = category_list,
        mapped_value_property_list = ['quantity'],
        )
    inventory_line = inventory.newContent(
      portal_type = self.inventory_line_portal_type,
      resource_value = sequence.get("second_resource"),
      inventory = 101)
    inventory.deliver()

  def stepCreatePackingListForModule(self, sequence=None,
                                      sequence_list=None, **kw):
    """
      Create a single packing_list for Inventory Module testing
    """
    node = sequence.get('node')
    section = sequence.get('section')
    mirror_node = sequence.get('mirror_node')
    mirror_section = sequence.get('mirror_section')
    packing_list_module = self.getPortal().getDefaultModule(
                              portal_type=self.packing_list_portal_type)
    packing_list = packing_list_module.newContent(
                              portal_type=self.packing_list_portal_type)
    if kw.get('start_date', None) is not None:
      start_date = stop_date = kw['start_date']
    else:
      start_date = stop_date = DateTime() - 2
    packing_list.edit(
                      specialise=self.business_process,
                      source_section_value = mirror_section,
                      source_value = mirror_node,
                      destination_section_value = section,
                      destination_value = node,
                      start_date = start_date,
                      stop_date = stop_date,
                      price_currency = self.price_currency
                     )
    self.assertNotEqual( packing_list.getSourceSectionValue(), None)
    self.assertNotEqual( packing_list.getSourceValue(), None)
    self.assertNotEqual( packing_list.getSourceSectionValue(),
                          packing_list.getDestinationSectionValue() )
    sequence.edit(packing_list=packing_list)

  def stepCreatePackingListLine(self, sequence=None,
                                      sequence_list=None, **kw):
    """
    Create a line not variated
    """
    packing_list = sequence.get('packing_list')
    if kw.get('resource_value', None) is not None:
      resource_value = kw['resource_value']
    else:
      resource_value = sequence.get('resource')
    packing_list_line = packing_list.newContent(
                  portal_type=self.packing_list_line_portal_type)
    packing_list_line.edit(resource_value = resource_value,
                           quantity = 100.
                          )

  def stepCreateVariatedPackingListLine(self, sequence=None,
                                      sequence_list=None, **kw):
    """
    Create a line not variated
    """
    packing_list = sequence.get('packing_list')
    delivery_line_list = sequence.get('delivery_line_list',[])
    # Create Packing List Line
    packing_list_line = packing_list.newContent(portal_type=self.packing_list_line_portal_type)
    delivery_line_list.append(packing_list_line)
    resource = sequence.get('resource')
    variation_category_list = ['size/Child/32',
                               'size/Child/34',
                               'colour/%s/1' % resource.getRelativeUrl(),
                               'morphology/%s/4' % resource.getRelativeUrl()]
    packing_list_line.edit(
        resource_value = resource,
        variation_category_list=variation_category_list)
    # Set cell range

    cell_range = packing_list_line.getCellRange(base_id='movement')
    cartesian_product = cartesianProduct(cell_range)
    for cell_key in cartesian_product:
      cell = packing_list_line.newCell(base_id='movement', *cell_key)
      if 'size/Child/32' in cell_key:
        quantity = 1
        sequence.edit(variation_1=cell_key)
      elif 'size/Child/34' in cell_key:
        sequence.edit(variation_2=cell_key)
        quantity = 3
      cell.edit(
          quantity = quantity,  # pylint:disable=used-before-assignment
          predicate_category_list = cell_key,
          variation_category_list = cell_key,
          mapped_value_property_list = ['quantity'],
          )
    sequence.edit(delivery_line_list=delivery_line_list)

  def stepCreateVariatedNonDefaultQuantityUnitPackingListLine(
    self, sequence=None, sequence_list=None, **kw):
    """
    Create a line not variated
    """
    self.stepCreateVariatedPackingListLine(sequence, sequence_list, **kw)
    delivery_line = sequence.get('delivery_line_list')[-1]
    delivery_line.setQuantityUnitValue(self.portal.portal_categories.quantity_unit.unit.drum)

  def stepDeliverPackingList(self, sequence=None,
                                      sequence_list=None, **kw):
    # Switch to "started" state
    packing_list = sequence.get('packing_list')
    workflow_tool = self.getPortal().portal_workflow
    workflow_tool.doActionFor(packing_list,
                      "confirm_action", "packing_list_workflow")
    self.commit()
    # Apply tic so that the packing list is not in building state
    self.tic() # acceptable here because this is not the job
               # of the test to check if can do all transition
               # without processing messages
    workflow_tool.doActionFor(packing_list,
                      "set_ready_action", "packing_list_workflow")
    self.tic()
    workflow_tool.doActionFor(packing_list,
                      "start_action", "packing_list_workflow")
    workflow_tool.doActionFor(packing_list,
                      "stop_action", "packing_list_workflow")
    workflow_tool.doActionFor(packing_list,
                      "deliver_action", "packing_list_workflow")

  def stepCreateOrganisationList(self, sequence=None, sequence_list=None, **kw):
    """
      Create some organisations to manipulate during the test
      Organisations organigram :
        section 0 :
          - payment 1
          - nodes 2, 3
        section 4 (provider) :
          - payment 5
          - node 6
        section 7 (customer) :
          - payment  8
          - node 9
    """
    organisation_list = []
    for _ in range(10):
      self.stepCreateOrganisation(sequence=sequence, sequence_list=sequence_list, **kw)
      organisation_list.append(sequence.get('organisation'))

    category_tool = self.getPortal().portal_categories
    bc = category_tool.site
    self.createCategory(bc, ['Place1', ['A', 'B'], 'Place2', ['C'], 'Place3', ['D']])
    organisation_list[2] = bc.Place1.A
    organisation_list[3] = bc.Place1.B
    organisation_list[6] = bc.Place2.C
    organisation_list[9] = bc.Place3.D

    sequence.edit(
      organisation = None,
      organisation_list = organisation_list)


  def stepCreateVariatedResourceList(self, sequence=None, sequence_list=None, **kw):
    """
      Create some variated resources to manipulate during the test
    """
    resource_list = []
    for _ in range(3):
      self.stepCreateVariatedResource(sequence=sequence, sequence_list=sequence_list, **kw)
      resource_list.append(sequence.get('resource'))
    sequence.edit(
      resource=None,
      resource_list = resource_list)


  def stepCreatePackingListList(self, sequence=None, sequence_list=None, **kw):
    """
      Create some packing lists
    """
    base_category_list = ['size', 'colour', 'morphology']
    data_list = [
      { 'source':6, 'destination':2, 'source_section':4, 'destination_section':0,
        'source_payment':5, 'destination_payment':1, 'start_date':DateTime()-30, 'lines':[
           {'resource':0, 'cells': [
                             #size, colour, morphology
               {'variation':['size/Baby', '1', '4'], 'quantity':.5},
               {'variation':['size/Baby', '2', '4'], 'quantity':1.},
               {'variation':['size/Baby', '3', '4'], 'quantity':1.5},
               {'variation':['size/Baby', '1', '5'], 'quantity':2.},
               {'variation':['size/Baby', '2', '5'], 'quantity':2.5},
               {'variation':['size/Baby', '3', '5'], 'quantity':3.},

               {'variation':['size/Child/32', '1', '4'], 'quantity':3.5},
               {'variation':['size/Child/32', '2', '4'], 'quantity':4.},
               {'variation':['size/Child/32', '3', '4'], 'quantity':4.5},
               {'variation':['size/Child/32', '1', '5'], 'quantity':5.},
               {'variation':['size/Child/32', '2', '5'], 'quantity':5.5},
               {'variation':['size/Child/32', '3', '5'], 'quantity':6.},

               {'variation':['size/Child/34', '1', '4'], 'quantity':6.5},
               {'variation':['size/Child/34', '2', '4'], 'quantity':7.},
               {'variation':['size/Child/34', '3', '4'], 'quantity':7.5},
               {'variation':['size/Child/34', '1', '5'], 'quantity':8.},
               {'variation':['size/Child/34', '2', '5'], 'quantity':8.5},
               {'variation':['size/Child/34', '3', '5'], 'quantity':9.},

               {'variation':['size/Man', '1', '4'], 'quantity':9.5},
               {'variation':['size/Man', '2', '4'], 'quantity':10.},
               {'variation':['size/Man', '3', '4'], 'quantity':10.5},
               {'variation':['size/Man', '1', '5'], 'quantity':11.},
               {'variation':['size/Man', '2', '5'], 'quantity':11.5},
               {'variation':['size/Man', '3', '5'], 'quantity':12.},

               {'variation':['size/Woman', '1', '4'], 'quantity':12.5},
               {'variation':['size/Woman', '2', '4'], 'quantity':13.},
               {'variation':['size/Woman', '3', '4'], 'quantity':13.5},
               {'variation':['size/Woman', '1', '5'], 'quantity':14.},
               {'variation':['size/Woman', '2', '5'], 'quantity':14.5},
               {'variation':['size/Woman', '3', '5'], 'quantity':15.},
             ]
           }, # line end
           {'resource':1, 'cells': [
               {'variation':['size/Man', '2', '4'], 'quantity':15.5},
               {'variation':['size/Man', '3', '4'], 'quantity':16.},
             ]
           }, # line end
           {'resource':2, 'cells': [
               {'variation':['size/Baby', '3', '5'], 'quantity':16.5},
             ]
           }  # line end
        ]
      }, # packing list end
      { 'source':6, 'destination':3, 'source_section':4, 'destination_section':0,
        'source_payment':5, 'destination_payment':1, 'start_date':DateTime()-25, 'lines':[
           {'resource':0, 'cells': [
               {'variation':['size/Baby', '1', '4'], 'quantity':16.5},
               {'variation':['size/Baby', '2', '4'], 'quantity':17.},
               {'variation':['size/Baby', '3', '4'], 'quantity':17.5},
               {'variation':['size/Baby', '1', '5'], 'quantity':18.},
               {'variation':['size/Baby', '2', '5'], 'quantity':18.5},
               {'variation':['size/Baby', '3', '5'], 'quantity':19.},
               {'variation':['size/Woman', '2', '4'], 'quantity':19.5},
             ]
           }, # line end
           {'resource':2, 'cells': [
               {'variation':['size/Baby', '3', '5'], 'quantity':20.},
             ]
           } # line end
        ]
      }, # packing list end
      { 'source':2, 'destination':9, 'source_section':0, 'destination_section':7,
        'source_payment':1, 'destination_payment':8, 'start_date':DateTime()-15, 'lines':[
           {'resource':0, 'cells': [
               {'variation':['size/Baby', '2', '4'], 'quantity':.25},
               {'variation':['size/Baby', '3', '4'], 'quantity':.5},
               {'variation':['size/Baby', '1', '5'], 'quantity':.75},
               {'variation':['size/Baby', '2', '5'], 'quantity':1.},
               {'variation':['size/Baby', '3', '5'], 'quantity':1.25},

               {'variation':['size/Child/32', '1', '4'], 'quantity':1.5},
               {'variation':['size/Child/32', '2', '4'], 'quantity':1.75},
               {'variation':['size/Child/32', '3', '4'], 'quantity':2.},
               {'variation':['size/Child/32', '1', '5'], 'quantity':2.25},
               {'variation':['size/Child/32', '2', '5'], 'quantity':2.5},
               {'variation':['size/Child/32', '3', '5'], 'quantity':2.75},

               {'variation':['size/Child/34', '1', '4'], 'quantity':3.},
               {'variation':['size/Child/34', '2', '4'], 'quantity':3.25},
               {'variation':['size/Child/34', '3', '4'], 'quantity':3.5},
               {'variation':['size/Child/34', '1', '5'], 'quantity':3.75},
               {'variation':['size/Child/34', '2', '5'], 'quantity':4.},
               {'variation':['size/Child/34', '3', '5'], 'quantity':4.25},

               {'variation':['size/Man', '1', '4'], 'quantity':4.5},
               {'variation':['size/Man', '2', '4'], 'quantity':4.75},
               {'variation':['size/Man', '3', '4'], 'quantity':5.},
               {'variation':['size/Man', '1', '5'], 'quantity':5.25},
               {'variation':['size/Man', '2', '5'], 'quantity':5.5},
               {'variation':['size/Man', '3', '5'], 'quantity':5.75},

               {'variation':['size/Woman', '1', '4'], 'quantity':6.},
               {'variation':['size/Woman', '2', '4'], 'quantity':6.5},
               {'variation':['size/Woman', '3', '4'], 'quantity':7.},
               {'variation':['size/Woman', '1', '5'], 'quantity':7.5},
               {'variation':['size/Woman', '2', '5'], 'quantity':8.},
               {'variation':['size/Woman', '3', '5'], 'quantity':8.5},
             ]
           }, # line end
           {'resource':1, 'cells': [
               {'variation':['size/Man', '3', '4'], 'quantity':6.},
             ]
           }, # line end
        ]
      }, # packing list end
      { 'source':3, 'destination':9, 'source_section':0, 'destination_section':7,
        'source_payment':1, 'destination_payment':8, 'start_date':DateTime()-10, 'lines':[
           {'resource':0, 'cells': [
               {'variation':['size/Baby', '1', '5'], 'quantity':7.5},
               {'variation':['size/Baby', '2', '5'], 'quantity':5.},
               {'variation':['size/Baby', '3', '5'], 'quantity':3.},
             ]
           }, # line end
           {'resource':2, 'cells': [
               {'variation':['size/Baby', '3', '5'], 'quantity':18.},
             ]
           }, # line end
        ]
      }, # packing list end
    ]

    packing_list_list = []
    delivery_line_list = []
    organisation_list = sequence.get('organisation_list')
    resource_list = sequence.get('resource_list')
    packing_list_module = self.getPortal().getDefaultModule(self.packing_list_portal_type)

    for data in data_list:
      # Create Packing List
      packing_list = packing_list_module.newContent(
          portal_type=self.packing_list_portal_type,
          specialise=self.business_process)
      packing_list_list.append(packing_list)
      # Add properties
      property_list = [x for x in data.items() if x[0] not in ('lines','start_date')]
      property_list = [(x[0], organisation_list[x[1]].getRelativeUrl()) for x in property_list] + \
                      [x for x in data.items() if x[0] in ('start_date',)]
      property_dict = {}
      property_dict['price_currency'] = self.price_currency
      for (id_, value) in property_list:
        property_dict[id_] = value
      packing_list.edit(**property_dict)
      for line in data['lines']:
        # Create Packing List Line
        packing_list_line = packing_list.newContent(portal_type=self.packing_list_line_portal_type)
        delivery_line_list.append(packing_list_line)
        resource_value = resource_list[line['resource']]
        resource_value.setVariationBaseCategoryList(base_category_list)
        variation_category_list = resource_value.getVariationRangeCategoryList(base_category_list=['size']) + \
            ['colour/' + x.getRelativeUrl() for x in resource_value.objectValues(portal_type='Apparel Model Colour Variation')] + \
            ['morphology/' + x.getRelativeUrl() for x in resource_value.objectValues(portal_type='Apparel Model Morphology Variation')]

        packing_list_line.edit(
            resource_value = resource_value,
            variation_category_list=variation_category_list
        )

        # Set cell range
        base_category_dict = {}
        for i in range(len(base_category_list)):
          base_category_dict[base_category_list[i]] = i

        # Set cells
        for cell in line['cells']:
          variation = cell['variation']
          for i in range(len(variation)):
            c = variation[i]
            if len(c.split('/')) == 1:
              variation[i] = '%s/%s' % (base_category_list[i], resource_value[c].getRelativeUrl())
          new_variation = []
          self.assertTrue(len(packing_list_line.getVariationBaseCategoryList())>0)
          for bc in packing_list_line.getVariationBaseCategoryList():
            new_variation.append(variation[base_category_dict[bc]])
          variation = new_variation
          packing_list_cell = packing_list_line.newCell(base_id='movement', *variation)
          packing_list_cell.edit(
              quantity = cell['quantity'],
              predicate_category_list = variation,
              variation_category_list = variation,
              mapped_value_property_list = ['quantity'],
              )
    sequence.edit(packing_list_list = packing_list_list)

  def stepCreateTestingCategories(self, sequence=None, sequence_list=None, **kw):
    """
      Create some categories and affect them to resources and organisations
    """
    category_tool = self.getPortal().portal_categories
    organisation_list = sequence.get('organisation_list')
    resource_list = sequence.get('resource_list')

    bc = category_tool.newContent(portal_type = 'Base Category', id = 'testing_category')
    self.createCategory(bc, ['a', ['aa', 'ab'], 'o', 'z', ['za', 'zb', ['zba', 'zbb'], 'zc'] ])
    self.tic()

    category_org_list = [ ['testing_category/a/aa', 'testing_category/o'], # 0
                          ['testing_category/a/aa', 'testing_category/z'], # 1
                          ['testing_category/a/aa', 'testing_category/z/zb/zba'], # 2
                          ['testing_category/a/aa', 'testing_category/z/zb/zbb'], # 3
                          ['testing_category/o', 'testing_category/z'], # 4
                          ['testing_category/z', 'testing_category/z/zc'], # 5
                          ['testing_category/z', 'testing_category/a/ab'],# 6
                          ['testing_category/o', 'testing_category/z/zc'], # 7
                          ['testing_category/z', 'testing_category/a/ab'], # 8
                          ['testing_category/a', 'testing_category/z/zb'],# 9
                        ]

    category_res_list = [ ['testing_category/a/aa', 'testing_category/z'],
                          ['testing_category/a/aa', 'testing_category/z/za'],
                          ['testing_category/a/aa', 'testing_category/o']
                        ]

    for i in range(len(category_org_list)):
      organisation = organisation_list[i]
      new_categories = category_org_list[i]
      organisation.edit(categories = organisation.getCategoryList() + new_categories)
    for i in range(len(category_res_list)):
      resource = resource_list[i]
      new_categories = category_res_list[i]
      resource.edit(categories = resource.getCategoryList() + new_categories)


  def stepTestGetInventoryOnNode(self, sequence=None, sequence_list=None, **kw):
    """
      Test getInventory on each node
    """
    organisation_list = sequence.get('organisation_list')
    expected_values_list = [
      {'id':2, 'values':[{'date':DateTime()-28, 'inventory':280.5},
                         {'date':DateTime()-20, 'inventory':280.5},
                         {'date':DateTime()-12, 'inventory':162.},
                         {'date':DateTime(),    'inventory':162.},]
      },
      {'id':3, 'values':[{'date':DateTime()-28, 'inventory':0.},
                         {'date':DateTime()-20, 'inventory':146.},
                         {'date':DateTime()-12, 'inventory':146.},
                         {'date':DateTime(),    'inventory':112.5},]
      },
      {'id':6, 'values':[{'date':DateTime()-28, 'inventory':-280.5},
                         {'date':DateTime()-20, 'inventory':-426.5},
                         {'date':DateTime()-12, 'inventory':-426.5},
                         {'date':DateTime(),    'inventory':-426.5},]
      },
      {'id':9, 'values':[{'date':DateTime()-28, 'inventory':0.},
                         {'date':DateTime()-20, 'inventory':0.},
                         {'date':DateTime()-12, 'inventory':118.5},
                         {'date':DateTime(),    'inventory':152.},]
      },
    ]

    for expected_values in expected_values_list:
      organisation = organisation_list[expected_values['id']]
      url = organisation.getRelativeUrl()
      values = expected_values['values']
      for value in values:
        date = value['date']
        e_inventory = value['inventory']
        self._testGetInventory(expected=e_inventory, at_date=date, node=url)


  def stepTestGetInventoryOnPayment(self, sequence=None, sequence_list=None, **kw):
    """
      Test getInventory on each payment
    """
    organisation_list = sequence.get('organisation_list')
    expected_values_list = [
      {'id':1, 'values':[{'date':DateTime()-28, 'inventory':280.5},
                         {'date':DateTime()-20, 'inventory':426.5},
                         {'date':DateTime()-12, 'inventory':308.},
                         {'date':DateTime(),    'inventory':274.5},]
      },
      {'id':5, 'values':[{'date':DateTime()-28, 'inventory':-280.5},
                         {'date':DateTime()-20, 'inventory':-426.5},
                         {'date':DateTime()-12, 'inventory':-426.5},
                         {'date':DateTime(),    'inventory':-426.5},]
      },
      {'id':8, 'values':[{'date':DateTime()-28, 'inventory':0.},
                         {'date':DateTime()-20, 'inventory':0.},
                         {'date':DateTime()-12, 'inventory':118.5},
                         {'date':DateTime(),    'inventory':152.},]
      },
    ]

    for expected_values in expected_values_list:
      organisation = organisation_list[expected_values['id']]
      url = organisation.getRelativeUrl()
      values = expected_values['values']
      for value in values:
        date = value['date']
        e_inventory = value['inventory']
        self._testGetInventory(expected=e_inventory, at_date=date, payment=url)


  def stepTestGetInventoryOnSection(self, sequence=None, sequence_list=None, **kw):
    """
      Test getInventory on each section
    """
    organisation_list = sequence.get('organisation_list')
    expected_values_list = [
      {'id':0, 'values':[{'date':DateTime()-28, 'inventory':280.5},
                         {'date':DateTime()-20, 'inventory':426.5},
                         {'date':DateTime()-12, 'inventory':308.},
                         {'date':DateTime(),    'inventory':274.5},]
      },
      {'id':4, 'values':[{'date':DateTime()-28, 'inventory':-280.5},
                         {'date':DateTime()-20, 'inventory':-426.5},
                         {'date':DateTime()-12, 'inventory':-426.5},
                         {'date':DateTime(),    'inventory':-426.5},]
      },
      {'id':7, 'values':[{'date':DateTime()-28, 'inventory':0.},
                         {'date':DateTime()-20, 'inventory':0.},
                         {'date':DateTime()-12, 'inventory':118.5},
                         {'date':DateTime(),    'inventory':152.},]
      },
    ]

    for expected_values in expected_values_list:
      organisation = organisation_list[expected_values['id']]
      url = organisation.getRelativeUrl()
      values = expected_values['values']
      for value in values:
        date = value['date']
        e_inventory = value['inventory']
        self._testGetInventory(expected=e_inventory, at_date=date, section=url)


  def stepTestGetInventoryOnMirrorSection(self, sequence=None, sequence_list=None, **kw):
    """
      Test getInventory on each mirror section
    """
    organisation_list = sequence.get('organisation_list')
    expected_values_list = [
      {'id':0, 'values':[{'date':DateTime()-28, 'inventory':-280.5},
                         {'date':DateTime()-20, 'inventory':-426.5},
                         {'date':DateTime()-12, 'inventory':-308.},
                         {'date':DateTime(),    'inventory':-274.5},]
      },
      {'id':4, 'values':[{'date':DateTime()-28, 'inventory':280.5},
                         {'date':DateTime()-20, 'inventory':426.5},
                         {'date':DateTime()-12, 'inventory':426.5},
                         {'date':DateTime(),    'inventory':426.5},]
      },
      {'id':7, 'values':[{'date':DateTime()-28, 'inventory':0.},
                         {'date':DateTime()-20, 'inventory':0.},
                         {'date':DateTime()-12, 'inventory':-118.5},
                         {'date':DateTime(),    'inventory':-152.},]
      },
    ]

    for expected_values in expected_values_list:
      organisation = organisation_list[expected_values['id']]
      url = organisation.getRelativeUrl()
      values = expected_values['values']
      for value in values:
        date = value['date']
        e_inventory = value['inventory']
        self._testGetInventory(expected=e_inventory, at_date=date, mirror_section=url)


  def stepTestGetInventoryOnResource(self, sequence=None, sequence_list=None, **kw):
    """
      Test getInventory on each resource
    """
    resource_list = sequence.get('resource_list')
    organisation_list = sequence.get('organisation_list')
    expected_values_list = [
      {'id':0, 'values':[{'date':DateTime()-28, 'inventory':232.5},
                         {'date':DateTime()-20, 'inventory':358.5},
                         {'date':DateTime()-12, 'inventory':246.},
                         {'date':DateTime(),    'inventory':230.5},]
      },
      {'id':1, 'values':[{'date':DateTime()-28, 'inventory':31.5},
                         {'date':DateTime()-20, 'inventory':31.5},
                         {'date':DateTime()-12, 'inventory':25.5},
                         {'date':DateTime(),    'inventory':25.5},]
      },
      {'id':2, 'values':[{'date':DateTime()-28, 'inventory':16.5},
                         {'date':DateTime()-20, 'inventory':36.5},
                         {'date':DateTime()-12, 'inventory':36.5},
                         {'date':DateTime(),    'inventory':18.5},]
      },
    ]

    organisation_url = organisation_list[0].getRelativeUrl()
    for expected_values in expected_values_list:
      resource = resource_list[expected_values['id']]
      url = resource.getRelativeUrl()
      values = expected_values['values']
      for value in values:
        date = value['date']
        e_inventory = value['inventory']
        self._testGetInventory(expected=e_inventory, at_date=date, resource=url, section=organisation_url)


  def stepTestGetInventoryOnVariationText(self, sequence=None, sequence_list=None, **kw):
    """

    """
    delivery = sequence.get('packing_list_list')[0]
    expected_values_list = [
      {'text':delivery['1']['movement_0_0_0'],
              'values':[{'inventory':17.},]
      },
    ]

    organisation_list = sequence.get('organisation_list')
    organisation_url = organisation_list[0].getRelativeUrl()
    for expected_values in expected_values_list:
      variation_text = expected_values['text'].getVariationText()
      values = expected_values['values']
      for value in values:
        e_inventory = value['inventory']
        self._testGetInventory(expected=e_inventory, variation_text=variation_text, section=organisation_url)

  def stepTestInventoryListBrainGetQuantity(self, sequence=None, sequence_list=None, **kw):
    """

    """
    simulation = self.getPortal().portal_simulation
    delivery = sequence.get('packing_list_list')[0]

    organisation_list = sequence.get('organisation_list')
    organisation_url = organisation_list[0].getRelativeUrl()
    movement = delivery['1']['movement_0_0_0']
    variation_text = movement.getVariationText()
    inventory_kw = {'section':organisation_url,
                    'variation_text':variation_text}
    simulation = self.getPortal().portal_simulation
    uid = movement.getUid()
    inventory_list = simulation.getInventoryList(**inventory_kw)
    found = 0
    for inventory in inventory_list:
      inventory_object = inventory.getObject()
      if inventory_object.getUid()==uid:
        found=1
        self.assertEqual(inventory_object.getQuantity(), 0.5)
        self.assertEqual(inventory.getQuantity(), 0.5)
    self.assertTrue(found==1)



  def stepTestGetInventoryOnVariationCategory(self, sequence=None, sequence_list=None, **kw):
    """
      Test getInventory on some variation categories
    """
    resource_list = sequence.get('resource_list')
    organisation_list = sequence.get('organisation_list')
    expected_values_list = [
      {'id':'size/Baby', 'values':[{'date':DateTime()-28, 'inventory':27.},
                                   {'date':DateTime()-20, 'inventory':153.5},
                                   {'date':DateTime()-12, 'inventory':149.75},
                                   {'date':DateTime(),    'inventory':116.25},]
      },
      {'id':'size/Child/32', 'values':[{'date':DateTime()-28, 'inventory':28.5},
                                       {'date':DateTime()-20, 'inventory':28.5},
                                       {'date':DateTime()-12, 'inventory':15.75},
                                       {'date':DateTime(),    'inventory':15.75},]
      },
      {'id':'size/Child/34', 'values':[{'date':DateTime()-28, 'inventory':46.5},
                                       {'date':DateTime()-20, 'inventory':46.5},
                                       {'date':DateTime()-12, 'inventory':24.75},
                                       {'date':DateTime(),    'inventory':24.75},]
      },
      {'id':'size/Man', 'values':[{'date':DateTime()-28, 'inventory':96.},
                                  {'date':DateTime()-20, 'inventory':96.},
                                  {'date':DateTime()-12, 'inventory':59.25},
                                  {'date':DateTime(),    'inventory':59.25},]
      },
      {'id':'size/Woman', 'values':[{'date':DateTime()-28, 'inventory':82.5},
                                    {'date':DateTime()-20, 'inventory':102.},
                                    {'date':DateTime()-12, 'inventory':58.5},
                                    {'date':DateTime(),    'inventory':58.5},]
      },
      {'id':['size/Baby', 'colour/' + resource_list[0]['3'].getRelativeUrl()],
                        'values':[{'date':DateTime()-28, 'inventory':105.},
                                  {'date':DateTime()-20, 'inventory':231.5},
                                  {'date':DateTime()-12, 'inventory':189.},
                                  {'date':DateTime(),    'inventory':155.5},]
      },
      {'id':['size/Man', 'colour/' + resource_list[0]['3'].getRelativeUrl(), 'morphology/' + resource_list[0]['4'].getRelativeUrl()],
                        'values':[{'date':DateTime()-28, 'inventory':204.},
                                  {'date':DateTime()-20, 'inventory':293.5},
                                  {'date':DateTime()-12, 'inventory':204.75},
                                  {'date':DateTime(),    'inventory':201.75},]
      },


    ]

    organisation_url = organisation_list[0].getRelativeUrl()
    for expected_values in expected_values_list:
      category_list = expected_values['id']
      values = expected_values['values']
      for value in values:
        date = value['date']
        e_inventory = value['inventory']
        self._testGetInventory(expected=e_inventory,
                               at_date=date,
                               variation_category=category_list,
                               section=organisation_url)


  def stepTestGetInventoryWithOmitOutput(self, sequence=None,
                                         sequence_list=None, **kw):
    """
      Test getInventory on each node with omit_output
    """
    organisation_list = sequence.get('organisation_list')
    expected_values_list = [
      {'id':2, 'values':[{'date':DateTime()-28, 'inventory':280.5},
                         {'date':DateTime()-20, 'inventory':280.5},
                         {'date':DateTime()-12, 'inventory':280.5},
                         {'date':DateTime(),    'inventory':280.5},]
      },
      {'id':3, 'values':[{'date':DateTime()-28, 'inventory':0.},
                         {'date':DateTime()-20, 'inventory':146.},
                         {'date':DateTime()-12, 'inventory':146.},
                         {'date':DateTime(),    'inventory':146.},]
      },
      {'id':6, 'values':[{'date':DateTime()-28, 'inventory':0.},
                         {'date':DateTime()-20, 'inventory':0.},
                         {'date':DateTime()-12, 'inventory':0.},
                         {'date':DateTime(),    'inventory':0.},]
      },
      {'id':9, 'values':[{'date':DateTime()-28, 'inventory':0.},
                         {'date':DateTime()-20, 'inventory':0.},
                         {'date':DateTime()-12, 'inventory':118.5},
                         {'date':DateTime(),    'inventory':152.},]
      },
    ]

    for expected_values in expected_values_list:
      organisation = organisation_list[expected_values['id']]
      url = organisation.getRelativeUrl()
      values = expected_values['values']
      for value in values:
        date = value['date']
        e_inventory = value['inventory']
        self._testGetInventory(expected=e_inventory,
                               at_date=date,
                               node=url,
                               omit_output=1)


  def stepTestGetInventoryWithOmitInput(self, sequence=None, sequence_list=None, **kw):
    """
      Test getInventory on each node with omit_input
    """
    organisation_list = sequence.get('organisation_list')
    expected_values_list = [
      {'id':2, 'values':[{'date':DateTime()-28, 'inventory':0.},
                         {'date':DateTime()-20, 'inventory':0.},
                         {'date':DateTime()-12, 'inventory':-118.5},
                         {'date':DateTime(),    'inventory':-118.5},]
      },
      {'id':3, 'values':[{'date':DateTime()-28, 'inventory':0.},
                         {'date':DateTime()-20, 'inventory':0.},
                         {'date':DateTime()-12, 'inventory':0.},
                         {'date':DateTime(),    'inventory':-33.5},]
      },
      {'id':6, 'values':[{'date':DateTime()-28, 'inventory':-280.5},
                         {'date':DateTime()-20, 'inventory':-426.5},
                         {'date':DateTime()-12, 'inventory':-426.5},
                         {'date':DateTime(),    'inventory':-426.5},]
      },
      {'id':9, 'values':[{'date':DateTime()-28, 'inventory':0.},
                         {'date':DateTime()-20, 'inventory':0.},
                         {'date':DateTime()-12, 'inventory':0.},
                         {'date':DateTime(),    'inventory':0.},]
      },
    ]

    for expected_values in expected_values_list:
      organisation = organisation_list[expected_values['id']]
      url = organisation.getRelativeUrl()
      values = expected_values['values']
      for value in values:
        date = value['date']
        e_inventory = value['inventory']
        self._testGetInventory(expected=e_inventory,
                               at_date=date,
                               node=url,
                               omit_input=1)


  def stepTestGetInventoryOnSectionCategory(self, sequence=None,
                                            sequence_list=None, **kw):
    """
      Test getInventory with a section_category argument
    """
    expected_values_list = [
      {'id':'testing_category/a/aa', 'values':[{'inventory':274.5},] },
      {'id':'testing_category/z/zc', 'values':[{'inventory':152.},] },
      {'id':'testing_category/z', 'values':[{'inventory':-274.5},] },
      {'id':'testing_category/o', 'values':[{'inventory':0.},] },
    ]

    for expected_values in expected_values_list:
      category = expected_values['id']
      values = expected_values['values']
      for value in values:
        e_inventory = value['inventory']
        self._testGetInventory(expected=e_inventory,
                               section_category=category)


  def stepTestGetInventoryOnPaymentCategory(self, sequence=None,
                                            sequence_list=None, **kw):
    """
      Test getInventory with a payment_category argument
    """
    expected_values_list = [
      {'id':'testing_category/a/aa', 'values':[{'inventory':274.5},] },
      {'id':'testing_category/z/zc', 'values':[{'inventory':-426.5},] },
      {'id':'testing_category/a/ab', 'values':[{'inventory':152.},] },
      {'id':'testing_category/a', 'values':[{'inventory':426.5},] },
    ]

    for expected_values in expected_values_list:
      category = expected_values['id']
      values = expected_values['values']
      for value in values:
        e_inventory = value['inventory']
        self._testGetInventory(expected=e_inventory,
                               payment_category=category)


  def stepTestGetInventoryOnNodeCategory(self, sequence=None,
                                         sequence_list=None, **kw):
    """
      Test getInventory with a node_category argument
    """
    expected_values_list = [
      {'id':'testing_category/z/zb/zba', 'values':[{'inventory':162.},] },
      {'id':'testing_category/z/zb/zbb', 'values':[{'inventory':112.5},] },
      {'id':'testing_category/a/ab', 'values':[{'inventory':-426.5},] },
      {'id':'testing_category/a', 'values':[{'inventory':0.},] },
      {'id':'testing_category/z', 'values':[{'inventory':0.},] },
    ]

    for expected_values in expected_values_list:
      category = expected_values['id']
      values = expected_values['values']
      for value in values:
        e_inventory = value['inventory']
        self._testGetInventory(expected=e_inventory, node_category=category)


  def stepTestGetInventoryOnMirrorSectionCategory(self, sequence=None, sequence_list=None, **kw):
    """
      Test getInventory with a section_category argument
    """
    expected_values_list = [
      {'id':'testing_category/a/aa', 'values':[{'inventory':-274.5},] },
      {'id':'testing_category/z/zc', 'values':[{'inventory':-152.},] },
      {'id':'testing_category/z', 'values':[{'inventory':274.5},] },
      {'id':'testing_category/o', 'values':[{'inventory':0.},] },
    ]

    for expected_values in expected_values_list:
      category = expected_values['id']
      values = expected_values['values']
      for value in values:
        e_inventory = value['inventory']
        self._testGetInventory(expected=e_inventory, mirror_section_category=category)


  def stepTestGetInventoryOnResourceCategory(self, sequence=None, sequence_list=None, **kw):
    """
      Test getInventory with a resource_category argument
    """
    organisation_list = sequence.get('organisation_list')
    expected_values_list = [
      {'id':'testing_category/a/aa', 'values':[{'inventory':274.5},] },
      {'id':'testing_category/o', 'values':[{'inventory':18.5},] },
      {'id':'testing_category/z/za', 'values':[{'inventory':25.5},] },
      {'id':'testing_category/z', 'values':[{'inventory':256.},] },
    ]

    for expected_values in expected_values_list:
      category = expected_values['id']
      values = expected_values['values']
      for value in values:
        e_inventory = value['inventory']
        self._testGetInventory(expected=e_inventory,
                               resource_category=category,
                               section=organisation_list[0].getRelativeUrl())


  def _testGetInventory(self, expected, **kw):
    """
      Shared testing method
    """
    simulation = self.getPortal().portal_simulation
    e_inventory = expected
    LOG('Testing inventory with args :', 0, kw)
    a_inventory = simulation.getInventory(**kw)
    if e_inventory != a_inventory:
      msg = 'Inventory differs between expected (%s) and real (%s) quantities'\
             % (repr(e_inventory), repr(a_inventory))
      LOG('TestInventory._testGetInventory', 0, msg)
      LOG('SQL Query was : ', 0, str(simulation.getInventory(src__=1, **kw)))
      self.assertEqual(e_inventory, a_inventory, msg)


  def stepTestGetInventoryOnSimulationState(self, sequence=None,
                                            sequence_list=None, **kw):
    """
      Test getInventory with some simulation states, by using
      methods getCurrentInventory, getAvailableInventory and getFutureInventory
    """
    packing_list_workflow = 'packing_list_workflow'
    state_variable = 'simulation_state'
    packing_list_list = sequence.get('packing_list_list')
    workflow_tool = self.getPortal().portal_workflow
    simulation = self.getPortal().portal_simulation
    transit_simulation_state = ['started']

    transition_list = [
       {'id':0, 'action':'confirm_action'}, # a
       {'id':0, 'action':'set_ready_action'}, # b
              {'id':1, 'action':'confirm_action'}, # c
       {'id':0, 'action':'start_action'}, # d
                     {'id':2, 'action':'confirm_action'}, # e
       {'id':0, 'action':'stop_action'}, # f
                     {'id':2, 'action':'set_ready_action'}, # g
                     {'id':2, 'action':'start_action'}, # h
                            {'id':3, 'action':'confirm_action'}, # i
                            {'id':3, 'action':'set_ready_action'}, # j
                            {'id':3, 'action':'start_action'}, # k
                            {'id':3, 'action':'stop_action'}, # l
    ]

    expected_values_list = [
     #( without omit_transit, with omit_transit)
      ({'Current':  0.  , 'Available': 0.  , 'Future':  0.  },
       {'Current':  0.  , 'Available': 0.  , 'Future':  0.  }),
      ({'Current':  0.  , 'Available': 0.  , 'Future':280.5 }, # a
       {'Current':  0.  , 'Available': 0.  , 'Future':280.5 }),
      ({'Current':  0.  , 'Available': 0.  , 'Future':280.5 }, # b
       {'Current':  0.  , 'Available': 0.  , 'Future':280.5 }),
      ({'Current':  0.  , 'Available': 0.  , 'Future':426.5 }, # c
       {'Current':  0.  , 'Available': 0.  , 'Future':426.5 }),
      ({'Current':280.5 , 'Available': 280.5  , 'Future':426.5 }, # d
       {'Current':  0.  , 'Available': 0.  , 'Future':146.  }),
      ({'Current':280.5 , 'Available': 162.  , 'Future':308.  }, # e
       {'Current':  0.  , 'Available': -118.5  , 'Future': 27.5 }),
      ({'Current':280.5 , 'Available': 162.  , 'Future':308.  }, # f
       {'Current':280.5 , 'Available': 162.  , 'Future':308.  }),
      ({'Current':280.5 , 'Available': 162.  , 'Future':308.  }, # g
       {'Current':280.5 , 'Available': 162.  , 'Future':308.  }),
      ({'Current':162.  , 'Available': 162.  , 'Future':308.  }, # h
       {'Current':162.  , 'Available': 162.  , 'Future':308.  }),
      ({'Current':162.  , 'Available': 128.5  , 'Future':274.5 }, # i
       {'Current':162.  , 'Available': 128.5  , 'Future':274.5 }),
      ({'Current':162.  , 'Available': 128.5   , 'Future':274.5 }, # j
       {'Current':162.  , 'Available': 128.5  , 'Future':274.5 }),
      ({'Current':128.5 , 'Available': 128.5  , 'Future':274.5 }, # k
       {'Current':128.5 , 'Available': 128.5  , 'Future':274.5 }),
      ({'Current':128.5 , 'Available': 128.5  , 'Future':274.5 }, # l
       {'Current':128.5 , 'Available': 128.5  , 'Future':274.5 }),
    ]

    organisation_list = sequence.get('organisation_list')
    organisation_url = organisation_list[0].getRelativeUrl()
    date = DateTime()

    def _testWithState(expected_values, omit_transit):
      # Get current workflow states to add it to the log
      state_list = []
      for packing_list in packing_list_list:
        state_list.append(workflow_tool.getStatusOf(
                packing_list_workflow, packing_list)[state_variable])

      LOG('Testing with these workflow states :', 0, state_list)
      for name, e_inventory in expected_values.items():
        method_name = 'get%sInventory' % name
        method = getattr(simulation, method_name, None)
        if method is None:
          LOG('TEST ERROR : Simulation Tool has no %s method'
              % method_name, 0, '')
          raise AssertionError
        a_inventory = method(section=organisation_url,
                             omit_transit=omit_transit,
                             transit_simulation_state=transit_simulation_state,
                             at_date=date)
        if a_inventory != e_inventory:
          LOG('TEST ERROR : Inventory quantity differs between expected (%s) and real (%s) quantities' % (repr(e_inventory), repr(a_inventory)), 0, 'with method %s and omit_transit=%s' % (method_name, omit_transit))
          LOG('SQL Query was :', 0, method(section=organisation_url,
                             omit_transit=omit_transit,
                             transit_simulation_state=transit_simulation_state,
                             at_date=date, src__=1))
          self.assertEqual(a_inventory, e_inventory)

    # First, test with draft state everywhere
    LOG('Testing Inventory with every Packing List in draft state...', 0, '')
    for omit_transit in (0,1):
      _testWithState(expected_values_list[0][omit_transit], omit_transit)

    i = 0
    for expected_values in expected_values_list[1:]:
      self.tic() # acceptable here because this is not the job
                 # of the test to check if can do all transition
                 # without processing messages
      transition_step = transition_list[i]
      transited_pl = packing_list_list[transition_step['id']]
      action = transition_step['action']
      LOG("Transiting '%s' on packing list %s" % (action, transition_step['id']), 0, '')
      workflow_tool.doActionFor(transited_pl, action, packing_list_workflow)
      self.tic()

      for omit_transit in (0,1):
        values = expected_values[omit_transit]
        _testWithState(values, omit_transit)

      i += 1


  def stepTestGetInventoryWithSelectionReport(self, sequence=None, sequence_list=None, **kw):
    """
    """
    organisation_list = sequence.get('organisation_list')
    expected_values_list = [
      {'id':2, 'values':[{'date':DateTime()-28, 'inventory':280.5},
                         {'date':DateTime()-20, 'inventory':280.5},
                         {'date':DateTime()-12, 'inventory':162.},
                         {'date':DateTime(),    'inventory':162.},]
      },
      {'id':3, 'values':[{'date':DateTime()-28, 'inventory':0.},
                         {'date':DateTime()-20, 'inventory':146.},
                         {'date':DateTime()-12, 'inventory':146.},
                         {'date':DateTime(),    'inventory':112.5},]
      },
      {'id':6, 'values':[{'date':DateTime()-28, 'inventory':-280.5},
                         {'date':DateTime()-20, 'inventory':-426.5},
                         {'date':DateTime()-12, 'inventory':-426.5},
                         {'date':DateTime(),    'inventory':-426.5},]
      },
      {'id':9, 'values':[{'date':DateTime()-28, 'inventory':0.},
                         {'date':DateTime()-20, 'inventory':0.},
                         {'date':DateTime()-12, 'inventory':118.5},
                         {'date':DateTime(),    'inventory':152.},]
      },
    ]

    for expected_values in expected_values_list:
      selection_domain = DomainSelection(domain_dict = {'destination_section':organisation_list[expected_values['id']],
                                                        'source_section':organisation_list[expected_values['id']]})
      values = expected_values['values']
      for value in values:
        date = value['date']
        e_inventory = value['inventory']
        self._testGetInventory(expected=e_inventory, at_date=date, selection_domain=selection_domain)


  def stepTestGetInventoryListOnSection(self, sequence=None, sequence_list=None, **kw):
    """
      Test getInventoryList on a section
    """
    organisation_list = sequence.get('organisation_list')
    resource_list = sequence.get('resource_list')

    # Build expected list
    expected_list = []
    for i in range(1, 31):
      quantity = (i + 0.) / 2
      expected_list.append({ 'node_relative_url': 2,
                             'section_relative_url': 0,
                             'resource_relative_url': 0,
                             'inventory': quantity })
    for i in range(31, 33):
      quantity = (i + 0.) / 2
      expected_list.append({ 'node_relative_url': 2,
                             'section_relative_url': 0,
                             'resource_relative_url': 1,
                             'inventory': quantity })
    for i in range(33, 34):
      quantity = (i + 0.) / 2
      expected_list.append({ 'node_relative_url': 2,
                             'section_relative_url': 0,
                             'resource_relative_url': 2,
                             'inventory': quantity })
    for i in range(33, 40):
      quantity = (i + 0.) / 2
      expected_list.append({ 'node_relative_url': 3,
                             'section_relative_url': 0,
                             'resource_relative_url': 0,
                             'inventory': quantity })
    for i in range(40, 41):
      quantity = (i + 0.) / 2
      expected_list.append({ 'node_relative_url': 3,
                             'section_relative_url': 0,
                             'resource_relative_url': 2,
                             'inventory': quantity })
    for i in range(1, 24):
      quantity = (i + 0.) / 4
      expected_list.append({ 'node_relative_url': 2,
                             'section_relative_url': 0,
                             'resource_relative_url': 0,
                             'inventory': - quantity })
    for i in range(12, 18):
      quantity = (i + 0.) / 2
      expected_list.append({ 'node_relative_url': 2,
                             'section_relative_url': 0,
                             'resource_relative_url': 0,
                             'inventory': - quantity })
    for i in range(12, 13):
      quantity = (i + 0.) / 2
      expected_list.append({ 'node_relative_url': 2,
                             'section_relative_url': 0,
                             'resource_relative_url': 1,
                             'inventory': - quantity })
    for i in [7.5, 5, 3]:
      quantity = (i + 0.)
      expected_list.append({ 'node_relative_url': 3,
                             'section_relative_url': 0,
                             'resource_relative_url': 0,
                             'inventory': - quantity })
    for i in [18]:
      quantity = (i + 0.)
      expected_list.append({ 'node_relative_url': 3,
                             'section_relative_url': 0,
                             'resource_relative_url': 2,
                             'inventory': - quantity })

    for i in [ [2,0,0], [2,0,1], [2,0,2], [3,0,0], [3,0,2],
               [2,0,0], [2,0,1], [3,0,0], [3,0,2] ]:
      expected_list.append({ 'node_relative_url': i[0],
                             'section_relative_url': i[1],
                             'resource_relative_url': i[2],
                             'inventory':0. })

    item_dict = { 'node': organisation_list,
                  'section': organisation_list,
                  'resource': resource_list }
    expected_l = expected_list[:]
    for expected in expected_l:
      for attribute in [x for x in expected.keys()
                          if x.endswith('_relative_url')]:
        attr_name = attribute.split('_')[0]
        expected[attribute] = item_dict[attr_name]\
                                  [expected[attribute]].getRelativeUrl()
    self._testGetInventoryList(expected=expected_l,
                               section=organisation_list[0].getRelativeUrl(),
                               omit_simulation=1)

  def stepTestGetInventoryListOnNode(self, sequence=None,
                                     sequence_list=None, **kw):
    """
      Test getInventoryList on a Node
    """
    organisation_list = sequence.get('organisation_list')
    resource_list = sequence.get('resource_list')

    # Build expected list
    expected_list = []
    for i in range(1, 31):
      quantity = (i + 0.) / 2
      expected_list.append({ 'node_relative_url': 2,
                             'section_relative_url': 0,
                             'resource_relative_url': 0,
                             'inventory': quantity })
    for i in range(31, 33):
      quantity = (i + 0.) / 2
      expected_list.append({ 'node_relative_url': 2,
                             'section_relative_url': 0,
                             'resource_relative_url': 1,
                             'inventory': quantity })
    for i in range(33, 34):
      quantity = (i + 0.) / 2
      expected_list.append({ 'node_relative_url': 2,
                             'section_relative_url': 0,
                             'resource_relative_url': 2,
                             'inventory': quantity })
    for i in range(1, 24):
      quantity = (i + 0.) / 4
      expected_list.append({ 'node_relative_url': 2,
                             'section_relative_url': 0,
                             'resource_relative_url': 0,
                             'inventory': - quantity })
    for i in range(12, 18):
      quantity = (i + 0.) / 2
      expected_list.append({ 'node_relative_url': 2,
                             'section_relative_url': 0,
                             'resource_relative_url': 0,
                             'inventory': - quantity })
    for i in range(12, 13):
      quantity = (i + 0.) / 2
      expected_list.append({ 'node_relative_url': 2,
                             'section_relative_url': 0,
                             'resource_relative_url': 1,
                             'inventory': - quantity })

    for i in [ [2,0,0], [2,0,1], [2,0,2], [2,0,0], [2,0,1] ]:
      expected_list.append({ 'node_relative_url': i[0],
                             'section_relative_url': i[1],
                             'resource_relative_url': i[2],
                             'inventory':0. })

    item_dict = { 'node': organisation_list,
                  'section': organisation_list,
                  'resource': resource_list }
    expected_l = expected_list[:]
    for expected in expected_l:
      for attribute in [x for x in expected.keys()
                            if x.endswith('_relative_url')]:
        attr_name = attribute.split('_')[0]
        expected[attribute] = item_dict[attr_name]\
                                [expected[attribute]].getRelativeUrl()
    self._testGetInventoryList( expected=expected_l,
                                node=organisation_list[2].getRelativeUrl(),
                                omit_simulation=1)


  def stepTestGetInventoryListWithOmitInput(self, sequence=None, sequence_list=None, **kw):
    """
      Test getInventoryList on a section with omit_input
    """
    organisation_list = sequence.get('organisation_list')
    resource_list = sequence.get('resource_list')

    # Build expected list
    expected_list = []
    for i in range(1, 24):
      quantity = (i + 0.) / 4
      expected_list.append({ 'node_relative_url': 2, 'section_relative_url':0, 'resource_relative_url':0, 'inventory':-quantity })
    for i in range(12, 18):
      quantity = (i + 0.) / 2
      expected_list.append({ 'node_relative_url': 2, 'section_relative_url':0, 'resource_relative_url':0, 'inventory':-quantity })
    for i in range(12, 13):
      quantity = (i + 0.) / 2
      expected_list.append({ 'node_relative_url': 2, 'section_relative_url':0, 'resource_relative_url':1, 'inventory':-quantity })
    for i in [7.5, 5, 3]:
      quantity = (i + 0.)
      expected_list.append({ 'node_relative_url': 3, 'section_relative_url':0, 'resource_relative_url':0, 'inventory':-quantity })
    for i in [18]:
      quantity = (i + 0.)
      expected_list.append({ 'node_relative_url': 3, 'section_relative_url':0, 'resource_relative_url':2, 'inventory':-quantity })

    item_dict = {'node':organisation_list, 'section':organisation_list, 'resource':resource_list}
    expected_l = expected_list[:]
    for expected in expected_l:
      for attribute in [x for x in expected.keys() if x.endswith('_relative_url')]:
        attr_name = attribute.split('_')[0]
        expected[attribute] = item_dict[attr_name][expected[attribute]].getRelativeUrl()
    self._testGetInventoryList(expected=expected_l, section=organisation_list[0].getRelativeUrl(), omit_simulation=1, omit_input=1)


  def stepTestGetInventoryListWithOmitOutput(self, sequence=None, sequence_list=None, **kw):
    """
      Test getInventoryList on a section with omit_output
    """
    organisation_list = sequence.get('organisation_list')
    resource_list = sequence.get('resource_list')

    # Build expected list
    expected_list = []
    for i in range(1, 31):
      quantity = (i + 0.) / 2
      expected_list.append({ 'node_relative_url': 2, 'section_relative_url':0, 'resource_relative_url':0, 'inventory':quantity })
    for i in range(31, 33):
      quantity = (i + 0.) / 2
      expected_list.append({ 'node_relative_url': 2, 'section_relative_url':0, 'resource_relative_url':1, 'inventory':quantity })
    for i in range(33, 34):
      quantity = (i + 0.) / 2
      expected_list.append({ 'node_relative_url': 2, 'section_relative_url':0, 'resource_relative_url':2, 'inventory':quantity })
    for i in range(33, 40):
      quantity = (i + 0.) / 2
      expected_list.append({ 'node_relative_url': 3, 'section_relative_url':0, 'resource_relative_url':0, 'inventory':quantity })
    for i in range(40, 41):
      quantity = (i + 0.) / 2
      expected_list.append({ 'node_relative_url': 3, 'section_relative_url':0, 'resource_relative_url':2, 'inventory':quantity })

    item_dict = {'node':organisation_list, 'section':organisation_list, 'resource':resource_list}
    expected_l = expected_list[:]
    for expected in expected_l:
      for attribute in [x for x in expected.keys() if x.endswith('_relative_url')]:
        attr_name = attribute.split('_')[0]
        expected[attribute] = item_dict[attr_name][expected[attribute]].getRelativeUrl()
    self._testGetInventoryList(expected=expected_l, section=organisation_list[0].getRelativeUrl(), omit_simulation=1, omit_output=1)


  def stepTestGetInventoryListWithGroupBy(self, sequence=None, sequence_list=None, **kw):
    """
      Test getInventoryList by using group_by_*
    """
    organisation_list = sequence.get('organisation_list')
    resource_list = sequence.get('resource_list')

    # Build expected list
    expected_list_list = [
      ({'group_by_node':1}, [
        {'node_relative_url': 2, 'section_relative_url':0, 'resource_relative_url':0, 'inventory':120. },
        {'node_relative_url': 2, 'section_relative_url':0, 'resource_relative_url':1, 'inventory':25.5 },
        {'node_relative_url': 2, 'section_relative_url':0, 'resource_relative_url':2, 'inventory':16.5 },
        {'node_relative_url': 3, 'section_relative_url':0, 'resource_relative_url':0, 'inventory':110.5 },
        {'node_relative_url': 3, 'section_relative_url':0, 'resource_relative_url':2, 'inventory':2. },
        {'node_relative_url': 6, 'section_relative_url':4, 'resource_relative_url':0, 'inventory':-358.5 },
        {'node_relative_url': 6, 'section_relative_url':4, 'resource_relative_url':1, 'inventory':-31.5 },
        {'node_relative_url': 6, 'section_relative_url':4, 'resource_relative_url':2, 'inventory':-36.5 },
        {'node_relative_url': 9, 'section_relative_url':7, 'resource_relative_url':0, 'inventory':128. },
        {'node_relative_url': 9, 'section_relative_url':7, 'resource_relative_url':1, 'inventory':6. },
        {'node_relative_url': 9, 'section_relative_url':7, 'resource_relative_url':2, 'inventory':18. },
      ]),
      ({'group_by_variation':1, 'section':organisation_list[0].getRelativeUrl()}, [
        {'resource_relative_url':0, 'inventory':17. },    # Baby
        {'resource_relative_url':0, 'inventory':17.75 },
        {'resource_relative_url':0, 'inventory':18.5 },
        {'resource_relative_url':0, 'inventory':11.75 },
        {'resource_relative_url':0, 'inventory':15. },
        {'resource_relative_url':0, 'inventory':17.75 },
        {'resource_relative_url':0, 'inventory':2. },     # 32
        {'resource_relative_url':0, 'inventory':2.25 },
        {'resource_relative_url':0, 'inventory':2.5 },
        {'resource_relative_url':0, 'inventory':2.75 },
        {'resource_relative_url':0, 'inventory':3. },
        {'resource_relative_url':0, 'inventory':3.25 },
        {'resource_relative_url':0, 'inventory':3.5 },    # 34
        {'resource_relative_url':0, 'inventory':3.75 },
        {'resource_relative_url':0, 'inventory':4. },
        {'resource_relative_url':0, 'inventory':4.25 },
        {'resource_relative_url':0, 'inventory':4.5 },
        {'resource_relative_url':0, 'inventory':4.75 },
        {'resource_relative_url':0, 'inventory':5. },     # Man
        {'resource_relative_url':0, 'inventory':5.25 },
        {'resource_relative_url':0, 'inventory':5.5 },
        {'resource_relative_url':0, 'inventory':5.75 },
        {'resource_relative_url':0, 'inventory':6. },
        {'resource_relative_url':0, 'inventory':6.25 },
        {'resource_relative_url':0, 'inventory':6.5 },    # Woman
        {'resource_relative_url':0, 'inventory':26. },
        {'resource_relative_url':0, 'inventory':6.5 },
        {'resource_relative_url':0, 'inventory':6.5 },
        {'resource_relative_url':0, 'inventory':6.5 },
        {'resource_relative_url':0, 'inventory':6.5 },
        {'resource_relative_url':0, 'inventory':0.}, #None }, # Sum of lines (quantity of lines is NULL)

        {'resource_relative_url':1, 'inventory':15.5 },
        {'resource_relative_url':1, 'inventory':10. },
        {'resource_relative_url':1, 'inventory':0. }, #None }, # Sum of lines (quantity of lines is ULL)

        {'resource_relative_url':2, 'inventory':18.5 },
        {'resource_relative_url':2, 'inventory':0. }, #None }, # Sum of lines (quantity of lines is NULL)
      ]),
    ]

    item_dict = {'node':organisation_list, 'section':organisation_list, 'resource':resource_list}
    for expected_tuple in expected_list_list:
      param, expected_list = expected_tuple
      expected_l = expected_list[:]
      for expected in expected_l:
        for attribute in [x for x in expected.keys() if x.endswith('_relative_url')]:
          attr_name = attribute.split('_')[0]
          expected[attribute] = item_dict[attr_name][expected[attribute]].getRelativeUrl()
      LOG('Testing getInventoryList with', 0, param)
      self._testGetInventoryList(expected=expected_l, omit_simulation=1, **param)


  def _testGetInventoryList(self, expected, **kw):
    """
      Shared testing method
      expected is a list of dictionaries containing identifying keys and 'inventory'
    """
    simulation = self.getPortal().portal_simulation
    expected = expected[:]
    if len(expected) > 0:
      attribute_list = [x for x in expected[0].keys() if x != 'inventory']
    else:
      attribute_list = []

    LOG('Testing getInventoryList with args :', 0, kw)
    inventory_list = simulation.getInventoryList(**kw)
    for inventory in inventory_list:
      a_attributes = {}
      for attr in attribute_list:
        if not hasattr(inventory, attr):
          LOG('TEST ERROR : Result of getInventoryList has no %s attribute' % attr, 0, '')
          LOG('SQL Query was : ', 0, repr(simulation.getInventoryList(src__=1, **kw)))
          raise RuntimeError
        a_attributes[attr] = getattr(inventory, attr)
      a_inventory = inventory.inventory
      # Build a function to filter on attributes
      def cmpfunction(item):
        for (key, value) in a_attributes.items(): # pylint: disable=cell-var-from-loop
          if item[key] != value:
            return 0
        return 1
      # Look for lines with the same attributes in expected list
      expected_list = []
      for i in range(len(expected)):
        exp = expected[i]
        if cmpfunction(exp):
          expected_list.append(dict(exp))
          expected_list[-1].update({'id':i})
      # Now, look in these lines for one which has the same inventory
      found_list = [x for x in expected_list if x['inventory'] == a_inventory]
      if len(found_list) == 0:
        LOG('TEST ERROR : Found a line with getInventoryList which is not expected.', 0, 'Found line : %s (inventory : %s) ; expected values with these attributes : %s' % (a_attributes, a_inventory, expected_list))
        LOG('SQL Query was : ', 0, repr(simulation.getInventoryList(src__=1, **kw)))
        self.assertNotEqual(len(found_list), 0)
      found = found_list[0]
      LOG('found a line with inventory =', 0, repr(found['inventory']))
      del expected[found['id']]
    # All inventory lines were found. Now check if some expected values remain
    if len(expected) > 0:
      LOG('TEST ERROR : Not all expected values were matched. Remaining =', 0, expected)
      LOG('SQL Query was : ', 0, str(simulation.getInventoryList(src__=1, **kw)))
      self.assertTrue(len(expected), 0)

  def checkVariatedInventory(self, sequence=None, sequence_list=None,
                             variation_category_list=None,
                             quantity=None,**kw):
    """
    """
    simulation = self.getPortal().portal_simulation
    variation_category_list = copy(variation_category_list)
    variation_category_list.sort()
    variation_text = '\n'.join(variation_category_list)
    inventory = simulation.getCurrentInventory(
      resource = sequence.get("resource").getRelativeUrl(),
      section = sequence.get('section').getRelativeUrl(),
      node = sequence.get('node').getRelativeUrl(),
      variation_text = variation_text
      )
    self.assertEqual(inventory, quantity)

  def stepTestInitialVariatedInventory(self, sequence=None, sequence_list=None, **kw):
    """
      Test Inventory Module behavior
    """
    variation_category_list = sequence.get('variation_1')
    quantity = 1
    self.checkVariatedInventory(variation_category_list=variation_category_list,
                                quantity=quantity,sequence=sequence)
    variation_category_list = sequence.get('variation_2')
    quantity = 3
    self.checkVariatedInventory(variation_category_list=variation_category_list,
                                quantity=quantity,sequence=sequence)

  def stepTestInitialVariatedNonDefaultQuantityUnitInventory(self, sequence=None, sequence_list=None, **kw):
    """
      Test Inventory Module behavior
    """
    variation_category_list = sequence.get('variation_1')
    quantity = 100
    self.checkVariatedInventory(variation_category_list=variation_category_list,
                                quantity=quantity,sequence=sequence)
    variation_category_list = sequence.get('variation_2')
    quantity = 300
    self.checkVariatedInventory(variation_category_list=variation_category_list,
                                quantity=quantity,sequence=sequence)

  def stepTestVariatedInventoryAfterInventory(self, sequence=None, sequence_list=None, **kw):
    """
      Test Inventory Module behavior
    """
    variation_category_list = sequence.get('variation_1')
    quantity = 5
    self.checkVariatedInventory(variation_category_list=variation_category_list,
                                quantity=quantity,sequence=sequence)
    variation_category_list = sequence.get('variation_2')
    quantity = 3
    self.checkVariatedInventory(variation_category_list=variation_category_list,
                                quantity=quantity,sequence=sequence)

  def stepTestVariatedInventoryNonDefaultQuantityUnitAfterInventory(self, sequence=None, sequence_list=None, **kw):
    """
      Test Inventory Module behavior
    """
    variation_category_list = sequence.get('variation_1')
    quantity = 5
    self.checkVariatedInventory(variation_category_list=variation_category_list,
                                quantity=quantity,sequence=sequence)
    variation_category_list = sequence.get('variation_2')
    quantity = 300
    self.checkVariatedInventory(variation_category_list=variation_category_list,
                                quantity=quantity,sequence=sequence)

  def stepTestFullVariatedInventory(self, sequence=None, sequence_list=None, **kw):
    """
      Test full inventory with variated resource
    """
    variation_category_list = sequence.get('variation_1')
    # Test first resource
    quantity = 55
    self.checkVariatedInventory(variation_category_list=variation_category_list,
                                quantity=quantity,sequence=sequence)
    variation_category_list = sequence.get('variation_2')
    quantity = 0
    self.checkVariatedInventory(variation_category_list=variation_category_list,
                                quantity=quantity,sequence=sequence)

    # second resource, must be 101
    simulation = self.getPortal().portal_simulation
    inventory = simulation.getCurrentInventory(
      resource = sequence.get("second_resource").getRelativeUrl(),
      section = sequence.get('section').getRelativeUrl(),
      node = sequence.get('node').getRelativeUrl(),
      )
    self.assertEqual(inventory, 101.,
                    'section=%s, node=%s' % (
                    sequence.get('section').getRelativeUrl(),
                    sequence.get('node').getRelativeUrl()))

  def stepTestInventoryModule(self, sequence=None, sequence_list=None, **kw):
    """
      Test Inventory Module behavior
    """
    step = sequence.get('step')
    inventory_list = sequence.get('inventory_list')
    simulation = self.getPortal().portal_simulation
    if step is None:
      step = 0
    expected = [(40.,0), (24.,1), (80.,0)]
    inventory = simulation.getCurrentInventory(
                    section=sequence.get('section').getRelativeUrl(),
                    node=sequence.get('node').getRelativeUrl(),
                    at_date=inventory_list[expected[step][1]].getStartDate()
                )
    self.assertEqual(inventory, expected[step][0],
                    'section=%s, node=%s' % (
                    sequence.get('section').getRelativeUrl(),
                    sequence.get('node').getRelativeUrl()))
    step += 1
    sequence.edit(step=step)

  def stepTestFullInventory(self, sequence=None, sequence_list=None, **kw):
    """
      Test Full inventory behavior
    """
    sequence.get('inventory_list')
    simulation = self.getPortal().portal_simulation

    # First resource, must be zero
    inventory = simulation.getCurrentInventory(
      resource = sequence.get("resource").getRelativeUrl(),
      section = sequence.get('section').getRelativeUrl(),
      node = sequence.get('node').getRelativeUrl(),
      )
    self.assertEqual(inventory, 0.,
                    'section=%s, node=%s' % (
                    sequence.get('section').getRelativeUrl(),
                    sequence.get('node').getRelativeUrl()))
    # second resource, must be 101
    inventory = simulation.getCurrentInventory(
      resource = sequence.get("second_resource").getRelativeUrl(),
      section = sequence.get('section').getRelativeUrl(),
      node = sequence.get('node').getRelativeUrl(),
      )
    self.assertEqual(inventory, 101.,
                    'section=%s, node=%s' % (
                    sequence.get('section').getRelativeUrl(),
                    sequence.get('node').getRelativeUrl()))



  def stepModifyFirstInventory(self, sequence=None, sequence_list=None, **kw):
    """
      Modify the first entered Inventory, to test the quantity change
    """
    inventory = sequence.get('inventory_list')[0]
    inventory_line = inventory['1']
    item_list = sequence.get('item_list')
    aggregate_value_list = [item_list[0],item_list[1], item_list[4]]
    inventory_line.edit(
        aggregate_value_list=aggregate_value_list,
        quantity=sum([x.getQuantity() for x in aggregate_value_list]))


  def stepCreateNotVariatedSecondResource(self,sequence=None,
                                          sequence_list=None,
                                          **kw):
    """
      Create a second resource with no variation
    """
    portal = self.getPortal()
    resource_module = portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent(portal_type=self.resource_portal_type)
    resource.edit(
      title = "NotVariatedSecondResource%s" % resource.getId(),
      industrial_phase_list=["phase1", "phase2"],
      product_line = 'apparel'
    )

    sequence.edit( second_resource = resource )
    resource_list = sequence.get('resource_list',default=[])
    resource_list.append(resource)
    sequence.edit( resource_list = resource_list )

  def stepSetTwoLevelProductLineOnFirstResource(self,
                                                sequence=None,
                                                sequence_list=None,
                                                **kw):
    """ Create a resource which has two level product_line """
    category_tool = self.portal.portal_categories
    pl = category_tool.product_line
    self.createCategory(pl, ['level1', ['level2']])
    product_module = self.portal.product_module
    resource_value = product_module.newContent(title='Resource',
                                               portal_type='Product')
    resource_value.setProductLine('level1/level2')
    sequence.edit(first_resource=resource_value)

  def stepTestFullInventoryWithResourceCategory(self,
                                                sequence=None,
                                                sequence_list=None,
                                                **kw):
    """
     Make sure that we can use resource_category parameter with Full inventory.
    """
    node = sequence.get('node')
    section = sequence.get('section')
    getInventory = self.getSimulationTool().getInventory
    self.assertEqual(10, getInventory(section_uid=section.getUid(),
                                        node_uid=node.getUid(),
                                        resource_category='product_line/level1',
                                        optimisation__=False))
    self.assertEqual(10, getInventory(section_uid=section.getUid(),
                                        node_uid=node.getUid(),
                                        resource_category='product_line/level1',
                                        optimisation__=True))
    self.assertEqual(100, getInventory(section_uid=section.getUid(),
                                        node_uid=node.getUid(),
                                        resource_category='product_line/apparel',
                                        optimisation__=False))
    self.assertEqual(100, getInventory(section_uid=section.getUid(),
                                        node_uid=node.getUid(),
                                        resource_category='product_line/apparel',
                                        optimisation__=True))

  def stepSetUpInventoryIndexingByNodeAndSection(self,
                                                 sequence=None,
                                                 sequence_list=None,
                                                 **kw):
    script_name = 'Inventory_getDefaultInventoryCalculationList'
    if script_name in self.portal.portal_skins.custom:
      return
    createZODBPythonScript(self.portal.portal_skins.custom,
                           'Inventory_getDefaultInventoryCalculationList', '',
    dedent('''
    return ({'inventory_params':{
             'section_uid':context.getDestinationSectionUid(),
             'node_uid':context.getDestinationUid(),
             'group_by_variation':1,
             'group_by_resource':1},
            'list_method':'getMovementList',
            'first_level':({'key':'resource_relative_url',
                            'getter':'getResource',
                            'setter':('appendToCategoryList', 'resource')},
                           {'key':'variation_text',
                            'getter':'getVariationText',
                            'setter':'splitAndExtendToCategoryList'},
                           ),
            "second_level":({'key' : 'sub_variation_text',
                             'getter' : 'getSubVariationText',
                             'setter' : "splitAndExtendToCategoryList"},
                            ),
            },)
    '''))


  def stepSetTwoLevelGroupOnSection(self,
                                    sequence=None,
                                    sequence_list=None,
                                    **kw):
    """ Create a section which has two level group """
    category_tool = self.portal.portal_categories
    self.createCategory(category_tool.group, ['level1', ['level2']])
    organisation_module = self.portal.organisation_module
    section_value = organisation_module.newContent(title='Organisation',
                                                   portal_type='Organisation')
    section_value.setGroup('level1/level2')
    sequence.edit(section=section_value)

  def stepTestFullInventoryWithSectionCategory(self,
                                               sequence=None,
                                               sequence_list=None,
                                               **kw):
    """
     Make sure that we can use section_category parameter with Full inventory.
    """
    node = sequence.get('node')
    getInventory = self.getSimulationTool().getInventory
    self.assertEqual(202, getInventory(node_uid=node.getUid()))
    self.assertEqual(101, getInventory(section_category='group/level1/level2',
                                        node_uid=node.getUid(),
                                        optimisation__=False))
    self.assertEqual(101, getInventory(node_uid=node.getUid(),
                                        section_category='group/level1/level2',
                                        optimisation__=True))

  def stepSetTwoLevelRegionOnNode(self,
                                  sequence=None,
                                  sequence_list=None,
                                  **kw):
    """ Create a node which has two tier region """
    category_tool = self.portal.portal_categories
    self.createCategory(category_tool.region, ['level1', ['level2']])
    organisation_module = self.portal.organisation_module
    node_value = organisation_module.newContent(title='Organisation',
                                                portal_type='Organisation')
    node_value.setRegion('level1/level2')
    sequence.edit(node=node_value)

  def stepTestFullInventoryWithNodeCategory(self,
                                            sequence=None,
                                            sequence_list=None,
                                            **kw):
    """
     Make sure that we can use node_category parameter with Full inventory.
    """
    section = sequence.get('section')
    getInventory = self.getSimulationTool().getInventory
    self.assertEqual(202, getInventory(section_uid=section.getUid()))
    self.assertEqual(101, getInventory(section_uid=section.getUid(),
                                        node_category='region/level1/level2',
                                        optimisation__=False))
    self.assertEqual(101, getInventory(section_uid=section.getUid(),
                                        node_category='region/level1/level2',
                                        optimisation__=True))

  def stepCreateFullInventoryAtTheDate(self, sequence=None,
                                       sequence_list=None, **kw):
    """ Create Full Inventory at the date' """
    inventory_list = sequence.get('inventory_list',[])
    if kw.get('start_date', None) is not None:
      start_date = kw['start_date']
    else:
      start_date = '2013/03/12 00:00:00 GMT+9'
    if kw.get('resource_value', None) is not None:
      resource_value = kw['resource_value']
    else:
      resource_value = sequence.get('resource')
    if kw.get('destination_value', None) is not None:
      destination_value = kw['destination_value']
    else:
      destination_value = sequence.get('node')
    inventory = self.createInventory(sequence=sequence)
    inventory.edit(full_inventory=True,
                   destination_section_value=sequence.get('section'),
                   destination_value=destination_value,
                   start_date=start_date)
    inventory.newContent(
      portal_type = self.inventory_line_portal_type,
      resource_value = resource_value,
      inventory = 100)
    inventory.deliver()
    inventory_list.append(inventory)
    sequence.edit(inventory_list=inventory_list)


  def stepCreateFullInventoryAtTheDate1(self, sequence=None,
                                        sequence_list=None, **kw):
    if getattr(self, 'full_inventory_start_date_1', None) is None:
      raise UnboundLocalError('Please assign self.full_inventory_start_date_1 '
                              'in your test method')
    params = dict(start_date=self.full_inventory_start_date_1)
    if getattr(self, 'full_inventory_resource_1', None) is not None:
      self.assertNotEqual(sequence.get(self.full_inventory_resource_1), None)
      params['resource_value'] = sequence.get(self.full_inventory_resource_1)
    if getattr(self, 'full_inventory_node_1', None) is not None:
      self.assertNotEqual(sequence.get(self.full_inventory_node_1), None)
      params['destination_value'] = sequence.get(self.full_inventory_node_1)
    self.stepCreateFullInventoryAtTheDate(sequence, sequence_list, **params)

  def stepCreateFullInventoryAtTheDate2(self, sequence=None,
                                        sequence_list=None, **kw):
    if getattr(self, 'full_inventory_start_date_2', None) is None:
      raise UnboundLocalError('Please assign self.full_inventory_start_date_2 '
                              'in your test method')
    params = dict(start_date=self.full_inventory_start_date_2)
    if getattr(self, 'full_inventory_resource_2', None) is not None:
      self.assertNotEqual(sequence.get(self.full_inventory_resource_2), None)
      params['resource_value'] = sequence.get(self.full_inventory_resource_2)
    if getattr(self, 'full_inventory_node_2', None) is not None:
      self.assertNotEqual(sequence.get(self.full_inventory_node_2), None)
      params['destination_value'] = sequence.get(self.full_inventory_node_2)
    self.stepCreateFullInventoryAtTheDate(sequence, sequence_list, **params)

  def stepCheckMultipleSectionAndFullInventory(self, sequence=None,
                                               sequence_list=None, **kw):
    """ Check that getInvetory() is surely working in
    MultipleSectionAndFullInventory case """
    section = sequence.get('section')
    other_section  = sequence.get('other_section')
    self._testGetInventory(expected=102, section_uid=section.getUid())
    self._testGetInventory(expected=7, section_uid=other_section.getUid())


  def stepCreatePackingListForMultipleSectionAndFullInventory(
        self, sequence=None, sequence_list=None, **kw):
    """ Create packing lists for MultipleSectionAndFullInventory Test """
    node = sequence.get('node')
    section = sequence.get('section')
    mirror_node = sequence.get('mirror_node')
    mirror_section = sequence.get('mirror_section')
    other_section = sequence.get('other_section')
    resource = sequence.get('resource')
    packing_list_module = self.getPortal().getDefaultModule(
                              portal_type=self.packing_list_portal_type)
    movement_list = [
      dict(start_date='2013/03/10 00:00:00 GMT+9',
           destination_section_value=section, quantity=1),
      dict(start_date='2013/03/13 00:00:00 GMT+9',
           destination_section_value=section, quantity=2),
      dict(start_date='2013/03/11 00:00:00 GMT+9',
           destination_section_value=other_section, quantity=3),
      dict(start_date='2013/03/12 00:00:00 GMT+9',
           destination_section_value=other_section, quantity=4)]
    packing_list_list = []
    for movement in movement_list:
      packing_list = packing_list_module.newContent(
                              portal_type=self.packing_list_portal_type)
      packing_list.edit(specialise=self.business_process,
                        source_section_value=mirror_section,
                        source_value=mirror_node,
                        destination_section_value= \
                          movement['destination_section_value'],
                        destination_value=node,
                        start_date=movement['start_date'],
                        price_currency=self.price_currency)
      self.assertNotEqual(packing_list.getSourceSectionValue(), None)
      self.assertNotEqual(packing_list.getSourceValue(), None)
      self.assertNotEqual(packing_list.getSourceSectionValue(),
                           packing_list.getDestinationSectionValue())

      line = packing_list.newContent(
        portal_type=self.packing_list_line_portal_type)
      line.edit(resource_value=resource, quantity=movement['quantity'])
      packing_list_list.append(packing_list)
    sequence.edit(packing_list_list=packing_list_list)

  def stepDeliverAllPackingList(self, sequence=None,
                                      sequence_list=None, **kw):
    """Deliver all the packing lists that are created by test sequences"""
    packing_list_list = sequence.get('packing_list_list')
    for packing_list in packing_list_list:
      for action in ('confirm', 'setReady', 'start', 'stop', 'deliver'):
        workflow_action = getattr(packing_list, action)
        workflow_action()
        self.tic()

  def stepCreatePackingListAtTheDate1(self,
                                     sequence=None,
                                     sequence_list=None,
                                     **kw):
    """ Create Packing List with self.start_date_1"""
    if getattr(self, 'start_date_1', None) is None:
      raise UnboundLocalError('Please Assign self.start_date_1 '
                              'in your test method')
    self.stepCreatePackingListForModule(sequence=sequence,
                                        sequence_list=sequence_list,
                                        start_date=self.start_date_1)

  def stepCreatePackingListAtTheDate2(self,
                                     sequence=None,
                                     sequence_list=None,
                                     **kw):
    """ Create Packing List with self.start_date_2"""
    if getattr(self, 'start_date_2', None) is None:
      raise UnboundLocalError('Please Assign self.start_date_2 '
                              'in your test method')
    self.stepCreatePackingListForModule(sequence=sequence,
                                        sequence_list=sequence_list,
                                        start_date=self.start_date_2)

  def stepCreatePackingListLineWithResource1(self,
                                             sequence=None,
                                             sequence_list=None,
                                             **kw):
    """ Create Packing List Line with self.resrouce_1"""
    if getattr(self, 'resource_1', None) is None:
      raise UnboundLocalError('Please Assign self.resource_1 '
                              'in your test method')
    resource_value = sequence.get(self.resource_1)
    self.assertNotEqual(resource_value, None)
    self.stepCreatePackingListLine(sequence=sequence,
                                   sequence_list=sequence_list,
                                   resource_value=resource_value)

  def stepCreatePackingListLineWithResource2(self,
                                             sequence=None,
                                             sequence_list=None,
                                             **kw):
    """ Create Packing List Line with self.resrouce_2"""
    if getattr(self, 'resource_2', None) is None:
      raise UnboundLocalError('Please Assign self.resource_2 '
                              'in your test method')
    resource_value = sequence.get(self.resource_2)
    self.assertNotEqual(resource_value, None)
    self.stepCreatePackingListLine(sequence=sequence,
                                   sequence_list=sequence_list,
                                   resource_value=resource_value)


  def _testGetMovementHistoryList(self, expected_history=None, **kw):
    """ Helper method to check getMovementHistoryList """
    simulation = self.getPortal().portal_simulation
    LOG('Testing movement history with args :', 0, kw)
    result = simulation.getMovementHistoryList(**kw)
    self.assertTrue(len(result) > 0)
    # Note: Now only checking total_quantity but can be checked more
    actual_history = [{'total_quantity':x.total_quantity} for x in result]
    try:
      self.assertEqual(len(expected_history), len(actual_history))
      for expected, actual in zip(expected_history, actual_history):
        shared_keys = set(expected) & set(actual)
        self.assertEqual(len(shared_keys), len(expected))
        shared_item = set(expected.items()) & set(actual.items())
        self.assertEqual(len(shared_item), len(expected))
    except AssertionError:
      msg = 'History differs between expected:\n%s\nand real:\n%s'\
             % (repr(expected_history), repr(actual_history))
      LOG('TestInventory._testGetMovementHistoryList', 0, msg)
      LOG('SQL Query was : ', 0,
         str(simulation.getMovementHistoryList(src__=1, **kw)))
      raise AssertionError(msg)

  def stepCheckFullInventoryAddOldMovement(self,
                                           sequence=None,
                                           sequence_list=None,
                                           **kw):
    """ Check Create Full Inventory Then Add Old Movement use case """
    section = sequence.get('section')
    node  = sequence.get('node')
    self._testGetInventory(expected=100,
                           section_uid=section.getUid(),
                           node_uid=node.getUid())
    self._testGetMovementHistoryList(expected_history=[{'total_quantity':-100},
                                                       {'total_quantity':100},
                                                       {'total_quantity':100},],
                              section_uid=section.getUid(),
                              node_uid=node.getUid())

  def stepCreateInventoryAtTheDate(self, sequence=None,
                                   sequence_list=None, **kw):
    """ Create Inventory at the date with some flexible variables """
    inventory_quantity = kw['inventory'] if 'inventory' in kw else 100
    start_date = kw['start_date'] if 'start_date' in kw else None
    if 'resource_value' in kw:
      resource_value = kw['resource_value']
    else:
      resource_value = sequence.get('second_resource')
    inventory = self.createInventory(sequence=sequence,
                                     full=False, start_date=start_date)
    inventory_list = sequence.get('inventory_list',[])
    inventory.newContent(
      portal_type=self.inventory_line_portal_type,
      resource_value=resource_value,
      inventory=inventory_quantity)
    inventory.deliver()
    inventory_list.append(inventory)
    sequence.edit(inventory_list=inventory_list)

  def stepCreateInventoryAtTheDate1(self, sequence=None,
                                    sequence_list=None, **kw):
    """ Create Inventory at the date:'self.inventory_start_date_1'
     with some flexible variables """
    if getattr(self, 'inventory_start_date_1', None) is None:
      raise UnboundLocalError('Please assign self.inventory_start_date_1 '
                              'in your test method')
    params = dict(start_date=self.inventory_start_date_1)
    if getattr(self, 'inventory_1', None) is not None:
      params['inventory'] = self.inventory_1
    if getattr(self, 'inventory_resource_1', None) is not None:
      params['resource_value'] = sequence.get(self.inventory_resource_1)

    self.stepCreateInventoryAtTheDate(sequence, sequence_list, **params)

  def stepCreateInventoryAtTheDate2(self, sequence=None,
                                    sequence_list=None, **kw):
    """ Create Inventory at the date:'self.inventory_start_date_2'
     with some flexible variables """
    if getattr(self, 'inventory_start_date_2', None) is None:
      raise UnboundLocalError('Please assign self.inventory_start_date_2 '
                              'in your test method')
    params = dict(start_date=self.inventory_start_date_2)
    if getattr(self, 'inventory_2', None) is not None:
      params['inventory'] = self.inventory_2
    if getattr(self, 'inventory_resource_2', None) is not None:
      params['resource_value'] = sequence.get(self.inventory_resource_2)
    self.stepCreateInventoryAtTheDate(sequence, sequence_list, **params)

  def stepCheckUseBothFullAndPartialInventory(
        self, sequence=None, sequence_list=None, **kw):
    """ Check a case Using both Full and Normal Inventory"""
    resource_value = sequence.get('second_resource')
    node_value = sequence.get('node')
    section_value = sequence.get('section')
    self._testGetInventory(expected=3,
                           section_uid=section_value.getUid(),
                           node_uid=node_value.getUid(),
                           resource_uid=resource_value.getUid())
    self._testGetInventory(expected=3,
                           resource_uid=resource_value.getUid(),
                           optimisation__=False)

  def stepTestFullInventoryMultipleNodeAndResource(
        self, sequence=None, sequence_list=None, **kw):
    """ Test Full inventory with multiple nodes and resources"""
    resource_value = sequence.get('resource')
    second_resource_value = sequence.get('second_resource')
    node_value = sequence.get('node')
    other_node_value = sequence.get('other_node')
    section_value = sequence.get('section')
    self._testGetInventory(expected=100,
                           section_uid=section_value.getUid(),
                           node_uid=node_value.getUid(),
                           resource_uid=resource_value.getUid())
    self._testGetInventory(expected=100,
                           section_uid=section_value.getUid(),
                           node_uid=node_value.getUid(),
                           resource_uid=second_resource_value.getUid())
    self._testGetInventory(expected=100,
                           section_uid=section_value.getUid(),
                           node_uid=other_node_value.getUid(),
                           resource_uid=second_resource_value.getUid())
    self._testGetInventory(expected=0,
                           section_uid=section_value.getUid(),
                           node_uid=other_node_value.getUid(),
                           resource_uid=resource_value.getUid())

  def stepTestFullInventoryCollideWithEachOther(
        self, sequence=None, sequence_list=None, **kw):
    resource_value = sequence.get('resource')
    node_value = sequence.get('node')
    section_value = sequence.get('section')
    self._testGetInventory(expected=200,
                           section_uid=section_value.getUid(),
                           node_uid=node_value.getUid(),
                           resource_uid=resource_value.getUid())

  def stepTestInventoryCollisionByMovements(
        self, sequence=None, sequence_list=None, **kw):
    resource_value = sequence.get('resource')
    node_value = sequence.get('node')
    section_value = sequence.get('section')
    self._testGetInventory(expected=300,
                           section_uid=section_value.getUid(),
                           node_uid=node_value.getUid(),
                           resource_uid=resource_value.getUid())


  def stepTestInventoryCollisionByInventory(
        self, sequence=None, sequence_list=None, **kw):
    resource_value = sequence.get('resource')
    node_value = sequence.get('node')
    section_value = sequence.get('section')
    self._testGetInventory(expected=300,
                           section_uid=section_value.getUid(),
                           node_uid=node_value.getUid(),
                           resource_uid=resource_value.getUid())

  def stepCreateTwoResourceFullInventory(self,
                                         sequence=None,
                                         sequence_list=None,
                                         **kw):
    """ Create a full Inventory which includes two inventory lines """
    inventory = self.createInventory(sequence=sequence)
    inventory_list = sequence.get('inventory_list',[])
    inventory.edit(full_inventory=True)
    inventory.newContent(
      portal_type = self.inventory_line_portal_type,
      resource_value = sequence.get("first_resource"),
      inventory = 10)
    inventory.newContent(
      portal_type = self.inventory_line_portal_type,
      resource_value = sequence.get("second_resource"),
      inventory = 100)
    inventory.deliver()
    inventory_list.append(inventory)
    sequence.edit(inventory_list=inventory_list)

  def stepCreateTwoResourceFullInventoryAtTheDate(self, sequence=None,
                                                  sequence_list=None, **kw):
    """ Create Full Inventory at the date' """
    inventory_list = sequence.get('inventory_list',[])
    if kw.get('start_date', None) is not None:
      start_date = kw['start_date']
    else:
      start_date = '2013/03/12 00:00:00 GMT+9'
    if kw.get('inventory1', None) is not None:
      inventory1 = kw['inventory1']
    else:
      inventory1 = 10
    if kw.get('inventory2', None) is not None:
      inventory2 = kw['inventory2']
    else:
      inventory2 = 100

    inventory = self.createInventory(sequence=sequence)
    inventory_list = sequence.get('inventory_list',[])
    inventory.edit(full_inventory=True,
                   start_date=start_date)
    inventory.newContent(
      portal_type = self.inventory_line_portal_type,
      resource_value = sequence.get("resource"),
      inventory = inventory1)
    inventory.newContent(
      portal_type = self.inventory_line_portal_type,
      resource_value = sequence.get("second_resource"),
      inventory = inventory2)
    inventory.deliver()
    inventory_list.append(inventory)
    sequence.edit(inventory_list=inventory_list)

  def stepCreateTwoResourceFullInventoryAtTheDate1(self, sequence=None,
                                                   sequence_list=None, **kw):
    params = dict(start_date=self.two_resource_full_inventory1_start_date,
                  inventory1=self.two_resource_full_inventory1_inventory_1,
                  inventory2=self.two_resource_full_inventory1_inventory_2)
    self.stepCreateTwoResourceFullInventoryAtTheDate(sequence, sequence_list,
                                                     **params)

  def stepCreateTwoResourceFullInventoryAtTheDate2(self, sequence=None,
                                                   sequence_list=None, **kw):
    params = dict(start_date=self.two_resource_full_inventory2_start_date,
                  inventory1=self.two_resource_full_inventory2_inventory_1,
                  inventory2=self.two_resource_full_inventory2_inventory_2)
    self.stepCreateTwoResourceFullInventoryAtTheDate(sequence, sequence_list,
                                                     **params)

  def stepCheckFullInventoryUpdateWithValidDateOrder(
        self, sequence=None, sequence_list=None, **kw):
    resource_value = sequence.get('resource')
    second_resource_value = sequence.get('second_resource')
    node_value = sequence.get('node')
    section_value = sequence.get('section')
    self._testGetInventory(expected=100,
                           section_uid=section_value.getUid(),
                           node_uid=node_value.getUid(),
                           resource_uid=resource_value.getUid())
    self._testGetInventory(expected=0,
                           section_uid=section_value.getUid(),
                           node_uid=node_value.getUid(),
                           resource_uid=second_resource_value.getUid())

  def stepDoubleStockValue(
        self, sequence=None, sequence_list=None, **kw):
    """
      Make stock table double
    """
    self.getPortalObject().erp5_sql_transactionless_connection.manage_test(
      "BEGIN\0"
      "UPDATE stock SET quantity=quantity*2 \0"
      "COMMIT")
    self.commit()

  def stepHalfStockValue(
        self, sequence=None, sequence_list=None, **kw):
    """
      Make stock table half
    """
    self.getPortalObject().erp5_sql_transactionless_connection.manage_test(
      "BEGIN\0"
      "UPDATE stock SET quantity=quantity/2 \0"
      "COMMIT")
    self.commit()


  def stepClearInventoryCache(
        self, sequence=None, sequence_list=None, **kw):
    """
      Explicitly Clear inventory cache.
    """
    self.getPortalObject().erp5_sql_transactionless_connection.manage_test(
      "BEGIN\0"
      "DELETE FROM inventory_cache \0"
      "COMMIT")
    self.commit()


  def stepCheckCorruptedCacheHasFixedByReindex(
        self, sequence=None, sequence_list=None, **kw):
    """
      Make sure that corrupted caches are ignored when inventory document
      are reindexing.
    """
    resource_value = sequence.get('resource')
    node_value = sequence.get('node')
    section_value = sequence.get('section')
    self._testGetInventory(expected=100,
                           optimise=True,
                           to_date=DateTime(self.full_inventory_start_date_1),
                           section_uid=section_value.getUid(),
                           node_uid=node_value.getUid(),
                           resource_uid=resource_value.getUid())
    self._testGetInventory(expected=100,
                           optimisation__=False,
                           to_date=DateTime(self.full_inventory_start_date_1),
                           section_uid=section_value.getUid(),
                           node_uid=node_value.getUid(),
                           resource_uid=resource_value.getUid())


  def stepStoreWrongCache(self, sequence=None, sequence_list=None, **kw):
    """
      Cache a corrupted stock data.
    """
    node_value = sequence.get('node')
    to_date=DateTime(self.two_resource_full_inventory2_start_date)
    self.getPortalObject().portal_simulation.getCurrentInventoryList(
      to_date=to_date,
      section=section_value.getRelativeUrl(), # pylint: disable=undefined-variable
      node=node_value.getRelativeUrl(),
      group_by_variation=1,
      group_by_sub_variation=1,
      group_by_resource=1)

  def stepCheckGetInveotoryGoesToCache(
        self, sequence=None, sequence_list=None, **kw):
    """
      Get inventory then store the inventory_cache record
      thanks to the at_date parameter
    """
    resource_value = sequence.get('resource')
    second_resource_value = sequence.get('second_resource')
    node_value = sequence.get('node')
    section_value = sequence.get('section')
    at_date = DateTime('2013/06/11 00:00:00 GMT+9')
    self._testGetInventory(
      expected=15,
      section_uid=section_value.getUid(),
      node_uid=node_value.getUid(),
      resource_uid=resource_value.getUid(),
      at_date=at_date)
    self._testGetInventory(
      expected=20,
      section_uid=section_value.getUid(),
      node_uid=node_value.getUid(),
      resource_uid=second_resource_value.getUid(),
      at_date=at_date)

  def stepCheckInventoryCacheIsClearedAfterAddingInventory(
        self, sequence=None, sequence_list=None, **kw):
    """
      Check that older invetory_cache is cleared.
    """
    resource_value = sequence.get('resource')
    second_resource_value = sequence.get('second_resource')
    node_value = sequence.get('node')
    section_value = sequence.get('section')
    at_date = DateTime('2013/06/11 02:00:00 GMT+9')
    self._testGetInventory(
      expected=30,
      section_uid=section_value.getUid(),
      node_uid=node_value.getUid(),
      resource_uid=resource_value.getUid(),
      at_date=at_date)
    self._testGetInventory(
      expected=50,
      section_uid=section_value.getUid(),
      node_uid=node_value.getUid(),
      resource_uid=second_resource_value.getUid(),
      at_date=at_date)

  def test_01_getInventory(self, quiet=0, run=run_all_test):
    """
      Test the getInventory methods
    """
    if not run: return
    sequence_list = SequenceList()

    get_inventory_test_sequence= 'stepTestInventoryListBrainGetQuantity \
                                   stepTestGetInventoryOnNode \
                                   stepTestGetInventoryOnVariationCategory \
                                   stepTestGetInventoryOnPayment \
                                   stepTestGetInventoryOnSection \
                                   stepTestGetInventoryOnMirrorSection \
                                   stepTestGetInventoryOnResource \
                                   stepTestGetInventoryWithOmitInput \
                                   stepTestGetInventoryWithOmitOutput \
                                   stepTestGetInventoryOnSimulationState \
                                   stepTestGetInventoryOnSectionCategory \
                                   stepTestGetInventoryOnPaymentCategory \
                                   stepTestGetInventoryOnNodeCategory \
                                   stepTestGetInventoryOnMirrorSectionCategory \
                                   stepTestGetInventoryOnResourceCategory \
                                   stepTestGetInventoryOnVariationText \
                                   '
                                   #TestGetInventoryWithSelectionReport \
    get_inventory_test_sequence += 'stepTestGetInventoryListOnSection \
                                   stepTestGetInventoryListOnNode \
                                   stepTestGetInventoryListWithOmitInput \
                                   stepTestGetInventoryListWithOmitOutput \
                                   stepTestGetInventoryListWithGroupBy \
                                  '

    sequence_string = 'stepCreateOrganisationList \
                       stepCreateOrder \
                       stepCreateVariatedResourceList \
                       stepCreatePackingListList \
                       stepTic \
                       stepCreateTestingCategories \
                       stepTic \
                       ' + get_inventory_test_sequence
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)


  def test_02_InventoryModule(self, quiet=0, run=run_all_test):
    """
      Test the InventoryModule behavior
    """
    if not run: return
    sequence_list = SequenceList()

    sequence_string = 'stepCreateOrganisationsForModule \
                       stepCreateVariatedResource \
                       stepCreateItemList \
                       stepCreatePackingListForModule \
                       stepTic \
                       stepCreatePackingListLine \
                       stepTic \
                       stepDeliverPackingList \
                       stepTic \
                       stepCreateAggregatingInventory \
                       stepTic \
                       stepTestInventoryModule \
                       stepCreateSingleInventory \
                       stepTic \
                       stepTestInventoryModule \
                       stepModifyFirstInventory \
                       stepTic \
                       stepTestInventoryModule \
                       '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_03_InventoryModuleWithVariation(self, quiet=0, run=run_all_test):
    """
      Test the InventoryModule behavior
    """
    if not run: return
    sequence_list = SequenceList()

    sequence_string = 'stepCreateOrganisationsForModule \
                       stepCreateVariatedResource \
                       stepTic \
                       stepCreatePackingListForModule \
                       stepTic \
                       stepCreateVariatedPackingListLine \
                       stepTic \
                       stepDeliverPackingList \
                       stepTic \
                       stepTestInitialVariatedInventory \
                       stepCreateSingleVariatedInventory \
                       stepTic \
                       stepTestVariatedInventoryAfterInventory \
                       '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_04_InventoryModuleWithVariationAndMultiQuantityUnit(self, quiet=0, run=run_all_test):
    """
      Test InventoryModule behavior with product which has
      variation and multiple quantity units.
    """
    if not run: return
    sequence_list = SequenceList()

    sequence_string = 'stepCreateOrganisationsForModule \
                       stepCreateVariatedMultipleQuantityUnitResource \
                       stepTic \
                       stepCreatePackingListForModule \
                       stepTic \
                       stepCreateVariatedNonDefaultQuantityUnitPackingListLine \
                       stepTic \
                       stepDeliverPackingList \
                       stepTic \
                       stepTestInitialVariatedNonDefaultQuantityUnitInventory \
                       stepCreateSingleVariatedInventory \
                       stepTic \
                       stepTestVariatedInventoryNonDefaultQuantityUnitAfterInventory \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_05_CancelInventoryAfterDelivered(self, quiet=0, run=run_all_test):
    """
      Make sure that changing workflow state after delivered changes
      records in stock table.
    """
    inventory_workflow = self.portal.portal_workflow.inventory_workflow
    delivered_state = inventory_workflow.getStateValueByReference('delivered')
    delivered_state.setDestinationValueSet(
      delivered_state.getDestinationValueList()
      + [inventory_workflow.getTransitionValueByReference('cancel')]
    )

    organisation = self.portal.organisation_module.newContent(portal_type='Organisation')
    product = self.portal.product_module.newContent(portal_type='Product')
    inventory = self.portal.inventory_module.newContent(portal_type='Inventory')
    inventory.edit(destination_value=organisation,
                   stop_date=DateTime('2012/09/12 00:00:00 GMT+9'))
    line = inventory.newContent(portal_type='Inventory Line')
    line.setResourceValue(product)
    line.setQuantity(100)

    self.tic()

    self.assertEqual(
      self.portal.portal_simulation.getCurrentInventory(
        node_uid=organisation.getUid(),
        resource_uid=product.getUid()),
      0)

    inventory.deliver()
    self.tic()

    self.assertEqual(
      self.portal.portal_simulation.getCurrentInventory(
        node_uid=organisation.getUid(),
        resource_uid=product.getUid()),
      100)

    inventory.cancel()
    self.tic()

    self.assertEqual(
      self.portal.portal_simulation.getCurrentInventory(
        node_uid=organisation.getUid(),
        resource_uid=product.getUid()),
      0)

  def test_06_FullInventory(self, quiet=0, run=run_all_test):
    """
      Test the full inventory behavior
    """
    if not run: return
    sequence_list = SequenceList()

    sequence_string = 'stepCreateOrganisationsForModule \
                       stepCreateNotVariatedResource \
                       stepCreateNotVariatedSecondResource \
                       stepCreateItemList \
                       stepCreatePackingListForModule \
                       stepTic \
                       stepCreatePackingListLine \
                       stepTic \
                       stepDeliverPackingList \
                       stepTic \
                       stepCreateFullInventory \
                       stepTic \
                       stepTestFullInventory \
                       '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_07_FullVariatedInventory(self, quiet=0, run=run_all_test):
    """
      Test the full inventory behavior with variated resource
    """
    if not run: return
    sequence_list = SequenceList()

    sequence_string = 'stepCreateOrganisationsForModule \
                       stepCreateVariatedResource \
                       stepCreateNotVariatedSecondResource \
                       stepCreateItemList \
                       stepCreatePackingListForModule \
                       stepTic \
                       stepCreateVariatedPackingListLine \
                       stepTic \
                       stepDeliverPackingList \
                       stepTic \
                       stepCreateFullVariatedInventory \
                       stepTic \
                       stepTestFullVariatedInventory \
                       '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_08_PartialInventoryMultipleResource(self, quiet=0, run=run_all_test):
    """
      Test behaviour of partial inventory with multiple resource
      defining inventory of resource B must not modify inventory of resource A
    """
    if not run: return
    sequence_list = SequenceList()

    sequence_string = 'stepCreateOrganisationsForModule \
                       stepCreateNotVariatedResource \
                       stepCreateNotVariatedSecondResource \
                       stepCreateItemList \
                       stepCreatePackingListForModule \
                       stepTic \
                       stepCreatePackingListLine \
                       stepTic \
                       stepDeliverPackingList \
                       stepTic \
                       stepCreatePartialInventoryMultipleResource \
                       stepTic \
                       stepTestPartialInventoryMultipleResource \
                       '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_09_FullInventoryWithResourceCategory(self, quiet=0, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()

    sequence_string = 'CreateOrganisationsForModule \
                       SetTwoLevelProductLineOnFirstResource \
                       CreateNotVariatedSecondResource \
                       Tic \
                       CreateTwoResourceFullInventory \
                       Tic \
                       TestFullInventoryWithResourceCategory \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_09_FullInventoryWithSectionCategory(self, quiet=0, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()
    sequence_string = 'CreateOrganisationsForModule \
                       SetUpInventoryIndexingByNodeAndSection \
                       CreateNotVariatedSecondResource \
                       Tic \
                       CreateFullInventory \
                       Tic \
                       SetTwoLevelGroupOnSection \
                       Tic \
                       CreateFullInventory \
                       Tic \
                       TestFullInventoryWithSectionCategory \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_09_FullInventoryWithNodeCategory(self, quiet=0, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()
    sequence_string = 'CreateOrganisationsForModule \
                       SetUpInventoryIndexingByNodeAndSection \
                       CreateNotVariatedSecondResource \
                       Tic \
                       CreateFullInventory \
                       Tic \
                       SetTwoLevelRegionOnNode \
                       Tic \
                       CreateFullInventory \
                       Tic \
                       TestFullInventoryWithNodeCategory \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_10_MultipleSectionAndFullInventory(self, quiet=0, run=run_all_test):
    """Make sure that getInventory works in the situation which
    two sections use the same node and one section has full inventory for
    the node.
    For Example:
    movement: 2013/03/10, section=A, node=C, quantity=1
    movement: 2013/03/13, section=A, node=C, quantity=2
    movement: 2013/03/11, section=B, node=C, quantity=3
    movement: 2013/03/12, section=B, node=C, quantity=4

    full inventory: 2013/03/12, section=A, node=C, quantity=100

    getInventory(section_A_uid) should return 102 (not 103)
    getInventory(section_B_uid) should return 7 (not 100)
    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = 'CreateOrganisationsForModule \
                       SetUpInventoryIndexingByNodeAndSection \
                       CreateNotVariatedResource \
                       Tic \
                       CreatePackingListForMultipleSectionAndFullInventory \
                       Tic \
                       DeliverAllPackingList \
                       Tic \
                       CreateFullInventoryAtTheDate \
                       Tic \
                       CheckMultipleSectionAndFullInventory \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  # Note: This inventory reindex function is not implemented yet
  @expectedFailure
  def test_11_FullInventoryAddOldMovement(self, quiet=0, run=run_all_test):
    """
    Make sure the following case:

    1) add movement 2013/02/10, quantity=100
    2) full inventory: 2013/03/15, quantity=100

    [test]
    getInventory() should return 100
    getMovementHistory() should return 100 ([100])

    3) add movement: 2013/02/01, quantity=100

    [test]
    getInventory() should return 100
    getMovementHistory() should return 100 ([-100, 100, 100])
    """
    if not run: return

    self.full_inventory_start_date_1 = '2013/03/15 00:00:00 GMT+9'
    self.start_date_1 = '2013/02/10 00:00:00 GMT+9'
    self.start_date_2 = '2013/02/01 00:00:00 GMT+9'
    sequence_list = SequenceList()
    sequence_string = 'CreateOrganisationsForModule \
                       CreateNotVariatedResource \
                       Tic \
                       CreatePackingListAtTheDate1 \
                       CreatePackingListLine \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CreateFullInventoryAtTheDate1 \
                       Tic \
                       CreatePackingListAtTheDate2 \
                       CreatePackingListLine \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CheckFullInventoryAddOldMovement \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)


  def test_12_UseBothFullAndPartialInventory(self, quiet=0, run=run_all_test):
    """
    Make sure a case Using both Full and Partial Inventories:

    The case is:
    1) inventory: 2013/01/10, section=A, node=B, resource=X, quantity=3
    2) full inventory: 2013/02/21,section=A, node=B, resource=Y, quantity=100
       (there is only *Y*. No X.)
    3) inventory: 2013/03/10,section=A, node=B, resource=X, quantity=3

    [test]
    getInventory(resource=X) should return 3
    getInventory(resource=X, optimisation__=False) should return 3
    """
    if not run: return

    self.inventory_start_date_1 = '2013/01/10 00:00:00 GMT+9'
    self.full_inventory_start_date_1 = '2013/01/10 00:00:00 GMT+9'
    self.inventory_start_date_2 = '2013/03/10 00:00:00 GMT+9'
    self.full_inventory_resource_1 = 'resource'
    self.inventory_resource_1 = self.inventory_resource_2 = 'second_resource'
    self.inventory_1 = 3
    self.inventory_2 = 3
    sequence_list = SequenceList()
    sequence_string = 'CreateOrganisationsForModule \
                       CreateNotVariatedResource \
                       CreateNotVariatedSecondResource \
                       Tic \
                       CreateInventoryAtTheDate1 \
                       Tic \
                       CreateFullInventoryAtTheDate1 \
                       Tic \
                       CreateInventoryAtTheDate2 \
                       Tic \
                       CheckUseBothFullAndPartialInventory \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)


  def test_13_FullInventoryMultipleNodeAndResource(
        self, quiet=0, run=run_all_test):
    """
     Test a case that is using full inventory with multiple nodes and resources.

     The case:
     1) movement: section=A,node=B,resource=X,quantity=100
     2) movement: section=A,node=B,resource=Y,quantity=100
     3) full inventory: section=A,node=C,resource=Y,quantity=100

     [Test]
     getInventory(section=A, node=B, resource=X) should return 100
     getInventory(section=A, node=B, resource=Y) should return 100
     getInventory(section=A, node=C, resource=Y) should return 100
     getInventory(section=A, node=C, resource=X) should return 0
    """
    if not run: return

    self.start_date_1 = '2013/03/10 00:00:00 GMT+9'
    self.resource_1 = 'resource'
    self.start_date_2 = '2013/03/12 00:00:00 GMT+9'
    self.resource_2 = 'second_resource'
    self.full_inventory_start_date_1 = '2013/03/20 00:00:00 GMT+9'
    self.full_inventory_resource_1 = 'second_resource'
    self.full_inventory_node_1 = 'other_node'
    sequence_list = SequenceList()
    sequence_string = 'CreateOrganisationsForModule \
                       SetUpInventoryIndexingByNodeAndSection \
                       CreateNotVariatedResource \
                       CreateNotVariatedSecondResource \
                       Tic \
                       CreatePackingListAtTheDate1 \
                       CreatePackingListLineWithResource1 \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CreatePackingListAtTheDate2 \
                       CreatePackingListLineWithResource2 \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CreateFullInventoryAtTheDate1 \
                       Tic \
                       TestFullInventoryMultipleNodeAndResource \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)


  def test_14_FullInventoryCollision(self, quiet=0, run=run_all_test):
    """
     Make sure a case when Full Inventory collide with other documents.

     The cases are:

     full inventory: 2013/03/20 00:00:00, section=A, node=B, quantity=100
     full inventory: 2013/03/20 00:00:00, section=A, node=B, quantity=100

     [Test]
     getInventory(section=A, node=B) should return 200 (not 100)

     movement: 2013/03/20 00:00:00, section=A, node=B, quantity=10
     movement: 2013/03/20 00:00:00, section=A, node=B, quantity=20
     full inventory: 2013/03/20 00:00:00, section=A, node=B, quantity=200

     [Test]
     getInventory(section=A, node=B) should return 230 (not 200)

     Full inventory acts as if it is created at FIRST among the SETS of the
     documents that are created at THE time.

     This is the specification of full inventory, the details are as follows.


     The specification when Full Inventory collide with others
     =========================================================

     case A [common usage]
     ---------------------

     1| packing list   | 2013/03/20 00:00:00 | 100
     2| packing list   | 2013/03/20 00:00:00 | 100
     3| full inventory | 2013/03/20 00:00:01 | 100 # The time is 00:00:01

     stock:
     1| movement | 2013/03/20 00:00:00 | 100
     2| movement | 2013/03/20 00:00:00 | 100
     3| movement | 2013/03/20 00:00:01 | -100

     getInventory() should return 100

     This full inventory does not collide with others, it is a normal usage of
     full inventory.

     case B [less common usage]
     --------------------------

     1| full inventory | 2013/03/20 00:00:01 100
     2| packing list   | 2013/03/20 00:00:00 100
     3| packing list   | 2013/03/20 00:00:00 100

     stock:
     1| movement | 2013/03/20 00:00:01 | 100  # The time is 00:00:01 !
     2| movement | 2013/03/20 00:00:00 | 100
     3| movement | 2013/03/20 00:00:00 | 100

     getInventory() should return 100 (or should not be in this state)

     This behavior is OK in some business. Full inventory is created AS at last
     even if the creation_date is at first.
     Or, if you do not want to fall in this situation, you can reject such a
     packing list inputs with a proper Constraint.

     case C [collision by movements]
     -------------------------------

     Input documents:
     1| full inventory | 2013/03/20 00:00:00 | 100
     2| packing list   | 2013/03/20 00:00:00 | 100
     3| packing list   | 2013/03/20 00:00:00 | 100

     stock:
     1| movement | 2013/03/20 00:00:00 | 100
     2| movement | 2013/03/20 00:00:00 | 100
     3| movement | 2013/03/20 00:00:00 | 100

     getInventory() should return 300

     This behavior is probably natural, at the beginning of a day, someone
     create a full inventory, then users input daily movements.
     In such case, users' inputs should be respected.

     case D [collision by full inventory]
     ------------------------------------

     Input documents:
     1| packing list   | 2013/03/20 00:00:00 | 100
     2| packing list   | 2013/03/20 00:00:00 | 100
     3| full inventory | 2013/03/20 00:00:00 | 100

     stock:
     1| movement |  2013/03/20 00:00:00 | 100
     2| movement |  2013/03/20 00:00:00 | 100
     3| movement |  2013/03/20 00:00:00 | 100

     getInventory() returns 300? (or should not be in this state)

     This behavior probably sounds weird because even if the full inventory
     created at last within the same date, it does not reset stocks.
     In this case, proper constrains should reject the SAMEDATE-SAMETIME full
     inventory inputs.

     case E [full inventories collide with each other]
     -----------------------------------------

     Input documents:
     1|  full inventory | 2013/03/20 00:00:00 | 100
     1|  full inventory | 2013/03/20 00:00:00 | 100

     stock:
     1| movement |  2013/03/20 00:00:00 | 100
     2| movement |  2013/03/20 00:00:00 | 100

     getInventory() returns 200??

     This must be an unnatural behavior, in reality, production environments
     must not fall into this state, because both two full inventory argue that
     "I am the full inventory" in the same time. In such case, which should be
     the TRUE full inventory? How can you decide it? We can not answer it.

     In other words, this behavior is UNDEFINED, like x/0 in arithmetics.
     Thus appropriate constraints MUST reject those full inventory inputs.
    """
    if not run: return

    # case A and B are tested in other tests

    # case C [collision by movements]
    self.full_inventory_start_date_1 = '2013/03/20 00:00:00 GMT+9'
    self.full_inventory_resource_1 = 'resource'
    self.start_date_1 = '2013/03/20 00:00:00 GMT+9'
    self.resource_1 = 'resource'
    sequence_list = SequenceList()
    sequence_string = 'CreateOrganisationsForModule \
                       SetUpInventoryIndexingByNodeAndSection \
                       CreateNotVariatedResource \
                       Tic \
                       CreateFullInventoryAtTheDate1 \
                       Tic \
                       CreatePackingListAtTheDate1 \
                       CreatePackingListLineWithResource1 \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CreatePackingListAtTheDate1 \
                       CreatePackingListLineWithResource1 \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       TestInventoryCollisionByMovements \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

    # case D [collision by full inventory]
    self.start_date_1 = '2013/03/20 00:00:00 GMT+9'
    self.resource_1 = 'resource'
    self.full_inventory_start_date_1 = '2013/03/20 00:00:00 GMT+9'
    self.full_inventory_resource_1 = 'resource'
    sequence_list = SequenceList()
    sequence_string = 'CreateOrganisationsForModule \
                       SetUpInventoryIndexingByNodeAndSection \
                       CreateNotVariatedResource \
                       Tic \
                       CreatePackingListAtTheDate1 \
                       CreatePackingListLineWithResource1 \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CreatePackingListAtTheDate1 \
                       CreatePackingListLineWithResource1 \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CreateFullInventoryAtTheDate1 \
                       Tic \
                       TestInventoryCollisionByInventory \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

    # case E [full inventories collide with each other]
    self.full_inventory_start_date_1 = '2013/03/20 00:00:00 GMT+9'
    self.full_inventory_resource_1 = 'resource'
    self.full_inventory_start_date_2 = '2013/03/20 00:00:00 GMT+9'
    self.full_inventory_resource_2 = 'resource'
    sequence_list = SequenceList()
    sequence_string = 'CreateOrganisationsForModule \
                       SetUpInventoryIndexingByNodeAndSection \
                       CreateNotVariatedResource \
                       Tic \
                       CreateFullInventoryAtTheDate1 \
                       Tic \
                       CreateFullInventoryAtTheDate2 \
                       Tic \
                       TestFullInventoryCollideWithEachOther \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_15_FullInventoryCanCreatesManyVirtualCompensationMovement(self, quiet=0, run=run_all_test):
    organisation = self.portal.organisation_module.newContent(portal_type='Organisation')
    resource_value_list = []
    for _ in range(2000):
      resource_value_list.append(self.portal.product_module.newContent(portal_type='Product'))

    self.commit()
    self.tic()

    # Create initial inventory
    date_1 = DateTime('2013/04/29 00:00:00 GMT+9')
    result = self.portal.portal_simulation.getCurrentInventoryList(at_date=date_1,
                                                                   section_uid=organisation.getUid(),
                                                                   node_uid=organisation.getUid(),
                                                                   group_by_resource=1)
    self.assertEqual(len(result), 0)

    full_inventory_1 = self.portal.inventory_module.newContent(portal_type='Inventory')
    full_inventory_1.edit(destination_section_value=organisation,
                          destination_value=organisation,
                          start_date=date_1,
                          full_inventory=True)
    for resource_value in resource_value_list:
      full_inventory_1.newContent(portal_type='Inventory Line',
                                  resource_value=resource_value,
                                  quantity=123)
    full_inventory_1.deliver()

    self.commit()
    self.tic()

    result = self.portal.portal_simulation.getCurrentInventoryList(at_date=date_1,
                                                                   section_uid=organisation.getUid(),
                                                                   node_uid=organisation.getUid(),
                                                                   group_by_resource=1)
    self.assertEqual(sorted([(brain.resource_uid, brain.inventory)
                             for brain in result]),
                     sorted([(movement.getResourceUid(), movement.getQuantity())
                             for movement in full_inventory_1.getMovementList()]))

    # Create second inventory which deletes inventories of many resources.
    date_2 = DateTime('2013/05/03 00:00:00 GMT+9')
    full_inventory_2 = self.portal.inventory_module.newContent(portal_type='Inventory')
    full_inventory_2.edit(destination_section_value=organisation,
                          destination_value=organisation,
                          start_date=date_2,
                          full_inventory=True)
    full_inventory_2.newContent(portal_type='Inventory Line',
                                resource_value=resource_value_list[0],
                                quantity=1)
    full_inventory_2.deliver()

    self.commit()
    self.tic()

    result = self.portal.portal_simulation.getCurrentInventoryList(at_date=date_2,
                                                                   section_uid=organisation.getUid(),
                                                                   node_uid=organisation.getUid(),
                                                                   group_by_resource=1)
    self.assertEqual(sorted([(brain.resource_uid, brain.inventory)
                             for brain in result if brain.inventory != 0]),
                     sorted([(movement.getResourceUid(), movement.getQuantity())
                             for movement in full_inventory_2.getMovementList()]))

  @expectedFailure
  def test_16_CorruptedInventoryCacheAndFullInventory(
        self, quiet=0, run=run_all_test):
    """
    XXX-Tatuya: Do we really need to support this case?

    To make assure this validity, we must ignore all the cache when reindexing.

    Proof: Inventory caching caches more than one month older inventory,
    to make THIS inventory valid, we need to invalidate one month ago
    inventory's cache, and the one month ago inventory may wrongly cached two
    month ago inventory and.. by mathematical induction, we need to invalidate
    all the cache when getting inventory from new to old.
     In contrast, reindex from the oldest inventory up to the newest one must
    work if and only if..
    ALL THE WRONG CACHES CAN BE REMOVED/IGNORED BY INVENTORY DOCUMENTS REINDEX.
     For example, if the oldest wrong cache date is 31 days before than the
    oldest inventory, re-index and stock table will be corrupted.
     The cache is still enable because it is older than 30 days ago and newer
    than 60 days ago, at the same time it can not be removed because the date
    is older than the oldest inventory start_date.
    Thus we must ignore all the cache to make assure this case validity.

    The case is:
    1) full inventory: 2013/01/01,section=A, node=B, resource=X, quantity=100
                                                     resource=Y, quantity=100
    2) clear the existing cache
    3) modify stock table by hand
    4) cache the wrong stock result at 2013/02/02
       Note: Here we need to use between 2013/02/02 and 2013/02/28 to cache
             2013/01/01 stock data.
    5) fix back the stock table
    6) full inventory: 2013/02/02,section=A, node=B, resource=X, quantity=100
                                                     resource=Y, quantity=100
       Note: Here we need to use between 2013/02/02 and 2013/02/28
    [test]
    getInventory(resource=X, to_date=2013/02/10) should return 100
    getInventory(resource=Y, to_date=2013/02/10) should return 100
    """
    if not run: return
    self.two_resource_full_inventory1_start_date = '2013/01/01 00:00:00 GMT+9'
    self.two_resource_full_inventory1_inventory_1 = 100
    self.two_resource_full_inventory1_inventory_2 = 100
    self.two_resource_full_inventory2_start_date = '2013/02/02 00:00:00 GMT+9'
    self.two_resource_full_inventory2_inventory_1 = 100
    self.two_resource_full_inventory2_inventory_2 = 100
    self.full_inventory_start_date_1 = '2013/02/10 00:00:00 GMT+9'
    sequence_list = SequenceList()
    sequence_string = 'CreateOrganisationsForModule \
                       CreateNotVariatedResource \
                       CreateNotVariatedSecondResource \
                       CreateTwoResourceFullInventoryAtTheDate1 \
                       Tic \
                       ClearInventoryCache \
                       DoubleStockValue \
                       StoreWrongCache \
                       HalfStockValue \
                       CreateTwoResourceFullInventoryAtTheDate2 \
                       Tic \
                       CheckCorruptedCacheHasFixedByReindex \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_17_FullInventoryUpdateWithValidDateOrder(
        self, quiet=0, run=run_all_test):
    """
    Confirm Full inventory update with a valid start_date order

    The case is:
    1) full inventory: 2013/02/01,section=A, node=B, resource=X, quantity=15
                                                     resource=Y, quantity=20
    2) full inventory: 2013/02/02,section=A, node=B, resource=X, quantity=20
                                                     resource=Y, quantity=50
    3) full inventory: 2013/02/10,section=A, node=B, resource=X, quantity=100
        -> X:100
           Y:0  # creates a dummy movement with quantity=-50
    [test]
    getInventory(resource=X, to_date=2013/02/15) should return 100
    getInventory(resource=Y, to_date=2013/02/15) should return 0
    """
    if not run: return

    self.two_resource_full_inventory1_start_date = '2013/02/01 00:00:00 GMT+9'
    self.two_resource_full_inventory1_inventory_1 = 15
    self.two_resource_full_inventory1_inventory_2 = 20
    self.two_resource_full_inventory2_start_date = '2013/02/02 00:00:00 GMT+9'
    self.two_resource_full_inventory2_inventory_1 = 20
    self.two_resource_full_inventory2_inventory_2 = 50
    self.full_inventory_start_date_1 = '2013/02/10 00:00:00 GMT+9'
    sequence_list = SequenceList()
    sequence_string = 'CreateOrganisationsForModule \
                       CreateNotVariatedResource \
                       CreateNotVariatedSecondResource \
                       CreateTwoResourceFullInventoryAtTheDate1 \
                       Tic \
                       CreateTwoResourceFullInventoryAtTheDate2 \
                       Tic \
                       CreateFullInventoryAtTheDate1 \
                       Tic \
                       CheckFullInventoryUpdateWithValidDateOrder \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_18_InventoryDocumentAndInventoryCache(
        self, quiet=0, run=run_all_test):
    """
    Check that inventory caches that are older than inventory stock movements
    are cleared.

    The case is:
    1) full inventory: 2013/05/01,section=A, node=B, resource=X, quantity=15
                                                     resource=Y, quantity=20
    [test]
    2) getInventory(section=A, node=B, resource=X, at_date=2013/06/11 00:00)
         => should return 15
       getInventory(section=A, node=B, resource=Y, at_date=2013/06/11 00:00)
         => should return 20

    3) full inventory: 2013/05/02,section=A, node=B, resource=X, quantity=30
                                                     resource=Y, quantity=50

    [test]
    4) getInventory(section=A, node=B, resource=X, at_date=2013/06/11 02:00)
       => should return 30
    4) getInventory(section=A, node=B, resource=Y, at_date=2013/06/11 02:00)
       => should return 50
    """
    if not run: return

    self.two_resource_full_inventory1_start_date = '2013/05/01 00:00:00 GMT+9'
    self.two_resource_full_inventory1_inventory_1 = 15
    self.two_resource_full_inventory1_inventory_2 = 20
    self.two_resource_full_inventory2_start_date = '2013/05/02 00:00:00 GMT+9'
    self.two_resource_full_inventory2_inventory_1 = 30
    self.two_resource_full_inventory2_inventory_2 = 50
    sequence_list = SequenceList()
    sequence_string = 'CreateOrganisationsForModule \
                       CreateNotVariatedResource \
                       CreateNotVariatedSecondResource \
                       CreateTwoResourceFullInventoryAtTheDate1 \
                       Tic \
                       CheckGetInveotoryGoesToCache \
                       CreateTwoResourceFullInventoryAtTheDate2 \
                       Tic \
                       CheckInventoryCacheIsClearedAfterAddingInventory \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)


  def stepCreateNotVariatedThirdResource(self,sequence=None,
                                          sequence_list=None,
                                          **kw):
    """
      Create a third resource with no variation
    """
    portal = self.getPortal()
    resource_module = portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent(portal_type=self.resource_portal_type)
    resource.edit(
      title = "NotVariatedThirdResource%s" % resource.getId(),
      industrial_phase_list=["phase1", "phase2"],
      product_line = 'apparel'
    )
    sequence.edit(third_resource = resource )
    resource_list = sequence.get('resource_list',default=[])
    resource_list.append(resource)
    sequence.edit( resource_list = resource_list )


  def stepCreatePackingList(self, sequence=None,
                                      sequence_list=None, **kw):
    """
      Create a single packing_list for Inventory Module testing
    """
    node = kw.get('node', None)
    section = kw.get('section', None)
    resource = kw.get('resource', None)
    quantity = kw.get('quantity', 100)
    price = kw.get('price', None)
    mirror_node =  kw.get('mirror_node', None)
    mirror_section = kw.get('mirror_section', None)
    if mirror_node is None:
      mirror_node = sequence.get('mirror_node')
    if mirror_section is None:
      mirror_section = sequence.get('mirror_section')

    packing_list_portal_type = kw.get('packing_list', self.packing_list_portal_type)
    packing_list_module = self.getPortal().getDefaultModule(
                              portal_type=packing_list_portal_type)
    packing_list = packing_list_module.newContent(
                              portal_type=packing_list_portal_type)

    if kw.get('at_date', None) is not None:
      start_date = stop_date = kw['at_date']
    else:
      start_date = stop_date = DateTime() - 2
    packing_list.edit(
                      specialise=self.business_process,
                      source_section_value = mirror_section,
                      source_value = mirror_node,
                      destination_section_value = section,
                      destination_value = node,
                      start_date = start_date,
                      stop_date = stop_date,
                      price_currency = self.price_currency
                     )

    packing_list_line_portal_type = packing_list_portal_type + ' Line'
    packing_list_line = packing_list.newContent(
                  portal_type = packing_list_line_portal_type)
    packing_list_line.edit(resource_value = resource,
                           quantity = quantity,
                           price = price
                          )
    sequence.edit(packing_list=packing_list)


  def stepCreateSalePackingListToSectionNodeForFirstResource(self, sequence=None,
                                                    sequence_list=None,
                                                    **kw):
    section = sequence.get('section')
    node = sequence.get('node')
    resource = sequence.get('resource')

    self.stepCreatePackingList(sequence=sequence,
                               sequence_list=sequence_list,
                               section = section,
                               node = node,
                               resource = resource,
                               quantity = 100,
                               packing_list= 'Sale Packing List')


  def stepCreateSalePackingListToOtherSectionNodeForFirstResource(self, sequence=None,sequence_list=None,**kw):
    section = sequence.get('other_section')
    node = sequence.get('node')
    resource = sequence.get('resource')

    self.stepCreatePackingList(sequence=sequence,
                               sequence_list=sequence_list,
                               section = section,
                               node = node,
                               resource = resource,
                               quantity = 200,
                               packing_list = 'Sale Packing List')


  def stepCreatePurchasePackingListForSectionOtherNodeForSecondResource(self, sequence=None,
                                                    sequence_list=None,
                                                    **kw):
    section = sequence.get('section')
    node = sequence.get('other_node')
    resource = sequence.get('second_resource')

    self.stepCreatePackingList(sequence=sequence,
                               sequence_list=sequence_list,
                               section = section,
                               node = node,
                               resource = resource,
                               quantity = 50,
                               packing_list = 'Purchase Packing List')


  def stepCreatePurchasePackingListForOtherSectionOtherNodeForThirdResource(self, sequence=None,
                                                    sequence_list=None,
                                                    **kw):
    section = sequence.get('other_section')
    node = sequence.get('other_node')
    resource = sequence.get('third_resource')

    self.stepCreatePackingList(sequence=sequence,
                               sequence_list=sequence_list,
                               section = section,
                               node = node,
                               resource = resource,
                               quantity = 30,
                               packing_list = 'Purchase Packing List')

  def stepTestMultipleOwnerNode(self, sequence=None, sequence_list=None, **kw):
    first_resource_value = sequence.get('resource')
    second_resource_value = sequence.get('second_resource')
    third_resource_value = sequence.get('third_resource')

    node_value = sequence.get('node')
    other_node_value = sequence.get('other_node')
    section_value = sequence.get('section')
    other_section_value = sequence.get('other_section')

    self._testGetInventory(expected=100,
                           section_uid=section_value.getUid(),
                           node_uid=node_value.getUid(),
                           resource_uid=first_resource_value.getUid())
    self._testGetInventory(expected=200,
                           section_uid=other_section_value.getUid(),
                           node_uid=node_value.getUid(),
                           resource_uid=first_resource_value.getUid())
    self._testGetInventory(expected=50,
                           section_uid=section_value.getUid(),
                           node_uid=other_node_value.getUid(),
                           resource_uid=second_resource_value.getUid())
    self._testGetInventory(expected=30,
                           section_uid=other_section_value.getUid(),
                           node_uid=other_node_value.getUid(),
                           resource_uid=third_resource_value.getUid())
  def test_19_InventoryMultipleOwner(self, quiet = 0, run=run_all_test):
    """
     Test multiple owner with multiple node resource.
     The case:
     1) movement: section=A,node=C,resource=X,quantity=100
     2) movement: section=B,node=C,resource=X, quantity=200
     3) movement: section=A,node=D,resource=Y,quantity=50
     4) movement: section=B, node=D,reource=Z,quantity=30

     [Test]
     getInventory(section=A, node=C, resource=X) should return 100
     getInventory(section=B, node=C, resource=X) should return 200
     getInventory(section=A, node=D, resource=Y) should return 50
     getInventory(section=B, node=D, resource=Z) should return 30
    """
    if not run: return

    sequence_list = SequenceList()
    sequence_string = 'CreateOrganisationsForModule \
                       CreateNotVariatedResource \
                       CreateNotVariatedSecondResource \
                       stepCreateNotVariatedThirdResource \
                       Tic \
                       CreateSalePackingListToSectionNodeForFirstResource \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CreateSalePackingListToOtherSectionNodeForFirstResource \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CreatePurchasePackingListForSectionOtherNodeForSecondResource \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CreatePurchasePackingListForOtherSectionOtherNodeForThirdResource \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       TestMultipleOwnerNode \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepInitialAWarehouseX(self, sequence=None, sequence_list=None, **kw):
    #sale packing list
    at_date = DateTime('2013/02/10 00:00:00 GMT+9')
    resource = sequence.get('resource')
    A = sequence.get('section')
    X = sequence.get('node')
    mirror_section = sequence.get('mirror_section')
    mirror_node = sequence.get('mirror_node')

    self.stepCreatePackingList(sequence=sequence,
                                 sequence_list=sequence_list,
                                 section = A,
                                 node = X,
                                 mirror_section = mirror_section,
                                 mirror_node = mirror_node,
                                 resource = resource,
                                 quantity = 100,
                                 at_date = at_date,
                                 packing_list = 'Sale Packing List')

  def stepCreateIPLFromAWarehouseXToAWarehouseYWithQuantity3(self, sequence=None, sequence_list=None, **kw):
    A = sequence.get('section')
    X = sequence.get('node')
    Y = sequence.get('other_node')
    resource = sequence.get('resource')
    at_date = DateTime('2013/02/11 00:00:00 GMT+9')

    self.stepCreatePackingList(sequence=sequence,
                                 sequence_list=sequence_list,
                                 section = A,
                                 node = Y,
                                 mirror_section = A,
                                 mirror_node = X,
                                 resource = resource,
                                 quantity = 3,
                                 at_date = at_date,
                                 packing_list = 'Internal Packing List')

  def stepCancelIPLFromAWarehouseXToAWarehouseYWithQuantity3(self, sequence=None, sequence_list=None, **kw):
    A = sequence.get('section')
    X = sequence.get('node')
    Y = sequence.get('other_node')
    resource = sequence.get('resource')
    at_date = DateTime('2013/02/11 02:00:00 GMT+9')

    self.stepCreatePackingList(sequence=sequence,
                                 sequence_list=sequence_list,
                                 section = A,
                                 node = X,
                                 mirror_section = A,
                                 mirror_node = Y,
                                 resource = resource,
                                 quantity = 3,
                                 at_date = at_date,
                                 packing_list = 'Internal Packing List')

  def stepCreateIPLFromAWarehouseXToAWarehouseYWithQuantity30(self, sequence=None, sequence_list=None, **kw):
    A = sequence.get('section')
    X = sequence.get('node')
    Y = sequence.get('other_node')
    resource = sequence.get('resource')
    at_date = DateTime('2013/02/13 04:00:00 GMT+9')

    self.stepCreatePackingList(sequence=sequence,
                                 sequence_list=sequence_list,
                                 section = A,
                                 node = Y,
                                 mirror_section = A,
                                 mirror_node = X,
                                 resource = resource,
                                 quantity = 30,
                                 at_date = at_date,
                                 packing_list = 'Internal Packing List')

  def stepCancelIPLFromAWarehouseXToAWarehouseYWithQuantity30(self, sequence=None, sequence_list=None, **kw):
    A = sequence.get('section')
    X = sequence.get('node')
    Y = sequence.get('other_node')
    resource = sequence.get('resource')
    at_date = DateTime('2013/02/14 05:00:00 GMT+9')

    self.stepCreatePackingList(sequence=sequence,
                                 sequence_list=sequence_list,
                                 section = A,
                                 node = X,
                                 mirror_section = A,
                                 mirror_node = Y,
                                 resource = resource,
                                 quantity = 30,
                                 at_date = at_date,
                                 packing_list = 'Internal Packing List')

  def stepCreateSPLFromAWarehouseXToBWarehouseYWithQuantity30(self, sequence=None,
                                      sequence_list=None, **kw):
    A = sequence.get('section')
    X = sequence.get('node')
    B = sequence.get('other_section')
    Y = sequence.get('other_node')
    resource = sequence.get('resource')
    at_date = DateTime('2013/02/14 04:00:00 GMT+9')

    self.stepCreatePackingList(sequence=sequence,
                                 sequence_list=sequence_list,
                                 section = B,
                                 node = Y,
                                 mirror_section = A,
                                 mirror_node = X,
                                 resource = resource,
                                 quantity = 30,
                                 at_date = at_date,
                                 packing_list = 'Sale Packing List')

  def stepCreatePPLForCWarehouseXFromAWarehouseXWithQuantity10(self, sequence=None,
                                      sequence_list=None, **kw):
    resource = sequence.get('resource')
    C = sequence.get('one_more_section')
    X = sequence.get('node')
    A = sequence.get('section')
    X = sequence.get('node')
    at_date = DateTime('2013/02/11 04:00:00 GMT+9')
    self.stepCreatePackingList(sequence=sequence,
                                 sequence_list=sequence_list,
                                 section = C,
                                 node = X,
                                 mirror_section = A,
                                 mirror_node = X,
                                 resource = resource,
                                 quantity = 10,
                                 at_date = at_date,
                                 packing_list = 'Purchase Packing List')

  def stepCancelSPLFromAWarehouseXToBWarehouseYWithQuantity30(self, sequence=None,
                                      sequence_list=None, **kw):
    A = sequence.get('section')
    X = sequence.get('node')
    B = sequence.get('other_section')
    Y = sequence.get('other_node')
    resource = sequence.get('resource')
    at_date = DateTime('2013/02/14 06:00:00 GMT+9')

    self.stepCreatePackingList(sequence=sequence,
                                 sequence_list=sequence_list,
                                 section = A,
                                 node = X,
                                 mirror_section = B,
                                 mirror_node = Y,
                                 resource = resource,
                                 quantity = 30,
                                 at_date = at_date,
                                 packing_list = 'Sale Packing List')



  def stepCreateProductionPFromAFactoryZToAWarehouseXWithQuantity10(self, sequence=None,
                                      sequence_list=None, **kw):
    A = sequence.get('section')
    Z = sequence.get('factory')
    X = sequence.get('node')
    resource = sequence.get('resource')
    at_date = DateTime('2013/02/14 08:00:00 GMT+9')

    self.stepCreatePackingList(sequence=sequence,
                                 sequence_list=sequence_list,
                                 section = A,
                                 node = X,
                                 mirror_section = A,
                                 mirror_node = Z,
                                 resource = resource,
                                 quantity = 10,
                                 at_date = at_date,
                                 packing_list = 'Production Packing List')


  def stepCreateSPLFromAWarehouseXToBWarehouseYWithQuantity24(self, sequence=None,
                                      sequence_list=None, **kw):
    A = sequence.get('section')
    X = sequence.get('node')
    B = sequence.get('other_section')
    Y = sequence.get('other_node')
    resource = sequence.get('resource')
    at_date = DateTime('2013/02/16 00:00:00 GMT+9')

    self.stepCreatePackingList(sequence=sequence,
                                 sequence_list=sequence_list,
                                 section = B,
                                 node = Y,
                                 mirror_section = A,
                                 mirror_node = X,
                                 resource = resource,
                                 quantity = 24,
                                 at_date = at_date,
                                 packing_list = 'Sale Packing List')

  def stepCreatePPLForCWarehouseXFromBWarehouseYWithQuantity5(self, sequence=None, sequence_list=None, **kw):
    C = sequence.get('one_more_section')
    X = sequence.get('node')
    B = sequence.get('other_section')
    Y = sequence.get('other_node')
    resource = sequence.get('resource')
    at_date = DateTime('2013/02/24 00:00:00 GMT+9')

    self.stepCreatePackingList(sequence=sequence,
                                 sequence_list=sequence_list,
                                 section = C,
                                 node = X,
                                 mirror_section = B,
                                 mirror_node = Y,
                                 resource = resource,
                                 quantity = 5,
                                 at_date = at_date,
                                 packing_list = 'Purchase Packing List')


  def stepCreateIPLFromAWarehouseXToAWarehouseYWithQuantity33(self, sequence=None, sequence_list=None, **kw):
    A = sequence.get('section')
    X = sequence.get('node')

    Y = sequence.get('other_node')
    resource = sequence.get('resource')
    at_date = DateTime('2013/02/25 01:00:00 GMT+9')

    self.stepCreatePackingList(sequence=sequence,
                                 sequence_list=sequence_list,
                                 section = A,
                                 node = Y,
                                 mirror_section = A,
                                 mirror_node = X,
                                 resource = resource,
                                 at_date = at_date,
                                 quantity = 33,
                                 packing_list = 'Internal Packing List')


  def stepCancelPPLForCWarehouseXFromBWarehouseYWithQuantity5(self, sequence=None, sequence_list=None, **kw):
    C = sequence.get('one_more_section')
    X = sequence.get('node')
    B = sequence.get('other_section')
    Y = sequence.get('other_node')
    resource = sequence.get('resource')
    at_date = DateTime('2013/02/25 02:00:00 GMT+9')
    self.stepCreatePackingList(sequence=sequence,
                                 sequence_list=sequence_list,
                                 section = B,
                                 node = Y,
                                 mirror_section = C,
                                 mirror_node = X,
                                 resource = resource,
                                 quantity = 5,
                                 at_date = at_date,
                                 packing_list = 'Purchase Packing List')

  def stepCreatePPLForCWarehouseXFromBWarehouseYWithQuantity10(self, sequence=None, sequence_list=None, **kw):
    C = sequence.get('one_more_section')
    X = sequence.get('node')
    B = sequence.get('other_section')
    Y = sequence.get('other_node')
    resource = sequence.get('resource')
    at_date = DateTime('2013/02/26 00:00:00 GMT+9')

    self.stepCreatePackingList(sequence=sequence,
                                 sequence_list=sequence_list,
                                 section = C,
                                 node = X,
                                 mirror_section = B,
                                 mirror_node = Y,
                                 resource = resource,
                                 quantity = 10,
                                 at_date = at_date,
                                 packing_list = 'Purchase Packing List')

  def stepCreateOneMoreSection(self, sequence=None,
                                 sequence_list=None, **kw):
    self.stepCreateOrganisation(sequence=sequence,
                        sequence_list=sequence_list, **kw)
    one_more_section = sequence.get('organisation')
    sequence.edit(
          one_more_section = one_more_section
        )
  def stepCreateFactory(self, sequence=None,
                                 sequence_list=None, **kw):
    self.stepCreateOrganisation(sequence=sequence,
                        sequence_list=sequence_list, **kw)
    factory = sequence.get('organisation')
    sequence.edit(
          factory = factory
        )
  def stepDeliverProductionPackingList(self, sequence=None,
                                      sequence_list=None, **kw):
    # Switch to "started" state
    packing_list = sequence.get('packing_list')
    workflow_tool = self.getPortal().portal_workflow
    workflow_tool.doActionFor(packing_list,
                      "confirm_action", "production_packing_list_workflow")
    self.commit()
    # Apply tic so that the packing list is not in building state
    self.tic() # acceptable here because this is not the job
               # of the test to check if can do all transition
               # without processing messages
    workflow_tool.doActionFor(packing_list,
                      "set_ready_action", "production_packing_list_workflow")
    self.tic()
    workflow_tool.doActionFor(packing_list,
                      "start_action", "production_packing_list_workflow")
    workflow_tool.doActionFor(packing_list,
                      "stop_action", "production_packing_list_workflow")
    workflow_tool.doActionFor(packing_list,
                      "deliver_action", "production_packing_list_workflow")

  def stepTestMultiCancelInventory(self, sequence=None,
                                 sequence_list=None, **kw):
    resource_value = sequence.get('resource')
    A = sequence.get('section')
    B = sequence.get('other_section')
    C = sequence.get('one_more_section')
    X = sequence.get('node')
    Y = sequence.get('other_node')

    self._testGetInventory(
      expected=33,
      section_uid=A.getUid(),
      node_uid=Y.getUid(),
      resource_uid=resource_value.getUid())

    self._testGetInventory(
      expected=43,
      section_uid=A.getUid(),
      node_uid=X.getUid(),
      resource_uid=resource_value.getUid())

    self._testGetInventory(
      expected=14,
      section_uid=B.getUid(),
      node_uid=Y.getUid(),
      resource_uid=resource_value.getUid())

    self._testGetInventory(
      expected=20,
      section_uid=C.getUid(),
      node_uid=X.getUid(),
      resource_uid=resource_value.getUid())

    at_date = DateTime('2013/02/15 00:00:00 GMT+9')

    self._testGetInventory(
      expected=0,
      section_uid=A.getUid(),
      node_uid=Y.getUid(),
      at_date = at_date,
      resource_uid=resource_value.getUid())

    self._testGetInventory(
      expected=100,
      section_uid=A.getUid(),
      node_uid=X.getUid(),
      at_date = at_date,
      resource_uid=resource_value.getUid())

    self._testGetInventory(
      expected=0,
      section_uid=B.getUid(),
      node_uid=Y.getUid(),
      at_date = at_date,
      resource_uid=resource_value.getUid())

    self._testGetInventory(
      expected=10,
      section_uid=C.getUid(),
      node_uid=X.getUid(),
      at_date = at_date,
      resource_uid=resource_value.getUid())

    at_date = DateTime('2013/02/25 00:00:00 GMT+9')

    self._testGetInventory(
      expected=0,
      section_uid=A.getUid(),
      node_uid=Y.getUid(),
      at_date = at_date,
      resource_uid=resource_value.getUid())

    self._testGetInventory(
      expected=76,
      section_uid=A.getUid(),
      node_uid=X.getUid(),
      at_date = at_date,
      resource_uid=resource_value.getUid())

    self._testGetInventory(
      expected=19,
      section_uid=B.getUid(),
      node_uid=Y.getUid(),
      at_date = at_date,
      resource_uid=resource_value.getUid())

    self._testGetInventory(
      expected=15,
      section_uid=C.getUid(),
      node_uid=X.getUid(),
      at_date = at_date,
      resource_uid=resource_value.getUid())


  def test_20_InventoryWhenCancelPackingList(self, quite=0, run=run_all_test):
    """
    initial 2013/02/10 00:00:00 GMT+9:
    A warehouse X, has product: Notvariated 100

    2013/02/11 00:00:00 GMT+9
    IPL 1: A warehouse X ----> A warehouse Y, quantity: 3

    2013/02/11 02:00:00 GMT+9
    cancel IPL1

    2013/02/13 04:00:00 GMT+9
    IPL 2: A warehouse X ----> A warehouse Y, quantity: 30

    2013/02/14 04:00:00 GMT+9
    SPL 1: A warehouse X ----> B warehouse Y, quantity: 30

    2013/02/14 05:00:00 GMT+9
    cancel IPL2

    2013/02/11 04:00:00 GMT+9
    PPL 1: A warehouse X ----> C warehouse X, quantity: 10

    2013/02/14 06:00:00 GMT+9
    cancel SPL1

    2013/02/14 08:00:00 GMT+9
    Production PL: A factory Z  ---> A warehouse X, quantity: 10

    2013/02/16 00:00:00 GMT+9
    SPL 2: A warehouse X ----> B warehouse Y, quantity: 24

    2013/02/24 00:00:00 GMT+9
    PPL 2: B warehouse Y ----> C warehouse X, quantity: 5

    2013/02/25 01:00:00 GMT+9
    IPL 3: A warehouse X ----> A warehouse Y, quantity: 33

    2013/02/25 02:00:00 GMT+9
    cancel PPL 2

    2013/02/26 00:00:00 GMT+9
    PPL 3: B warehouse Y ----> C warehouse X, quantity: 10

    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = 'CreateOrganisationsForModule \
                       CreateOneMoreSection \
                       CreateFactory \
                       CreateNotVariatedResource \
                       Tic \
                       InitialAWarehouseX \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CreateIPLFromAWarehouseXToAWarehouseYWithQuantity3 \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CancelIPLFromAWarehouseXToAWarehouseYWithQuantity3 \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CreateIPLFromAWarehouseXToAWarehouseYWithQuantity30 \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CreateSPLFromAWarehouseXToBWarehouseYWithQuantity30 \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CancelIPLFromAWarehouseXToAWarehouseYWithQuantity30 \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CreatePPLForCWarehouseXFromAWarehouseXWithQuantity10 \
                       Tic \
                       DeliverPackingList\
                       Tic \
                       CancelSPLFromAWarehouseXToBWarehouseYWithQuantity30 \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CreateProductionPFromAFactoryZToAWarehouseXWithQuantity10 \
                       Tic \
                       DeliverProductionPackingList \
                       Tic \
                       CreateSPLFromAWarehouseXToBWarehouseYWithQuantity24 \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CreatePPLForCWarehouseXFromBWarehouseYWithQuantity5 \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CreateIPLFromAWarehouseXToAWarehouseYWithQuantity33 \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CancelPPLForCWarehouseXFromBWarehouseYWithQuantity5 \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       CreatePPLForCWarehouseXFromBWarehouseYWithQuantity10 \
                       Tic \
                       DeliverPackingList \
                       Tic \
                       TestMultiCancelInventory\
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)



def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestInventory))
  return suite
