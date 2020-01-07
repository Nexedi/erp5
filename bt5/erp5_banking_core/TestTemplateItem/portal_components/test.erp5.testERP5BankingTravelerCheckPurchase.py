
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
from erp5.component.test.testERP5BankingCheckbookUsualCashTransfer \
     import TestERP5BankingCheckbookUsualCashTransferMixin
from erp5.component.test.testERP5BankingTravelerCheckSale \
     import TestERP5BankingTravelerCheckSaleMixin

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

class TestERP5BankingTravelerCheckPurchase(TestERP5BankingCheckbookUsualCashTransferMixin,
                                       TestERP5BankingTravelerCheckSaleMixin):
  """
    This class is a unit test to check the module of Cash Transfer

    Here are the following step that will be done in the test :

  """


  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet


  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingTravelerCheckPurchase"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    # Set some variables :

    TestERP5BankingTravelerCheckSaleMixin.afterSetUp(self)
    self.tic()
    self.stepCreateTravelerCheckSale()
    self.stepCreateTravelerCheckLineList()
    self.stepDeliverTravelerCheckSale()
    self.traveler_check_purchase_module = self.getTravelerCheckPurchaseModule()

  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that TravelerCheckPurchase Module was created
    self.assertEqual(self.traveler_check_purchase_module.getPortalType(), 'Traveler Check Purchase Module')
    # check module is empty
    self.assertEqual(len(self.traveler_check_purchase_module.objectValues()), 0)


  def stepCheckInitialCheckbookInventory(self, sequence=None, sequence_list=None, **kw):
    """
    Check initial cash checkbook on source
    """
    self.assertEqual(len(self.simulation_tool.getCurrentTrackingList(
                     node=self.traveler_check_source.getRelativeUrl(),
                     at_date=self.date)), 0)
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(
                     node=self.traveler_check_source.getRelativeUrl(),
                     at_date=self.date)), 0)
    checkbook_list = self.simulation_tool.getCurrentTrackingList(
                             node=self.traveler_check_source.getRelativeUrl(),
                             at_date=self.date)
    self.assertEqual(len(checkbook_list), 0)
    # check we have cash checkbook 1
    checkbook_object_list = [x.getObject() for x in checkbook_list]
    self.failIfDifferentSet(checkbook_object_list, [])
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(
                   payment=self.bank_account_1.getRelativeUrl(),
                   resource=self.currency_1.getRelativeUrl()), 67500)
    self.assertEqual(self.simulation_tool.getFutureInventory(
                   payment=self.bank_account_1.getRelativeUrl(),
                   resource=self.currency_1.getRelativeUrl()), 67500)

  def stepCreateTravelerCheckPurchase(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a traveler check purchase
    """
    # We will do the transfer ot two items.
    self.traveler_check_purchase = self.traveler_check_purchase_module.newContent(
                     id='traveler_check_purchase', portal_type='Traveler Check Purchase',
                     source_value=self.traveler_check_source, destination_value=None,
                     destination_payment_value=self.bank_account_1,
                     resource_value=self.currency_1,
                     description='test',
                     start_date=self.date)
    # check its portal type
    self.assertEqual(self.traveler_check_purchase.getPortalType(), 'Traveler Check Purchase')
    # check source
    self.assertEqual(self.traveler_check_purchase.getBaobabSource(), None)
    # check destination
    self.assertEqual(self.traveler_check_purchase.getBaobabDestination(), None)
    self.setDocumentSourceReference(self.traveler_check_purchase)


  def stepCreateTravelerCheckPurchaseLineList(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the checkbook
    """
    # This is not required to create checkbook items, they will be
    # automatically created with the confirm action worfklow transition

    # Add a line for check
    self.line_1 = self.traveler_check_purchase.newContent(quantity=1,
                                 portal_type='Checkbook Delivery Line',
                                 resource_value=self.traveler_check_model,
                                 check_type_value=self.traveler_check_model.variant_1,
                                 reference_range_min="abcd123456",
                                 reference_range_max="abcd123456",
                                 aggregate_value=self.traveler_check,
                                 price_currency_value=self.currency_2
                                 )


  def stepDeliverTravelerCheckPurchase(self, sequence=None, sequence_list=None, **kw):
    """
    Deliver the traveler check purchase
    """
    state = self.traveler_check_purchase.getSimulationState()
    # check that state is draft
    self.assertEqual(state, 'draft')
    self.workflow_tool.doActionFor(self.traveler_check_purchase,
                                   'deliver_action',
                                   wf_id='traveler_check_purchase_workflow')
    # get state of cash sorting
    state = self.traveler_check_purchase.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.traveler_check_purchase,
                            name='history', wf_id='traveler_check_purchase_workflow')
    self.assertEqual(len(workflow_history), 3)
    self.assertEqual(self.traveler_check_purchase.movement.getQuantity(), 32500)


  def stepCheckFinalCheckbookInventory(self, sequence=None, sequence_list=None, **kw):
    """
    Check cash checkbook in item table
    """
    self.assertEqual(len(self.simulation_tool.getCurrentTrackingList(
                     node=self.traveler_check_source.getRelativeUrl(),
                     at_date=self.date)), 0)
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(
                     node=self.traveler_check_source.getRelativeUrl(),
                     at_date=self.date)), 0)
    checkbook_list = self.simulation_tool.getCurrentTrackingList(
                             node=self.traveler_check_source.getRelativeUrl(),
                             at_date=self.date)
    self.assertEqual(len(checkbook_list), 0)
    # check we have cash checkbook 1
    checkbook_object_list = [x.getObject() for x in checkbook_list]
    self.assertEqual(len(checkbook_object_list), 0)
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(
                     payment=self.bank_account_1.getRelativeUrl(),
                     resource=self.currency_1.getRelativeUrl()), 100000)
    self.assertEqual(self.simulation_tool.getFutureInventory(
                     payment=self.bank_account_1.getRelativeUrl(),
                     resource=self.currency_1.getRelativeUrl()), 100000)

  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingTravelerCheckPurchase(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialCheckbookInventory ' \
                    + 'CreateTravelerCheckPurchase Tic ' \
                    + 'CreateTravelerCheckPurchaseLineList Tic ' \
                    + 'DeliverTravelerCheckPurchase Tic ' \
                    + 'CheckFinalCheckbookInventory'
    sequence_list.addSequenceString(sequence_string)
    # play the sequence
    sequence_list.play(self)

