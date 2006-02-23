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
import AccessControl
from zLOG import LOG
from Testing import ZopeTestCase
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from AccessControl.SecurityManagement import newSecurityManager
from Products.DCWorkflow.DCWorkflow import Unauthorized, ValidationFailed
from Testing.ZopeTestCase.PortalTestCase import PortalTestCase

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

# Define how to launch the script if we don't use runUnitTest script
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))



class TestERP5BankingCheckPayment(ERP5TypeTestCase):
  """
    This class is a unit test to check the module of Check Payment

    Here are the following step that will be done in the test :
  
    - before the test, we need to create some movements that will put resources in the source

    - create a cash classification
    - check it has been created correctly
    - check source and destination (current == future)
    - check roles (who is author, assignor, assignee, ...)

    - create a "Note Line" (billetage)
    - check it has been created correctly
    - check the total amount

    - create a second Line
    - check it has been created correctly
    - check the total amount

    - create an invalid Line (quantity > available at source)
    - check that the system behaves correctly

    - pass "confirm_action" transition
    - check that we can't pass the transition as another user (depending on roles)
    - check that the new state is confirmed
    - check that the source has been debited correctly (current < future)

    - log in as "Controleur" (assignee)
    - check amount, lines, ...

    - pass "deliver_action" transition
    - check that we can't pass the transition as another user
    - check that the new state is delivered
    - check that the destination has been credited correctly (current == future)
  """

  login = PortalTestCase.login

  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet



  ##################################
  ##  ZopeTestCase Skeleton
  ##################################

  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingCheckPayment"


  def getBusinessTemplateList(self):
    """
      Return the list of business templates we need to run the test.
      This method is called during the initialization of the unit test by
      the unit test framework in order to know which business templates
      need to be installed to run the test on.
    """
    return ('erp5_trade', 'erp5_banking_core', 'erp5_banking_inventory', 'erp5_banking_check_payment')


  def enableLightInstall(self):
    """
      Return if we should do a light install (1) or not (0)
      Light install variable is used at installation of categories in business template
      to know if we wrap the category or not, if 1 we don't use and installation is faster
    """
    return 1 # here we want a light install for a faster installation


  def enableActivityTool(self):
    """
      Return if we should create (1) or not (0) an activity tool
      This variable is used at the creation of the site to know if we use
      the activity tool or not
    """
    return 1 # here we want to use the activity tool


  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    # Set some variables : 
    # the erp5 site
    self.portal = self.getPortal()
    # the check payment module
    self.check_payment_module = self.getCheckPaymentModule()
    # the checkbook module
    self.checkbook_module = self.getCheckbookModule()
    # the cash inventory module
    self.cash_inventory_module = self.getCashInventoryModule()
    # the person module
    self.person_module = self.getPersonModule()
    # the organisation module
    self.organisation_module = self.getOrganisationModule()
    # the category tool
    self.category_tool = self.getCategoryTool()
    # the workflow tool
    self.workflow_tool = self.getWorkflowTool()

    # Let us know which user folder is used (PAS or NuxUserGroup)
    self.checkUserFolderType()

    # Create a user and login as manager to populate the erp5 portal with objects for tests.
    self.createManagerAndLogin()

    # Define static values (only use prime numbers to prevent confusions like 2 * 6 == 3 * 4)
    # variation list is the list of years for banknotes and coins
    self.variation_list = ('variation/1992', 'variation/2003')

    # quantity of banknotes of 10000 :
    self.quantity_10000 = {}
    # 2 banknotes of 10000 for the year 1992
    self.quantity_10000[self.variation_list[0]] = 2
    # 3 banknotes of 10000 for the year of 2003
    self.quantity_10000[self.variation_list[1]] = 3

    # quantity of coin of 200
    self.quantity_200 = {}
    # 5 coins of 200 for the year 1992
    self.quantity_200[self.variation_list[0]] = 5
    # 7 coins of 200 for the year 2003
    self.quantity_200[self.variation_list[1]] = 7

    # quantity of banknotes of 5000
    self.quantity_5000 = {}
    # 11 banknotes of 5000 for hte year 1992
    self.quantity_5000[self.variation_list[0]] = 11
    # 13 banknotes of 5000 for the year 2003
    self.quantity_5000[self.variation_list[1]] = 13


    # Create Categories (vaults)

    # as local roles are defined in portal types as real categories, we will need to reproduce (or import) the real category tree
    # get the base category function
    self.function_base_category = getattr(self.category_tool, 'function')
    # add category banking in function which will hold all functions neccessary in a bank (at least for this unit test)
    self.banking = self.function_base_category.newContent(id='banking', portal_type='Category', codification='BNK')
    # add function categories
    self.caissier_principal = self.banking.newContent(id='caissier_principal', portal_type='Category', codification='CCP')
    self.caissier_particulier = self.banking.newContent(id='caissier_particulier', portal_type='Category', codification='CGU')
    self.comptable = self.banking.newContent(id='comptable', portal_type='Category', codification='FXF')
    self.chef_section = self.banking.newContent(id='chef_section', portal_type='Category', codification='FXS')
    self.void_function = self.banking.newContent(id='void_function', portal_type='Category', codification='VOID')
    self.chef_comptable = self.banking.newContent(id='chef_comptable', portal_type='Category', codification='CCB')
    self.gestionnaire_caisse_courante = self.banking.newContent(id='gestionnaire_caisse_courante', portal_type='Category', codification='CCO')

    # get the base category group
    self.group_base_category = getattr(self.category_tool, 'group')
    # add the group baobab in the group category
    self.baobab = self.group_base_category.newContent(id='baobab', portal_type='Category', codification='BAOBAB')

    # get the base category site
    self.site_base_category = getattr(self.category_tool, 'site')
    # add the category testsite in the category site which hold vaults situated in the bank
    self.testsite = self.site_base_category.newContent(id='site', portal_type='Category', codification='TEST')
#     self.siegesite = self.testsite.newContent(id='siege', portal_type='Category', codification='SIEGE')
    self.siegesite = self.site_base_category.newContent(id='siege', portal_type='Category', codification='SIEGE')
    self.agencesite = self.site_base_category.newContent(id='agence', portal_type='Category', codification='AGENCE')
    self.principalesite = self.agencesite.newContent(id='principale', portal_type='Category', codification='PRINCIPALE')
    self.dakar = self.principalesite.newContent(id='dakar', portal_type='Category', codification='K00')
    self.auxisite = self.agencesite.newContent(id='auxiliaire', portal_type='Category', codification='AUXILIAIRE')
        
    self.encaisse_billets_et_monnaies = self.testsite.newContent(id='encaisse_des_billets_et_monnaies', portal_type='Category', codification='C1')
    self.encaisse_externe = self.testsite.newContent(id='encaisse_des_externes', portal_type='Category', codification='C1')
    self.encaisse_ventilation = self.testsite.newContent(id='encaisse_des_billets_recus_pour_ventilation', portal_type='Category', codification='C1')
    self.caisse_abidjan = self.encaisse_ventilation.newContent(id='abidjan', portal_type='Category', codification='C1')

    # get the base category cash_status
    self.cash_status_base_category = getattr(self.category_tool, 'cash_status')
    # add the category valid in cash_status which define status of banknotes and coin
    self.cash_status_valid = self.cash_status_base_category.newContent(id='valid', portal_type='Category')
    self.cash_status_valid = self.cash_status_base_category.newContent(id='to_sort', portal_type='Category')

    # get the base category emission letter
    self.emission_letter_base_category = getattr(self.category_tool, 'emission_letter')
    # add the category k in emission letter that will be used fo banknotes and coins
    self.emission_letter_k = self.emission_letter_base_category.newContent(id='k', portal_type='Category')
    self.emission_letter_b = self.emission_letter_base_category.newContent(id='b', portal_type='Category')
    self.emission_letter_d = self.emission_letter_base_category.newContent(id='d', portal_type='Category')

    # get the base category variation which hold the year of banknotes and coins
    self.variation_base_category = getattr(self.category_tool, 'variation')
    # add the category 1992 in variation
    self.variation_1992 = self.variation_base_category.newContent(id='1992', portal_type='Category')
    # add the category 2003 in varitation
    self.variation_2003 = self.variation_base_category.newContent(id='2003', portal_type='Category')

    # get the base category quantity_unit
    self.variation_base_category = getattr(self.category_tool, 'quantity_unit')
    # add category unit in quantity_unit which is the unit that will be used for banknotes and coins
    self.unit = self.variation_base_category.newContent(id='unit', title='Unit')

    # Create an Organisation that will be used for users assignment
    self.organisation = self.organisation_module.newContent(id='baobab_org', portal_type='Organisation',
        function='banking', group='baobab',  site='site')

    # Create some users who will get different roles on the cash classification.
    #
    # Dictionnary data scheme:
    #     'user_login': [['Global Role'], 'organisation', 'function', 'group', 'site']
    #
    user_dict = {
        'user_1' : [[], self.organisation, 'banking/comptable', 'baobab', 'site']
      , 'user_2' : [[], self.organisation, 'banking/caissier_particulier' , 'baobab', 'site']
      , 'user_3' : [[], self.organisation, 'banking/void_function'     , 'baobab', 'site']
      }
    # call method to create this user
    self.createERP5Users(user_dict)

    # We must assign local roles to check_payment_module, checkbook_module and person_module manually, as they are
    #   not packed in Business Templates yet.
    # The local roles must be the one for gestionnaire_caisse_courante
    if self.PAS_installed:
      # in case of use of PAS
      self.check_payment_module.manage_addLocalRoles('FXF_BAOBAB_TEST', ('Author',))
      self.person_module.manage_addLocalRoles('FXF_BAOBAB_TEST', ('Assignor',))
      self.checkbook_module.manage_addLocalRoles('FXF_BAOBAB_TEST', ('Auditor',))
      self.check_payment_module.manage_addLocalRoles('CGU_BAOBAB_TEST', ('DestinationAssignor',))
    else:
      # in case of NuxUserGroup
      self.check_payment_module.manage_addLocalGroupRoles('FXF_BAOBAB_TEST', ('Author',))
      self.person_module.manage_addLocalGroupRoles('FXF_BAOBAB_TEST', ('Assignor',))
      self.checkbook_module.manage_addLocalGroupRoles('FXF_BAOBAB_TEST', ('Auditor',))
      self.check_payment_module.manage_addLocalGroupRoles('CGU_BAOBAB_TEST', ('DestinationAssignor',))

    # get the currency module
    self.currency_module = self.getCurrencyModule()
    # create the currency document for Fran CFA inside the currency module
    self.currency_1 = self .currency_module.newContent(id='EUR', title='Euros', reference='EUR')

    # Create Resources (Banknotes & Coins)
    # get the currency cash module
    self.currency_cash_module = self.getCurrencyCashModule()
    # create document for banknote of 10000 euros from years 1992 and 2003
    self.billet_10000 = self.currency_cash_module.newContent(id='billet_10000', portal_type='Banknote', base_price=10000, price_currency_value=self.currency_1, variation_list=('1992', '2003'), quantity_unit_value=self.unit)
    # create document for banknote of 500 euros from years 1992 and 2003
    self.billet_5000 = self.currency_cash_module.newContent(id='billet_5000', portal_type='Banknote', base_price=5000, price_currency_value=self.currency_1, variation_list=('1992', '2003'), quantity_unit_value=self.unit)
    # create docuemnt for coin of 200 euros from years 1992 and 2003
    self.billet_200 = self.currency_cash_module.newContent(id='billet_200', portal_type='Banknote', base_price=200, price_currency_value=self.currency_1, variation_list=('1992', '2003'), quantity_unit_value=self.unit)

    # Before the test, we need to input the inventory
    self.cash_inventory_group = self.cash_inventory_module.newContent(id='inventory_group_1', portal_type='Cash Inventory Group',
            source=None, destination_value=self.encaisse_billets_et_monnaies)
    self.cash_inventory = self.cash_inventory_group.newContent(id='inventory_1', portal_type='Cash Inventory',
                                                               price_currency_value=self.currency_1)
    # add a line for banknotes of 10000 with emission letter k, status valid and from years 1992 and 2003 with the quantity defined
    # before in quantity_10000 (2 for 1992 and 3 for 2003)
    self.addCashLineToDelivery(self.cash_inventory, 'delivery_init_1', 'Cash Inventory Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/k', 'cash_status/to_sort') + self.variation_list,
            self.quantity_10000)
    # add a line for coins of 200 with emission letter k, status valid and from years 1992 and 2003 with the quantity defined
    # before in quantity_200 (5 for 1992 and 7 for 2003)
    self.addCashLineToDelivery(self.cash_inventory, 'delivery_init_2', 'Cash Inventory Line', self.billet_200,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/k', 'cash_status/to_sort') + self.variation_list,
            self.quantity_200)
    self.addCashLineToDelivery(self.cash_inventory, 'delivery_init_3', 'Cash Inventory Line', self.billet_5000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/k', 'cash_status/to_sort') + self.variation_list,
            self.quantity_5000)

    # create a person and a bank account
    self.person_1 = self.person_module.newContent(id = 'person_1', portal_type = 'Person',
                                                  first_name = 'toto', last_name = 'titi')
    self.bank_account_1 = self.person_1.newContent(id = 'bank_account_1', portal_type = 'Bank Account',
                                                   price_currency_value = self.currency_1)
    # validate this bank account for payment
    self.bank_account_1.validate()

    # create a check
    self.checkbook_1 = self.checkbook_module.newContent(id = 'checkbook_1', portal_type = 'Checkbook',
                                                        destination_value = self.dakar,
                                                        destination_payment_value = self.bank_account_1,
                                                        reference_range_min = '50',
                                                        reference_range_max = '100',
                                                        start_date = DateTime())
    self.check_1 = self.checkbook_1.newContent(id = 'check_1', portal_type = 'Check',
                                               quantity = 20000, reference='50') # XXX what is this quantity???

    # logout from manager
    self.logout()
    # Finally, login as user_1
    self.login('user_1')


  def checkUserFolderType(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Check the type of user folder to let the test working with both NuxUserGroup and PAS.
    """
    self.user_folder = self.getUserFolder()
    self.PAS_installed = 0
    if self.user_folder.meta_type == 'Pluggable Auth Service':
      # we use PAS
      self.PAS_installed = 1


  def assignPASRolesToUser(self, user_name, role_list, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Assign a list of roles to one user with PAS.
    """
    for role in role_list:
      if role not in self.user_folder.zodb_roles.listRoleIds():
        self.user_folder.zodb_roles.addRole(role)
      self.user_folder.zodb_roles.assignRoleToPrincipal(role, user_name)


  def createManagerAndLogin(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Create a simple user in user_folder with manager rights.
      This user will be used to initialize data in the method afterSetup
    """
    self.getUserFolder()._doAddUser('manager', '', ['Manager'], [])
    self.login('manager')


  def createERP5Users(self, user_dict, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Create all ERP5 users needed for the test.
      ERP5 user = Person object + Assignment object in erp5 person_module.
    """
    for user_login, user_data in user_dict.items():
      user_roles = user_data[0]
      # Create the Person.
      person = self.person_module.newContent(id=user_login,
          portal_type='Person', reference=user_login, career_role="internal")
      # Create the Assignment.
      assignment = person.newContent( portal_type       = 'Assignment'
                                    , destination_value = user_data[1]
                                    , function          = user_data[2]
                                    , group             = user_data[3]
                                    , site              = user_data[4]
                                    )
      if self.PAS_installed and len(user_roles) > 0:
        # In the case of PAS, if we want global roles on user, we have to do it manually.
        self.assignPASRolesToUser(user_login, user_roles)
      elif not self.PAS_installed:
        # The user_folder counterpart of the erp5 user must be
        #   created manually in the case of NuxUserGroup.
        self.user_folder.userFolderAddUser( name     = user_login
                                          , password = ''
                                          , roles    = user_roles
                                          , domains  = []
                                          )
      # User assignment to security groups is also required, but is taken care of
      #   by the assignment workflow when NuxUserGroup is used and
      #   by ERP5Security PAS plugins in the context of PAS use.
      assignment.open()
      
    if self.PAS_installed:
      # reindexing is required for the security to work
      get_transaction().commit()
      self.tic()


  ##################################
  ##  Usefull methods
  ##################################

  def addCashLineToDelivery(self, delivery_object, line_id, line_portal_type, resource_object,
          variation_base_category_list, variation_category_list, resource_quantity_dict):
    """
    Add a cash line to a delivery
    This will add an Internal Packing List Line to a Internal Packing List
    """
    base_id = 'movement'
    line_kwd = {'base_id':base_id}
    # create the cash line
    line = delivery_object.newContent( id                  = line_id
                                     , portal_type         = line_portal_type
                                     , resource_value      = resource_object # banknote or coin
                                     , quantity_unit_value = self.unit
                                     )
    # set base category list on line
    line.setVariationBaseCategoryList(variation_base_category_list)
    # set category list line
    line.setVariationCategoryList(variation_category_list)
    line.updateCellRange(script_id='CashDetail_asCellRange', base_id=base_id)
    cell_range_key_list = line.getCellRangeKeyList(base_id=base_id)
    if cell_range_key_list <> [[None, None]] :
      for k in cell_range_key_list:
        category_list = [item for item in k if item is not None]
        c = line.newCell(*k, **line_kwd)
        mapped_value_list = ['price', 'quantity']
        c.edit( membership_criterion_category_list = category_list
              , mapped_value_property_list         = mapped_value_list
              , category_list                      = category_list
              , force_update                       = 1
              )
    # set quantity on cell to define quantity of bank notes / coins
    for variation in self.variation_list:
      cell = line.getCell('emission_letter/k', variation, 'cash_status/to_sort')
      if cell is not None:
        cell.setQuantity(resource_quantity_dict[variation])
    for variation in self.variation_list:
      cell = line.getCell('emission_letter/b', variation, 'cash_status/to_sort')
      if cell is not None:
        cell.setQuantity(resource_quantity_dict[variation])

  def getUserFolder(self):
    """
    Return the user folder
    """
    return getattr(self.getPortal(), 'acl_users', None)

  def getPersonModule(self):
    """
    Return the person module
    """
    return getattr(self.getPortal(), 'person_module', None)
  
  def getOrganisationModule(self):
    """
    Return the organisation module
    """
    return getattr(self.getPortal(), 'organisation_module', None)
  
  def getCurrencyCashModule(self):
    """
    Return the Currency Cash Module
    """
    return getattr(self.getPortal(), 'currency_cash_module', None)
  
  def getCashInventoryModule(self):
    """
    Return the Cash Inventory Module
    """
    return getattr(self.getPortal(), 'cash_inventory_module', None)
  
  def getCheckPaymentModule(self):
    """
    Return the Check Payment Module
    """
    return getattr(self.getPortal(), 'check_payment_module', None)
  
  def getCheckbookModule(self):
    """
    Return the Checkbook Module
    """
    return getattr(self.getPortal(), 'checkbook_module', None)
  
  def getCurrencyModule(self):
    """
    Return the Currency Module
    """
    return getattr(self.getPortal(), 'currency_module', None)
  
  def getCategoryTool(self):
    """
    Return the Category Tool
    """
    return getattr(self.getPortal(), 'portal_categories', None)
  
  def getWorkflowTool(self):
    """
    Return the Worklfow Tool
    """
    return getattr(self.getPortal(), 'portal_workflow', None)
  
  def getSimulationTool(self):
    """
    Return the Simulation Tool
    """
    return getattr(self.getPortal(), 'portal_simulation', None)



  ##################################
  ##  Basic steps
  ##################################

  def stepTic(self, **kwd):
    """
    The is used to simulate the zope_tic_loop script
    Each time this method is called, it simulates a call to tic
    which invoke activities in the Activity Tool
    """
    # execute transaction
    get_transaction().commit()
    self.tic()


  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    # check that Categories were created
    self.assertEqual(self.encaisse_billets_et_monnaies.getPortalType(), 'Category')

    # check that Resources were created
    # check portal type of billet_10000
    self.assertEqual(self.billet_10000.getPortalType(), 'Banknote')
    # check value of billet_10000
    self.assertEqual(self.billet_10000.getBasePrice(), 10000)
    # check currency value  of billet_10000
    self.assertEqual(self.billet_10000.getPriceCurrency(), 'currency_module/EUR')
    # check years  of billet_10000
    self.assertEqual(self.billet_10000.getVariationList(), ['1992', '2003'])

    # check portal type of billet_5000
    self.assertEqual(self.billet_5000.getPortalType(), 'Banknote')
    # check value of billet_5000
    self.assertEqual(self.billet_5000.getBasePrice(), 5000)
    # check currency value  of billet_5000
    self.assertEqual(self.billet_5000.getPriceCurrency(), 'currency_module/EUR')
    # check years  of billet_5000
    self.assertEqual(self.billet_5000.getVariationList(), ['1992', '2003'])
    
    # check portal type of billet_200
    self.assertEqual(self.billet_200.getPortalType(), 'Banknote')
    # check value of billet_200
    self.assertEqual(self.billet_200.getBasePrice(), 200)
    # check currency value  of billet_200
    self.assertEqual(self.billet_200.getPriceCurrency(), 'currency_module/EUR')
    # check years  of billet_200
    self.assertEqual(self.billet_200.getVariationList(), ['1992', '2003'])

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
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_billets_et_monnaies.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_billets_et_monnaies.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200 in encaisse_billets_et_monnaies
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_billets_et_monnaies.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_billets_et_monnaies.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    # check we have 24 banknotes of 200 in encaisse_billets_et_monnaies
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_billets_et_monnaies.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_billets_et_monnaies.getRelativeUrl(), resource = self.billet_5000.getRelativeUrl()), 24.0)


  def stepCreateCheckPayment(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a check payment document and check it
    """
    self.check_payment = self.check_payment_module.newContent(id = 'check_payment', portal_type = 'Check Payment',
                                         destination_payment_value = self.bank_account_1,
                                         aggregate_value = self.check_1,
                                         source_value = self.encaisse_billets_et_monnaies,
                                         start_date = DateTime(),
                                         source_total_asset_price = 20000.0)
    self.assertNotEqual(self.check_payment, None)
    self.assertEqual(self.check_payment.getTotalPrice(), 0.0)
    self.assertEqual(self.check_payment.getDestinationPayment(), self.bank_account_1.getRelativeUrl())
    self.assertEqual(self.check_payment.getAggregate(), self.check_1.getRelativeUrl())
    self.assertEqual(self.check_payment.getSourceTotalAssetPrice(), 20000.0)
    self.assertEqual(self.check_payment.getSource(), self.encaisse_billets_et_monnaies.getRelativeUrl())

    # the initial state must be draft
    self.assertEqual(self.check_payment.getSimulationState(), 'draft')

    # source reference must be automatically generated
    self.check_payment.setSourceReference(self.check_payment.Baobab_getUniqueReference())
    self.assertNotEqual(self.check_payment.getSourceReference(), None)
    self.assertNotEqual(self.check_payment.getSourceReference(), '')

  def stepCheckConsistency(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the consistency of the check payment

    FIXME: check if the transition fails when a category or property is invalid.
    FIXME: check if the transition fails when a bad user tries.
    """
    self.assertNotEqual(self.check_payment.getAggregateValue(), None)

    self.workflow_tool.doActionFor(self.check_payment, 'plan_action', wf_id='check_payment_workflow')
    self.assertEqual(self.check_payment.getSimulationState(), 'planned')

  def stepSendToCounter(self, sequence=None, sequence_list=None, **kwd):
    """
    Send the check payment to the counter

    FIXME: check if the transition fails when a category or property is invalid.
    FIXME: check if the transition fails when a bad user tries.
    """
    self.workflow_tool.doActionFor(self.check_payment, 'confirm_action', wf_id='check_payment_workflow')
    self.assertEqual(self.check_payment.getSimulationState(), 'confirmed')

    self.assertEqual(self.check_payment.getSourceTotalAssetPrice(),
                     - self.check_payment.getTotalPrice(portal_type = 'Banking Operation Line'))

  def stepInputCashDetails(self, sequence=None, sequence_list=None, **kwd):
    """
    Input cash details
    """
    self.addCashLineToDelivery(self.check_payment, 'line_1', 'Cash Delivery Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'),
            ('emission_letter/k', 'cash_status/to_sort') + self.variation_list[1:],
            {self.variation_list[1] : 1})
    self.assertEqual(self.check_payment.line_1.getPrice(), 10000)

    self.addCashLineToDelivery(self.check_payment, 'line_2', 'Cash Delivery Line', self.billet_5000,
            ('emission_letter', 'cash_status', 'variation'),
            ('emission_letter/k', 'cash_status/to_sort') + self.variation_list[1:],
            {self.variation_list[1] : 2})
    self.assertEqual(self.check_payment.line_2.getPrice(), 5000)

  def stepPay(self, sequence=None, sequence_list=None, **kwd):
    """
    Pay the check payment

    FIXME: check if the transition fails when a category or property is invalid.
    FIXME: check if the transition fails when a bad user tries.
    """
    self.logout()
    self.login('user_2')

    self.assertEqual(self.check_payment.getSourceTotalAssetPrice(),
                     self.check_payment.getTotalPrice(portal_type = 'Cash Delivery Cell'))
    try:
      self.workflow_tool.doActionFor(self.check_payment, 'deliver_action', wf_id='check_payment_workflow')
    except:
      import pdb
      pdb.set_trace()

    self.assertEqual(self.check_payment.getSimulationState(), 'delivered')

  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingCheckPayment(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run: return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialInventory ' \
                      'CreateCheckPayment Tic ' \
                      'CheckConsistency Tic ' \
                      'SendToCounter Tic ' \
                      'InputCashDetails Tic ' \
                      'Pay Tic '
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
    suite.addTest(unittest.makeSuite(TestERP5BankingCheckPayment))
    return suite
