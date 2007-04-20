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


class TestERP5BankingCurrencyPurchase(TestERP5BankingMixin, ERP5TypeTestCase):
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
    return "ERP5BankingCurrencyPurchase"


  def getCurrencyPurchaseModule(self):
    """
    Return the Currency purchase Module
    """
    return getattr(self.getPortal(), 'currency_purchase_module', None)

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    self.initDefaultVariable()
    # the check payment module
    self.currency_purchase_module = self.getCurrencyPurchaseModule()


    # Create a user and login as manager to populate the erp5 portal with objects for tests.
    self.createManagerAndLogin()

    # variation list is the list of years for banknotes and coins
    self.variation_list = ('variation/1992', 'variation/2003')

    self.createFunctionGroupSiteCategory(site_list=['paris',])
    self.createBanknotesAndCoins()

    self.bi_counter = self.paris.surface.banque_interne
    self.counter_site = self.paris.surface.banque_interne.guichet_1
    self.bi_counter_vault = self.paris.surface.banque_interne.guichet_1.encaisse_des_devises.usd.entrante
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
    self.openCounter(site=self.counter_site)


  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that Currency Purchase Module was created
    self.assertEqual(self.currency_purchase_module.getPortalType(), 'Currency Purchase Module')
    # check check payment module is empty
    self.assertEqual(len(self.currency_purchase_module.objectValues()), 0)


  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):

    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 0 banknotes of 10000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 0.0)
     # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 100000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 100000)

  def stepCreateCurrencyPurchase(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a check payment document and check it
    """

    self.currency_purchase = self.currency_purchase_module.newContent(id = 'currency_purchase', portal_type = 'Currency Purchase',
                                         price_currency='currency_module/EUR',currency_exchange_type='purchase',
                                         destination_payment_value = self.bank_account_1,
                                         resource_value = self.currency_2,
                                         description='test',
                                         start_date = DateTime().Date(),
                                         source_total_asset_price = 100.0,
                                         discount = 1000.0)
    #self.currency_purchase.setPriceCurrency('currency_module/EUR')
    #self.assertEqual(self.currency_purchase.getPriceCurrency(), 'currency_module/EUR')
    # call set source to go into the interaction workflow to update local roles
    self.currency_purchase._setSource(self.bi_counter.getRelativeUrl())
    self.assertNotEqual(self.currency_purchase, None)
    self.assertEqual(self.currency_purchase.getTotalPrice(), 0.0)
    self.assertEqual(self.currency_purchase.getDestinationPayment(), self.bank_account_1.getRelativeUrl())
    self.assertEqual(self.currency_purchase.getSourceTotalAssetPrice(), 100.0)
    self.assertEqual(self.currency_purchase.getSource(), self.bi_counter.getRelativeUrl())
    self.currency_purchase.setPrice(self.currency_purchase.ERP5Banking_getExchangeValue())
    self.currency_purchase.setQuantity(self.currency_purchase.CurrencyPurchase_getQuantity()
    )

    # the initial state must be draft
    self.assertEqual(self.currency_purchase.getSimulationState(), 'draft')

    # source reference must be automatically generated
    self.currency_purchase.setSourceReference(self.currency_purchase.Baobab_getUniqueReference())
    self.assertNotEqual(self.currency_purchase.getSourceReference(), None)
    self.assertNotEqual(self.currency_purchase.getSourceReference(), '')

    self.assertEqual(self.currency_purchase.getPrice(), 65000)
    self.assertEqual(self.currency_purchase.getQuantity(), 64000)



 #def stepCreateValidIncomingLine(self, sequence=None, sequence_list=None, **kwd):
  def stepCreateValidIncomingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash exchange incoming line  with banknotes of 10000 and check it has been well created
    """
    # create the cash exchange line
    self.addCashLineToDelivery(self.currency_purchase, 'valid_incoming_line_1', 'Cash Delivery Line', self.usd_billet_20,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/not_defined') + self.usd_variation_list,
            self.quantity_usd_20,
            variation_list = self.usd_variation_list)
    # execute tic
    self.stepTic()
    # check there is only one line created
    self.assertEqual(len(self.currency_purchase.objectValues()), 2)
    # get the cash exchange line
    self.valid_incoming_line = getattr(self.currency_purchase, 'valid_incoming_line_1')
    # check its portal type
    self.assertEqual(self.valid_incoming_line.getPortalType(), 'Cash Delivery Line')
    # check the resource is banknotes of 20
    self.assertEqual(self.valid_incoming_line.getResourceValue(), self.usd_billet_20)
    # chek the value of the banknote
    self.assertEqual(self.valid_incoming_line.getPrice(), 20.0)
    # check the unit of banknote
    self.assertEqual(self.valid_incoming_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_incoming_line.objectValues()), 1)
    # now check for each variation (years 1992 and 2003)
    for variation in self.usd_variation_list:
      # get the delivery cell
      cell = self.valid_incoming_line.getCell('emission_letter/not_defined', variation, 'cash_status/not_defined')
      # chek portal types
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.usd_billet_20)
      # check the source vault is encaisse_paris
      self.assertEqual(cell.getBaobabSource(), None)
      # check the destination vault is guichet_1
      #self.assertEqual(cell.getBaobabDestination(), 'site/testsite/paris/surface/banque_interne/guichet_1/encaisse_des_devises/usd/entrante')
      if cell.getId() == 'movement_0_0_0':
        # check the quantity of banknote 20
        self.assertEqual(cell.getQuantity(), 5.0)

      else:
        self.fail('Wrong cell created : %s' % cell.getId())



  def stepAssignToCounter(self, sequence=None, sequence_list=None, **kwd):
    """
    Pay the check payment

    FIXME: check if the transition fails when a category or property is invalid.
    """
    self.workflow_tool.doActionFor(self.currency_purchase, 'confirm_action', wf_id='currency_purchase_workflow')
    self.assertEqual(self.currency_purchase.getSimulationState(), 'confirmed')



  def stepCheckConfirmedInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the inventory in state confirmed
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 0 banknotes of 10000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 0.0)
     # check the final inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl(),resource=self.currency_1.getRelativeUrl()), 100000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl(),resource=self.currency_1.getRelativeUrl()), 164000)


  def stepPay(self, sequence=None, sequence_list=None, **kwd):
    """
    Pay the check payment

    FIXME: check if the transition fails when a category or property is invalid.
    """
    self.assertEqual(self.currency_purchase.getSourceTotalAssetPrice(),
                     self.currency_purchase.getTotalPrice(portal_type = 'Cash Delivery Cell'))
    self.workflow_tool.doActionFor(self.currency_purchase, 'deliver_action', wf_id='currency_purchase_workflow')
    self.assertEqual(self.currency_purchase.getSimulationState(), 'delivered')
    self.assertEqual(100.0, self.currency_purchase.getTotalPrice(portal_type = 'Cash Delivery Cell'))

  def stepCheckFinalInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 0 banknotes of 10000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.bi_counter_vault.getRelativeUrl(), resource = self.usd_billet_20.getRelativeUrl()), 5.0)
     # check the final inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl(),resource=self.currency_1.getRelativeUrl()), 164000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl(),resource=self.currency_1.getRelativeUrl()), 164000)
     #self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl(),resource=self.currency_1.getRelativeUrl()), 120000)

    for variation in self.usd_variation_list:
      # get the delivery cell
      cell = self.valid_incoming_line.getCell('emission_letter/not_defined', variation, 'cash_status/not_defined')
      # chek portal types
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.usd_billet_20)
      # check the source vault is encaisse_paris
      self.assertEqual(cell.getBaobabSource(), None)
      # check the destination vault is guichet_1
      self.assertEqual(cell.getBaobabDestination(), 'site/testsite/paris/surface/banque_interne/guichet_1/encaisse_des_devises/usd/entrante')

  def test_01_ERP5BankingCurrencyPurchase(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run: return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialInventory ' \
                      'CreateCurrencyPurchase Tic ' \
                      'AssignToCounter ' \
                      'CreateValidIncomingLine ' \
                      'Tic ' \
                      'CheckConfirmedInventory ' \
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
    suite.addTest(unittest.makeSuite(TestERP5BankingCurrencyPurchase))
    return suite
