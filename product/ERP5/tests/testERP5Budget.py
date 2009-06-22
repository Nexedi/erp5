##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
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

import unittest

import transaction
from zLOG import LOG
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.Utils import convertToUpperCase



class TestBudget(ERP5TypeTestCase):
  """
    ERP5 Budget related tests. For the moment every assignment of budget
    related features are in Budget module, as well as the predicates to test
    the accounting operations. These are packaged in the erp5_budget business
    template.
  """

  # pseudo constants
  RUN_ALL_TEST = 1
  QUIET = 0

  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "ERP5 Budget"

  def getBusinessTemplateList(self):
    """
      Return the list of required business templates.
    """
    return ('erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_accounting',
            'erp5_invoicing', 'erp5_simplified_invoicing', 'erp5_budget')

  def login(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Create a new manager user and login.
    """
    user_name = 'maurice'
    user_folder = self.getPortal().acl_users
    user_folder._doAddUser(user_name, '', ['Manager', 'Owner', 'Assignor',
      'Assignee', 'Author'], [])
    user = user_folder.getUserById(user_name).__of__(user_folder)
    newSecurityManager(None, user)

  def stepCheckBudgetTransactionDrafted(self,budget_transaction,
      sequence=None, sequence_list=None, **kw):
    self.assertEquals('draft', budget_transaction.getSimulationState())


  def stepCheckBudgetTransactionDelivered(self,budget_transaction,
      sequence=None, sequence_list=None, **kw):
    self.assertEquals('delivered', budget_transaction.getSimulationState())

  def stepDeliverBudgetTransaction(self,budget_transaction, sequence=None,
      sequence_list=None, **kw):
    self.portal_workflow.doActionFor(budget_transaction,'deliver_action',
        wf_id='budget_transaction_workflow')


  def stepDeliverAccountingTransaction(self,accounting_transaction,
      sequence=None, sequence_list=None, **kw):
    self.portal_workflow.doActionFor(accounting_transaction,'deliver_action',
        wf_id='accounting_workflow')

  def stepCheckAccountingTransactionDelivered(self,accounting_transaction,
      sequence=None, sequence_list=None, **kw):
    self.assertEquals('delivered',
        accounting_transaction.getSimulationState())

  def stepPlanAccountingTransaction(self,accounting_transaction,
      sequence=None, sequence_list=None, **kw):
    self.portal_workflow.doActionFor(accounting_transaction,'plan_action',
        wf_id='accounting_workflow')

  def stepCheckAccountingTransactionPlanned(self,accounting_transaction,
      sequence=None, sequence_list=None, **kw):
    self.assertEquals('planned', accounting_transaction.getSimulationState())

  def stepStopAccountingTransaction(self,accounting_transaction,
      sequence=None, sequence_list=None, **kw):
    self.portal_workflow.doActionFor(accounting_transaction,'stop_action',
        wf_id='accounting_workflow')

  def stepCheckAccountingTransactionStopped(self,accounting_transaction,
      sequence=None, sequence_list=None, **kw):
    self.assertEquals('stopped', accounting_transaction.getSimulationState())

  def stepConfirmAccountingTransaction(self, accounting_transaction,
      sequence=None, sequence_list=None, **kw):
    self.portal_workflow.doActionFor(accounting_transaction,'confirm_action',
        wf_id='accounting_workflow')

  def stepCheckAccountingTransactionConfirmed(self,accounting_transaction,
      sequence=None, sequence_list=None, **kw):
    self.assertEquals('confirmed',
        accounting_transaction.getSimulationState())


  def afterSetUp(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Initialize the ERP5 site.
    """
    self.login()
    self.portal         = self.getPortal()
    self.portal_catalog = self.getCatalogTool()
    self.portal_categories = self.getCategoryTool()
    self.portal_workflow = self.getWorkflowTool()
    self.createCategories()
    # Must add some accounts, accounting transactions, budget and budget
    # transaction, etc.
    account_module = self.getAccountModule()
    accounting_module = self.getAccountingModule()
    self.currency_module = self.getCurrencyModule()
    self.organisation_module = self.getOrganisationModule()
    budget_module = self.getBudgetModule()
    budget_transaction_module  = self.getBudgetTransactionModule()
    self.getAccountingModule().manage_addLocalRoles('maurice',
        ('Assignor','Assignee','Manager','Owner',))
    # flush activities
    transaction.commit()
    self.tic()
    # When using light install, only base categories are created
    if len(self.portal_categories.region.contentValues()) == 0 :
      o = self.portal_categories.region.newContent(portal_type='Category',
          id='europe')
      o = o.newContent(portal_type='Category', id='west')
      o.newContent(portal_type='Category', id='france')

    # If currency_module/XOF already exists, it means that the afterSetUp
    # actions were already commited. Then, we just need to link to them.
    old_eur = getattr( self.getCurrencyModule(), 'EUR', None)
    # Create some currencies
    if old_eur is None :
      eur = self.getCurrencyModule().newContent(id='EUR', title='Euros',
          portal_type='Currency')

    # Create some organisations
    old_organisation = getattr( self.organisation_module, 'world_company',
        None)
    if old_organisation is None:
      self.organisation0 = self.organisation_module.newContent(
          id='world_company', title='World Company Inc.',
          portal_type='Organisation')
      self.organisation0.newContent(id='default_address',
          portal_type='Address', region='europe/west/france')
    old_nexedi = getattr( self.organisation_module, 'nexedi', None)
    if old_nexedi is None:
      self.organisation1 = self.organisation_module.newContent(id='nexedi',
          title='Nexedi', portal_type='Organisation')
      self.organisation1.newContent(id='default_address',
          portal_type='Address', region='europe/west/france')
    old_client1 = getattr( self.organisation_module, 'client1', None)
    if old_client1 is None:
      self.organisation2 = self.organisation_module.newContent(id='client1',
          title='Client1', portal_type='Organisation')
      self.organisation2.newContent(id='default_address',
          portal_type='Address', region='europe/west/france')

    # Create some accounts
    old_accounts = getattr( account_module, 'prestation_service', None)
    if old_accounts is None:
      account_module.newContent(id='prestation_service',
          title='prestation_service', portal_type='Account',
          financial_section='actif/actif_circulant')
      account_module.newContent(id='creance_client', title='creance_client',
          portal_type='Account',
          financial_section='actif/actif_circulant/caisse')
      account_module.newContent(id='tva_collectee_196',
          title='tva_collectee_196', portal_type='Account',
          financial_section='actif/actif_circulant/caisse')
      account_module.newContent(id='account1', title='Account1',
          portal_type='Account',
          financial_section='actif/actif_circulant/caisse')
      account_module.newContent(id='account2', title='Account2',
          portal_type='Account',
          financial_section='actif/actif_immobilise/immobilisations_financieres')
      account_module.newContent(id='account3', title='Account3',
          portal_type='Account',
          financial_section='actif/actif_immobilise/immobilisations_financieres')
      account_module.newContent(id='account4', title='Account4',
          portal_type='Account',
          financial_section='actif/actif_immobilise/immobilisations_financieres')

    # Open accounts
    for account in account_module.objectValues(portal_type='Account'):
      account.validate()

    # Create some accounting transactions
    self.accounting_transaction1 = accounting_module.newContent(
        portal_type='Accounting Transaction',title='Accounting 1',
        source_section='organisation_module/world_company',
        destination_section='organisation_module/client1',
        start_date='2005/08/22 18:06:26.388 GMT-4',
        resource='currency_module/EUR', source_function='function/hq')
    self.accounting_transaction1.newContent(
        portal_type='Accounting Transaction Line',
        source_section='organisation_module/world_company',
        resource='currency_module/EUR', source_debit='2000.0',
        source='account_module/account1')
    self.accounting_transaction1.newContent(
        portal_type='Accounting Transaction Line',
        source_section='organisation_module/world_company',
        resource='currency_module/EUR', source_credit='2000.0',
        source='account_module/account2')

    self.accounting_transaction2 = accounting_module.newContent(
        portal_type='Accounting Transaction',title='Accounting 2',
        source_section='organisation_module/world_company',
        destination_section='organisation_module/client1',
        start_date='2005/08/22 18:06:26.388 GMT-4',
        resource='currency_module/EUR', source_function='function/hq')
    self.accounting_transaction2.newContent(
        portal_type='Accounting Transaction Line',
        source_section='organisation_module/world_company',
        resource='currency_module/EUR', source_debit='100000.0',
        source='account_module/account1')
    self.accounting_transaction2.newContent(
        portal_type='Accounting Transaction Line',
        source_section='organisation_module/world_company',
        resource='currency_module/EUR', source_credit='100000.0',
        source='account_module/account4')

    id_list = []
    for objects in self.accounting_transaction1.getPortalObject().\
        budget_module.objectValues():
      id_list.append(objects.getId())
    self.accounting_transaction1.budget_module.manage_delObjects(id_list)

    id_list = []
    for objects in self.accounting_transaction1.getPortalObject().\
        budget_transaction_module.objectValues():
      id_list.append(objects.getId())
    self.accounting_transaction1.budget_transaction_module.\
        manage_delObjects(id_list)


    budget1 = budget_module.newContent(
        portal_type='Budget', title='Budget initial ', group='world_company',
        start_date='2005/01/01 18:06:26.388 GMT-4',
        stop_date='2005/12/31 18:06:26.388 GMT-4')
    budget_line1 = budget1.newContent(
        portal_type='Budget Line', group='world_company',
        resource='currency_module/EUR', title='Line 1 of budget')
    budget_cell1 = budget_line1.newContent(
        id='cell_0_0_1', portal_type='Budget Cell',
        mapped_value_property_list=('max_quantity'),
        membership_criterion_category_list=[
          'financial_section/actif/actif_circulant/caisse', 'function/hq',
          'group/world_company'],
        membership_criterion_base_category_list=[ 'financial_section',
          'function', 'group'])
    budget_cell1.setQuantity(3000.0)

    budget_cell2 = budget_line1.newContent(
        id='cell_0_1_0', portal_type='Budget Cell',
        mapped_value_property_list=('max_quantity'),
        membership_criterion_category_list=[
          'financial_section/actif/actif_immobilise/immobilisations_financieres',
          'function/hq', 'group/world_company'],
        membership_criterion_base_category_list=[ 'financial_section',
          'function', 'group'])
    budget_cell2.setQuantity(1000.0)

    budget_transfert1 = budget1.newContent(
        portal_type='Budget Transfer Line',
        source=budget_cell1.getRelativeUrl(), resource='currency_module/EUR',
        destination=budget_cell2.getRelativeUrl(), quantity=500.0)

    self.budget_transaction1 = budget_transaction_module.newContent(
        portal_type='Budget Transaction',
        source=budget_cell1.getRelativeUrl(),
        destination=budget_cell2.getRelativeUrl(),
        quantity=25.0,group='world_company',
        stop_date='2005/05/01 18:06:26.388 GMT-4')

    self.budget_transaction2 = budget_transaction_module.newContent(
        portal_type='Budget Transaction',
        source=budget_cell2.getRelativeUrl(),
        destination=budget_cell1.getRelativeUrl(),
        quantity=25.0,group='world_company',
        stop_date='2005/05/01 18:06:26.388 GMT-4')

    # flush activities
    transaction.commit()
    self.tic()

  def getAccountModule(self):
    return getattr(self.getPortal(), 'account_module', None)

  def getAccountingModule(self):
    return getattr(self.getPortal(), 'accounting_module', None)

  def getBudgetModule(self):
    return getattr(self.getPortal(), 'budget_module', None)

  def getBudgetTransactionModule(self):
    return getattr(self.getPortal(), 'budget_transaction_module', None)

  def createCategories(self):
    """
      Create some categories for testing.
    """
    self.category_list = [

        # Function categories
         {'path' : 'function/hq'
          ,'title': 'HQ'
          }
        , {'path' : 'function/warehouse'
          ,'title': 'Warehouse'
          }
        , {'path' : 'function/research_center'
          ,'title': 'Research Center'
          }

        # Group categories
        , {'path' : 'group/nexedi'
          ,'title': 'Nexedi'
          }
        , {'path' : 'group/world_company'
          ,'title': 'World Company Inc.'
          }
        # some financial sections
        , {'path' : 'financial_section/actif/actif_circulant'
          ,'title': 'Actif Circulant'
          }
        , {'path' : 'financial_section/actif/actif_circulant/caisse'
          ,'title': 'Caisse'
          }
        , {'path' : 'financial_section/actif/actif_immobilise/immobilisations_financieres'
          ,'title': 'Immobilisations Financieres'
          }

        ]

    # Create categories
    # Note : this code was taken from the CategoryTool_importCategoryFile
    # python script (packaged in erp5_core).
    for category in self.category_list:
      keys = category.keys()
      if 'path' in keys:
        base_path_obj = self.portal_categories
        is_base_category = True
        for category_id in category['path'].split('/'):
          # The current category is not existing
          if category_id not in base_path_obj.contentIds():
            # Create the category
            if is_base_category:
              category_type = 'Base Category'
            else:
              category_type = 'Category'
            base_path_obj.newContent( portal_type       = category_type
                                    , id                = category_id
                                    , immediate_reindex = 1
                                    )
          base_path_obj = base_path_obj[category_id]
          is_base_category = False
        new_category = base_path_obj

        # Set the category properties
        for key in keys:
          if key != 'path':
            method_id = "set" + convertToUpperCase(key)
            value = category[key]
            if value not in ('', None):
              if hasattr(new_category, method_id):
                method = getattr(new_category, method_id)
                method(value.encode('UTF-8'))




  ##################################
  ##  Basic steps
  ##################################

#  def createOrganisation(self, sequence=None, sequence_list=None, **kw):
#    """
#      Create an organisation
#    """
#    portal_type = 'Organisation'
#    organisation_module = self.portal.getDefaultModule(portal_type)
#    self.organisation = organisation_module.newContent(
#    portal_type=portal_type, group='group/world_company',
#    immediate_reindex=1)

  ### TODO: write here basic steps


  ##################################
  ##  Tests
  ##################################

  def test_01_HasEverything(self, quiet=0, run=RUN_ALL_TEST):
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Has Everything ')
      LOG('Testing... ',0,'testHasEverything')
    self.failUnless(self.getCategoryTool() != None)
    self.failUnless(self.getAccountModule() != None)
    self.failUnless(self.getAccountingModule() != None)
    self.failUnless(self.getOrganisationModule() != None)
    self.failUnless(self.getCurrencyModule() != None)
    self.failUnless(self.getBudgetModule() != None)
    self.failUnless(self.getBudgetTransactionModule() != None)

  def test_02_HasBudgetCells(self, quiet=0, run=RUN_ALL_TEST):
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Has Budget Cells ')
      LOG('Testing... ',0,'testHasBudgetCells')
    message = ""
    len_cells = 0
    for objects in self.getBudgetModule().budget_module.objectValues():
      if objects.getPortalType() == 'Budget':
        for obj_line in objects.objectValues():
          if obj_line.getPortalType() == 'Budget Line':
            for obj in obj_line.objectValues():
              len_cells += 1
              financial_section = obj.getMembershipCriterionCategoryList()[0]
              function = obj.getMembershipCriterionCategoryList()[1]
              group = obj.getMembershipCriterionCategoryList()[2]
              quantity = obj.getQuantity()
              message += str(obj.getId())+': '+str(financial_section)+', ' \
                  +str(function)+', '+str(group)+', '+str(quantity)+'\n'
    if len_cells == 0:
       message = "could not create budget cells"
    ZopeTestCase._print('\n%s ' % message)
    LOG('Testing values... ',0,message)
    self.failUnless(len_cells != 0)


  def test_03_Enough_budget(self, quiet=0, run=RUN_ALL_TEST):
    """
    Try to validate transactions of accountings if there is enough budget
    """
    if not run: return
    if not quiet:
      message = 'Test if there is enough budget before validating an '\
          + 'accounting transaction'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    self.stepConfirmAccountingTransaction(self.accounting_transaction1)
    message = str(self.accounting_transaction1.getSimulationState())
    ZopeTestCase._print('\n%s ' % message)
    LOG('Testing simulation state accounting transaction 1... ',0,message)
#     if self.stepCheckAccountingTransactionStopped(self.accounting_transaction1):
#       message = 'There is enough budget, so this transaction will be validated'
#       ZopeTestCase._print('\n%s ' % message)
#       LOG('Testing accounting transaction 1... ',0,message)
#     else:
#       message = 'There is not enough budget, so this transaction will not be
#       validated'
#       ZopeTestCase._print('\n%s ' % message)
#       LOG('Testing accounting transaction 1... ',0,message)

    self.stepConfirmAccountingTransaction(self.accounting_transaction2)
    message = str(self.accounting_transaction2.getSimulationState())
    ZopeTestCase._print('\n%s ' % message)
    LOG('Testing simulation state accounting transaction 2... ',0,message)
#     if self.stepCheckAccountingTransactionStopped(self.accounting_transaction2):
#       message = 'There is enough budget, so this transaction will be validated'
#       ZopeTestCase._print('\n%s ' % message)
#       LOG('Testing accounting transaction 2... ',0,message)
#     else:
#       message = 'There is not enough budget, so this transaction will not be
#       validated'
#       ZopeTestCase._print('\n%s ' % message)
#       LOG('Testing accounting transaction 2... ',0,message)


  # jerome: disabled this test for now, it was from the first budget
  # implementation, and this is not covered by the new version.
  def XXXtest_04_Transaction_of_budget(self, quiet=0, run=RUN_ALL_TEST):
    """
    Try to validate budget trasaction if the transfert is authorized
    """
    if not run: return
    if not quiet:
      message = 'Test if the transaction of budget is authorized'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    self.stepDeliverBudgetTransaction(self.budget_transaction1)
    message = str(self.budget_transaction1.getSimulationState())
    ZopeTestCase._print('\n%s ' % message)
    LOG('Testing simulation state budet 1... ',0,message)
    if self.stepCheckBudgetTransactionDelivered(self.budget_transaction1):
      message = 'This transaction is possible so we can validate it'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing budget transaction 1... ',0,message)
    else:
      message = 'This transaction is not possible because it is not authorized'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing budget transaction 1... ',0,message)

    self.stepDeliverBudgetTransaction(self.budget_transaction2)
    message = str(self.budget_transaction2.getSimulationState())
    ZopeTestCase._print('\n%s ' % message)
    LOG('Testing simulation state budet 2... ',0,message)
    if self.stepCheckBudgetTransactionDrafted(self.budget_transaction2):
      message = 'This transaction is possible so we can validate it'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing budget transaction 2... ',0,message)
    else:
      message = 'This transaction is not possible because it is not authorized'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing budget transaction 2... ',0,message)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestBudget))
  return suite
