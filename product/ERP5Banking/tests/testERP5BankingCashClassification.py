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



class TestERP5BankingCashClassification(TestERP5BankingMixin, ERP5TypeTestCase):

  login = PortalTestCase.login

  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet


  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingCashClassification"


  def getBusinessTemplateList(self):
    """
      Return the list of business templates we need to run the test.
      This method is called during the initialization of the unit test by
      the unit test framework in order to know which business templates
      need to be installed to run the test on.
    """
    return ( 'erp5_base'
           , 'erp5_trade'
           , 'erp5_accounting'
           , 'erp5_banking_core' # erp5_banking_core contains all generic methods for banking
           , 'erp5_banking_inventory'
           , 'erp5_banking_cash' # erp5_banking_cash contains all method for cash sorting
           )

  def getCashSortingModule(self):
    """
    Return the Cash Sorting Module
    """
    return getattr(self.getPortal(), 'cash_sorting_module', None)


  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    self.initDefaultVariable()
    # Set some variables :
    self.cash_sorting_module = self.getCashSortingModule()

    # Create a user and login as manager to populate the erp5 portal with objects for tests.
    self.createManagerAndLogin()

    self.createFunctionGroupSiteCategory(site_list=('paris',))
    self.createBanknotesAndCoins()


    inventory_dict_line_1 = {'id' : 'inventory_line_1',
                             'resource': self.billet_10000,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/not_defined', 'cash_status/to_sort') + self.variation_list,
                             'quantity': self.quantity_10000}

    inventory_dict_line_2 = {'id' : 'inventory_line_2',
                             'resource': self.billet_200,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/not_defined', 'cash_status/to_sort') + self.variation_list,
                             'quantity': self.quantity_200}

    inventory_dict_line_3 = {'id' : 'inventory_line_3',
                             'resource': self.billet_5000,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/not_defined', 'cash_status/to_sort') + self.variation_list,
                             'quantity': self.quantity_5000}


    line_list = [inventory_dict_line_1, inventory_dict_line_2, inventory_dict_line_3]
    self.encaisse_tri = self.paris.surface.salle_tri.encaisse_des_billets_recus_pour_ventilation.madrid
    self.encaisse_reserve = self.paris.caveau.reserve.encaisse_des_billets_et_monnaies
    self.encaisse_aux_externe = self.paris.caveau.auxiliaire.encaisse_des_externes
    #self.encaisse_aux_bm = self.paris.caveau.auxiliaire.encaisse_des_billets_recus_pour_ventilation.madrid
    self.encaisse_aux_bm = self.paris.caveau.auxiliaire.encaisse_des_billets_et_monnaies
    self.encaisse_aux_ventil_madrid = self.paris.caveau.auxiliaire.encaisse_des_billets_recus_pour_ventilation.madrid

    self.createCashInventory(source=None, destination=self.encaisse_tri, currency=self.currency_1,
                             line_list=line_list)

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
    # check that CashSorting Module was created
    self.assertEqual(self.cash_sorting_module.getPortalType(), 'Cash Sorting Module')
    # check cash sorting module is empty
    self.assertEqual(len(self.cash_sorting_module.objectValues()), 0)


  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)


  def stepCheckSource(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory in source vault (encaisse_paris) before a confirm
    """
    # check we have 5 banknotes of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)


  def stepCheckDestination(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory in destination vault (caisse_2) before confirm
    """
    # check we don't have banknotes of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_reserve.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_reserve.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_aux_externe.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_aux_externe.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_aux_bm.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_aux_bm.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)

    # check we don't have coins of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_reserve.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_reserve.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_aux_externe.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_aux_externe.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_aux_bm.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_aux_bm.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 0.0)

    # check for banknote of 5000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_reserve.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_reserve.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_aux_externe.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_aux_externe.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_aux_bm.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_aux_bm.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)


  def stepCreateCashSorting(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a cash sorting document and check it
    """
    # Cash sorting has encaisse_paris for source, encaisse_aux_externe for destination, and a price cooreponding to the sum of banknote of 10000 and banknotes of 200 ( (2+3) * 1000 + (5+7) * 200 )
    self.cash_sorting = self.cash_sorting_module.newContent(
                               id='cash_sorting_1', 
                               portal_type='Cash Sorting', 
                               source_value=self.encaisse_tri, 
                               description='test',
                               destination_value=None, 
                               source_total_asset_price=52400.0)
    # execute tic
    self.stepTic()
    # set source reference
    self.setDocumentSourceReference(self.cash_sorting)
    # check source reference
    self.assertNotEqual(self.cash_sorting.getSourceReference(), '')
    self.assertNotEqual(self.cash_sorting.getSourceReference(), None)
    # check we have only one cash sorting
    self.assertEqual(len(self.cash_sorting_module.objectValues()), 1)
    # get the cash sorting document
    self.cash_sorting = getattr(self.cash_sorting_module, 'cash_sorting_1')
    # check its portal type
    self.assertEqual(self.cash_sorting.getPortalType(), 'Cash Sorting')
    # check that its source is encaisse_paris
    self.assertEqual(self.cash_sorting.getSource(), 'site/testsite/paris/surface/salle_tri/encaisse_des_billets_recus_pour_ventilation/madrid')
    # check that its destination is encaisse_aux_externe
    self.assertEqual(self.cash_sorting.getDestination(), None)


  def stepCreateThreeValidIncomingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash sorting incoming line  with banknotes of 10000 and check it has been well created
    """
    # create the cash sorting line
    self.addCashLineToDelivery(self.cash_sorting, 'valid_incoming_line_1', 'Incoming Cash Sorting Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/to_sort') + self.variation_list,
            self.quantity_10000)
    # execute tic
    self.stepTic()
    # check there is only one line created
    self.assertEqual(len(self.cash_sorting.objectValues()), 1)
    # get the cash sorting line
    self.valid_incoming_line = getattr(self.cash_sorting, 'valid_incoming_line_1')
    # check its portal type
    self.assertEqual(self.valid_incoming_line.getPortalType(), 'Incoming Cash Sorting Line')
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
      cell = self.valid_incoming_line.getCell('emission_letter/not_defined', variation, 'cash_status/to_sort')
      # chek portal types
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      # check the source vault is encaisse_paris
      self.assertEqual(cell.getSourceValue(), self.encaisse_tri)
      # check the destination vault is encaisse_aux_externe
      self.assertEqual(cell.getDestinationValue(), None)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity of banknote for year 1992 is 2
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity of banknote for year 2003 is 3
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

    self.addCashLineToDelivery(self.cash_sorting, 'valid_incoming_line_2', 'Incoming Cash Sorting Line', self.billet_200,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/to_sort') + self.variation_list,
            self.quantity_200)
    # execute tic
    self.stepTic()
    # check there is only one line created
    self.assertEqual(len(self.cash_sorting.objectValues()), 2)
    # get the cash sorting line
    self.valid_incoming_line = getattr(self.cash_sorting, 'valid_incoming_line_2')
    # check its portal type
    self.assertEqual(self.valid_incoming_line.getPortalType(), 'Incoming Cash Sorting Line')
    # check the resource is banknotes of 10000
    self.assertEqual(self.valid_incoming_line.getResourceValue(), self.billet_200)
    # chek the value of the banknote
    self.assertEqual(self.valid_incoming_line.getPrice(), 200.0)
    # check the unit of banknote
    self.assertEqual(self.valid_incoming_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_incoming_line.objectValues()), 2)
    # now check for each variation (years 1992 and 2003)
    for variation in self.variation_list:
      # get the delivery cell
      cell = self.valid_incoming_line.getCell('emission_letter/not_defined', variation, 'cash_status/to_sort')
      # chek portal types
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.billet_200)
      # check the source vault is encaisse_paris
      self.assertEqual(cell.getSourceValue(), self.encaisse_tri)
      # check the destination vault is encaisse_aux_externe
      self.assertEqual(cell.getDestinationValue(), None)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity of banknote for year 1992 is 2
        self.assertEqual(cell.getQuantity(), 5.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity of banknote for year 2003 is 3
        self.assertEqual(cell.getQuantity(), 7.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

    self.addCashLineToDelivery(self.cash_sorting, 'valid_incoming_line_3', 'Incoming Cash Sorting Line', self.billet_5000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/to_sort') + self.variation_list,
            self.quantity_5000)
    # execute tic
    self.stepTic()
    # check there is only one line created
    self.assertEqual(len(self.cash_sorting.objectValues()), 3)
    # get the cash sorting line
    self.valid_incoming_line = getattr(self.cash_sorting, 'valid_incoming_line_3')
    # check its portal type
    self.assertEqual(self.valid_incoming_line.getPortalType(), 'Incoming Cash Sorting Line')
    # check the resource is banknotes of 10000
    self.assertEqual(self.valid_incoming_line.getResourceValue(), self.billet_5000)
    # chek the value of the banknote
    self.assertEqual(self.valid_incoming_line.getPrice(), 5000.0)
    # check the unit of banknote
    self.assertEqual(self.valid_incoming_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_incoming_line.objectValues()), 2)
    # now check for each variation (years 1992 and 2003)
    for variation in self.variation_list:
      # get the delivery cell
      cell = self.valid_incoming_line.getCell('emission_letter/not_defined', variation, 'cash_status/to_sort')
      # chek portal types
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.billet_5000)
      # check the source vault is encaisse_paris
      self.assertEqual(cell.getSourceValue(), self.encaisse_tri)
      # check the destination vault is encaisse_aux_externe
      self.assertEqual(cell.getDestinationValue(), None)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity of banknote for year 1992 is 2
        self.assertEqual(cell.getQuantity(), 11.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity of banknote for year 2003 is 3
        self.assertEqual(cell.getQuantity(), 13.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepCheckSubTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the amount after the creation of cash sorting line 1
    """
    # Check number of lines
    self.assertEqual(len(self.cash_sorting.objectValues()), 3)
    # Check quantity of banknotes (2 for 1992 and 3 for 2003)
    self.assertEqual(self.cash_sorting.getTotalQuantity(deliveryLineType="Incoming Cash Sorting Line"), 41.0)
    # Check the total price
    self.assertEqual(self.cash_sorting.getTotalPrice(deliveryLineType="Incoming Cash Sorting Line"), 10000 * 5.0 + 200 * 12.0 + 5000 * 24.0)


  def stepCreateValidOutgoingLineForInternalBanknote(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash sorting outgoing line wiht banknotes of 200 and check it has been well created
    """
    # create the line
    self.addCashLineToDelivery(self.cash_sorting, 'valid_outgoing_line_1', 'Outgoing Cash Sorting Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/valid') + self.variation_list,
            self.quantity_10000)
    # execute tic
    self.stepTic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.cash_sorting.objectValues()), 4)
    # get the second cash sorting line
    self.valid_outgoing_line = getattr(self.cash_sorting, 'valid_outgoing_line_1')
    # check portal types
    self.assertEqual(self.valid_outgoing_line.getPortalType(), 'Outgoing Cash Sorting Line')
    # check the resource is coin of 200
    self.assertEqual(self.valid_outgoing_line.getResourceValue(), self.billet_10000)
    # check the value of coin
    self.assertEqual(self.valid_outgoing_line.getPrice(), 10000.0)
    # check the unit of coin
    self.assertEqual(self.valid_outgoing_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_outgoing_line.objectValues()), 2)
    for variation in self.variation_list:
      # get the delivery  cell
      cell = self.valid_outgoing_line.getCell('emission_letter/p', variation, 'cash_status/valid')
      # check the portal type
      self.assertEqual(cell.getPortalType(), 'Outgoing Cash Sorting Cell')
      if cell.getId() == 'movement_0_0_0':
        # check the quantity for coin for year 1992 is 5
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity for coin for year 2003 is 7
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepCreateValidOutgoingLineForExternalBanknote(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash sorting outgoing line wiht banknotes of 200 and check it has been well created
    """
    # create the line
    self.addCashLineToDelivery(self.cash_sorting, 'valid_outgoing_line_2', 'Outgoing Cash Sorting Line', self.billet_200,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/s', 'cash_status/valid') + self.variation_list,
            self.quantity_200)
    # execute tic
    self.stepTic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.cash_sorting.objectValues()), 5)
    # get the second cash sorting line
    self.valid_outgoing_line = getattr(self.cash_sorting, 'valid_outgoing_line_2')
    # check portal types
    self.assertEqual(self.valid_outgoing_line.getPortalType(), 'Outgoing Cash Sorting Line')
    # check the resource is coin of 200
    self.assertEqual(self.valid_outgoing_line.getResourceValue(), self.billet_200)
    # check the value of coin
    self.assertEqual(self.valid_outgoing_line.getPrice(), 200.0)
    # check the unit of coin
    self.assertEqual(self.valid_outgoing_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_outgoing_line.objectValues()), 2)
    for variation in self.variation_list:
      # get the delivery  cell
      cell = self.valid_outgoing_line.getCell('emission_letter/s', variation, 'cash_status/valid')
      # check the portal type
      self.assertEqual(cell.getPortalType(), 'Outgoing Cash Sorting Cell')
      if cell.getId() == 'movement_0_0_0':
        # check the quantity for coin for year 1992 is 5
        self.assertEqual(cell.getQuantity(), 5.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity for coin for year 2003 is 7
        self.assertEqual(cell.getQuantity(), 7.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepCreateValidOutgoingLineForInternalAndCancelledBanknote(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash sorting outgoing line wiht banknotes of 200 and check it has been well created
    """
    # create the line
    self.addCashLineToDelivery(self.cash_sorting, 'valid_outgoing_line_3', 'Outgoing Cash Sorting Line', self.billet_5000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/cancelled') + self.variation_list,
            self.quantity_5000)
    # execute tic
    self.stepTic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.cash_sorting.objectValues()), 6)
    # get the second cash sorting line
    self.valid_outgoing_line = getattr(self.cash_sorting, 'valid_outgoing_line_3')
    # check portal types
    self.assertEqual(self.valid_outgoing_line.getPortalType(), 'Outgoing Cash Sorting Line')
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
      cell = self.valid_outgoing_line.getCell('emission_letter/p', variation, 'cash_status/cancelled')
      # check the portal type
      self.assertEqual(cell.getPortalType(), 'Outgoing Cash Sorting Cell')
      if cell.getId() == 'movement_0_0_0':
        # check the quantity for coin for year 1992 is 5
        self.assertEqual(cell.getQuantity(), 11.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity for coin for year 2003 is 7
        self.assertEqual(cell.getQuantity(), 13.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepCheckTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the total after the creation of the two cash sorting lines
    """
    # Check number of lines (line1 + line2)
    self.assertEqual(len(self.cash_sorting.objectValues()), 6)
    # Check quantity, banknotes : 2 for 1992 and 3 for 2003, coin : 5 for 1992 and 7 for 2003
    self.assertEqual(self.cash_sorting.getTotalQuantity(), (5.0 + 12.0 + 24.0) * 2.0)
    # check the total price
    self.assertEqual(self.cash_sorting.getTotalPrice(), (10000 * 5.0 + 200 * 12.0 + 5000 * 24.0) * 2.0)


  def stepOrderCashSorting(self, sequence=None, sequence_list=None, **kwd):
    """
    Order the cash sorting and check it
    """
    # fix amount (10000 * 5.0 + 200 * 12.0 + 5000 * 24)
    self.cash_sorting.setSourceTotalAssetPrice('172400.0')
    # do the Workflow action
    self.workflow_tool.doActionFor(self.cash_sorting, 'order_action', wf_id='cash_sorting_workflow')
    # execute tic
    self.stepTic()
    # get state
    state = self.cash_sorting.getSimulationState()
    # check state is confirmed
    self.assertEqual(state, 'ordered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_sorting, name='history', wf_id='cash_sorting_workflow')
    # check len of workflow history is 4
    self.assertEqual(len(workflow_history), 3)


  def stepConfirmCashSorting(self, sequence=None, sequence_list=None, **kwd):
    """
    Confirm the cash sorting and check it
    """
    # do the Workflow action
    self.workflow_tool.doActionFor(self.cash_sorting, 'confirm_action', wf_id='cash_sorting_workflow')
    # execute tic
    self.stepTic()
    # get state
    state = self.cash_sorting.getSimulationState()
    # check state is confirmed
    self.assertEqual(state, 'confirmed')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_sorting, name='history', wf_id='cash_sorting_workflow')
    # check len of workflow history is 6
    self.assertEqual(len(workflow_history), 5)


  def stepCheckSourceDebitPlanned(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault encaisse_paris is right after confirm and before deliver
    """
    # check we have 5 banknotes of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we will have 0 banknote of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 12 coins of 200 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    # check we will have 0 coin of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 0.0)
    # check that all banknote of 5000 go to the right cash
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)


  def stepCheckDestinationCreditPlanned(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault encaisse_aux_externe is right after confirm and before deliver
    """
    # check we have 0 banknote of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_aux_ventil_madrid.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we will have 5 banknotes of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_aux_ventil_madrid.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 0 banknote of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_reserve.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we will have 5 banknotes of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_reserve.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 0 coin of 200 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_aux_externe.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 0.0)
    # check we will have 12 coins of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_aux_externe.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    # check for banknote of 5000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_aux_bm.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    # check we will have 12 coins of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_aux_bm.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)


  def stepDeliverCashSorting(self, sequence=None, sequence_list=None, **kwd):
    """
    Deliver the cash sorting with a good user
    and check that the deliver of a cash tranfer have achieved
    """
    #     self.security_manager = AccessControl.getSecurityManager()
    #     self.user = self.security_manager.getUser()
    # do the workflow transition "deliver_action"
    self.workflow_tool.doActionFor(self.cash_sorting, 'deliver_action', wf_id='cash_sorting_workflow')
    # execute tic
    self.stepTic()
    # get state of cash sorting
    state = self.cash_sorting.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_sorting, name='history', wf_id='cash_sorting_workflow')
    # check len of len workflow history is 6
    self.assertEqual(len(workflow_history), 7)


  def stepCheckSourceDebit(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at source (vault encaisse_paris) after deliver of the cash sorting
    """
    # check we have 0 banknote of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 0 coin of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_tri.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)


  def stepCheckDestinationCredit(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at destination (vault encaisse_aux_externe) after deliver of the cash sorting
    """
    # check we have 5 banknotes of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_aux_ventil_madrid.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_aux_ventil_madrid.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 0 banknote of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_reserve.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we will have 5 banknotes of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_reserve.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)

    # check we have 12 coins of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_aux_externe.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_aux_externe.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    # check we have 24 banknotes of 5000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_aux_bm.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_aux_bm.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)


  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingCashClassification(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run: return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialInventory CheckSource CheckDestination ' \
                    + 'CreateCashSorting ' \
                    + 'CreateThreeValidIncomingLine CheckSubTotal ' \
                    + 'CreateValidOutgoingLineForInternalBanknote ' \
                    + 'CreateValidOutgoingLineForExternalBanknote ' \
                    + 'CreateValidOutgoingLineForInternalAndCancelledBanknote Tic CheckTotal ' \
                    + 'CheckSource CheckDestination ' \
                    + 'OrderCashSorting Tic '\
                    + 'ConfirmCashSorting Tic ' \
                    + 'CheckSourceDebitPlanned CheckDestinationCreditPlanned ' \
                    + 'DeliverCashSorting Tic ' \
                    + 'CheckSourceDebit CheckDestinationCredit '
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
    suite.addTest(unittest.makeSuite(TestERP5BankingCashClassification))
    return suite
