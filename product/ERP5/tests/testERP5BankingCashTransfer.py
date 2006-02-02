##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Alexandre Boeglin <alex_AT_nexedi_DOT_com>
#                    Kevin Deldycke <kevin_AT_nexedi_DOT_com>
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



class TestERP5BankingCashTransfer(ERP5TypeTestCase):
  """
    This class is a unit test to check the module of Cash Transfer

    Here are the following step that will be done in the test :
  
    - before the test, we need to create some movements that will put resources in the source

    - create a cash transfer
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
    return "ERP5BankingCashTransfer"


  def getBusinessTemplateList(self):
    """
      Return the list of business templates we need to run the test.
      This method is called during the initialization of the unit test by
      the unit test framework in order to know which business templates
      need to be installed to run the test on.
    """
    return ( 'erp5_trade'  # erp5_trade is not required to make erp5_banking_cash_transfer working.
                           # As explained below erp5_trade is just used to help us initialize ressources
                           #   via Internal Packing List.
           , 'erp5_banking_core' # erp5_banking_core contains all generic methods for banking
           , 'erp5_banking_cash_transfer' # erp5_banking_cash contains all method for cash transfer
           )


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
    # the cahs transfer module
    self.cash_transfer_module = self.getCashTransferModule()
    # the person module
    self.person_folder = self.getPersonModule()
    # the organisation module
    self.organisation_folder = self.getOrganisationModule()
    # the category tool
    self.category_tool = self.getCategoryTool()

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
    # add category caisier_principal in function banking
    self.caissier_principal = self.banking.newContent(id='caissier_principal', portal_type='Category', codification='CCP')
    # add category controleur_caisse in function banking
    self.controleur_caisse = self.banking.newContent(id='controleur_caisse', portal_type='Category', codification='CCT')
    # add category void_function in function banking
    self.void_function = self.banking.newContent(id='void_function', portal_type='Category', codification='VOID')
    # add category gestionnaire_caisse_courante in function banking
    self.gestionnaire_caisse_courante = self.banking.newContent(id='gestionnaire_caisse_courante', portal_type='Category', codification='CCO')
    # add category gestionnaire_caveau in function banking
    self.gestionnaire_caveau = self.banking.newContent(id='gestionnaire_caveau', portal_type='Category', codification='CCV')
    # add category caissier_particulier in function banking
    self.caissier_particulier = self.banking.newContent(id='caissier_particulier', portal_type='Category', codification='CGU')

    # get the base category group
    self.group_base_category = getattr(self.category_tool, 'group')
    # add the group baobab in the group category
    self.baobab = self.group_base_category.newContent(id='baobab', portal_type='Category', codification='BAOBAB')

    # get the base category site
    self.site_base_category = getattr(self.category_tool, 'site')
    # add the category testsite in the category site which hold vaults situated in the bank
    self.testsite = self.site_base_category.newContent(id='testsite', portal_type='Category', codification='TEST')
    # add vault caisse_1 in testsite
    self.caisse_1 = self.testsite.newContent(id='caisse_1', portal_type='Category', codification='C1')
    # add vault caisse_2 in testsite
    self.caisse_2 = self.testsite.newContent(id='caisse_2', portal_type='Category', codification='C2')

    # get the base category cash_status
    self.cash_status_base_category = getattr(self.category_tool, 'cash_status')
    # add the category valid in cash_status which define status of banknotes and coin
    self.cash_status_valid = self.cash_status_base_category.newContent(id='valid', portal_type='Category')

    # get the base category emission letter
    self.emission_letter_base_category = getattr(self.category_tool, 'emission_letter')
    # add the category k in emission letter that will be used fo banknotes and coins
    self.emission_letter_k = self.emission_letter_base_category.newContent(id='k', portal_type='Category')

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
    self.organisation = self.organisation_folder.newContent(id='baobab_org', portal_type='Organisation',
        function='banking', group='baobab',  site='testsite')

    # Create some users who will get different roles on the cash transfer.
    #
    # Dictionnary data scheme:
    #     'user_login': [['Global Role'], 'organisation', 'function', 'group', 'site']
    #
    user_dict = {
        'user_1' : [[], self.organisation, 'banking/gestionnaire_caisse_courante', 'baobab', 'testsite']
      , 'user_2' : [[], self.organisation, 'banking/controleur_caisse' , 'baobab', 'testsite']
      , 'user_3' : [[], self.organisation, 'banking/void_function'     , 'baobab', 'testsite']
      }
    # call method to create this user
    self.createERP5Users(user_dict)

    # We must assign local roles to cash_transfer_module manually, as they are
    #   not packed in Business Templates yet.
    # The local roles must be the one for gestionnaire_caisse_courante
    if self.PAS_installed:
      # in case of use of PAS
      self.cash_transfer_module.manage_addLocalRoles('CCO_BAOBAB_TEST', ('Author',))
    else:
      # in case of NuxUserGroup
      self.cash_transfer_module.manage_addLocalGroupRoles('CCO_BAOBAB_TEST', ('Author',))

    # get the currency module
    self.currency_module = self.getCurrencyModule()
    # create the currency document for euro inside the currency module
    self.currency_1 = self .currency_module.newContent(id='EUR', title='Euro')

    # Create Resources (Banknotes & Coins)
    # get the currency cash module
    self.currency_cash_module = self.getCurrencyCashModule()
    # create document for banknote of 10000 euros from years 1992 and 2003
    self.billet_10000 = self.currency_cash_module.newContent(id='billet_10000', portal_type='Banknote', base_price=10000, price_currency_value=self.currency_1, variation_list=('1992', '2003'), quantity_unit_value=self.unit)
    # create document for banknote of 500 euros from years 1992 and 2003
    self.billet_5000 = self.currency_cash_module.newContent(id='billet_5000', portal_type='Banknote', base_price=5000, price_currency_value=self.currency_1, variation_list=('1992', '2003'), quantity_unit_value=self.unit)
    # create docuemnt for coin of 200 euros from years 1992 and 2003
    self.piece_200 = self.currency_cash_module.newContent(id='piece_200', portal_type='Coin', base_price=200, price_currency_value=self.currency_1, variation_list=('1992', '2003'), quantity_unit_value=self.unit)

    # Before the test, we need to create resources in the source.
    # Using internal_packing_list from erp5_trade is the easiest.
    # set the type of delivery
    self.portal.portal_delivery_type_list = list(self.portal.portal_delivery_type_list)
    self.portal.portal_delivery_type_list.append('Internal Packing List')
    self.portal.portal_delivery_type_list = tuple(self.portal.portal_delivery_type_list)
    # set the type of delivey movement
    self.portal.portal_delivery_movement_type_list = list(self.portal.portal_delivery_movement_type_list)
    self.portal.portal_delivery_movement_type_list.append('Internal Packing List Line')
    self.portal.portal_delivery_movement_type_list = tuple(self.portal.portal_delivery_movement_type_list)
    # get the internal packing list module
    self.internal_packing_list_module = self.getInternalPackingListModule()
    # add a new internal packing list for caisse_1
    self.internal_packing_list = self.internal_packing_list_module.newContent(id='packing_list_1', portal_type='Internal Packing List',
            source=None, destination_value=self.caisse_1)
    # add a line for banknotes of 10000 with emission letter k, status valid and from years 1992 and 2003 with the quantity defined
    # before in quantity_10000 (2 for 1992 and 3 for 2003)
    self.addCashLineToDelivery(self.internal_packing_list, 'delivery_init_1', 'Internal Packing List Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/k', 'cash_status/valid') + self.variation_list,
            self.quantity_10000)
    # add a line for coins of 200 with emission letter k, status valid and from years 1992 and 2003 with the quantity defined
    # before in quantity_200 (5 for 1992 and 7 for 2003)
    self.addCashLineToDelivery(self.internal_packing_list, 'delivery_init_2', 'Internal Packing List Line', self.piece_200,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/k', 'cash_status/valid') + self.variation_list,
            self.quantity_200)

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
      person = self.person_folder.newContent(id=user_login,
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
        category_list = filter(lambda k_item: k_item is not None, k)
        c = line.newCell(*k, **line_kwd)
        mapped_value_list = ['price', 'quantity']
        c.edit( membership_criterion_category_list = category_list
              , mapped_value_property_list         = mapped_value_list
              , category_list                      = category_list
              , force_update                       = 1
              )
    # set quantity on cell to define quantity of bank notes / coins
    for variation in self.variation_list:
      cell = line.getCell('emission_letter/k', variation, 'cash_status/valid')
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
  
  def getCashTransferModule(self):
    """
    Return the Cash Transer Module
    """
    return getattr(self.getPortal(), 'cash_transfer_module', None)
  
  def getInternalPackingListModule(self):
    """
    Return the Internal Packing List Module
    """
    return getattr(self.getPortal(), 'internal_packing_list_module', None)
  
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
    self.assertEqual(self.caisse_1.getPortalType(), 'Category')
    self.assertEqual(self.caisse_2.getPortalType(), 'Category')

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
    
    # check portal type of piece_200
    self.assertEqual(self.piece_200.getPortalType(), 'Coin')
    # check value of piece_200
    self.assertEqual(self.piece_200.getBasePrice(), 200)
    # check currency value  of piece_200
    self.assertEqual(self.piece_200.getPriceCurrency(), 'currency_module/EUR')
    # check years  of piece_200
    self.assertEqual(self.piece_200.getVariationList(), ['1992', '2003'])

    # check that CashTransfer Module was created
    self.assertEqual(self.cash_transfer_module.getPortalType(), 'Cash Transfer Module')
    # check cash transfer module is empty
    self.assertEqual(len(self.cash_transfer_module.objectValues()), 0)


  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in caisse_1
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200 in caisse_1
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)


  def stepCheckSource(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory in source vault (caisse_1) before a confirm
    """
    # check we have 5 banknotes of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)


  def stepCheckDestination(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory in destination vault (caisse_2) before confirm
    """
    # check we don't have banknotes of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_2.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_2.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we don't have coins of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_2.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_2.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)


  def stepCreateCashTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a cash transfer document and check it
    """
    # Cash transfer has caisse_1 for source, caisse_2 for destination, and a price cooreponding to the sum of banknote of 10000 abd coin of 200 ( (2+3) * 1000 + (5+7) * 200 )
    self.cash_transfer = self.cash_transfer_module.newContent(id='cash_transfer_1', portal_type='Cash Transfer', source_value=self.caisse_1, destination_value=self.caisse_2, price=52400.0)
    # execute tic
    self.stepTic()
    # check we have only one cash transfer
    self.assertEqual(len(self.cash_transfer_module.objectValues()), 1)
    # get the cash transfer document
    self.cash_transfer = getattr(self.cash_transfer_module, 'cash_transfer_1')
    # check its portal type
    self.assertEqual(self.cash_transfer.getPortalType(), 'Cash Transfer')
    # check that its source is caisse_1
    self.assertEqual(self.cash_transfer.getSource(), 'site/testsite/caisse_1')
    # check that its destination is caisse_2
    self.assertEqual(self.cash_transfer.getDestination(), 'site/testsite/caisse_2')
    #XXX Check roles were correctly affected
    #self.security_manager = AccessControl.getSecurityManager()
    #self.user = self.security_manager.getUser()
    #raise 'alex', repr( self.cash_transfer.get_local_roles() )


  def stepCreateValidLine1(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash transfer line 1 with banknotes of 10000 and check it has been well created
    """
    # create the cash transfer line
    self.addCashLineToDelivery(self.cash_transfer, 'valid_line_1', 'Cash Transfer Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/k', 'cash_status/valid') + self.variation_list,
            self.quantity_10000)
    # execute tic
    self.stepTic()
    # check there is only one line created
    self.assertEqual(len(self.cash_transfer.objectValues()), 1)
    # get the cash transfer line
    self.valid_line_1 = getattr(self.cash_transfer, 'valid_line_1')
    # check its portal type
    self.assertEqual(self.valid_line_1.getPortalType(), 'Cash Transfer Line')
    # check the resource is banknotes of 10000
    self.assertEqual(self.valid_line_1.getResourceValue(), self.billet_10000)
    # chek the value of the banknote
    self.assertEqual(self.valid_line_1.getPrice(), 10000.0)
    # check the unit of banknote
    self.assertEqual(self.valid_line_1.getQuantityUnit(), 'quantity_unit/unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_line_1.objectValues()), 2)
    # now check for each variation (years 1992 and 2003)
    for variation in self.variation_list:
      # get the delivery cell
      cell = self.valid_line_1.getCell('emission_letter/k', variation, 'cash_status/valid')
      # chek portal types
      self.assertEqual(cell.getPortalType(), 'Delivery Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      # check the source vault is caisse_1
      self.assertEqual(cell.getSourceValue(), self.caisse_1)
      # check the destination vault is caisse_2
      self.assertEqual(cell.getDestinationValue(), self.caisse_2)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity of banknote for year 1992 is 2
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity of banknote for year 2003 is 3
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepCheckSubTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the amount after the creation of cash transfer line 1
    """
    # Check number of lines
    self.assertEqual(len(self.cash_transfer.objectValues()), 1)
    # Check quantity of banknotes (2 for 1992 and 3 for 2003)
    self.assertEqual(self.cash_transfer.getTotalQuantity(), 5.0)
    # Check the total price
    self.assertEqual(self.cash_transfer.getTotalPrice(), 10000 * 5.0)


  def stepCreateValidLine2(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash transfer line 2 wiht coins of 200 and check it has been well created
    """
    # create the line
    self.addCashLineToDelivery(self.cash_transfer, 'valid_line_2', 'Cash Transfer Line', self.piece_200,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/k', 'cash_status/valid') + self.variation_list,
            self.quantity_200)
    # execute tic
    self.stepTic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.cash_transfer.objectValues()), 2)
    # get the second cash transfer line
    self.valid_line_2 = getattr(self.cash_transfer, 'valid_line_2')
    # check portal types
    self.assertEqual(self.valid_line_2.getPortalType(), 'Cash Transfer Line')
    # check the resource is coin of 200
    self.assertEqual(self.valid_line_2.getResourceValue(), self.piece_200)
    # check the value of coin
    self.assertEqual(self.valid_line_2.getPrice(), 200.0)
    # check the unit of coin
    self.assertEqual(self.valid_line_2.getQuantityUnit(), 'quantity_unit/unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_line_2.objectValues()), 2)
    for variation in self.variation_list:
      # get the delivery  cell
      cell = self.valid_line_2.getCell('emission_letter/k', variation, 'cash_status/valid')
      # check the portal type
      self.assertEqual(cell.getPortalType(), 'Delivery Cell')
      if cell.getId() == 'movement_0_0_0':
        # check the quantity for coin for year 1992 is 5
        self.assertEqual(cell.getQuantity(), 5.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity for coin for year 2003 is 7
        self.assertEqual(cell.getQuantity(), 7.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

        
  
  def stepTryConfirmCashTransferWithBadUser(self, sequence=None, sequence_list=None, **kwd):
    """
    Try to confirm cash transfer with a user that doesn't have the right and
    check that the try of confirm by a bad user doesn't change the cash transfer
    """
    # logout from user_1
    self.logout()
    # log in as bad user
    self.login('user_3')
    # get workflow tool
    self.workflow_tool = self.getWorkflowTool()
    # check that an Unauthorized exception is raised when trying to confirm the cash transfer
    self.assertRaises(Unauthorized, self.workflow_tool.doActionFor, self.cash_transfer, 'confirm_action', wf_id='cash_transfer_workflow')
    # logout from user_3
    self.logout()
    # login as default user
    self.login('user_1')
    # execute tic
    self.stepTic()
    # get state of the cash transfer
    state = self.cash_transfer.getSimulationState()
    # check it has remain as draft
    self.assertEqual(state, 'draft')
    # get the workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_transfer, name='history', wf_id='cash_transfer_workflow')
    # check its len is one
    self.assertEqual(len(workflow_history), 1)


  def stepCreateInvalidLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create an invalid cash transfer line and
    check the total with the invalid cash transfer line
    """
    # create a line in which quanity of banknotes of 5000 is higher that quantity available at source
    # here create a line with 24 (11+13) banknotes of 500 although the vault caisse_1 has no banknote of 5000
    self.addCashLineToDelivery(self.cash_transfer, 'invalid_line', 'Cash Transfer Line', self.billet_5000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/k', 'cash_status/valid') + self.variation_list,
            self.quantity_5000)
    # execute tic
    self.stepTic()
    # Check number of cash transfer lines (line1 + line2 +invalid_line)
    self.assertEqual(len(self.cash_transfer.objectValues()), 3)
    # Check quantity, same as checkTotal + banknote of 500: 11 for 1992 and 13 for 2003
    self.assertEqual(self.cash_transfer.getTotalQuantity(), 5.0 + 12.0 + 24)
    # chect the total price
    self.assertEqual(self.cash_transfer.getTotalPrice(), 10000 * 5.0 + 200 * 12.0 + 5000 * 24)


  def stepTryConfirmCashTransferWithBadInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Try to confirm the cash transfer with a bad cash transfer line and
    check the try of confirm the cash transfer with the invalid line has failed
    """
    # fix amount (10000 * 5.0 + 200 * 12.0 + 5000 * 24)
    self.cash_transfer.setPrice('172400.0')
    # try to do the workflow action "confirm_action', cath the exception ValidationFailed raised by workflow transition 
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.cash_transfer, 'confirm_action', wf_id='cash_transfer_workflow')
    # execute tic
    self.stepTic()
    # get state of the cash transfer
    state = self.cash_transfer.getSimulationState()
    # check the state is draft
    self.assertEqual(state, 'draft')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_transfer, name='history', wf_id='cash_transfer_workflow')
    # check its len is 2
    self.assertEqual(len(workflow_history), 2)
    # check we get an "Insufficient balance" message in the workflow history because of the invalid line
    self.assertEqual('Insufficient balance' in workflow_history[-1]['error_message'], True)


  def stepDelInvalidLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Delete the invalid cash transfer line previously create
    """
    self.cash_transfer.deleteContent('invalid_line')


  def stepCheckTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the total after the creation of the two cash transfer lines
    """
    # Check number of lines (line1 + line2)
    self.assertEqual(len(self.cash_transfer.objectValues()), 2)
    # Check quantity, banknotes : 2 for 1992 and 3 for 2003, coin : 5 for 1992 and 7 for 2003
    self.assertEqual(self.cash_transfer.getTotalQuantity(), 5.0 + 12.0)
    # check the total price
    self.assertEqual(self.cash_transfer.getTotalPrice(), 10000 * 5.0 + 200 * 12.0)


  def stepConfirmCashTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    Confirm the cash transfer and check it
    """
    # fix amount (10000 * 5.0 + 200 * 12.0)
    self.cash_transfer.setPrice('52400.0')
    # do the Workflow action
    self.workflow_tool.doActionFor(self.cash_transfer, 'confirm_action', wf_id='cash_transfer_workflow')
    # execute tic
    self.stepTic()
    # get state
    state = self.cash_transfer.getSimulationState()
    # check state is confirmed
    self.assertEqual(state, 'confirmed')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_transfer, name='history', wf_id='cash_transfer_workflow')
    # check len of workflow history is 4
    self.assertEqual(len(workflow_history), 4)


  def stepCheckSourceDebitPlanned(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault caisse_1 is right after confirm and before deliver 
    """
    # check we have 5 banknotes of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we will have 0 banknote of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 12 coins of 200 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    # check we will have 0 coin of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)


  def stepCheckDestinationCreditPlanned(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault caisse_2 is right after confirm and before deliver
    """
    # check we have 0 banknote of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_2.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we will have 5 banknotes of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_2.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 0 coin of 200 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_2.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    # check we will have 12 coins of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_2.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)


  def stepTryDeliverCashTransferWithBadUser(self, sequence=None, sequence_list=None, **kwd):
    """
    Try to deliver a cash transfer with a user that doesn't have the right
    and check that it failed
    """
    # logout from user_1
    self.logout()
    # log in as bad user
    self.login('user_3')
    # check we raise an Unauthorized Exception if we try to deliver cash transfer
    self.assertRaises(Unauthorized, self.workflow_tool.doActionFor, self.cash_transfer, 'deliver_action', wf_id='cash_transfer_workflow')
    # logout from bad user
    self.logout()
    # log in as default user
    self.login('user_1')
    # execute tic
    self.stepTic()
    # get state of the cash transfer
    state = self.cash_transfer.getSimulationState()
    # check that state is confirmed
    self.assertEqual(state, 'confirmed')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_transfer, name='history', wf_id='cash_transfer_workflow')
    # check len of workflow history is 4
    self.assertEqual(len(workflow_history), 4)


  def stepDeliverCashTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    Deliver the cash transfer with a good user
    and check that the deliver of a cash tranfer have achieved
    """
    # logout from user_1
    self.logout()
    # log in as good user (controleur_caisse)
    self.login('user_2')
    #     self.security_manager = AccessControl.getSecurityManager()
    #     self.user = self.security_manager.getUser()
    # do the workflow transition "deliver_action"
    self.workflow_tool.doActionFor(self.cash_transfer, 'deliver_action', wf_id='cash_transfer_workflow')
    # logout from user_2
    self.logout()
    # log in as default user
    self.login('user_1')
    # execute tic
    self.stepTic()
    # get state of cash transfer
    state = self.cash_transfer.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_transfer, name='history', wf_id='cash_transfer_workflow')
    # check len of len workflow history is 6
    self.assertEqual(len(workflow_history), 6)
    

  def stepCheckSourceDebit(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at source (vault caisse_1) after deliver of the cash transfer
    """
    # check we have 0 banknote of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 0 coin of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)


  def stepCheckDestinationCredit(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at destination (vault caisse_2) after deliver of the cash transfer
    """
    # check we have 5 banknotes of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_2.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_2.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coins of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_2.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_2.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)


  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingCashTransfer(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run: return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialInventory CheckSource CheckDestination ' \
                    + 'CreateCashTransfer ' \
                    + 'CreateValidLine1 CheckSubTotal ' \
                    + 'CreateValidLine2 CheckTotal ' \
                    + 'TryConfirmCashTransferWithBadUser ' \
                    + 'CheckSource CheckDestination ' \
                    + 'CreateInvalidLine ' \
                    + 'TryConfirmCashTransferWithBadInventory ' \
                    + 'DelInvalidLine Tic CheckTotal ' \
                    + 'ConfirmCashTransfer ' \
                    + 'CheckSourceDebitPlanned CheckDestinationCreditPlanned ' \
                    + 'TryDeliverCashTransferWithBadUser ' \
                    + 'CheckSourceDebitPlanned CheckDestinationCreditPlanned ' \
                    + 'DeliverCashTransfer ' \
                    + 'CheckSourceDebit CheckDestinationCredit '
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
    suite.addTest(unittest.makeSuite(TestERP5BankingCashTransfer))
    return suite
