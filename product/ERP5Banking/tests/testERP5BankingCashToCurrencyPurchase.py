##############################################################################
#
# Copyright (c) 2005-2006 Nexedi SARL and Contributors. All Rights Reserved.
#                   Aurelien Calonne <aurel@nexedi.com>
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



class TestERP5BankingCashToCurrencyPurchase(TestERP5BankingMixin, ERP5TypeTestCase):
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

  login = PortalTestCase.login

  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet

  outgoing_quantity_5000 = {'variation/1992':4,'variation/2003':6}
  outgoing_quantity_100 = {'variation/1992':120,'variation/2003':0}

  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingCashToCurrencyPurchase"

  def getCashToCurrencyPurchaseModule(self):
    """
    Return the Cash To Currency Purchase Module
    """
    return getattr(self.getPortal(), 'cash_to_currency_purchase_module', None)


  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    self.initDefaultVariable()
    # Set some variables :
    self.cash_to_currency_purchase_module = self.getCashToCurrencyPurchaseModule()

    # Create a user and login as manager to populate the erp5 portal with objects for tests.
    self.createManagerAndLogin()

    self.createFunctionGroupSiteCategory()
    self.createBanknotesAndCoins()

    """
    Windows to create the BANKNOTES of 10 000 and 5000, coins 200.
    It s same to click to the fast input button.
    """

    inventory_dict_line_1 = {'id' : 'inventory_line_1',
                             'resource': self.billet_5000,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/p', 'cash_status/valid') + self.variation_list,
                             'quantity': self.outgoing_quantity_5000}


    inventory_dict_line_2 = {'id' : 'inventory_line_2',
                             'resource': self.piece_100,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/not_defined', 'cash_status/valid') + self.variation_list,
                             'quantity': self.outgoing_quantity_100 }




    line_list_sortante = [inventory_dict_line_1, inventory_dict_line_2]

    self.guichet_entrante = self.paris.surface.banque_interne.guichet_1.encaisse_des_devises.usd.sortante
    self.guichet_sortante= self.paris.surface.banque_interne.guichet_1.encaisse_des_billets_et_monnaies.sortante
    self.guichet = self.paris.surface.banque_interne.guichet_1


    self.createCashInventory(source=None, destination=self.guichet_sortante, currency=self.currency_1,
                             line_list=line_list_sortante)

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
    self.login('super_user')
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
    # check that CashToCurrencyPurchase Module was created
    self.assertEqual(self.cash_to_currency_purchase_module.getPortalType(), 'Cash To Currency Purchase Module')
    # check cash sorting module is empty
    self.assertEqual(len(self.cash_to_currency_purchase_module.objectValues()), 0)


  def stepCheckInitialInventoryGuichet_Entrante(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """

    self.simulation_tool = self.getSimulationTool()
    # check we have 0 banknotes of 10000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_entrante.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_entrante.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 0.0)




  def stepCheckInitialInventoryGuichet_Sortante(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 0 banknotes of 10000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_sortante.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_sortante.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 0 coin of 200 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_sortante.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_sortante.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)

    # check we have 10 banknotes of 5000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_sortante.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 10.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_sortante.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 10.0)
    # check we have 24 coin of 100 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_sortante.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 120.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_sortante.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 120.0)


  def stepCreateCashToCurrencyPurchase(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a cash sorting document and check it
    """
    # Cash sorting has encaisse_paris for source, guichet_1 for destination, and a price cooreponding to the sum of banknote of 10000 and banknotes of 200 ( (2+3) * 10000 + (2+3) * 200 )
    self.cash_to_currency_purchase = self.cash_to_currency_purchase_module.newContent(
                                           id='cash_to_currency_purchase_1', 
                                           portal_type='Cash To Currency Purchase', 
                                           source_value=self.guichet, 
                                           destination_value=None, 
                                           description='test',
                                           resource_value = self.currency_2, 
                                           source_total_asset_price=100.0)
    # execute tic
    self.stepTic()
    # check we have only one cash sorting
    self.assertEqual(len(self.cash_to_currency_purchase_module.objectValues()), 1)
    # get the cash sorting document
    self.cash_to_currency_purchase = getattr(self.cash_to_currency_purchase_module, 'cash_to_currency_purchase_1')
    # check its portal type
    self.assertEqual(self.cash_to_currency_purchase.getPortalType(), 'Cash To Currency Purchase')
    # check that its source is encaisse_paris
    self.assertEqual(self.cash_to_currency_purchase.getSource(), 'site/testsite/paris/surface/banque_interne/guichet_1')
    # check that its destination is guichet_1
    self.assertEqual(self.cash_to_currency_purchase.getDestination(), None)
    self.setDocumentSourceReference(self.cash_to_currency_purchase)
    # Check carrefully the script CurrencyPurchase_getQuantity
    script = self.cash_to_currency_purchase.CurrencyPurchase_getQuantity
    self.assertEqual(script(),65000)
    self.cash_to_currency_purchase.setDiscountRatio(0.01)
    self.assertEqual(script(),64350)
    self.cash_to_currency_purchase.setDiscountRatio(None)
    self.cash_to_currency_purchase.setDiscount(3000)
    self.assertEqual(script(),62000)
    # Check that we can define a specific rate
    self.cash_to_currency_purchase.setCurrencyExchangeRate(660)
    self.assertEqual(script(),63000)
    self.cash_to_currency_purchase.setCurrencyExchangeRate(None)
    self.assertEqual(script(),62000)

  #def stepCreateValidIncomingLine(self, sequence=None, sequence_list=None, **kwd):
  def stepCreateValidIncomingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash exchange incoming line  with banknotes of 10000 and check it has been well created
    """
    # create the cash exchange line
    self.addCashLineToDelivery(self.cash_to_currency_purchase, 'valid_incoming_line_1', 'Incoming Cash To Currency Purchase Line', self.usd_billet_20,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/not_defined') + self.usd_variation_list,
            self.quantity_usd_20,
            variation_list = self.usd_variation_list)
    # execute tic
    self.stepTic()
    # check there is only one line created
    self.assertEqual(len(self.cash_to_currency_purchase.objectValues()), 1)
    # get the cash exchange line
    self.valid_incoming_line = getattr(self.cash_to_currency_purchase, 'valid_incoming_line_1')
    # check its portal type
    self.assertEqual(self.valid_incoming_line.getPortalType(), 'Incoming Cash To Currency Purchase Line')
    # check the resource is banknotes of 20
    self.assertEqual(self.valid_incoming_line.getResourceValue(), self.usd_billet_20)
    # chek the value of the banknote
    self.assertEqual(self.valid_incoming_line.getPrice(), 20.0)
    # check the unit of banknote
    self.assertEqual(self.valid_incoming_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_incoming_line.objectValues()), 1)
    # now check for each variation (years 1992 and 2003)
    for variation in self.usd_variation_list:
      # get the delivery cell
      cell = self.valid_incoming_line.getCell('emission_letter/not_defined', variation, 'cash_status/not_defined')
      # chek portal types
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.usd_billet_20)
      # check the source vault is encaisse_paris
      self.assertEqual(cell.getBaobabSource(), None)
      # check the destination vault is guichet_1
      self.assertEqual(cell.getBaobabDestination(), 'site/testsite/paris/surface/banque_interne/guichet_1/encaisse_des_devises/usd/sortante')
      if cell.getId() == 'movement_0_0_0':
        # check the quantity of banknote 20
        self.assertEqual(cell.getQuantity(), 5.0)

      else:
        self.fail('Wrong cell created : %s' % cell.getId())





  def stepCheckSubTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the amount after the creation of cash exchange line 1
    """
    # Check number of lines
    self.assertEqual(len(self.cash_to_currency_purchase.objectValues()), 1)
    # Check quantity of banknotes (2 for 1992 and 3 for 2003)
    self.assertEqual(self.cash_to_currency_purchase.getTotalQuantity(deliveryLineType="Incoming Cash To Currency Purchase Line"), 5.0)
    # Check the total price
    self.assertEqual(self.cash_to_currency_purchase.getTotalPrice(deliveryLineType="Incoming Cash To Currency Purchase Line"), 20 * 5.0)


  def stepCreateValidOutgoingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash sorting outgoing line wiht banknotes of 200 and check it has been well created
    """
    # create the line
    self.addCashLineToDelivery(self.cash_to_currency_purchase, 'valid_outgoing_line_1', 'Outgoing Cash To Currency Purchase Line', self.billet_5000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/valid') + self.variation_list,
            self.outgoing_quantity_5000)
    # execute tic
    self.stepTic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.cash_to_currency_purchase.objectValues()), 2)
    # get the second cash exchange line
    self.valid_outgoing_line = getattr(self.cash_to_currency_purchase, 'valid_outgoing_line_1')
    # check portal types
    self.assertEqual(self.valid_outgoing_line.getPortalType(), 'Outgoing Cash To Currency Purchase Line')
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
    self.addCashLineToDelivery(self.cash_to_currency_purchase, 'valid_outgoing_line_2', 'Outgoing Cash To Currency Purchase Line', self.piece_100,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/valid') + self.variation_list,
            self.outgoing_quantity_100)
    # execute tic
    self.stepTic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.cash_to_currency_purchase.objectValues()), 3)
    # get the second cash exchange line
    self.valid_outgoing_line = getattr(self.cash_to_currency_purchase, 'valid_outgoing_line_2')
    # check portal types
    self.assertEqual(self.valid_outgoing_line.getPortalType(), 'Outgoing Cash To Currency Purchase Line')
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
        self.assertEqual(cell.getQuantity(), 120.0)
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
    self.assertEqual(len(self.cash_to_currency_purchase.objectValues()), 3)
    # Check quantity, banknotes : 2 for 1992 and 3 for 2003, coin : 5 for 1992 and 7 for 2003
    self.assertEqual(self.cash_to_currency_purchase.getTotalQuantity(deliveryLineType="Outgoing Cash To Currency Purchase Line"), 130.0)
    # check the total price
    self.assertEqual(self.cash_to_currency_purchase.getTotalPrice(deliveryLineType="Outgoing Cash To Currency Purchase Line"), 5000 * 4.0 + 100 * 0.0 + 5000 * 6.0 + 100 * 120.0)



  def stepDeliverCashToCurrencyPurchase(self, sequence=None, sequence_list=None, **kwd):
    """
    Deliver the cash sorting with a good user
    and check that the deliver of a cash tranfer have achieved
    """
    self.workflow_tool.doActionFor(self.cash_to_currency_purchase, 'deliver_action', wf_id='cash_to_currency_purchase_workflow')
    # execute tic
    self.stepTic()
    # get state of cash sorting
    state = self.cash_to_currency_purchase.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_to_currency_purchase, name='history', wf_id='cash_to_currency_purchase_workflow')
    # check len of len workflow history is 6
    self.assertEqual(len(workflow_history), 3)






  def stepCheckFinalInventoryGuichet_Entrante(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 0 banknotes of 10000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_entrante.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_entrante.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 5.0)




  def stepCheckFinalInventoryGuichet_Sortante(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at source (vault encaisse_paris) after deliver of the cash sorting
    """

    # check we have 14 coin of 5000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_sortante.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_sortante.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    # check we have 12 coins of 100
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_sortante.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_sortante.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 0.0)



  def stepDelCashToCurrencyPurchase(self, sequence=None, sequence_list=None, **kwd):
    """
    Delete the invalid vault_transfer line previously create
    """
    self.cash_to_currency_purchase_module.deleteContent('cash_to_currency_purchase_1')



  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingCashToCurrencyPurchase(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run: return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialInventoryGuichet_Entrante ' \
                    + 'CheckInitialInventoryGuichet_Sortante ' \
                    + 'CreateCashToCurrencyPurchase ' \
                    + 'CreateValidIncomingLine CheckSubTotal ' \
                    + 'CreateValidOutgoingLine ' \
                    + 'Tic CheckTotal ' \
                    + 'DeliverCashToCurrencyPurchase Tic ' \
                    + 'CheckFinalInventoryGuichet_Entrante ' \
                    + 'CheckFinalInventoryGuichet_Sortante'
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
    suite.addTest(unittest.makeSuite(TestERP5BankingCashToCurrencyPurchase))
    return suite
