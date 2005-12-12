##############################################################################
#
# Copyright (c) 2004, 2005 Nexedi SARL and Contributors. All Rights Reserved.
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
from testOrder import TestOrderMixin

class TestInventoryModule(TestOrderMixin,ERP5TypeTestCase):
  """
    Test business template erp5_trade 
  """
  run_all_test = 0
  inventory_portal_type = 'Inventory'
  inventory_line_portal_type = 'Inventory Line'
  inventory_cell_portal_type = 'Inventory Line'
  first_date_string = '2005/12/09' # First Inventory
  second_date_string = '2005/12/29' # Next Inventory
  view_stock_date = '2005/12/31' # The day where we are looking for stock

  def getInventoryModule(self):
    return getattr(self.getPortal(), 'inventory_module',None)

  def stepCommit(self,**kw):
    get_transaction().commit()

  def createNotVariatedInventory(self, start_date=None,quantity=None,
                                       sequence=None,**kw):
    """
    We will put default values for an inventory
    """
    portal = self.getPortal()
    resource = sequence.get('resource_list')[0]
    organisation =  sequence.get('organisation')
    inventory = self.getInventoryModule().newContent()
    inventory.edit(start_date=start_date,
                   destination_value=organisation)
    inventory_line = inventory.newContent(
           portal_type=self.inventory_line_portal_type)
    inventory_line.edit(inventory=quantity,
                        resource_value = resource,
                        destination_value=organisation)
    LOG('create inventory with start_date',0,start_date)
    LOG('inventory.getStopDate',0,inventory.getStopDate())
    LOG('inventory_line.getStopDate',0,inventory_line.getStopDate())
    LOG('inventory_line.showDict()',0,inventory_line.showDict())
    return inventory

  def stepCreateFirstNotVariatedInventory(self, sequence=None, sequence_list=None, \
                                 **kw):
    """
    We will put default values for an inventory
    """
    portal = self.getPortal()
    date = DateTime(self.first_date_string)
    LOG('stepCreateFirstNotVariatedInventory, date',0,date)
    quantity=self.default_quantity
    self.createNotVariatedInventory(start_date=date,sequence=sequence,
                                    quantity=quantity)

  def stepCreateSecondNotVariatedInventory(self, sequence=None, sequence_list=None, \
                                 **kw):
    """
    We will put default values for an inventory
    """
    portal = self.getPortal()
    date = DateTime(self.second_date_string)
    quantity=self.default_quantity - 2
    self.createNotVariatedInventory(start_date=date,sequence=sequence,
                                    quantity=quantity)

  def stepCheckFirstNotVariatedInventory(self, start_date=None,quantity=None,
                                             sequence=None,**kw):
    node_uid = sequence.get('organisation').getUid()
    resource_url = sequence.get('resource').getRelativeUrl()
    date = DateTime(self.view_stock_date)
    LOG('sql src',0,self.getSimulationTool().getInventory(node_uid=node_uid,
                        resource=resource_url,
                        to_date=date,src__=1))
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                        resource=resource_url,
                        to_date=date)
    self.assertEquals(self.default_quantity,quantity)

  def stepCheckSecondNotVariatedInventory(self, start_date=None,quantity=None,
                                             sequence=None,**kw):
    node_uid = sequence.get('organisation').getUid()
    resource_url = sequence.get('resource').getRelativeUrl()
    date = DateTime(self.view_stock_date)
    quantity = self.getSimulationTool().getInventory(node_uid=node_uid,
                        resource=resource_url,
                        to_date=date)
    self.assertEquals(self.default_quantity-2,quantity)

  def test_01_NotVariatedInventory(self, quiet=0, run=1):
    """
    We will create an inventory with the default quantity for
    a particular resource. Then we will check if the is correct.
    Then we create another inventory and see if we have the new
    stock value
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = 'CreateNotVariatedResource \
                       CreateOrganisation \
                       CreateFirstNotVariatedInventory \
                       Tic \
                       Commit \
                       CheckFirstNotVariatedInventory \
                       CreateSecondNotVariatedInventory \
                       Tic \
                       CheckSecondNotVariatedInventory'
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def createVariatedInventory(self, sequence=None, sequence_list=None, \
                                 **kw):
    """
    We will put default values for an inventory
    """
    portal = self.getPortal()
    inventory = self.createVariatedInventory(date=date,sequence=sequence)
    inventory_line = self.objectValues(
         portal_type=self.inventory_line_portal_type)[0]
    order_line = sequence.get('order_line')
    # XXX XXX XXX To be updated
    resource = sequence.get('resource')
    resource_vcl = list(resource.getVariationCategoryList(
                                   omit_individual_variation=0))
    resource_vcl.sort()
    order_line.setVariationCategoryList(resource_vcl)
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
                price=price, quantity=quantity,
                predicate_category_list=cell_key,
                variation_category_list=cell_key)
      price += 1
      quantity += 1

  def stepCreateVariatedInventory(self, sequence=None, sequence_list=None, \
                                 **kw):
    """
    We will put default values for an inventory
    """
    portal = self.getPortal()
    date = DateTime(self.first_date_string)
    inventory = self.createVariatedInventory(date=date,sequence=sequence)
    inventory_line = 'a'

  def createVariatedInventory(self, start_date=None,quantity=None,
                                       sequence=None,**kw):
    """
    We will put default values for an inventory
    """
    inventory = self.createNotVariatedInventory()
    resource = sequence.get('resource_list')[0]
    organisation =  sequence.get('organisation')
    inventory = self.getInventoryModule().newContent()
    inventory.edit(start_date=start_date,
                   destination_value=organisation)
    inventory_line = inventory.newContent(
           portal_type=self.inventory_line_portal_type)
    inventory_line.edit(inventory=quantity,
                        resource_value = resource,
                        destination_value=organisation)

  def test_02_VariatedInventory(self, quiet=0, run=run_all_test):
    """
    Same thing as test_01 with variation
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = ''
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_02_VariatedAggregatedInventory(self, quiet=0, run=run_all_test):
    """
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = ''
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

