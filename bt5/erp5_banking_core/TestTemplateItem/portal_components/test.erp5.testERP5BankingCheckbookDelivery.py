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
from erp5.component.test.testERP5BankingCheckbookUsualCashTransfer \
     import TestERP5BankingCheckbookUsualCashTransferMixin
from erp5.component.module.TestERP5BankingMixin import TestERP5BankingMixin

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

class TestERP5BankingCheckbookDeliveryMixin(TestERP5BankingMixin):

  def createCheckbookDelivery(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a checkbook delivery
    """
    # We will do the transfer ot two items.
    self.checkbook_delivery = self.checkbook_delivery_module.newContent(
                     id='checkbook_delivery', portal_type='Checkbook Delivery',
                     source_value=self.source_site, destination_value=None,
                     resource_value=self.currency_1,
                     destination_payment_value=self.bank_account_2,
                     start_date=self.date)
    self.line_2 = self.checkbook_delivery.newContent(quantity=1,
                                 resource_value=self.check_model_1,
                                 check_amount_value=None,
                                 destination_trade_value=self.bank_account_2,
                                 aggregate_value=self.check_1,
                                 )
    self.workflow_tool.doActionFor(self.checkbook_delivery, 'deliver_action',
                                   wf_id='checkbook_delivery_workflow')

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    # Set some variables :
    self.initDefaultVariable()
    # the cash inventory module
    self.checkbook_delivery_module = self.getCheckbookDeliveryModule()
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
    self.logout()
    self.loginByUserName('super_user')
    # open counter date and counter
    self.openCounterDate(site=self.paris)
    # this is required in order to have some items
    # in the source
    self.createCheckbookReception()
    self.checkItemsCreated()
    self.tic()
    self.createCheckbookVaultTransfer()


class TestERP5BankingCheckbookDelivery(TestERP5BankingCheckbookDeliveryMixin,
                                       TestERP5BankingCheckbookUsualCashTransferMixin):
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
    return "ERP5BankingCheckbookDelivery"

  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that CheckbookDelivery Module was created
    self.assertEqual(self.checkbook_delivery_module.getPortalType(), 'Checkbook Delivery Module')
    # check cash inventory module is empty
    self.assertEqual(len(self.checkbook_delivery_module.objectValues()), 0)


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
    checkbook_list = self.simulation_tool.getCurrentTrackingList(
                             node=self.source_vault.getRelativeUrl(),
                             at_date=self.date)
    self.assertEqual(len(checkbook_list), 2)
    # check we have cash checkbook 1
    checkbook_object_list = [x.getObject() for x in checkbook_list]
    self.failIfDifferentSet(checkbook_object_list, [self.check_1, self.checkbook_1])

  def stepCreateCheckbookDelivery(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a checkbook delivery
    """
    # We will do the transfer ot two items.
    self.checkbook_delivery = self.checkbook_delivery_module.newContent(
                     id='checkbook_delivery', portal_type='Checkbook Delivery',
                     source_value=self.source_site, destination_value=None,
                     destination_payment_value=self.bank_account_2,
                     resource_value=self.currency_1,
                     start_date=self.date)
    # check its portal type
    self.assertEqual(self.checkbook_delivery.getPortalType(), 'Checkbook Delivery')
    # check source
    self.assertEqual(self.checkbook_delivery.getBaobabSource(),
               'site/testsite/paris/surface/caisse_courante/encaisse_des_billets_et_monnaies')
    # check destination
    self.assertEqual(self.checkbook_delivery.getBaobabDestination(), None)


  def stepCreateCheckAndCheckbookLineList(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the checkbook
    """
    # This is not required to create checkbook items, they will be
    # automatically created with the confirm action worfklow transition

    # Add a line for check and checkbook
    self.line_1 = self.checkbook_delivery.newContent(quantity=1,
                                 resource_value=self.checkbook_model_1,
                                 check_amount_value=self.checkbook_model.variant_1,
                                 reference_range_min=1,
                                 description='test',
                                 reference_range_max=50,
                                 aggregate_value=self.checkbook_1
                                 )


  def stepDeliverCheckbookDelivery(self, sequence=None, sequence_list=None, **kw):
    """
    Deliver the checkbook delivery
    """
    state = self.checkbook_delivery.getSimulationState()
    # check that state is draft
    self.assertEqual(state, 'empty')
    self.workflow_tool.doActionFor(self.checkbook_delivery,
                                   'deliver_action',
                                   wf_id='checkbook_delivery_workflow')
    # get state of cash sorting
    state = self.checkbook_delivery.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # check that checks are issued
    check = self.checkbook_1.objectValues()[0]
    self.assertEqual(check.getSimulationState(), 'confirmed')


  def stepCheckFinalCheckbookInventory(self, sequence=None, sequence_list=None, **kw):
    """
    Check cash checkbook in item table
    """
    self.assertEqual(len(self.simulation_tool.getCurrentTrackingList(
                     node=self.source_vault.getRelativeUrl(),
                     at_date=self.date)), 1)
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(
                     node=self.source_vault.getRelativeUrl(),
                     at_date=self.date)), 1)
    checkbook_list = self.simulation_tool.getCurrentTrackingList(
                             node=self.source_vault.getRelativeUrl(),
                             at_date=self.date)
    self.assertEqual(len(checkbook_list), 1)
    # check we have cash checkbook 1
    checkbook_object_list = [x.getObject() for x in checkbook_list]
    self.failIfDifferentSet(checkbook_object_list, [self.check_1])

  def stepChangePreviousDeliveryDate(self,
               sequence=None, sequence_list=None, **kwd):
    """
    Reset a vault
    """
    self.previous_delivery = self.checkbook_vault_transfer
    self.previous_date = self.previous_delivery.getStartDate()
    self.previous_delivery.edit(start_date=self.date+5)

  def stepDeliverCheckbookDeliveryFails(self, sequence=None, sequence_list=None, **kwd):
    """
    Try if we get Insufficient balance
    """
    message = self.assertWorkflowTransitionFails(self.checkbook_delivery,
              'checkbook_delivery_workflow', 'deliver_action')
    self.assertTrue(message.find('Sorry, the item with reference')>=0)
    self.assertTrue(message.find('is not available any more')>=0)

  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingCheckbookDelivery(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialCheckbookInventory ' \
                    + 'CreateCheckbookDelivery Tic ' \
                    + 'CreateCheckAndCheckbookLineList Tic ' \
                    + 'ChangePreviousDeliveryDate Tic ' \
                    + 'DeliverCheckbookDeliveryFails Tic ' \
                    + 'PutBackPreviousDeliveryDate Tic ' \
                    + 'DeliverCheckbookDelivery Tic ' \
                    + 'CheckFinalCheckbookInventory'
    sequence_list.addSequenceString(sequence_string)
    # play the sequence
    sequence_list.play(self)

