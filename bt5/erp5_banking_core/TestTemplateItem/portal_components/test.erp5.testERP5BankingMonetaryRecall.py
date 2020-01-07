
##############################################################################
#
# Copyright (c) 2005-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Alexandre Boeglin <alex_AT_nexedi_DOT_com>
#                    Kevin Deldycke <kevin_AT_nexedi_DOT_com>
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
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from erp5.component.module.TestERP5BankingMixin import TestERP5BankingMixin

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

class TestERP5BankingMonetaryRecall(TestERP5BankingMixin):
  """
    This class is a unit test to check the module of  Monetary Recall

    Here are the following step that will be done in the test :

    - before the test, we need to create some movements that will put resources in the source

    - create a monetary recall
    - check it has been created correctly
    - check source and destination (current == future)

    - create a "Note Line" (billetage)
    - check it has been created correctly
    - check the total amount

    - create a second Line
    - check it has been created correctly
    - check the total amount

    - create an invalid Line (quantity > available at source)
    - check that the system behaves correctly

    - pass "confirm_action" transition
    - check that the new state is confirmed
    - check that the source has been debited correctly (current < future)
    - check amount, lines, ...

    - pass "deliver_action" transition
    - check that the new state is delivered
    - check that the destination has been credited correctly (current == future)
  """


  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet

  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingMonetaryRecall"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    # Set some variables :
    self.initDefaultVariable()
    # the cahs transfer module
    self.monetary_recall_module = self.getMonetaryRecallModule()

    self.createManagerAndLogin()

    # create categories
    self.createFunctionGroupSiteCategory()

    # Before the test, we need to input the inventory
    inventory_dict_line_1 = {'id' : 'inventory_line_1',
                             'resource': self.billet_10000,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/p', 'cash_status/cancelled') + self.variation_list,
                             'quantity': self.quantity_10000}

    inventory_dict_line_2 = {'id' : 'inventory_line_2',
                             'resource': self.piece_200,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/p', 'cash_status/cancelled') + self.variation_list,
                             'quantity': self.quantity_200}


    self.line_list = line_list = [inventory_dict_line_1, inventory_dict_line_2]
    self.cash = self.paris.caveau.auxiliaire.encaisse_des_billets_et_monnaies
    self.cash_surface = self.paris.surface.caisse_courante.encaisse_des_billets_et_monnaies

    ###Comment this part because the destination is automatic
    #print self.paris.caveau.objectIds()
    self.counter = self.paris.caveau.serre.encaisse_des_billets_retires_de_la_circulation

    self.createCashInventory(source=None, destination=self.cash, currency=self.currency_1,
                             line_list=line_list)
    surface_line_list = []
    for line in line_list:
      line['id'] = 'surface_%s' % line['id']
      surface_line_list.append(line)
    self.createCashInventory(source=None, destination=self.cash_surface,
                             currency=self.currency_1,
                             line_list=surface_line_list)
    # now we need to create a user as Manager to do the test
    # in order to have an assigment defined which is used to do transition
    # Create an Organisation that will be used for users assignment
    self.checkUserFolderType()
    self.organisation = self.organisation_module.newContent(id='paris', portal_type='Organisation',
                          function='banking', group='baobab',  site='testsite/paris')
    # define the user
    user_dict = {
        'super_user' : [['Manager'], self.organisation, 'banking/comptable', 'baobab', 'testsite/paris/surface/banque_interne/guichet_1']
      }
    # call method to create this user
    self.createERP5Users(user_dict)
    self.logout()
    self.loginByUserName('super_user')
    # open counter date and counter
    self.openCounterDate(site=self.paris)


  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that MonetaryRecall Module was created
    self.assertEqual(self.monetary_recall_module.getPortalType(), 'Monetary Recall Module')
    # check monetary recall module is empty
    self.assertEqual(len(self.monetary_recall_module.objectValues()), 0)


  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in cash
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.cash.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.cash.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200 in cash
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.cash.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.cash.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)


  def stepCheckSource(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory in source vault (cash) before a confirm
    """
    # check we have 5 banknotes of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.cash.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.cash.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.cash.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.cash.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)


  def stepCheckDestination(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory in destination vault (counter) before confirm
    """
    # check we don't have banknotes of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.counter.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.counter.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we don't have coins of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.counter.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.counter.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)


  def stepCreateMonetaryRecall(self, sequence=None, sequence_list=None,
                               document_id='monetary_recall_1',
                               source=None, **kwd):
    """
    Create a monetary recall document and check it
    """
    # Cash transfer has cash for source, counter for destination, and a price cooreponding to the sum of banknote of 10000 abd coin of 200 ( (2+3) * 1000 + (5+7) * 200 )
    self.monetary_recall = self.monetary_recall_module.newContent(
                                 id=document_id,
                                 portal_type='Monetary Recall',
                                 description='test',
                                 source_total_asset_price=52400.0)

    # execute tic
    self.tic()
    # get the monetary recall document
    self.monetary_recall = getattr(self.monetary_recall_module, document_id)
    # check its portal type
    self.assertEqual(self.monetary_recall.getPortalType(), 'Monetary Recall')
    # check that its source is cash
    if source is None:
      self.assertEqual(self.monetary_recall.getSource(), 'site/testsite/paris/caveau/auxiliaire/encaisse_des_billets_et_monnaies')
    else:
      self.monetary_recall.setSource(source)
      self.assertEqual(self.monetary_recall.getSource(), source)
    # set source reference
    self.setDocumentSourceReference(self.monetary_recall)
    # check source reference
    self.assertNotEqual(self.monetary_recall.getSourceReference(), '')
    self.assertNotEqual(self.monetary_recall.getSourceReference(), None)
    # check that its destination is counter
    self.assertEqual(self.monetary_recall.getBaobabDestination(),
      'site/testsite/paris/caveau/serre/encaisse_des_billets_retires_de_la_circulation')

  def stepCreateSurfaceMonetaryRecall(self, sequence=None,
      sequence_list=None, **kwd):
    """
    Create a monetary recall document and check it
    """
    source = self.cash_surface.getRelativeUrl()
    self.stepCreateMonetaryRecall(source=source,
                                  document_id='monetary_recall_2')

  def stepCreateValidLine1(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the monetary recall line 1 with banknotes of 10000 and check it has been well created
    """
    # create the monetary recall line
    self.addCashLineToDelivery(self.monetary_recall, 'valid_line_1', 'Monetary Recall Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/cancelled') + self.variation_list,
            self.quantity_10000)
    # execute tic
    self.tic()
    # check there is only one line created
    self.assertEqual(len(self.monetary_recall.objectValues()), 1)
    # get the monetary recall line
    self.valid_line_1 = getattr(self.monetary_recall, 'valid_line_1')
    # check its portal type
    self.assertEqual(self.valid_line_1.getPortalType(), 'Monetary Recall Line')
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
      cell = self.valid_line_1.getCell('emission_letter/p', variation, 'cash_status/cancelled')
      # chek portal types
      self.assertEqual(cell.getPortalType(), 'Monetary Recall Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      # check the destination vault is counter
      ##self.assertEqual(cell.getDestinationValue(), self.counter)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity of banknote for year 1992 is 2
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity of banknote for year 2003 is 3
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepCheckSubTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the amount after the creation of monetary recall line 1
    """
    # Check number of lines
    self.assertEqual(len(self.monetary_recall.objectValues()), 1)
    # Check quantity of banknotes (2 for 1992 and 3 for 2003)
    self.assertEqual(self.monetary_recall.getTotalQuantity(fast=0), 5.0)
    # Check the total price
    self.assertEqual(self.monetary_recall.getTotalPrice(fast=0), 10000 * 5.0)


  def stepCreateValidLine2(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the monetary recall line 2 wiht coins of 200 and check it has been well created
    """
    # create the line
    self.addCashLineToDelivery(self.monetary_recall, 'valid_line_2', 'Monetary Recall Line', self.piece_200,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/cancelled') + self.variation_list,
            self.quantity_200)
    # execute tic
    self.tic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.monetary_recall.objectValues()), 2)
    # get the second monetary recall line
    self.valid_line_2 = getattr(self.monetary_recall, 'valid_line_2')
    # check portal types
    self.assertEqual(self.valid_line_2.getPortalType(), 'Monetary Recall Line')
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
      cell = self.valid_line_2.getCell('emission_letter/p', variation, 'cash_status/cancelled')
      # check the portal type
      self.assertEqual(cell.getPortalType(), 'Monetary Recall Cell')
      if cell.getId() == 'movement_0_0_0':
        # check the quantity for coin for year 1992 is 5
        self.assertEqual(cell.getQuantity(), 5.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity for coin for year 2003 is 7
        self.assertEqual(cell.getQuantity(), 7.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepCreateInvalidLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create an invalid monetary recall line and
    check the total with the invalid monetary recall line
    """
    # create a line in which quanity of banknotes of 5000 is higher that quantity available at source
    # here create a line with 24 (11+13) banknotes of 500 although the vault cash has no banknote of 5000
    self.addCashLineToDelivery(self.monetary_recall, 'invalid_line', 'Monetary Recall Line', self.billet_5000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/cancelled') + self.variation_list,
            self.quantity_5000)
    # execute tic
    self.tic()
    # Check number of monetary recall lines (line1 + line2 +invalid_line)
    self.assertEqual(len(self.monetary_recall.objectValues()), 3)
    # Check quantity, same as checkTotal + banknote of 500: 11 for 1992 and 13 for 2003
    self.assertEqual(self.monetary_recall.getTotalQuantity(fast=0), 5.0 + 12.0 + 24)
    # chect the total price
    self.assertEqual(self.monetary_recall.getTotalPrice(fast=0), 10000 * 5.0 + 200 * 12.0 + 5000 * 24)


  def stepTryConfirmMonetaryRecallWithBadInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Try to confirm the monetary recall with a bad monetary recall line and
    check the try of confirm the monetary recall with the invalid line has failed
    """
    # fix amount (10000 * 5.0 + 200 * 12.0 + 5000 * 24)
    self.monetary_recall.setSourceTotalAssetPrice('172400.0')
    # try to do the workflow action "confirm_action', cath the exception ValidationFailed raised by workflow transition
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.monetary_recall, 'confirm_action', wf_id='monetary_recall_workflow')
    # execute tic
    self.tic()
    # get state of the monetary recall
    state = self.monetary_recall.getSimulationState()
    # check the state is draft
    self.assertEqual(state, 'empty')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.monetary_recall, name='history', wf_id='monetary_recall_workflow')
    # check its len is 2
    self.assertEqual(len(workflow_history), 2)
    # check we get an "Insufficient balance" message in the workflow history because of the invalid line
    msg = workflow_history[-1]['error_message']
    self.assertTrue('Insufficient balance' in "%s" %(msg,))


  def stepDelInvalidLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Delete the invalid monetary recall line previously create
    """
    self.monetary_recall.deleteContent('invalid_line')


  def stepCheckTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the total after the creation of the two monetary recall lines
    """
    # Check number of lines (line1 + line2)
    self.assertEqual(len(self.monetary_recall.objectValues()), 2)
    # Check quantity, banknotes : 2 for 1992 and 3 for 2003, coin : 5 for 1992 and 7 for 2003
    self.assertEqual(self.monetary_recall.getTotalQuantity(fast=0), 5.0 + 12.0)
    # check the total price
    self.assertEqual(self.monetary_recall.getTotalPrice(fast=0), 10000 * 5.0 + 200 * 12.0)


  def stepConfirmMonetaryRecall(self, sequence=None, sequence_list=None, **kwd):
    """
    Confirm the monetary recall and check it
    """
    # fix amount (10000 * 5.0 + 200 * 12.0)
    self.monetary_recall.setSourceTotalAssetPrice('52400.0')
    # do the Workflow action
    self.workflow_tool.doActionFor(self.monetary_recall, 'confirm_action', wf_id='monetary_recall_workflow')
    # execute tic
    self.tic()
    # get state
    state = self.monetary_recall.getSimulationState()
    # check state is confirmed
    self.assertEqual(state, 'confirmed')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.monetary_recall, name='history', wf_id='monetary_recall_workflow')
    # check len of workflow history is 4
    self.assertEqual(len(workflow_history), 4)

  def stepPlanMonetaryRecall(self, sequence=None, sequence_list=None, **kwd):
    """
    Confirm the monetary recall and check it
    """
    self.monetary_recall.setSourceTotalAssetPrice('52400.0')
    self.workflow_tool.doActionFor(self.monetary_recall, 'plan_action', wf_id='monetary_recall_workflow')
    state = self.monetary_recall.getSimulationState()
    self.assertEqual(state, 'planned')

  def stepOrderMonetaryRecall(self, sequence=None, sequence_list=None, **kwd):
    """
    Confirm the monetary recall and check it
    """
    self.monetary_recall.setSourceTotalAssetPrice('52400.0')
    self.workflow_tool.doActionFor(self.monetary_recall, 'order_action', wf_id='monetary_recall_workflow')
    state = self.monetary_recall.getSimulationState()
    self.assertEqual(state, 'ordered')

  def stepOrderToDeliverMonetaryRecall(self, sequence=None, sequence_list=None, **kwd):
    """
    Confirm the monetary recall and check it
    """
    self.workflow_tool.doActionFor(self.monetary_recall, 'order_to_deliver_action', wf_id='monetary_recall_workflow')
    state = self.monetary_recall.getSimulationState()
    self.assertEqual(state, 'delivered')

  def stepCheckSourceDebitPlanned(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault cash is right after confirm and before deliver
    """
    # check we have 5 banknotes of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.cash.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we will have 0 banknote of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.cash.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 12 coins of 200 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.cash.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    # check we will have 0 coin of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.cash.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)


  def stepCheckDestinationCreditPlanned(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault counter is right after confirm and before deliver
    """
    #print self.monetary_recall.getBaobabDestination()

    # check we have 0 banknote of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.counter.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we will have 5 banknotes of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.counter.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 0 coin of 200 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.counter.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    # check we will have 12 coins of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.counter.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)


  def stepDeliverMonetaryRecall(self, sequence=None, sequence_list=None, **kwd):
    """
    Deliver the monetary recall with a good user
    and check that the deliver of a cash tranfer have achieved
    """
    # do the workflow transition "deliver_action"
    self.workflow_tool.doActionFor(self.monetary_recall, 'deliver_action', wf_id='monetary_recall_workflow')
    # execute tic
    self.tic()
    # get state of monetary recall
    state = self.monetary_recall.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.monetary_recall, name='history', wf_id='monetary_recall_workflow')

  def stepCheckSourceDebit(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at source (vault cash) after deliver of the monetary recall
    """
    # check we have 0 banknote of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.cash.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.cash.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 0 coin of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.cash.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.cash.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)


  def stepCheckDestinationCredit(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at destination (vault counter) after deliver of the monetary recall
    """
    # check we have 5 banknotes of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.counter.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.counter.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coins of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.counter.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.counter.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)


  def stepCheckCashDeliveryLine(self, sequence=None, sequence_list=None):
    """
    Check the cash delivery line
    """
    variation = 'variation/2003'
    # get the delivery cell
    cell = self.valid_line_1.getCell('emission_letter/p', variation, 'cash_status/cancelled')
    # check the destination variation text is redefine on destination
    self.assertEqual(cell.getBaobabDestinationVariationText(), 'cash_status/retired\nemission_letter/p\nvariation/2003')

  def stepResetInventory(self,
               sequence=None, sequence_list=None, **kwd):
    node = self.cash
    line_list = self.line_list
    self.resetInventory(destination=node, currency=self.currency_1,
                        line_list=line_list,extra_id='_reset_out')

  def stepDeliverFails(self, sequence=None, sequence_list=None, **kwd):
    message = self.assertWorkflowTransitionFails(self.monetary_recall,
              'monetary_recall_workflow','deliver_action')
    self.assertTrue(message.find('Insufficient balance')>=0)

  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingMonetaryRecall(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialInventory CheckSource CheckDestination ' \
                    + 'CreateMonetaryRecall ' \
                    + 'CreateValidLine1 CheckSubTotal ' \
                    + 'CreateValidLine2 CheckTotal ' \
                    + 'CheckSource CheckDestination ' \
                    + 'CreateInvalidLine ' \
                    + 'TryConfirmMonetaryRecallWithBadInventory ' \
                    + 'DelInvalidLine Tic CheckTotal ' \
                    + 'ConfirmMonetaryRecall ' \
                    + 'CheckSourceDebitPlanned CheckDestinationCreditPlanned ' \
                    + 'CheckSourceDebitPlanned CheckDestinationCreditPlanned ' \
                    + 'ResetInventory Tic ' \
                    + 'DeliverFails ' \
                    + 'DeleteResetInventory Tic ' \
                    + 'DeliverMonetaryRecall ' \
                    + 'CheckSourceDebit CheckDestinationCredit CheckCashDeliveryLine '
    sequence_list.addSequenceString(sequence_string)
    # define the sequence
    sequence_string = 'Tic '\
                    + 'CreateSurfaceMonetaryRecall ' \
                    + 'CreateValidLine1 CheckSubTotal ' \
                    + 'CreateValidLine2 CheckTotal ' \
                    + 'PlanMonetaryRecall Tic ' \
                    + 'OrderMonetaryRecall Tic ' \
                    + 'OrderToDeliverMonetaryRecall '
    sequence_list.addSequenceString(sequence_string)
    # play the sequence
    sequence_list.play(self)

