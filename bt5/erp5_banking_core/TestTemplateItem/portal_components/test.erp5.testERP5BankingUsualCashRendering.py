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
# This program is Free Software; you can rediscaisse_courantebute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is discaisse_courantebuted in the hope that it will be useful,
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

class TestERP5BankingUsualCashRendering(TestERP5BankingMixin):
  """
    This class is a unit test to check the module of Usual Cash Rendering

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

    - pass "plan_action" transition
    - check that the new state is planned
    - check that the source has been debited correctly (current < future)
    - check amount, lines, ...

    - pass "order_action" transition
    - check that the new state is ordered
    - check that the source has been debited correctly (current < future)
    - check amount, lines, ...


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
    return "ERP5BankingUsualCashRendering"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    # Set some variables :
    self.initDefaultVariable()
    # the cahs transfer module
    self.usual_cash_rendering_module = self.getUsualCashRenderingModule()

    self.createManagerAndLogin()

    # create categories
    self.createFunctionGroupSiteCategory()

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

    self.caisse_courante = self.paris.surface.caisse_courante.encaisse_des_billets_et_monnaies
    self.auxiliaire = self.paris.caveau.auxiliaire.encaisse_des_billets_et_monnaies
    self.createCashInventory(source=None, destination=self.caisse_courante, currency=self.currency_1,
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


  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that UsualCashRendering Module was created
    self.assertEqual(self.usual_cash_rendering_module.getPortalType(), 'Usual Cash Rendering Module')
    # check vault transfer module is empty
    self.assertEqual(len(self.usual_cash_rendering_module.objectValues()), 0)


  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in caisse_courante
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_courante.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_courante.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200 in caisse_courante
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_courante.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_courante.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)




  def stepCheckSource(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory in source vault (caisse_courante) before a confirm
    """
    # check we have 5 banknotes of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_courante.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_courante.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_courante.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_courante.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)

  def stepCheckDestination(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory in destination vault (caisse_courante) before confirm
    """
    # check we don't have banknotes of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.auxiliaire.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.auxiliaire.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we don't have coins of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.auxiliaire.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.auxiliaire.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)

  def stepCreateUsualCashRendering(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a vault transfer document and check it
    """
    # Usual Cash Rendering has caisse_courante (Gros versment) for source, caisse_courante for destination, and a price cooreponding to the sum of banknote of 10000 abd coin of 200 ( (2+3) * 1000 + (5+7) * 200 )


    self.usual_cash_rendering = self.usual_cash_rendering_module.newContent(id='usual_cash_rendering_1',
        portal_type='Usual Cash Rendering', source=self.caisse_courante.getRelativeUrl(),
        description='test',
        destination=self.auxiliaire.getRelativeUrl(), source_total_asset_price=52400.0)
    # execute tic
    self.tic()
    # check we have only one vault transfer
    self.assertEqual(len(self.usual_cash_rendering_module.objectValues()), 1)
    # get the vault transfer document
    self.usual_cash_rendering = getattr(self.usual_cash_rendering_module, 'usual_cash_rendering_1')
    # check its portal type
    self.assertEqual(self.usual_cash_rendering.getPortalType(), 'Usual Cash Rendering')
    # check that its source is caisse_courante
    self.assertEqual(self.usual_cash_rendering.getSource(), 'site/testsite/paris/surface/caisse_courante/encaisse_des_billets_et_monnaies')
    # check that its destination is caisse auxiliaire
    self.assertEqual(self.usual_cash_rendering.getDestination(), 'site/testsite/paris/caveau/auxiliaire/encaisse_des_billets_et_monnaies')




  def stepCreateValidLine1(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the vault transfer line 1 with banknotes of 10000 and check it has been well created
    """
    # create the vault transfer line
    self.addCashLineToDelivery(self.usual_cash_rendering, 'valid_line_1', 'Cash Delivery Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/valid') + self.variation_list,
            self.quantity_10000)
    # execute tic
    self.tic()
    # check there is only one line created
    self.assertEqual(len(self.usual_cash_rendering.objectValues()), 1)
    # get the vault transfer line
    self.valid_line_1 = getattr(self.usual_cash_rendering, 'valid_line_1')
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
      # check the source vault is caisse_courante
      self.assertEqual(cell.getSourceValue(), self.caisse_courante)
      # check the destination vault is caisse_courante
      self.assertEqual(cell.getDestinationValue(), self.auxiliaire)
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
    Check the amount after the creation of vault transfer line 1
    """
    # Check number of lines
    self.assertEqual(len(self.usual_cash_rendering.objectValues()), 1)
    # Check quantity of banknotes (2 for 1992 and 3 for 2003)
    self.assertEqual(self.usual_cash_rendering.getTotalQuantity(fast=0), 5.0)
    # Check the total price
    self.assertEqual(self.usual_cash_rendering.getTotalPrice(fast=0), 10000 * 5.0)


  def stepCreateValidLine2(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the vault transfer line 2 wiht coins of 200 and check it has been well created
    """
    # create the line
    self.addCashLineToDelivery(self.usual_cash_rendering, 'valid_line_2', 'Cash Delivery Line', self.piece_200,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/valid') + self.variation_list,
            self.quantity_200)
    # execute tic
    self.tic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.usual_cash_rendering.objectValues()), 2)
    # get the second vault transfer line
    self.valid_line_2 = getattr(self.usual_cash_rendering, 'valid_line_2')
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
    # here create a line with 24 (11+13) banknotes of 500 although the vault caisse_courante has no banknote of 5000
    self.addCashLineToDelivery(self.usual_cash_rendering, 'invalid_line', 'Cash Delivery Line', self.billet_5000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/valid') + self.variation_list,
            self.quantity_5000)
    # execute tic
    self.tic()
    # Check number of vault transfer lines (line1 + line2 +invalid_line)
    self.assertEqual(len(self.usual_cash_rendering.objectValues()), 3)
    # Check quantity, same as checkTotal + banknote of 500: 11 for 1992 and 13 for 2003
    self.assertEqual(self.usual_cash_rendering.getTotalQuantity(fast=0), 5.0 + 12.0 + 24)
    # chect the total price
    self.assertEqual(self.usual_cash_rendering.getTotalPrice(fast=0), 10000 * 5.0 + 200 * 12.0 + 5000 * 24)


  def stepTryPlanUsualCashRenderingWithBadInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Try to plan the usual_cash_rendering with a bad usual_cash_rendering line and
    check the try of confirm the usual_cash_rendering with the invalid line has failed
    """
    # fix amount (10000 * 5.0 + 200 * 12.0 + 5000 * 24)
    self.usual_cash_rendering.setSourceTotalAssetPrice('172400.0')
    # try to do the workflow action "plan_action', cath the exception ValidationFailed raised by workflow transition
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.usual_cash_rendering, 'plan_action', wf_id='usual_cash_rendering_workflow')
    # execute tic
    self.tic()
    # get state of the usual_cash_rendering
    state = self.usual_cash_rendering.getSimulationState()
    # check the state is draft
    self.assertEqual(state, 'draft')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.usual_cash_rendering, name='history', wf_id='usual_cash_rendering_workflow')
    # check its len is 2
    self.assertEqual(len(workflow_history), 2)
    # check we get an "Insufficient balance" message in the workflow history because of the invalid line
    msg = workflow_history[-1]['error_message']
    self.assertTrue('Insufficient balance' in "%s" %(msg,))

  def stepDelInvalidLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Delete the invalid usual_cash_rendering line previously create
    """
    self.usual_cash_rendering.deleteContent('invalid_line')


  def stepCheckTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the total after the creation of the two usual_cash_rendering lines
    """
    # Check number of lines (line1 + line2)
    self.assertEqual(len(self.usual_cash_rendering.objectValues()), 2)
    # Check quantity, banknotes : 2 for 1992 and 3 for 2003, coin : 5 for 1992 and 7 for 2003
    self.assertEqual(self.usual_cash_rendering.getTotalQuantity(fast=0), 5.0 + 12.0)
    # check the total price
    self.assertEqual(self.usual_cash_rendering.getTotalPrice(fast=0), 10000 * 5.0 + 200 * 12.0)


  def stepPlanUsualCashRendering(self, sequence=None, sequence_list=None, **kwd):
    """
    Confirm the usual_cash_rendering and check it
    """
    # fix amount (10000 * 5.0 + 200 * 12.0)
    self.usual_cash_rendering.setSourceTotalAssetPrice('52400.0')
    # do the Workflow action
    self.workflow_tool.doActionFor(self.usual_cash_rendering, 'plan_action', wf_id='usual_cash_rendering_workflow')
    # execute tic
    self.tic()
    # get state
    state = self.usual_cash_rendering.getSimulationState()
    # check state is planned
    self.assertEqual(state, 'planned')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.usual_cash_rendering, name='history', wf_id='usual_cash_rendering_workflow')
    # check len of workflow history is 4
    self.assertEqual(len(workflow_history), 4)

  def stepOrderUsualCashRendering(self, sequence=None, sequence_list=None, **kwd):
    """
    Confirm the usual_cash_rendering and check it
    """
    # fix amount (10000 * 5.0 + 200 * 12.0)
    self.usual_cash_rendering.setSourceTotalAssetPrice('52400.0')
    # do the Workflow action
    self.workflow_tool.doActionFor(self.usual_cash_rendering, 'order_action', wf_id='usual_cash_rendering_workflow')
    # execute tic
    self.tic()
    # get state
    state = self.usual_cash_rendering.getSimulationState()
    # check state is ordered
    self.assertEqual(state, 'ordered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.usual_cash_rendering, name='history', wf_id='usual_cash_rendering_workflow')
    # check len of workflow history is 4
    self.assertEqual(len(workflow_history), 6)

  def stepCheckSourceDebitPlanned(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault caisse_courante is right after confirm and before deliver
    """
    # check we have 5 banknotes of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_courante.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we will have 0 banknote of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_courante.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 12 coins of 200 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_courante.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    # check we will have 0 coin of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_courante.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)





  def stepCheckDestinationCreditPlanned(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault caisse_courante is right after confirm and before deliver
    """
    # check we have 0 banknote of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.auxiliaire.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we will have 5 banknotes of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.auxiliaire.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 0 coin of 200 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.auxiliaire.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    # check we will have 12 coins of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.auxiliaire.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)

  def stepDeliverUsualCashRendering(self, sequence=None, sequence_list=None, **kwd):
    """
    Deliver the usual_cash_rendering with a good user
    and check that the deliver of a cash tranfer have achieved
    """
    # do the workflow transition "deliver_action"
    self.workflow_tool.doActionFor(self.usual_cash_rendering, 'deliver_action', wf_id='usual_cash_rendering_workflow')
    # execute tic
    self.tic()
    # get state of usual_cash_rendering
    state = self.usual_cash_rendering.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.usual_cash_rendering, name='history', wf_id='usual_cash_rendering_workflow')
    # check len of len workflow history is 10

  def stepOrderToDeliverUsualCashRendering(self, sequence=None, sequence_list=None, **kwd):
    """
    Deliver the usual_cash_rendering with a good user
    and check that the deliver of a cash tranfer have achieved
    """
    # do the workflow transition "deliver_action"

    self.workflow_tool.doActionFor(self.usual_cash_rendering, 'order_to_deliver_action', wf_id='usual_cash_rendering_workflow')
    # execute tic
    self.tic()
    # get state of usual_cash_rendering
    state = self.usual_cash_rendering.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.usual_cash_rendering, name='history', wf_id='usual_cash_rendering_workflow')
    # check len of len workflow history is 10
    self.assertEqual(len(workflow_history), 8)

  def stepCheckSourceDebit(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at source (vault caisse_courante) after deliver of the usual_cash_rendering
    """
    # check we have 0 banknote of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_courante.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_courante.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 0 coin of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_courante.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_courante.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)



  def stepCheckDestinationCredit(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at destination (vault caisse_courante) after deliver of the usual_cash_rendering
    """
    # check we have 5 banknotes of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.auxiliaire.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.auxiliaire.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coins of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.auxiliaire.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.auxiliaire.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)

  def stepResetSourceInventory(self,
               sequence=None, sequence_list=None, **kwd):
    """
    Reset a vault
    """
    node = self.caisse_courante
    line_list = self.line_list
    self.resetInventory(destination=node, currency=self.currency_1,
                        line_list=line_list,extra_id='_reset_out')

  def stepDeliverUsualCashRenderingFails(self, sequence=None, sequence_list=None, **kwd):
    """
    Try if we get Insufficient balance
    """
    message = self.assertWorkflowTransitionFails(self.usual_cash_rendering,
              'usual_cash_rendering_workflow','deliver_action')
    self.assertTrue(message.find('Insufficient balance')>=0)

  def test_01_ERP5BankingUsualCashRendering(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialInventory CheckSource CheckDestination ' \
                    + 'CreateUsualCashRendering ' \
                    + 'CreateValidLine1 CheckSubTotal ' \
                    + 'CreateValidLine2 CheckTotal ' \
                    + 'CheckSource CheckDestination ' \
                    + 'CreateInvalidLine ' \
                    + 'TryPlanUsualCashRenderingWithBadInventory ' \
                    + 'DelInvalidLine Tic CheckTotal ' \
                    + 'PlanUsualCashRendering ' \
                    + 'CheckSourceDebitPlanned CheckDestinationCreditPlanned ' \
                    + 'CheckSourceDebitPlanned CheckDestinationCreditPlanned ' \
                    + 'OrderUsualCashRendering ' \
                    + 'ResetSourceInventory Tic ' \
                    + 'DeliverUsualCashRenderingFails Tic ' \
                    + 'DeleteResetInventory Tic ' \
                    + 'DeliverUsualCashRendering ' \
                    + 'CheckSourceDebit CheckDestinationCredit '

    sequence_list.addSequenceString(sequence_string)
    # play the sequence
    sequence_list.play(self)

