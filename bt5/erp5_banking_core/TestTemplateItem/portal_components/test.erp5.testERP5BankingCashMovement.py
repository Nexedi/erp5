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
# This program is Free Software; you can redisvault_destinationbute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is disvault_destinationbuted in the hope that it will be useful,
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

class TestERP5BankingCashMovement(TestERP5BankingMixin):
  """
    This class is a unit test to check the module of Cash Movement

    Here are the following step that will be done in the test :

    - before the test, we need to create some movements that will put resources in the source

    - create a vault transfer
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
    - check that the new state is planned
    - check amount, lines, ...

    - pass "start_action" transition
    - check that the new state is ordered
    - check that the source has been debited correctly
    - check that the destination has not been credited yet
    - check amount, lines, ...


    - pass "stop_action" transition
    - check that the new state is confirmed
    - check that the destination has been credited correctly
    - check amount, lines, ...

    - pass "deliver_action" transition
    - check that the new state is delivered

  """


  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet

  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingCashMovement"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    # Set some variables :
    self.initDefaultVariable()
    # the cahs transfer module
    self.cash_movement_module = self.getCashMovementModule()

    self.createManagerAndLogin()

    # create categories
    self.createFunctionGroupSiteCategory(site_list=['paris', 'madrid'])

    # Before the test, we need to input the inventory

    inventory_dict_line_1 = {'id' : 'inventory_line_1',
                             'resource': self.billet_10000,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/p', 'cash_status/valid') + self.variation_list,
                             'quantity': self.quantity_10000}

    inventory_dict_line_2 = {'id' : 'inventory_line_2',
                             'resource': self.piece_200,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/p', 'cash_status/valid') + self.variation_list,
                             'quantity': self.quantity_200}

    self.line_list = line_list = [inventory_dict_line_1, inventory_dict_line_2]
    self.vault_source = self.paris.caveau.auxiliaire.encaisse_des_externes
    self.currency_handover_vault_source = self.paris.caveau.auxiliaire.encaisse_des_devises.usd
    self.vault_destination = self.madrid.caveau.reserve.encaisse_des_billets_et_monnaies

    self.createCashInventory(source=None, destination=self.vault_source, currency=self.currency_1,
                             line_list=line_list)
    self.createCashInventory(source=None, destination=self.currency_handover_vault_source,
                             currency=self.currency_1,
                             line_list=line_list)
    # Create an Organisation that will be used for users assignment
    self.checkUserFolderType()
    self.organisation = self.organisation_module.newContent(id='baobab_org', portal_type='Organisation',
                          function='banking', group='baobab',  site='testsite/paris')
    # define the user
    user_dict = {
        'super_user' : [['Manager'], self.organisation, 'banking/comptable', 'baobab', 'testsite/paris/surface/banque_interne/guichet_1']
      }
    # call method to create this user
    self.createERP5Users(user_dict)
    self.logout()
    self.loginByUserName('super_user')
    self.openCounterDate(site=self.paris)
    self.openCounterDate(site=self.madrid, id='counter_date_2')



  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that CashMovement Module was created
    self.assertEqual(self.cash_movement_module.getPortalType(), 'Cash Movement Module')
    # check vault transfer module is empty
    self.assertEqual(len(self.cash_movement_module.objectValues()), 0)


  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in vault_source
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault_source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault_source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200 in vault_source
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault_source.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault_source.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    # check we don't have banknotes of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault_destination.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault_destination.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we don't have coins of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault_destination.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault_destination.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)

  def stepCheckCurrencyHandoverInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in vault_source
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.currency_handover_vault_source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.currency_handover_vault_source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200 in vault_source
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.currency_handover_vault_source.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.currency_handover_vault_source.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    # check we don't have banknotes of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault_destination.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault_destination.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we don't have coins of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault_destination.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault_destination.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)

  def stepCreateCashMovement(self, sequence=None, sequence_list=None,
                             none_destination=0, **kwd):
    """
    Create a vault transfer document and check it
    """
    # Cash Movement has vault_source (Gros versment) for source, vault_destination for destination, and a price cooreponding to the sum of banknote of 10000 abd coin of 200 ( (2+3) * 1000 + (5+7) * 200 )


    self.cash_movement = self.cash_movement_module.newContent(
                                id='cash_movement_1',
                                portal_type='Cash Movement',
                                source=self.vault_source.getRelativeUrl(),
                                destination=self.vault_destination.getRelativeUrl(),
                                description='test',
                                start_date=self.date,
                                source_total_asset_price=52400.0)
    # execute tic
    self.tic()
    # check we have only one vault transfer
    self.assertEqual(len(self.cash_movement_module.objectValues()), 1)
    # get the vault transfer document
    self.cash_movement = getattr(self.cash_movement_module, 'cash_movement_1')
    # check its portal type
    self.assertEqual(self.cash_movement.getPortalType(), 'Cash Movement')
    # check that its source is vault_source
    self.assertEqual(self.cash_movement.getSource(), 'site/testsite/paris/caveau/auxiliaire/encaisse_des_externes')
    # check that its destination is vault_destination
    self.assertEqual(self.cash_movement.getDestination(), 'site/testsite/madrid/caveau/reserve/encaisse_des_billets_et_monnaies')
    self.setDocumentSourceReference(self.cash_movement)

  def stepCreateValidLine1(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the vault transfer line 1 with banknotes of 10000 and check it has been well created
    """
    # create the vault transfer line
    self.addCashLineToDelivery(self.cash_movement, 'valid_line_1', 'Cash Delivery Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/valid') + self.variation_list,
            self.quantity_10000)
    # execute tic
    self.tic()
    # check there is only one line created
    self.assertEqual(len(self.cash_movement.objectValues()), 1)
    # get the vault transfer line
    self.valid_line_1 = getattr(self.cash_movement, 'valid_line_1')
    # check its portal type
    self.assertEqual(self.valid_line_1.getPortalType(), 'Cash Delivery Line')
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
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      # check the source vault is vault_source
      if cell.getExplanationValue().isCurrencyHandover():
        self.assertEqual(cell.getSourceValue(), self.currency_handover_vault_source)
      else:
        self.assertEqual(cell.getSourceValue(), self.vault_source)
      # check the destination vault is vault_destination
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
    Check the amount after the creation of cash movement line 1
    """
    # Check number of lines
    self.assertEqual(len(self.cash_movement.objectValues()), 1)
    # Check quantity of banknotes (2 for 1992 and 3 for 2003)
    self.assertEqual(self.cash_movement.getTotalQuantity(fast=0), 5.0)
    # Check the total price
    self.assertEqual(self.cash_movement.getTotalPrice(fast=0), 10000 * 5.0)


  def stepCreateValidLine2(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the vault transfer line 2 wiht coins of 200 and check it has been well created
    """
    # create the line
    self.addCashLineToDelivery(self.cash_movement, 'valid_line_2', 'Cash Delivery Line', self.piece_200,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/valid') + self.variation_list,
            self.quantity_200)
    # execute tic
    self.tic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.cash_movement.objectValues()), 2)
    # get the second vault transfer line
    self.valid_line_2 = getattr(self.cash_movement, 'valid_line_2')
    # check portal types
    self.assertEqual(self.valid_line_2.getPortalType(), 'Cash Delivery Line')
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
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
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
    Create an invalid vault transfer line and
    check the total with the invalid vault transfer line
    """
    # create a line in which quanity of banknotes of 5000 is higher that quantity available at source
    # here create a line with 24 (11+13) banknotes of 500 although the vault vault_source has no banknote of 5000
    self.addCashLineToDelivery(self.cash_movement, 'invalid_line', 'Cash Delivery Line', self.billet_5000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/valid') + self.variation_list,
            self.quantity_5000)
    # execute tic
    self.tic()
    # Check number of vault transfer lines (line1 + line2 +invalid_line)
    self.assertEqual(len(self.cash_movement.objectValues()), 3)
    # Check quantity, same as checkTotal + banknote of 500: 11 for 1992 and 13 for 2003
    self.assertEqual(self.cash_movement.getTotalQuantity(fast=0), 5.0 + 12.0 + 24)
    # chect the total price
    self.assertEqual(self.cash_movement.getTotalPrice(fast=0), 10000 * 5.0 + 200 * 12.0 + 5000 * 24)


  def stepTryStopCashMovementWithBadInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Try to confirm the cash_movement with a bad cash_movement line and
    check the try of confirm the cash_movement with the invalid line has failed
    """
    # fix amount (10000 * 5.0 + 200 * 12.0 + 5000 * 24)
    self.cash_movement.setSourceTotalAssetPrice('172400.0')
    # try to do the workflow action "stop_action', cath the exception ValidationFailed raised by workflow transition
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor,
                  self.cash_movement, 'stop_action',
                  wf_id='cash_movement_workflow', your_stop_date=self.date)
    # execute tic
    self.tic()
    # get state of the cash_movement
    state = self.cash_movement.getSimulationState()
    # check the state is draft
    self.assertEqual(state, 'draft')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_movement, name='history', wf_id='cash_movement_workflow')
    # check its len is 2
    self.assertEqual(len(workflow_history), 2)
    # check we get an "Insufficient balance" message in the workflow history because of the invalid line
    msg = workflow_history[-1]['error_message']
    self.assertTrue('Insufficient balance' in "%s" %(msg, ))


  def stepTryConfirmCashMovementWithBadInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Try to plan the cash_movement with a bad cash_movement line and
    check the try of confirm the cash_movement with the invalid line has failed
    """

    # fix amount (10000 * 5.0 + 200 * 12.0 + 5000 * 24)

    self.cash_movement.setSourceTotalAssetPrice('172400.0')
    # try to do the workflow action "confirm_action', cath the exception ValidationFailed raised by workflow transition
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.cash_movement, 'confirm_action', wf_id='cash_movement_workflow')
    # execute tic
    self.tic()
    # get state of the cash_movement
    state = self.cash_movement.getSimulationState()
    # check the state is draft
    self.assertEqual(state, 'empty')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_movement, name='history', wf_id='cash_movement_workflow')
    # check we get an "Insufficient balance" message in the workflow history because of the invalid line
    msg = '%s' % (workflow_history[-1]['error_message'], )
    self.assertTrue('Insufficient balance' in msg, msg)

  def stepDelInvalidLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Delete the invalid cash_movement line previously create
    """
    self.cash_movement.deleteContent('invalid_line')

  def stepCheckTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the total after the creation of the two cash_movement lines
    """
    # Check number of lines (line1 + line2)
    self.assertEqual(len(self.cash_movement.objectValues()), 2)
    # Check quantity, banknotes : 2 for 1992 and 3 for 2003, coin : 5 for 1992 and 7 for 2003
    self.assertEqual(self.cash_movement.getTotalQuantity(fast=0), 5.0 + 12.0)
    # check the total price
    self.assertEqual(self.cash_movement.getTotalPrice(fast=0), 10000 * 5.0 + 200 * 12.0)


  def stepStopCashMovement(self, sequence=None, sequence_list=None, **kwd):
    """
    Confirm the cash_movement and check it
    """
    # fix amount (10000 * 5.0 + 200 * 12.0)
    self.cash_movement.setSourceTotalAssetPrice('52400.0')

    # do the Workflow action
    self.workflow_tool.doActionFor(self.cash_movement, 'stop_action',
                  wf_id='cash_movement_workflow', stop_date=self.date)
    # execute tic
    self.tic()
    # get state
    state = self.cash_movement.getSimulationState()
    # check state is stopped
    self.assertEqual(state, 'stopped')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_movement, name='history', wf_id='cash_movement_workflow')


  def stepConfirmCashMovement(self, sequence=None, sequence_list=None, **kwd):
    """
    Confirm the cash_movement and check it
    """
    # fix amount (10000 * 5.0 + 200 * 12.0)
    self.cash_movement.setSourceTotalAssetPrice('52400.0')
    # do the Workflow action
    self.workflow_tool.doActionFor(self.cash_movement, 'confirm_action', wf_id='cash_movement_workflow')
    # execute tic
    self.tic()
    # get state
    state = self.cash_movement.getSimulationState()
    # check state is confirmed
    self.assertEqual(state, 'confirmed')

  def stepStartCashMovement(self, sequence=None, sequence_list=None, **kwd):
    """
    Confirm the cash_movement and check it
    """
    # fix amount (10000 * 5.0 + 200 * 12.0)
    self.cash_movement.setSourceTotalAssetPrice('52400.0')
    # do the Workflow action
    self.workflow_tool.doActionFor(self.cash_movement, 'start_action', wf_id='cash_movement_workflow')
    # execute tic
    self.tic()
    # get state
    state = self.cash_movement.getSimulationState()
    # check state is started
    self.assertEqual(state, 'started')

  def stepCheckSourceDebitStarted(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that computaion of inventory at vault vault_source is right after start and before stop
    """
    # check we have 0 banknotes of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault_source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we will have 0 banknote of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault_source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 0 coins of 200 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault_source.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    # check we will have 0 coin of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault_source.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)

  def stepCheckCurrencyHandoverSourceDebitStarted(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that computaion of inventory at vault vault_source is right after start and before stop
    """
    # check we have 0 banknotes of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.currency_handover_vault_source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we will have 0 banknote of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.currency_handover_vault_source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 0 coins of 200 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.currency_handover_vault_source.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    # check we will have 0 coin of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.currency_handover_vault_source.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)

  def stepCheckDestinationCreditStarted(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault vault_destination is right after start and before stop
    """
    # check we have 0 banknote of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault_destination.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we will have 5 banknotes of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault_destination.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 0 coin of 200 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault_destination.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    # check we will have 12 coins of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault_destination.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)

  def stepSetCashMovementCurrencyHandover(self, sequence=None, sequence_list=None, **kwd):
    self.cash_movement.setCurrencyHandover(True)
    self.cash_movement.setDestination(None)
    self.cash_movement.setSourceValue(self.currency_handover_vault_source)

  def stepDeliverCashMovement(self, sequence=None, sequence_list=None, **kwd):
    """
    Deliver the cash_movement with a good user
    and check that the deliver of a cash tranfer have achieved
    """
    # do the workflow transition "deliver_action"
    self.workflow_tool.doActionFor(self.cash_movement, 'deliver_action', wf_id='cash_movement_workflow')
    # execute tic
    self.tic()
    # get state of cash_movement
    state = self.cash_movement.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')


  def stepCheckSourceDebit(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at source (vault vault_source) after deliver of the cash_movement
    """
    # check we have 0 banknote of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault_source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault_source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 0 coin of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault_source.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault_source.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)

  def stepCheckCurrencyHandoverSourceDebit(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at source (vault vault_source) after deliver of the cash_movement
    """
    # check we have 0 banknote of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.currency_handover_vault_source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.currency_handover_vault_source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 0 coin of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.currency_handover_vault_source.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.currency_handover_vault_source.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)

  def stepCheckDestinationCredit(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at destination (vault vault_destination) after deliver of the cash_movement
    """
    # check we have 5 banknotes of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault_destination.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault_destination.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coins of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault_destination.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault_destination.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)

  def stepCheckDestinationHasNotChanged(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at destination (vault vault_destination) after deliver of the cash_movement
    """
    # check we have 5 banknotes of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault_destination.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault_destination.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 12 coins of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault_destination.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault_destination.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)

  def stepResetSourceInventory(self,
               sequence=None, sequence_list=None, **kwd):
    """
    Reset a vault
    """
    node = self.vault_source
    line_list = self.line_list
    self.resetInventory(destination=node, currency=self.currency_1,
                        line_list=line_list, extra_id='_reset_out')

  def stepDelCashMovement(self, sequence=None, sequence_list=None, **kwd):
    self.cash_movement_module.deleteContent('cash_movement_1')

  def stepStartCashMovementFails(self, sequence=None, sequence_list=None, **kwd):
    """
    Try if we get Insufficient balance
    """
    message = self.assertWorkflowTransitionFails(self.cash_movement,
              'cash_movement_workflow', 'start_action')
    self.assertTrue(message.find('Insufficient balance')>=0)


  def test_01_ERP5BankingCashMovement(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialInventory ' \
                    + 'CreateCashMovement ' \
                    + 'CreateValidLine1 CheckSubTotal ' \
                    + 'CreateValidLine2 CheckTotal ' \
                    + 'CheckInitialInventory ' \
                    + 'CreateInvalidLine ' \
                    + 'TryConfirmCashMovementWithBadInventory ' \
                    + 'DelInvalidLine Tic CheckTotal ' \
                    + 'ConfirmCashMovement ' \
                    + 'ResetSourceInventory Tic ' \
                    + 'StartCashMovementFails DeleteResetInventory Tic ' \
                    + 'StartCashMovement ' \
                    + 'CheckSourceDebitStarted CheckDestinationCreditStarted ' \
                    + 'StopCashMovement ' \
                    + 'DeliverCashMovement ' \
                    + 'CheckSourceDebit CheckDestinationCredit '

    sequence_list.addSequenceString(sequence_string)

    # Another sequence in order to test that the currency handover
    # is working
    sequence_string = 'Tic DelCashMovement Tic CheckCurrencyHandoverInitialInventory ' \
                    + 'CreateCashMovement ' \
                    + 'SetCashMovementCurrencyHandover ' \
                    + 'CreateValidLine1 CheckSubTotal ' \
                    + 'CreateValidLine2 CheckTotal ' \
                    + 'CheckCurrencyHandoverInitialInventory ' \
                    + 'Tic CheckTotal ' \
                    + 'ConfirmCashMovement ' \
                    + 'StartCashMovement ' \
                    + 'CheckCurrencyHandoverSourceDebitStarted ' \
                    + 'CheckDestinationHasNotChanged ' \
                    + 'StopCashMovement ' \
                    + 'DeliverCashMovement ' \
                    + 'CheckCurrencyHandoverSourceDebit CheckDestinationHasNotChanged '

    sequence_list.addSequenceString(sequence_string)

    # play the sequence
    sequence_list.play(self)
