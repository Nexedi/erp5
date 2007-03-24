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

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

# Define how to launch the script if we don't use runUnitTest script
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))



class TestERP5BankingCashToCurrencySale(TestERP5BankingMixin, ERP5TypeTestCase):
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
  outgoing_quantity_100 = {'variation/1992':200,'variation/2003':0}

  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingCashToCurrencySale"

  def getCashToCurrencySaleModule(self):
    """
    Return the Cash To Currency Sale Module
    """
    return getattr(self.getPortal(), 'cash_to_currency_sale_module', None)


  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    self.initDefaultVariable()
    # Set some variables :
    self.cash_to_currency_sale_module = self.getCashToCurrencySaleModule()

    # Create a user and login as manager to populate the erp5 portal with objects for tests.
    self.createManagerAndLogin()

    self.createFunctionGroupSiteCategory()
    self.createBanknotesAndCoins()

    """
    Windows to create the BANKNOTES of 10 000 and 5000, coins 200.
    It s same to click to the fast input button.
    """

    inventory_dict_line_1 = {'id' : 'inventory_line_1',
                             'resource': self.usd_billet_20,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/not_defined', 'cash_status/not_defined') + self.usd_variation_list,
                             'variation_list': self.usd_variation_list,
                             'quantity': self.quantity_usd_20}

    line_list_sortante = [inventory_dict_line_1]

    self.guichet_entrante = self.paris.surface.banque_interne.guichet_1.encaisse_des_billets_et_monnaies.entrante
    self.guichet_sortante= self.paris.surface.banque_interne.guichet_1.encaisse_des_devises.usd.sortante
    self.guichet = self.paris.surface.banque_interne.guichet_1


    self.createCashInventory(source=None, destination=self.guichet_sortante, currency=self.currency_2,
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
    self.openCounterDate(site=self.paris.surface.banque_interne.guichet_1)



  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that CashToCurrencySale Module was created
    self.assertEqual(self.cash_to_currency_sale_module.getPortalType(), 'Cash To Currency Sale Module')
    # check cash sorting module is empty
    self.assertEqual(len(self.cash_to_currency_sale_module.objectValues()), 0)


  def stepCheckInitialInventoryGuichet_Entrante(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """

    self.simulation_tool = self.getSimulationTool()
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_entrante.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_entrante.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    # check we have 0 coin of 100 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_entrante.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_entrante.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 0.0)



  def stepCheckInitialInventoryGuichet_Sortante(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 0 banknotes of 10000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_sortante.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_sortante.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 5.0)





  def stepCreateCashToCurrencySale(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a cash sorting document and check it
    """
    # Create Cash sorting 
    self.cash_to_currency_sale = self.cash_to_currency_sale_module.newContent(
                                  id='cash_to_currency_sale_1', 
                                  portal_type='Cash To Currency Sale', 
                                  source_value=self.guichet, 
                                  destination_value=None, 
                                  description='test',
                                  resource_value = self.currency_2, 
                                  source_total_asset_price=100.0, 
                                  discount = 3000.0, quantity = 70000.0)
    # execute tic
    self.stepTic()
    # check we have only one cash sorting
    self.assertEqual(len(self.cash_to_currency_sale_module.objectValues()), 1)
    # get the cash sorting document
    self.cash_to_currency_sale = getattr(self.cash_to_currency_sale_module, 'cash_to_currency_sale_1')
    # check its portal type
    self.assertEqual(self.cash_to_currency_sale.getPortalType(), 'Cash To Currency Sale')
    # check that its source is encaisse_paris
    self.assertEqual(self.cash_to_currency_sale.getSource(), 'site/testsite/paris/surface/banque_interne/guichet_1')
    # check that its destination is guichet_1
    self.assertEqual(self.cash_to_currency_sale.getDestination(), None)
    self.setDocumentSourceReference(self.cash_to_currency_sale)


  #def stepCreateValidIncomingLine(self, sequence=None, sequence_list=None, **kwd):
  def stepCreateValidIncomingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash exchange incoming line  with banknotes of 10000 and check it has been well created
    """
    # create the cash exchange line
    self.addCashLineToDelivery(self.cash_to_currency_sale, 'valid_incoming_line_1', 'Incoming Cash To Currency Sale Line', self.billet_5000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/valid') + self.variation_list,
            self.outgoing_quantity_5000)
    # execute tic
    self.stepTic()
    # check there is only one line created
    self.assertEqual(len(self.cash_to_currency_sale.objectValues()), 1)
    # get the cash exchange line
    self.valid_incoming_line = getattr(self.cash_to_currency_sale, 'valid_incoming_line_1')
    # check its portal type
    self.assertEqual(self.valid_incoming_line.getPortalType(), 'Incoming Cash To Currency Sale Line')
    self.assertEqual(self.valid_incoming_line.getResourceValue(), self.billet_5000)
    self.assertEqual(self.valid_incoming_line.getPrice(), 5000.0)
    self.assertEqual(self.valid_incoming_line.getQuantityUnit(), 'unit')
    self.assertEqual(len(self.valid_incoming_line.objectValues()), 2)
    for variation in self.variation_list:
      # get the delivery cell
      cell = self.valid_incoming_line.getCell('emission_letter/not_defined', variation, 'cash_status/valid')
      # chek portal types
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      self.assertEqual(cell.getResourceValue(), self.billet_5000)
      self.assertEqual(cell.getBaobabSource(), None)
      # check the destination vault is guichet_1
      self.assertEqual(cell.getBaobabDestination(), 'site/testsite/paris/surface/banque_interne/guichet_1/encaisse_des_billets_et_monnaies/entrante')
      if cell.getId() == 'movement_0_0_0':
        self.assertEqual(cell.getQuantity(), 4.0)
      elif cell.getId() == 'movement_0_1_0':
        self.assertEqual(cell.getQuantity(), 6.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

    self.addCashLineToDelivery(self.cash_to_currency_sale, 'valid_incoming_line_2', 'Incoming Cash To Currency Sale Line', self.piece_100,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/valid') + self.variation_list,
            self.outgoing_quantity_100)
    # execute tic
    self.stepTic()
    # check there is only one line created
    self.assertEqual(len(self.cash_to_currency_sale.objectValues()), 2)
    # get the cash exchange line
    self.valid_incoming_line = getattr(self.cash_to_currency_sale, 'valid_incoming_line_2')
    # check its portal type
    self.assertEqual(self.valid_incoming_line.getPortalType(), 'Incoming Cash To Currency Sale Line')
    self.assertEqual(self.valid_incoming_line.getResourceValue(), self.piece_100)
    # chek the value of the banknote
    self.assertEqual(self.valid_incoming_line.getPrice(), 100.0)
    # check the unit of banknote
    self.assertEqual(self.valid_incoming_line.getQuantityUnit(), 'unit')
    self.assertEqual(len(self.valid_incoming_line.objectValues()), 2)
    for variation in self.variation_list:
      # get the delivery cell
      cell = self.valid_incoming_line.getCell('emission_letter/not_defined', variation, 'cash_status/valid')
      # chek portal types
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      self.assertEqual(cell.getResourceValue(), self.piece_100)
      self.assertEqual(cell.getBaobabSource(), None)
      # check the destination vault is guichet_1
      self.assertEqual(cell.getBaobabDestination(), 'site/testsite/paris/surface/banque_interne/guichet_1/encaisse_des_billets_et_monnaies/entrante')
      if cell.getId() == 'movement_0_0_0':
        self.assertEqual(cell.getQuantity(), 200.0)
      elif cell.getId() == 'movement_0_1_0':
        self.assertEqual(cell.getQuantity(), 0.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())



  def stepCheckSubTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the amount after the creation of cash exchange line 1
    """
    # Check number of lines
    self.assertEqual(len(self.cash_to_currency_sale.objectValues()), 2)
    self.assertEqual(self.cash_to_currency_sale.getTotalQuantity(deliveryLineType="Incoming Cash To Currency Sale Line"), 210)
    # Check the total price
    self.assertEqual(self.cash_to_currency_sale.getTotalPrice(deliveryLineType="Incoming Cash To Currency Sale Line"), 5000 * 4.0 + 100 * 0.0 + 5000 * 6.0 + 100 * 200.0)


  def stepCreateValidOutgoingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash exchange incoming line  with banknotes of 10000 and check it has been well created
    """
    # create the cash exchange line
    self.addCashLineToDelivery(self.cash_to_currency_sale,
         'valid_outgoing_line_1', 'Outgoing Cash To Currency Sale Line',
         self.usd_billet_20,
         ('emission_letter', 'cash_status', 'variation'),
         ('emission_letter/not_defined', 'cash_status/not_defined') + \
         self.usd_variation_list,
         self.quantity_usd_20,
         variation_list = self.usd_variation_list)
    # execute tic
    self.stepTic()
    # check there is only one line created
    self.assertEqual(len(self.cash_to_currency_sale.objectValues()), 3)
    # get the cash exchange line
    self.valid_outgoing_line = getattr(self.cash_to_currency_sale, 'valid_outgoing_line_1')
    # check its portal type
    self.assertEqual(self.valid_outgoing_line.getPortalType(), 'Outgoing Cash To Currency Sale Line')
    # check the resource is banknotes of 20
    self.assertEqual(self.valid_outgoing_line.getResourceValue(), self.usd_billet_20)
    # chek the value of the banknote
    self.assertEqual(self.valid_outgoing_line.getPrice(), 20.0)
    self.assertEqual(self.valid_outgoing_line.getQuantityUnit(), 'unit')
    self.assertEqual(len(self.valid_outgoing_line.objectValues()), 1)
    for variation in self.usd_variation_list:
      cell = self.valid_outgoing_line.getCell('emission_letter/not_defined', variation, 'cash_status/not_defined')
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      self.assertEqual(cell.getResourceValue(), self.usd_billet_20)
      self.assertEqual(cell.getBaobabSource(), 'site/testsite/paris/surface/banque_interne/guichet_1/encaisse_des_devises/usd/sortante')
      self.assertEqual(cell.getBaobabDestination(), None)
      if cell.getId() == 'movement_0_0_0':
        self.assertEqual(cell.getQuantity(), 5.0)

      else:
        self.fail('Wrong cell created : %s' % cell.getId())

  def stepCheckTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the total after the creation of the two cash exchange lines
    """
    # Check number of lines (line1 + line2)
    self.assertEqual(len(self.cash_to_currency_sale.objectValues()), 3)
    # Check quantity, banknotes : 2 for 1992 and 3 for 2003, coin : 5 for 1992 and 7 for 2003
    self.assertEqual(self.cash_to_currency_sale.getTotalQuantity(deliveryLineType="Outgoing Cash To Currency Sale Line"), 5.0)
    # check the total price
    self.assertEqual(self.cash_to_currency_sale.getTotalPrice(deliveryLineType="Outgoing Cash To Currency Sale Line"), 20 * 5.0)

  def stepDeliverCashToCurrencySale(self, sequence=None, sequence_list=None, **kwd):
    """
    Deliver the cash sorting with a good user
    and check that the deliver of a cash tranfer have achieved
    """
    #self.cash_to_currency_sale.setSourceTotalAssetPrice('52400.0')
    #     self.security_manager = AccessControl.getSecurityManager()
    #     self.user = self.security_manager.getUser()
    # do the workflow transition "deliver_action"
    self.workflow_tool.doActionFor(self.cash_to_currency_sale, 'deliver_action', wf_id='cash_to_currency_sale_workflow')
    # execute tic
    self.stepTic()
    # get state of cash sorting
    state = self.cash_to_currency_sale.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_to_currency_sale, name='history', wf_id='cash_to_currency_sale_workflow')
    # check len of len workflow history is 6
    self.assertEqual(len(workflow_history), 3)






  def stepCheckFinalInventoryGuichet_Entrante(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """

    self.simulation_tool = self.getSimulationTool()
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_entrante.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 10.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_entrante.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 10.0)
    # check we have 0 coin of 100 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_entrante.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 200.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_entrante.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 200.0)



  def stepCheckFinalInventoryGuichet_Sortante(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 0 banknotes of 10000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_sortante.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_sortante.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 0.0)



  def stepDelCashToCurrencySale(self, sequence=None, sequence_list=None, **kwd):
    """
    Delete the invalid vault_transfer line previously create
    """
    self.cash_to_currency_sale_module.deleteContent('cash_to_currency_sale_1')



  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingCashToCurrencySale(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run: return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialInventoryGuichet_Entrante ' \
                    + 'CheckInitialInventoryGuichet_Sortante ' \
                    + 'CreateCashToCurrencySale ' \
                    + 'CreateValidIncomingLine CheckSubTotal ' \
                    + 'CreateValidOutgoingLine ' \
                    + 'Tic CheckTotal ' \
                    + 'DeliverCashToCurrencySale Tic ' \
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
    suite.addTest(unittest.makeSuite(TestERP5BankingCashToCurrencySale))
    return suite
