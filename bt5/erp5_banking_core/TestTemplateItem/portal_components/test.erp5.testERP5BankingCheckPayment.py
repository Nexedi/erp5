
##############################################################################
#
# Copyright (c) 2005-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
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
from zLOG import LOG
from DateTime import DateTime
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from erp5.component.module.TestERP5BankingMixin import TestERP5BankingMixin

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

class TestERP5BankingCheckPaymentMixin(TestERP5BankingMixin):
  """
  Unit test class for the check payment module
  """

  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet


  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingCheckPayment"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    self.initDefaultVariable()
    # the check payment module
    self.check_payment_module = self.getCheckPaymentModule()
    # the checkbook module
    self.checkbook_module = self.getCheckbookModule()

    # Create a user and login as manager to populate the erp5 portal with objects for tests.
    self.createManagerAndLogin()

    # Define static values (only use prime numbers to prevent confusions like 2 * 6 == 3 * 4)
    # variation list is the list of years for banknotes and coins
    self.variation_list = ('variation/1992', 'variation/2003')

    self.createFunctionGroupSiteCategory(site_list=['paris'])

    # Before the test, we need to input the inventory
    inventory_dict_line_1 = {'id' : 'inventory_line_1',
                             'resource': self.billet_10000,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/p', 'cash_status/valid') + self.variation_list,
                             'quantity': self.quantity_10000}

    inventory_dict_line_2 = {'id' : 'inventory_line_2',
                             'resource': self.billet_200,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/p', 'cash_status/valid') + self.variation_list,
                             'quantity': self.quantity_200}

    inventory_dict_line_3 = {'id' : 'inventory_line_3',
                             'resource': self.billet_5000,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/p', 'cash_status/valid') + self.variation_list,
                             'quantity': self.quantity_5000}

    line_list = [inventory_dict_line_1, inventory_dict_line_2, inventory_dict_line_3]
    self.line_list = line_list
    self.bi_counter = self.paris.surface.banque_interne
    self.bi_counter_vault = self.paris.surface.banque_interne.guichet_1.encaisse_des_billets_et_monnaies.sortante
    self.createCashInventory(source=None, destination=self.bi_counter_vault, currency=self.currency_1,
                             line_list=line_list)
    self.tic()
    # create a person and a bank account
    self.person_1 = self.createPerson(id='person_1',
                                      first_name='toto',
                                      last_name='titi')
    self.bank_account_1 = self.createBankAccount(person=self.person_1,
                                                 account_id='bank_account_1',
                                                 currency=self.currency_1,
                                                 amount=30000,
                                                 overdraft_facility=1,
                                                 internal_bank_account_number="343434343434")

    # now we need to create a user as Manager to do the test
    # in order to have an assigment defined which is used to do transition
    # Create an Organisation that will be used for users assignment
    self.checkUserFolderType()
    self.organisation = self.organisation_module.newContent(id='baobab_org', portal_type='Organisation',
                          function='banking', group='baobab',  site='testsite/paris')
    # define the user
    user_dict = {
        'super_user' : [['Manager'], self.organisation, 'banking/comptable', 'baobab', 'testsite/paris/surface/banque_interne/guichet_1']
      }
    # call method to create this user
    self.createERP5Users(user_dict)
    self.logout()
    self.loginByUserName('super_user')

    # open counter date and counter
    self.openCounterDate(site=self.paris, force_check=1)
    self.openCounter(site=self.bi_counter_vault)

    self.createCheckAndCheckbookModel()
    # create a check
    self.checkbook_1 = self.createCheckbook(id= 'checkbook_1',
                                            vault=self.paris,
                                            bank_account=self.bank_account_1,
                                            min=50,
                                            max=100,
                                            )

    self.check_1 = self.createCheck(id='check_1',
                                    reference='0000050',
                                    resource_value=self.check_model,
                                    checkbook=self.checkbook_1,
                                    destination_value=self.paris)
    self.check_2 = self.createCheck(id='check_2',
                                    reference='0000051',
                                    resource_value=self.check_model,
                                    checkbook=self.checkbook_1,
                                    destination_value=self.paris)
    self.check_3 = self.createCheck(id='check_3',
                                    reference='0000052',
                                    resource_value=self.check_model,
                                    checkbook=self.checkbook_1,
                                    destination_value=self.paris)
    self.check_4 = self.createCheck(id='check_4',
                                    reference='0000053',
                                    resource_value=self.check_model,
                                    checkbook=self.checkbook_1,
                                    destination_value=self.paris)
    self.check_5 = self.createCheck(id='check_5',
                                    reference='0000054',
                                    resource_value=self.check_model,
                                    checkbook=self.checkbook_1,
                                    destination_value=self.paris)
    self.check_5 = self.createCheck(id='check_6',
                                    reference='0000056',
                                    resource_value=self.check_model,
                                    checkbook=self.checkbook_1,
                                    destination_value=self.paris)
    self.non_existant_check_reference = '0000055'

  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that Check Payment Module was created
    self.assertEqual(self.check_payment_module.getPortalType(), 'Check Payment Module')
    # check check payment module is empty
    self.assertEqual(len(self.check_payment_module.objectValues()), 0)


  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in encaisse_billets_et_monnaies
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200 in encaisse_billets_et_monnaies
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    # check we have 24 banknotes of 200 in encaisse_billets_et_monnaies
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 30000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 30000)

  def stepModifyCheckPayment(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    self.check_payment.edit(aggregate_free_text="0000051")


  def stepCreateCheckPayment(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a check payment document and check it
    """
    self.check_payment = self.check_payment_module.newContent(id = 'check_payment',
                                   portal_type = 'Check Payment',
                                   destination_payment_value = self.bank_account_1,
                                   # aggregate_value = self.check_1,
                                   resource_value = self.currency_1,
                                   aggregate_free_text = "0000050",
                                   description = "test",
                                   # source_value = self.bi_counter,
                                   start_date = DateTime().Date(),
                                   source_total_asset_price = 20000.0,
                                   unique_per_account=True)
    # call set source to go into the interaction workflow to update local roles
    self.check_payment._setSource(self.bi_counter.getRelativeUrl())
    self.assertNotEqual(self.check_payment, None)
    self.assertEqual(self.check_payment.getTotalPrice(fast=0), 0.0)
    self.assertEqual(self.check_payment.getDestinationPayment(), self.bank_account_1.getRelativeUrl())
    self.assertEqual(self.check_payment.getAggregateFreeText(), self.check_1.getReference())
    self.assertEqual(self.check_payment.getSourceTotalAssetPrice(), 20000.0)
    self.assertEqual(self.check_payment.getSource(), self.bi_counter.getRelativeUrl())
    # set source reference
    self.setDocumentSourceReference(self.check_payment)
    # check source reference
    self.assertNotEqual(self.check_payment.getSourceReference(), '')
    self.assertNotEqual(self.check_payment.getSourceReference(), None)
    # the initial state must be draft
    self.assertEqual(self.check_payment.getSimulationState(), 'draft')

    # source reference must be automatically generated
    self.check_payment.setSourceReference(self.check_payment.Baobab_getUniqueReference())
    self.assertNotEqual(self.check_payment.getSourceReference(), None)
    self.assertNotEqual(self.check_payment.getSourceReference(), '')

  def stepValidateAnotherCheckPaymentWorks(self, sequence=None, sequence_list=None, **kwd):
    """ Make sure we can validate another check payment """
    self.createAnotherCheckPayment(sequence=sequence, will_fail=0, number="0000051")

  def stepPayAnotherCheckPaymentFails(self, sequence=None, sequence_list=None, **kwd):
    """ Make sure we can validate another check payment """
    self.createAnotherCheckPayment(sequence=sequence,
                  check_pay_will_fail=1, number="0000056")

  def stepValidateAnotherCheckPaymentWorksAgain(self, sequence=None, sequence_list=None, **kwd):
    """ Make sure we can validate another check payment """
    self.createAnotherCheckPayment(sequence=sequence,
                                   will_fail=0, number="0000054")

  def stepValidateAnotherCheckPaymentFails(self, sequence=None, sequence_list=None, **kwd):
    """ Make sure that we can not validate another check payment """
    self.createAnotherCheckPayment(sequence=sequence, will_fail=1,
                                   pending_account=1, number="0000052")

  def stepValidateAnotherCheckPaymentFailsAgain(self, sequence=None, sequence_list=None, **kwd):
    """ Make sure that we can not validate another check payment """
    self.createAnotherCheckPayment(sequence=sequence, will_fail=1,
               insuffisient_balance=1, number="0000053")

  def createAnotherCheckPayment(self, will_fail=0, check_pay_will_fail=0, sequence=None,
                                number=None, pending_account=0,
                                insuffisient_balance=0, **kwd):
    new_payment = self.check_payment_module.newContent(portal_type = 'Check Payment',
                                         destination_payment_value = self.bank_account_1,
                                         resource_value = self.currency_1,
                                         aggregate_resource_value = self.check_model,
                                         aggregate_free_text = number,
                                         start_date = DateTime().Date(),
                                         source_total_asset_price = 20000.0)
    new_payment._setSource(self.bi_counter.getRelativeUrl())
    if will_fail and insuffisient_balance:
      message = self.assertWorkflowTransitionFails(new_payment,
                         'check_payment_workflow', 'plan_action')
      LOG('self.assertWorkflowTransitionFails message', 0, message)
      if insuffisient_balance:
        self.assertTrue(message.find('Bank account is not sufficient')>=0)
      # We will force it in order to test the next step
      new_payment.plan()
    else:
      self.workflow_tool.doActionFor(new_payment, 'plan_action',
                                     wf_id='check_payment_workflow')
    self.assertEqual(new_payment.getSimulationState(), 'planned')
    self.commit()
    if will_fail:
      message = self.assertWorkflowTransitionFails(new_payment,
                         'check_payment_workflow', 'confirm_action')
      LOG('self.assertWorkflowTransitionFails message', 0, message)
      if pending_account:
        self.assertTrue(message.find('There are operations pending for this account')>=0)
      if insuffisient_balance:
        self.assertTrue(message.find('Bank account is not sufficient')>=0)
      self.assertEqual(new_payment.getSimulationState(), 'planned')
      self.commit()
      self.workflow_tool.doActionFor(new_payment, 'reject_action',
                                     wf_id='check_payment_workflow')
      self.workflow_tool.doActionFor(new_payment, 'cancel_action',
                                     wf_id='check_payment_workflow')

    else:
      self.workflow_tool.doActionFor(
                        new_payment, 'confirm_action',
                        wf_id='check_payment_workflow')
      self.assertEqual(new_payment.getSimulationState(), 'confirmed')
      self.commit()
      if check_pay_will_fail:
        self.stepInputCashDetails(check_payment=new_payment)
        message = self.assertWorkflowTransitionFails(new_payment,
                           'check_payment_workflow', 'deliver_action')
        LOG('self.assertWorkflowTransitionFails message', 0, message)
        self.assertTrue(message.find('There are operations pending for this vault')>=0)
      self.workflow_tool.doActionFor(new_payment, 'reject_action',
                                     wf_id='check_payment_workflow')
      self.workflow_tool.doActionFor(new_payment, 'cancel_action',
                                     wf_id='check_payment_workflow')


  def stepCheckConsistency(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the consistency of the check payment

    FIXME: check if the transition fails when a category or property is invalid.
    """
    self.workflow_tool.doActionFor(self.check_payment, 'plan_action', wf_id='check_payment_workflow')
    self.assertNotEqual(self.check_payment.getAggregateValue(), None)
    self.assertEqual(self.check_payment.getSimulationState(), 'planned')

  def stepRejectCheckPayment(self, sequence=None, sequence_list=None, **kwd):
    """
    Reject the check payment
    """
    self.workflow_tool.doActionFor(self.check_payment, 'reject_action', wf_id='check_payment_workflow')
    self.assertNotEqual(self.check_payment.getAggregateValue(), None)
    self.assertEqual(self.check_payment.getSimulationState(), 'rejected')

  def stepAggregateToInnexistantCheck(self, sequence=None, sequence_list=None, **kwd):
    """
      Set the aggrate relation to direct to an innexistant object, thus
      requiring the test process to generate one.
    """
    self.check_payment.setAggregateFreeText(self.non_existant_check_reference)
    self.assertEqual(self.check_payment.getAggregateValue(), None)

  def stepTryCheckConsistencyWithoutAutomaticCheckCreation(self, sequence=None, sequence_list=None, **kwd):
    """
      Do not enable automatic check creation and verify that validation fails.
    """
    self.assertFalse(self.getPortal().Base_isAutomaticCheckCreationAllowed())
    self.assertEqual(self.check_payment.getAggregateValue(), None)
    self.assertNotEqual(self.check_payment.getSimulationState(), 'planned')

    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.check_payment, 'plan_action', wf_id='check_payment_workflow')

    self.assertEqual(self.check_payment.getAggregateValue(), None)
    self.assertNotEqual(self.check_payment.getSimulationState(), 'planned')

  def stepTryCheckConsistencyWithAutomaticCheckCreation(self, sequence=None, sequence_list=None, **kwd):
    """
      Enable automatic check creation and verify that validation succeeds.
    """
    check_creation_script = self.getPortal().Base_isAutomaticCheckCreationAllowed
    original_script_source = check_creation_script._body
    check_creation_script.ZPythonScript_edit(check_creation_script._params, 'return True')
    self.assertTrue(self.getPortal().Base_isAutomaticCheckCreationAllowed())
    self.assertEqual(self.check_payment.getAggregateValue(), None)
    self.assertNotEqual(self.check_payment.getSimulationState(), 'planned')

    self.workflow_tool.doActionFor(self.check_payment, 'plan_action', wf_id='check_payment_workflow')

    self.assertNotEqual(self.check_payment.getAggregateValue(), None)
    self.assertEqual(self.check_payment.getSimulationState(), 'planned')
    check_creation_script.ZPythonScript_edit(check_creation_script._params, original_script_source)

  def stepSendToCounter(self, sequence=None, sequence_list=None, **kwd):
    """
    Send the check payment to the counter

    FIXME: check if the transition fails when a category or property is invalid.
    """
    self.workflow_tool.doActionFor(self.check_payment, 'confirm_action', wf_id='check_payment_workflow')
    self.assertEqual(self.check_payment.getSimulationState(), 'confirmed')

    self.assertEqual(self.check_payment.getSourceTotalAssetPrice(),
                     - self.check_payment.getTotalPrice(fast=0, portal_type = 'Banking Operation Line'))

  def stepCheckConfirmedInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the inventoryinb state confirmed
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in encaisse_billets_et_monnaies
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200 in encaisse_billets_et_monnaies
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    # check we have 24 banknotes of 200 in encaisse_billets_et_monnaies
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    # check the inventory of the bank account, must be planned to be decrease by 20000
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 30000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 10000)


  def stepInputCashDetails(self, sequence=None, check_payment=None,
                           sequence_list=None, **kwd):
    """
    Input cash details
    """
    if check_payment is None:
      check_payment = self.check_payment
    self.addCashLineToDelivery(check_payment, 'line_1', 'Cash Delivery Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'),
            ('emission_letter/p', 'cash_status/valid') + self.variation_list[1:],
            {self.variation_list[1] : 1})
    self.assertEqual(check_payment.line_1.getPrice(), 10000)

    self.addCashLineToDelivery(check_payment, 'line_2', 'Cash Delivery Line', self.billet_5000,
            ('emission_letter', 'cash_status', 'variation'),
            ('emission_letter/p', 'cash_status/valid') + self.variation_list[1:],
            {self.variation_list[1] : 2})
    self.assertEqual(check_payment.line_2.getPrice(), 5000)

  def stepPay(self, sequence=None, sequence_list=None, **kwd):
    """
    Pay the check payment

    FIXME: check if the transition fails when a category or property is invalid.
    """
    self.assertEqual(self.check_payment.getSourceTotalAssetPrice(),
                     self.check_payment.getTotalPrice(fast=0, portal_type = ['Cash Delivery Line', 'Cash Delivery Cell']))
    self.workflow_tool.doActionFor(self.check_payment, 'deliver_action', wf_id='check_payment_workflow')
    self.assertEqual(self.check_payment.getSimulationState(), 'delivered')

  def stepCheckFinalInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in encaisse_billets_et_monnaies
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 4.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 4.0)
    # check we have 12 coin of 200 in encaisse_billets_et_monnaies
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    # check we have 24 banknotes of 200 in encaisse_billets_et_monnaies
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 22.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 22.0)
    # check the final inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 10000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 10000)

  def stepCleanup(self, sequence=None, sequence_list=None, **kwd):
    """
      Cleanup test remains
    """
    # Fetch all ids before deleting the objects, otherwise the iterator will
    # skip objects as the list dynamicaly shrinks.
    object_id_list = [x for x in self.check_payment_module.objectIds()]
    for id in object_id_list:
      self.check_payment_module.deleteContent(id)

  def stepResetInventory(self,
               sequence=None, sequence_list=None, **kwd):
    """
    Make sure we can not close the counter date
    when there is still some operations remaining
    """
    bi_counter_vault = self.bi_counter_vault
    line_list = self.line_list
    self.resetInventory(source=None, destination=bi_counter_vault, currency=self.currency_1,
                             line_list=line_list, extra_id='_reset_out')

  def stepPayCheckPaymentFails(self, sequence=None, sequence_list=None, **kwd):
    """
    Pay the check payment

    FIXME: check if the transition fails when a category or property is invalid.
    """
    message = self.assertWorkflowTransitionFails(self.check_payment,
              'check_payment_workflow', 'deliver_action')
    self.assertTrue(message.find('Insufficient balance')>=0)

  def stepCheckCheckIsDelivered(self, sequence=None, sequence_list=None, **kwd):
    """
    Make sure that the check is in delivered state
    """
    check = self.check_payment.getAggregateValue()
    self.assertEqual(check, self.check_1)
    self.assertEqual(check.getSimulationState(), 'delivered')

  def stepCheckUndeliverCheck(self, sequence=None, sequence_list=None, **kwd):
    """
    Make sure that the check is in delivered state
    """
    check = self.check_payment.getAggregateValue()
    self.assertEqual(check, self.check_1)
    self.workflow_tool.doActionFor(check, 'undeliver_action',
        wf_id='check_workflow')
    self.assertEqual(check.getSimulationState(), 'confirmed')

  def stepCheckCheckAfterReject(self, sequence=None, sequence_list=None, **kwd):
    """
    Make sure that the check is in delivered state
    """
    check = self.check_payment.getAggregateValue()
    self.assertEqual(check, self.check_2)
    self.assertEqual(check.getSimulationState(), 'delivered')
    self.assertEqual(self.check_1.getSimulationState(), 'confirmed')

class TestERP5BankingCheckPayment(TestERP5BankingCheckPaymentMixin):

  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet

  def test_01_ERP5BankingCheckPayment(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialInventory ' \
                      'CreateCheckPayment Tic ' \
                      'CheckConsistency Tic ' \
                      'stepValidateAnotherCheckPaymentWorks Tic ' \
                      'SendToCounter ' \
                      'stepValidateAnotherCheckPaymentFails Tic ' \
                      'CheckConfirmedInventory ' \
                      'stepValidateAnotherCheckPaymentFailsAgain Tic ' \
                      'InputCashDetails Tic ' \
                      'ResetInventory Tic ' \
                      'PayCheckPaymentFails Tic ' \
                      'DeleteResetInventory Tic ' \
                      'Pay Tic ' \
                      'CheckCheckIsDelivered Tic ' \
                      'CheckUndeliverCheck Tic ' \
                      'CheckFinalInventory Cleanup Tic'
    # sequence 2 : check if validating with non-exiting check fail if
    # automatic check creation is disabled.
    sequence_string_2 = 'Tic CheckObjects Tic CheckInitialInventory ' \
                        'CreateCheckPayment Tic ' \
                        'AggregateToInnexistantCheck Tic ' \
                        'TryCheckConsistencyWithoutAutomaticCheckCreation Tic ' \
                        'Cleanup Tic'
    # sequence 3 : check is validating with non-existing check succeeds if
    # automatic check creation is enabled.
    sequence_string_3 = 'Tic CheckObjects Tic CheckInitialInventory ' \
                        'CreateCheckPayment Tic ' \
                        'AggregateToInnexistantCheck Tic ' \
                        'TryCheckConsistencyWithAutomaticCheckCreation Tic ' \
                        'Cleanup Tic'

    # sequence 4 : reject document and change check number
    sequence_string_4 = 'Tic CheckObjects Tic CheckInitialInventory ' \
                      'CreateCheckPayment Tic ' \
                      'CheckConsistency Tic ' \
                      'SendToCounter Tic ' \
                      'RejectCheckPayment Tic ' \
                      'ModifyCheckPayment Tic ' \
                      'CheckConsistency Tic ' \
                      'SendToCounter Tic ' \
                      'CheckConfirmedInventory ' \
                      'InputCashDetails Tic ' \
                      'Pay Tic ' \
                      'CheckCheckAfterReject ' \
                      'CheckFinalInventory Cleanup Tic'

    sequence_list.addSequenceString(sequence_string)
    sequence_list.addSequenceString(sequence_string_2)
    sequence_list.addSequenceString(sequence_string_3)
    sequence_list.addSequenceString(sequence_string_4)
    # play the sequence
    sequence_list.play(self)

