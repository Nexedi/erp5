
##############################################################################
#
# Copyright (c) 2005-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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
from DateTime import DateTime
from Products.ERP5Type.tests.Sequence import SequenceList
from erp5.component.module.TestERP5BankingMixin import TestERP5BankingMixin

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

class TestERP5BankingAccountingCancellation(TestERP5BankingMixin):
  """
  Inside this test we will check that it is possible to cancel a transaction.
  """


  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet

  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingAccountingCancellation"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    self.initDefaultVariable()
    # the check payment module
    self.accounting_cancellation_module = self.getAccountingCancellationModule()

    # Create a user and login as manager to populate the erp5 portal with objects for tests.
    self.createManagerAndLogin()

    # Define static values (only use prime numbers to prevent confusions like 2 * 6 == 3 * 4)
    # variation list is the list of years for banknotes and coins
    self.variation_list = ('variation/1992', 'variation/2003')

    self.createFunctionGroupSiteCategory(site_list=['paris'])

    self.tic()
    # create a person and a bank account
    self.person_1 = self.createPerson(id='person_1',
                                      first_name='toto',
                                      last_name='titi')
    self.person_2 = self.createPerson(id='person_2',
                                      first_name='foo',
                                      last_name='bar')
    self.bank_account_1 = self.createBankAccount(person=self.person_1,
                                                 account_id='bank_account_1',
                                                 currency=self.currency_1,
                                                 amount=30000,
                                                 internal_bank_account_number="343434343434")
    self.bank_account_2 = self.createBankAccount(person=self.person_2,
                                                 account_id='bank_account_2',
                                                 currency=self.currency_1,
                                                 amount=80000,
                                                 internal_bank_account_number="343434343435")

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
    self.loginByUserName('super_user')

    # open counter date and counter
    self.openCounterDate(site=self.paris)

  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(
                     payment=self.bank_account_1.getRelativeUrl()), 30000)
    self.assertEqual(self.simulation_tool.getFutureInventory(
                     payment=self.bank_account_1.getRelativeUrl()), 30000)
    self.assertEqual(self.simulation_tool.getCurrentInventory(
                     payment=self.bank_account_2.getRelativeUrl()), 80000)
    self.assertEqual(self.simulation_tool.getFutureInventory(
                     payment=self.bank_account_2.getRelativeUrl()), 80000)


  def stepCreateAccountingCancellation(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a check payment document and check it
    """
    self.accounting_cancellation = self.accounting_cancellation_module.newContent(
                                   id = 'accounting_cancellation',
                                   portal_type = 'Accounting Cancellation',
                                   description = "test",
                                   # source_value = self.bi_counter,
                                   start_date = DateTime().Date(),
                                   source_total_asset_price = 20000.0)
    self.assertEqual(self.accounting_cancellation.getSourceTotalAssetPrice(), 20000.0)
    # set source reference
    self.setDocumentSourceReference(self.accounting_cancellation)
    # check source reference
    self.assertNotEqual(self.accounting_cancellation.getSourceReference(), '')
    self.assertNotEqual(self.accounting_cancellation.getSourceReference(), None)
    # the initial state must be draft
    self.assertEqual(self.accounting_cancellation.getSimulationState(), 'draft')

  def stepAddAccountingCancellationLine(self, sequence=None, sequence_list=None, **kw):
    """
    Create a line on internal account transfer
    """
    self.line_1 = self.accounting_cancellation.newContent(
                                    portal_type='Accounting Cancellation Line',
                                    id='line_1',
                                    source_payment_value=self.bank_account_1,
                                    destination_payment_value=self.bank_account_2,
                                    source_credit=-20000,
                                    )
    self.assertNotEqual(self.line_1, None)
    self.assertEqual(self.line_1.isCancellationAmount(), 1)

  def stepOrderAccountingCancellation(self, sequence=None, sequence_list=None, **kwd):
    self.workflow_tool.doActionFor(self.accounting_cancellation,
                      'order_action', wf_id='accounting_cancellation_workflow')
    self.assertEqual(self.accounting_cancellation.getSimulationState(), 'ordered')

  def stepDelAccountingCancellation(self, sequence=None, sequence_list=None, **kwd):
    """
    Delete the previous accounting cancellation
    """
    self.accounting_cancellation_module.deleteContent('accounting_cancellation')

  def stepCheckConfirmedInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the inventory in state confirmed
    """
    self.simulation_tool = self.getSimulationTool()
    # check the inventory of the bank account, must be planned to be decrease by 20000
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 30000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 50000)
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_2.getRelativeUrl()), 80000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_2.getRelativeUrl()), 60000)


  def stepConfirmAccountingCancellation(self, sequence=None, sequence_list=None, **kwd):
    self.workflow_tool.doActionFor(self.accounting_cancellation,
                    'confirm_action', wf_id='accounting_cancellation_workflow')
    self.assertEqual(self.accounting_cancellation.getSimulationState(), 'confirmed')

  def stepDeliverAccountingCancellation(self, sequence=None, sequence_list=None, **kwd):
    self.workflow_tool.doActionFor(self.accounting_cancellation,
                 'deliver_action', wf_id='accounting_cancellation_workflow')
    self.assertEqual(self.accounting_cancellation.getSimulationState(), 'delivered')


  def stepCheckFinalInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check the final inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 50000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 50000)
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_2.getRelativeUrl()), 60000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_2.getRelativeUrl()), 60000)

  def stepCleanup(self, sequence=None, sequence_list=None, **kwd):
    """
      Cleanup test remains
    """
    # Fetch all ids before deleting the objects, otherwise the iterator will
    # skip objects as the list dynamicaly shrinks.
    object_id_list = [x for x in self.accounting_cancellation_module.objectIds()]
    for id in object_id_list:
      self.accounting_cancellation_module.deleteContent(id)

  def test_01_ERP5BankingAccountingCancellation(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckInitialInventory ' \
                      'CreateAccountingCancellation Tic ' \
                      'AddAccountingCancellationLine Tic ' \
                      'OrderAccountingCancellation ' \
                      'ConfirmAccountingCancellation Tic ' \
                      'CheckConfirmedInventory Tic ' \
                      'DeliverAccountingCancellation Tic ' \
                      'CheckFinalInventory Tic'
    sequence_list.addSequenceString(sequence_string)
    # play the sequence
    sequence_list.play(self)

