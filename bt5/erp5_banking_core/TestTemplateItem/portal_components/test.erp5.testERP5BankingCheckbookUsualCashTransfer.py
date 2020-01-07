
##############################################################################
#
# Copyright (c) 2006-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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
from erp5.component.test.testERP5BankingCheckbookVaultTransfer \
     import TestERP5BankingCheckbookVaultTransferMixin
from zLOG import LOG

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

class TestERP5BankingCheckbookUsualCashTransferMixin(
          TestERP5BankingCheckbookVaultTransferMixin):

  def createCheckbookVaultTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a checkbook Reception
    We do not need to check it because it is already done in another unit test.
    """
    self.checkbook_vault_transfer = self.getCheckbookVaultTransferModule().newContent(
                     id='checkbook_vault_transfer', portal_type='Checkbook Vault Transfer',
                     source_value=self.vault_transfer_source_site,
                     destination_value=self.vault_transfer_destination_site,
                     start_date=(self.date-3))
    # Add a line for check and checkbook
    self.line_1 = self.checkbook_vault_transfer.newContent(quantity=1,
                                 resource_value=self.checkbook_model_1,
                                 check_amount_value=self.checkbook_model_1.variant_1,
                                 destination_trade_value=self.bank_account_1,
                                 aggregate_value=self.checkbook_1,
                                 )
    self.line_2 = self.checkbook_vault_transfer.newContent(quantity=1,
                                 resource_value=self.check_model_1,
                                 check_amount_value=None,
                                 destination_trade_value=self.bank_account_2,
                                 aggregate_value=self.check_1,
                                 )
    self.workflow_tool.doActionFor(self.checkbook_vault_transfer, 'order_action',
                                   wf_id='checkbook_vault_transfer_workflow')
    self.workflow_tool.doActionFor(self.checkbook_vault_transfer, 'confirm_action',
                                   wf_id='checkbook_vault_transfer_workflow')
    self.workflow_tool.doActionFor(self.checkbook_vault_transfer, 'deliver_action',
                                   wf_id='checkbook_vault_transfer_workflow')

  def createCheckbookVaultTransferWithTravelerCheck(self, sequence=None,
                                 sequence_list=None, **kwd):
    """
    Create a checkbook Reception
    We do not need to check it because it is already done in another unit test.
    """
    self.checkbook_vault_transfer = self.getCheckbookVaultTransferModule().newContent(
                     id='checkbook_vault_transfer', portal_type='Checkbook Vault Transfer',
                     source_value=self.vault_transfer_source_site,
                     destination_value=self.vault_transfer_destination_site,
                     description='test',
                     start_date=(self.date-3))
    # Add a line for traveler check
    self.line_2 = self.checkbook_vault_transfer.newContent(quantity=1,
                             resource_value=self.traveler_check_model,
                             check_type_value=self.traveler_check_model.variant_1,
                             aggregate_value=self.traveler_check,
                             price_currency_value=self.currency_2
                             )
    self.workflow_tool.doActionFor(self.checkbook_vault_transfer, 'order_action',
                                   wf_id='checkbook_vault_transfer_workflow')
    self.workflow_tool.doActionFor(self.checkbook_vault_transfer, 'confirm_action',
                                   wf_id='checkbook_vault_transfer_workflow')
    self.workflow_tool.doActionFor(self.checkbook_vault_transfer, 'deliver_action',
                                   wf_id='checkbook_vault_transfer_workflow')

class TestERP5BankingCheckbookUsualCashTransfer(TestERP5BankingCheckbookUsualCashTransferMixin):
  """
    This class is a unit test to check the module of Cash Transfer

    Here are the following step that will be done in the test :

    XXX to be completed

  """


  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet


  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingCheckbookUsualCashTransfer"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    # Set some variables :
    self.initDefaultVariable()
    # the cash inventory module
    self.checkbook_usual_cash_transfer_module = self.getCheckbookUsualCashTransferModule()
    self.checkbook_reception_module = self.getCheckbookReceptionModule()
    self.check_module = self.getCheckModule()
    self.checkbook_module = self.getCheckbookModule()
    self.checkbook_model_module = self.getCheckbookModelModule()

    self.createManagerAndLogin()
    self.createFunctionGroupSiteCategory()
    self.createCheckAndCheckbookModel()
    self.vault_transfer_source_site = self.paris.caveau
    self.vault_transfer_destination_site = self.paris.surface
    self.source_site = self.paris.surface.caisse_courante
    self.reception_destination_site = self.paris
    self.destination_site = self.paris.surface.banque_interne.guichet_1
    self.source_vault = self.paris.surface.caisse_courante.encaisse_des_billets_et_monnaies
    self.destination_vault = self.paris.surface.banque_interne.guichet_1.encaisse_des_billets_et_monnaies
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

    # create a person and a bank account
    self.person_1 = self.createPerson(id='person_1',
                                      first_name='Sebastien',
                                      last_name='Robin')
    self.bank_account_1 = self.createBankAccount(person=self.person_1,
                                                 account_id='bank_account_1',
                                                 currency=self.currency_1,
                                                 amount=100000)
    # create a person and a bank account
    self.person_2 = self.createPerson(id='person_2',
                                      first_name='Aurelien',
                                      last_name='Calonne')
    self.bank_account_2 = self.createBankAccount(person=self.person_2,
                                                 account_id='bank_account_1',
                                                 currency=self.currency_1,
                                                 amount=100000)
    # this is required in order to have some items
    # in the source
    self.createCheckbookReception()
    self.checkItemsCreated()
    self.tic()
    self.createCheckbookVaultTransfer()


  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that CheckbookUsualCashTransfer Module was created
    self.assertEqual(self.checkbook_usual_cash_transfer_module.getPortalType(), 'Checkbook Usual Cash Transfer Module')
    # check cash inventory module is empty
    self.assertEqual(len(self.checkbook_usual_cash_transfer_module.objectValues()), 0)


  def stepCheckInitialCheckbookInventory(self, sequence=None, sequence_list=None, **kw):
    """
    Check initial cash checkbook on source
    """
    self.assertEqual(len(self.simulation_tool.getCurrentTrackingList(
                     node=self.source_vault.getRelativeUrl(),
                     at_date=self.date)), 2)
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(
                     node=self.source_vault.getRelativeUrl(),
                     at_date=self.date)), 2)
    self.assertEqual(len(self.simulation_tool.getCurrentTrackingList(
                             node=self.destination_vault.getRelativeUrl(),
                             at_date=self.date)), 0)
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(
                             node=self.destination_vault.getRelativeUrl(),
                             at_date=self.date)), 0)

  def stepCreateCheckbookUsualCashTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a checkbook usual cash transfer
    """
    # We will do the transfer ot two items.
    self.checkbook_usual_cash_transfer = self.checkbook_usual_cash_transfer_module.newContent(
                     id='checkbook_usual_cash_transfer', portal_type='Checkbook Usual Cash Transfer',
                     source_value=self.source_site, destination_value=self.destination_site,
                     resource_value=self.currency_1,
                     start_date=(self.date-3.1))
    # check its portal type
    self.assertEqual(self.checkbook_usual_cash_transfer.getPortalType(), 'Checkbook Usual Cash Transfer')
    # check source
    self.assertEqual(self.checkbook_usual_cash_transfer.getBaobabSource(),
               'site/testsite/paris/surface/caisse_courante/encaisse_des_billets_et_monnaies')
    # check destination
    self.assertEqual(self.checkbook_usual_cash_transfer.getBaobabDestination(),
               'site/testsite/paris/surface/banque_interne/guichet_1/encaisse_des_billets_et_monnaies')


  def stepCreateCheckAndCheckbookLineList(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the checkbook
    """
    # This is not required to create checkbook items, they will be
    # automatically created with the confirm action worfklow transition

    # Add a line for check and checkbook
    self.line_1 = self.checkbook_usual_cash_transfer.newContent(quantity=1,
                                 resource_value=self.checkbook_model_1,
                                 check_amount_value=self.checkbook_model_1.variant_1,
                                 reference_range_min=1,
                                 reference_range_max=50,
                                 aggregate_value=self.checkbook_1
                                 )
    self.line_2 = self.checkbook_usual_cash_transfer.newContent(quantity=1,
                                 resource_value=self.check_model_1,
                                 check_amount_value=None,
                                 reference_range_min=51,
                                 reference_range_max=51,
                                 aggregate_value=self.check_1
                                 )

  def stepCheckConfirmCheckbookUsualCashTransferRaiseError(self, sequence=None, sequence_list=None, **kwd):
    """
    confirm the checkbook usual cash transfer
    """
    state = self.checkbook_usual_cash_transfer.getSimulationState()
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor,
                      self.checkbook_usual_cash_transfer, 'confirm_action',
                      wf_id='checkbook_usual_cash_transfer_workflow')
    workflow_history = self.workflow_tool.getInfoFor(ob=self.checkbook_usual_cash_transfer, name='history', wf_id='checkbook_usual_cash_transfer_workflow')

  def stepConfirmCheckbookUsualCashTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    confirm the checkbook usual cash transfer
    """
    state = self.checkbook_usual_cash_transfer.getSimulationState()
    self.assertEqual(state, 'draft')
    self.workflow_tool.doActionFor(self.checkbook_usual_cash_transfer, 'confirm_action', wf_id='checkbook_usual_cash_transfer_workflow')
    self.assertEqual(self.checkbook_usual_cash_transfer.getSimulationState(), 'confirmed')
    workflow_history = self.workflow_tool.getInfoFor(ob=self.checkbook_usual_cash_transfer, name='history', wf_id='checkbook_usual_cash_transfer_workflow')

  def stepChangeCheckbookUsualCashTransferStartDate(self,
               sequence=None, sequence_list=None, **kw):
    """
    Set a correct date
    """
    self.checkbook_usual_cash_transfer.edit(start_date=self.date)

  def stepCheckConfirmedCheckbookInventory(self, sequence=None, sequence_list=None, **kw):
    """
    Check cash checkbook in item table
    """
    self.assertEqual(len(self.simulation_tool.getCurrentTrackingList(
                     node=self.source_vault.getRelativeUrl(),
                     at_date=self.date)), 2)
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(
                     node=self.source_vault.getRelativeUrl(),
                     at_date=self.date)), 0)
    self.assertEqual(len(self.simulation_tool.getCurrentTrackingList(
                     node=self.destination_vault.getRelativeUrl(),
                     at_date=self.date)), 0)
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(
                     node=self.destination_vault.getRelativeUrl(),
                     at_date=self.date)), 2)


  def stepDeliverCheckbookUsualCashTransfer(self, sequence=None, sequence_list=None, **kw):
    """
    Deliver the checkbook usual cash transfer
    """
    state = self.checkbook_usual_cash_transfer.getSimulationState()
    # check that state is draft
    self.assertEqual(state, 'confirmed')
    self.workflow_tool.doActionFor(self.checkbook_usual_cash_transfer,
                                   'confirm_to_deliver_action',
                                   wf_id='checkbook_usual_cash_transfer_workflow')
    # get state of cash sorting
    state = self.checkbook_usual_cash_transfer.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')

  def stepCheckFinalCheckbookInventory(self, sequence=None, sequence_list=None, **kw):
    """
    Check cash checkbook in item table
    """
    LOG('sql request for getCurrentTrackingList', 0, self.simulation_tool.getCurrentTrackingList(
                     node=self.source_vault.getRelativeUrl(),
                     at_date=self.date, src__=1))
    self.assertEqual(len(self.simulation_tool.getCurrentTrackingList(
                     node=self.source_vault.getRelativeUrl(),
                     at_date=self.date)), 0)
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(
                     node=self.source_vault.getRelativeUrl(),
                     at_date=self.date)), 0)
    self.assertEqual(len(self.simulation_tool.getCurrentTrackingList(
                     node=self.destination_vault.getRelativeUrl(),
                     at_date=self.date)), 2)
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(
                     node=self.destination_vault.getRelativeUrl(),
                     at_date=self.date)), 2)
    checkbook_list = self.simulation_tool.getCurrentTrackingList(
                             node=self.destination_vault.getRelativeUrl(),
                             at_date=self.date)
    self.assertEqual(len(checkbook_list), 2)
    # check we have cash checkbook 1
    checkbook_object_list = [x.getObject() for x in checkbook_list]
    self.failIfDifferentSet(checkbook_object_list, [self.checkbook_1, self.check_1])
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(
                node=self.destination_vault.getRelativeUrl(),
                at_date=self.date)), 2)

  def stepChangePreviousDeliveryDate(self,
               sequence=None, sequence_list=None, **kwd):
    """
    Reset a vault
    """
    self.previous_delivery = self.checkbook_vault_transfer
    self.previous_date = self.previous_delivery.getStartDate()
    self.previous_delivery.edit(start_date=self.date+5)

  def stepDeliverCheckbookUsualCashTransferFails(self, sequence=None, sequence_list=None, **kwd):
    """
    Try if we get Insufficient balance
    """
    message = self.assertWorkflowTransitionFails(self.checkbook_usual_cash_transfer,
              'checkbook_usual_cash_transfer_workflow', 'confirm_to_deliver_action')
    self.assertTrue(message.find('Sorry, the item with reference')>=0)
    self.assertTrue(message.find('is not available any more')>=0)

  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingCheckbookUsualCashTransfer(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialCheckbookInventory ' \
                    + 'CreateCheckbookUsualCashTransfer Tic ' \
                    + 'CreateCheckAndCheckbookLineList Tic ' \
                    + 'CheckConfirmCheckbookUsualCashTransferRaiseError Tic ' \
                    + 'ChangeCheckbookUsualCashTransferStartDate Tic ' \
                    + 'ConfirmCheckbookUsualCashTransfer Tic ' \
                    + 'CheckConfirmedCheckbookInventory Tic ' \
                    + 'ChangePreviousDeliveryDate Tic ' \
                    + 'DeliverCheckbookUsualCashTransferFails Tic ' \
                    + 'PutBackPreviousDeliveryDate Tic ' \
                    + 'DeliverCheckbookUsualCashTransfer Tic ' \
                    + 'CheckFinalCheckbookInventory'
    sequence_list.addSequenceString(sequence_string)
    # play the sequence
    sequence_list.play(self)

