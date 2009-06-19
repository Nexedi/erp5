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
import transaction

from Products.ERP5Type.Utils import cartesianProduct
from copy import copy


from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from DateTime import DateTime
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.DateUtils import addToDate
from testOrder import TestOrderMixin

from Products.ERP5Form.Selection import DomainSelection

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
    return ('erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_apparel')

  def afterSetUp(self, quiet=1, run=run_all_test):
    self.login()
    self.category_tool = self.getCategoryTool()
    self.createCategories()
    self.validateRules()
    # Patch PackingList.asPacked so that we do not need
    # to manage containers here, this not the job of this test
    def isPacked(self):
      return 1
    from Products.ERP5Type.Document.PackingList import PackingList
    PackingList.isPacked = isPacked
    self.createCurrency()

  def createCategory(self, parent, id_list):
      last_category = None
      for category_id in id_list:
        if type(category_id) == type('a'):
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
    sequence.edit(
          node = node,
          section = section,
          mirror_node = mirror_node,
          mirror_section = mirror_section,
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

  def createInventory(self, sequence=None):
    """
    """
    portal = self.getPortal()
    inventory_list = sequence.get('inventory_list',[])
    inventory_module = portal.getDefaultModule(portal_type = self.inventory_portal_type)
    inventory = inventory_module.newContent(portal_type = self.inventory_portal_type)
    inventory.edit(destination_value = sequence.get('node'),
                   destination_section_value = sequence.get('section'),
                   start_date = DateTime() + 1
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
    category_list = sequence.get('variation_2')
    inventory_line = inventory.newContent(portal_type = self.inventory_line_portal_type)
    inventory_line.edit(resource_value = sequence.get('resource'),
                        variation_category_list=category_list
                       )
    cell = inventory_line.newCell(base_id='movement',*category_list)
    quantity=0
    cell.edit(
        quantity = quantity,
        predicate_category_list = category_list,
        variation_category_list = category_list,
        mapped_value_property_list = ['quantity'],
        )
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
    resource = sequence.get('resource')
    packing_list_module = self.getPortal().getDefaultModule(
                              portal_type=self.packing_list_portal_type)
    packing_list = packing_list_module.newContent(
                              portal_type=self.packing_list_portal_type)
    packing_list.edit(
                      source_section_value = mirror_section,
                      source_value = mirror_node,
                      destination_section_value = section,
                      destination_value = node,
                      start_date = DateTime() - 2,
                      stop_date = DateTime() - 2,
                      price_currency = self.price_currency
                     )
    self.assertNotEquals( packing_list.getSourceSectionValue(), None)
    self.assertNotEquals( packing_list.getSourceValue(), None)
    self.assertNotEquals( packing_list.getSourceSectionValue(),
                          packing_list.getDestinationSectionValue() )
    sequence.edit(packing_list=packing_list)

  def stepCreatePackingListLine(self, sequence=None,
                                      sequence_list=None, **kw):
    """
    Create a line not variated
    """
    packing_list = sequence.get('packing_list')
    resource = sequence.get('resource')
    packing_list_line = packing_list.newContent(
                  portal_type=self.packing_list_line_portal_type)
    packing_list_line.edit(resource_value = resource,
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
          quantity = quantity,
          predicate_category_list = cell_key,
          variation_category_list = cell_key,
          mapped_value_property_list = ['quantity'],
          )
    sequence.edit(delivery_line_list=delivery_line_list)

  def stepDeliverPackingList(self, sequence=None,
                                      sequence_list=None, **kw):
    # Switch to "started" state
    packing_list = sequence.get('packing_list')
    workflow_tool = self.getPortal().portal_workflow
    workflow_tool.doActionFor(packing_list,
                      "confirm_action", "packing_list_workflow")
    transaction.commit()
    # Apply tic so that the packing list is not in building state
    self.tic() # acceptable here because this is not the job
               # of the test to check if can do all transition
               # without processing messages
    workflow_tool.doActionFor(packing_list,
                      "set_ready_action", "packing_list_workflow")
    transaction.commit()
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
    for i in range(10):
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
    for i in range(3):
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
    order = sequence.get('order')
    packing_list_module = self.getPortal().getDefaultModule(self.packing_list_portal_type)
    
    for data in data_list:
      # Create Packing List
      packing_list = packing_list_module.newContent(portal_type=self.packing_list_portal_type)
      packing_list_list.append(packing_list)
      # Add properties
      property_list = [x for x in data.items() if x[0] not in ('lines','start_date')]
      property_list = [(x[0], organisation_list[x[1]].getRelativeUrl()) for x in property_list] + \
                      [x for x in data.items() if x[0] in ('start_date',)]
      property_dict = {}
      property_dict['price_currency'] = self.price_currency
      for (id, value) in property_list: property_dict[id] = value
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
          self.failUnless(len(packing_list_line.getVariationBaseCategoryList())>0)
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
    self.stepTic()
    
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
    simulation = self.getPortal().portal_simulation
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
        self.assertEquals(inventory_object.getQuantity(), 0.5)
        self.assertEquals(inventory.getQuantity(), 0.5)
    self.failUnless(found==1)

    
    
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
    organisation_list = sequence.get('organisation_list')
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
    organisation_list = sequence.get('organisation_list')
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
    organisation_list = sequence.get('organisation_list')
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
    organisation_list = sequence.get('organisation_list')
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
      self.assertEquals(e_inventory, a_inventory, msg)

               
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
          self.failUnless(0)
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
          self.assertEquals(a_inventory, e_inventory)
        
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
      transited_pl.recursiveImmediateReindexObject() # XXX
      transaction.commit()
      self.stepTic()
      
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
          self.failUnless(0)
        a_attributes[attr] = getattr(inventory, attr)
      a_inventory = inventory.inventory
      # Build a function to filter on attributes
      def cmpfunction(item):
        for (key, value) in a_attributes.items():
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
      found_list = filter(lambda x:x['inventory'] == a_inventory, expected_list)
      if len(found_list) == 0:
        LOG('TEST ERROR : Found a line with getInventoryList which is not expected.', 0, 'Found line : %s (inventory : %s) ; expected values with these attributes : %s' % (a_attributes, a_inventory, expected_list))
        LOG('SQL Query was : ', 0, repr(simulation.getInventoryList(src__=1, **kw)))
        self.assertNotEquals(len(found_list), 0)
      found = found_list[0]
      LOG('found a line with inventory =', 0, repr(found['inventory']))
      del expected[found['id']]
    # All inventory lines were found. Now check if some expected values remain
    if len(expected) > 0:
      LOG('TEST ERROR : Not all expected values were matched. Remaining =', 0, expected)
      LOG('SQL Query was : ', 0, str(simulation.getInventoryList(src__=1, **kw)))
      self.failUnless(len(expected), 0)
      
      
  def stepTestGetNextNegativeInventoryDate(self, sequence=None, sequence_list=None, **kw):
    """
      Test getNextNegativeInventoryDate
    """
    expected_negative_date = addToDate(DateTime())
    base_category_list = ['size', 'colour', 'morphology']
    variation_categories = ['size/Baby', '1', '5'] # size, colour, morphology
    node = 3
    # Set some new deliveries to reach a negative inventory
    # Resource and variation MUST be the same on each new delivery
    data_list = [
      { 'source':node, 'destination':9, 'source_section':0, 'destination_section':7,
        'source_payment':1, 'destination_payment':8, 'start_date':expected_negative_date, 'lines':[
           {'resource':0, 'cells': [
               {'variation':variation_categories, 'quantity':100000.},
             ]
           }, # line end
        ] 
      }, # packing list end
      { 'source':6, 'destination':node, 'source_section':4, 'destination_section':0,
        'source_payment':5, 'destination_payment':1, 'start_date':expected_negative_date+5, 'lines':[
           {'resource':0, 'cells': [
               {'variation':variation_categories, 'quantity':100000.},
             ]
           }, # line end
        ] 
      }, # packing list end
    ]
    
    portal = self.getPortal()
    simulation = portal.portal_simulation
    packing_list_module = portal.getDefaultModule(self.packing_list_portal_type)
    packing_list_list = sequence.get('packing_list_list')
    organisation_list = sequence.get('organisation_list')
    resource_list = sequence.get('resource_list')
    delivery_line_list = []
    
    for data in data_list:
      # Create Packing List
      packing_list = packing_list_module.newContent(portal_type=self.packing_list_portal_type)
      packing_list_list.append(packing_list)
      # Add properties
      property_list = [x for x in data.items() if x[0] not in ('lines','start_date')]
      property_list = [(x[0], organisation_list[x[1]].getRelativeUrl()) for x in property_list] + \
                      [x for x in data.items() if x[0] in ('start_date',)]
      property_dict = {}
      for (id, value) in property_list: property_dict[id] = value
      packing_list.edit(**property_dict)
      for line in data['lines']:
        # Create Packing List Line
        packing_list_line = packing_list.newContent(portal_type=self.packing_list_line_portal_type)
        delivery_line_list.append(packing_list_line)
        resource_value = resource_list[line['resource']]
        resource_value.setVariationBaseCategoryList(base_category_list)
        category_list = packing_list_line.getCategoryList()
        variation_category_list = resource_value.getVariationRangeCategoryList(base_category_list=['size']) + \
            ['colour/' + x.getRelativeUrl() for x in resource_value.objectValues(portal_type='Apparel Model Colour Variation')] + \
            ['morphology/' + x.getRelativeUrl() for x in resource_value.objectValues(portal_type='Apparel Model Morphology Variation')]

        packing_list_line.edit(
            resource_value=resource_value,
            variation_category_list=variation_category_list,
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
    
    transaction.commit()
    self.stepTic()
    transaction.commit()
    
    # Then test the next negative date
    next_date = simulation.getNextNegativeInventoryDate(
                      resource=resource_value.getRelativeUrl(),
                      node=organisation_list[node].getRelativeUrl(),
                      variation_category=variation_categories)

    if type(next_date) == type(''):
      next_date = DateTime(next_date)
    next_date = next_date.strftime('%Y-%m-%d %H:%M:%S')
    expected_negative_date = '%.4d-%.2d-%.2d %.2d:%.2d:%.2d' % (
                            expected_negative_date.year(),
                            expected_negative_date.month(),
                            expected_negative_date.day(),
                            expected_negative_date.hour(),
                            expected_negative_date.minute(),
                            expected_negative_date.second())
    if next_date != expected_negative_date:
      LOG('TEST ERROR : Next negative date is not the expected one.', 0,
          'calculated : %s, expected : %s' % (
           repr(next_date), repr(expected_negative_date)))
      LOG('SQL Query was ', 0,
          simulation.getNextNegativeInventoryDate(
                    resource=resource_value.getRelativeUrl(),
                    node=organisation_list[node].getRelativeUrl(),
                    variation_category=variation_categories, src__=1))
    self.assertEquals(next_date, expected_negative_date)


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
                    section=sequence.get('section').getRelativeUrl(),
                    node=sequence.get('node').getRelativeUrl(),
                    variation_text=variation_text
                )
    self.assertEquals(inventory, quantity)
      
  def stepTestInitialVariatedInventory(self, sequence=None, sequence_list=None, **kw):
    """
      Test Inventory Module behavior
    """
    resource = sequence.get('resource')
    variation_category_list = sequence.get('variation_1')
    quantity = 1
    self.checkVariatedInventory(variation_category_list=variation_category_list,
                                quantity=quantity,sequence=sequence)
    variation_category_list = sequence.get('variation_2')
    quantity = 3
    self.checkVariatedInventory(variation_category_list=variation_category_list,
                                quantity=quantity,sequence=sequence)

  def stepTestVariatedInventoryAfterInventory(self, sequence=None, sequence_list=None, **kw):
    """
      Test Inventory Module behavior
    """
    resource = sequence.get('resource')
    variation_category_list = sequence.get('variation_1')
    quantity = 5
    self.checkVariatedInventory(variation_category_list=variation_category_list,
                                quantity=quantity,sequence=sequence)
    variation_category_list = sequence.get('variation_2')
    quantity = 0
    self.checkVariatedInventory(variation_category_list=variation_category_list,
                                quantity=quantity,sequence=sequence)

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
    self.assertEquals(inventory, expected[step][0],
                    'section=%s, node=%s' % (
                    sequence.get('section').getRelativeUrl(),
                    sequence.get('node').getRelativeUrl()))
    step += 1
    sequence.edit(step=step)
    
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
                                   stepTestGetNextNegativeInventoryDate \
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

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestInventory))
  return suite

