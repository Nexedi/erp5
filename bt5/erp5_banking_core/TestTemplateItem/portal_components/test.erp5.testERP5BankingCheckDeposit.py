##############################################################################
#
# Copyright (c) 2005-2010 Nexedi SA and Contributors. All Rights Reserved.
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
from DateTime import DateTime
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from erp5.component.module.TestERP5BankingMixin import TestERP5BankingMixin

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

class TestERP5BankingCheckDeposit(TestERP5BankingMixin):
  """
  Unit test class for the check deposit module
  """


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
    # Set some variables :
    self.initDefaultVariable()

    self.check_deposit_module = self.getCheckDepositModule()

    self.createManagerAndLogin()
    # create categories
    self.createFunctionGroupSiteCategory(site_list=['paris'])
    # define the user, a site is needed for accouting event
    self.checkUserFolderType()
    self.organisation = self.organisation_module.newContent(id='baobab_org', portal_type='Organisation',
                                                            function='banking', group='baobab',  site='testsite/paris', role='internal')
    user_dict = {
      'super_user' : [['Manager'], self.organisation, 'banking/comptable', 'baobab', 'testsite/paris/surface/banque_interne/guichet_1']
      }
    # call method to create this user
    self.createERP5Users(user_dict)
    self.logout()
    self.loginByUserName('super_user')
    # create a person with a bank account
    self.person_1 = self.createPerson(id='person_1',
                                      first_name='toto',
                                      last_name='titi',
                                      site='testsite/paris')
    self.bank_account_1 = self.createBankAccount(person=self.person_1,
                                                 account_id='bank_account_1',
                                                 reference = 'bank_account_1',
                                                 currency=self.currency_1,
                                                 amount=100000,
                                                 bic_code='',
                                                 swift_registered=0,
                                                 internal_bank_account_number="343434343434")
    # create a second person with a bank account
    self.person_2 = self.createPerson(id='person_2',
                                      first_name='foo',
                                      last_name='bar',
                                      site='testsite/paris')
    self.bank_account_2 = self.createBankAccount(person=self.person_2,
                                                 account_id='bank_account_2',
                                                 reference = 'bank_account_2',
                                                 currency=self.currency_1,
                                                 amount=50000,
                                                 bic_code='',
                                                 swift_registered=0,
                                                 overdraft_facility=1,
                                                 internal_bank_account_number="878787878787")
    # create a bank account for the organisation
    self.bank_account_3 = self.createBankAccount(person=self.organisation,
                                                 account_id='bank_account_3',
                                                 reference = 'bank_account_3',
                                                 currency=self.currency_1,
                                                 amount=50000,
                                                 bic_code='BICAGENCPARIS',
                                                 swift_registered=1,
                                                 internal_bank_account_number="121212121212")

    # the checkbook module
    self.checkbook_module = self.getCheckbookModule()
    self.createCheckAndCheckbookModel()
    # create a check
    self.checkbook_1 = self.createCheckbook(id= 'checkbook_1',
                                            vault=self.testsite.paris,
                                            bank_account=self.bank_account_2,
                                            min='0000050',
                                            max='0000100',
                                            )

    self.check_1 = self.createCheck(id='check_1',
                                    reference='CHKNB1',
                                    resource_value=self.check_model,
                                    checkbook=self.checkbook_1)
    self.check_2 = self.createCheck(id='check_2',
                                    reference='CHKNB2',
                                    resource_value=self.check_model,
                                    checkbook=self.checkbook_1)

    self.openCounterDate(site=self.testsite.paris)
    self.openAccountingDate(site=self.testsite.paris)


  def stepLogout(self, sequence=None, sequence_list=None, **kwd):
    self.logout()

  def stepLoginAsSuperUser(self, sequence=None, sequence_list=None, **kwd):
    self.loginByUserName('super_user')

  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 100000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 100000)
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_2.getRelativeUrl()), 50000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_2.getRelativeUrl()), 50000)

  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    self.assertEqual(self.check_deposit_module.getPortalType(),
                     'Check Deposit Module')
    self.assertEqual(len(self.check_deposit_module.objectValues()), 0)

  def stepCreateCheckDepositOperation(self, sequence=None, sequence_list=None, **kw):
    """
    Create a first check deposite that used a ban account which has no bic code
    """

    self.check_deposit = self.check_deposit_module.newContent(id = 'check_deposit',
                                                              portal_type = 'Check Deposit',
                                                              destination_payment_value = self.bank_account_1,
                                                              start_date = DateTime().Date(),
                                                              source_total_asset_price = 2000.0,
                                                              resource_value=self.currency_1,
                                                              external_software_value=None)
    self.assertNotEqual(self.check_deposit, None)
    self.assertEqual(self.check_deposit.getTotalPrice(fast=0), 0.0)
    self.assertEqual(self.check_deposit.getDestinationPayment(), self.bank_account_1.getRelativeUrl())
    self.assertEqual(self.check_deposit.getSourceTotalAssetPrice(), 2000.0)
    # the initial state must be draft
    self.assertEqual(self.check_deposit.getSimulationState(), 'draft')
    # set source reference
    self.setDocumentSourceReference(self.check_deposit)
    # check source reference
    self.assertNotEqual(self.check_deposit.getSourceReference(), '')
    self.assertNotEqual(self.check_deposit.getSourceReference(), None)

  def stepSetCheckLess(self, sequence=None, sequence_list=None, **kwd):
    """
      Make CheckDeposit check-less.
    """
    self.check_deposit.setCheckLess(True)

  def stepAddCheckOperationLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Add a check to the check deposit
    """
    self.check_operation_line_1 = self.check_deposit.newContent(
        id='check_operation_line_1',
        portal_type="Check Operation Line",
        aggregate_free_text="CHKNB1",
        aggregate_resource=self.check_model.getRelativeUrl(),
        source_payment_value = self.bank_account_2,
        price=2000,
        quantity=1,
        description='aa',
        quantity_unit_value=self.unit)
    self.assertNotEqual(self.check_operation_line_1, None)
    self.assertEqual(len(self.check_deposit.objectIds()), 1)

  def stepAddCheckOperationLineWithNoAggregate(self, sequence=None, sequence_list=None, **kwd):
    """
    Add a check to the check deposit
    """
    self.check_operation_line_1 = self.check_deposit.newContent(
        id='check_operation_line_1',
        portal_type="Check Operation Line",
        source_payment_value = self.bank_account_2,
        price=2000,
        quantity=1,
        description='aa',
        quantity_unit_value=self.unit)
    self.assertNotEqual(self.check_operation_line_1, None)
    self.assertEqual(len(self.check_deposit.objectIds()), 1)

  def stepAddSecondCheckOperationLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Add a check to the check deposit
    """
    self.check_operation_line_2 = self.check_deposit.newContent(
        id='check_operation_line_2',
        portal_type="Check Operation Line",
        aggregate_free_text="CHKNB2",
        aggregate_resource=self.check_model.getRelativeUrl(),
        source_payment_value = self.bank_account_2,
        price=50000,
        quantity=1,
        description='aa',
        quantity_unit_value=self.unit)
    self.assertNotEqual(self.check_operation_line_2, None)
    self.assertEqual(len(self.check_deposit.objectIds()), 2)


  def stepModifyCheckOperationAmount(self, sequence=None, sequence_list=None, **kwd):
    """
    Set amount for the two lines
    """
    self.check_deposit.edit(source_total_asset_price=52000)


  def stepModifyCheckOperationLineAmount(self, sequence=None, sequence_list=None, **kwd):
    """
    Set amount for the two lines
    """
    self.check_deposit.edit(source_total_asset_price=12000)
    self.check_operation_line_2.edit(price=10000)


  def stepAddWrongCheckOperationLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Add a check to the check deposit, check number is not defined into site
    so transition must failed
    """
    self.check_operation_line_2 = self.check_deposit.newContent(
          id='check_operation_line_1',
          portal_type="Check Operation Line",
          aggregate_free_text="CHKNB6",
          aggregate_resource=self.check_model.getRelativeUrl(),
          source_payment_value = self.bank_account_2,
          price=2000,
          quantity=1,
          description='aa',
          quantity_unit_value=self.unit)
    self.assertNotEqual(self.check_operation_line_1, None)
    self.assertEqual(len(self.check_deposit.objectIds()), 1)


  def stepPlanCheckDepositOperation(self, sequence=None, sequence_list=None, **kwd):
    """
    Send the check deposit document to first validation level
    """
    self.assertEqual(self.check_deposit.getTotalPrice(fast=0, portal_type="Check Operation Line"), 2000.0)
    self.workflow_tool.doActionFor(self.check_deposit, 'plan_action', wf_id='check_deposit_workflow')
    self.assertEqual(self.check_deposit.getSimulationState(), 'planned')
    self.assertEqual(len(self.check_deposit.contentValues(filter = {'portal_type' : 'Incoming Check Deposit Line'})), 1)
    self.assertEqual(len(self.check_deposit.contentValues(filter = {'portal_type' : 'Outgoing Check Deposit Line'})), 1)

  def stepTryPlanCheckDepositOperation(self, sequence=None, sequence_list=None, **kwd):
    """
    Send the check deposit document to first validation level
    """
    self.assertEqual(self.check_deposit.getTotalPrice(fast=0, portal_type="Check Operation Line"), 2000.0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.check_deposit, 'plan_action', wf_id='check_deposit_workflow')
    #self.workflow_tool.doActionFor(self.check_deposit, 'plan_action', wf_id='check_deposit_workflow')
    self.assertEqual(self.check_deposit.getSimulationState(), 'draft')

  def stepTrySecondPlanCheckDepositOperation(self, sequence=None, sequence_list=None, **kwd):
    """
    Send the check deposit document to first validation level
    """
    self.assertEqual(self.check_deposit.getTotalPrice(fast=0, portal_type="Check Operation Line"), 52000.0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.check_deposit, 'plan_action', wf_id='check_deposit_workflow')
    #self.workflow_tool.doActionFor(self.check_deposit, 'plan_action', wf_id='check_deposit_workflow')
    self.assertEqual(self.check_deposit.getSimulationState(), 'draft')

  def stepTrySecondPlanCheckDepositOperationWithAggregate(self, sequence=None, sequence_list=None, **kwd):
    """
    Send the check deposit document to first validation level
    """
    self.assertEqual(self.check_deposit.getTotalPrice(fast=0, portal_type="Check Operation Line"), 2000.0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.check_deposit, 'plan_action', wf_id='check_deposit_workflow')
    #self.workflow_tool.doActionFor(self.check_deposit, 'plan_action', wf_id='check_deposit_workflow')
    self.assertEqual(self.check_deposit.getSimulationState(), 'draft')

  def stepSecondPlanCheckDepositOperation(self, sequence=None, sequence_list=None, **kwd):
    """
    Send the check deposit document to first validation level
    """
    self.assertEqual(self.check_deposit.getTotalPrice(fast=0, portal_type="Check Operation Line"), 12000.0)
    self.workflow_tool.doActionFor(self.check_deposit, 'plan_action', wf_id='check_deposit_workflow')
    self.assertEqual(self.check_deposit.getSimulationState(), 'planned')
    self.assertEqual(len(self.check_deposit.contentValues(filter = {'portal_type' : 'Incoming Check Deposit Line'})), 1)
    self.assertEqual(len(self.check_deposit.contentValues(filter = {'portal_type' : 'Outgoing Check Deposit Line'})), 2)


  def stepSendCheckDepositOperationToManualValidation(self, sequence=None, sequence_list=None, **kwd):
    """
    Send to manual validation
    """
    self.workflow_tool.doActionFor(self.check_deposit, 'wait_action', wf_id='check_deposit_workflow')
    self.assertEqual(self.check_deposit.getSimulationState(), 'waiting')

  def stepAcceptCheckDepositOperation(self, sequence=None, sequence_list=None, **kwd):
    """
    Accept manual validation
    """
    self.workflow_tool.doActionFor(self.check_deposit, 'accept_action', wf_id='check_deposit_workflow')
    self.assertEqual(self.check_deposit.getSimulationState(), 'planned')


  def stepOrderCheckDepositOperation(self, sequence=None, sequence_list=None, **kwd):
    """
    Send the check deposit document to second validation level
    """
    self.workflow_tool.doActionFor(self.check_deposit, 'order_action', wf_id='check_deposit_workflow')
    self.assertEqual(self.check_deposit.getSimulationState(), 'ordered')

  def stepDeliverCheckDepositOperation(self, sequence=None, sequence_list=None, **kwd):
    """
    Deliver the check deposit
    """
    self.workflow_tool.doActionFor(self.check_deposit, 'deliver_action', wf_id='check_deposit_workflow')
    self.assertEqual(self.check_deposit.getSimulationState(), 'delivered')

  def stepRejectCheckDepositOperation(self, sequence=None, sequence_list=None, **kwd):
    """
    Cancel the check deposit
    """
    self.workflow_tool.doActionFor(self.check_deposit, 'reject_action', wf_id='check_deposit_workflow')
    self.assertEqual(self.check_deposit.getSimulationState(), 'draft')

  def stepCheckBankAccountInventoryAfterCheckDepositDelivered(self, sequence=None, sequence_list=None, **kw):
    """
    Check inventory of the bank account changed after validation of operation
    """
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 102000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 102000)
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_2.getRelativeUrl()), 48000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_2.getRelativeUrl()), 48000)

  def stepCheckSecondBankAccountInventoryAfterCheckDepositDelivered(self, sequence=None, sequence_list=None, **kw):
    """
    Check inventory of the bank account changed after validation of operation
    """
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 112000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 112000)
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_2.getRelativeUrl()), 38000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_2.getRelativeUrl()), 38000)


  def stepCheckThirdBankAccountInventoryAfterCheckDepositDelivered(self, sequence=None, sequence_list=None, **kw):
    """
    Check inventory of the bank account changed after validation of operation
    """
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 152000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 152000)
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_2.getRelativeUrl()), -2000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_2.getRelativeUrl()), -2000)


  def stepCheckBankAccountInventoryAfterCheckDepositRejected(self, sequence=None, sequence_list=None, **kw):
    """
    Check inventory of the bank account doesn't changed after reject of operation
    """
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 100000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 100000)
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_2.getRelativeUrl()), 50000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_2.getRelativeUrl()), 50000)

  def stepClearCheck(self, sequence=None, sequence_list=None, **kw):
    """
    Remove previous check and create a new one with same reference,
    like this we make sure the workflow history is empty
    """
    self.checkbook_1.manage_delObjects([self.check_1.getId(), ])
    self.check_1 = self.createCheck(id='check_1',
                                    reference='CHKNB1',
                                    resource_value=self.check_model,
                                    checkbook=self.checkbook_1)
    self.checkbook_1.manage_delObjects([self.check_2.getId()])
    self.check_2 = self.createCheck(id='check_2',
                                    reference='CHKNB2',
                                    resource_value=self.check_model,
                                    checkbook=self.checkbook_1)


  def stepClearCheckDepositModule(self, sequence=None, sequence_list=None, **kw):
    """
    Clear the check deposit module
    """
    if hasattr(self, 'check_deposit'):
      self.check_deposit_module.manage_delObjects([self.check_deposit.getId()])

  def test_01_ERP5BankingCheckDeposit(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string1 = 'Tic CheckObjects Tic CheckInitialInventory ' \
                       + 'CreateCheckDepositOperation Tic ' \
                       + 'AddCheckOperationLine Tic ' \
                       + 'PlanCheckDepositOperation Tic ' \
                       + 'OrderCheckDepositOperation Tic ' \
                       + 'Tic DeliverCheckDepositOperation Tic ' \
                       + 'CheckBankAccountInventoryAfterCheckDepositDelivered'
    # one to test reject
    sequence_string2 = 'Tic ClearCheck ClearCheckDepositModule Tic '\
                       + 'CheckObjects Tic CheckInitialInventory ' \
                       + 'CreateCheckDepositOperation Tic ' \
                       + 'AddCheckOperationLine Tic ' \
                       + 'PlanCheckDepositOperation Tic OrderCheckDepositOperation ' \
                       + 'Tic RejectCheckDepositOperation Tic ' \
                       + 'CheckBankAccountInventoryAfterCheckDepositRejected'
    # one to test check not defined
    sequence_string3 =  'Tic ClearCheck ClearCheckDepositModule Tic '\
                       + 'Tic CheckObjects Tic CheckInitialInventory ' \
                       + 'CreateCheckDepositOperation Tic ' \
                       + 'AddWrongCheckOperationLine Tic ' \
                       + 'TryPlanCheckDepositOperation Tic ' \
                       + 'CheckInitialInventory'


    # same account on line
    sequence_string4 = 'Tic ClearCheck ClearCheckDepositModule Tic '\
                       + 'Tic CheckObjects Tic CheckInitialInventory ' \
                       + 'CreateCheckDepositOperation Tic ' \
                       + 'AddCheckOperationLine Tic ' \
                       + 'AddSecondCheckOperationLine Tic ' \
                       + 'ModifyCheckOperationAmount Tic ' \
                       + 'TrySecondPlanCheckDepositOperation Tic ' \
                       + 'ModifyCheckOperationLineAmount Tic ' \
                       + 'SecondPlanCheckDepositOperation Tic ' \
                       + 'OrderCheckDepositOperation Tic ' \
                       + 'Tic DeliverCheckDepositOperation Tic ' \
                       + 'CheckSecondBankAccountInventoryAfterCheckDepositDelivered'

    # test manual validation
    sequence_string5 = 'Tic ClearCheck ClearCheckDepositModule Tic '\
                       + 'Tic CheckObjects Tic CheckInitialInventory ' \
                       + 'CreateCheckDepositOperation Tic ' \
                       + 'AddCheckOperationLine Tic ' \
                       + 'AddSecondCheckOperationLine Tic ' \
                       + 'ModifyCheckOperationAmount Tic ' \
                       + 'TrySecondPlanCheckDepositOperation Tic ' \
                       + 'SendCheckDepositOperationToManualValidation Tic ' \
                       + 'AcceptCheckDepositOperation Tic ' \
                       + 'OrderCheckDepositOperation Tic ' \
                       + 'Tic DeliverCheckDepositOperation Tic ' \
                       + 'CheckThirdBankAccountInventoryAfterCheckDepositDelivered'

    # test transfer with no check refuses lines with aggregate
    sequence_string6 = 'Tic ClearCheck ClearCheckDepositModule Tic '\
                       + 'Tic CheckInitialInventory ' \
                       + 'CreateCheckDepositOperation SetCheckLess Tic ' \
                       + 'AddCheckOperationLine Tic ' \
                       + 'TrySecondPlanCheckDepositOperationWithAggregate'

    # test transfer with no check
    sequence_string7 = 'Tic ClearCheck ClearCheckDepositModule Tic '\
                       + 'Tic CheckInitialInventory ' \
                       + 'CreateCheckDepositOperation SetCheckLess Tic ' \
                       + 'AddCheckOperationLineWithNoAggregate Tic ' \
                       + 'PlanCheckDepositOperation Tic ' \
                       + 'OrderCheckDepositOperation Tic ' \
                       + 'DeliverCheckDepositOperation Tic ' \
                       + 'CheckBankAccountInventoryAfterCheckDepositDelivered'

    sequence_list.addSequenceString(sequence_string1)
    sequence_list.addSequenceString(sequence_string2)
    sequence_list.addSequenceString(sequence_string3)
    sequence_list.addSequenceString(sequence_string4)
    sequence_list.addSequenceString(sequence_string5)
    sequence_list.addSequenceString(sequence_string6)
    sequence_list.addSequenceString(sequence_string7)
    # play the sequence
    sequence_list.play(self)

