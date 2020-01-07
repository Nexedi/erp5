
#############################################################################
#
# Copyright (c) 2005-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Aurelien Calonne <aurel@nexedi.com>
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


# import requested python module
import os
from Products.ERP5Type.tests.Sequence import SequenceList
from erp5.component.module.TestERP5BankingMixin import TestERP5BankingMixin
from DateTime import DateTime

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'


class TestERP5BankingInventory(TestERP5BankingMixin):
  """
    This class is a unit test to check the module of Cash Transfer

    Here are the following step that will be done in the test :

    XXX to be completed

  """


  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet


  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingInventory"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    # Set some variables :
    self.initDefaultVariable()
    # the cash inventory module
    self.cash_inventory_module = self.getCashInventoryModule()

    self.createManagerAndLogin()
    self.createFunctionGroupSiteCategory()
    # do everything as manager, as no roles are defined for inventory


  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    # check that Categories were created
    self.assertEqual(self.paris.getPortalType(), 'Category')

    # check that Resources were created
    # check portal type of billet_10000
    self.assertEqual(self.billet_10000.getPortalType(), 'Banknote')
    # check value of billet_10000
    self.assertEqual(self.billet_10000.getBasePrice(), 10000)
    # check currency value  of billet_10000
    self.assertEqual(self.billet_10000.getPriceCurrency(), 'currency_module/EUR')
    # check years  of billet_10000
    self.assertEqual(self.billet_10000.getVariationList(), ['1992', '2003'])

    # check portal type of billet_5000
    self.assertEqual(self.billet_5000.getPortalType(), 'Banknote')
    # check value of billet_5000
    self.assertEqual(self.billet_5000.getBasePrice(), 5000)
    # check currency value  of billet_5000
    self.assertEqual(self.billet_5000.getPriceCurrency(), 'currency_module/EUR')
    # check years  of billet_5000
    self.assertEqual(self.billet_5000.getVariationList(), ['1992', '2003'])

    # check portal type of piece_200
    self.assertEqual(self.piece_200.getPortalType(), 'Coin')
    # check value of piece_200
    self.assertEqual(self.piece_200.getBasePrice(), 200)
    # check currency value  of piece_200
    self.assertEqual(self.piece_200.getPriceCurrency(), 'currency_module/EUR')
    # check years  of piece_200
    self.assertEqual(self.piece_200.getVariationList(), ['1992', '2003'])

    # check that CashInventory Module was created
    self.assertEqual(self.cash_inventory_module.getPortalType(), 'Cash Inventory Module')
    # check cash inventory module is empty
    self.assertEqual(len(self.cash_inventory_module.objectValues()), 0)


  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 0 banknotes of 10000 in caisse_1
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.paris.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.paris.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 0 coin of 200 in caisse_1
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.paris.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.paris.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    # check we have 0 banknotes of 5000 in caisse_1
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.paris.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.paris.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)


  def stepCreateCashInventoryGroup(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a cash inventory document and check it
    """
    # Cash inventory has caisse_1 for source, caisse_2 for destination, and a price cooreponding to the sum of banknote of 10000 abd coin of 200 ( (2+3) * 1000 + (5+7) * 200 )
    self.cash_inventory_group = self.cash_inventory_module.newContent(id='cash_inventory_group', portal_type='Cash Inventory Group', source_value=None, destination_value=self.paris, start_date = DateTime())
    # execute tic
    self.tic()
    # check we have only one cash inventory
    self.assertEqual(len(self.cash_inventory_module.objectValues()), 1)
    # get the cash inventory document
    self.cash_inventory = getattr(self.cash_inventory_module, 'cash_inventory_group')
    # check its portal type
    self.assertEqual(self.cash_inventory.getPortalType(), 'Cash Inventory Group')
    # check that its source is caisse_1
    self.assertEqual(self.cash_inventory.getSource(), None)
    # check that its destination is caisse_2
    self.assertEqual(self.cash_inventory.getDestination(), 'site/testsite/paris')


  def stepCreateCashInventoryGroup2(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a second cash inventory document and check it
    """
    # Cash inventory has caisse_1 for source, caisse_2 for destination, and a price cooreponding to the sum of banknote of 10000 abd coin of 200 ( (2+3) * 1000 + (5+7) * 200 )
    self.cash_inventory_group = self.cash_inventory_module.newContent(id='cash_inventory_group_2', portal_type='Cash Inventory Group', source_value=None, destination_value=self.paris, start_date = DateTime())
    # execute tic
    self.tic()
    # check we have only one cash inventory
    self.assertEqual(len(self.cash_inventory_module.objectValues()), 2)
    # get the cash inventory document
    self.cash_inventory = getattr(self.cash_inventory_module, 'cash_inventory_group_2')
    # check its portal type
    self.assertEqual(self.cash_inventory.getPortalType(), 'Cash Inventory Group')
    # check that its source is caisse_1
    self.assertEqual(self.cash_inventory.getSource(), None)
    # check that its destination is caisse_2
    self.assertEqual(self.cash_inventory.getDestination(), 'site/testsite/paris')


  def stepCreateCashInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a cash inventory document and check it
    """
    # Cash inventory has caisse_1 for source, caisse_2 for destination, and a price cooreponding to the sum of banknote of 10000 abd coin of 200 ( (2+3) * 1000 + (5+7) * 200 )
    self.cash_inventory = self.cash_inventory_group.newContent(id='cash_inventory', portal_type='Cash Inventory', price_currency='currency_module/EUR')
    # execute tic
    self.tic()
    # check we have only one cash inventory
    self.assertEqual(len(self.cash_inventory_group.objectValues()), 1)
    # get the cash inventory document
    self.cash_inventory = getattr(self.cash_inventory_group, 'cash_inventory')
    # check its portal type
    self.assertEqual(self.cash_inventory.getPortalType(), 'Cash Inventory')
    # check that its source is caisse_1
    self.assertEqual(self.cash_inventory.getSource(), None)
    # check that its destination is caisse_2
    self.assertEqual(self.cash_inventory.getDestination(), 'site/testsite/paris')


  def stepCreateInventoryLine1(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash inventory
    """
    # create the cash inventory
    self.addCashLineToDelivery(self.cash_inventory, 'valid_line_1', 'Cash Inventory Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/valid') + self.variation_list,
            self.quantity_10000)
    # execute tic
    self.tic()
    # check there is only one line created
    self.assertEqual(len(self.cash_inventory.objectValues()), 1)
    # get the cash inventory line
    self.valid_line_1 = getattr(self.cash_inventory, 'valid_line_1')
    # check its portal type
    self.assertEqual(self.valid_line_1.getPortalType(), 'Cash Inventory Line')
    # check the resource is banknotes of 10000
    self.assertEqual(self.valid_line_1.getResourceValue(), self.billet_10000)
    # chek the value of the banknote
    self.assertEqual(self.valid_line_1.getPrice(), 10000.0)
    # check the unit of banknote
    self.assertEqual(self.valid_line_1.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_line_1.objectValues()), 2)
    # now check for each variation (years 1992 and 2003)
    for variation in self.variation_list:
      # get the delivery cell
      cell = self.valid_line_1.getCell('emission_letter/p', variation, 'cash_status/valid')
      # chek portal types
      self.assertEqual(cell.getPortalType(), 'Cash Inventory Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      # check the source vault is caisse_1
      self.assertEqual(cell.getSourceValue(), None)
      # check the destination vault is caisse_2
      self.assertEqual(cell.getDestinationValue(), self.paris)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity of banknote for year 1992 is 2
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity of banknote for year 2003 is 3
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

  def stepCheckSubTotal1(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the amount after the creation of cash inventory line 1
    """
    # Check number of lines
    self.assertEqual(len(self.cash_inventory.objectValues()), 1)
    # Check quantity of banknotes (2 for 1992 and 3 for 2003)
    self.assertEqual(self.cash_inventory.getTotalQuantity(fast=0), 5.0)
    # Check the total price
    self.assertEqual(self.cash_inventory.getTotalPrice(fast=0), 10000 * 5.0)


  def stepCreateInventoryLine2(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash inventory line 2 wiht coins of 200 and check it has been well created
    """
    # create the line
    self.addCashLineToDelivery(self.cash_inventory, 'valid_line_2', 'Cash Inventory Line', self.piece_200,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/valid') + self.variation_list,
            self.quantity_200)
    # execute tic
    self.tic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.cash_inventory.objectValues()), 2)
    # get the second cash inventory line
    self.valid_line_2 = getattr(self.cash_inventory, 'valid_line_2')
    # check portal types
    self.assertEqual(self.valid_line_2.getPortalType(), 'Cash Inventory Line')
    # check the resource is coin of 200
    self.assertEqual(self.valid_line_2.getResourceValue(), self.piece_200)
    # check the value of coin
    self.assertEqual(self.valid_line_2.getPrice(), 200.0)
    # check the unit of coin
    self.assertEqual(self.valid_line_2.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_line_2.objectValues()), 2)
    for variation in self.variation_list:
      # get the delivery  cell
      cell = self.valid_line_2.getCell('emission_letter/p', variation, 'cash_status/valid')
      # check the portal type
      self.assertEqual(cell.getPortalType(), 'Cash Inventory Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.piece_200)
      # check the source vault is caisse_1
      self.assertEqual(cell.getSourceValue(), None)
      # check the destination vault is caisse_2
      self.assertEqual(cell.getDestinationValue(), self.paris)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity for coin for year 1992 is 5
        self.assertEqual(cell.getQuantity(), 5.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity for coin for year 2003 is 7
        self.assertEqual(cell.getQuantity(), 7.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepCheckSubTotal2(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the total after the creation of the two cash inventory lines
    """
    # Check number of lines (line1 + line2)
    self.assertEqual(len(self.cash_inventory.objectValues()), 2)
    # Check quantity, banknotes : 2 for 1992 and 3 for 2003, coin : 5 for 1992 and 7 for 2003
    self.assertEqual(self.cash_inventory.getTotalQuantity(fast=0), 5.0 + 12.0)
    # check the total price
    self.assertEqual(self.cash_inventory.getTotalPrice(fast=0), 10000 * 5.0 + 200 * 12.0)


  def stepCreateInventoryLine3(self, sequence=None, sequence_list=None, **kwd):
    """
    Create an invalid cash inventory line and
    check the total with the invalid cash inventory line
    """
    # create a line in which quanity of banknotes of 5000 is higher that quantity available at source
    # here create a line with 24 (11+13) banknotes of 500 although the vault caisse_1 has no banknote of 5000
    self.addCashLineToDelivery(self.cash_inventory, 'valid_line_3', 'Cash Inventory Line', self.billet_5000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/valid') + self.variation_list,
            self.quantity_5000)
    # execute tic
    self.tic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.cash_inventory.objectValues()), 3)
    # get the second cash inventory line
    self.valid_line_3 = getattr(self.cash_inventory, 'valid_line_3')
    # check portal types
    self.assertEqual(self.valid_line_3.getPortalType(), 'Cash Inventory Line')
    # check the resource is coin of 200
    self.assertEqual(self.valid_line_3.getResourceValue(), self.billet_5000)
    # check the value of coin
    self.assertEqual(self.valid_line_3.getPrice(), 5000.0)
    # check the unit of coin
    self.assertEqual(self.valid_line_3.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_line_3.objectValues()), 2)
    for variation in self.variation_list:
      # get the delivery  cell
      cell = self.valid_line_3.getCell('emission_letter/p', variation, 'cash_status/valid')
      # check the portal type
      self.assertEqual(cell.getPortalType(), 'Cash Inventory Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.billet_5000)
      # check the source vault is caisse_1
      self.assertEqual(cell.getSourceValue(), None)
      # check the destination vault is caisse_2
      self.assertEqual(cell.getDestinationValue(), self.paris)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity for coin for year 1992 is 5
        self.assertEqual(cell.getQuantity(), 11.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity for coin for year 2003 is 7
        self.assertEqual(cell.getQuantity(), 13.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepCheckTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the total after the creation of the two cash inventory lines
    """
    # Check number of lines (line1 + line2)
    self.assertEqual(len(self.cash_inventory.objectValues()), 3)
    # Check quantity, banknotes : 2 for 1992 and 3 for 2003, coin : 5 for 1992 and 7 for 2003
    self.assertEqual(self.cash_inventory.getTotalQuantity(fast=0), 5.0 + 12.0 + 24.0)
    # check the total price
    self.assertEqual(self.cash_inventory.getTotalPrice(fast=0), 10000 * 5.0 + 200 * 12.0 + 5000 * 24)


  def stepCheckInventoryDelivered(self, sequence=None, sequence_list=None, **kw):
    """
    Deliver the inventory
    """
    # get state of cash sorting
    state = self.cash_inventory_group.cash_inventory.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_inventory_group.cash_inventory, name='history', wf_id='inventory_workflow')
    # check len of len workflow history is 1
    self.assertEqual(len(workflow_history), 1)


  def stepCheckInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault caisse_2 is right after confirm and before deliver
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.paris.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.paris.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)

    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.paris.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.paris.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)

    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.paris.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.paris.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)

  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingCashInventory(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialInventory ' \
                    + 'CreateCashInventoryGroup CreateCashInventory ' \
                    + 'CreateInventoryLine1 CheckSubTotal1 ' \
                    + 'CreateInventoryLine2 CheckSubTotal2 ' \
                    + 'CreateInventoryLine3 CheckTotal ' \
                    + 'CheckInventoryDelivered Tic CheckInventory ' \
                    + 'CreateCashInventoryGroup2 CreateCashInventory ' \
                    + 'CreateInventoryLine1 CheckSubTotal1 ' \
                    + 'CreateInventoryLine2 CheckSubTotal2 ' \
                    + 'CreateInventoryLine3 CheckTotal ' \
                    + 'CheckInventoryDelivered Tic CheckInventory'

    sequence_list.addSequenceString(sequence_string)
    # play the sequence
    sequence_list.play(self)

