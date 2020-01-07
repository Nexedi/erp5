##############################################################################
#
# Copyright (c) 2006-2010 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5Type.tests.Sequence import SequenceList
from erp5.component.test.testERP5BankingCheckbookVaultTransfer \
     import TestERP5BankingCheckbookVaultTransferMixin
from erp5.component.test.testERP5BankingCheckbookUsualCashTransfer \
     import TestERP5BankingCheckbookUsualCashTransferMixin
from erp5.component.test.testERP5BankingCheckbookDelivery \
     import TestERP5BankingCheckbookDeliveryMixin

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

class TestERP5BankingStopPayment( TestERP5BankingCheckbookDeliveryMixin,
                                  TestERP5BankingCheckbookUsualCashTransferMixin,
                                  TestERP5BankingCheckbookVaultTransferMixin):
  """
    This class is a unit test to check the module of Stop Payment
  """


  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet


  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingStopPayment"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    # Set some variables :

    TestERP5BankingCheckbookDeliveryMixin.afterSetUp(self)
    self.tic()
    self.createCheckbookDelivery()
    # the stop payment module
    self.stop_payment_module = self.getStopPaymentModule()



  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that StopPayment Module was created
    self.assertEqual(self.stop_payment_module.getPortalType(), 'Stop Payment Module')
    # check module is empty
    self.assertEqual(len(self.stop_payment_module.objectValues()), 0)


  def stepCheckInitialAndFinalCheckbookInventory(self, sequence=None, sequence_list=None, **kw):
    """
    Check initial account inventory.

    For this test, the intial inventory and the final inventory is the same
    """
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_2.getRelativeUrl(), resource=self.currency_1.getRelativeUrl()), 100000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_2.getRelativeUrl(), resource=self.currency_1.getRelativeUrl()), 100000)

  def stepCreateStopPayment(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a stop payment
    """
    # We will do the transfer ot two items.
    self.stop_payment = self.stop_payment_module.newContent(
                     id='stop_payment', portal_type='Stop Payment',
                     destination_payment_value=self.bank_account_2,
                     resource_value=self.currency_1,
                     description='test',
                     start_date=self.date,
                     reference_range_min='0000051',
                     aggregate_resource_value=self.check_model_1,
                     source_total_asset_price=20000)
    # set source reference
    self.setDocumentSourceReference(self.stop_payment)
    # check source reference
    self.assertNotEqual(self.stop_payment.getSourceReference(), '')
    self.assertNotEqual(self.stop_payment.getSourceReference(), None)
    # check its portal type
    self.assertEqual(self.stop_payment.getPortalType(), 'Stop Payment')
    # check source
    self.assertEqual(self.stop_payment.getBaobabSource(),
                     None)
    # check destination
    self.assertEqual(self.stop_payment.getBaobabDestination(), None)

  def stepCheckLineCreated(self, sequence=None, sequence_list=None, **kwd):
    """
    Make sure we have found the check corresponding to the
    reference and that a new line was created
    """
    line_list = self.stop_payment.objectValues(
                          portal_type='Checkbook Delivery Line')
    self.assertEqual(len(line_list), 1)
    line = line_list[0]
    self.assertEqual(line.getAggregateValue(), self.check_1)
    self.assertEqual(line.getQuantity(), 1)

  def stepSetStopPaymentDebit(self, sequence=None, sequence_list=None, **kwd):
    """
    Set the debit required
    """
    self.stop_payment.setDebitRequired(1)

  def stepDeleteStopPayment(self, sequence=None, sequence_list=None, **kwd):
    """
    Set the debit required
    """
    self.stop_payment_module.manage_delObjects(['stop_payment'])

  def stepConfirmStopPayment(self, sequence=None, sequence_list=None, **kw):
    """
    Confirm the stop payment
    """
    state = self.stop_payment.getSimulationState()
    # check that state is draft
    self.assertEqual(state, 'draft')
    self.workflow_tool.doActionFor(self.stop_payment,
                                   'confirm_action',
                                   wf_id='stop_payment_workflow')
    # get state of cash sorting
    state = self.stop_payment.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'confirmed')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.stop_payment,
                            name='history', wf_id='stop_payment_workflow')
    self.assertEqual(len(workflow_history), 3)

  def stepStartStopPayment(self, sequence=None, sequence_list=None, **kw):
    """
    Start the stop payment
    """
    state = self.stop_payment.getSimulationState()
    # check that state is draft
    self.assertEqual(state, 'confirmed')
    self.workflow_tool.doActionFor(self.stop_payment,
                                   'start_action',
                                   wf_id='stop_payment_workflow')
    # get state of cash sorting
    state = self.stop_payment.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'started')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.stop_payment,
                            name='history', wf_id='stop_payment_workflow')
    self.assertEqual(len(workflow_history), 5)

  def stepStopStopPayment(self, sequence=None, sequence_list=None, **kw):
    """
    Stop the stop payment
    """
    state = self.stop_payment.getSimulationState()
    # check that state is draft
    self.assertEqual(state, 'started')
    self.workflow_tool.doActionFor(self.stop_payment,
                                   'stop_action',
                                   wf_id='stop_payment_workflow')
    # get state of cash sorting
    state = self.stop_payment.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'stopped')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.stop_payment,
                            name='history', wf_id='stop_payment_workflow')
    self.assertEqual(len(workflow_history), 7)

  def stepDebitStopStopPayment(self, sequence=None, sequence_list=None, **kw):
    """
    Deliver the stop payment
    """
    state = self.stop_payment.getSimulationState()
    # check that state is draft
    self.assertEqual(state, 'started')
    self.workflow_tool.doActionFor(self.stop_payment,
                                   'debit_stop_action',
                                   wf_id='stop_payment_workflow',
                                   stop_date=self.stop_payment.getStartDate())
    # get state of cash sorting
    state = self.stop_payment.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'stopped')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.stop_payment,
                            name='history', wf_id='stop_payment_workflow')
    self.assertEqual(len(workflow_history), 7)

  def stepDeliverStopPayment(self, sequence=None, sequence_list=None, **kw):
    """
    Deliver the stop payment
    """
    state = self.stop_payment.getSimulationState()
    # check that state is draft
    self.assertEqual(state, 'stopped')
    self.workflow_tool.doActionFor(self.stop_payment,
                                   'deliver_action',
                                   wf_id='stop_payment_workflow')
    # get state of cash sorting
    state = self.stop_payment.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.stop_payment,
                            name='history', wf_id='stop_payment_workflow')
    self.assertEqual(len(workflow_history), 9)

  def stepDebitDeliverStopPayment(self, sequence=None, sequence_list=None, **kw):
    """
    Deliver the stop payment
    """
    state = self.stop_payment.getSimulationState()
    # check that state is draft
    self.assertEqual(state, 'stopped')
    self.workflow_tool.doActionFor(self.stop_payment,
                                   'debit_deliver_action',
                                   wf_id='stop_payment_workflow')
    # get state of cash sorting
    state = self.stop_payment.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.stop_payment,
                            name='history', wf_id='stop_payment_workflow')
    self.assertEqual(len(workflow_history), 9)

  def stepCheckConfirmedCheckbookInventory(self, sequence=None, sequence_list=None, **kw):
    """
    Check cash checkbook in item table
    """
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(
                     payment=self.bank_account_2.getRelativeUrl(),
                     resource=self.currency_1.getRelativeUrl()), 100000)
    self.assertEqual(self.simulation_tool.getAvailableInventory(
                     payment=self.bank_account_2.getRelativeUrl(),
                     resource=self.currency_1.getRelativeUrl()), 80000)
    self.assertEqual(self.simulation_tool.getFutureInventory(
                     payment=self.bank_account_2.getRelativeUrl(),
                     resource=self.currency_1.getRelativeUrl()), 80000)

  def stepCheckCheckIsStopped(self, sequence=None, sequence_list=None, **kw):
    """
    Check that the check is stopped
    """
    self.assertEqual(self.check_1.getSimulationState(), 'stopped')

  def stepCheckCheckIsConfirmed(self, sequence=None, sequence_list=None, **kw):
    """
    Check that the check is confirmed
    """
    self.assertEqual(self.check_1.getSimulationState(), 'confirmed')

  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingStopPayment(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()
    # define the sequence
    # Here we will debit the account
    sequence_string = 'Tic CheckObjects Tic CheckInitialAndFinalCheckbookInventory ' \
                    + 'CreateStopPayment Tic ' \
                    + 'SetStopPaymentDebit Tic ' \
                    + 'ConfirmStopPayment Tic ' \
                    + 'CheckLineCreated Tic ' \
                    + 'CheckConfirmedCheckbookInventory ' \
                    + 'StartStopPayment Tic ' \
                    + 'CheckCheckIsStopped Tic ' \
                    + 'DebitStopStopPayment Tic ' \
                    + 'DebitDeliverStopPayment Tic ' \
                    + 'CheckCheckIsConfirmed Tic ' \
                    + 'CheckInitialAndFinalCheckbookInventory '
    sequence_list.addSequenceString(sequence_string)
    # Here we will not debit the account
    sequence_string = 'DeleteStopPayment ' \
                    + 'Tic CheckObjects Tic CheckInitialAndFinalCheckbookInventory ' \
                    + 'CreateStopPayment Tic ' \
                    + 'ConfirmStopPayment Tic ' \
                    + 'CheckLineCreated Tic ' \
                    + 'CheckInitialAndFinalCheckbookInventory ' \
                    + 'StartStopPayment Tic ' \
                    + 'CheckCheckIsStopped Tic ' \
                    + 'StopStopPayment Tic ' \
                    + 'DeliverStopPayment Tic ' \
                    + 'CheckCheckIsConfirmed Tic ' \
                    + 'CheckInitialAndFinalCheckbookInventory '
    sequence_list.addSequenceString(sequence_string)
    # play the sequence
    sequence_list.play(self)

