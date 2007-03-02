##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
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
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.DCWorkflow.DCWorkflow import Unauthorized, ValidationFailed
from Testing.ZopeTestCase.PortalTestCase import PortalTestCase
from Products.ERP5Banking.tests.testERP5BankingCheckbookUsualCashTransfer \
     import TestERP5BankingCheckbookUsualCashTransferMixin
from Products.ERP5Banking.tests.TestERP5BankingMixin import TestERP5BankingMixin
from DateTime import DateTime
from zLOG import LOG

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

# Define how to launch the script if we don't use runUnitTest script
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))

class TestERP5BankingTravelerCheckSaleMixin:

  def getTravelerCheckSaleModule(self):
    """
    Return the Traveler Check Sale Module
    """
    return getattr(self.getPortal(), 'traveler_check_sale_module', None)



  def createCheckbookUsualCashTransferWithTravelerCheck(self, sequence=None, 
                                 sequence_list=None, **kwd):
    """
    Create a checkbook Reception
    We do not need to check it because it is already done in another unit test.
    """
    self.checkbook_vault_transfer = self.getCheckbookUsualCashTransferModule().newContent(
                     id='checkbook_usual_cash_transfer', portal_type='Checkbook Usual Cash Transfer',
                     source_value=self.source_vault, 
                     description='test',
                     destination_value=self.destination_vault,
                     start_date=(self.date-1))
    # Add a line for traveler check
    self.line_2 = self.checkbook_vault_transfer.newContent(quantity=1,
                             resource_value=self.traveler_check_model,
                             check_amount_value=self.traveler_check_model.variant_1,
                             aggregate_value=self.traveler_check,
                             )
    self.workflow_tool.doActionFor(self.checkbook_vault_transfer, 'confirm_action', 
                                   wf_id='checkbook_usual_cash_transfer_workflow')
    self.workflow_tool.doActionFor(self.checkbook_vault_transfer, 'confirm_to_deliver_action', 
                                   wf_id='checkbook_usual_cash_transfer_workflow')


  def stepCreateTravelerCheckSale(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a traveler check sale
    """
    # We will do the transfer ot two items.
    self.traveler_check_sale = self.traveler_check_sale_module.newContent(
                     id='traveler_check_sale', portal_type='Traveler Check Sale',
                     source_value=self.traveler_check_source, destination_value=None,
                     destination_payment_value=self.bank_account_1,
                     resource_value=self.currency_1,
                     start_date=self.date)
    # check its portal type
    self.assertEqual(self.traveler_check_sale.getPortalType(), 'Traveler Check Sale')
    # check source
    self.assertEqual(self.traveler_check_sale.getBaobabSource(), 
               'site/testsite/paris/surface/banque_interne/guichet_1/encaisse_des_billets_et_monnaies')
    # check destination
    self.assertEqual(self.traveler_check_sale.getBaobabDestination(), None)
    self.setDocumentSourceReference(self.traveler_check_sale)

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    # Set some variables :

    self.initDefaultVariable()
    # the cash inventory module
    self.traveler_check_sale_module = self.getTravelerCheckSaleModule()
    self.checkbook_reception_module = self.getCheckbookReceptionModule()
    self.check_module = self.getCheckModule()
    self.checkbook_module = self.getCheckbookModule()
    self.checkbook_model_module = self.getCheckbookModelModule()

    self.createManagerAndLogin()
    self.createFunctionGroupSiteCategory()
    self.checkbook_model_1 = self.createCheckbookModel('checkbook_model_1')
    self.check_model_1 = self.createCheckModel('check_model_1')
    self.createBanknotesAndCoins()
    self.vault_transfer_source_site = self.paris.caveau
    self.vault_transfer_destination_site = self.paris.surface
    self.source_site = self.paris.surface.caisse_courante
    self.reception_destination_site = self.paris
    self.destination_site = self.paris.surface.banque_interne.guichet_1
    self.source_vault = self.paris.surface.caisse_courante.encaisse_des_billets_et_monnaies
    self.destination_vault = self.paris.surface.banque_interne.guichet_1.encaisse_des_billets_et_monnaies
             
    self.destination_vault = self.paris.surface.banque_interne.guichet_1.encaisse_des_billets_et_monnaies
    self.traveler_check_source = self.destination_vault
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

    # create a person and a bank account
    self.person_1 = self.createPerson(id='person_1',
                                      first_name='Sebastien',
                                      last_name='Robin')
    self.bank_account_1 = self.createBankAccount(person=self.person_1,
                                                 account_id='bank_account_1',
                                                 currency=self.currency_1,
                                                 amount=100000)
    # this is required in order to have some items
    # in the source
    self.traveler_check_model = self.createTravelerCheckModel('traveler_check_model')
    self.createCheckbookReceptionWithTravelerCheck()
    get_transaction().commit()
    self.tic()
    self.checkItemsCreatedWithTravelerCheck()
    get_transaction().commit()
    self.tic()
    self.createCheckbookVaultTransferWithTravelerCheck()
    get_transaction().commit()
    self.tic()
    # open counter date and counter
    self.openCounterDate(site=self.paris)
    self.openCounter(site=self.destination_site)
    self.createCheckbookUsualCashTransferWithTravelerCheck()
    get_transaction().commit()
    self.tic()

  def stepCreateTravelerCheckLineList(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the checkbook
    """
    # This is not required to create checkbook items, they will be
    # automatically created with the confirm action worfklow transition

    # Add a line for check
    self.line_1 = self.traveler_check_sale.newContent(quantity=1,
                                 resource_value=self.traveler_check_model,
                                 check_type_value=self.traveler_check_model.variant_1,
                                 reference_range_min=52,
                                 reference_range_max=52,
                                 aggregate_value=self.traveler_check,
                                 price_currency_value=self.currency_2
                                 )


  def stepDeliverTravelerCheckSale(self, sequence=None, sequence_list=None, **kw):
    """
    Deliver the traveler check sale
    """
    state = self.traveler_check_sale.getSimulationState()
    # check that state is draft
    self.assertEqual(state, 'draft')
    self.workflow_tool.doActionFor(self.traveler_check_sale, 
                                   'deliver_action', 
                                   wf_id='traveler_check_sale_workflow')
    # get state of cash sorting
    state = self.traveler_check_sale.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.traveler_check_sale, 
                            name='history', wf_id='traveler_check_sale_workflow')
    self.assertEqual(len(workflow_history), 3)

class TestERP5BankingTravelerCheckSale(TestERP5BankingCheckbookUsualCashTransferMixin,
                                       TestERP5BankingTravelerCheckSaleMixin,
                                       TestERP5BankingMixin, ERP5TypeTestCase):
  """
    This class is a unit test to check the module of Cash Transfer

    Here are the following step that will be done in the test :

    XXX to be completed

  """

  login = PortalTestCase.login

  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet


  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingTravelerCheckSale"


  def getBusinessTemplateList(self):
    """
      Return the list of business templates we need to run the test.
      This method is called during the initialization of the unit test by
      the unit test framework in order to know which business templates
      need to be installed to run the test on.
    """
    return ('erp5_base',
            'erp5_trade',
            'erp5_accounting',
            'erp5_banking_core',
            'erp5_banking_inventory',
            'erp5_banking_check',
            )



  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that TravelerCheckSale Module was created
    self.assertEqual(self.traveler_check_sale_module.getPortalType(), 'Traveler Check Sale Module')
    # check module is empty
    self.assertEqual(len(self.traveler_check_sale_module.objectValues()), 0)


  def stepCheckInitialCheckbookInventory(self, sequence=None, sequence_list=None, **kw):
    """
    Check initial cash checkbook on source
    """
    self.assertEqual(len(self.simulation_tool.getCurrentTrackingList(
                     node=self.traveler_check_source.getRelativeUrl(),
                     at_date=self.date)), 1)
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(
                     node=self.traveler_check_source.getRelativeUrl(),
                     at_date=self.date)), 1)
    checkbook_list = self.simulation_tool.getCurrentTrackingList(
                             node=self.traveler_check_source.getRelativeUrl(),
                             at_date=self.date)
    self.assertEqual(len(checkbook_list), 1)
    # check we have cash checkbook 1
    checkbook_object_list = [x.getObject() for x in checkbook_list]
    self.failIfDifferentSet(checkbook_object_list,[self.traveler_check])
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 100000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 100000)



  def stepCheckFinalCheckbookInventory(self, sequence=None, sequence_list=None, **kw):
    """
    Check cash checkbook in item table
    """
    self.assertEqual(len(self.simulation_tool.getCurrentTrackingList(
                     node=self.traveler_check_source.getRelativeUrl(),
                     at_date=self.date)), 0)
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(
                     node=self.traveler_check_source.getRelativeUrl(),
                     at_date=self.date)), 0)
    checkbook_list = self.simulation_tool.getCurrentTrackingList(
                             node=self.traveler_check_source.getRelativeUrl(),
                             at_date=self.date)
    self.assertEqual(len(checkbook_list), 0)
    # check we have cash checkbook 1
    checkbook_object_list = [x.getObject() for x in checkbook_list]
    self.assertEquals(len(checkbook_object_list),0)
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(
                     payment=self.bank_account_1.getRelativeUrl()), 67500)
    self.assertEqual(self.simulation_tool.getFutureInventory(
                     payment=self.bank_account_1.getRelativeUrl()), 67500)

  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingTravelerCheckSale(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run: return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialCheckbookInventory ' \
                    + 'CreateTravelerCheckSale Tic ' \
                    + 'CreateTravelerCheckLineList Tic ' \
                    + 'DeliverTravelerCheckSale Tic ' \
                    + 'CheckFinalCheckbookInventory'
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
    suite.addTest(unittest.makeSuite(TestERP5BankingTravelerCheckSale))
    return suite
