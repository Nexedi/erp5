
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
from erp5.component.module.TestERP5BankingMixin import TestERP5BankingMixin

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

class TestERP5BankingCheckbookVaultTransferMixin(TestERP5BankingMixin):

  def createCheckbookReception(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a checkbook Reception
    We do not need to check it because it is already done in another unit test.
    """
    self.checkbook_reception = self.checkbook_reception_module.newContent(
                     id='checkbook_reception', portal_type='Checkbook Reception',
                     source_value=None, destination_value=self.reception_destination_site,
                     description='test',
                     start_date=(self.date-4))
    # get the checkbook reception document
    self.checkbook_reception = getattr(self.checkbook_reception_module, 'checkbook_reception')
    # Add a line for check and checkbook
    self.line_1 = self.checkbook_reception.newContent(quantity=1,
                                 resource_value=self.checkbook_model_1,
                                 check_amount_value=self.checkbook_model_1.variant_1,
                                 destination_payment_value=self.bank_account_1,
                                 reference_range_min='0000001',
                                 reference_range_max='0000050',
                                 )
    self.line_2 = self.checkbook_reception.newContent(quantity=1,
                                 resource_value=self.check_model_1,
                                 check_amount_value=None,
                                 destination_payment_value=self.bank_account_2,
                                 reference_range_min='0000051',
                                 reference_range_max='0000051',
                                 )
    self.workflow_tool.doActionFor(self.checkbook_reception, 'confirm_action',
                                   wf_id='checkbook_reception_workflow')
    self.workflow_tool.doActionFor(self.checkbook_reception, 'deliver_action',
                                   wf_id='checkbook_reception_workflow')
    self.tic()

  def createCheckbookReceptionWithTravelerCheck(self, sequence=None,
                                  sequence_list=None, **kwd):
    """
    Create a checkbook Reception
    We do not need to check it because it is already done in another unit test.
    """
    self.checkbook_reception = self.checkbook_reception_module.newContent(
                     id='checkbook_reception', portal_type='Checkbook Reception',
                     source_value=None, destination_value=self.reception_destination_site,
                     destination_payment_value=self.bank_account_1,
                     description='test',
                     start_date=(self.date-4))
    # get the checkbook reception document
    self.checkbook_reception = getattr(self.checkbook_reception_module, 'checkbook_reception')
    # Add a line for check and checkbook
    self.line_2 = self.checkbook_reception.newContent(quantity=1,
                             resource_value=self.traveler_check_model,
                             check_type_value=self.traveler_check_model.variant_1,
                             reference_range_min="abcd123456",
                             reference_range_max="abcd123456",
                             price_currency_value=self.currency_2
                             )
    self.workflow_tool.doActionFor(self.checkbook_reception, 'confirm_action',
                                   wf_id='checkbook_reception_workflow')
    self.workflow_tool.doActionFor(self.checkbook_reception, 'deliver_action',
                                   wf_id='checkbook_reception_workflow')

  def checkItemsCreatedWithTravelerCheck(self, sequence=None,
                                         sequence_list=None, **kwd):
    self.checkItemsCreated(sequence=sequence,
                           sequence_list=sequence_list,
                           traveler_check=1, **kwd)

  def checkItemsCreated(self, sequence=None, sequence_list=None,
                        traveler_check=0, **kwd):
    """
    Create the checkbook
    """
    self.checkbook_1 = None
    self.check_1 = None
    self.traveler_check = None

    for line in self.checkbook_reception.objectValues():
      aggregate_value_list = line.getAggregateValueList()
      self.assertEqual(len(aggregate_value_list), 1)
      aggregate_value = aggregate_value_list[0]
      if aggregate_value.getPortalType()=='Checkbook':
        self.checkbook_1 = aggregate_value
      elif aggregate_value.getPortalType()=='Check':
        if aggregate_value.getResourceValue().isFixedPrice():
          self.traveler_check = aggregate_value
        else:
          self.check_1 = aggregate_value
    if not traveler_check:
      self.assertNotEquals(None, self.checkbook_1)
      self.assertNotEquals(None, self.check_1)
    else:
      self.assertNotEquals(traveler_check, None)

  def stepPutBackPreviousDeliveryDate(self,
               sequence=None, sequence_list=None, **kwd):
    """
    Put back right inventory
    """
    self.previous_delivery.edit(start_date=self.previous_date)

class TestERP5BankingCheckbookVaultTransfer(TestERP5BankingCheckbookVaultTransferMixin):
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
    return "ERP5BankingCheckbookVaultTransfer"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    # Set some variables :
    self.initDefaultVariable()
    # the cash inventory module
    self.checkbook_vault_transfer_module = self.getCheckbookVaultTransferModule()
    self.checkbook_reception_module = self.getCheckbookReceptionModule()
    self.check_module = self.getCheckModule()
    self.checkbook_module = self.getCheckbookModule()
    self.checkbook_model_module = self.getCheckbookModelModule()

    self.createManagerAndLogin()
    self.createFunctionGroupSiteCategory()
    self.createCheckAndCheckbookModel()
    self.destination_site = self.paris
    self.reception_destination_site = self.paris
    self.source_site = self.paris.caveau
    self.destination_site = self.paris.surface
    self.source_vault = self.paris.caveau.auxiliaire.encaisse_des_billets_et_monnaies
    self.destination_vault = self.paris.surface.caisse_courante.encaisse_des_billets_et_monnaies
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


  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that CheckbookVaultTransfer Module was created
    self.assertEqual(self.checkbook_vault_transfer_module.getPortalType(), 'Checkbook Vault Transfer Module')
    # check cash inventory module is empty
    self.assertEqual(len(self.checkbook_vault_transfer_module.objectValues()), 0)


  def stepCheckInitialCheckbookInventory(self, sequence=None, sequence_list=None, **kw):
    """
    Check initial cash checkbook on source
    """
    self.assertEqual(len(self.simulation_tool.getCurrentTrackingList(
                             node=self.destination_vault.getRelativeUrl())), 0)
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(
                             node=self.destination_vault.getRelativeUrl())), 0)


  def stepCreateCheckbookVaultTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a checkbook vault transfer
    """
    # We will do the transfer ot two items.
    self.checkbook_vault_transfer = self.checkbook_vault_transfer_module.newContent(
                     id='checkbook_vault_transfer', portal_type='Checkbook Vault Transfer',
                     source_value=self.source_site, destination_value=self.destination_site,
                     description='test',
                     start_date=self.date,
                     resource_value=self.currency_1)
    # check its portal type
    self.assertEqual(self.checkbook_vault_transfer.getPortalType(), 'Checkbook Vault Transfer')
    # check source
    self.assertEqual(self.checkbook_vault_transfer.getBaobabSource(),
               'site/testsite/paris/caveau/auxiliaire/encaisse_des_billets_et_monnaies')
    # check destination
    self.assertEqual(self.checkbook_vault_transfer.getBaobabDestination(),
               'site/testsite/paris/surface/caisse_courante/encaisse_des_billets_et_monnaies')


  def stepCreateCheckAndCheckbookLineList(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the checkbook
    """
    # This is not required to create checkbook items, they will be
    # automatically created with the confirm action worfklow transition

    # Add a line for check and checkbook
    self.line_1 = self.checkbook_vault_transfer.newContent(quantity=1,
                                 resource_value=self.checkbook_model_1,
                                 check_amount_value=self.checkbook_model_1.variant_1,
                                 reference_range_min='0000001',
                                 reference_range_max='0000050',
                                 aggregate_value=self.checkbook_1
                                 )
    self.line_2 = self.checkbook_vault_transfer.newContent(quantity=1,
                                 resource_value=self.check_model_1,
                                 check_amount_value=None,
                                 reference_range_min='0000051',
                                 reference_range_max='0000051',
                                 aggregate_value=self.check_1
                                 )


  def stepOrderCheckbookVaultTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    order the checkbook vault transfer
    """
    state = self.checkbook_vault_transfer.getSimulationState()
    self.assertEqual(state, 'draft')
    self.workflow_tool.doActionFor(self.checkbook_vault_transfer,
               'order_action', wf_id='checkbook_vault_transfer_workflow')
    self.assertEqual(self.checkbook_vault_transfer.getSimulationState(), 'ordered')

  def stepConfirmCheckbookVaultTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    confirm the checkbook vault transfer
    """
    state = self.checkbook_vault_transfer.getSimulationState()
    self.assertEqual(state, 'ordered')
    self.workflow_tool.doActionFor(self.checkbook_vault_transfer, 'confirm_action', wf_id='checkbook_vault_transfer_workflow')
    self.assertEqual(self.checkbook_vault_transfer.getSimulationState(), 'confirmed')


  def stepCheckConfirmedCheckbookInventory(self, sequence=None, sequence_list=None, **kw):
    """
    Check cash checkbook in item table
    """
    self.assertEqual(len(self.simulation_tool.getCurrentTrackingList(
                     node=self.destination_vault.getRelativeUrl())), 0)
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(
                     node=self.destination_vault.getRelativeUrl())), 2)


  def stepDeliverCheckbookVaultTransfer(self, sequence=None, sequence_list=None, **kw):
    """
    Deliver the checkbook vault transfer
    """
    state = self.checkbook_vault_transfer.getSimulationState()
    # check that state is draft
    self.assertEqual(state, 'confirmed')
    self.workflow_tool.doActionFor(self.checkbook_vault_transfer,
                                   'deliver_action',
                                   wf_id='checkbook_vault_transfer_workflow')
    state = self.checkbook_vault_transfer.getSimulationState()
    self.assertEqual(state, 'delivered')


  def stepCheckFinalCheckbookInventory(self, sequence=None, sequence_list=None, **kw):
    """
    Check cash checkbook in item table
    """
    checkbook_list = self.simulation_tool.getCurrentTrackingList(
                node=self.destination_vault.getRelativeUrl())
    self.assertEqual(len(checkbook_list), 2)
    # check we have cash checkbook 1
    checkbook_object_list = [x.getObject() for x in checkbook_list]
    self.failIfDifferentSet(checkbook_object_list, [self.checkbook_1, self.check_1])
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(
                node=self.destination_vault.getRelativeUrl())), 2)

  def stepChangePreviousDeliveryDate(self,
               sequence=None, sequence_list=None, **kwd):
    """
    Reset a vault
    """
    self.previous_delivery = self.checkbook_reception
    self.previous_date = self.previous_delivery.getStartDate()
    self.previous_delivery.edit(start_date=self.date+5)

  def stepDeliverCheckbookVaultTransferFails(self, sequence=None, sequence_list=None, **kwd):
    """
    Try if we get Insufficient balance
    """
    message = self.assertWorkflowTransitionFails(self.checkbook_vault_transfer,
              'checkbook_vault_transfer_workflow', 'deliver_action')
    self.assertTrue(message.find('Sorry, the item with reference')>=0)
    self.assertTrue(message.find('is not available any more')>=0)

  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingCheckbookVaultTransfer(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialCheckbookInventory ' \
                    + 'CreateCheckbookVaultTransfer Tic ' \
                    + 'CreateCheckAndCheckbookLineList Tic ' \
                    + 'OrderCheckbookVaultTransfer Tic ' \
                    + 'ConfirmCheckbookVaultTransfer Tic ' \
                    + 'CheckConfirmedCheckbookInventory Tic ' \
                    + 'ChangePreviousDeliveryDate Tic ' \
                    + 'DeliverCheckbookVaultTransferFails Tic ' \
                    + 'PutBackPreviousDeliveryDate Tic ' \
                    + 'DeliverCheckbookVaultTransfer Tic ' \
                    + 'CheckFinalCheckbookInventory'
    sequence_list.addSequenceString(sequence_string)
    # play the sequence
    sequence_list.play(self)

