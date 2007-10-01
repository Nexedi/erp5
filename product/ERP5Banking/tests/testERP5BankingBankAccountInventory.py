##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
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
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.DCWorkflow.DCWorkflow import Unauthorized, ValidationFailed
from Testing.ZopeTestCase.PortalTestCase import PortalTestCase
from Products.ERP5Banking.tests.TestERP5BankingMixin import TestERP5BankingMixin
from DateTime import DateTime

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

# Define how to launch the script if we don't use runUnitTest script
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))



class TestERP5BankingInventory(TestERP5BankingMixin, ERP5TypeTestCase):
  """
    This class is a unit test to check the module of Bank Account Inventory
  """

  login = PortalTestCase.login
  RUN_ALL_TEST = 1
  QUIET = 0

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base',
            'erp5_trade',
            'erp5_accounting',
            'erp5_banking_core',
            'erp5_banking_inventory',)

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
    self.currency_1 = self.createCurrency()
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

  def stepCreateBankAccountInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a cash inventory document and check it
    """
    inventory = self.inventory_module.newContent(id='inventory_1',
                                                      portal_type='Bank Account Inventory',
                                                      source_value=None,
                                                      destination_value=self.site,
                                                      start_date = DateTime())
    self.assertNotEqual(inventory, None)
    
    self.stepTic()

    self.assertEqual(len(self.inventory_module.objectValues()), 1)
    self.inventory = getattr(self.inventory_module, 'inventory_1')
    self.assertEqual(self.inventory.getPortalType(), 'Bank Account Inventory')
    self.assertEqual(self.inventory.getSource(), None)
    self.assertEqual(self.inventory.getDestination(), 'site/testsite/paris')
    self.assertEqual(self.inventory.getSourcePayment(), None)
    self.assertEqual(self.inventory.getDestinationPayment(), None)

  def stepCreateBankAccountInventoryLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create an inventory line document and check it
    """
    inventory_line = self.inventory.newContent(id="line_1",
                                               portal_type='Bank Account Inventory Line',
                                               resource_value=self.currency_1,
                                               destination_payment_value=self.bank_account_1,
                                               quantity=50000)
    self.assertNotEqual(inventory_line, None)

    self.stepTic()
    
    self.assertEqual(len(self.inventory.objectValues()), 1)
    self.inventory_line = getattr(self.inventory, 'line_1')
    self.assertEqual(self.inventory_line.getPortalType(), 'Bank Account Inventory Line')
    self.assertEqual(self.inventory_line.getSource(), None)
    self.assertEqual(self.inventory_line.getDestination(), 'site/testsite/paris')
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
    if not run: return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckInitialInventory ' \
                    + 'CreateBankAccountInventory ' \
                    + 'CreateBankAccountInventoryLine ' \
                    + 'CheckFinalInventory'

    sequence_list.addSequenceString(sequence_string)
    # play the sequence
    sequence_list.play(self)


# define how we launch the unit test
if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestERP5BankingInventory))
    return suite
