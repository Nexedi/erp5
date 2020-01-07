
##############################################################################
#
# Copyright (c) 2007-2010 Nexedi SA and Contributors. All Rights Reserved.
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
    This class is a unit test to check the module of Bank Account Inventory
  """

  RUN_ALL_TEST = 1
  QUIET = 0

  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingBankAccountInventory"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    self.initDefaultVariable()
    self.inventory_module = self.getBankAccountInventoryModule()
    self.createManagerAndLogin()
    self.createFunctionGroupSiteCategory(no_site=1)
    self.currency_1 = self.currency_module['EUR']
    # Create a person and a bank account to test
    self.person_1 = self.createPerson(id='person_1',
                                      first_name='toto',
                                      last_name='titi')
    self.bank_account_1 = self.createBankAccount(person=self.person_1,
                                                 account_id='bank_account_1',
                                                 currency=self.currency_1,
                                                 amount=0,
                                                 internal_bank_account_number="343434343434")
    self.site = self.paris


  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # for bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(
      payment=self.bank_account_1.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(
      payment=self.bank_account_1.getRelativeUrl()), 0.0)
    # for agency
    self.assertEqual(self.simulation_tool.getCurrentInventory(
      payment=self.site.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(
      payment=self.site.getRelativeUrl()), 0.0)

  def stepCreateBankAccountInventoryGroup(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a cash inventory document and check it
    """
    inventory_group = self.inventory_module.newContent(id='inventory_group_1',
                                                 portal_type='Bank Account Inventory Group',
                                                 site_value=self.site,
                                                 start_date = DateTime())
    self.assertNotEqual(inventory_group, None)
    self.tic()

    self.assertEqual(len(self.inventory_module.objectValues()), 1)
    self.inventory_group = getattr(self.inventory_module, 'inventory_group_1')
    self.assertEqual(self.inventory_group.getPortalType(), 'Bank Account Inventory Group')
    self.assertEqual(self.inventory_group.getSource(), None)
    self.assertEqual(self.inventory_group.getDestination(), None)
    self.assertEqual(self.inventory_group.getSite(), 'testsite/paris')
    self.assertEqual(self.inventory_group.getSourcePayment(), None)
    self.assertEqual(self.inventory_group.getDestinationPayment(), None)

  def stepCreateBankAccountInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a cash inventory document and check it
    """

    inventory = self.inventory_group.newContent(id='inventory_1',
                                                portal_type='Bank Account Inventory',
                                                destination_payment_value=self.bank_account_1,
                                                )
    self.assertNotEqual(inventory, None)
    self.tic()
    self.assertEqual(len(self.inventory_group.objectValues()), 1)
    self.inventory = getattr(self.inventory_group, 'inventory_1')
    self.assertEqual(self.inventory.getPortalType(), 'Bank Account Inventory')
    self.assertEqual(self.inventory.getSource(), "account_module/bank_account")
    self.assertEqual(self.inventory.getDestination(), "account_module/bank_account")
    self.assertEqual(self.inventory.getSourcePayment(), None)
    self.assertEqual(self.inventory.getDestinationPayment(), self.bank_account_1.getRelativeUrl())


  def stepCreateBankAccountInventoryLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create an inventory line document and check it
    """
    inventory_line = self.inventory.newContent(id="line_1",
                                               portal_type='Bank Account Inventory Line',
                                               resource_value=self.currency_1,
                                               quantity=50000)
    self.assertNotEqual(inventory_line, None)

    self.tic()

    self.assertEqual(len(self.inventory.objectValues()), 1)
    self.inventory_line = getattr(self.inventory, 'line_1')
    self.assertEqual(self.inventory_line.getPortalType(), 'Bank Account Inventory Line')
    self.assertEqual(self.inventory.getSource(), "account_module/bank_account")
    self.assertEqual(self.inventory.getDestination(), "account_module/bank_account")
    self.assertEqual(self.inventory_line.getSourcePayment(), None)
    self.assertEqual(self.inventory_line.getDestinationPayment(), self.bank_account_1.getRelativeUrl())
    self.assertEqual(self.inventory_line.getQuantity(), 50000)

  def stepCheckFinalInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check Final Inventory
    """
    self.simulation_tool = self.getSimulationTool()
    # for bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(
      payment=self.bank_account_1.getRelativeUrl()), 50000.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(
      payment=self.bank_account_1.getRelativeUrl()), 50000.0)
    # for agency
    self.assertEqual(self.simulation_tool.getCurrentInventory(
      payment=self.site.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(
      payment=self.site.getRelativeUrl()), 0.0)


  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingBankAccountInventory(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckInitialInventory ' \
                      + 'CreateBankAccountInventoryGroup ' \
                      + 'CreateBankAccountInventory ' \
                      + 'CreateBankAccountInventoryLine ' \
                      + 'CheckFinalInventory'

    sequence_list.addSequenceString(sequence_string)
    # play the sequence
    sequence_list.play(self)


