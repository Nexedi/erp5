
##############################################################################
#
# Copyright (c) 2006-2010 Nexedi SA and Contributors. All Rights Reserved.
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
from erp5.component.module.TestERP5BankingMixin import TestERP5BankingMixin

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'


class TestERP5BankingForeignCashReception(TestERP5BankingMixin):
  """
    This class is a unit test to check the module of Cash Transfer

    Here are the following step that will be done in the test :

    XXX to be completed

  """


  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet

  not_defined_variation_list = ('variation/not_defined',)


  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingForeignCashReception"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    # Set some variables :
    self.initDefaultVariable()
    # the cash inventory module
    self.foreign_cash_reception_module = self.getForeignCashReceptionModule()

    self.createManagerAndLogin()
    self.createFunctionGroupSiteCategory()
    self.reception = self.paris.caveau.auxiliaire.encaisse_des_devises.usd
    self.checkUserFolderType()
    self.organisation = self.organisation_module.newContent(id='baobab_org', portal_type='Organisation',
                          function='banking', group='baobab',  site='testsite/paris')
    # define the user
    user_dict = {
        'super_user' : [['Manager'], self.organisation, 'banking/comptable', 'baobab', 'testsite/paris']
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
    # check that ForeignCashReception Module was created
    self.assertEqual(self.foreign_cash_reception_module.getPortalType(), 'Foreign Cash Reception Module')
    # check cash inventory module is empty
    self.assertEqual(len(self.foreign_cash_reception_module.objectValues()), 0)


  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 0 banknotes of 50 in caisse_1
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.reception.getRelativeUrl(), resource = self.usd_billet_50.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.reception.getRelativeUrl(), resource = self.usd_billet_50.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.reception.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.reception.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 0.0)


  def stepCreateForeignCashReception(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a cash inventory document and check it
    """
    #and a price cooreponding to the sum of banknote of 50 and 20
    #( (3) * 50 + (5) * 20 ) = 250
    self.foreign_cash_reception = self.foreign_cash_reception_module.newContent(
                    id='foreign_cash_reception', portal_type='Foreign Cash Reception',
                    source_value=None, destination_value=self.reception,
                    resource_value=self.currency_1,
                    description='test',
                    source_total_asset_price=250)
    # set source reference
    self.setDocumentSourceReference(self.foreign_cash_reception)
    # execute tic
    self.tic()
    # get the cash inventory document
    self.foreign_cash_reception = getattr(self.foreign_cash_reception_module, 'foreign_cash_reception')
    # check its portal type
    self.assertEqual(self.foreign_cash_reception.getPortalType(), 'Foreign Cash Reception')
    # check that its source is caisse_1
    self.assertEqual(self.foreign_cash_reception.getSource(), None)
    # check that its destination is caisse_2
    self.assertEqual(self.foreign_cash_reception.getBaobabDestination(), 'site/testsite/paris/caveau/auxiliaire/encaisse_des_devises/usd')

  def stepCreateValidLine1(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash transfer line 1 with banknotes of 50 and check it has been well created
    """
    # create the cash transfer line
    self.addCashLineToDelivery(self.foreign_cash_reception, 'valid_line_1', 'Cash Delivery Line', self.usd_billet_50,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/not_defined') +self.not_defined_variation_list,
            self.quantity_usd_50,
            variation_list=self.not_defined_variation_list)
    # execute tic
    self.tic()
    # check there is only one line created
    self.assertEqual(len(self.foreign_cash_reception.objectValues()), 1)
    # get the cash transfer line
    self.valid_line_1 = getattr(self.foreign_cash_reception, 'valid_line_1')
    # check its portal type
    self.assertEqual(self.valid_line_1.getPortalType(), 'Cash Delivery Line')
    # check the resource is banknotes of 10000
    self.assertEqual(self.valid_line_1.getResourceValue(), self.usd_billet_50)
    # chek the value of the banknote
    self.assertEqual(self.valid_line_1.getPrice(), 50.0)
    # check the unit of banknote
    self.assertEqual(self.valid_line_1.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_line_1.objectValues()), 1)
    # now check for each variation (years 1992 and 2003)
    for variation in self.not_defined_variation_list:
      # get the delivery cell
      cell = self.valid_line_1.getCell('emission_letter/not_defined',
                                 variation, 'cash_status/not_defined')
      # check portal types
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.usd_billet_50)
      # check the source vault is None
      self.assertEqual(cell.getSourceValue(), None)
      # check the destination vault is counter
      self.assertEqual(cell.getDestinationValue(), self.reception)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity of banknote 2
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

  def stepCreateValidLine2(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash transfer line 1 with banknotes of 20 and check it has been well created
    """
    # create the cash transfer line
    self.addCashLineToDelivery(self.foreign_cash_reception, 'valid_line_2', 'Cash Delivery Line', self.usd_billet_20,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/not_defined') +self.not_defined_variation_list,
            self.quantity_usd_20,
            variation_list=self.not_defined_variation_list)
    # execute tic
    self.tic()
    # check there is only one line created
    self.assertEqual(len(self.foreign_cash_reception.objectValues()), 2)
    # get the cash transfer line
    self.valid_line_1 = getattr(self.foreign_cash_reception, 'valid_line_2')
    # check its portal type
    self.assertEqual(self.valid_line_1.getPortalType(), 'Cash Delivery Line')
    # check the resource is banknotes of 10000
    self.assertEqual(self.valid_line_1.getResourceValue(), self.usd_billet_20)
    # chek the value of the banknote
    self.assertEqual(self.valid_line_1.getPrice(), 20.0)
    # check the unit of banknote
    self.assertEqual(self.valid_line_1.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_line_1.objectValues()), 1)
    # now check for each variation (years 1992 and 2003)
    for variation in self.not_defined_variation_list:
      # get the delivery cell
      cell = self.valid_line_1.getCell('emission_letter/not_defined',
                                 variation, 'cash_status/not_defined')
      # check portal types
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.usd_billet_20)
      # check the source vault is None
      self.assertEqual(cell.getSourceValue(), None)
      # check the destination vault is counter
      self.assertEqual(cell.getDestinationValue(), self.reception)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity of banknote 2
        self.assertEqual(cell.getQuantity(), 5.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepCheckValidLine1(self, sequence=None, sequence_list=None):
    """
    Check the cash delivery line
    """
    # check the cash delivery line
    self.valid_line_1 = getattr(self.foreign_cash_reception, 'valid_line_1')
    # check its portal type
    self.assertEqual(self.valid_line_1.getPortalType(), 'Cash Delivery Line')
    # check the resource is banknotes of 50
    self.assertEqual(self.valid_line_1.getResourceValue(), self.usd_billet_50)
    # chek the value of the banknote
    self.assertEqual(self.valid_line_1.getPrice(), 50.0)
    # check the unit of banknote
    self.assertEqual(self.valid_line_1.getQuantityUnit(), 'unit')
    # check we have one delivery cells
    self.assertEqual(len(self.valid_line_1.objectValues()), 1)
    # now check for variation
    variation = 'variation/not_defined'
    # get the delivery cell
    cell = self.valid_line_1.getCell('emission_letter/not_defined', variation, 'cash_status/not_defined')
    # chek portal types
    self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
    # check the banknote of the cell is banknote of 50
    self.assertEqual(cell.getResourceValue(), self.usd_billet_50)
    # check the source vault is caisse_1
    self.assertEqual(cell.getSourceValue(), None)
    # check the destination vault is caisse_2
    self.assertEqual(cell.getDestinationValue(), self.reception)
    self.assertEqual(cell.getQuantity(), 3.0)

  def stepCheckValidLine2(self, sequence=None, sequence_list=None):
    """
    Check the cash delivery line
    """
    # check the cash delivery line
    self.valid_line_1 = getattr(self.foreign_cash_reception, 'valid_line_2')
    # check its portal type
    self.assertEqual(self.valid_line_1.getPortalType(), 'Cash Delivery Line')
    # check the resource is banknotes of 50
    self.assertEqual(self.valid_line_1.getResourceValue(), self.usd_billet_20)
    # chek the value of the banknote
    self.assertEqual(self.valid_line_1.getPrice(), 20.0)
    # check the unit of banknote
    self.assertEqual(self.valid_line_1.getQuantityUnit(), 'unit')
    # check we have one delivery cells
    self.assertEqual(len(self.valid_line_1.objectValues()), 1)
    # now check for variation
    variation = 'variation/not_defined'
    # get the delivery cell
    cell = self.valid_line_1.getCell('emission_letter/not_defined', variation, 'cash_status/not_defined')
    # chek portal types
    self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
    # check the banknote of the cell is banknote of 50
    self.assertEqual(cell.getResourceValue(), self.usd_billet_20)
    # check the source vault is caisse_1
    self.assertEqual(cell.getSourceValue(), None)
    # check the destination vault is caisse_2
    self.assertEqual(cell.getDestinationValue(), self.reception)
    self.assertEqual(cell.getQuantity(), 5.0)

  def stepConfirmForeignCashReception(self, sequence=None, sequence_list=None, **kwd):
    """
    confirm the foreign cash reception
    """
    state = self.foreign_cash_reception.getSimulationState()
    # check that state is draft
    self.assertEqual(state, 'empty')
    self.workflow_tool.doActionFor(self.foreign_cash_reception, 'confirm_action', wf_id='foreign_cash_reception_workflow')
    self.assertEqual(self.foreign_cash_reception.getSimulationState(), 'confirmed')
    workflow_history = self.workflow_tool.getInfoFor(ob=self.foreign_cash_reception, name='history', wf_id='foreign_cash_reception_workflow')
    # check len of len workflow history is 6
    self.assertEqual(len(workflow_history), 3)


  def stepCheckConfirmedInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault caisse_2 is right after confirm and before deliver
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.reception.getRelativeUrl(), resource = self.usd_billet_50.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.reception.getRelativeUrl(), resource = self.usd_billet_50.getRelativeUrl()), 3.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.reception.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.reception.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 5.0)


  def stepDeliverForeignCashReception(self, sequence=None, sequence_list=None, **kw):
    """
    Deliver the foreign cash reception
    """
    state = self.foreign_cash_reception.getSimulationState()
    # check that state is draft
    self.assertEqual(state, 'confirmed')
    self.workflow_tool.doActionFor(self.foreign_cash_reception, 'deliver_action', wf_id='foreign_cash_reception_workflow')
    # execute tic
    self.tic()
    # get state of cash sorting
    state = self.foreign_cash_reception.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.foreign_cash_reception, name='history', wf_id='foreign_cash_reception_workflow')
    # check len of len workflow history is 6
    self.assertEqual(len(workflow_history), 5)


  def stepCheckFinalInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault caisse_2 is right after confirm and before deliver
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.reception.getRelativeUrl(), resource = self.usd_billet_50.getRelativeUrl()), 3.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.reception.getRelativeUrl(), resource = self.usd_billet_50.getRelativeUrl()), 3.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.reception.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.reception.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 5.0)

  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingForeignCashReception(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic ' \
                    + 'CheckInitialInventory ' \
                    + 'CreateForeignCashReception Tic ' \
                    + 'CreateValidLine1 Tic ' \
                    + 'CreateValidLine2 Tic ' \
                    + 'CheckValidLine1 ' \
                    + 'CheckValidLine2 ' \
                    + 'ConfirmForeignCashReception Tic ' \
                    + 'CheckConfirmedInventory ' \
                    + 'DeliverForeignCashReception Tic ' \
                    + 'CheckFinalInventory'
    sequence_list.addSequenceString(sequence_string)
    # play the sequence
    sequence_list.play(self)

