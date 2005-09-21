# 2005-02-22 Alex
# - added getCurrentInventory and getFutureInventory to getSource and getDestination

from Testing.ZopeTestCase.PortalTestCase import PortalTestCase
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.DCWorkflow.DCWorkflow import Unauthorized
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager

from zLOG import LOG
import AccessControl
import os
import sys

class TestERP5BankingCashTransfer(ERP5TypeTestCase):
  """
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

  def getTitle(self):
    """
    Return the title
    """
    return "ERP5BankingCashTransfer"

  def getBusinessTemplateList(self):
    """
    Return the list of business templates we need
    """
    return ('erp5_trade', 'erp5_banking_core-0.1', 'erp5_banking_cash_transfer-0.1',)
    return ('erp5_accounting', 'erp5_banking_core-0.1', 'erp5_banking_cash_transfer-0.1',)

  def enableLightInstall(self):
    """
    Return if we should do a light install (1) or not (0)
    """
    return 1

  def enableActivityTool(self):
    """
    Return if we should create (1) or not (0) an activity tool
    """
    return 1

  def getUserFolder(self):
    return getattr(self.getPortal(), 'acl_users', None)
  def getPersonModule(self):
    return getattr(self.getPortal(), 'person', None)
  def getOrganisationModule(self):
    return getattr(self.getPortal(), 'organisation', None)
  def getCurrencyCashModule(self):
    return getattr(self.getPortal(), 'currency_cash_module', None)
  def getCashTransferModule(self):
    return getattr(self.getPortal(), 'cash_transfer_module', None)
  def getInternalPackingListModule(self):
    return getattr(self.getPortal(), 'internal_packing_list_module', None)
  def getCurrencyModule(self):
    return getattr(self.getPortal(), 'currency', None)
  def getCategoryTool(self):
    return getattr(self.getPortal(), 'portal_categories', None)
  def getWorkflowTool(self):
    return getattr(self.getPortal(), 'portal_workflow', None)
  def getSimulationTool(self):
    return getattr(self.getPortal(), 'portal_simulation', None)

  def createCategories(self):
    """
      Create some categories for testing.
    """
    self.category_list = [
                         # Function categories
                           {'path'        : 'function/banking'
                           ,'title'       : 'Banking Function'
                           ,'codification': 'BNK'
                           }
                         , {'path'        : 'function/banking/gestionnaire_caisse_courante'
                           ,'title'       : 'Gestionnaire Caisse Courante'
                           ,'codification': 'CCO'
                           }
                         ]
    # Create categories
    # Note : this code was taken from the CategoryTool_importCategoryFile python
    #        script (packaged in erp5_core).
    for category in self.category_list:
      keys = category.keys()
      if 'path' in keys:
        base_path_obj = self.category_tool
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

  # Define which users will be created
  # 'user_name' : [['Global Role'], 'function', 'group', 'site']
  user_dict = {
      'user_1': [[], 'banking/caissier_principal', 'baobab', 'testsite'],
      'user_2': [[], 'banking/controleur_caisse', 'baobab', 'testsite'],
      'user_3': [[], 'banking/void_function', 'baobab', 'testsite'],
  }

  def afterSetUp(self):
    """
    """
    # Set variables
    self.portal = self.getPortal()
    self.cash_transfer_module = self.getCashTransferModule()
    self.user_folder = self.getUserFolder()
    self.person_folder = self.getPersonModule()
    self.organisation_folder = self.getOrganisationModule()
    self.category_tool = self.getCategoryTool()

    # Define static values (only use prime numbers to prevent confusions like 2 * 6 == 3 * 4)
    self.variation_list = ('variation/1992', 'variation/2003')
    self.quantity_10000 = {}
    self.quantity_10000[self.variation_list[0]] = 2
    self.quantity_10000[self.variation_list[1]] = 3
    self.quantity_200 = {}
    self.quantity_200[self.variation_list[0]] = 5
    self.quantity_200[self.variation_list[1]] = 7
    self.quantity_5000 = {}
    self.quantity_5000[self.variation_list[0]] = 11
    self.quantity_5000[self.variation_list[1]] = 13

    # login as manager for bootstrap
    self.user_folder.userFolderAddUser('manager', '', ['Manager'], [])
    self.login('manager')

    # Create Categories (vaults)
    #self.createCategories()
    # as local roles are defined in portal types as real categories, we will need to reproduce (or import) the real category tree
    self.function_base_category = getattr(self.category_tool, 'function')
    self.banking = self.function_base_category.newContent(id='banking', portal_type='Category', codification='BNK')
    self.caissier_principal = self.banking.newContent(id='caissier_principal', portal_type='Category', codification='CCP')
    self.controleur_caisse = self.banking.newContent(id='controleur_caisse', portal_type='Category', codification='CCT')
    self.void_function = self.banking.newContent(id='void_function', portal_type='Category', codification='VOID')

    self.gestionnaire_caisse_courante = self.banking.newContent(id='gestionnaire_caisse_courante', portal_type='Category', codification='CCO')
    self.gestionnaire_caveau = self.banking.newContent(id='gestionnaire_caveau', portal_type='Category', codification='CCV')
    self.caissier_particulier = self.banking.newContent(id='caissier_particulier', portal_type='Category', codification='CGU')

    self.group_base_category = getattr(self.category_tool, 'group')
    self.baobab = self.group_base_category.newContent(id='baobab', portal_type='Category', codification='BAOBAB')

    self.site_base_category = getattr(self.category_tool, 'site')
    self.testsite = self.site_base_category.newContent(id='testsite', portal_type='Category', codification='TEST')
    self.caisse_1 = self.testsite.newContent(id='caisse_1', portal_type='Category', codification='C1')
    self.caisse_2 = self.testsite.newContent(id='caisse_2', portal_type='Category', codification='C2')

    self.cash_status_base_category = getattr(self.category_tool, 'cash_status')
    self.cash_status_valid = self.cash_status_base_category.newContent(id='valid', portal_type='Category')

    self.emission_letter_base_category = getattr(self.category_tool, 'emission_letter')
    self.emission_letter_k = self.emission_letter_base_category.newContent(id='k', portal_type='Category')

    self.variation_base_category = getattr(self.category_tool, 'variation')
    self.variation_1992 = self.variation_base_category.newContent(id='1992', portal_type='Category')
    self.variation_2003 = self.variation_base_category.newContent(id='2003', portal_type='Category')

    self.variation_base_category = getattr(self.category_tool, 'quantity_unit')
    self.unit = self.variation_base_category.newContent(id='unit', title='Unit')

    # Create an Organisation that will be used for users assignment
    self.organisation = self.organisation_folder.newContent(id='baobab_org', portal_type='Organisation',
        function='banking', group='baobab',  site='testsite')

    # Create some users who will get different roles on the cash transfer
    for user_name, user_data in self.user_dict.items():
      person = self.person_folder.newContent(id=user_name, portal_type='Person')
      assignment = person.newContent(portal_type='Assignment', destination_value=self.organisation,
          function=user_data[1], group=user_data[2], site=user_data[3])
      self.user_folder.userFolderAddUser(user_name, '', user_data[0], [])
      # User assignment to groups is also required, and is taken care of by the assignment workflow
      assignment.open()

    # We must assign local roles to cash_transfer_module manually, as they are
    # not packed in Business Templates yet
    self.cash_transfer_module.manage_addLocalGroupRoles('CCP_BAOBAB_TEST', ('Author',))

    # Create a Currency
    self.currency_module = self.getCurrencyModule()
    self.currency_1 = self .currency_module.newContent(id='EUR', title='Euro')

    # Create Resources (Banknotes)
    self.currency_cash_module = self.getCurrencyCashModule()
    self.billet_10000 = self.currency_cash_module.newContent(id='billet_10000', portal_type='Banknote', base_price=10000, price_currency_value=self.currency_1, variation_list=('1992', '2003'), quantity_unit_value=self.unit)
    self.billet_5000 = self.currency_cash_module.newContent(id='billet_5000', portal_type='Banknote', base_price=5000, price_currency_value=self.currency_1, variation_list=('1992', '2003'), quantity_unit_value=self.unit)
    self.piece_200 = self.currency_cash_module.newContent(id='piece_200', portal_type='Coin', base_price=200, price_currency_value=self.currency_1, variation_list=('1992', '2003'), quantity_unit_value=self.unit)

    # Before the test, we need to create resources in the source
    # Using internal_packing_list from erp5_trade is the easiest
    self.portal.portal_delivery_type_list = list(self.portal.portal_delivery_type_list)
    self.portal.portal_delivery_type_list.append('Internal Packing List')
    self.portal.portal_delivery_type_list = tuple(self.portal.portal_delivery_type_list)
    self.portal.portal_delivery_movement_type_list = list(self.portal.portal_delivery_movement_type_list)
    self.portal.portal_delivery_movement_type_list.append('Internal Packing List Line')
    self.portal.portal_delivery_movement_type_list = tuple(self.portal.portal_delivery_movement_type_list)

    self.internal_packing_list_module = self.getInternalPackingListModule()
    self.internal_packing_list = self.internal_packing_list_module.newContent(id='packing_list_1', portal_type='Internal Packing List',
            source=None, destination_value=self.caisse_1)
    self.addCashLineToDelivery(self.internal_packing_list, 'delivery_init_1', 'Internal Packing List Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/k', 'cash_status/valid') + self.variation_list,
            self.quantity_10000)
    self.addCashLineToDelivery(self.internal_packing_list, 'delivery_init_2', 'Internal Packing List Line', self.piece_200,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/k', 'cash_status/valid') + self.variation_list,
            self.quantity_200)

    # Finally, login as user_1
    self.logout()
    self.login(name='user_1')

  def addCashLineToDelivery(self, delivery_object, line_id, line_portal_type, resource_object,
          variation_base_category_list, variation_category_list, resource_quantity_dict):
      """
      """
      base_id = 'movement'
      line_kwd = {'base_id':base_id}
      line = delivery_object.newContent(id=line_id, portal_type=line_portal_type,
              resource_value=resource_object, quantity_unit_value=self.unit)
      line.setVariationBaseCategoryList(variation_base_category_list)
      line.setVariationCategoryList(variation_category_list)
      line.updateCellRange(script_id='CashDetail_asCellRange', base_id=base_id)
      cell_range_key_list = line.getCellRangeKeyList(base_id=base_id)
      if cell_range_key_list <> [[None, None]] :
          for k in cell_range_key_list:
              category_list = filter(lambda k_item: k_item is not None, k)
              c = line.newCell(*k, **line_kwd)
              mapped_value_list = ['price', 'quantity']
              c.edit(mapped_value_property_list=mapped_value_list
                      ,force_update=1
                      ,membership_criterion_category_list=category_list
                      ,category_list=category_list
                      )
      for variation in self.variation_list:
          cell = line.getCell('emission_letter/k', variation, 'cash_status/valid')
          cell.setQuantity(resource_quantity_dict[variation])


  def stepTic(self, **kwd):
    """
    """
    self.tic()

  def stepFirstCheck(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or that were added by the business template and that we rely on are really here
    """
    # check that Categories were created
    self.assertEqual(self.caisse_1.getPortalType(), 'Category')
    self.assertEqual(self.caisse_2.getPortalType(), 'Category')
    # check that Resources were created
    self.assertEqual(self.billet_10000.getPortalType(), 'Banknote')
    self.assertEqual(self.billet_10000.getBasePrice(), 10000)
    self.assertEqual(self.billet_10000.getPriceCurrency(), 'currency/EUR')
    self.assertEqual(self.billet_10000.getVariationList(), ['1992', '2003'])

    self.assertEqual(self.billet_5000.getPortalType(), 'Banknote')
    self.assertEqual(self.billet_5000.getBasePrice(), 5000)
    self.assertEqual(self.billet_5000.getPriceCurrency(), 'currency/EUR')
    self.assertEqual(self.billet_5000.getVariationList(), ['1992', '2003'])

    self.assertEqual(self.piece_200.getPortalType(), 'Coin')
    self.assertEqual(self.piece_200.getBasePrice(), 200)
    self.assertEqual(self.piece_200.getPriceCurrency(), 'currency/EUR')
    self.assertEqual(self.piece_200.getVariationList(), ['1992', '2003'])

    # check that CashTransfer Module was created
    self.assertEqual(self.cash_transfer_module.getPortalType(), 'Cash Transfer Module')
    self.assertEqual(len(self.cash_transfer_module.objectValues()), 0)

    # check inventory at source
    self.simulation_tool = self.getSimulationTool()
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)

  def stepCheckSource(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)

  def stepCheckDestination(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_2.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_2.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_2.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_2.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)

  def stepCheckCashTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    self.assertEqual(len(self.cash_transfer_module.objectValues()), 1)
    self.cash_transfer = getattr(self.cash_transfer_module, 'cash_transfer_1')
    self.assertEqual(self.cash_transfer.getPortalType(), 'Cash Transfer')
    self.assertEqual(self.cash_transfer.getSource(), 'site/testsite/caisse_1')
    self.assertEqual(self.cash_transfer.getDestination(), 'site/testsite/caisse_2')
    #XXX Check roles were correctly affected
    #self.security_manager = AccessControl.getSecurityManager()
    #self.user = self.security_manager.getUser()
    #raise 'alex', repr( self.cash_transfer.get_local_roles() )

  def stepCheckValidLine1(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    self.assertEqual(len(self.cash_transfer.objectValues()), 1)
    self.valid_line_1 = getattr(self.cash_transfer, 'valid_line_1')
    self.assertEqual(self.valid_line_1.getPortalType(), 'Cash Transfer Line')
    self.assertEqual(self.valid_line_1.getResourceValue(), self.billet_10000)
    self.assertEqual(self.valid_line_1.getPrice(), 10000.0)
    self.assertEqual(self.valid_line_1.getQuantityUnit(), 'quantity_unit/unit')
    self.assertEqual(len(self.valid_line_1.objectValues()), 2)
    for variation in self.variation_list:
      cell = self.valid_line_1.getCell('emission_letter/k', variation, 'cash_status/valid')
      self.assertEqual(cell.getPortalType(), 'Delivery Cell')
      if cell.getId() == 'movement_0_0_0':
        self.assertEqual(cell.getQuantity(), 2.0)
        self.assertEqual(cell.getResourceValue(), self.billet_10000)
        self.assertEqual(cell.getSourceValue(), self.caisse_1)
        self.assertEqual(cell.getDestinationValue(), self.caisse_2)
      elif cell.getId() == 'movement_0_1_0':
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepCheckSubTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    # Check number of lines
    self.assertEqual(len(self.cash_transfer.objectValues()), 1)
    # Check sum
    self.assertEqual(self.cash_transfer.getTotalQuantity(), 5.0)
    self.assertEqual(self.cash_transfer.getTotalPrice(), 10000 * 5.0)

  def stepCheckValidLine2(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    self.assertEqual(len(self.cash_transfer.objectValues()), 2)
    self.valid_line_2 = getattr(self.cash_transfer, 'valid_line_2')
    self.assertEqual(self.valid_line_2.getPortalType(), 'Cash Transfer Line')
    self.assertEqual(self.valid_line_2.getResourceValue(), self.piece_200)
    self.assertEqual(self.valid_line_2.getPrice(), 200.0)
    self.assertEqual(self.valid_line_2.getQuantityUnit(), 'quantity_unit/unit')
    for variation in self.variation_list:
      cell = self.valid_line_2.getCell('emission_letter/k', variation, 'cash_status/valid')
      self.assertEqual(cell.getPortalType(), 'Delivery Cell')
      if cell.getId() == 'movement_0_0_0':
        self.assertEqual(cell.getQuantity(), 5.0)
      elif cell.getId() == 'movement_0_1_0':
        self.assertEqual(cell.getQuantity(), 7.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

  def stepCheckTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    # Check number of lines
    self.assertEqual(len(self.cash_transfer.objectValues()), 2)
    # Check sum
    self.assertEqual(self.cash_transfer.getTotalQuantity(), 5.0 + 12.0)
    self.assertEqual(self.cash_transfer.getTotalPrice(), 10000 * 5.0 + 200 * 12.0)

  def stepCheckBadTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    # Check number of lines
    self.assertEqual(len(self.cash_transfer.objectValues()), 3)
    # Check sum
    self.assertEqual(self.cash_transfer.getTotalQuantity(), 5.0 + 12.0 + 24)
    self.assertEqual(self.cash_transfer.getTotalPrice(), 10000 * 5.0 + 200 * 12.0 + 5000 * 24)

  def stepCheckBadUserConfirmCashTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    state = self.cash_transfer.getSimulationState()
    self.assertEqual(state, 'draft')
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_transfer, name='history', wf_id='cash_transfer_workflow')
    self.assertEqual(len(workflow_history), 1)

  def stepCheckBadInventoryConfirmCashTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    state = self.cash_transfer.getSimulationState()
    self.assertEqual(state, 'draft')
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_transfer, name='history', wf_id='cash_transfer_workflow')
    self.assertEqual(len(workflow_history), 2)
    self.assertEqual('Insufficient balance' in workflow_history[-1]['error_message'], True)

  def stepCheckConfirmCashTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    state = self.cash_transfer.getSimulationState()
    self.assertEqual(state, 'confirmed')
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_transfer, name='history', wf_id='cash_transfer_workflow')
    self.assertEqual(len(workflow_history), 4)

  def stepCheckSourceDebitPlanned(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)

  def stepCheckDestinationCreditPlanned(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_2.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_2.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_2.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_2.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)

  def stepBadUserCheckDeliverCashTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    state = self.cash_transfer.getSimulationState()
    self.assertEqual(state, 'confirmed')
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_transfer, name='history', wf_id='cash_transfer_workflow')
    self.assertEqual(len(workflow_history), 4)

  def stepCheckDeliverCashTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    state = self.cash_transfer.getSimulationState()
    self.assertEqual(state, 'delivered')
    workflow_history = self.workflow_tool.getInfoFor(ob=self.cash_transfer, name='history', wf_id='cash_transfer_workflow')
    self.assertEqual(len(workflow_history), 6)

  def stepCheckSourceDebit(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_1.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_1.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)

  def stepCheckDestinationCredit(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_2.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_2.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.caisse_2.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.caisse_2.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)

  def stepCreateCashTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    self.cash_transfer = self.cash_transfer_module.newContent(id='cash_transfer_1', portal_type='Cash Transfer', source_value=self.caisse_1, destination_value=self.caisse_2, price=52400.0) # 5 * 1000 + 12 * 200

  def stepCreateValidLine1(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    self.addCashLineToDelivery(self.cash_transfer, 'valid_line_1', 'Cash Transfer Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/k', 'cash_status/valid') + self.variation_list,
            self.quantity_10000)

  def stepCreateValidLine2(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    self.addCashLineToDelivery(self.cash_transfer, 'valid_line_2', 'Cash Transfer Line', self.piece_200,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/k', 'cash_status/valid') + self.variation_list,
            self.quantity_200)

  def stepCreateInvalidLine(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    self.addCashLineToDelivery(self.cash_transfer, 'invalid_line', 'Cash Transfer Line', self.billet_5000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/k', 'cash_status/valid') + self.variation_list,
            self.quantity_5000)

  def stepDelInvalidLine(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    self.cash_transfer.deleteContent('invalid_line')

  def stepBadUserConfirmCashTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    # log in as bad user
    self.logout()
    self.login(name='user_3')
    # try to doActionFor
    self.workflow_tool = self.getWorkflowTool()
    self.assertRaises(Unauthorized, self.workflow_tool.doActionFor, self.cash_transfer, 'confirm_action', wf_id='cash_transfer_workflow')
    # log in as default user
    self.logout()
    self.login(name='user_1')

  def stepBadInventoryConfirmCashTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    # fix amount
    self.cash_transfer.setPrice('172400.0')
    # logged in as good user
    # try to doActionFor
    self.workflow_tool.doActionFor(self.cash_transfer, 'confirm_action', wf_id='cash_transfer_workflow')

  def stepConfirmCashTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    # fix amount
    self.cash_transfer.setPrice('52400.0')
    # logged in as good user
    # try to doActionFor
    self.workflow_tool.doActionFor(self.cash_transfer, 'confirm_action', wf_id='cash_transfer_workflow')

  def stepBadUserDeliverCashTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    # log in as bad user
    self.logout()
    self.login(name='user_3')
    # try to doActionFor
    self.assertRaises(Unauthorized, self.workflow_tool.doActionFor, self.cash_transfer, 'deliver_action', wf_id='cash_transfer_workflow')
    # log in as default user
    self.logout()
    self.login(name='user_1')

  def stepDeliverCashTransfer(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    # log in as good user
    self.logout()
    self.login(name='user_2')
    # try to doActionFor
    self.security_manager = AccessControl.getSecurityManager()
    self.user = self.security_manager.getUser()
    self.workflow_tool.doActionFor(self.cash_transfer, 'deliver_action', wf_id='cash_transfer_workflow')
    # log in as default user
    self.logout()
    self.login(name='user_1')

  def testERP5BankingCashTransfer(self):
    """
    We'll play the sequence
    """
    sequence_list = SequenceList()
    sequence_string = 'Tic FirstCheck CheckSource CheckDestination' \
                    + ' CreateCashTransfer Tic CheckCashTransfer' \
                    + ' CreateValidLine1 Tic CheckValidLine1 CheckSubTotal' \
                    + ' CreateValidLine2 Tic CheckValidLine2 CheckTotal' \
                    + ' BadUserConfirmCashTransfer Tic CheckBadUserConfirmCashTransfer' \
                      + ' CheckSource CheckDestination' \
                    + ' CreateInvalidLine Tic CheckBadTotal' \
                    + ' BadInventoryConfirmCashTransfer Tic CheckBadInventoryConfirmCashTransfer' \
                    + ' DelInvalidLine Tic CheckTotal' \
                    + ' ConfirmCashTransfer Tic CheckConfirmCashTransfer' \
                      + ' CheckSourceDebitPlanned CheckDestinationCreditPlanned' \
                    + ' BadUserDeliverCashTransfer Tic BadUserCheckDeliverCashTransfer' \
                      + ' CheckSourceDebitPlanned CheckDestinationCreditPlanned' \
                    + ' DeliverCashTransfer Tic CheckDeliverCashTransfer' \
                      + ' CheckSourceDebit CheckDestinationCredit'
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)
