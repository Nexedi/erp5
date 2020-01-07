
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
from DateTime import DateTime

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

class TestERP5BankingMonetaryDestruction(TestERP5BankingMixin):
  """
    This class is a unit test to check the module of Monetary Destruction

    Here are the following step that will be done in the test :

    - before the test, we need to create some movements that will put resources in the source

    - create a monetary destruction
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
    return "ERP5BankingMonetaryDestruction"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    # Set some variables :
    self.initDefaultVariable()
    # the monetary destruction module
    self.monetary_destruction_module = self.getMonetaryDestructionModule()

    self.createManagerAndLogin()

    # create categories
    self.createFunctionGroupSiteCategory(site_list=[
      'paris',
      'madrid',
      ('lyon', 'P11', 'testsite/auxiliaire',
        ('FR', '000', '11113', '000000000000', '16'), 'france'),
    ])

    # Before the test, we need to input the inventory

    inventory_dict_line_1 = {'id' : 'inventory_line_1',
                             'resource': self.billet_10000,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/p', 'cash_status/retired') + self.variation_list,
                             'quantity': self.quantity_10000}

    inventory_dict_line_2 = {'id' : 'inventory_line_2',
                             'resource': self.billet_5000,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/p', 'cash_status/retired') + self.variation_list,
                             'quantity': self.quantity_5000}

    inventory_dict_line_for_externe_1 = {'id' : 'inventory_line_1',
                             'resource': self.billet_10000,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/s', 'cash_status/cancelled') + self.variation_list,
                             'quantity': self.quantity_10000}

    inventory_dict_line_for_externe_2 = {'id' : 'inventory_line_2',
                             'resource': self.billet_5000,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/s', 'cash_status/cancelled') + self.variation_list,
                             'quantity': self.quantity_5000}

    inventory_dict_line_for_auxiliaire_1 = {'id' : 'inventory_line_1',
                             'resource': self.billet_10000,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/p', 'cash_status/retired') + self.variation_list,
                             'quantity': self.quantity_10000}

    inventory_dict_line_for_auxiliaire_2 = {'id' : 'inventory_line_2',
                             'resource': self.billet_5000,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/p', 'cash_status/retired') + self.variation_list,
                             'quantity': self.quantity_5000}

    inventory_dict_line_for_dematerialization = {'id' : 'inventory_line_3',
                             'resource': self.piece_200,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/p', 'cash_status/retired') + self.variation_list,
                             'quantity': self.quantity_200}


    self.line_list = line_list = [inventory_dict_line_1, inventory_dict_line_2]
    self.line_list_for_externe = line_list_for_externe = [inventory_dict_line_for_externe_1, inventory_dict_line_for_externe_2]
    self.line_list_for_dematerialization = [inventory_dict_line_for_dematerialization]
    self.line_list_auxiliaire = line_list_auxiliaire = [inventory_dict_line_for_auxiliaire_1, inventory_dict_line_for_auxiliaire_2]
    self.source = self.paris.caveau.serre.encaisse_des_billets_retires_de_la_circulation
    self.source_for_externe = self.paris.caveau.auxiliaire.encaisse_des_externes
    portal = self.getPortal()
    self.source_auxiliaire = portal.portal_categories.site.testsite.auxiliaire.lyon.caveau.serre.encaisse_des_billets_retires_de_la_circulation
    ###self.destinat = self.paris.caveau.serre.encaisse_des_billets_detruits
    self.destination = self.paris.caveau.serre.encaisse_des_billets_neufs_non_emis_en_transit_allant_a.madrid
    self.createCashInventory(source=None, destination=self.source, currency=self.currency_1,
                             line_list=line_list)
    self.createCashInventory(source=None, destination=self.source, currency=self.currency_1,
                             line_list=self.line_list_for_dematerialization)
    self.createCashInventory(source=None, destination=self.source_for_externe, currency=self.currency_1,
                             line_list=line_list_for_externe)
    self.createCashInventory(source=None, destination=self.source_auxiliaire, currency=self.currency_1,
                             line_list=line_list_auxiliaire)

    # now we need to create a user as Manager to do the test
    # in order to have an assigment defined which is used to do transition
    # Create an Organisation that will be used for users assignment
    self.checkUserFolderType()
    self.organisation = self.organisation_module['site_P10']
    self.organisation_externe = self.organisation_module['site_S10']
    self.organisation_auxiliaire = self.organisation_module['site_P11']

    # define the user
    user_dict = {
        'super_user' : [['Manager'], self.organisation, 'banking/comptable', 'baobab', 'testsite/paris']
    }
    # call method to create this user
    self.createERP5Users(user_dict)
    self.logout()
    self.loginByUserName('super_user')
    # open counter date and counter
    self.openCounterDate(site=self.paris)
    self.openCounterDate(site=self.madrid, id='counter_date_2')
    lyon = portal.portal_categories.site.testsite.auxiliaire.lyon
    self.openCounterDate(site=lyon, id='counter_date_3')

  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that Monetary Destruction Module was created
    self.assertEqual(self.monetary_destruction_module.getPortalType(), 'Monetary Destruction Module')
    # check monetary destruction module is empty
    self.assertEqual(len(self.monetary_destruction_module.objectValues()), 0)


  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in source
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 24 banknotes of 5000 in source
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)

  def stepCheckInitialInventoryForAuxiliaire(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in source
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 24 banknotes of 5000 in source
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)

  def stepCheckInitialInventoryForDematerialization(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have  12 coins in source
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    # check we have 0 coins in destination
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.destination.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.destination.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)

  def stepCheckFinalInventoryForDematerialization(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have  0 coins in source
    self.assertEqual(self.simulation_tool.getCurrentInventory(
      node=self.source.getRelativeUrl(),
      resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(
      node=self.source.getRelativeUrl(),
      resource = self.piece_200.getRelativeUrl()), 0.0)
    # check we have 12 coins in destination
    self.assertEqual(self.simulation_tool.getCurrentInventory(
      node=self.destination.getRelativeUrl(),
      resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(
      node=self.destination.getRelativeUrl(),
      resource = self.piece_200.getRelativeUrl()), 12.0)

  def stepCheckInitialInventoryForExterne(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in source
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 24 banknotes of 5000 in source
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)

  def stepCreateMonetaryDestruction(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a monetary destruction document and check it
    """
    #print self.portal.portal_categories.objectIds()
    # Monetary Destruction has source(serre) for source, destinat (serre) for destination, and a price coresponding to the sum of banknote of 10000 and of 5000 ( (2*3) * 10000 + (5*7) * 5000 )
    self.monetary_destruction = self.monetary_destruction_module.newContent(
                                      id='monetary_destruction_1',
                                      portal_type='Monetary Destruction',
                                      start_date = DateTime().Date(),
                                      source_value=self.source,
                                      destination_value=None,
                                      source_total_asset_price=110000.0,
                                      description='test',
                                      source_section_value=self.paris)
    # execute tic
    self.tic()
    # set source reference
    self.setDocumentSourceReference(self.monetary_destruction)
    # check source reference
    self.assertNotEqual(self.monetary_destruction.getSourceReference(), '')
    self.assertNotEqual(self.monetary_destruction.getSourceReference(), None)
    # check we have only one monetary destruction
    self.assertEqual(len(self.monetary_destruction_module.objectValues()), 1)
    # get the monetary destruction document
    self.monetary_destruction = getattr(self.monetary_destruction_module, 'monetary_destruction_1')
    # check its portal type
    self.assertEqual(self.monetary_destruction.getPortalType(), 'Monetary Destruction')
    # check that its source is source
    self.assertEqual(self.monetary_destruction.getSource(), 'site/testsite/paris/caveau/serre/encaisse_des_billets_retires_de_la_circulation')
    # check that its destination is destinat
    ##self.assertEqual(self.monetary_destruction.getDestination(), 'site/testsite/paris/caveau/serre/encaisse_des_billets_detruits')

  def stepCreateMonetaryDestructionForAuxiliaire(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a monetary destruction document and check it
    """
    #print self.portal.portal_categories.objectIds()
    # Monetary Destruction has source(serre) for source, destinat (serre) for destination, and a price coresponding to the sum of banknote of 10000 and of 5000 ( (2*3) * 10000 + (5*7) * 5000 )
    self.monetary_destruction = self.monetary_destruction_module.newContent(
                                      id='monetary_destruction_1',
                                      portal_type='Monetary Destruction',
                                      start_date = DateTime().Date(),
                                      source_value=self.source_auxiliaire,
                                      destination_value=None,
                                      source_total_asset_price=110000.0,
                                      description='test',
                                      source_section_value=self.paris)
    # execute tic
    self.tic()
    # set source reference
    self.setDocumentSourceReference(self.monetary_destruction)
    # check source reference
    self.assertNotEqual(self.monetary_destruction.getSourceReference(), '')
    self.assertNotEqual(self.monetary_destruction.getSourceReference(), None)
    # check we have only one monetary destruction
    self.assertEqual(len(self.monetary_destruction_module.objectValues()), 1)
    # get the monetary destruction document
    self.monetary_destruction = getattr(self.monetary_destruction_module, 'monetary_destruction_1')
    # check its portal type
    self.assertEqual(self.monetary_destruction.getPortalType(), 'Monetary Destruction')
    # check that its source is source
    self.assertEqual(self.monetary_destruction.getSource(), 'site/testsite/auxiliaire/lyon/caveau/serre/encaisse_des_billets_retires_de_la_circulation')
    # check that its destination is destinat
    ##self.assertEqual(self.monetary_destruction.getDestination(), 'site/testsite/paris/caveau/serre/encaisse_des_billets_detruits')

  def stepCreateMonetaryDestructionForDematerialization(self,
       sequence=None, sequence_list=None, **kwd):
    self.stepCreateMonetaryDestruction(sequence=sequence, **kwd)
    self.monetary_destruction.setDematerialization(True)
    self.monetary_destruction.setSourceSectionValue(self.madrid)

  def stepCreateMonetaryDestructionForExterne(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a monetary destruction document and check it
    """
    # Monetary Destruction has source(serre) for source, destinat (serre) for destination, and a price coresponding to the sum of banknote of 10000 and of 5000 ( (2*3) * 10000 + (5*7) * 5000 )
    self.monetary_destruction = self.monetary_destruction_module.newContent(
                                        id='monetary_destruction_1',
                                        portal_type='Monetary Destruction',
                                        source_value=self.source_for_externe,
                                        start_date = DateTime().Date(),
                                        destination_value=None,
                                        source_total_asset_price=110000.0,
                                        source_section_value=self.madrid)
    # execute tic
    self.tic()
    # set source reference
    self.setDocumentSourceReference(self.monetary_destruction)
    # check source reference
    self.assertNotEqual(self.monetary_destruction.getSourceReference(), '')
    self.assertNotEqual(self.monetary_destruction.getSourceReference(), None)
    # check we have only one monetary destruction
    self.assertEqual(len(self.monetary_destruction_module.objectValues()), 1)
    # get the monetary destruction document
    self.monetary_destruction = getattr(self.monetary_destruction_module, 'monetary_destruction_1')
    # check its portal type
    self.assertEqual(self.monetary_destruction.getPortalType(), 'Monetary Destruction')
    # check that its source is source
    self.assertEqual(self.monetary_destruction.getSource(), 'site/testsite/paris/caveau/auxiliaire/encaisse_des_externes')
    # check that its destination is destinat


  def stepCreateValidLine1(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the monetary destruction line 1 with banknotes of 10000 and check it has been well created
    """
    # create the monetary destruction line
    self.addCashLineToDelivery(self.monetary_destruction, 'valid_line_1', 'Monetary Destruction Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/retired') + self.variation_list,
            self.quantity_10000)
    # execute tic
    self.tic()
    # check there is only one line created
    self.assertEqual(len(self.monetary_destruction.objectValues()), 1)
    # get the monetary destruction line
    self.valid_line_1 = getattr(self.monetary_destruction, 'valid_line_1')
    # check its portal type
    self.assertEqual(self.valid_line_1.getPortalType(), 'Monetary Destruction Line')
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
      cell = self.valid_line_1.getCell('emission_letter/p', variation, 'cash_status/retired')
      # chek portal types
      self.assertEqual(cell.getPortalType(), 'Monetary Destruction Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      # check the source vault is source
      self.assertEqual(cell.getSourceValue(), self.source)
      # check the destination vault is counter
      #self.assertEqual(cell.getDestinationValue(), self.destinat)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity of banknote for year 1992 is 2
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity of banknote for year 2003 is 3
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepCreateValidLineForAuxiliaire1(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the monetary destruction line 1 with banknotes of 10000 and check it has been well created
    """
    # create the monetary destruction line
    self.addCashLineToDelivery(self.monetary_destruction, 'valid_line_1', 'Monetary Destruction Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/retired') + self.variation_list,
            self.quantity_10000)
    # execute tic
    self.tic()
    # check there is only one line created
    self.assertEqual(len(self.monetary_destruction.objectValues()), 1)
    # get the monetary destruction line
    self.valid_line_1 = getattr(self.monetary_destruction, 'valid_line_1')
    # check its portal type
    self.assertEqual(self.valid_line_1.getPortalType(), 'Monetary Destruction Line')
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
      cell = self.valid_line_1.getCell('emission_letter/p', variation, 'cash_status/retired')
      # chek portal types
      self.assertEqual(cell.getPortalType(), 'Monetary Destruction Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      # check the source vault is source
      self.assertEqual(cell.getSourceValue(), self.source_auxiliaire)
      # check the destination vault is counter
      #self.assertEqual(cell.getDestinationValue(), self.destinat)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity of banknote for year 1992 is 2
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity of banknote for year 2003 is 3
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepCreateValidLineForExterne1(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the monetary destruction line 1 with banknotes of 10000 and check it has been well created
    """
    # create the monetary destruction line
    self.addCashLineToDelivery(self.monetary_destruction, 'valid_line_1', 'Monetary Destruction Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/s', 'cash_status/cancelled') + self.variation_list,
            self.quantity_10000)
    # execute tic
    self.tic()
    # check there is only one line created
    self.assertEqual(len(self.monetary_destruction.objectValues()), 1)
    # get the monetary destruction line
    self.valid_line_1 = getattr(self.monetary_destruction, 'valid_line_1')
    # check its portal type
    self.assertEqual(self.valid_line_1.getPortalType(), 'Monetary Destruction Line')
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
      cell = self.valid_line_1.getCell('emission_letter/s', variation, 'cash_status/cancelled')
      # chek portal types
      self.assertEqual(cell.getPortalType(), 'Monetary Destruction Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      # check the source vault is source
      self.assertEqual(cell.getSourceValue(), self.source_for_externe)
      # check the destination vault is counter
      #self.assertEqual(cell.getDestinationValue(), self.destinat)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity of banknote for year 1992 is 2
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity of banknote for year 2003 is 3
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

  def stepCreateValidLineForDematerialization(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the vault transfer line 2 wiht coins of 200 and check it has been well created
    """
    # create the line
    self.addCashLineToDelivery(self.monetary_destruction, 'valid_line_1', 'Monetary Destruction Line', self.piece_200,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/retired') + self.variation_list,
            self.quantity_200)
    # execute tic
    self.tic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.monetary_destruction.objectValues()), 1)
    # get the second vault transfer line
    self.valid_line_1 = getattr(self.monetary_destruction, 'valid_line_1')
    # check portal types
    self.assertEqual(self.valid_line_1.getPortalType(), 'Monetary Destruction Line')
    # check the resource is coin of 200
    self.assertEqual(self.valid_line_1.getResourceValue(), self.piece_200)
    # check the value of coin
    self.assertEqual(self.valid_line_1.getPrice(), 200.0)
    # check the unit of coin
    self.assertEqual(self.valid_line_1.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_line_1.objectValues()), 2)
    for variation in self.variation_list:
      # get the delivery  cell
      cell = self.valid_line_1.getCell('emission_letter/p', variation, 'cash_status/retired')
      # check the portal type
      self.assertEqual(cell.getPortalType(), 'Monetary Destruction Cell')
      self.assertTrue(cell.getBaobabDestinationVariationText().find('new_not_emitted')>=0)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity for coin for year 1992 is 5
        self.assertEqual(cell.getQuantity(), 5.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity for coin for year 2003 is 7
        self.assertEqual(cell.getQuantity(), 7.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepCheckSubTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the amount after the creation of monetary destruction line 1
    """
    # Check number of lines
    self.assertEqual(len(self.monetary_destruction.objectValues()), 1)
    # Check quantity of banknotes (2 for 1992 and 3 for 2003)
    self.assertEqual(self.monetary_destruction.getTotalQuantity(fast=0), 5.0)
    # Check the total price
    self.assertEqual(self.monetary_destruction.getTotalPrice(fast=0), 10000 * 5.0)


  def stepCreateValidLine2(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the monetary destruction line 2 wiht banknotes of 5000 and check it has been well created
    """
    # create the line
    self.addCashLineToDelivery(self.monetary_destruction, 'valid_line_2', 'Monetary Destruction Line', self.billet_5000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/retired') + self.variation_list,
            self.quantity_5000)
    # execute tic
    self.tic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.monetary_destruction.objectValues()), 2)
    # get the second monetary destruction line
    self.valid_line_2 = getattr(self.monetary_destruction, 'valid_line_2')
    # check portal types
    self.assertEqual(self.valid_line_2.getPortalType(), 'Monetary Destruction Line')
    # check the resource is banknotes of 5000
    self.assertEqual(self.valid_line_2.getResourceValue(), self.billet_5000)
    # check the value of banknote
    self.assertEqual(self.valid_line_2.getPrice(), 5000.0)
    # check the unit of banknote
    self.assertEqual(self.valid_line_2.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_line_2.objectValues()), 2)
    for variation in self.variation_list:
      # get the delivery  cell
      cell = self.valid_line_2.getCell('emission_letter/p', variation, 'cash_status/retired')
      # check the portal type
      self.assertEqual(cell.getPortalType(), 'Monetary Destruction Cell')
      if cell.getId() == 'movement_0_0_0':
        # check the quantity for banknote for year 1992 is 5
        self.assertEqual(cell.getQuantity(), 11.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity for banknote for year 2003 is 7
        self.assertEqual(cell.getQuantity(), 13.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

  def stepCreateValidLineForAuxiliaire2(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the monetary destruction line 2 wiht banknotes of 5000 and check it has been well created
    """
    # create the line
    self.addCashLineToDelivery(self.monetary_destruction, 'valid_line_2', 'Monetary Destruction Line', self.billet_5000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/retired') + self.variation_list,
            self.quantity_5000)
    # execute tic
    self.tic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.monetary_destruction.objectValues()), 2)
    # get the second monetary destruction line
    self.valid_line_2 = getattr(self.monetary_destruction, 'valid_line_2')
    # check portal types
    self.assertEqual(self.valid_line_2.getPortalType(), 'Monetary Destruction Line')
    # check the resource is banknotes of 5000
    self.assertEqual(self.valid_line_2.getResourceValue(), self.billet_5000)
    # check the value of banknote
    self.assertEqual(self.valid_line_2.getPrice(), 5000.0)
    # check the unit of banknote
    self.assertEqual(self.valid_line_2.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_line_2.objectValues()), 2)
    for variation in self.variation_list:
      # get the delivery  cell
      cell = self.valid_line_2.getCell('emission_letter/p', variation, 'cash_status/retired')
      # check the portal type
      self.assertEqual(cell.getPortalType(), 'Monetary Destruction Cell')
      if cell.getId() == 'movement_0_0_0':
        # check the quantity for banknote for year 1992 is 5
        self.assertEqual(cell.getQuantity(), 11.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity for banknote for year 2003 is 7
        self.assertEqual(cell.getQuantity(), 13.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

  def stepCreateValidLineForExterne2(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the monetary destruction line 2 wiht banknotes of 5000 and check it has been well created
    """
    # create the line
    self.addCashLineToDelivery(self.monetary_destruction, 'valid_line_2', 'Monetary Destruction Line', self.billet_5000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/s', 'cash_status/cancelled') + self.variation_list,
            self.quantity_5000)
    # execute tic
    self.tic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.monetary_destruction.objectValues()), 2)
    # get the second monetary destruction line
    self.valid_line_2 = getattr(self.monetary_destruction, 'valid_line_2')
    # check portal types
    self.assertEqual(self.valid_line_2.getPortalType(), 'Monetary Destruction Line')
    # check the resource is banknotes of 5000
    self.assertEqual(self.valid_line_2.getResourceValue(), self.billet_5000)
    # check the value of banknote
    self.assertEqual(self.valid_line_2.getPrice(), 5000.0)
    # check the unit of banknote
    self.assertEqual(self.valid_line_2.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_line_2.objectValues()), 2)
    for variation in self.variation_list:
      # get the delivery  cell
      cell = self.valid_line_2.getCell('emission_letter/s', variation, 'cash_status/cancelled')
      # check the portal type
      self.assertEqual(cell.getPortalType(), 'Monetary Destruction Cell')
      if cell.getId() == 'movement_0_0_0':
        # check the quantity for banknote for year 1992 is 5
        self.assertEqual(cell.getQuantity(), 11.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity for banknote for year 2003 is 7
        self.assertEqual(cell.getQuantity(), 13.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())



  def stepCreateInvalidLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create an invalid monetary destruction line and
    check the total with the invalid monetary destruction line
    """
    # create a line in which quanity of coin of 200 is higher that quantity available at source
    # here create a line with 12 (5+7) coin of 200 although the vault source has no coin of 200
    self.addCashLineToDelivery(self.monetary_destruction, 'invalid_line', 'Monetary Destruction Line', self.piece_200,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/cancelled') + self.variation_list,
            self.quantity_200)
    # execute tic
    self.tic()
    # Check number of monetary destruction lines (line1 + line2 +invalid_line)
    self.assertEqual(len(self.monetary_destruction.objectValues()), 3)
    # Check quantity, same as checkTotal + coin of 200: 5 for 1992 and 7 for 2003
    self.assertEqual(self.monetary_destruction.getTotalQuantity(fast=0), 5.0 + 24.0 + 12)
    # chect the total price
    self.assertEqual(self.monetary_destruction.getTotalPrice(fast=0), 10000 * 5.0 + 5000 * 24.0 + 200 * 12)

  def stepTryPlannedMonetaryDestructionWithBadInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Try to confirm the monetary destruction with a bad monetary destruction line and
    check the try of confirm the monetary destruction with the invalid line has failed
    """
    # fix amount (10000 * 5.0 + 5000 * 24.0 + 200 * 12)

    self.monetary_destruction.setSourceTotalAssetPrice('172400.0')
    # try to do the workflow action "confirm_action', cath the exception ValidationFailed raised by workflow transition
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.monetary_destruction, 'plan_action',  wf_id='monetary_destruction_workflow')
    # execute tic
    self.tic()
    # get state of the monetary destruction
    state = self.monetary_destruction.getSimulationState()
    # check the state is draft
    self.assertEqual(state, 'empty')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.monetary_destruction, name='history', wf_id='monetary_destruction_workflow')
    # check its len is 2
    # check we get an "Insufficient balance" message in the workflow history because of the invalid line
    msg = workflow_history[-1]['error_message']
    self.assertTrue('Insufficient balance' in "%s" %(msg,))


  def stepDelInvalidLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Delete the invalid monetary destruction line previously create
    """
    self.monetary_destruction.deleteContent('invalid_line')

  def stepDelMonetrayDestruction(self, sequence=None, sequence_list=None, **kwd):
    """
    Delete the invalid monetary_destruction line previously create
    """
    self.monetary_destruction.deleteContent('monetary_destruction_1')


  def stepCheckTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the total after the creation of the two monetary destruction lines
    """
    # Check number of lines (line1 + line2)
    self.assertEqual(len(self.monetary_destruction.objectValues()), 2)
    # Check quantity, banknotes : 2 for 1992 and 3 for 2003, banknotes : 5 for 1992 and 7 for 2003
    self.assertEqual(self.monetary_destruction.getTotalQuantity(fast=0), 5.0 + 24.0)
    # check the total price
    self.assertEqual(self.monetary_destruction.getTotalPrice(fast=0), 10000 * 5.0 + 5000 * 24.0)


  def stepPlannedMonetaryDestruction(self, sequence=None, sequence_list=None, **kwd):
    """
    Confirm the monetary destruction and check it
    """
    # do the Workflow action
    self.workflow_tool.doActionFor(self.monetary_destruction, 'plan_action', wf_id='monetary_destruction_workflow')
    # execute tic
    self.tic()
    # get state
    state = self.monetary_destruction.getSimulationState()
    # check state is planned
    self.assertEqual(state, 'planned')
    # get workflow history


  def stepCheckSourceDebitPlanned(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault source is right after confirm and before deliver
    """
    # check we have 5 banknotes of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getAvailableInventory(node=self.source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we will have 0 banknote of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 24 banknotes of 5000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getAvailableInventory(node=self.source.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    # check we will have 0 banknote of 5000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)


  def stepCheckSourceDebitPlannedForExterne(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault source is right after confirm and before deliver
    """
    # check we have 5 banknotes of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getAvailableInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we will have 0 banknote of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 24 banknotes of 5000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getAvailableInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    # check we will have 0 banknote of 5000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)

  def stepCheckSourceDebitPlannedForAuxiliaire(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault source is right after confirm and before deliver
    """
    # check we have 5 banknotes of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getAvailableInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we will have 0 banknote of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 24 banknotes of 5000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getAvailableInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    # check we will have 0 banknote of 5000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)

  def stepCheckSourceDebitAvailableForExterne(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault source is right after confirm and before deliver
    """
    # check we have 5 banknotes of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we will have 0 banknote of 10000 after deliver
    self.assertEqual(self.simulation_tool.getAvailableInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 24 banknotes of 5000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    # check we will have 0 banknote of 5000 after deliver
    self.assertEqual(self.simulation_tool.getAvailableInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)

  def stepCheckSourceDebitAvailableForAuxiliaire(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault source is right after confirm and before deliver
    """
    # check we have 5 banknotes of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we will have 0 banknote of 10000 after deliver
    self.assertEqual(self.simulation_tool.getAvailableInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 24 banknotes of 5000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    # check we will have 0 banknote of 5000 after deliver
    self.assertEqual(self.simulation_tool.getAvailableInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)

  def stepValidateMonetaryDestruction(self, sequence=None, sequence_list=None, **kwd):
    """
    Validate the monetary destruction with a good user
    and check that the validation of a monetary destruction have achieved
    """
    # do the workflow transition "deliver_action"
    self.workflow_tool.doActionFor(self.monetary_destruction, 'plan_to_deliver_action', wf_id='monetary_destruction_workflow')
    # execute tic
    self.tic()
    # get state of monetary destruction
    state = self.monetary_destruction.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.monetary_destruction, name='history', wf_id='monetary_destruction_workflow')


  def stepCheckSourceDebit(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at source (vault source) after validation of the monetary destruction
    """
    # check we have 0 banknote of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getAvailableInventory(node=self.source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 0 banknote of 5000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getAvailableInventory(node=self.source.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)


  def stepCheckSourceDebitForExterne(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at source (vault source) after validation of the monetary destruction
    """
    # check we have 0 banknote of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getAvailableInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 0 banknote of 5000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getAvailableInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source_for_externe.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)

  def stepCheckSourceDebitForAuxiliaire(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at source (vault source) after validation of the monetary destruction
    """
    # check we have 0 banknote of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getAvailableInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 0 banknote of 5000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getAvailableInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.source_auxiliaire.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 0.0)

  def stepPlanMonetaryDestruction(self, sequence=None, sequence_list=None, **kwd):
    """
    Confirm the monetary_destruction and check it
    """
    # do the Workflow action
    self.workflow_tool.doActionFor(self.monetary_destruction, 'plan_action', wf_id='monetary_destruction_workflow')
    # execute tic
    self.tic()
    # get state
    state = self.monetary_destruction.getSimulationState()
    # check state is planned
    self.assertEqual(state, 'planned')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.monetary_destruction, name='history', wf_id='monetary_destruction_workflow')

  def stepSetMonetaryDestructionSourceTotalAssetPrice(self,
                     sequence=None, sequence_list=None, **kwd):
    self.monetary_destruction.setSourceTotalAssetPrice('170000.0')

  def stepSetMonetaryDestructionSourceTotalAssetPriceForDematerialization(self,
                     sequence=None, sequence_list=None, **kwd):
    self.monetary_destruction.setSourceTotalAssetPrice('2400.0')

  def stepStartMonetaryDestruction(self, sequence=None, sequence_list=None, **kwd):
    """
    Confirm the monetary_destruction and check it
    """
    # do the Workflow action
    self.workflow_tool.doActionFor(self.monetary_destruction, 'start_action', wf_id='monetary_destruction_workflow')
    # execute tic
    self.tic()
    # get state
    state = self.monetary_destruction.getSimulationState()
    # check state is started
    self.assertEqual(state, 'started')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.monetary_destruction, name='history', wf_id='monetary_destruction_workflow')

  def stepStopMonetaryDestruction(self, sequence=None, sequence_list=None, **kwd):
    """
    Confirm the monetary_destruction and check it
    """
    # do the Workflow action
    self.workflow_tool.doActionFor(self.monetary_destruction, 'stop_action', wf_id='monetary_destruction_workflow', stop_date=DateTime().Date())
    # execute tic
    self.tic()
    # get state
    state = self.monetary_destruction.getSimulationState()
    # check state is stopped
    self.assertEqual(state, 'stopped')

  def stepStoppedToDeliverMonetaryDestruction(self, sequence=None, sequence_list=None, **kwd):
    """
    Deliver the monetary_destruction with a good user
    and check that the deliver of a cash tranfer have achieved
    """
    # do the workflow transition "deliver_action"
    self.workflow_tool.doActionFor(self.monetary_destruction, 'stop_to_deliver_action', wf_id='monetary_destruction_workflow')
    # execute tic
    self.tic()
    # get state of monetary_destruction
    state = self.monetary_destruction.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history


  def stepDelMonetaryDestruction(self, sequence=None, sequence_list=None, **kwd):
    self.monetary_destruction_module.deleteContent('monetary_destruction_1')

  def stepResetInventory(self,
               sequence=None, sequence_list=None, **kwd):
    node = self.source
    line_list = self.line_list
    self.resetInventory(destination=node, currency=self.currency_1,
                        line_list=line_list,extra_id='_reset_out')

  def stepValidateFails(self, sequence=None, sequence_list=None, **kwd):
    message = self.assertWorkflowTransitionFails(self.monetary_destruction,
              'monetary_destruction_workflow','plan_to_deliver_action')
    self.assertTrue(message.find('Insufficient balance')>=0)

  def stepResetInventoryForExterne(self,
               sequence=None, sequence_list=None, **kwd):
    node = self.source_for_externe
    line_list = self.line_list_for_externe
    self.resetInventory(destination=node, currency=self.currency_1,
                        line_list=line_list,extra_id='_reset_out')

  def stepDeliverFails(self, sequence=None, sequence_list=None, **kwd):
    message = self.assertWorkflowTransitionFails(self.monetary_destruction,
              'monetary_destruction_workflow','deliver_action')
    self.assertTrue(message.find('Insufficient balance')>=0)

  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingMonetaryDestruction(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()

    # define the sequence for auxiliaiare
    sequence_string_auxiliare = 'Tic CheckObjects Tic CheckInitialInventory ' \
                    + 'CreateMonetaryDestructionForAuxiliaire ' \
                    + 'CreateValidLineForAuxiliaire1 CheckSubTotal ' \
                    + 'CreateValidLineForAuxiliaire2 CheckTotal ' \
                    + 'CheckInitialInventoryForAuxiliaire ' \
                    + 'SetMonetaryDestructionSourceTotalAssetPrice ' \
                    + 'PlannedMonetaryDestruction Tic ' \
                    + 'CheckSourceDebitPlannedForAuxiliaire ' \
                    + 'StartMonetaryDestruction Tic ' \
                    + 'StopMonetaryDestruction Tic ' \
                    + 'CheckSourceDebitAvailableForAuxiliaire ' \
                    + 'StoppedToDeliverMonetaryDestruction Tic ' \
                    + 'CheckSourceDebitForAuxiliaire ' \
                    + 'DelMonetaryDestruction Tic '
    sequence_list.addSequenceString(sequence_string_auxiliare)

    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialInventory ' \
                    + 'CreateMonetaryDestruction ' \
                    + 'CreateValidLine1 CheckSubTotal ' \
                    + 'CreateValidLine2 CheckTotal ' \
                    + 'CheckInitialInventory ' \
                    + 'CreateInvalidLine Tic ' \
                    + 'TryPlannedMonetaryDestructionWithBadInventory ' \
                    + 'DelInvalidLine Tic CheckTotal ' \
                    + 'SetMonetaryDestructionSourceTotalAssetPrice ' \
                    + 'PlannedMonetaryDestruction Tic ' \
                    + 'CheckSourceDebitPlanned ' \
                    + 'ResetInventory Tic ' \
                    + 'ValidateFails ' \
                    + 'DeleteResetInventory Tic ' \
                    + 'ValidateMonetaryDestruction Tic ' \
                    + 'CheckSourceDebit ' \
                    + 'DelMonetaryDestruction Tic'
    sequence_list.addSequenceString(sequence_string)

    # This is the case of a destruction for another agency
    another_sequence_string = 'Tic CheckObjects Tic CheckInitialInventoryForExterne ' \
                    + 'CreateMonetaryDestructionForExterne ' \
                    + 'CreateValidLineForExterne1 CheckSubTotal ' \
                    + 'CreateValidLineForExterne2 CheckTotal ' \
                    + 'CheckInitialInventoryForExterne ' \
                    + 'CreateInvalidLine Tic ' \
                    + 'TryPlannedMonetaryDestructionWithBadInventory ' \
                    + 'DelInvalidLine Tic CheckTotal ' \
                    + 'SetMonetaryDestructionSourceTotalAssetPrice ' \
                    + 'PlanMonetaryDestruction ' \
                    + 'CheckSourceDebitPlannedForExterne ' \
                    + 'StartMonetaryDestruction Tic ' \
                    + 'CheckSourceDebitAvailableForExterne ' \
                    + 'StopMonetaryDestruction Tic ' \
                    + 'CheckSourceDebitAvailableForExterne ' \
                    + 'StoppedToDeliverMonetaryDestruction Tic ' \
                    + 'CheckSourceDebitForExterne ' \
                    + 'DelMonetaryDestruction Tic '

    sequence_list.addSequenceString(another_sequence_string)

    # We will now do a dematerialization
    # It will be the same workflow validation as the destruction for
    # another agency
    another_sequence_string = 'Tic CheckObjects Tic ' \
                    + 'CheckInitialInventoryForDematerialization ' \
                    + 'CreateMonetaryDestructionForDematerialization ' \
                    + 'CreateValidLineForDematerialization ' \
                    + 'CheckInitialInventoryForDematerialization ' \
                    + 'SetMonetaryDestructionSourceTotalAssetPriceForDematerialization ' \
                    + 'PlanMonetaryDestruction ' \
                    + 'ValidateMonetaryDestruction ' \
                    + 'CheckFinalInventoryForDematerialization '

    sequence_list.addSequenceString(another_sequence_string)


    # play the sequence
    sequence_list.play(self)

