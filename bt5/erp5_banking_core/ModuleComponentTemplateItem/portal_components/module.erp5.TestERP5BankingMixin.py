#############################################################################
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

from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

def isSameSet(a, b):
  for i in a:
    if i not in b:
      return False
  for i in b:
    if i not in a:
      return False
  return len(a) == len(b)

class TestERP5BankingMixin(ERP5TypeTestCase):
  """
  Mixin class for unit test of banking operations
  """

  def getBusinessTemplateList(self):
    """
      Return the list of business templates we need to run the test.
      This method is called during the initialization of the unit test by
      the unit test framework in order to know which business templates
      need to be installed to run the test on.
    """
    return ('erp5_core_proxy_field_legacy',
            'erp5_base',
            'erp5_pdm',
            'erp5_trade',
            'erp5_item',
            'erp5_accounting',
            'erp5_banking_core',
            'erp5_banking_inventory',
            'erp5_banking_cash',
            'erp5_banking_check',
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

  def checkUserFolderType(self):
    """
      Check the type of user folder to let the test working with both NuxUserGroup and PAS.
    """
    self.user_folder = self.getUserFolder()
    self.PAS_installed = 0
    if self.user_folder.meta_type == 'Pluggable Auth Service':
      # we use PAS
      self.PAS_installed = 1

  def updateRoleMappings(self, portal_type_list=None):
    """Update the local roles in existing objects.
    """
    portal_catalog = self.portal.portal_catalog
    for portal_type in portal_type_list:
      for brain in portal_catalog(portal_type = portal_type):
        obj = brain.getObject()
        userdb_path, user_id = obj.getOwnerTuple()
        obj.assignRoleToSecurityGroup(user_name = user_id)

  def assignPASRolesToUser(self, user_name, role_list):
    """
      Assign a list of roles to one user with PAS.
    """
    for role in role_list:
      if role not in self.user_folder.zodb_roles.listRoleIds():
        self.user_folder.zodb_roles.addRole(role)
      self.user_folder.zodb_roles.assignRoleToPrincipal(role, user_name)

  def createManagerAndLogin(self):
    """
      Create a simple user in user_folder with manager rights.
      This user will be used to initialize data in the method afterSetup
    """
    self.getUserFolder()._doAddUser('manager', '', ['Manager'], [])
    self.loginByUserName('manager')

  def createERP5Users(self, user_dict):
    """
      Create all ERP5 users needed for the test.
      ERP5 user = Person object + Assignment object in erp5 person_module.
    """
    for user_login, user_data in user_dict.items():
      user_roles = user_data[0]
      # Create the Person.
      main_site = '/'.join(user_data[4].split('/')[0:2])
      person = self.person_module.newContent(id=user_login,
          portal_type='Person', reference=user_login, career_role="internal",
          site=main_site)
      # Create the Assignment.
      assignment = person.newContent( portal_type       = 'Assignment'
                                    , destination_value = user_data[1]
                                    , function          = "function/%s" %user_data[2]
                                    , group             = "group/%s" %user_data[3]
                                    , site              = "%s" %user_data[4]
                                    , start_date        = '01/01/1900'
                                    , stop_date         = '01/01/2900'
                                    )
      if self.PAS_installed and len(user_roles) > 0:
        # In the case of PAS, if we want global roles on user, we have to do it manually.
        self.assignPASRolesToUser(person.Person_getUserId(), user_roles)
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
      person.newContent(
        portal_type='ERP5 Login',
        reference=user_login,
      ).validate()

    if self.PAS_installed:
      # reindexing is required for the security to work
      self.tic()



  def getUserFolder(self):
    return self.getPortal().acl_users

  def getPersonModule(self):
    return self.getPortal().person_module

  def getOrganisationModule(self):
    return self.getPortal().organisation_module

  def getCurrencyCashModule(self):
    return self.getPortal().currency_cash_module

  def getCashInventoryModule(self):
    return self.getPortal().cash_inventory_module

  def getBankAccountInventoryModule(self):
    return self.getPortal().bank_account_inventory_module

  def getCurrencyModule(self):
    return self.getPortal().currency_module

  def getCategoryTool(self):
    return self.getPortal().portal_categories

  def getWorkflowTool(self):
    return self.getPortal().portal_workflow

  def getSimulationTool(self):
    return self.getPortal().portal_simulation

  def getCheckPaymentModule(self):
    return self.getPortal().check_payment_module

  def getStopPaymentModule(self):
    return self.getPortal().stop_payment_module

  def getCheckDepositModule(self):
    return self.getPortal().check_deposit_module

  def getCheckbookModule(self):
    return self.getPortal().checkbook_module

  def getCheckbookModelModule(self):
    return self.getPortal().checkbook_model_module

  def getCheckbookReceptionModule(self):
    return self.getPortal().checkbook_reception_module

  def getCheckbookVaultTransferModule(self):
    return self.getPortal().checkbook_vault_transfer_module

  def getCheckbookUsualCashTransferModule(self):
    return self.getPortal().checkbook_usual_cash_transfer_module

  def getCheckbookDeliveryModule(self):
    return self.getPortal().checkbook_delivery_module

  def getCheckModule(self):
    return self.getPortal().check_module

  def getAccountingDateModule(self):
    return self.getPortal().accounting_date_module

  def getCounterDateModule(self):
    return self.getPortal().counter_date_module

  def getCounterModule(self):
    return self.getPortal().counter_module

  def getCashMovementModule(self):
    return self.getPortal().cash_movement_module

  def getCashMovementNewNotEmittedModule(self):
    return self.getPortal().cash_movement_new_not_emitted_module

  def getMonetaryReceptionModule(self):
    return self.getPortal().monetary_reception_module

  def getMonetaryIssueModule(self):
    return self.getPortal().monetary_issue_module

  def getAccountingCancellationModule(self):
    return self.getPortal().accounting_cancellation_module

  def getCashBalanceRegulationModule(self):
    return self.getPortal().cash_balance_regulation_module

  def getCashSortingModule(self):
    return self.getPortal().cash_sorting_module

  def getCashExchangeModule(self):
    return self.getPortal().cash_exchange_module

  def getCashToCurrencyPurchaseModule(self):
    return self.getPortal().cash_to_currency_purchase_module

  def getClassificationSurveyModule(self):
    return self.getPortal().classification_survey_module

  def getCounterRenderingModule(self):
    return self.getPortal().counter_rendering_module

  def getDestructionSurveyModule(self):
    return self.getPortal().destruction_survey_module

  def getForeignCashReceptionModule(self):
    return self.getPortal().foreign_cash_reception_module

  def getInternalMoneyDepositModule(self):
    return self.getPortal().internal_money_deposit_module

  def getInternalMoneyPaymentModule(self):
    return self.getPortal().internal_money_payment_module

  def getMonetaryDestructionModule(self):
    return self.getPortal().monetary_destruction_module

  def getMonetaryRecallModule(self):
    return self.getPortal().monetary_recall_module

  def getMonetarySurveyModule(self):
    return self.getPortal().monetary_survey_module

  def getMoneyDepositModule(self):
    return self.getPortal().money_deposit_module

  def getMoneyDepositRenderingModule(self):
    return self.getPortal().money_deposit_rendering_module

  def getMutilatedBanknoteModule(self):
    return self.getPortal().mutilated_banknote_module

  def getTravelerCheckPurchaseModule(self):
    return self.getPortal().traveler_check_purchase_module

  def getTravelerCheckSaleModule(self):
    return self.getPortal().traveler_check_sale_module

  def getUsualCashRenderingModule(self):
    return self.getPortal().usual_cash_rendering_module

  def getUsualCashTransferModule(self):
    return self.getPortal().usual_cash_transfer_module

  def getVaultTransferModule(self):
    return self.getPortal().vault_transfer_module

  def createCurrency(self, currency_list=(('EUR', 'Euro', 1/652., 1/650., 'USD'), ('USD', 'USD', 652, 650., 'EUR')), only_currency=False):
    # create the currency document for euro inside the currency module
    #currency_list = (('EUR', 'Euro', 1/650., 'USD'), ('USD', 'Dollar', 650., 'EUR'))
    # first create currency
    for currency_id, title, base_price, cell_price, price_currency in currency_list:
      self._maybeNewContent(self.getCurrencyModule(), id=currency_id,
        title=title, reference=currency_id)

    if only_currency:
      return

    # second, create exchange lines
    for currency_id, title, base_price, cell_price, price_currency in currency_list:
      currency = self.getCurrencyModule()[currency_id]
      exchange_line = None
      exchange_line = currency.newContent(portal_type='Currency Exchange Line',
                                          start_date='01/01/1900', stop_date='01/01/2900',
                                          base_price=base_price,
                                          currency_exchange_type_list=['currency_exchange_type/sale',
                                                                       'currency_exchange_type/purchase',
                                                                       'currency_exchange_type/transfer'],
                                          )
      exchange_line.setPriceCurrencyValue(self.getCurrencyModule()[price_currency])
      cell_list = exchange_line.objectValues()
      self.assertEqual(len(cell_list), 3)
      for cell in cell_list:
        cell.setBasePrice(cell_price)

      exchange_line.confirm()
      exchange_line.validate()



  def _createBanknotesAndCoins(self):
    """
    Create some banknotes and coins
    """
    # Define static values (only use prime numbers to prevent confusions like 2 * 6 == 3 * 4)
    # variation list is the list of years for banknotes and coins
    self.variation_list = ('variation/1992', 'variation/2003')
    self.usd_variation_list = ('variation/not_defined', )
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

    # quantity of coin of 100
    self.quantity_100 = {}
    # 5 coins of 100 for the year 1992
    self.quantity_100[self.variation_list[0]] = 4
    # 7 coins of 100 for the year 2003
    self.quantity_100[self.variation_list[1]] = 6

    # quantity of banknotes of 5000
    self.quantity_5000 = {}
    # 11 banknotes of 5000 for hte year 1992
    self.quantity_5000[self.variation_list[0]] = 11
    # 13 banknotes of 5000 for the year 2003
    self.quantity_5000[self.variation_list[1]] = 13

    # quantity of usd banknote of 200
    self.quantity_usd_200 = {}
    # 2 banknotes of 200
    self.quantity_usd_200['variation/not_defined'] = 2
    # quantity of usd banknote of 100
    self.quantity_usd_100 = {}
    # 2 banknotes of 100
    self.quantity_usd_100['variation/not_defined'] = 2
    # quantity of usd banknote of 50
    self.quantity_usd_50 = {}
    # 3 banknotes of 50
    self.quantity_usd_50['variation/not_defined'] = 3
    # quantity of usd banknote of 20
    self.quantity_usd_20 = {}
    # 5 banknotes of 20
    self.quantity_usd_20['variation/not_defined'] = 5

    # Now create required category for banknotes and coin
    self.cash_status_base_category = getattr(self.category_tool, 'cash_status')
    # add the category valid in cash_status which define status of banknotes and coin
    self.cash_status_valid = self._maybeNewContent(self.cash_status_base_category, id='valid', portal_type='Category')
    self.cash_status_to_sort = self._maybeNewContent(self.cash_status_base_category, id='to_sort', portal_type='Category')
    self.cash_status_cancelled = self._maybeNewContent(self.cash_status_base_category, id='cancelled', portal_type='Category')
    self.cash_status_not_defined = self._maybeNewContent(self.cash_status_base_category, id='not_defined', portal_type='Category')
    self.cash_status_mutilated = self._maybeNewContent(self.cash_status_base_category, id='mutilated', portal_type='Category')
    self.cash_status_retired = self._maybeNewContent(self.cash_status_base_category, id='retired', portal_type='Category')
    self.cash_status_new_not_emitted = self._maybeNewContent(self.cash_status_base_category, id='new_not_emitted', portal_type='Category')
    self.cash_status_mixed = self._maybeNewContent(self.cash_status_base_category, id='mixed', portal_type='Category')

    self.emission_letter_base_category = getattr(self.category_tool, 'emission_letter')
    # add the category k in emission letter that will be used fo banknotes and coins
    self.emission_letter_p = self._maybeNewContent(self.emission_letter_base_category, id='p', portal_type='Category')
    self.emission_letter_s = self._maybeNewContent(self.emission_letter_base_category, id='s', portal_type='Category')
    self.emission_letter_b = self._maybeNewContent(self.emission_letter_base_category, id='b', portal_type='Category')
    self.emission_letter_k = self._maybeNewContent(self.emission_letter_base_category, id='k', portal_type='Category')
    self.emission_letter_mixed = self._maybeNewContent(self.emission_letter_base_category, id='mixed', portal_type='Category')
    self.emission_letter_not_defined = self._maybeNewContent(self.emission_letter_base_category, id='not_defined', portal_type='Category')

    self.variation_base_category = getattr(self.category_tool, 'variation')
    # add the category 1992 in variation
    self.variation_1992 = self._maybeNewContent(self.variation_base_category, id='1992', portal_type='Category')
    # add the category 2003 in variation
    self.variation_2003 = self._maybeNewContent(self.variation_base_category, id='2003', portal_type='Category')
    # add the category not_defined in variation
    self.variation_not_defined = self._maybeNewContent(self.variation_base_category, id='not_defined',
                                      portal_type='Category')

    # Now create required category for region and coin
    self.region_base_category = getattr(self.category_tool, 'region')
    # add the category valid in cash_status which define status of banknotes and coin
    self.region_france = self._maybeNewContent(self.region_base_category, id='france', title="France", portal_type='Category')
    self.region_spain = self._maybeNewContent(self.region_base_category, id='spain', title="Spain", portal_type='Category')

    # Create Resources Document (Banknotes & Coins)
    # get the currency cash module
    self.currency_cash_module = self.getCurrencyCashModule()
    # Create Resources Document (Banknotes & Coins)
    self.createCurrency()
    self.currency_1 = self.currency_module['EUR']
    # create document for banknote of 10000 euros from years 1992 and 2003
    self.billet_10000 = self.currency_cash_module.newContent(id='billet_10000',
         portal_type='Banknote', base_price=10000,
         price_currency_value=self.currency_1, variation_list=('1992', '2003'),
         quantity_unit_value=self.unit)
    # create document for banknote of 500 euros from years 1992 and 2003
    self.billet_5000 = self.currency_cash_module.newContent(id='billet_5000',
         portal_type='Banknote', base_price=5000,
         price_currency_value=self.currency_1, variation_list=('1992', '2003'),
         quantity_unit_value=self.unit)
    # create document for coin of 200 euros from years 1992 and 2003
    self.piece_200 = self.currency_cash_module.newContent(id='piece_200',
         portal_type='Coin', base_price=200,
         price_currency_value=self.currency_1, variation_list=('1992', '2003'),
         quantity_unit_value=self.unit)
    # create document for coin of 200 euros from years 1992 and 2003
    self.piece_100 = self.currency_cash_module.newContent(id='piece_100',
         portal_type='Coin', base_price=100,
         price_currency_value=self.currency_1, variation_list=('1992', '2003'),
         quantity_unit_value=self.unit)
    # create document for banknote of 200 euros from years 1992 and 2003
    self.billet_200 = self.currency_cash_module.newContent(id='billet_200',
         portal_type='Banknote', base_price=200,
         price_currency_value=self.currency_1, variation_list=('1992', '2003'),
         quantity_unit_value=self.unit)
    # create document for banknote of 200 euros from years 1992 and 2003
    self.billet_100 = self.currency_cash_module.newContent(id='billet_100',
         portal_type='Banknote', base_price=100,
         price_currency_value=self.currency_1, variation_list=('1992', '2003'),
         quantity_unit_value=self.unit)
    # Create Resources Document (Banknotes & Coins) in USD
    self.currency_2 = self.currency_module['USD']
    # create document for banknote of 100 USD
    self.usd_billet_100 = self.currency_cash_module.newContent(id='usd_billet_100',
         portal_type='Banknote', base_price=100,
         price_currency_value=self.currency_2, variation_list=('not_defined', ),
         quantity_unit_value=self.unit)
    # create document for banknote of 200 USD
    self.usd_billet_200 = self.currency_cash_module.newContent(id='usd_billet_200',
         portal_type='Banknote', base_price=200,
         price_currency_value=self.currency_2, variation_list=('not_defined', ),
         quantity_unit_value=self.unit)
    # create document for banknote of 50 USD
    self.usd_billet_50 = self.currency_cash_module.newContent(id='usd_billet_50',
         portal_type='Banknote', base_price=50,
         price_currency_value=self.currency_2, variation_list=('not_defined', ),
         quantity_unit_value=self.unit)
    # create document for banknote of 20 USD
    self.usd_billet_20 = self.currency_cash_module.newContent(id='usd_billet_20',
         portal_type='Banknote', base_price=20,
         price_currency_value=self.currency_2, variation_list=('not_defined', ),
         quantity_unit_value=self.unit)

  def _maybeNewContent(self, container, id, **kw):
    try:
      result = container[id]
    except KeyError:
      result = container.newContent(id=id, **kw)
    return result

  def createFunctionGroupSiteCategory(self, no_site=0, site_list=None):
    """
    Create site group function category that can be used for security
    """
    if site_list is None:
      site_list = ["paris", 'madrid', 'siege']

    # add category unit in quantity_unit which is the unit that will be used for banknotes and coins
    self.variation_base_category = getattr(self.category_tool, 'quantity_unit')
    self.unit = self._maybeNewContent(self.variation_base_category, id='unit', title='Unit')

    self._maybeNewContent(self.category_tool.role, id='internal', portal_type='Category')

    # add category for currency_exchange_type
    self.currency_exchange_type = getattr(self.category_tool, 'currency_exchange_type')
    self._maybeNewContent(self.currency_exchange_type, id='sale')
    self._maybeNewContent(self.currency_exchange_type, id='purchase')
    self._maybeNewContent(self.currency_exchange_type, id='transfer')

    # get the base category function
    self.function_base_category = getattr(self.category_tool, 'function')
    # add category banking in function which will hold all functions neccessary in a bank (at least for this unit test)
    self.banking = self._maybeNewContent(self.function_base_category, id='banking', portal_type='Category', codification='BNK')
    self.caissier_principal = self._maybeNewContent(self.banking, id='caissier_principal', portal_type='Category', codification='CCP')
    self.controleur_caisse = self._maybeNewContent(self.banking, id='controleur_caisse', portal_type='Category', codification='CCT')
    self.void_function = self._maybeNewContent(self.banking, id='void_function', portal_type='Category', codification='VOID')
    self.gestionnaire_caisse_courante = self._maybeNewContent(self.banking, id='gestionnaire_caisse_courante', portal_type='Category', codification='CCO')
    self.gestionnaire_caveau = self._maybeNewContent(self.banking, id='gestionnaire_caveau', portal_type='Category', codification='CCV')
    self.caissier_particulier = self._maybeNewContent(self.banking, id='caissier_particulier', portal_type='Category', codification='CGU')
    self.controleur_caisse_courante = self._maybeNewContent(self.banking, id='controleur_caisse_courante', portal_type='Category', codification='CCC')
    self.controleur_caveau = self._maybeNewContent(self.banking, id='controleur_caveau', portal_type='Category', codification='CCA')
    self.comptable = self._maybeNewContent(self.banking, id='comptable', portal_type='Category', codification='FXF')
    self.commis_comptable = self._maybeNewContent(self.banking, id='commis_comptable', portal_type='Category', codification='CBM')
    self.commis_caisse = self._maybeNewContent(self.banking, id='commis_caisse', portal_type='Category', codification='CCM')
    self.chef_section_comptable = self._maybeNewContent(self.banking, id='chef_section_comptable', portal_type='Category', codification='CSB')
    self.chef_comptable = self._maybeNewContent(self.banking, id='chef_comptable', portal_type='Category', codification='CCB')
    self.chef_de_tri = self._maybeNewContent(self.banking, id='chef_de_tri', portal_type='Category', codification='CTR')
    self.chef_caisse = self._maybeNewContent(self.banking, id='chef_caisse', portal_type='Category', codification='CCP')
    self.chef_section = self._maybeNewContent(self.banking, id='chef_section', portal_type='Category', codification='FXS')
    self.chef_section_financier = self._maybeNewContent(self.banking, id='chef_section_financier', portal_type='Category', codification='FXA')
    self.financier_a = self._maybeNewContent(self.banking, id='financier_a', portal_type='Category', codification='FNA')
    self.financier_b = self._maybeNewContent(self.banking, id='financier_b', portal_type='Category', codification='FNB')
    self.chef_financier = self._maybeNewContent(self.banking, id='chef_financier', portal_type='Category', codification='FCF')
    self.admin_local = self._maybeNewContent(self.banking, id='administrateur_local', portal_type='Category', codification='ADL')
    self.agent_saisie_sref = self._maybeNewContent(self.banking, id='agent_saisie_sref', portal_type='Category', codification='SSREF')
    self.chef_sref = self._maybeNewContent(self.banking, id='chef_sref', portal_type='Category', codification='CSREF')
    self.analyste_sref = self._maybeNewContent(self.banking, id='analyste_sref', portal_type='Category', codification='ASREF')
    self.gestionnaire_devise_a = self._maybeNewContent(self.banking, id='gestionnaire_cours_devise_a', portal_type='Category', codification='GCA')
    self.gestionnaire_devise_b = self._maybeNewContent(self.banking, id='gestionnaire_cours_devise_b', portal_type='Category', codification='GCB')
    self.comptable_inter_site = self._maybeNewContent(self.banking, id='comptable_inter_site', portal_type='Category', codification='FXFIS')

    # get the base category group
    self.group_base_category = getattr(self.category_tool, 'group')
    self.baobab_group = self._maybeNewContent(self.group_base_category, id='baobab', portal_type='Category', codification='BAOBAB')
    # get the base category site
    self.site_base_category = getattr(self.category_tool, 'site')
    # add the category testsite in the category site which hold vaults situated in the bank
    self.testsite = self._maybeNewContent(self.site_base_category, id='testsite', portal_type='Category', codification='TEST')
    site_reference_from_codification_dict = {
      'P10': ('FR', '000', '11111', '000000000000', '25'),
      'S10': ('SP', '000', '11111', '000000000000', '08'),
      'HQ1': ('FR', '000', '11112', '000000000000', '69'),
    }
    site_region_from_codification_dict = {
      'P10': 'france', # paris
      'S10': 'spain',  # madrid
      'HQ1': 'france', # main
    }
    self.paris = self._maybeNewContent(self.testsite, id='paris', portal_type='Category', codification='P10',  vault_type='site')
    self.madrid = self._maybeNewContent(self.testsite, id='madrid', portal_type='Category', codification='S10',  vault_type='site')
    self.siege = self._maybeNewContent(self.site_base_category, id='siege', portal_type='Category', codification='HQ1',  vault_type='site')
    created_site_list = [self.paris, self.madrid, self.siege]

    self._createBanknotesAndCoins()

    if len(site_list) != 0:
      for site in site_list:
        if isinstance(site, tuple):
          container = self.site_base_category
          if len(site) > 2:
            for category_id in site[2].split('/'):
              contained = getattr(container, category_id, None)
              if contained is None:
                contained = self._maybeNewContent(container, id=category_id, portal_type='Category')
              container = contained
            if len(site) > 3:
              site_reference_from_codification_dict[site[1]] = site[3]
              if len(site) > 4:
                site_region_from_codification_dict[site[1]] = site[4]
          codification = site[1]
          site = site[0]
        if site not in ("paris", 'madrid', 'siege'):
          site = self._maybeNewContent(container, id=site, portal_type='Category',  codification=codification, vault_type='site')
          created_site_list.append(site)

    # Create organisation + bank account for each site category.
    organisation_module = self.organisation_module
    newContent = organisation_module.newContent
    for site in created_site_list:
      codification = site.getCodification()
      organisation_id = 'site_%s' % (codification, )
      try:
        organisation_module[organisation_id]
      except KeyError:
        organisation = newContent(
          portal_type='Organisation',
          id=organisation_id,
          site=site.getRelativeUrl(),
          region=site_region_from_codification_dict.get(codification),
          group='baobab',
          role='internal',
          function='banking')
        site_reference = site_reference_from_codification_dict.get(codification)
        if site_reference is not None:
          self.createBankAccount(
            person=organisation,
            account_id='account_%s' % (codification, ),
            currency=self.currency_1,
            amount=0,
            bank_country_code=site_reference[0],
            bank_code=site_reference[1],
            branch=site_reference[2],
            bank_account_number=site_reference[3],
            bank_account_key=site_reference[4],
          )

    self.vault_type_base_category = getattr(self.category_tool, 'vault_type')
    site_vault_type = self._maybeNewContent(self.vault_type_base_category, id='site')
    surface_vault_type = self._maybeNewContent(site_vault_type, 'surface')
    bi_vault_type = self._maybeNewContent(surface_vault_type, 'banque_interne')
    co_vault_type = self._maybeNewContent(surface_vault_type, 'caisse_courante')
    de_co_vault_type = self._maybeNewContent(co_vault_type, 'encaisse_des_devises')
    guichet_bi_vault_type = self._maybeNewContent(bi_vault_type, 'guichet')
    gp_vault_type = self._maybeNewContent(surface_vault_type, 'gros_paiement')
    guichet_gp_vault_type = self._maybeNewContent(gp_vault_type, 'guichet')
    gv_vault_type = self._maybeNewContent(surface_vault_type, 'gros_versement')
    guichet_gv_vault_type = self._maybeNewContent(gv_vault_type, 'guichet')
    op_vault_type = self._maybeNewContent(surface_vault_type, 'operations_diverses')
    guichet_op_vault_type = self._maybeNewContent(op_vault_type, 'guichet')
    caveau_vault_type = self._maybeNewContent(site_vault_type, 'caveau')
    auxiliaire_vault_type = self._maybeNewContent(caveau_vault_type, 'auxiliaire')
    self._maybeNewContent(auxiliaire_vault_type, 'auxiliaire_vault_type')
    self._maybeNewContent(auxiliaire_vault_type, 'encaisse_des_devises')
    externe = self._maybeNewContent(auxiliaire_vault_type, 'encaisse_des_externes')
    self._maybeNewContent(externe, 'transit')
    self._maybeNewContent(caveau_vault_type, 'reserve')
    serre = self._maybeNewContent(caveau_vault_type, 'serre')
    self._maybeNewContent(serre, 'transit')
    self._maybeNewContent(serre, 'retire')
    salle_tri = self._maybeNewContent(surface_vault_type, 'salle_tri')

    if not no_site:
      destination_site_list = [x.getId() for x in created_site_list]
      for c in created_site_list: #self.testsite.getCategoryChildValueList():
        # create bank structure for each agency
        site = c.getId()
        # surface
        surface = self._maybeNewContent(c, id='surface', portal_type='Category', codification='',  vault_type='site/surface')
        caisse_courante = self._maybeNewContent(surface, id='caisse_courante', portal_type='Category', codification='',  vault_type='site/surface/caisse_courante')
        self._maybeNewContent(caisse_courante, id='encaisse_des_billets_et_monnaies', portal_type='Category', codification='',  vault_type='site/surface/caisse_courante')
        self._maybeNewContent(caisse_courante, id='billets_mutiles', portal_type='Category', codification='',  vault_type='site/surface/caisse_courante')
        self._maybeNewContent(caisse_courante, id='billets_macules', portal_type='Category', codification='',  vault_type='site/surface/caisse_courante')
        encaisse_des_devises = self._maybeNewContent(caisse_courante, id='encaisse_des_devises', portal_type='Category', codification='',  vault_type='site/surface/caisse_courante/encaisse_des_devises')
        # create counter for surface
        for s in ['banque_interne', 'gros_versement', 'gros_paiement']:
          vault_codification = c.getCodification()
          if s == 'banque_interne':
            vault_codification += 'BI'
          elif s == 'gros_versement':
            vault_codification += 'GV'
          elif s == 'gros_paiement':
            vault_codification += 'GP'
          s = self._maybeNewContent(surface, id='%s' % (s, ), portal_type='Category', codification=vault_codification,  vault_type='site/surface/%s' % (s, ))
          for ss in ['guichet_1', 'guichet_2']:
            final_vault_codification = vault_codification + ss[-1]
            ss =  self._maybeNewContent(s, id='%s' % (ss, ), portal_type='Category', codification=final_vault_codification,  vault_type='site/surface/%s/guichet' % (s.getId(), ))
            for sss in ['encaisse_des_billets_et_monnaies']:
              sss =  self._maybeNewContent(ss, id='%s' % (sss, ), portal_type='Category', codification='',  vault_type='site/surface/%s/guichet' % (s.getId(), ))
              for ssss in ['entrante', 'sortante']:
                self._maybeNewContent(sss, id='%s' % (ssss, ), portal_type='Category', codification='',  vault_type='site/surface/%s/guichet' % (s.getId(), ))
            for sss in ['encaisse_des_devises']:
              sss =  self._maybeNewContent(ss, id='%s' % (sss, ), portal_type='Category', codification='',  vault_type='site/surface/%s/guichet' % (s.getId(), ))
              for currency in ['usd']:
                currency_cat = self._maybeNewContent(sss, id='%s' % (currency, ), portal_type='Category', codification='',  vault_type='site/surface/%s' % (ss.getId(), ))
                for ssss in ['entrante', 'sortante']:
                  self._maybeNewContent(currency_cat, id='%s' % (ssss, ), portal_type='Category', codification='',  vault_type='site/surface/%s/guichet' % (s.getId(), ))
        # create sort room
        salle_tri = self._maybeNewContent(surface, id='salle_tri', portal_type='Category', codification='',  vault_type='site/surface/salle_tri')
        for ss in ['encaisse_des_billets_et_monnaies', 'encaisse_des_billets_recus_pour_ventilation', 'encaisse_des_differences', 'encaisse_des_externes']:
          ss =  self._maybeNewContent(salle_tri, id='%s' % (ss, ), portal_type='Category', codification='',  vault_type='site/surface/salle_tri')
          if 'ventilation' in ss.getId():
            for country in destination_site_list:
              if country[0] != c.getCodification()[0]:
                self._maybeNewContent(ss, id='%s' % (country, ), portal_type='Category', codification='',  vault_type='site/caveau/%s' % (s.getId(), ))
        # caveau
        caveau =  self._maybeNewContent(c, id='caveau', portal_type='Category', codification='',  vault_type='site/caveau')
        for s in ['auxiliaire', 'reserve', 'serre']:
          s = self._maybeNewContent(caveau, id='%s' % (s, ), portal_type='Category', codification='',  vault_type='site/caveau/%s' % (s, ))
          if s.getId() == 'serre':
            for ss in ['encaisse_des_billets_neufs_non_emis', 'encaisse_des_billets_retires_de_la_circulation', 'encaisse_des_billets_detruits', 'encaisse_des_billets_neufs_non_emis_en_transit_allant_a']:
              ss =  self._maybeNewContent(s, id='%s' % (ss, ), portal_type='Category', codification='',  vault_type='site/caveau/%s' % (s.getId(), ))
              if 'transit' in ss.getId():
                for country in destination_site_list:
                  if country[0] != c.getCodification()[0]:
                    self._maybeNewContent(ss, id='%s' % (country, ), portal_type='Category', codification='',  vault_type='site/caveau/%s' % (s.getId(), ))

          else:
            for ss in ['encaisse_des_billets_et_monnaies', 'encaisse_des_externes',
                       'encaisse_des_billets_recus_pour_ventilation', 'encaisse_des_devises']:
              ss =  self._maybeNewContent(s, id='%s' % (ss, ), portal_type='Category', codification='',  vault_type='site/caveau/%s' % (s.getId(), ))
              if 'ventilation' in ss.getId():
                for country in destination_site_list:
                  if country[0] != c.getCodification()[0]:
                    self._maybeNewContent(ss, id='%s' % (country, ), portal_type='Category', codification='',  vault_type='site/caveau/%s' % (s.getId(), ))
              if 'devises' in ss.getId():
                for currency in ['eur', 'usd']:
                  self._maybeNewContent(ss, id='%s' % (currency, ), portal_type='Category', codification='',  vault_type='site/caveau/%s' % (ss.getId(), ))
              if 'encaisse_des_externes' in ss.getId():
                self._maybeNewContent(ss, id='transit', portal_type='Category', codification='',  vault_type='site/caveau/%s' % (s.getId(), ))
              #if ss.getId()=='encaisse_des_devises':
              #  for
            if s.getId() == 'auxiliaire':
              for ss in ['encaisse_des_billets_a_ventiler_et_a_detruire', 'encaisse_des_billets_ventiles_et_detruits', 'billets_detenus_par_des_tiers', 'encaisse_des_billets_recus_pour_ventilation_venant_de']:
                self._maybeNewContent(s, id='%s' % (ss, ), portal_type='Category', codification='',  vault_type='site/caveau/%s' % (s.getId(), ))
        # Create forreing currency entries in encaisse_des_devises.
        for currency in ['usd', ]:
          self._maybeNewContent(caisse_courante.encaisse_des_devises, id=currency, portal_type='Category', codification='', vault_type='site/surface/caisse_courante/encaisse_des_devises')

    return created_site_list

  def _openDate(self, date=None, site=None, id=None, open=True, container=None,
                portal_type=None, force_check=0):
    if date is None:
      date = DateTime().Date()
    if not isinstance(date, str):
      date = date.Date()
    if site is None:
      site = self.testsite
    date_object = container.newContent(id=id, portal_type=portal_type,
                                       site_value = site, start_date = date)
    if open:
      if force_check and date_object.getPortalType() == 'Counter Date':
        self.workflow_tool.doActionFor(date_object, 'open_action',
                                     wf_id='counter_date_workflow',
                                     your_check_date_is_today=0)
      else:
        date_object.open()
    setattr(self, id, date_object)
    date_object.assignRoleToSecurityGroup()

  def openAccountingDate(self, date=None, site=None, id='accounting_date_1', open=True):
    """
    open an accounting date for the given date
    by default use the current date
    """
    self._openDate(date=date, site=site, id=id, open=open, container=self.getAccountingDateModule(), portal_type='Accounting Date')

  def openCounterDate(self, date=None, site=None, id='counter_date_1', open=True, force_check=0):
    """
    open a couter date for the given date
    by default use the current date
    """
    self._openDate(date=date, site=site, id=id, open=open,
                   container=self.getCounterDateModule(),
                   portal_type='Counter Date',
                   force_check=force_check)

  def openCounter(self, site=None, id='counter_1'):
    """
    open a counter for the givent site
    """
    # create a counter
    counter_module = self.getCounterModule()
    while "guichet" not in site.getId():
      site = site.getParentValue()
    counter = counter_module.newContent(id=id, site_value=site)
    # open it
    counter.open()

  def closeCounterDate(self, id):
    """
    close the counter date
    """
    module = self.getCounterDateModule()
    counter_date = module[id]
    counter_date.close()

  def initDefaultVariable(self):
    """
    init some default variable use in all test
    """
    # the erp5 site
    self.portal = self.getPortal()

    # Make sure movement table does not exist
    sql_connection = self.getSQLConnection()
    sql_connection.manage_test("DROP TABLE IF EXISTS movement")
    # Delete also all ZSQL Methods related to movement table
    catalog = self.portal.portal_catalog.getSQLCatalog()
    for zsql in ["z0_drop_movement", "z0_uncatalog_movement",
                 "z_catalog_movement_list", "z_create_movement", ]:
      if catalog._getOb(zsql, None) is not None:
        catalog.manage_delObjects(ids=[zsql])

    # Update properties of catalog
    sql_catalog_object_list = list(catalog.sql_catalog_object_list)
    sql_uncatalog_object = list(catalog.sql_uncatalog_object)
    sql_clear_catalog = list(catalog.sql_clear_catalog)
    sql_search_tables = list(catalog.sql_search_tables)

    if "z_catalog_movement_list" in sql_catalog_object_list:
      sql_catalog_object_list.remove("z_catalog_movement_list")
    if "z0_uncatalog_movement" in sql_uncatalog_object:
      sql_uncatalog_object.remove("z0_uncatalog_movement")
    if "z0_drop_movement" in sql_clear_catalog:
      sql_clear_catalog.remove("z0_drop_movement")
    if "z_create_movement" in sql_clear_catalog:
      sql_clear_catalog.remove("z_create_movement")
    if "movement" in sql_search_tables:
      sql_search_tables.remove("movement")

    catalog.sql_catalog_object_list = tuple(sql_catalog_object_list)
    catalog.sql_uncatalog_object = tuple(sql_uncatalog_object)
    catalog.sql_clear_catalog = tuple(sql_clear_catalog)
    catalog.sql_search_tables = tuple(sql_search_tables)

    # the default currency for the site
    if not self.portal.hasProperty('reference_currency_id'):
      self.portal.manage_addProperty('reference_currency_id', 'EUR', type='string')
    # not working days
    if not self.portal.hasProperty('not_working_days'):
      self.portal.manage_addProperty('not_working_days', '', type='string')
    else:
      self.portal.not_working_days = ''
    setattr(self.portal, 'functionnal_test_mode', 1)
    # the person module
    self.person_module = self.getPersonModule()
    # the organisation module
    self.organisation_module = self.getOrganisationModule()
    # the category tool
    self.category_tool = self.getCategoryTool()
    # the workflow tool
    self.workflow_tool = self.getWorkflowTool()
    # nb use for bank account inventory
    self.account_inventory_number = 0
    # the cash inventory module
    self.cash_inventory_module = self.getCashInventoryModule()
    # the bank inventory module
    self.bank_account_inventory_module = self.getBankAccountInventoryModule()
    # simulation tool
    self.simulation_tool = self.getSimulationTool()
    # get the currency module
    self.currency_module = self.getCurrencyModule()
    self.checkbook_model_module = self.portal.checkbook_model_module
    # a default date
    self.date = DateTime()

  def setDocumentSourceReference(self, doc):
    """
    Compute and set the source reference for a document
    """
    # document must have a date defined
    if doc.getStartDate() is None:
      doc.edit(start_date=DateTime())
    # call script to set source reference
    doc.Baobab_getUniqueReference()


  def createPerson(self, id, first_name, last_name, site=None):
    """
    Create a person
    """
    if site is None:
      site = "testsite/paris"
    return self.person_module.newContent(id = id,
                                         portal_type = 'Person',
                                         first_name = first_name,
                                         last_name = last_name,
                                         site=site)


  def createBankAccount(self, person, account_id, currency, amount, inv_date=None, **kw):
    """
    Create and initialize a bank account for a person
    """
    if not kw.has_key('bank_country_code'):
      kw['bank_country_code'] = 'k'
    if not kw.has_key('bank_code'):
      kw['bank_code'] = '1234'
    if not kw.has_key('branch'):
      kw['branch'] = '12345'
    if not kw.has_key('bank_account_number'):
      kw['bank_account_number'] = '123456789012'
    if not kw.has_key('bank_account_key'):
      kw['bank_account_key'] = '12'
    if not kw.has_key('internal_bank_account_number'):
      kw['internal_bank_account_number'] = 'k%11s' % (12341234512 + self.account_inventory_number, )
      #kw['internal_bank_account_number'] = 'k12341234512'
    bank_account = person.newContent(id = account_id,
                                     portal_type = 'Bank Account',
                                     price_currency_value = currency,
                                     **kw)
    if not kw.has_key('reference') and bank_account.getReference() is None:
      # If there is no automatic getter-time calculation of the reference and
      # no reference has been explicitely set, generate one composed of all
      # bank codes and a static prefix - to avoid collisions as much as
      # possible.
      bank_account.edit(reference='ref_%s%s%s%s%s' % (kw['bank_country_code'],
        kw['bank_code'], kw['branch'], kw['bank_account_number'],
        kw['bank_account_key']))

    # validate this bank account for payment
    bank_account.validate()
    if amount:
      # we need to put some money on this bank account
      self.createBankAccountInventory(bank_account, amount, inv_date=inv_date)
    return bank_account

  def createBankAccountInventory(self, bank_account, amount, inv_date=None):
    if not hasattr(self, 'bank_account_inventory'):
      self.bank_account_inventory = self.bank_account_inventory_module.newContent(id='account_inventory_group',
                                                                                portal_type='Bank Account Inventory Group',
                                                                                site_value=self.testsite,
                                                                                stop_date=DateTime().Date())

    if inv_date is None:
      inv_date = DateTime()
    inventory = self.bank_account_inventory.newContent(id=bank_account.getInternalBankAccountNumber(),
                                                       portal_type='Bank Account Inventory',
                                                       destination_payment_value=bank_account,
                                                       stop_date=inv_date)
    account_inventory_line_id = 'account_inventory_line_%s' % (self.account_inventory_number, )
    inventory_line = inventory.newContent(id=account_inventory_line_id,
                                          portal_type='Bank Account Inventory Line',
                                          resource_value=bank_account.getPriceCurrencyValue(),
                                          quantity=amount)


    # deliver the inventory
    if inventory.getSimulationState()!='delivered':
      inventory.deliver()

    self.account_inventory_number += 1

  def createCheckbook(self, id, vault, bank_account, min, max, date=None):
    """
    Create a checkbook for the given bank account
    """
    if date is None:
      date = DateTime().Date()
    return self.checkbook_module.newContent(
        id=id,
        portal_type='Checkbook',
        destination_value=vault,
        destination_payment_value=bank_account,
        reference_range_min=min,
        reference_range_max=max,
        start_date=date,
    )

  def createCheckbookModel(self, id, check_model, reference=None,
          unique_per_account=True):
    """
    Create a checkbook for the given bank account
    with 3 variations
    """
    model =  self.checkbook_model_module.newContent(
        id=id,
        portal_type='Checkbook Model',
        title='Generic',
        account_number_enabled=True,
        reference=reference,
        composition=check_model.getRelativeUrl(),
        unique_per_account=unique_per_account,
    )
    model.newContent(id='variant_1', portal_type='Checkbook Model Check Amount Variation',
                     quantity=50, title='50')
    model.newContent(id='variant_2', portal_type='Checkbook Model Check Amount Variation',
                     quantity=100, title='100')
    model.newContent(id='variant_3', portal_type='Checkbook Model Check Amount Variation',
                     quantity=200, title='200')
    return model


  def createCheckModel(self, id, reference='CCOP', unique_per_account=True):
    """
    Create a checkbook for the given bank account
    """
    return self.checkbook_model_module.newContent(
        id=id,
        portal_type='Check Model',
        title='Check',
        reference=reference,
        account_number_enabled=True,
        unique_per_account=unique_per_account,
    )

  def createCheckAndCheckbookModel(self):
    """
    create default checkbook and check models
    """
    self.check_model = self.createCheckModel(id='check_model')
    self.check_model_1 = self.check_model
    self.check_model_2 = self.createCheckModel(id='check_model_2', reference='CCCO')
    self.check_model_1_2 = self.createCheckModel(
        id='check_model_1_2',
        reference='CCOP',
        unique_per_account=False,
    )
    self.check_model_2_2 = self.createCheckModel(
        id='check_model_2_2',
        reference='CCCO',
        unique_per_account=False,
    )
    self.checkbook_model = self.createCheckbookModel(
           id='checkbook_model', check_model=self.check_model)
    self.checkbook_model_1 = self.checkbook_model
    self.checkbook_model_2 = self.createCheckbookModel(
           id='checkbook_model_2', check_model=self.check_model_2)
    self.checkbook_model_1_2 = self.createCheckbookModel(
           id='checkbook_model_1_2',
           check_model=self.check_model_1_2,
           unique_per_account=False,
    )
    self.checkbook_model_2_2 = self.createCheckbookModel(
           id='checkbook_model_2_2',
           check_model=self.check_model_2_2,
           unique_per_account=False,
    )

  def createCheck(self, id, reference, checkbook, bank_account=None,
                        resource_value=None, destination_value=None):
    """
    Create Check in a checkbook
    """
    check = checkbook.newContent(id=id,
                                 portal_type = 'Check',
                                 reference=reference,
                                 destination_payment_value=bank_account,
                                 resource_value=resource_value,
                                 destination_value=destination_value
                                )

    # mark the check as issued
    check.confirm()
    return check

  def createTravelerCheckModel(self, id):
    """
    Create a checkbook for the given bank account
    """
    model = self.checkbook_model_module.newContent(id = id,
                                            title = 'USD Traveler Check',
                                            portal_type = 'Check Model',
                                            fixed_price = 1
                                            )
    variation = model.newContent(id='variant_1',
                                 portal_type='Check Model Type Variation',
                                 price=50)
    model.setPriceCurrency(self.currency_2.getRelativeUrl())
    return model

  def createCashContainer(self, document, container_portal_type, global_dict, line_list, delivery_line_type='Cash Delivery Line'):
    """
    Create a cash container
    global_dict has keys :
      emission_letter, variation, cash_status, resource
    line_list is a list od dict with keys:
      reference, range_start, range_stop, quantity, aggregate
    """
    # Container Creation
    base_list = ('emission_letter', 'variation', 'cash_status')
    category_list =  ('emission_letter/'+global_dict['emission_letter'], 'variation/'+global_dict['variation'], 'cash_status/'+global_dict['cash_status'] )
    resource_total_quantity = 0
    # create cash container
    for line_dict in line_list:
      movement_container = document.newContent(portal_type          = container_portal_type
                                               , reindex_object     = 1
                                               , reference                 = line_dict['reference']
                                               , cash_number_range_start   = line_dict['range_start']
                                               , cash_number_range_stop    = line_dict['range_stop']
                                               )
      if line_dict.has_key('aggregate'):
        movement_container.setAggregateValueList([line_dict['aggregate'], ])
      # create a cash container line
      container_line = movement_container.newContent(portal_type      = 'Container Line'
                                                     , reindex_object = 1
                                                     , resource_value = global_dict['resource']
                                                     , quantity       = line_dict['quantity']
                                                     )
      container_line.setResourceValue(global_dict['resource'])
      container_line.setVariationCategoryList(category_list)
      container_line.updateCellRange(script_id='CashDetail_asCellRange', base_id="movement")
      for key in container_line.getCellKeyList(base_id='movement'):
        if isSameSet(key, category_list):
          cell = container_line.newCell(*key)
          cell.setCategoryList(category_list)
          cell.setQuantity(line_dict['quantity'])
          cell.setMappedValuePropertyList(['quantity', 'price'])
          cell.setMembershipCriterionBaseCategoryList(base_list)
          cell.setMembershipCriterionCategoryList(category_list)
          cell.edit(force_update = 1,
                    price = container_line.getResourceValue().getBasePrice())


      resource_total_quantity += line_dict['quantity']
    # create cash delivery movement
    movement_line = document.newContent(id               = "movement"
                                        , portal_type    = delivery_line_type
                                        , resource_value = global_dict['resource']
                                        , quantity_unit_value = self.getCategoryTool().quantity_unit.unit
                                        )
    movement_line.setVariationBaseCategoryList(base_list)
    movement_line.setVariationCategoryList(category_list)
    movement_line.updateCellRange(script_id="CashDetail_asCellRange", base_id="movement")
    for key in movement_line.getCellKeyList(base_id='movement'):
      if isSameSet(key, category_list):
        cell = movement_line.newCell(*key)
        cell.setCategoryList(category_list)
        cell.setQuantity(resource_total_quantity)
        cell.setMappedValuePropertyList(['quantity', 'price'])
        cell.setMembershipCriterionBaseCategoryList(base_list)
        cell.setMembershipCriterionCategoryList(category_list)
        cell.edit(force_update = 1,
                  price = movement_line.getResourceValue().getBasePrice())


  def createCashInventory(self, source, destination, currency, line_list=[], extra_id='',
                          reset_quantity=0, start_date=None, quantity_factor=1):
    """
    Create a cash inventory group
    """
    # we need to have a unique inventory group id by destination

    inventory_group_id = '%s%s' % (destination.getUid(), extra_id)
    if start_date is None:
      start_date = DateTime()-1
    if not hasattr(self, inventory_group_id):
      inventory_group =  self.cash_inventory_module.newContent(id=inventory_group_id,
                                                               portal_type='Cash Inventory Group',
                                                               destination_value=destination,
                                                               start_date=start_date)
      setattr(self, inventory_group_id, inventory_group)
    else:
      inventory_group = getattr(self, inventory_group_id)

    # get/create the inventory based on currency
    inventory_id = 'inventory_%s_%s' % (inventory_group.getUid(), currency.getId())
    if not hasattr(self, inventory_id):
      inventory = inventory_group.newContent(id=inventory_id,
                                             portal_type='Cash Inventory',
                                             price_currency_value=currency)
      setattr(self, inventory_id, inventory)
    else:
      inventory = getattr(self, inventory_id)

    # line data are given by a list of dict, dicts must have this key :
    # id :  line id
    # resource : banknote or coin
    # variation_id : list of variation id
    # variation_value : list of variation value (must be in the same order as variation_id
    # quantity
    for line in line_list:
      variation_list = line.get('variation_list', None)
      self.addCashLineToDelivery(inventory,
                                 line['id'],
                                 "Cash Inventory Line",
                                 line['resource'],
                                 line['variation_id'],
                                 line['variation_value'],
                                 line['quantity'],
                                 variation_list=variation_list,
                                 reset_quantity=reset_quantity,
                                 quantity_factor=quantity_factor)
    # deliver the inventory
    if inventory.getSimulationState()!='delivered':
      inventory.deliver()
    return inventory_group


  def addCashLineToDelivery(self, delivery_object, line_id, line_portal_type, resource_object,
          variation_base_category_list, variation_category_list, resource_quantity_dict,
          variation_list=None, reset_quantity=0, quantity_factor=1):
    """
    Add a cash line to a delivery
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
    if variation_list is None:
      variation_list = self.variation_list
    for variation in variation_list:
      v1, v2 = variation_category_list[:2]
      cell = line.getCell(v1, variation, v2)
      if cell is not None:
        quantity = resource_quantity_dict[variation]
        if reset_quantity:
          quantity = 0
        cell.setQuantity(quantity*quantity_factor)


  def checkResourceCreated(self):
    """
    Check that all have been create after setup
    """
    # check that Categories were created
    self.assertEqual(self.paris.getPortalType(), 'Category')

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

  def resetInventory(self,
               sequence=None, line_list=None, sequence_list=None, extra_id=None,
               destination=None, currency=None, start_date=None, **kwd):
    """
    Make sure we can not close the counter date
    when there is still some operations remaining
    """
    if extra_id is not None:
      extra_id = '_reset_%s' % extra_id
    else:
      extra_id = '_reset'
    # Before the test, we need to input the inventory
    self.createCashInventory(source=None, destination=destination, currency=currency,
                             line_list=line_list, extra_id=extra_id, reset_quantity=1,
                             start_date=start_date)

  def stepDeleteResetInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Make sure we can not close the counter date
    when there is still some operations remaining
    """
    inventory_module = self.getPortal().cash_inventory_module
    to_delete_id_list = [x for x in inventory_module.objectIds()
                         if x.find('reset')>=0]
    inventory_module.manage_delObjects(ids=to_delete_id_list)

