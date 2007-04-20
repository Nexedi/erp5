##############################################################################
#
# Copyright (c) 2005-2006 Nexedi SARL and Contributors. All Rights Reserved.
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
from Products.CMFCore.utils import getToolByName
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


class TestERP5BankingCurrencySale(TestERP5BankingMixin, ERP5TypeTestCase):
  """
  Unit test class for the check payment module
  """

  login = PortalTestCase.login

  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet


  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingCurrencySale"

  def getCurrencySaleModule(self):
    """
    Return the Currency Sale Module
    """
    return getattr(self.getPortal(), 'currency_sale_module', None)

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    self.initDefaultVariable()
    # the check payment module
    self.currency_sale_module = self.getCurrencySaleModule()


    # Create a user and login as manager to populate the erp5 portal with objects for tests.
    self.createManagerAndLogin()

    # Define static values (only use prime numbers to prevent confusions like 2 * 6 == 3 * 4)
    # variation list is the list of years for banknotes and coins
    self.variation_list = ('variation/1992', 'variation/2003')

    self.createFunctionGroupSiteCategory(site_list=['paris',])
    self.createBanknotesAndCoins()

    # Before the test, we need to input the inventory
    inventory_dict_line_1 = {'id' : 'inventory_line_1',
                             'resource': self.usd_billet_20,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/not_defined', 'cash_status/not_defined') + self.usd_variation_list,
                             'variation_list': self.usd_variation_list,
                             'quantity': self.quantity_usd_20}



    self.line_list = line_list = [inventory_dict_line_1]
    self.bi_counter = self.paris.surface.banque_interne
    self.bi_counter_vault = self.paris.surface.banque_interne.guichet_1.encaisse_des_devises.usd.sortante
    self.createCashInventory(source=None, destination=self.bi_counter_vault, currency=self.currency_2,
                             line_list=line_list)
    self.stepTic()
    # create a person and a bank account
    self.person_1 = self.createPerson(id='person_1',
                                      first_name='toto',
                                      last_name='titi')
    self.bank_account_1 = self.createBankAccount(person=self.person_1,
                                                 account_id='bank_account_1',
                                                 currency=self.currency_1,
                                                 amount=100000,
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
    self.login('super_user')
    # open counter date and counter
    self.openCounterDate(site=self.paris)
    self.openCounter(site=self.bi_counter_vault)


  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that Currency Sale Module was created
    self.assertEqual(self.currency_sale_module.getPortalType(), 'Currency Sale Module')
    # check check payment module is empty
    self.assertEqual(len(self.currency_sale_module.objectValues()), 0)


  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in encaisse_billets_et_monnaies
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 5.0)

        # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 100000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 100000)



  def stepCreateCurrencySale(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a check payment document and check it
    """
    self.currency_sale = self.currency_sale_module.newContent(id = 'currency_sale', portal_type = 'Currency Sale',
                                         price_currency='currency_module/EUR',currency_exchange_type='sale',
                                         destination_payment_value = self.bank_account_1,
                                         resource_value = self.currency_2,
                                         description='test',
                                         start_date = DateTime().Date(),
                                         source_total_asset_price = 100.0,
                                         discount = 3000.0,
                                         quantity = 68000.0)
    # call set source to go into the interaction workflow to update local roles
    self.currency_sale._setSource(self.bi_counter.getRelativeUrl())
    self.assertNotEqual(self.currency_sale, None)
    self.assertEqual(self.currency_sale.getTotalPrice(), 0.0)
    self.assertEqual(self.currency_sale.getDestinationPayment(), self.bank_account_1.getRelativeUrl())

    self.assertEqual(self.currency_sale.getSourceTotalAssetPrice(), 100.0)
    self.assertEqual(self.currency_sale.getSource(), self.bi_counter.getRelativeUrl())
    self.currency_sale.setPrice(self.currency_sale.ERP5Banking_getExchangeValue())
    self.currency_sale.setQuantity(self.currency_sale.CurrencySale_getQuantity())

    # the initial state must be draft
    self.assertEqual(self.currency_sale.getSimulationState(), 'draft')
    #self.assertEqual(self.currency_sale.getDestinationPaymentValue(), self.bank_account_1)
    # source reference must be automatically generated
    self.currency_sale.setSourceReference(self.currency_sale.Baobab_getUniqueReference())
    self.assertNotEqual(self.currency_sale.getSourceReference(), None)
    self.assertNotEqual(self.currency_sale.getSourceReference(), '')


  def stepCheckConsistency(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the consistency of the check payment

    FIXME: check if the transition fails when a category or property is invalid.
    """

    self.assertEqual(self.currency_sale.getDestinationPaymentValue(), self.bank_account_1)
    self.workflow_tool.doActionFor(self.currency_sale, 'plan_action', wf_id='currency_sale_workflow')
    #self.assertNotEqual(self.currency_sale.getAggregateValue(), None)
    self.assertEqual(self.currency_sale.getSimulationState(), 'planned')


  def stepSendToCounter(self, sequence=None, sequence_list=None, **kwd):
    """
    Send the check payment to the counter

    FIXME: check if the transition fails when a category or property is invalid.
    """
    self.workflow_tool.doActionFor(self.currency_sale, 'confirm_action', wf_id='currency_sale_workflow')
    self.assertEqual(self.currency_sale.getSimulationState(), 'confirmed')

    #self.assertEqual(self.currency_sale.getSourceTotalAssetPrice(),
    #                 - self.currency_sale.getTotalPrice(portal_type = 'Banking Operation Line'))

  def stepCheckConfirmedInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the inventoryinb state confirmed
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in encaisse_billets_et_monnaies
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 5.0)

    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl(), resource=self.currency_1.getRelativeUrl()), 32000)


  def stepInputCashDetails(self, sequence=None, sequence_list=None, **kwd):
    """
    Input cash details
    """
    self.addCashLineToDelivery(self.currency_sale, 'line_1', 'Cash Delivery Line', self.usd_billet_20,
            ('emission_letter', 'cash_status', 'variation'),
            ('emission_letter/not_defined', 'cash_status/not_defined') + self.usd_variation_list,
            self.quantity_usd_20,
            variation_list = self.usd_variation_list)
    #self.assertEqual(self.currency_sale.line_1.getPrice(), 10000)



  def stepPay(self, sequence=None, sequence_list=None, **kwd):
    """
    Pay the check payment

    FIXME: check if the transition fails when a category or property is invalid.
    """
    self.assertEqual(self.currency_sale.getSourceTotalAssetPrice(),
                     self.currency_sale.getTotalPrice(portal_type = 'Cash Delivery Cell'))
    self.workflow_tool.doActionFor(self.currency_sale, 'deliver_action', wf_id='currency_sale_workflow')
    self.assertEqual(self.currency_sale.getSimulationState(), 'delivered')


  def stepCheckFinalInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in encaisse_billets_et_monnaies
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 0.0)

    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl(), resource=self.currency_1.getRelativeUrl()), 32000)

  def stepResetSourceInventory(self, 
               sequence=None, sequence_list=None, **kwd):
    """
    Reset a vault
    """
    node = self.bi_counter_vault
    line_list = self.line_list
    self.resetInventory(destination=node, currency=self.currency_1,
                        line_list=line_list,extra_id='_reset_out')

  def stepPayFails(self, sequence=None, sequence_list=None, **kwd):
    """
    Try if we get Insufficient balance
    """
    message = self.assertWorkflowTransitionFails(self.currency_sale,
              'currency_sale_workflow','deliver_action')
    self.failUnless(message.find('Insufficient balance')>=0)

  def test_01_ERP5BankingCurrencySale(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run: return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialInventory ' \
                      'CreateCurrencySale Tic ' \
                      'CheckConsistency Tic ' \
                      'SendToCounter Tic ' \
                      'CheckConfirmedInventory ' \
                      'InputCashDetails Tic ' \
                      'ResetSourceInventory Tic ' \
                      'PayFails DeleteResetInventory Tic ' \
                      'Pay Tic ' \
                      'CheckFinalInventory '
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
    suite.addTest(unittest.makeSuite(TestERP5BankingCurrencySale))
    return suite
