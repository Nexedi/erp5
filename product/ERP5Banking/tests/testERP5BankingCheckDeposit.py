##############################################################################
#
# Copyright (c) 2005-2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
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
from zLOG import LOG
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.DCWorkflow.DCWorkflow import Unauthorized, ValidationFailed
from Testing.ZopeTestCase.PortalTestCase import PortalTestCase
from Products.ERP5Banking.tests.TestERP5BankingMixin import TestERP5BankingMixin

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

# Define how to launch the script if we don't use runUnitTest script
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))


class TestERP5BankingCheckDeposit(TestERP5BankingMixin, ERP5TypeTestCase):
  """
  Unit test class for the check deposit module
  """
  
  login = PortalTestCase.login

  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet


  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingCheckDeposit"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    self.initDefaultVariable()
    # the check deposit module
    self.check_deposit_module = self.getCheckDepositModule()
    # the checkbook module
    self.checkbook_module = self.getCheckbookModule()

    # Create a user and login as manager to populate the erp5 portal with objects for tests.
    self.createManagerAndLogin()
    self.currency_1 = self.createCurrency()
    self.createFunctionGroupSiteCategory()

    # create a person and a bank account
    self.person_1 = self.createPerson(id='person_1',
                                      first_name='toto',
                                      last_name='titi')
    self.bank_account_1 = self.createBankAccount(person=self.person_1,
                                                 account_id='bank_account_1',
                                                 currency=self.currency_1,
                                                 amount=0) 

    

    # create a second person who will be used as agent for the check
    self.person_2 = self.createPerson(id='person_2',
                                      first_name='foo',
                                      last_name='bar')
    self.bank_account_2 = self.createBankAccount(person=self.person_2,
                                                 account_id='bank_account_2',
                                                 currency=self.currency_1,
                                                 amount=1000) 

    # create a check for this person
    self.checkbook_1 = self.createCheckbook(id= 'checkbook_1',
                                            vault=self.paris,
                                            bank_account=self.bank_account_2,
                                            min=250,
                                            max=300,                                            
                                            )

    self.check_1 = self.createCheck(id='check_1',
                                    reference='250',
                                    checkbook=self.checkbook_1)

    self.check_2 = self.createCheck(id='check_2',
                                    reference='251',
                                    checkbook=self.checkbook_1)
    


    # now we need to create a user as Manager to do the test
    # in order to have an assigment defined which is used to do transition
    # Create an Organisation that will be used for users assignment
    self.checkUserFolderType()
    self.organisation = self.organisation_module.newContent(id='baobab_org', portal_type='Organisation',
                          function='banking', group='baobab',  site='testsite/paris')
    # define the user
    user_dict = {
        'super_user' : [['Manager'], self.organisation, 'banking/comptable', 'baobab', 'testsite/paris']
      }
    # call method to create this user
    self.createERP5Users(user_dict)
    self.logout()
    self.login('super_user')


  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    # check that Check Deposit Module was created
    self.assertEqual(self.check_deposit_module.getPortalType(), 'Check Deposit Module')
    # check check deposit module is empty
    self.assertEqual(len(self.check_deposit_module.objectValues()), 0)


  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 0)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 0)

    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_2.getRelativeUrl()), 1000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_2.getRelativeUrl()), 1000)


  def stepCreateCheckDeposit(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a check deposit document and check it
    """
    self.check_deposit = self.check_deposit_module.newContent(
                                id = 'check_deposit',
                                portal_type = 'Check Deposit',
                                destination_payment_value = self.bank_account_1,
                                start_date = DateTime().Date(),
                                source_total_asset_price = 500.0,
                                description='test',
                                resource_value=self.currency_1)
    
    self.assertNotEqual(self.check_deposit, None)
    self.assertEqual(self.check_deposit.getTotalPrice(), 0.0)
    self.assertEqual(self.check_deposit.getDestinationPayment(), self.bank_account_1.getRelativeUrl())
    self.assertEqual(self.check_deposit.getSourceTotalAssetPrice(), 500.0)
    # the initial state must be draft
    self.assertEqual(self.check_deposit.getSimulationState(), 'draft')
    # set source reference
    self.setDocumentSourceReference(self.check_deposit)
    # check source reference
    self.assertNotEqual(self.check_deposit.getSourceReference(), '')
    self.assertNotEqual(self.check_deposit.getSourceReference(), None)

  def stepAddCheckOperationLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Add Check to the check deposit
    """
    self.check_operation_line_1 = self.check_deposit.newContent(id='check_operation_line_1',
                                                                portal_type="Check Operation Line",
                                                                aggregate_free_text="250",
                                                                source_payment_value = self.bank_account_2,
                                                                price=500,
                                                                quantity=1,
                                                                quantity_unit_value=self.unit)
    self.assertNotEqual(self.check_operation_line_1, None)
    self.assertEqual(len(self.check_deposit.objectIds()), 1)
    

  def stepCheckConsistency(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the consistency of the check deposit

    FIXME: check if the transition fails when a category or property is invalid.
    """
    self.assertEqual(self.check_deposit.getTotalPrice(portal_type="Check Operation Line"), 500.0)
    self.workflow_tool.doActionFor(self.check_deposit, 'plan_action', wf_id='check_deposit_workflow')
    self.assertEqual(self.check_deposit.getSimulationState(), 'planned')


  def stepRequestBalance(self, sequence=None, sequence_list=None, **kwd):
    """
    Request balance verification for the check deposit

    FIXME: check if the transition fails when a category or property is invalid.
    """
    self.workflow_tool.doActionFor(self.check_deposit, 'order_action', wf_id='check_deposit_workflow')
    self.assertEqual(self.check_deposit.getSimulationState(), 'ordered')


  def stepCheckOrderedInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the inventory at state ordered
    """
    # bank account 1 is planned to be increased by 500
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 0)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 500)
    # bank account 1 is planned to be decreased by 500
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_2.getRelativeUrl()), 1000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_2.getRelativeUrl()), 500)


  def stepPay(self, sequence=None, sequence_list=None, **kwd):
    """
    Pay the check deposit

    FIXME: check if the transition fails when a category or property is invalid.
    """
    self.workflow_tool.doActionFor(self.check_deposit, 'deliver_action', wf_id='check_deposit_workflow')
    self.assertEqual(self.check_deposit.getSimulationState(), 'delivered')


  def stepCheckFinalInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 500)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 500)

    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_2.getRelativeUrl()), 500)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_2.getRelativeUrl()), 500)


  def test_01_ERP5BankingCheckDeposit(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run: return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialInventory ' \
                      'CreateCheckDeposit Tic AddCheckOperationLine Tic ' \
                      'CheckConsistency Tic ' \
                      'RequestBalance Tic ' \
                      'CheckOrderedInventory ' \
                      'Pay Tic ' \
                      'CheckFinalInventory'
    
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
    suite.addTest(unittest.makeSuite(TestERP5BankingCheckDeposit))
    return suite
