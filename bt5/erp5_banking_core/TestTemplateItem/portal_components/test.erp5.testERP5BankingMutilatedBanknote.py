
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
from Products.DCWorkflow.DCWorkflow import Unauthorized, ValidationFailed
from erp5.component.module.TestERP5BankingMixin import TestERP5BankingMixin
from DateTime import DateTime

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

class TestERP5BankingMutilatedBanknote(TestERP5BankingMixin):
  """
  """

  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet

  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingMutilatedBanknote"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    self.simulation_tool = self.getSimulationTool()
    # Set some variables :
    self.initDefaultVariable()
    # the cahs transfer module
    self.mutilated_banknote_module = self.getMutilatedBanknoteModule()
    self.createManagerAndLogin()
    # create categories
    self.createFunctionGroupSiteCategory(site_list = ['siege', 'paris'])
    # Before the test, we need to input the inventory
    inventory_dict_line_1 = {'id' : 'inventory_line_1',
                             'resource': self.billet_10000,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/not_defined', 'cash_status/valid') + self.variation_list,
                             'quantity': self.quantity_10000}

    line_list = [inventory_dict_line_1]
    self.mutilated_banknote_vault = self.paris.surface.caisse_courante.billets_mutiles
    self.maculated_banknote_vault = self.paris.surface.caisse_courante.billets_macules
    self.counter = self.paris.surface.banque_interne.guichet_1.encaisse_des_billets_et_monnaies.sortante
    self.hq_mutilated_banknote_vault = self.siege.surface.caisse_courante.billets_mutiles
    self.hq_maculated_banknote_vault = self.siege.surface.caisse_courante.billets_macules
    self.usual_vault = self.paris.surface.caisse_courante.encaisse_des_billets_et_monnaies
    self.hq_usual_vault = self.siege.surface.caisse_courante.encaisse_des_billets_et_monnaies
    self.hq_counter = self.siege.surface.banque_interne.guichet_1.encaisse_des_billets_et_monnaies.sortante
    self.counter_incomming = self.paris.surface.banque_interne.guichet_1.encaisse_des_billets_et_monnaies.entrante
    self.hq_counter_incomming = self.siege.surface.banque_interne.guichet_1.encaisse_des_billets_et_monnaies.entrante
    self.createCashInventory(source=None, destination=self.counter, currency=self.currency_1,
                             line_list=line_list)
    self.createCashInventory(source=None, destination=self.hq_counter, currency=self.currency_1,
                             line_list=line_list)
    # now we need to create a user as Manager to do the test
    # in order to have an assigment defined which is used to do transition
    # Create an Organisation that will be used for users assignment
    self.checkUserFolderType()
    self.organisation_1 = self.organisation_module.newContent(id='baobab_org', portal_type='Organisation',
                          function='banking', group='baobab',  site='testsite/paris')
    self.organisation_2 = self.organisation_module.newContent(id='baobab_org_hq', portal_type='Organisation',
                                                            function='banking', group='baobab',  site='siege')
    # define the user
    user_dict = {
        'super_user' : [['Manager'], self.organisation_1, 'banking/comptable', 'baobab', 'testsite/paris/surface/banque_interne/guichet_1'],
        'hq_super_user' : [['Manager'], self.organisation_2, 'banking/comptable', 'baobab', 'siege/surface/banque_interne/guichet_1']
      }
    # call method to create this user
    self.createERP5Users(user_dict)
    self.logout()
    self.loginByUserName('super_user')
    self.future_date =  DateTime(DateTime().Date()) + 4
    self.openCounterDate(site=self.paris)
    self.openCounterDate(site=self.siege, id='counter_date_2')
    self.openCounterDate(site=self.paris, id='counter_date_3', date=self.future_date)
    self.openCounterDate(site=self.siege, id='counter_date_4', date=self.future_date)
    self.openCounter(site=self.paris.surface.banque_interne.guichet_1)
    self.openCounter(site=self.siege.surface.banque_interne.guichet_1, id='counter_2')

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

  def stepCancelDocument(self, sequence=None, sequence_list=None, **kwd):
    """
      Cancel document.
    """
    self.workflow_tool.doActionFor(self.mutilated_banknote, 'cancel_action', wf_id='mutilated_banknote_workflow')
    self.assertEqual(self.mutilated_banknote.getSimulationState(), 'cancelled')

  def stepArchiveDocument(self, sequence=None, sequence_list=None, **kwd):
    """
      Archive document.
    """
    self.workflow_tool.doActionFor(self.mutilated_banknote, 'archive_action', wf_id='mutilated_banknote_workflow')
    self.assertEqual(self.mutilated_banknote.getSimulationState(), 'archived')

  def stepCancelHQDocument(self, sequence=None, sequence_list=None, **kwd):
    """
      Cancel HQ document.
    """
    self.workflow_tool.doActionFor(self.hq_mutilated_banknote, 'cancel_action', wf_id='mutilated_banknote_workflow')
    self.assertEqual(self.hq_mutilated_banknote.getSimulationState(), 'cancelled')


  def stepDepositDocument(self, sequence=None, sequence_list=None, **kwd):
    """
      Deposit document.
    """
    self.workflow_tool.doActionFor(self.mutilated_banknote, 'deposit_action', wf_id='mutilated_banknote_workflow')
    self.assertEqual(self.mutilated_banknote.getSimulationState(), 'depositied')

  def stepDepositHQDocument(self, sequence=None, sequence_list=None, **kwd):
    """
      Deposit HQ document.
    """
    self.hq_mutilated_banknote.setDestinationTotalAssetPrice(50000.0)
    self.assertEqual(self.hq_mutilated_banknote.getDestinationTotalAssetPrice(), 50000.0)
    self.workflow_tool.doActionFor(self.hq_mutilated_banknote, 'deposit_action', wf_id='mutilated_banknote_workflow')
    self.tic()
    self.assertEqual(self.hq_mutilated_banknote.getSimulationState(), 'deposited')

  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    # check we have 5 banknotes of 10000 in mutilated_banknote
    self.checkBanknoteInventory(node_path=self.counter.getRelativeUrl(), quantity=5.0)
    # mutilated banknote inventory contains no 10000 banknote
    self.checkBanknoteInventory(node_path=self.mutilated_banknote_vault.getRelativeUrl(), quantity=0.0)
    # maculated banknote inventory contains no 10000 banknote
    self.checkBanknoteInventory(node_path=self.maculated_banknote_vault.getRelativeUrl(), quantity=0.0)
    # Nothing in counter's incomming
    self.checkBanknoteInventory(node_path=self.counter_incomming.getRelativeUrl(), quantity=0.0)
    # Nothing in HQ counter's incomming
    self.checkBanknoteInventory(node_path=self.hq_counter_incomming.getRelativeUrl(), quantity=0.0)
    # Nothing in usual vault
    self.checkBanknoteInventory(node_path=self.usual_vault.getRelativeUrl(), quantity=0.0)

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
                                    deponent="user",
                                    destination_value=self.mutilated_banknote_vault,
                                    site_value=self.paris)
    self.tic()
    self.assertTrue(len(self.mutilated_banknote_module.objectValues()) != 0)
    self.assertEqual(self.mutilated_banknote.getPortalType(), 'Mutilated Banknote')
    self.assertEqual(self.mutilated_banknote.getSource(), 'site/testsite/paris/surface/banque_interne/guichet_1')
    self.assertEqual(self.mutilated_banknote.getSourceTrade(), 'site/testsite/paris')
    self.assertEqual(self.mutilated_banknote.getDestination(), self.mutilated_banknote_vault.getRelativeUrl())
    # set source reference
    self.setDocumentSourceReference(self.mutilated_banknote)
    # check source reference
    self.assertNotEqual(self.mutilated_banknote.getSourceReference(), '')
    self.assertNotEqual(self.mutilated_banknote.getSourceReference(), None)
    # headquarter is used in order to know if the document will go to the
    # headquarter or not.
    sequence.edit(headquarter=0)


  def stepTryDraftWithNoLineDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to stop with no amount defined on the document
    """
    self.assertEqual(len(self.mutilated_banknote.objectValues()), 0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.mutilated_banknote, 'draft_action', wf_id='mutilated_banknote_workflow')

  def stepTryHQDraftWithNoLineDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to stop with no amount defined on the document
    """
    self.assertEqual(len(self.hq_mutilated_banknote.objectValues()), 0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.hq_mutilated_banknote, 'draft_action', wf_id='mutilated_banknote_workflow')

  def stepCreateIncomingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the incoming mutilated banknote line with banknotes of 10000 and check it has been well created
    """
    # create the  line
    self.addCashLineToDelivery(self.mutilated_banknote, 'incoming_line', 'Incoming Mutilated Banknote Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/mutilated') + self.variation_list,
            self.quantity_10000)
    self.tic()
    self.assertEqual(len(self.mutilated_banknote.objectValues()), 1)
    # get the  line
    self.incoming_line = getattr(self.mutilated_banknote, 'incoming_line')
    self.assertEqual(self.incoming_line.getPortalType(), 'Incoming Mutilated Banknote Line')
    self.assertEqual(self.incoming_line.getResourceValue(), self.billet_10000)
    self.assertEqual(self.incoming_line.getPrice(), 10000.0)
    self.assertEqual(self.incoming_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.incoming_line.objectValues()), 2)
    mutilated_banknote_destination = self.mutilated_banknote.getDestination()
    for variation in self.variation_list:
      cell = self.incoming_line.getCell('emission_letter/not_defined', variation, 'cash_status/mutilated')
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      self.assertEqual(cell.getBaobabSourceValue(), None)
      self.assertEqual(cell.getBaobabDestination(), None)
      if cell.getId() == 'movement_0_0_0':
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

  def stepTryDraftWithNoAmountDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to stop with no amount defined on the document
    """
    self.assertEqual(self.mutilated_banknote.getSourceTotalAssetPrice(), 0.0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.mutilated_banknote, 'draft_action', wf_id='mutilated_banknote_workflow')

  def stepTryHQDraftWithNoAmountDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to stop with no amount defined on the document
    """
    self.assertEqual(self.hq_mutilated_banknote.getSourceTotalAssetPrice(), 0.0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.hq_mutilated_banknote, 'draft_action', wf_id='mutilated_banknote_workflow')

  def stepDraftDocument(self, sequence=None, sequence_list=None, **kw):
    """
    Draft mutilated banknote operation
    Also sets the received amount on the document.
    """
    self.mutilated_banknote.setSourceTotalAssetPrice(50000.0)
    self.assertEqual(self.mutilated_banknote.getSourceTotalAssetPrice(), 50000.0)
    self.workflow_tool.doActionFor(self.mutilated_banknote, 'draft_action', wf_id='mutilated_banknote_workflow')
    self.tic()
    self.assertEqual(self.mutilated_banknote.getSimulationState(), "draft")

  def stepDraftHQDocument(self, sequence=None, sequence_list=None, **kw):
    """
    Draft mutilated banknote operation
    Also set the original price of mutilated banknotes.
    """
    self.hq_mutilated_banknote.setSourceTotalAssetPrice(50000.0)
    self.assertEqual(self.hq_mutilated_banknote.getSourceTotalAssetPrice(), 50000.0)
    self.workflow_tool.doActionFor(self.hq_mutilated_banknote, 'draft_action', wf_id='mutilated_banknote_workflow')
    self.tic()
    self.assertEqual(self.hq_mutilated_banknote.getSimulationState(), "draft")

  def stepStopDocument(self, sequence=None, sequence_list=None, **kw):
    """
    Stop mutilated banknote operation
    """
    self.workflow_tool.doActionFor(self.mutilated_banknote, 'stop_action', wf_id='mutilated_banknote_workflow')
    self.tic()
    self.assertEqual(self.mutilated_banknote.getSimulationState(), "stopped")

  def stepCreateExchangedLine(self, sequence=None, sequence_list=None, **kw):
    """
    """
    # create an exchanged
    self.addCashLineToDelivery(self.mutilated_banknote, 'exchanged_line', 'Exchanged Mutilated Banknote Line', self.billet_10000,
                               ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/cancelled') + self.variation_list,
                               self.quantity_10000)
    self.tic()
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
      cell = self.exchanged_line.getCell('emission_letter/not_defined', variation, 'cash_status/cancelled')
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      self.assertEqual(cell.getBaobabSourceValue(), None)
      self.assertEqual(cell.getBaobabDestinationValue(), None)
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
    self.tic()
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
    self.tic()
    self.assertEqual(self.mutilated_banknote.getSimulationState(), "delivered")

  def stepDeliverHQDocument(self, sequence=None, sequence_list=None, **kw):
    """
    Deliver mutilated banknote operation.
    Also sets the exchanged amount on the document.
    """
    self.hq_mutilated_banknote.setDestinationTotalAssetPrice(50000.0)
    self.assertEqual(self.hq_mutilated_banknote.getDestinationTotalAssetPrice(), 50000.0)
    self.workflow_tool.doActionFor(self.hq_mutilated_banknote, 'deliver_action', wf_id='mutilated_banknote_workflow')
    self.tic()
    self.assertEqual(self.hq_mutilated_banknote.getSimulationState(), "delivered")

  def stepCheckFinalInventoryWithNoPayBack(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the final inventory when document got rejected without HQ request
    """
    self.checkBanknoteInventory(node_path=self.counter.getRelativeUrl(), quantity=5.0)
    self.checkBanknoteInventory(node_path=self.counter_incomming.getRelativeUrl(), quantity=0.0)
    self.checkBanknoteInventory(node_path=self.hq_counter_incomming.getRelativeUrl(), quantity=0.0)
    self.checkFinalInventory()

  stepCheckFinalInventoryWithNoPayBackAfterHQRequest = stepCheckFinalInventoryWithNoPayBack

  def stepClearMutilatedBanknoteModule(self, sequence=None, sequence_list=None, **kw):
    """
    Remove all operations in module
    """
    delattr(self, 'mutilated_banknote')
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

  def stepTryDepositHQWithNoLineDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to deposit with no line defined on the document
    """
    self.assertEqual(len(self.hq_mutilated_banknote.objectValues(portal_type="Exchanged Mutilated Banknote Line")), 0.0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.hq_mutilated_banknote, 'deposit_action', wf_id='mutilated_banknote_workflow')

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

  def stepTryDepositHQWithNoAmountDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to deposit with no amount defined on the document
    """
    self.assertEqual(self.hq_mutilated_banknote.getDestinationTotalAssetPrice(), 0.0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.hq_mutilated_banknote, 'deposit_action', wf_id='mutilated_banknote_workflow')

  def stepFinishDocument(self, sequence=None, sequence_list=None, **kw):
    """
    Finish mutilated banknote operation (send to counter)
    """
    self.mutilated_banknote.setDestinationTotalAssetPrice(50000.0)
    self.assertEqual(self.mutilated_banknote.getDestinationTotalAssetPrice(), 50000.0)
    self.workflow_tool.doActionFor(self.mutilated_banknote, 'finish_action', wf_id='mutilated_banknote_workflow')
    self.tic()
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

  def stepTryDeliverHQWithNoLineDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to deliver with no outgoing line defined on the document
    """
    self.assertEqual(len(self.hq_mutilated_banknote.objectValues(portal_type="Outgoing Mutilated Banknote Line")), 0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.hq_mutilated_banknote, 'deliver_action', wf_id='mutilated_banknote_workflow')

  def stepTryDeliverHQWithWrongAmountDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to deliver with wrong amount defined on the document at state ordered
    """
    self.hq_mutilated_banknote.setDestinationTotalAssetPrice(4000.0)
    self.assertEqual(self.hq_mutilated_banknote.getDestinationTotalAssetPrice(), 4000.0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.hq_mutilated_banknote, 'deliver_action', wf_id='mutilated_banknote_workflow')

  def createOutgoingLine(self, mutilated_banknote):
    """
    """
    # create an exchanged
    self.addCashLineToDelivery(mutilated_banknote, 'outgoing_line', 'Outgoing Mutilated Banknote Line', self.billet_10000,
                               ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/valid') + self.variation_list,
                               self.quantity_10000)
    self.tic()
    # get the line
    self.outgoing_line = getattr(mutilated_banknote, 'outgoing_line')
    self.assertEqual(self.outgoing_line.getPortalType(), 'Outgoing Mutilated Banknote Line')
    self.assertEqual(self.outgoing_line.getResourceValue(), self.billet_10000)
    self.assertEqual(self.outgoing_line.getPrice(), 10000.0)
    self.assertEqual(self.outgoing_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.outgoing_line.objectValues()), 2)
    for variation in self.variation_list:
      cell = self.outgoing_line.getCell('emission_letter/not_defined', variation, 'cash_status/valid')
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

  def stepCreateOutgoingLine(self, sequence=None, sequence_list=None, **kw):
    """
    """
    self.createOutgoingLine(self.mutilated_banknote)

  def stepCreateHQOutgoingLine(self, sequence=None, sequence_list=None, **kw):
    """
    """
    self.createOutgoingLine(self.hq_mutilated_banknote)

  def stepCheckFinalInventoryWithPayBack(self, sequence=None, sequence_list=None, **kwd):
    self.checkBanknoteInventory(node_path=self.counter.getRelativeUrl(), quantity=0.0, get_inventory_kw={'variation_text': '%cash_status/valid%'})
    self.checkBanknoteInventory(node_path=self.counter_incomming.getRelativeUrl(), quantity=5.0)
    self.checkBanknoteInventory(node_path=self.hq_counter_incomming.getRelativeUrl(), quantity=0.0)
    self.checkFinalInventory()

  def checkFinalInventory(self):
    self.checkBanknoteInventory(node_path=self.hq_counter.getRelativeUrl(), quantity=5.0)
    self.checkBanknoteInventory(node_path=self.mutilated_banknote_vault.getRelativeUrl(), quantity=0.0)
    self.checkBanknoteInventory(node_path=self.maculated_banknote_vault.getRelativeUrl(), quantity=0.0)
    self.checkBanknoteInventory(node_path=self.hq_mutilated_banknote_vault.getRelativeUrl(), quantity=0.0)
    self.checkBanknoteInventory(node_path=self.hq_maculated_banknote_vault.getRelativeUrl(), quantity=0.0)
    self.checkBanknoteInventory(node_path=self.usual_vault.getRelativeUrl(), quantity=0.0)
    self.checkBanknoteInventory(node_path=self.hq_usual_vault.getRelativeUrl(), quantity=0.0)

  def stepCheckFinalInventoryWithPayBackAfterHQRequest(self, sequence=None, sequence_list=None, **kw):
    self.checkBanknoteInventory(node_path=self.counter.getRelativeUrl(), quantity=5.0, get_inventory_kw={'at_date': self.future_date - 1})
    self.checkBanknoteInventory(node_path=self.counter.getRelativeUrl(), quantity=0.0, get_inventory_kw={'at_date': self.future_date + 1})
    self.checkBanknoteInventory(node_path=self.hq_usual_vault.getRelativeUrl(), quantity=0.0, get_inventory_kw={'at_date': self.future_date - 1})
    self.checkBanknoteInventory(node_path=self.hq_usual_vault.getRelativeUrl(), quantity=5.0, get_inventory_kw={'at_date': self.future_date + 1})
    for offset in (-1, 1):
      self.checkBanknoteInventory(node_path=self.hq_counter_incomming.getRelativeUrl(), quantity=0.0, get_inventory_kw={'at_date': self.future_date + offset})
      self.checkBanknoteInventory(node_path=self.usual_vault.getRelativeUrl(), quantity=0.0, get_inventory_kw={'at_date': self.future_date + offset})
      self.checkBanknoteInventory(node_path=self.counter_incomming.getRelativeUrl(), quantity=0.0, get_inventory_kw={'at_date': self.future_date + offset})
      self.checkBanknoteInventory(node_path=self.hq_counter.getRelativeUrl(), quantity=5.0, get_inventory_kw={'at_date': self.future_date + offset})
      self.checkBanknoteInventory(node_path=self.mutilated_banknote_vault.getRelativeUrl(), quantity=0.0, get_inventory_kw={'at_date': self.future_date + offset})
      self.checkBanknoteInventory(node_path=self.maculated_banknote_vault.getRelativeUrl(), quantity=0.0, get_inventory_kw={'at_date': self.future_date + offset})
      self.checkBanknoteInventory(node_path=self.hq_mutilated_banknote_vault.getRelativeUrl(), quantity=0.0, get_inventory_kw={'at_date': self.future_date + offset})
      self.checkBanknoteInventory(node_path=self.hq_maculated_banknote_vault.getRelativeUrl(), quantity=0.0, get_inventory_kw={'at_date': self.future_date + offset})

  #
  # Headquarter part
  #
  def stepHQLogin(self, sequence=None, sequence_list=None, **kw):
    """
    Login as a headquarter user
    """
    self.logout()
    self.loginByUserName("hq_super_user")

  def stepHQLogout(self, sequence=None, sequence_list=None, **kw):
    """
    Login as a headquarter user
    """
    self.logout()
    self.loginByUserName("super_user")

  def stepCheckHQInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    # check we have 5 banknotes of 10000 in mutilated_banknote
    self.checkBanknoteInventory(node_path=self.hq_counter.getRelativeUrl(), quantity=5.0)
    # mutilated banknote inventory contains no 10000 banknote
    self.checkBanknoteInventory(node_path=self.hq_mutilated_banknote_vault.getRelativeUrl(), quantity=0.0)
    # maculated banknote inventory contains no 10000 banknote
    self.checkBanknoteInventory(node_path=self.hq_maculated_banknote_vault.getRelativeUrl(), quantity=0.0)
    # nothing in usual vault
    self.checkBanknoteInventory(node_path=self.hq_usual_vault.getRelativeUrl(), quantity=0.0)

  def stepCreateHQMutilatedBanknote(self, sequence=None, sequence_list=None,
      owner_assigned_counter='site/siege/surface/banque_interne/guichet_1', **kwd):
    """
    Create a mutilated banknote document and check it
    """
    self.hq_mutilated_banknote = self.mutilated_banknote_module.newContent(id='hq_mutilated_banknote',
                                                                           portal_type='Mutilated Banknote',
                                                                           source_total_asset_price=0.0,
                                                                           destination_total_asset_price=0.0,
                                                                           destination_value=self.hq_mutilated_banknote_vault,
                                                                           deponent="hq user",
                                                                           causality_value=getattr(self, 'mutilated_banknote', None),
                                                                           site_value=self.siege)
    self.hq_mutilated_banknote.edit(source_trade='site/testsite/paris')
    self.tic()
    self.assertTrue(len(self.mutilated_banknote_module.objectValues()) != 0)
    self.assertEqual(self.hq_mutilated_banknote.getPortalType(), 'Mutilated Banknote')
    self.assertEqual(self.hq_mutilated_banknote.getSource(), owner_assigned_counter)
    self.assertEqual(self.hq_mutilated_banknote.getSourceTrade(), 'site/testsite/paris')
    self.assertEqual(self.hq_mutilated_banknote.getDestination(), self.hq_mutilated_banknote_vault.getRelativeUrl())
    # set source reference
    self.setDocumentSourceReference(self.hq_mutilated_banknote)
    # check source reference
    self.assertNotEqual(self.hq_mutilated_banknote.getSourceReference(), '')
    self.assertNotEqual(self.hq_mutilated_banknote.getSourceReference(), None)


  def stepTryDraftHQWithNoLineDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to plan with no amount defined on the document
    """
    self.assertEqual(len(self.hq_mutilated_banknote.objectValues()), 0.0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.hq_mutilated_banknote, 'draft_action', wf_id='mutilated_banknote_workflow')

  def stepCreateHQIncomingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the incoming mutilated banknote line with banknotes of 10000 and check it has been well created
    """
    # create the  line
    self.addCashLineToDelivery(self.hq_mutilated_banknote, 'hq_incoming_line', 'Incoming Mutilated Banknote Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/mutilated') + self.variation_list,
            self.quantity_10000)
    self.tic()
    self.assertEqual(len(self.hq_mutilated_banknote.objectValues()), 1)
    # get the  line
    self.hq_incoming_line = getattr(self.hq_mutilated_banknote, 'hq_incoming_line')
    self.assertEqual(self.hq_incoming_line.getPortalType(), 'Incoming Mutilated Banknote Line')
    self.assertEqual(self.hq_incoming_line.getResourceValue(), self.billet_10000)
    self.assertEqual(self.hq_incoming_line.getPrice(), 10000.0)
    self.assertEqual(self.hq_incoming_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.hq_incoming_line.objectValues()), 2)
    hq_mutilated_banknote_destination = self.hq_mutilated_banknote.getDestination()
    for variation in self.variation_list:
      cell = self.hq_incoming_line.getCell('emission_letter/not_defined', variation, 'cash_status/mutilated')
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      self.assertEqual(cell.getBaobabSourceValue(), None)
      self.assertEqual(cell.getBaobabDestination(), None)
      if cell.getId() == 'movement_0_0_0':
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

  def stepTryDraftHQWithNoAmountDefined(self, sequence=None, sequence_list=None, **kw):
    """
    Try to plan with no amount defined on the document
    """
    self.assertEqual(self.hq_mutilated_banknote.getSourceTotalAssetPrice(), 0.0)
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.hq_mutilated_banknote, 'draft_action', wf_id='mutilated_banknote_workflow')

  def stepStopHQDocument(self, sequence=None, sequence_list=None, **kw):
    """
    Plan mutilated banknote operation
    """
    self.workflow_tool.doActionFor(self.hq_mutilated_banknote, 'stop_action', wf_id='mutilated_banknote_workflow')
    self.tic()
    self.assertEqual(self.hq_mutilated_banknote.getSimulationState(), "stopped")

  def stepTryPlanHQDocument(self, sequence=None, sequence_list=None, **kw):
    """
      It must not be possible (ie, action not present) to plan when the document is initiated in HQ.
    """
    self.assertRaises(Unauthorized, self.workflow_tool.doActionFor, self.hq_mutilated_banknote, 'plan_action', wf_id='mutilated_banknote_workflow')

  def stepTryFinishHQDocument(self, sequence=None, sequence_list=None, **kw):
    """
      It must not be possible (ie, action not present) to finish when the document is sent to HQ.
    """
    self.assertRaises(Unauthorized, self.workflow_tool.doActionFor, self.hq_mutilated_banknote, 'finish_action', wf_id='mutilated_banknote_workflow')

  def stepFinishHQDocument(self, sequence=None, sequence_list=None, **kw):
    """
    Finish mutilated banknote operation
    Also set the price to pay back to the customer.
    """
    self.hq_mutilated_banknote.setDestinationTotalAssetPrice(50000.0)
    self.assertEqual(self.hq_mutilated_banknote.getDestinationTotalAssetPrice(), 50000.0)
    self.workflow_tool.doActionFor(self.hq_mutilated_banknote, 'finish_action', wf_id='mutilated_banknote_workflow')
    self.tic()
    self.assertEqual(self.hq_mutilated_banknote.getSimulationState(), "finished")
    sequence.edit(headquarter=1)

  def checkBanknoteInventory(self, node_path, quantity, get_inventory_kw=None):
    """
      Check that node contains expected quantity of banknotes.
    """
    if get_inventory_kw is None:
      get_inventory_kw = {}
    resource_path = self.billet_10000.getRelativeUrl()
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=node_path, resource=resource_path, **get_inventory_kw), quantity)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=node_path, resource=resource_path, **get_inventory_kw), quantity)

  def stepCheckHQMaculatedBanknoteInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check HQ maculated banknote inventory
    """
    self.checkBanknoteInventory(node_path=self.hq_maculated_banknote_vault.getRelativeUrl(), quantity=5.0)

  def stepCheckHQFinalInventoryWithNoPayBack(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.checkBanknoteInventory(node_path=self.counter.getRelativeUrl(), quantity=5.0)
    self.checkBanknoteInventory(node_path=self.hq_mutilated_banknote_vault.getRelativeUrl(), quantity=0.0)
    self.checkBanknoteInventory(node_path=self.hq_counter_incomming.getRelativeUrl(), quantity=0.0)
    self.checkFinalInventory()

  def stepClearHQMutilatedBanknoteModule(self, sequence=None, sequence_list=None, **kw):
    """
    Remove all operations in module
    """
    delattr(self, 'hq_mutilated_banknote')
    self.mutilated_banknote_module.deleteContent('hq_mutilated_banknote')

  def stepCreateHQExchangedLine(self, sequence=None, sequence_list=None, **kw):
    """
    """
    # create an exchanged
    self.addCashLineToDelivery(self.hq_mutilated_banknote, 'hq_exchanged_line', 'Exchanged Mutilated Banknote Line', self.billet_10000,
                               ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/cancelled') + self.variation_list,
                               self.quantity_10000)
    self.tic()
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
      cell = self.hq_exchanged_line.getCell('emission_letter/not_defined', variation, 'cash_status/cancelled')
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      self.assertEqual(cell.getBaobabSourceValue(), None)
      self.assertEqual(cell.getBaobabDestination(), None)
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
    self.checkBanknoteInventory(node_path=self.hq_usual_vault.getRelativeUrl(), quantity=0.0, get_inventory_kw={'at_date': self.future_date - 1})
    self.checkBanknoteInventory(node_path=self.hq_usual_vault.getRelativeUrl(), quantity=5.0, get_inventory_kw={'at_date': self.future_date + 1})
    for offset in (-1, 1):
      self.checkBanknoteInventory(node_path=self.hq_counter_incomming.getRelativeUrl(), quantity=0.0, get_inventory_kw={'at_date': self.future_date + offset})
      self.checkBanknoteInventory(node_path=self.counter.getRelativeUrl(), quantity=5.0, get_inventory_kw={'at_date': self.future_date + offset})
      self.checkBanknoteInventory(node_path=self.counter_incomming.getRelativeUrl(), quantity=0.0, get_inventory_kw={'at_date': self.future_date + offset})
      self.checkBanknoteInventory(node_path=self.hq_counter.getRelativeUrl(), quantity=5.0, get_inventory_kw={'at_date': self.future_date + offset})
      self.checkBanknoteInventory(node_path=self.mutilated_banknote_vault.getRelativeUrl(), quantity=0.0, get_inventory_kw={'at_date': self.future_date + offset})
      self.checkBanknoteInventory(node_path=self.maculated_banknote_vault.getRelativeUrl(), quantity=0.0, get_inventory_kw={'at_date': self.future_date + offset})
      self.checkBanknoteInventory(node_path=self.hq_mutilated_banknote_vault.getRelativeUrl(), quantity=0.0, get_inventory_kw={'at_date': self.future_date + offset})
      self.checkBanknoteInventory(node_path=self.hq_maculated_banknote_vault.getRelativeUrl(), quantity=0.0, get_inventory_kw={'at_date': self.future_date + offset})

  def stepCheckHQFinalInventoryWithHQPayBack(self, sequence=None, sequence_list=None, **kwd):
    self.checkBanknoteInventory(node_path=self.hq_usual_vault.getRelativeUrl(), quantity=0.0)
    self.checkBanknoteInventory(node_path=self.hq_mutilated_banknote_vault.getRelativeUrl(), quantity=0.0)
    self.checkBanknoteInventory(node_path=self.counter_incomming.getRelativeUrl(), quantity=0.0)
    self.checkBanknoteInventory(node_path=self.hq_counter_incomming.getRelativeUrl(), quantity=5.0)
    self.checkBanknoteInventory(node_path=self.hq_counter.getRelativeUrl(), quantity=0.0)
    self.checkBanknoteInventory(node_path=self.mutilated_banknote_vault.getRelativeUrl(), quantity=0.0)
    self.checkBanknoteInventory(node_path=self.maculated_banknote_vault.getRelativeUrl(), quantity=0.0)
    self.checkBanknoteInventory(node_path=self.hq_mutilated_banknote_vault.getRelativeUrl(), quantity=0.0)
    self.checkBanknoteInventory(node_path=self.hq_maculated_banknote_vault.getRelativeUrl(), quantity=0.0)

  def CheckInventoryWithIncommingBanknotes(self, node, hq_node):
    """
    Check that mutilated banknotes transmites by agency are in the right stock place.
    """
    self.checkBanknoteInventory(node_path=node.getRelativeUrl(), quantity=5.0)
    self.checkBanknoteInventory(node_path=hq_node.getRelativeUrl(), quantity=0.0)

  def stepCheckInventoryWithIncommingMutilatedBanknotes(self, sequence=None, sequence_list=None, **kwd):
    self.CheckInventoryWithIncommingBanknotes(self.mutilated_banknote_vault, self.hq_mutilated_banknote_vault)

  def stepCheckInventoryWithIncommingMaculatedBanknotes(self, sequence=None, sequence_list=None, **kwd):
    self.CheckInventoryWithIncommingBanknotes(self.maculated_banknote_vault, self.hq_maculated_banknote_vault)

  def CheckHQInventoryWithIncommingBanknotes(self, node, hq_node):
    """
    Check that mutilated banknotes transmites by agency are in the right stock place.
    """
    self.checkBanknoteInventory(node_path=node.getRelativeUrl(), quantity=0.0)
    self.checkBanknoteInventory(node_path=hq_node.getRelativeUrl(), quantity=5.0)

  def stepCheckHQInventoryWithIncommingMutilatedBanknotes(self, sequence=None, sequence_list=None, **kwd):
    self.CheckHQInventoryWithIncommingBanknotes(self.mutilated_banknote_vault, self.hq_mutilated_banknote_vault)

  def stepCheckHQInventoryWithIncommingMaculatedBanknotes(self, sequence=None, sequence_list=None, **kwd):
    self.CheckHQInventoryWithIncommingBanknotes(self.maculated_banknote_vault, self.hq_maculated_banknote_vault)

  def stepSetMaculatedState(self, sequence=None, sequence_list=None, **kwd):
    """
    Inform that the banknotes are in a maculated state, not in a mutilated state.
    """
    self.mutilated_banknote.setDestinationValue(self.maculated_banknote_vault)

  def stepSetHQMaculatedState(self, sequence=None, sequence_list=None, **kwd):
    """
    Inform that the banknotes are in a maculated state, not in a mutilated state.
    """
    self.hq_mutilated_banknote.setDestinationValue(self.hq_maculated_banknote_vault)

  def moveToFuture(self, document):
    """
      Set document's stop date to self.future_date.
    """
    document.setStopDate(self.future_date)

  def stepMoveToFuture(self, sequence=None, sequence_list=None, **kwd):
    self.moveToFuture(self.mutilated_banknote)

  def stepMoveHQToFuture(self, sequence=None, sequence_list=None, **kwd):
    self.moveToFuture(self.hq_mutilated_banknote)

  ##################################
  ##  Tests
  ##################################
  def test_01_ERP5BankingMutilatedBanknote(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()
    # define the sequence
    # sequence 1 : no payback, mutilated banknotes
    sequence_string_1 = 'Tic CheckObjects Tic CheckInitialInventory ' \
                        + 'CreateMutilatedBanknote Tic TryDraftWithNoLineDefined ' \
                        + 'CreateIncomingLine Tic TryDraftWithNoAmountDefined ' \
                        + 'DraftDocument Tic StopDocument Tic ' \
                        + 'CheckInventoryWithIncommingMutilatedBanknotes ' \
                        + 'CancelDocument Tic ' \
                        + 'CheckFinalInventoryWithNoPayBack ClearMutilatedBanknoteModule'

    # sequence 2 : pay back, maculated banknotes
    sequence_string_2 = 'Tic CheckObjects Tic CheckInitialInventory ' \
                        + 'CreateMutilatedBanknote SetMaculatedState Tic ' \
                        + 'CreateIncomingLine Tic ' \
                        + 'DraftDocument Tic StopDocument Tic ' \
                        + 'CheckInventoryWithIncommingMaculatedBanknotes ' \
                        + 'TryFinishWithNoLineDefined CreateExchangedLine Tic TryFinishWithNoAmountDefined FinishDocument Tic ' \
                        + 'TryDeliverWithNoLineDefined CreateOutgoingLine Tic TryDeliverWithWrongAmountDefined DeliverDocument Tic ' \
                        + 'CheckFinalInventoryWithPayBack ClearMutilatedBanknoteModule'

    # sequence 3 : ask headquarters then no payback, mutilated banknotes
    sequence_string_3 = 'Tic CheckObjects Tic CheckInitialInventory ' \
                        + 'CreateMutilatedBanknote Tic ' \
                        + 'CreateIncomingLine Tic ' \
                        + 'DraftDocument Tic StopDocument Tic ' \
                        + 'CheckInventoryWithIncommingMutilatedBanknotes ' \
                        + 'CreateExchangedLine Tic TryPlanWithExchangedLine DelExchangedLine Tic PlanDocument Tic ' \
                        + 'HQLogin ' \
                        + 'CheckHQInitialInventory ' \
                        + 'CreateHQMutilatedBanknote Tic '\
                        + 'TryDraftHQWithNoLineDefined Tic CreateHQIncomingLine Tic TryDraftHQWithNoAmountDefined DraftHQDocument Tic StopHQDocument Tic ' \
                        + 'CheckHQInventoryWithIncommingMutilatedBanknotes ' \
                        + 'TryPlanHQDocument ' \
                        + 'CancelHQDocument Tic ' \
                        + 'HQLogout ' \
                        + 'CheckHQFinalInventoryWithNoPayBack ' \
                        + 'ArchiveDocument Tic ' \
                        + 'CheckFinalInventoryWithNoPayBackAfterHQRequest ClearMutilatedBanknoteModule ClearHQMutilatedBanknoteModule'

    # sequence 4 : ask headquarters then payback, maculated banknotes
    sequence_string_4 = 'Tic CheckObjects Tic CheckInitialInventory ' \
                        + 'CreateMutilatedBanknote SetMaculatedState Tic ' \
                        + 'CreateIncomingLine Tic ' \
                        + 'DraftDocument Tic StopDocument Tic ' \
                        + 'PlanDocument Tic ' \
                        + 'HQLogin ' \
                        + 'CheckHQInitialInventory ' \
                        + 'CreateHQMutilatedBanknote SetHQMaculatedState Tic ' \
                        + 'CreateHQIncomingLine Tic DraftHQDocument Tic StopHQDocument Tic ' \
                        + 'MoveHQToFuture Tic ' \
                        + 'CheckHQInventoryWithIncommingMaculatedBanknotes ' \
                        + 'CheckHQMaculatedBanknoteInventory ' \
                        + 'TryDepositHQWithNoLineDefined CreateHQExchangedLine Tic TryDepositHQWithNoAmountDefined DepositHQDocument Tic ' \
                        + 'HQLogout ' \
                        + 'CheckHQFinalInventoryWithPayBack '\
                        + 'MoveToFuture Tic ' \
                        + 'CreateExchangedLine Tic FinishDocument Tic ' \
                        + 'CreateOutgoingLine Tic DeliverDocument Tic ' \
                        + 'CheckFinalInventoryWithPayBackAfterHQRequest ClearMutilatedBanknoteModule ClearHQMutilatedBanknoteModule'

    # sequence 5 : HQ, no payback, mutilated banknotes
    sequence_string_5 = 'Tic CheckObjects Tic CheckHQInitialInventory ' \
                        'HQLogin ' \
                        'CreateHQMutilatedBanknote Tic TryHQDraftWithNoLineDefined ' \
                        'CreateHQIncomingLine Tic TryHQDraftWithNoAmountDefined ' \
                        'DraftHQDocument Tic StopHQDocument Tic ' \
                        'CheckHQInventoryWithIncommingMutilatedBanknotes ' \
                        'CancelHQDocument Tic ' \
                        'CheckHQFinalInventoryWithNoPayBack ClearHQMutilatedBanknoteModule'

    # sequence 6 : HQ, pay back, maculated banknotes
    sequence_string_6 = 'Tic CheckObjects Tic CheckHQInitialInventory ' \
                        'HQLogin ' \
                        'CreateHQMutilatedBanknote SetHQMaculatedState Tic ' \
                        'CreateHQIncomingLine Tic ' \
                        'DraftHQDocument Tic StopHQDocument Tic ' \
                        'CheckHQInventoryWithIncommingMaculatedBanknotes ' \
                        'TryFinishHQWithNoLineDefined CreateHQExchangedLine Tic TryFinishHQWithNoAmountDefined FinishHQDocument Tic ' \
                        'TryDeliverHQWithNoLineDefined CreateHQOutgoingLine Tic TryDeliverHQWithWrongAmountDefined DeliverHQDocument Tic ' \
                        'CheckHQFinalInventoryWithHQPayBack ClearHQMutilatedBanknoteModule'

    #sequence_list.addSequenceString(sequence_string_1)
    #sequence_list.addSequenceString(sequence_string_2)
    #sequence_list.addSequenceString(sequence_string_3)
    sequence_list.addSequenceString(sequence_string_4)
    sequence_list.addSequenceString(sequence_string_5)
    sequence_list.addSequenceString(sequence_string_6)
    # play the sequence
    sequence_list.play(self)

