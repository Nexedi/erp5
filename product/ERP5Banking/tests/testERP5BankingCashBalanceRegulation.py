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



class TestERP5BankingCashBalanceRegulation(TestERP5BankingMixin, ERP5TypeTestCase):
  """
  Unit test for the cash balance regulation module
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
  outgoing_quantity_100 = {'variation/1992':24,'variation/2003':0}

  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingCashBalanceRegulation"
  
  def getCashBalanceRegulationModule(self):
    """
    Return the Cash Balance Regulation Module
    """
    return getattr(self.getPortal(), 'cash_balance_regulation_module', None)


  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    self.initDefaultVariable()
    # Set some variables : 
    self.cash_balance_regulation_module = self.getCashBalanceRegulationModule()

    # Create a user and login as manager to populate the erp5 portal with objects for tests.
    self.createManagerAndLogin()

    self.createFunctionGroupSiteCategory()
    self.createBanknotesAndCoins()

    """
    Windows to create the BANKNOTES of 10 000 and 5000, coins 5000.
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
                             'variation_value': ('emission_letter/not_defined', 'cash_status/valid') + self.variation_list,
                             'quantity': self.quantity_5000}

    
    line_list = [inventory_dict_line_1, inventory_dict_line_2, inventory_dict_line_3]
    """
    self.encaisse_tri= self.paris.surface.salle_de_tri.encaisse_des_billets_et_monnaies
    self.guichet_1 = self.paris.caveau.reserve.encaisse_des_billets_et_monnaies
    self.guichet_1 = self.paris.caveau.externes.encaisse_des_externes
    self.guichet_1 = self.paris.caveau.auxiliaire.encaisse_des_billets_et_monnaies
    """
    self.guichet_1 = self.paris.surface.banque_interne.guichet_1.encaisse_des_billets_et_monnaies
    self.createCashInventory(source=self.guichet_1, destination=self.guichet_1, currency=self.currency_1, line_list=line_list)
    
    self.guichet_caveau = self.paris.caveau.auxiliaire.encaisse_des_billets_et_monnaies
    self.createCashInventory(source=self.guichet_caveau, destination=self.guichet_caveau, currency=self.currency_1, line_list=line_list)
    
    self.guichet_salletri = self.paris.surface.salle_tri.encaisse_des_billets_et_monnaies
    self.createCashInventory(source=self.guichet_salletri, destination=self.guichet_salletri, currency=self.currency_1, line_list=line_list)
        
    self.guichet_surface = self.paris.surface.caisse_courante.encaisse_des_billets_et_monnaies
    self.createCashInventory(source=self.guichet_surface, destination=self.guichet_surface, currency=self.currency_1, line_list=line_list)

    # now we need to create a user as Manager to do the test
    # in order to have an assigment defined which is used to do transition
    # Create an Organisation that will be used for users assignment
    self.checkUserFolderType()
    self.organisation = self.organisation_module.newContent(id='paris', portal_type='Organisation',
                          function='banking', group='baobab',  site='testsite/paris')
    # define the user
    user_dict = {
        'super_user' : [['Manager'], self.organisation, 'banking/comptable', 'baobab', 'testsite/paris']
      }
    # call method to create this user
    self.createERP5Users(user_dict)
    self.logout()
    self.login('super_user')
    # open counter date and counter
    self.openCounterDate(site=self.paris)



  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that CashBalance Regulation Module was created
    self.assertEqual(self.cash_balance_regulation_module.getPortalType(), 'Cash Balance Regulation Module')
    # check cash sorting module is empty
    self.assertEqual(len(self.cash_balance_regulation_module.objectValues()), 0)


  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
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
    # check we have 24 banknotes of 5000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_1.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_1.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    # check we have 24 banknotes of 5000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_1.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_1.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 0.0)




  def stepCheckInitialInventoryCaveau(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    # check we have 24 banknotes of 5000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    # check we have 24 banknotes of 5000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 0.0)


  def stepCheckInitialInventorySalleTri(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    # check we have 24 banknotes of 5000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    # check we have 24 banknotes of 5000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 0.0)


  def stepCheckInitialInventorySurface(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    # check we have 24 banknotes of 5000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    # check we have 24 banknotes of 5000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 0.0)




  def stepCreateCashBalanceRegulation(self, sequence=None, sequence_list=None, **kwd):
    self.cash_balance_regulation = self.cash_balance_regulation_module.newContent(
                                          id='cash_balance_regulation_1', 
                                          portal_type='Cash Balance Regulation', 
                                          source_value=self.guichet_1, 
                                          destination_value=None, 
                                          description='test',
                                          source_total_asset_price=52400.0)
    self.stepTic()
    self.assertEqual(len(self.cash_balance_regulation_module.objectValues()), 1)
    self.cash_balance_regulation = getattr(self.cash_balance_regulation_module, 'cash_balance_regulation_1')
    self.assertEqual(self.cash_balance_regulation.getPortalType(), 'Cash Balance Regulation')
    self.assertEqual(self.cash_balance_regulation.getSource(), 'site/testsite/paris/surface/banque_interne/guichet_1/encaisse_des_billets_et_monnaies')
    self.assertEqual(self.cash_balance_regulation.getDestination(), None)

  def stepCreateCashBalanceRegulationCaveau(self, sequence=None, sequence_list=None, **kwd):
    self.cash_balance_regulation = self.cash_balance_regulation_module.newContent(id='cash_balance_regulation_1', portal_type='Cash Balance Regulation', source_value=self.guichet_caveau, destination_value=None, source_total_asset_price=52400.0)
    self.stepTic()
    self.assertEqual(len(self.cash_balance_regulation_module.objectValues()), 1)
    self.cash_balance_regulation = getattr(self.cash_balance_regulation_module, 'cash_balance_regulation_1')
    self.assertEqual(self.cash_balance_regulation.getPortalType(), 'Cash Balance Regulation')
    self.assertEqual(self.cash_balance_regulation.getSource(), 'site/testsite/paris/caveau/auxiliaire/encaisse_des_billets_et_monnaies')
    self.assertEqual(self.cash_balance_regulation.getDestination(), None)
  
  def stepCreateCashBalanceRegulationSalleTri(self, sequence=None, sequence_list=None, **kwd):
    self.cash_balance_regulation = self.cash_balance_regulation_module.newContent(id='cash_balance_regulation_1', portal_type='Cash Balance Regulation', source_value=self.guichet_salletri, destination_value=None, source_total_asset_price=52400.0)
    self.stepTic()
    self.assertEqual(len(self.cash_balance_regulation_module.objectValues()), 1)
    self.cash_balance_regulation = getattr(self.cash_balance_regulation_module, 'cash_balance_regulation_1')
    self.assertEqual(self.cash_balance_regulation.getPortalType(), 'Cash Balance Regulation')
    self.assertEqual(self.cash_balance_regulation.getSource(), 'site/testsite/paris/surface/salle_tri/encaisse_des_billets_et_monnaies')
    self.assertEqual(self.cash_balance_regulation.getDestination(), None)

  def stepCreateCashBalanceRegulationSurface(self, sequence=None, sequence_list=None, **kwd):
    self.cash_balance_regulation = self.cash_balance_regulation_module.newContent(id='cash_balance_regulation_1', portal_type='Cash Balance Regulation', source_value=self.guichet_surface, destination_value=None, source_total_asset_price=52400.0)
    self.stepTic()
    self.assertEqual(len(self.cash_balance_regulation_module.objectValues()), 1)
    self.cash_balance_regulation = getattr(self.cash_balance_regulation_module, 'cash_balance_regulation_1')
    self.assertEqual(self.cash_balance_regulation.getPortalType(), 'Cash Balance Regulation')
    self.assertEqual(self.cash_balance_regulation.getSource(), 'site/testsite/paris/surface/caisse_courante/encaisse_des_billets_et_monnaies')
    self.assertEqual(self.cash_balance_regulation.getDestination(), None)






  #def stepCreateValidIncomingLine(self, sequence=None, sequence_list=None, **kwd):
  def stepCreateValidIncomingLine(self, sequence=None, sequence_list=None, check_source=1,**kwd):
    """
    Create the cash balance regulation incoming line  with banknotes of 10000 and check it has been well created
    """
    # create the cash balance regulation line
    self.addCashLineToDelivery(self.cash_balance_regulation, 'valid_incoming_line_1', 'Incoming Cash Balance Regulation Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/valid') + self.variation_list,
            self.quantity_10000)
    # execute tic
    self.stepTic()
    # check there is only one line created
    self.assertEqual(len(self.cash_balance_regulation.objectValues()), 1)
    # get the cash balance regulation line
    self.valid_incoming_line = getattr(self.cash_balance_regulation, 'valid_incoming_line_1')
    # check its portal type
    self.assertEqual(self.valid_incoming_line.getPortalType(), 'Incoming Cash Balance Regulation Line')
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
      ####if check_source:
        ####self.assertEqual(cell.getSourceValue(), self.guichet_1)
      # check the destination vault is guichet_1
      self.assertEqual(cell.getDestinationValue(), self.cash_balance_regulation.getDestination())
      if cell.getId() == 'movement_0_0_0':
        # check the quantity of banknote for year 1992 is 2
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity of banknote for year 2003 is 3
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

    self.addCashLineToDelivery(self.cash_balance_regulation, 'valid_incoming_line_2', 'Incoming Cash Balance Regulation Line', self.piece_200,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/valid') + self.variation_list,
            self.quantity_200)
    # execute tic
    self.stepTic()
    # check there is only one line created
    self.assertEqual(len(self.cash_balance_regulation.objectValues()), 2)
    # get the cash balance regulation line
    self.valid_incoming_line = getattr(self.cash_balance_regulation, 'valid_incoming_line_2')
    # check its portal type
    self.assertEqual(self.valid_incoming_line.getPortalType(), 'Incoming Cash Balance Regulation Line')
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
      ####if check_source:
        ####self.assertEqual(cell.getSourceValue(), self.guichet_1)
      # check the destination vault is guichet_1
      self.assertEqual(cell.getDestinationValue(), self.cash_balance_regulation.getBaobabDestination())
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
    Check the amount after the creation of cash balance regulation line 1
    """
    # Check number of lines
    self.assertEqual(len(self.cash_balance_regulation.objectValues()), 2)
    # Check quantity of banknotes (2 for 1992 and 3 for 2003)
    self.assertEqual(self.cash_balance_regulation.getTotalQuantity(deliveryLineType="Incoming Cash Balance Regulation Line"), 17.0)
    # Check the total price
    self.assertEqual(self.cash_balance_regulation.getTotalPrice(deliveryLineType="Incoming Cash Balance Regulation Line"), 10000 * 5.0 + 200 * 12.0)


  def stepCreateValidOutgoingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash sorting outgoing line wiht banknotes of 200 and check it has been well created
    """
    # create the line
    self.addCashLineToDelivery(self.cash_balance_regulation, 'valid_outgoing_line_1', 'Outgoing Cash Balance Regulation Line', self.billet_5000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/valid') + self.variation_list,
            self.outgoing_quantity_5000)
    # execute tic
    self.stepTic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.cash_balance_regulation.objectValues()), 3)
    # get the second cash balance regulation line
    self.valid_outgoing_line = getattr(self.cash_balance_regulation, 'valid_outgoing_line_1')
    # check portal types
    self.assertEqual(self.valid_outgoing_line.getPortalType(), 'Outgoing Cash Balance Regulation Line')
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
      if cell.getId() == 'movement_0_0_0':
        # check the quantity for coin for year 1992 is 5
        self.assertEqual(cell.getQuantity(), 4.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity for coin for year 2003 is 7
        self.assertEqual(cell.getQuantity(), 6.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

    # create the line for coins
    self.addCashLineToDelivery(self.cash_balance_regulation, 'valid_outgoing_line_2', 'Outgoing Cash Balance Regulation Line', self.piece_100,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/s', 'cash_status/valid') + self.variation_list,
            self.outgoing_quantity_100)
    # execute tic
    self.stepTic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.cash_balance_regulation.objectValues()), 4)
    # get the second cash balance regulation line
    self.valid_outgoing_line = getattr(self.cash_balance_regulation, 'valid_outgoing_line_2')
    # check portal types
    self.assertEqual(self.valid_outgoing_line.getPortalType(), 'Outgoing Cash Balance Regulation Line')
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
      cell = self.valid_outgoing_line.getCell('emission_letter/s', variation, 'cash_status/valid')
      # check the portal type
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
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
    Check the total after the creation of the two cash balance regulation lines
    """
    # Check number of lines (line1 + line2)
    self.assertEqual(len(self.cash_balance_regulation.objectValues()), 4)
    # Check quantity, banknotes : 2 for 1992 and 3 for 2003, coin : 5 for 1992 and 7 for 2003
    self.assertEqual(self.cash_balance_regulation.getTotalQuantity(deliveryLineType="Outgoing Cash Balance Regulation Line"), 34.0)
    # check the total price
    self.assertEqual(self.cash_balance_regulation.getTotalPrice(deliveryLineType="Outgoing Cash Balance Regulation Line"), 5000 * 4.0 + 100 * 0.0 + 5000 * 6.0 + 100 * 24.0)




  def stepConfirmCashBalanceRegulation(self, sequence=None, sequence_list=None, **kwd):
    """
    Confirm the cash sorting and check it
    """
    # do the Workflow action
    self.workflow_tool.doActionFor(self.cash_balance_regulation, 'confirm_action', wf_id='cash_balance_regulation_workflow')
    # execute tic
    self.stepTic()
    # get state
    state = self.cash_balance_regulation.getSimulationState()
    # check state is confirmed
    self.assertEqual(state, 'confirmed')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_balance_regulation, name='history', wf_id='cash_balance_regulation_workflow')
    # check len of workflow history is 6
    self.assertEqual(len(workflow_history), 3)


  def stepCheckConfirmedInventoryCaveau(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault encaisse_paris is right after confirm and before deliver 
    """
    # check we have 5 banknotes of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we will have 0 banknote of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 12 coins of 200 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    # check we will have 0 coin of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    # check that all banknote of 5000 go to the right cash
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 34.0)
    # check we have 0 coin of 100 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 0.0)
    # check we will have 12 coins of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 24.0)




  def stepCheckConfirmedInventorySalleTri(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault encaisse_paris is right after confirm and before deliver 
    """
    # check we have 5 banknotes of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we will have 0 banknote of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 12 coins of 200 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    # check we will have 0 coin of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    # check that all banknote of 5000 go to the right cash
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 34.0)
    # check we have 0 coin of 100 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 0.0)
    # check we will have 12 coins of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 24.0)


  def stepCheckConfirmedInventorySurface(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault encaisse_paris is right after confirm and before deliver 
    """
    # check we have 5 banknotes of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we will have 0 banknote of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 12 coins of 200 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    # check we will have 0 coin of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    # check that all banknote of 5000 go to the right cash
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 34.0)
    # check we have 0 coin of 100 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 0.0)
    # check we will have 12 coins of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 24.0)

  
  def stepCheckConfirmedInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault encaisse_paris is right after confirm and before deliver 
    """
    # check we have 5 banknotes of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we will have 0 banknote of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 12 coins of 200 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    # check we will have 0 coin of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    # check that all banknote of 5000 go to the right cash
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_1.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_1.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 34.0)
    # check we have 0 coin of 100 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_1.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 0.0)
    # check we will have 12 coins of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_1.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 24.0)




  def stepDeliverCashBalanceRegulation(self, sequence=None, sequence_list=None, **kwd):
    """
    Deliver the cash sorting with a good user
    and check that the deliver of a cash tranfer have achieved
    """
    #     self.security_manager = AccessControl.getSecurityManager()
    #     self.user = self.security_manager.getUser()
    # do the workflow transition "deliver_action"
    self.workflow_tool.doActionFor(self.cash_balance_regulation, 'deliver_action', wf_id='cash_balance_regulation_workflow')
    # execute tic
    self.stepTic()
    # get state of cash sorting
    state = self.cash_balance_regulation.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_balance_regulation, name='history', wf_id='cash_balance_regulation_workflow')
    # check len of len workflow history is 6
    self.assertEqual(len(workflow_history), 5)
    

  def stepCheckFinalInventory(self, sequence=None, sequence_list=None, check_source=1,**kwd):
    """
    Check inventory at source (vault encaisse_paris) after deliver of the cash sorting
    """
    if check_source:
      # check we have 0 banknote of 10000
      self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
      self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
      # check we have 0 coin of 200
      self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
      self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
      self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_1.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 34.0)
      self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_1.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 34.0)
      # check we have 12 coins of 100
      self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_1.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 24.0)
      self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_1.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 24.0)


  def stepCheckFinalInventoryCaveau(self, sequence=None, sequence_list=None, check_source=1,**kwd):
    """
    Check inventory at source (vault encaisse_paris) after deliver of the cash sorting
    """
    if check_source:
      # check we have 0 banknote of 10000
      self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
      self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
      # check we have 0 coin of 200
      self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
      self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
      self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 34.0)
      self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 34.0)
      # check we have 12 coins of 100
      self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 24.0)
      self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_caveau.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 24.0)


  def stepCheckFinalInventorySalleTri(self, sequence=None, sequence_list=None, check_source=1,**kwd):
    """
    Check inventory at source (vault encaisse_paris) after deliver of the cash sorting
    """
    if check_source:
      # check we have 0 banknote of 10000
      self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
      self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
      # check we have 0 coin of 200
      self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
      self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
      self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 34.0)
      self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 34.0)
      # check we have 12 coins of 100
      self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 24.0)
      self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_salletri.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 24.0)


  def stepCheckFinalInventorySurface(self, sequence=None, sequence_list=None, check_source=1,**kwd):
    """
    Check inventory at source (vault encaisse_paris) after deliver of the cash sorting
    """
    if check_source:
      # check we have 0 banknote of 10000
      self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
      self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
      # check we have 0 coin of 200
      self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
      self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
      self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 34.0)
      self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 34.0)
      # check we have 12 coins of 100
      self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 24.0)
      self.assertEqual(self.simulation_tool.getFutureInventory(node=self.guichet_surface.getRelativeUrl(), resource = self.piece_100.getRelativeUrl()), 24.0)



  def stepCheckWorklist(self, **kw):
    self.checkWorklist(self.cash_balance_regulation)

  def stepDelCashBalanceRegulation(self, sequence=None, sequence_list=None, **kwd):
    """
    Delete the invalid vault_transfer line previously create
    """
    self.cash_balance_regulation_module.deleteContent('cash_balance_regulation_1')



  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingCashBalanceRegulation(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run: return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialInventory ' \
                    + 'CreateCashBalanceRegulation ' \
                    + 'CreateValidIncomingLine CheckSubTotal ' \
                    + 'CreateValidOutgoingLine ' \
                    + 'Tic CheckTotal ' \
                    + 'CheckInitialInventory ' \
                    + 'Tic CheckWorklist ' \
                    + 'ConfirmCashBalanceRegulation Tic ' \
                    + 'CheckConfirmedInventory ' \
                    + 'Tic CheckWorklist ' \
                    + 'DeliverCashBalanceRegulation Tic ' \
                    + 'CheckFinalInventory'
    sequence_list.addSequenceString(sequence_string)


    sequence_caveau = 'Tic DelCashBalanceRegulation Tic CheckObjects Tic CheckInitialInventoryCaveau ' \
                    + 'CreateCashBalanceRegulationCaveau ' \
                    + 'CreateValidIncomingLine CheckSubTotal ' \
                    + 'CreateValidOutgoingLine ' \
                    + 'Tic CheckTotal ' \
                    + 'CheckInitialInventoryCaveau ' \
                    + 'Tic CheckWorklist ' \
                    + 'ConfirmCashBalanceRegulation Tic ' \
                    + 'CheckConfirmedInventoryCaveau ' \
                    + 'Tic CheckWorklist ' \
                    + 'DeliverCashBalanceRegulation Tic ' \
                    + 'CheckFinalInventoryCaveau'
    sequence_list.addSequenceString(sequence_caveau)

    sequence_salletri = 'Tic DelCashBalanceRegulation Tic CheckObjects Tic CheckInitialInventorySalleTri ' \
                    + 'CreateCashBalanceRegulationSalleTri ' \
                    + 'CreateValidIncomingLine CheckSubTotal ' \
                    + 'CreateValidOutgoingLine ' \
                    + 'Tic CheckTotal ' \
                    + 'CheckInitialInventorySalleTri ' \
                    + 'ConfirmCashBalanceRegulation Tic ' \
                    + 'CheckConfirmedInventorySalleTri ' \
                    + 'Tic CheckWorklist ' \
                    + 'DeliverCashBalanceRegulation Tic ' \
                    + 'CheckFinalInventorySalleTri'
    sequence_list.addSequenceString(sequence_salletri)

    sequence_surface = 'Tic DelCashBalanceRegulation Tic CheckObjects Tic CheckInitialInventorySurface ' \
                    + 'CreateCashBalanceRegulationSurface ' \
                    + 'CreateValidIncomingLine CheckSubTotal ' \
                    + 'CreateValidOutgoingLine ' \
                    + 'Tic CheckTotal ' \
                    + 'CheckInitialInventorySurface ' \
                    + 'ConfirmCashBalanceRegulation Tic ' \
                    + 'CheckConfirmedInventorySurface ' \
                    + 'Tic CheckWorklist ' \
                    + 'DeliverCashBalanceRegulation Tic ' \
                    + 'CheckFinalInventorySurface'
    sequence_list.addSequenceString(sequence_surface)


    # play the sequence
    sequence_list.play(self)

# define how we launch the unit test
if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestERP5BankingCashBalanceRegulation))
    return suite
