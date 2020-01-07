
##############################################################################
#
# Copyright (c) 2005-2010 Nexedi SA and Contributors. All Rights Reserved.
#                   Aurelien Calonne <aurel@nexedi.com>
#                   Sebastien Robin <seb@nexedi.com>
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

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'


class TestERP5BankingCashExchange(TestERP5BankingMixin):
  """
  Unit test for the cash exchange module
  Source =  destination
  Initial cash detail :
        5 banknotes of 10000
        12 coin of 200
        24 banknotes of 5000
        0 coin of 100

  Ordered by Assignor
  Confirmed by Assignee
  Delivered by DestinationAssignee
  Final cash detail :
        0 banknotes of 10000
        0 coin of 200
        34 banknotes of 5000
        24 coin of 100

  """


  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet

  outgoing_quantity_5000 = {'variation/1992':4, 'variation/2003':6}
  outgoing_quantity_100 = {'variation/1992':24, 'variation/2003':0}

  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingCashExchange"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    self.initDefaultVariable()
    # Set some variables :
    self.cash_exchange_module = self.getCashExchangeModule()

    # Create a user and login as manager to populate the erp5 portal with objects for tests.
    self.createManagerAndLogin()

    self.createFunctionGroupSiteCategory()

    """
    Windows to create the BANKNOTES of 10 000 and 5000, coins 200.
    It s same to click to the fast input button.
    """
    inventory_dict_line_1 = {'id' : 'inventory_line_1',
                             'resource': self.billet_10000,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/not_defined', 'cash_status/valid') + self.variation_list,
                             'quantity': self.quantity_10000}

    inventory_dict_line_2 = {'id' : 'inventory_line_2',
                             'resource': self.piece_200,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/not_defined', 'cash_status/valid') + self.variation_list,
                             'quantity': self.quantity_200}

    inventory_dict_line_3 = {'id' : 'inventory_line_3',
                             'resource': self.billet_5000,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/p', 'cash_status/valid') + self.variation_list,
                             'quantity': self.outgoing_quantity_5000}


    inventory_dict_line_4 = {'id' : 'inventory_line_4',
                             'resource': self.piece_100,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/not_defined', 'cash_status/valid') + self.variation_list,
                             'quantity': self.outgoing_quantity_100 }



    self.line_list = line_list = [inventory_dict_line_1, inventory_dict_line_2]
    self.line_list_guichet_2 = line_list_guichet_2 = [inventory_dict_line_3, inventory_dict_line_4]
    self.guichet_1 = self.paris.surface.banque_interne.guichet_1.encaisse_des_billets_et_monnaies.entrante
    self.guichet_2 = self.paris.surface.banque_interne.guichet_1.encaisse_des_billets_et_monnaies.sortante
    self.guichet = self.paris.surface.banque_interne.guichet_1

    self.createCashInventory(source=self.guichet_1, destination=self.guichet_1, currency=self.currency_1,
                             line_list=line_list)

    self.createCashInventory(source=self.guichet_2, destination=self.guichet_2, currency=self.currency_1,
                             line_list=line_list_guichet_2)

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
    self.openCounterDate(site=self.paris.surface.banque_interne.guichet_1.encaisse_des_billets_et_monnaies.sortante)
    self.openCounter(site=self.paris.surface.banque_interne.guichet_1)


  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that CashExchange Module was created
    self.assertEqual(self.cash_exchange_module.getPortalType(), 'Cash Exchange Module')
    # check cash sorting module is empty
    self.assertEqual(len(self.cash_exchange_module.objectValues()), 0)


  def stepCheckInitialInventoryGuichet_1(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """

    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)


  def stepCheckInitialInventoryGuichet_2(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 5000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_2.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 10.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_2.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 10.0)
    # check we have 0 coin of 100 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_2.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_2.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 24.0)


  def stepCreateCashExchange(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a cash sorting document and check it
    """
    # Cash sorting has encaisse_paris for source, guichet_1 for destination, and a price cooreponding to the sum of banknote of 10000 and banknotes of 200 ( (2+3) * 10000 + (2+3) * 200 )
    self.cash_exchange = self.cash_exchange_module.newContent(
                                  id='cash_exchange_1',
                                  portal_type='Cash Exchange',
                                  source_value=self.guichet,
                                  destination_value=None,
                                  description='test',
                                  resource_value = self.currency_1,
                                  source_total_asset_price=52400.0)
    # execute tic
    self.tic()
    # check we have only one cash sorting
    self.assertEqual(len(self.cash_exchange_module.objectValues()), 1)
    # get the cash sorting document
    self.cash_exchange = getattr(self.cash_exchange_module, 'cash_exchange_1')
    # check its portal type
    self.assertEqual(self.cash_exchange.getPortalType(), 'Cash Exchange')
    # check that its source is encaisse_paris
    self.assertEqual(self.cash_exchange.getSource(), 'site/testsite/paris/surface/banque_interne/guichet_1')
    # check that its destination is guichet_1
    self.assertEqual(self.cash_exchange.getDestination(), None)

  def stepCreateValidIncomingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash exchange incoming line  with banknotes of 10000 and check it has been well created
    """
    # create the cash exchange line
    self.addCashLineToDelivery(self.cash_exchange, 'valid_incoming_line_1', 'Incoming Cash Exchange Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/valid') + self.variation_list,
            self.quantity_10000)
    # execute tic
    self.tic()
    # set source reference
    self.setDocumentSourceReference(self.cash_exchange)
    # check source reference
    self.assertNotEqual(self.cash_exchange.getSourceReference(), '')
    self.assertNotEqual(self.cash_exchange.getSourceReference(), None)
    # check there is only one line created
    self.assertEqual(len(self.cash_exchange.objectValues()), 1)
    # get the cash exchange line
    self.valid_incoming_line = getattr(self.cash_exchange, 'valid_incoming_line_1')
    # check its portal type
    self.assertEqual(self.valid_incoming_line.getPortalType(), 'Incoming Cash Exchange Line')
    # check the resource is banknotes of 10000
    self.assertEqual(self.valid_incoming_line.getResourceValue(), self.billet_10000)
    # chek the value of the banknote
    self.assertEqual(self.valid_incoming_line.getPrice(), 10000.0)
    # check the unit of banknote
    self.assertEqual(self.valid_incoming_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_incoming_line.objectValues()), 2)
    # now check for each variation (years 1992 and 2003)
    for variation in self.variation_list:
      # get the delivery cell
      cell = self.valid_incoming_line.getCell('emission_letter/not_defined', variation, 'cash_status/valid')
      # chek portal types
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      # check the source vault is encaisse_paris
      self.assertEqual(cell.getBaobabSource(), None)
      # check the destination vault is guichet_1
      self.assertEqual(cell.getBaobabDestination(), 'site/testsite/paris/surface/banque_interne/guichet_1/encaisse_des_billets_et_monnaies/entrante')
      if cell.getId() == 'movement_0_0_0':
        # check the quantity of banknote for year 1992 is 2
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity of banknote for year 2003 is 3
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

    self.addCashLineToDelivery(self.cash_exchange, 'valid_incoming_line_2', 'Incoming Cash Exchange Line', self.piece_200,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/valid') + self.variation_list,
            self.quantity_200)
    # execute tic
    self.tic()
    # check there is only one line created
    self.assertEqual(len(self.cash_exchange.objectValues()), 2)
    # get the cash exchange line
    self.valid_incoming_line = getattr(self.cash_exchange, 'valid_incoming_line_2')
    # check its portal type
    self.assertEqual(self.valid_incoming_line.getPortalType(), 'Incoming Cash Exchange Line')
    # check the resource is banknotes of 10000
    self.assertEqual(self.valid_incoming_line.getResourceValue(), self.piece_200)
    # chek the value of the banknote
    self.assertEqual(self.valid_incoming_line.getPrice(), 200.0)
    # check the unit of banknote
    self.assertEqual(self.valid_incoming_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_incoming_line.objectValues()), 2)
    # now check for each variation (years 1992 and 2003)
    for variation in self.variation_list:
      # get the delivery cell
      cell = self.valid_incoming_line.getCell('emission_letter/not_defined', variation, 'cash_status/valid')
      # chek portal types
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.piece_200)
      # check the source vault is encaisse_paris
      self.assertEqual(cell.getBaobabSource(), None)
      # check the destination vault is guichet_1
      self.assertEqual(cell.getBaobabDestination(), 'site/testsite/paris/surface/banque_interne/guichet_1/encaisse_des_billets_et_monnaies/entrante')
      if cell.getId() == 'movement_0_0_0':
        # check the quantity of banknote for year 1992 is 2
        self.assertEqual(cell.getQuantity(), 5.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity of banknote for year 2003 is 3
        self.assertEqual(cell.getQuantity(), 7.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())



  def stepCheckSubTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the amount after the creation of cash exchange line 1
    """
    # Check number of lines
    self.assertEqual(len(self.cash_exchange.objectValues()), 2)
    # Check quantity of banknotes (2 for 1992 and 3 for 2003)
    self.assertEqual(self.cash_exchange.getTotalQuantity(fast=0, portal_type="Incoming Cash Exchange Line"), 17.0)
    # Check the total price
    self.assertEqual(self.cash_exchange.getTotalPrice(fast=0, portal_type="Incoming Cash Exchange Line"), 10000 * 3.0 + 10000 * 2.0 + 200 * 5.0 + 200 * 7.0)


  def stepCreateValidOutgoingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash sorting outgoing line wiht banknotes of 200 and check it has been well created
    """
    # create the line
    self.addCashLineToDelivery(self.cash_exchange, 'valid_outgoing_line_1', 'Outgoing Cash Exchange Line', self.billet_5000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/valid') + self.variation_list,
            self.outgoing_quantity_5000)
    # execute tic
    self.tic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.cash_exchange.objectValues()), 3)
    # get the second cash exchange line
    self.valid_outgoing_line = getattr(self.cash_exchange, 'valid_outgoing_line_1')
    # check portal types
    self.assertEqual(self.valid_outgoing_line.getPortalType(), 'Outgoing Cash Exchange Line')
    # check the resource is coin of 200
    self.assertEqual(self.valid_outgoing_line.getResourceValue(), self.billet_5000)
    # check the value of coin
    self.assertEqual(self.valid_outgoing_line.getPrice(), 5000.0)
    # check the unit of coin
    self.assertEqual(self.valid_outgoing_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_outgoing_line.objectValues()), 2)
    for variation in self.variation_list:
      # get the delivery  cell
      cell = self.valid_outgoing_line.getCell('emission_letter/p', variation, 'cash_status/valid')
      # check the portal type
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      # check the source vault is encaisse_paris
      self.assertEqual(cell.getBaobabSource(), 'site/testsite/paris/surface/banque_interne/guichet_1/encaisse_des_billets_et_monnaies/sortante')
      # check the destination vault is guichet_1
      self.assertEqual(cell.getBaobabDestination(), None)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity for coin for year 1992 is 5
        self.assertEqual(cell.getQuantity(), 4.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity for coin for year 2003 is 7
        self.assertEqual(cell.getQuantity(), 6.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

    # create the line for coins
    self.addCashLineToDelivery(self.cash_exchange, 'valid_outgoing_line_2', 'Outgoing Cash Exchange Line', self.piece_100,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/valid') + self.variation_list,
            self.outgoing_quantity_100)
    # execute tic
    self.tic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.cash_exchange.objectValues()), 4)
    # get the second cash exchange line
    self.valid_outgoing_line = getattr(self.cash_exchange, 'valid_outgoing_line_2')
    # check portal types
    self.assertEqual(self.valid_outgoing_line.getPortalType(), 'Outgoing Cash Exchange Line')
    # check the resource is coin of 200
    self.assertEqual(self.valid_outgoing_line.getResourceValue(), self.piece_100)
    # check the value of coin
    self.assertEqual(self.valid_outgoing_line.getPrice(), 100.0)
    # check the unit of coin
    self.assertEqual(self.valid_outgoing_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_outgoing_line.objectValues()), 2)
    for variation in self.variation_list:
      # get the delivery  cell
      cell = self.valid_outgoing_line.getCell('emission_letter/not_defined', variation, 'cash_status/valid')
      # check the portal type
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      # check the source vault is encaisse_paris
      self.assertEqual(cell.getBaobabSource(), 'site/testsite/paris/surface/banque_interne/guichet_1/encaisse_des_billets_et_monnaies/sortante')
      # check the destination vault is guichet_1
      self.assertEqual(cell.getBaobabDestination(), None)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity for coin for year 1992 is 5
        self.assertEqual(cell.getQuantity(), 24.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity for coin for year 2003 is 7
        self.assertEqual(cell.getQuantity(), 0.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())




  def stepCheckTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the total after the creation of the two cash exchange lines
    """
    # Check number of lines (line1 + line2)
    self.assertEqual(len(self.cash_exchange.objectValues()), 4)
    # Check quantity, banknotes : 2 for 1992 and 3 for 2003, coin : 5 for 1992 and 7 for 2003
    self.assertEqual(self.cash_exchange.getTotalQuantity(fast=0, portal_type="Outgoing Cash Exchange Line"), 34.0)
    # check the total price
    self.assertEqual(self.cash_exchange.getTotalPrice(fast=0, portal_type="Outgoing Cash Exchange Line"), 5000 * 4.0 + 100 * 0.0 + 5000 * 6.0 + 100 * 24.0)




  def stepDeliverCashExchange(self, sequence=None, sequence_list=None, **kwd):
    """
    Deliver the cash sorting with a good user
    and check that the deliver of a cash tranfer have achieved
    """
    #self.cash_exchange.setSourceTotalAssetPrice('52400.0')
    #     self.security_manager = AccessControl.getSecurityManager()
    #     self.user = self.security_manager.getUser()
    # do the workflow transition "deliver_action"
    self.workflow_tool.doActionFor(self.cash_exchange, 'deliver_action', wf_id='cash_exchange_workflow')
    # execute tic
    self.tic()
    # get state of cash sorting
    state = self.cash_exchange.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_exchange, name='history', wf_id='cash_exchange_workflow')

  def stepCheckFinalInventoryGuichet_1(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at source (vault encaisse_paris) after deliver of the cash sorting
    """

    # check we have 10 banknote of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 10.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 10.0)
    # check we ahve 24 coins of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 24.0)



  def stepCheckFinalInventoryGuichet_2(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at source (vault encaisse_paris) after deliver of the cash sorting
    """
    # check we have no banknote any more
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_2.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_2.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    # check no coins any more
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_2.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_2.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 0.0)



  def stepDelCashExchange(self, sequence=None, sequence_list=None, **kwd):
    """
    Delete the invalid vault_transfer line previously create
    """
    self.cash_exchange_module.deleteContent('cash_exchange_1')

  def stepResetInventory(self,
               sequence=None, sequence_list=None, **kwd):
    node = self.guichet_2
    line_list = self.line_list_guichet_2
    self.resetInventory(destination=node, currency=self.currency_1,
                        line_list=line_list,extra_id='_reset_out')

  def stepDeliverFails(self, sequence=None, sequence_list=None, **kwd):
    message = self.assertWorkflowTransitionFails(self.cash_exchange,
              'cash_exchange_workflow','deliver_action')
    self.assertTrue(message.find('Insufficient balance')>=0)


  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingCashExchange(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialInventoryGuichet_1 ' \
                    + 'CheckInitialInventoryGuichet_2 ' \
                    + 'CreateCashExchange ' \
                    + 'CreateValidIncomingLine CheckSubTotal ' \
                    + 'CreateValidOutgoingLine ' \
                    + 'Tic CheckTotal ' \
                    + 'CheckInitialInventoryGuichet_1 CheckInitialInventoryGuichet_2 ' \
                    + 'ResetInventory Tic ' \
                    + 'DeliverFails Tic ' \
                    + 'DeleteResetInventory Tic ' \
                    + 'DeliverCashExchange Tic ' \
                    + 'CheckFinalInventoryGuichet_1 ' \
                    + 'CheckFinalInventoryGuichet_2'
    sequence_list.addSequenceString(sequence_string)
    # play the sequence
    sequence_list.play(self)

