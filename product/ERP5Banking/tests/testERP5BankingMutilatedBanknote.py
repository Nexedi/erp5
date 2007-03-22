##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
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


class TestERP5BankingMutilatedBanknote(TestERP5BankingMixin, ERP5TypeTestCase):
  """
  """
  login = PortalTestCase.login

  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet

  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingMutilatedBanknote"

  def getBusinessTemplateList(self):
    """
      Return the list of business templates we need to run the test.
      This method is called during the initialization of the unit test by
      the unit test framework in order to know which business templates
      need to be installed to run the test on.
    """
    return ('erp5_base'
            , 'erp5_trade'
            , 'erp5_accounting'
            , 'erp5_banking_core'
            , 'erp5_banking_inventory'
            , 'erp5_banking_cash'
            )

  def getMutilatedBanknoteModule(self):
    """
    Return the Cash Transer Module
    """
    return getattr(self.getPortal(), 'mutilated_banknote_module', None)

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    # Set some variables :
    self.initDefaultVariable()
    # the cahs transfer module
    self.mutilated_banknote_module = self.getMutilatedBanknoteModule()
    self.createManagerAndLogin()
    # create categories
    self.createFunctionGroupSiteCategory(site_list = ['siege', 'paris'])
    # create resources
    self.createBanknotesAndCoins()
    # Before the test, we need to input the inventory
    inventory_dict_line_1 = {'id' : 'inventory_line_1',
                             'resource': self.billet_10000,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/not_defined', 'cash_status/to_sort') + self.variation_list,
                             'quantity': self.quantity_10000}

    line_list = [inventory_dict_line_1,]
    self.mutilated_banknote_vault = self.paris.surface.caisse_courante.billets_mutiles
    self.usual_vault = self.paris.surface.caisse_courante.encaisse_des_billets_et_monnaies
    self.hq_mutilated_banknote_vault = self.siege.surface.caisse_courante.billets_mutiles
    self.hq_usual_vault = self.siege.surface.caisse_courante.encaisse_des_billets_et_monnaies
    
    self.createCashInventory(source=None, destination=self.usual_vault, currency=self.currency_1,
                             line_list=line_list)
    self.createCashInventory(source=None, destination=self.hq_usual_vault, currency=self.currency_1,
                             line_list=line_list)
    # now we need to create a user as Manager to do the test
    # in order to have an assigment defined which is used to do transition
    # Create an Organisation that will be used for users assignment
    self.checkUserFolderType()
    self.organisation_1 = self.organisation_module.newContent(id='baobab_org', portal_type='Organisation',
                          function='banking', group='baobab',  site='testsite/paris')
    self.organisation_2 = self.organisation_module.newContent(id='baobab_org_hq', portal_type='Organisation',
                                                            function='banking', group='baobab',  site='testsite/siege')
    # define the user
    user_dict = {
        'super_user' : [['Manager'], self.organisation_1, 'banking/comptable', 'baobab', 'testsite/paris/surface/banque_interne/guichet_1'],
        'hq_super_user' : [['Manager'], self.organisation_2, 'banking/comptable', 'baobab', 'testsite/siege/surface/banque_interne/guichet_1']
      }
    # call method to create this user
    self.createERP5Users(user_dict)
    self.logout()
    self.login('super_user')
    self.openCounterDate(site=self.paris)
    self.openCounterDate(site=self.siege, id='counter_date_2')


  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that MutilatedBanknote Module was created
    self.assertEqual(self.mutilated_banknote_module.getPortalType(), 'Mutilated Banknote Module')
    # check cash transfer module is empty
    self.assertEqual(len(self.mutilated_banknote_module.objectValues()), 0)

  def stepArchiveDocument(self, sequence=None, sequence_list=None, **kwd):
    """
      Archive document.
    """
    self.workflow_tool.doActionFor(self.mutilated_banknote, 'archive_action', wf_id='mutilated_banknote_workflow')
    self.assertEqual(self.mutilated_banknote.getSimulationState(), 'archived')

  def stepArchiveHQDocument(self, sequence=None, sequence_list=None, **kwd):
    """
      Archive HQ document.
    """
    self.workflow_tool.doActionFor(self.hq_mutilated_banknote, 'archive_action', wf_id='mutilated_banknote_workflow')
    self.assertEqual(self.hq_mutilated_banknote.getSimulationState(), 'archived')

  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in mutilated_banknote
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.usual_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.usual_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200 in mutilated_banknote
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.mutilated_banknote_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.mutilated_banknote_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)

  def stepCreateMutilatedBanknote(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a mutilated banknote document and check it
    """
    self.mutilated_banknote = self.mutilated_banknote_module.newContent(
                                    id='mutilated_banknote',
                                    portal_type='Mutilated Banknote',
                                    source_total_asset_price=0.0,
                                    destination_total_asset_price=0.0,
                                    description='test',
                                    destination_value=self.mutilated_banknote_vault
                                                                        )
    self.stepTic()
    self.assertEqual(len(self.mutilated_banknote_module.objectValues()), 1)
    self.assertEqual(self.mutilated_banknote.getPortalType(), 'Mutilated Banknote')
    self.assertEqual(self.mutilated_banknote.getSource(), 'site/testsite/paris')
    self.assertEqual(self.mutilated_banknote.getSourceTrade(), 'site/testsite/paris')
    self.assertEqual(self.mutilated_banknote.getDestination(), self.mutilated_banknote_vault.getRelativeUrl())

  def stepTryStopWithNoLineDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to stop with no amount defined on the document
    """
    self.assertEqual(len(self.mutilated_banknote.objectValues()), 0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.mutilated_banknote, 'stop_action', wf_id='mutilated_banknote_workflow')

  def stepCreateIncomingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the incoming mutilated banknote line with banknotes of 10000 and check it has been well created
    """
    # create the  line
    self.addCashLineToDelivery(self.mutilated_banknote, 'incoming_line', 'Incoming Mutilated Banknote Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/mutilated') + self.variation_list,
            self.quantity_10000)
    self.stepTic()
    self.assertEqual(len(self.mutilated_banknote.objectValues()), 1)
    # get the  line
    self.incoming_line = getattr(self.mutilated_banknote, 'incoming_line')
    self.assertEqual(self.incoming_line.getPortalType(), 'Incoming Mutilated Banknote Line')
    self.assertEqual(self.incoming_line.getResourceValue(), self.billet_10000)
    self.assertEqual(self.incoming_line.getPrice(), 10000.0)
    self.assertEqual(self.incoming_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.incoming_line.objectValues()), 2)
    for variation in self.variation_list:
      cell = self.incoming_line.getCell('emission_letter/not_defined', variation, 'cash_status/mutilated')
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      self.assertEqual(cell.getBaobabSourceValue(), None)
      self.assertEqual(cell.getBaobabDestination(), self.mutilated_banknote_vault.getRelativeUrl())
      if cell.getId() == 'movement_0_0_0':
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

  def stepTryStopWithNoAmountDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to stop with no amount defined on the document
    """
    self.assertEqual(self.mutilated_banknote.getSourceTotalAssetPrice(), 0.0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.mutilated_banknote, 'stop_action', wf_id='mutilated_banknote_workflow')

  def stepStopDocument(self, sequence=None, sequence_list=None, **kw):
    """
    Stop mutilated banknote operation
    Also sets the received amount on the document.
    """
    self.mutilated_banknote.setSourceTotalAssetPrice(50000.0)
    self.assertEqual(self.mutilated_banknote.getSourceTotalAssetPrice(), 50000.0)
    self.workflow_tool.doActionFor(self.mutilated_banknote, 'stop_action', wf_id='mutilated_banknote_workflow')
    self.stepTic()
    self.assertEqual(self.mutilated_banknote.getSimulationState(), "stopped")

  def stepCreateExchangedLine(self, sequence=None, sequence_list=None, **kw):
    """
    """
    # create an exchanged
    self.addCashLineToDelivery(self.mutilated_banknote, 'exchanged_line', 'Exchanged Mutilated Banknote Line', self.billet_10000,
                               ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/to_sort') + self.variation_list,
                               self.quantity_10000)
    self.stepTic()
    self.assertEqual(len(self.mutilated_banknote.objectValues()), 2)
    # get the line
    self.exchanged_line = getattr(self.mutilated_banknote, 'exchanged_line')
    self.assertEqual(self.exchanged_line.getPortalType(), 'Exchanged Mutilated Banknote Line')
    self.assertEqual(self.exchanged_line.getResourceValue(), self.billet_10000)
    self.assertEqual(self.exchanged_line.getPrice(), 10000.0)
    self.assertEqual(self.exchanged_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.exchanged_line.objectValues()), 2)
    for variation in self.variation_list:
      cell = self.exchanged_line.getCell('emission_letter/not_defined', variation, 'cash_status/to_sort')
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      self.assertEqual(cell.getBaobabSourceValue(), None)
      self.assertEqual(cell.getBaobabDestination(), self.usual_vault.getRelativeUrl())
      if cell.getId() == 'movement_0_0_0':
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

  def stepTryPlanWithExchangedLine(self, sequence=None, sequence_list=None, **kw):
    """
    Try to plan with exchanged line defined
    """
    self.assertEqual(len(self.mutilated_banknote.objectValues(portal_type='Exchanged Mutilated Banknote Line')), 1.0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.mutilated_banknote, 'plan_action', wf_id='mutilated_banknote_workflow')

  def stepPlanDocument(self, sequence=None, sequence_list=None, **kw):
    """
    Plan mutilated banknote operation
    """
    self.workflow_tool.doActionFor(self.mutilated_banknote, 'plan_action', wf_id='mutilated_banknote_workflow')
    self.stepTic()
    self.assertEqual(self.mutilated_banknote.getSimulationState(), "planned")

  def stepDelExchangedLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Delete the invalid cash transfer line previously create
    """
    self.mutilated_banknote.deleteContent('exchanged_line')

  def stepDeliverDocument(self, sequence=None, sequence_list=None, **kw):
    """
    Deliver mutilated banknote operation.
    Also sets the exchanged amount on the document.
    """
    self.mutilated_banknote.setDestinationTotalAssetPrice(50000.0)
    self.assertEqual(self.mutilated_banknote.getDestinationTotalAssetPrice(), 50000.0)
    self.workflow_tool.doActionFor(self.mutilated_banknote, 'deliver_action', wf_id='mutilated_banknote_workflow')
    self.stepTic()
    self.assertEqual(self.mutilated_banknote.getSimulationState(), "delivered")

  def stepCheckFinalInventoryWithNoPayBack(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the final inventory when document got rejected without HQ request
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.usual_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.usual_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.mutilated_banknote_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.mutilated_banknote_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)

  def stepCheckFinalInventoryWithNoPayBackAfterHQRequest(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the final inventory when document got rejected with HQ request
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.usual_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.usual_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.mutilated_banknote_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.mutilated_banknote_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)

  def stepClearMutilatedBanknoteModule(self, sequence=None, sequence_list=None, **kw):
    """
    Remove all operations in module
    """
    self.mutilated_banknote_module.deleteContent('mutilated_banknote')    

  def stepTryFinishWithNoLineDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to confirm with no line defined on the document
    """
    self.assertEqual(len(self.mutilated_banknote.objectValues(portal_type="Exchanged Mutilated Banknote Line")), 0.0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.mutilated_banknote, 'finish_action', wf_id='mutilated_banknote_workflow')

  def stepTryFinishHQWithNoLineDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to confirm with no line defined on the document
    """
    self.assertEqual(len(self.hq_mutilated_banknote.objectValues(portal_type="Exchanged Mutilated Banknote Line")), 0.0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.hq_mutilated_banknote, 'finish_action', wf_id='mutilated_banknote_workflow')

  def stepTryFinishWithNoAmountDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to confirm with no amount defined on the document
    """
    self.assertEqual(self.mutilated_banknote.getDestinationTotalAssetPrice(), 0.0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.mutilated_banknote, 'finish_action', wf_id='mutilated_banknote_workflow')

  def stepTryFinishHQWithNoAmountDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to confirm with no amount defined on the document
    """
    self.assertEqual(self.hq_mutilated_banknote.getDestinationTotalAssetPrice(), 0.0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.hq_mutilated_banknote, 'finish_action', wf_id='mutilated_banknote_workflow')

  def stepFinishDocument(self, sequence=None, sequence_list=None, **kw):
    """
    Finish mutilated banknote operation (send to counter)
    """
    self.mutilated_banknote.setDestinationTotalAssetPrice(50000.0)
    self.assertEqual(self.mutilated_banknote.getDestinationTotalAssetPrice(), 50000.0)
    self.workflow_tool.doActionFor(self.mutilated_banknote, 'finish_action', wf_id='mutilated_banknote_workflow')
    self.stepTic()
    self.assertEqual(self.mutilated_banknote.getSimulationState(), "finished")

  def stepTryDeliverWithNoLineDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to deliver with no outgoing line defined on the document
    """
    self.assertEqual(len(self.mutilated_banknote.objectValues(portal_type="Outgoing Mutilated Banknote Line")), 0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.mutilated_banknote, 'deliver_action', wf_id='mutilated_banknote_workflow')

  def stepTryDeliverWithWrongAmountDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to deliver with wrong amount defined on the document at state ordered
    """
    self.mutilated_banknote.setDestinationTotalAssetPrice(4000.0)
    self.assertEqual(self.mutilated_banknote.getDestinationTotalAssetPrice(), 4000.0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.mutilated_banknote, 'deliver_action', wf_id='mutilated_banknote_workflow')

  def stepCreateOutgoingLine(self, sequence=None, sequence_list=None, **kw):
    """
    """
    # create an exchanged
    self.addCashLineToDelivery(self.mutilated_banknote, 'outgoing_line', 'Outgoing Mutilated Banknote Line', self.billet_10000,
                               ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/to_sort') + self.variation_list,
                               self.quantity_10000)
    self.stepTic()
    # get the line
    self.outgoing_line = getattr(self.mutilated_banknote, 'outgoing_line')
    self.assertEqual(self.outgoing_line.getPortalType(), 'Outgoing Mutilated Banknote Line')
    self.assertEqual(self.outgoing_line.getResourceValue(), self.billet_10000)
    self.assertEqual(self.outgoing_line.getPrice(), 10000.0)
    self.assertEqual(self.outgoing_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.outgoing_line.objectValues()), 2)
    for variation in self.variation_list:
      cell = self.outgoing_line.getCell('emission_letter/not_defined', variation, 'cash_status/to_sort')
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      self.assertEqual(cell.getBaobabSource(), None)
      self.assertEqual(cell.getBaobabDestinationValue(), None)
      if cell.getId() == 'movement_0_0_0':
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

  def stepCheckFinalInventoryWithPayBack(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.usual_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.usual_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.mutilated_banknote_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.mutilated_banknote_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)

  def stepCheckFinalInventoryWithPayBackAfterHQRequest(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.usual_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.usual_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.mutilated_banknote_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.mutilated_banknote_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)

  #
  # Headquarter part
  #
  def stepHQLogin(self, sequence=None, sequence_list=None, **kw):
    """
    Login as a headquarter user    
    """
    self.logout()
    self.login("hq_super_user")

  def stepHQLogout(self, sequence=None, sequence_list=None, **kw):
    """
    Login as a headquarter user    
    """
    self.logout()
    self.login("super_user")

  def stepCheckHQInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in mutilated_banknote
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.hq_usual_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.hq_usual_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200 in mutilated_banknote
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.hq_mutilated_banknote_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.hq_mutilated_banknote_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)

  def stepCreateHQMutilatedBanknote(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a mutilated banknote document and check it
    """
    self.hq_mutilated_banknote = self.mutilated_banknote_module.newContent(id='hq_mutilated_banknote',
                                                                           portal_type='Mutilated Banknote',
                                                                           source_total_asset_price=0.0,
                                                                           destination_total_asset_price=0.0,
                                                                           destination_value=self.hq_mutilated_banknote_vault
                                                                           )
    self.stepTic()
    self.hq_mutilated_banknote.edit(source_trade='site/testsite/paris')
    self.assertEqual(len(self.mutilated_banknote_module.objectValues()), 2)
    self.assertEqual(self.hq_mutilated_banknote.getPortalType(), 'Mutilated Banknote')
    self.assertEqual(self.hq_mutilated_banknote.getSource(), 'site/testsite/siege')
    self.assertEqual(self.hq_mutilated_banknote.getSourceTrade(), 'site/testsite/paris')
    self.assertEqual(self.hq_mutilated_banknote.getDestination(), self.hq_mutilated_banknote_vault.getRelativeUrl())

  def stepTryStopHQWithNoLineDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to plan with no amount defined on the document
    """
    self.assertEqual(len(self.hq_mutilated_banknote.objectValues()), 0.0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.hq_mutilated_banknote, 'stop_action', wf_id='mutilated_banknote_workflow')

  def stepCreateHQIncomingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the incoming mutilated banknote line with banknotes of 10000 and check it has been well created
    """
    # create the  line
    self.addCashLineToDelivery(self.hq_mutilated_banknote, 'hq_incoming_line', 'Incoming Mutilated Banknote Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/mutilated') + self.variation_list,
            self.quantity_10000)
    self.stepTic()
    self.assertEqual(len(self.hq_mutilated_banknote.objectValues()), 1)
    # get the  line
    self.hq_incoming_line = getattr(self.hq_mutilated_banknote, 'hq_incoming_line')
    self.assertEqual(self.hq_incoming_line.getPortalType(), 'Incoming Mutilated Banknote Line')
    self.assertEqual(self.hq_incoming_line.getResourceValue(), self.billet_10000)
    self.assertEqual(self.hq_incoming_line.getPrice(), 10000.0)
    self.assertEqual(self.hq_incoming_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.hq_incoming_line.objectValues()), 2)
    for variation in self.variation_list:
      cell = self.hq_incoming_line.getCell('emission_letter/not_defined', variation, 'cash_status/mutilated')
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      self.assertEqual(cell.getBaobabSourceValue(), None)
      self.assertEqual(cell.getBaobabDestination(), self.hq_mutilated_banknote_vault.getRelativeUrl())
      if cell.getId() == 'movement_0_0_0':
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

  def stepTryStopHQWithNoAmountDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to plan with no amount defined on the document
    """
    self.assertEqual(self.hq_mutilated_banknote.getSourceTotalAssetPrice(), 0.0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.hq_mutilated_banknote, 'stop_action', wf_id='mutilated_banknote_workflow')

  def stepStopHQDocument(self, sequence=None, sequence_list=None, **kw):
    """
    Plan mutilated banknote operation
    Also set the original price of mutilated banknotes.
    """
    self.hq_mutilated_banknote.setSourceTotalAssetPrice(50000.0)
    self.assertEqual(self.hq_mutilated_banknote.getSourceTotalAssetPrice(), 50000.0)
    self.workflow_tool.doActionFor(self.hq_mutilated_banknote, 'stop_action', wf_id='mutilated_banknote_workflow')
    self.stepTic()
    self.assertEqual(self.hq_mutilated_banknote.getSimulationState(), "stopped")

  def stepTryPlanHQDocument(self, sequence=None, sequence_list=None, **kw):
    """
      It must not be possible (ie, action not present) to plan when the document is initiated in HQ.
    """
    self.assertRaises(Unauthorized, self.workflow_tool.doActionFor, self.hq_mutilated_banknote, 'plan_action', wf_id='mutilated_banknote_workflow')

  def stepTryDeliverHQDocument(self, sequence=None, sequence_list=None, **kw):
    """
      It must not be possible (ie, action not present) to deliver when the document is initiated in HQ.
    """
    self.assertRaises(Unauthorized, self.workflow_tool.doActionFor, self.hq_mutilated_banknote, 'deliver_action', wf_id='mutilated_banknote_workflow')

  def stepFinishHQDocument(self, sequence=None, sequence_list=None, **kw):
    """
    Finish mutilated banknote operation
    Also set the price to pay back to the customer.
    """
    self.hq_mutilated_banknote.setDestinationTotalAssetPrice(50000.0)
    self.assertEqual(self.hq_mutilated_banknote.getDestinationTotalAssetPrice(), 50000.0)
    self.workflow_tool.doActionFor(self.hq_mutilated_banknote, 'finish_action', wf_id='mutilated_banknote_workflow')
    self.stepTic()
    self.assertEqual(self.hq_mutilated_banknote.getSimulationState(), "finished")

  def stepCheckHQFinalInventoryWithNoPayBack(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.usual_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.usual_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.hq_mutilated_banknote_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.hq_mutilated_banknote_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)

  def stepClearHQMutilatedBanknoteModule(self, sequence=None, sequence_list=None, **kw):
    """
    Remove all operations in module
    """
    self.mutilated_banknote_module.deleteContent('hq_mutilated_banknote')    

  def stepCreateHQExchangedLine(self, sequence=None, sequence_list=None, **kw):
    """
    """
    # create an exchanged
    self.addCashLineToDelivery(self.hq_mutilated_banknote, 'hq_exchanged_line', 'Exchanged Mutilated Banknote Line', self.billet_10000,
                               ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/to_sort') + self.variation_list,
                               self.quantity_10000)
    self.stepTic()
    self.assertEqual(len(self.hq_mutilated_banknote.objectValues()), 2)
    # get the line
    self.hq_exchanged_line = getattr(self.hq_mutilated_banknote, 'hq_exchanged_line')
    self.assertEqual(self.hq_exchanged_line.getPortalType(), 'Exchanged Mutilated Banknote Line')
    self.assertEqual(self.hq_exchanged_line.getResourceValue(), self.billet_10000)
    self.assertEqual(self.hq_exchanged_line.getPrice(), 10000.0)
    self.assertEqual(self.hq_exchanged_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.hq_exchanged_line.objectValues()), 2)
    for variation in self.variation_list:
      cell = self.hq_exchanged_line.getCell('emission_letter/not_defined', variation, 'cash_status/to_sort')
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      self.assertEqual(cell.getBaobabSourceValue(), None)
      self.assertEqual(cell.getBaobabDestination(), self.hq_usual_vault.getRelativeUrl())
      if cell.getId() == 'movement_0_0_0':
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

  def stepCheckHQFinalInventoryWithPayBack(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the final inventory when the mutilated payment was approved by headquaters.
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.hq_usual_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.hq_usual_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.hq_mutilated_banknote_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.hq_mutilated_banknote_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)

  ##################################
  ##  Tests
  ##################################
  def test_01_ERP5BankingMutilatedBanknote(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run: return
    sequence_list = SequenceList()
    # define the sequence
    # sequence 1 : no payback
    sequence_string_1 = 'Tic CheckObjects Tic CheckInitialInventory ' \
                        + 'CreateMutilatedBanknote Tic TryStopWithNoLineDefined ' \
                        + 'CreateIncomingLine Tic TryStopWithNoAmountDefined ' \
                        + 'StopDocument Tic ' \
                        + 'ArchiveDocument Tic ' \
                        + 'CheckFinalInventoryWithNoPayBack ClearMutilatedBanknoteModule'
    
    # sequence 2 : pay back
    sequence_string_2 = 'Tic CheckObjects Tic CheckInitialInventory ' \
                        + 'CreateMutilatedBanknote Tic ' \
                        + 'CreateIncomingLine Tic ' \
                        + 'StopDocument Tic ' \
                        + 'TryFinishWithNoLineDefined CreateExchangedLine Tic TryFinishWithNoAmountDefined FinishDocument Tic ' \
                        + 'TryDeliverWithNoLineDefined CreateOutgoingLine Tic TryDeliverWithWrongAmountDefined DeliverDocument Tic ' \
                        + 'CheckFinalInventoryWithPayBack ClearMutilatedBanknoteModule'

    # sequence 3 : ask headquarters then no payback
    sequence_string_3 = 'Tic CheckObjects Tic CheckInitialInventory ' \
                        + 'CreateMutilatedBanknote Tic ' \
                        + 'CreateIncomingLine Tic ' \
                        + 'StopDocument Tic ' \
                        + 'CreateExchangedLine Tic TryPlanWithExchangedLine DelExchangedLine Tic PlanDocument Tic ' \
                        + 'HQLogin ' \
                        + 'CheckHQInitialInventory ' \
                        + 'CreateHQMutilatedBanknote Tic '\
                        + 'TryStopHQWithNoLineDefined Tic CreateHQIncomingLine Tic TryStopHQWithNoAmountDefined StopHQDocument Tic ' \
                        + 'TryPlanHQDocument ' \
                        + 'ArchiveHQDocument Tic ' \
                        + 'HQLogout ' \
                        + 'CheckHQFinalInventoryWithNoPayBack ClearHQMutilatedBanknoteModule Tic ' \
                        + 'ArchiveDocument Tic ' \
                        + 'CheckFinalInventoryWithNoPayBackAfterHQRequest ClearMutilatedBanknoteModule'
    
    # sequence 4 : ask headquarters then payback
    sequence_string_4 = 'Tic CheckObjects Tic CheckInitialInventory ' \
                        + 'CreateMutilatedBanknote Tic ' \
                        + 'CreateIncomingLine Tic ' \
                        + 'StopDocument Tic ' \
                        + 'PlanDocument Tic ' \
                        + 'HQLogin ' \
                        + 'CheckHQInitialInventory ' \
                        + 'CreateHQMutilatedBanknote Tic '\
                        + 'CreateHQIncomingLine Tic StopHQDocument Tic ' \
                        + 'TryFinishHQWithNoLineDefined CreateHQExchangedLine Tic TryFinishHQWithNoAmountDefined FinishHQDocument Tic ' \
                        + 'HQLogout ' \
                        + 'CheckHQFinalInventoryWithPayBack ClearHQMutilatedBanknoteModule Tic '\
                        + 'CreateExchangedLine Tic FinishDocument Tic ' \
                        + 'CreateOutgoingLine Tic DeliverDocument Tic ' \
                        + 'CheckFinalInventoryWithPayBackAfterHQRequest ClearMutilatedBanknoteModule'

    sequence_list.addSequenceString(sequence_string_1)
    sequence_list.addSequenceString(sequence_string_2)
    sequence_list.addSequenceString(sequence_string_3)
    sequence_list.addSequenceString(sequence_string_4)
    # play the sequence
    sequence_list.play(self)

# define how we launch the unit test
if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestERP5BankingMutilatedBanknote))
    return suite
