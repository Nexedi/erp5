##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#          Guillaume Michon <guillaume.michon@e-asc.com>
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



#
# Skeleton ZopeTestCase
#

from random import randint

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from Products.DCWorkflow.DCWorkflow import Unauthorized, ValidationFailed
from DateTime import DateTime
from Acquisition import aq_base, aq_inner
from zLOG import LOG
from testOrder import TestOrderMixin
import time
from Products.ERP5.Document.ImmobilisationMovement import UNIMMOBILISING_METHOD, NO_CHANGE_METHOD

try:
  from transaction import get as get_transaction
except ImportError:
  pass

class TestImmobilisationMixin(TestOrderMixin, ERP5TypeTestCase):
  run_all_test = 1
  # Different variables used for this test
  item_portal_type = 'Apparel Fabric Item'
  packing_list_portal_type = 'Purchase Packing List'
  packing_list_line_portal_type = 'Purchase Packing List Line'
  internal_packing_list_portal_type = 'Internal Packing List'
  sale_packing_list_portal_type = 'Sale Packing List'
  inventory_portal_type = 'Inventory'
  inventory_line_portal_type = 'Inventory Line'
  organisation_portal_type = 'Organisation'
  account_portal_type = 'Account'
  currency_portal_type = 'Currency'
  linear_method = 'eu/linear'
  degressive_method = 'fr/degressive'
  uncontinuous_degressive_method = 'fr/uncontinuous_degressive'
  actual_use_method = 'fr/actual_use'
  no_amortisation_method = 'eu/no_amortisation'
  diverged = 'diverged'
  solved = 'solved'
  id_transaction = 0
  id_simulation = 0
  reindex_done = 0

  def getTitle(self):
    return "Immobilisation"
  
  def stepCommitTransaction(self, sequence=None, sequence_list=None, **kw):
    """
    For debugging
    """
    get_transaction().commit()

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.

    """
    return ( "erp5_base",
            "erp5_trade",
            "erp5_pdm",# Needed by accounting
            "erp5_accounting",
            "erp5_apparel", # In order to use items
            "erp5_immobilisation",
            )

  def getRuleTool(self):
    return getattr(self.getPortal(), 'portal_rules', None)
  def getAccountingModule(self):
    return getattr(self.getPortal(), 'accounting_module', None)
  def getOrganisationModule(self):
    return self.getPortal().getDefaultModule(portal_type=self.organisation_portal_type)
  def getItemModule(self):
    return self.getPortal().getDefaultModule(portal_type=self.item_portal_type)
  def getPackingListModule(self):
    return self.getPortal().getDefaultModule(portal_type=self.packing_list_portal_type)
  def getInternalPackingListModule(self):
    return self.getPortal().getDefaultModule(portal_type=self.internal_packing_list_portal_type)
  def getSalePackingListModule(self):
    return self.getPortal().getDefaultModule(portal_type=self.sale_packing_list_portal_type)
  def getInventoryModule(self):
    return self.getPortal().getDefaultModule(portal_type=self.inventory_portal_type)
  def getAccountModule(self):
    return self.getPortal().getDefaultModule(portal_type=self.account_portal_type)
  def getUserFolder(self):
    return getattr(self.getPortal(), 'acl_users', None)
  def getWorkflowTool(self):
    return getattr(self.getPortal(), 'portal_workflow', None)
  
  def createManagerAndLogin(self, quiet=0, run=run_all_test):
    """
      Create a simple user in user_folder with manager rights.
      This user will be used to initialize data in the method afterSetup
    """
    all_roles = ['Manager','Assignor','Assignee','Author','Associate','Auditor']
    if not "manager" in [x.id for x in self.getUserFolder().objectValues()]:
      self.getUserFolder()._doAddUser('manager', '', all_roles, [])
    self.login('manager')
    self.assignPASRolesToUser('test_user_1_', all_roles)
    
  
  def checkUserFolderType(self, quiet=0, run=run_all_test):
    """
      Check the type of user folder to let the test working with both NuxUserGroup and PAS.
    """
    self.user_folder = self.getUserFolder()
    self.PAS_installed = 0
    if self.user_folder.meta_type == 'Pluggable Auth Service':
      # we use PAS
      self.PAS_installed = 1
      
  def assignPASRolesToUser(self, user_name, role_list, quiet=0, run=run_all_test):
    """
      Assign a list of roles to one user with PAS.
    """
    user_folder = self.getUserFolder()
    for role in role_list:
      if role not in user_folder.zodb_roles.listRoleIds():
        user_folder.zodb_roles.addRole(role)
      user_folder.zodb_roles.assignRoleToPrincipal(role, user_name)

  def createERP5Users(self, user_dict, quiet=0, run=run_all_test):
    """
      Create all ERP5 users needed for the test.
      ERP5 user = Person object + Assignment object in erp5 person_module.
    """
    for user_login, user_data in user_dict.items():
      user_roles = user_data[0]
      # Create the Person.
      if len([p for p in self.getPersonModule().objectValues() if p.getReference() == user_login]) == 0:
        person = self.getPersonModule().newContent(id=user_login,
                                                  portal_type='Person',
                                                  reference=user_login,
                                                  career_role="internal")
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
        person.validate()
  
  def updateRoleMappings(self, portal_type_list=[]):
    """
    Update the local roles in existing objects.
    """
    portal_catalog = self.portal.portal_catalog
    for portal_type in portal_type_list:
      for brain in portal_catalog(portal_type = portal_type):
        obj = brain.getObject()
        userdb_path, user_id = obj.getOwnerTuple()
        obj.updateLocalRolesOnSecurityGroups(user_name = user_id)
        #obj.assignRoleToSecurityGroup(user_name = user_id)
  
  def afterSetUp(self):
    LOG('testImmobilisationMixin',0,'In AfterSetUp')
    portal = self.getPortal()
    self.createManagerAndLogin()
    
    
    # remove all message in the message_table because
    # the previous test might have failed
    message_list = portal.portal_activities.getMessageList()
    for message in message_list:
      portal.portal_activities.manageCancel(message.object_path,message.method_id)
    
    self.createCategories()

    #Assert default security Value
    
    list_module = [ 'Inventory Module',
                    'Purchase Packing List Module',
                    'Internal Packing List Module',
                    'Sale Packing List Module',
                    'Building Module',
                    'Incorporeal Item Module',
                    'Reevaluation Module',
                    'Restoration Module',
                    self.getAccountingModule().getPortalType(),
                    self.getOrganisationModule().getPortalType(),
                    self.getItemModule().getPortalType(),
                    self.getPackingListModule().getPortalType(),
                    self.getInventoryModule().getPortalType(),
                    self.getAccountModule().getPortalType(),
                    self.getCurrencyModule().getPortalType(),
                    self.getPersonModule().getPortalType()
                    ]

    # Then add new components
    self.createCurrency()
    self.createOrganisationList()
    self.createAccountList()
    self.createItemList()
    get_transaction().commit()
    self.tic()
    
    self.workflow_tool = self.getWorkflowTool()
    self.checkUserFolderType()

  def beforeTearDown(self):
    """
    Delete all Objects in PL & M Module
    """
    LOG('testImmobilisationMixin',0,'In beforeTearDown')
    self.logout()
    self.login('manager')

    get_transaction().commit()
    self.tic()

    simulation_id_list = [r for r in self.getPortal().portal_simulation.objectIds()]
    self.getPortal().portal_simulation.manage_delObjects(simulation_id_list)

    item_id_list = [r for r in self.getItemModule().objectIds()]
    self.getItemModule().manage_delObjects(item_id_list)

    #LOG('item_id_list after',0,[r for r in self.getPortal().material_module.objectIds()])
    #item_catalog = [(r.uid,r.path) for r in self.getPortal().portal_catalog(portal_type = 'Material')]
    pl_id_list = [r for r in self.getPortal().purchase_packing_list_module.objectIds()]
    self.getPortal().purchase_packing_list_module.manage_delObjects(pl_id_list)

    id_list = [r for r in self.getAccountingModule().objectIds()]
    self.getAccountingModule().manage_delObjects(id_list)
    
    get_transaction().commit()
    self.tic()

  def createCategories(self):
    """
    Replace OrderMixin method
    """
    # Create group categories
    category_tool = self.getCategoryTool()
    self.createCategoryTree(category_tool.group,
                    [
                      ("group A","GA",
                        [
                          ("group Aa","GAa",
                            [
                              ("group Aa1","GAa1",[]),
                              ("group Aa2","GAa2",[])
                            ]
                          ),
                          ("group Ab","GAb",
                            [
                              ("group Ab1","GAb1",[]),
                              ("group Ab2","GAb2",[])
                            ]
                          )
                        ]
                      ),
                      ("group B","GB",
                        [
                          ("group Ba","GBa", []),
                          ("group Bb","GBb", [])
                        ],
                      ),
                      ("group C","GC", []),
                    ]
                 )

  def createCategoryTree(self, current_category, category_tree):
    """
    Create a category tree
    """
    for category, codification, new_tree in category_tree:
      if category not in current_category.objectIds():
        new_category = current_category.newContent(portal_type='Category', id=category, codification=codification)
        self.createCategoryTree(new_category, new_tree)
  
  def createCategorySiteTree(self, current_category, category_tree):
    """
    Create a category tree
    """
    for category, codification, vault_type, new_tree in category_tree:
      if category not in current_category.objectIds():
        new_category = current_category.newContent(portal_type='Category',
                                                   id=category,
                                                   codification=codification)
        new_category.setVaultType(vault_type)
        self.createCategorySiteTree(new_category, new_tree)
   
  def createCurrency(self):
    currency_module = self.getCurrencyModule()
    if len(currency_module.contentValues())==0:
      currency_module.newContent(id="EUR", portal_type='Currency')
      currency_module.newContent(id="FCFA", portal_type='Currency')

  def createOrganisationList(self):
    """
    Create some organisations relating to the group tree
    """
    organisation_module = self.getOrganisationModule()
    if len(organisation_module.contentValues())==0:
      organisation_list= (
                               ("A", "A", "group A", "group/group A"),
                               ("Aa", "Aa", "group A", "group/group A/group Aa"),
                               ("Ab", "Ab", "group A", "group/group A/group Ab"),
                               ("Aa1", "Aa1", "group A", "group/group A/group Aa/group Aa1"),
                               ("Aa2", "Aa2", "group A", "group/group A/group Aa/group Aa2"),
                               ("Ab1", "Ab1", "group A", "group/group A/group Ab/group Ab1"),
                               ("Ab2", "Ab2", "group A", "group/group A/group Ab/group Ab2"),
                               ("B", "B", "group B", "group/group B"),
                               ("Ba", "Ba", "group B", "group/group B/group Ba"),
                               ("Bb", "Bb", "group B", "group/group B/group Bb"),
                               ("standalone", "standalone", "", ""),
                           )
      for organisation_id, title, group, mapping in organisation_list:
        organisation_module.newContent(id = organisation_id,
                                       title = title,
                                       group = group,
                                       mapping = mapping,
                                       )
      ##We need to commit here because edit organisation doesn't apply
      #get_transaction().commit()
      #self.tic()
      for organisation_id in ['A','Aa','Ab','B','Ba','Bb','standalone']:
        organisation = organisation_module[organisation_id]
        organisation.edit(price_currency_value = self.getCurrencyModule()["EUR"],
                          financial_year_stop_date = DateTime('2000/01/01'))

  def createAccountList(self):
    """
    Create some accounts
    """
    account_module = self.getAccountModule()
    if len(account_module.contentValues())==0:
      for i in range(15):
        account_id = 'account%i' % i
        account = account_module.newContent(id=account_id, gap='gap')
        account.validate()
    self.account_dict = {
    'input_account':              '%s/%s' % (self.getAccountModule().getId(),'account1'),
    'output_account':             '%s/%s' % (self.getAccountModule().getId(),'account2'),
    'immobilisation_account':     '%s/%s' % (self.getAccountModule().getId(),'account3'),
    'amortisation_account':       '%s/%s' % (self.getAccountModule().getId(),'account4'),
    'depreciation_account':       '%s/%s' % (self.getAccountModule().getId(),'account5'),
    'immobilisation_vat_account': '%s/%s' % (self.getAccountModule().getId(),'account6'),
    'extra_cost_account':         '%s/%s' % (self.getAccountModule().getId(),'account7'),
    }
    self.monthly_dict = {
    'monthly_amortisation_account':'%s/%s' % (self.getAccountModule().getId(),'account8'),
    }
    self.extra_account_dict = {
    'immobilisation_account':   '%s/%s' % (self.getAccountModule().getId(),'account9'),
    'amortisation_account':     '%s/%s' % (self.getAccountModule().getId(),'account10'),
    'depreciation_account':     '%s/%s' % (self.getAccountModule().getId(),'account11'),
    }
    self.extra_monthly_dict = {
    'monthly_amortisation_account':'%s/%s' % (self.getAccountModule().getId(),'account12'),
    }
  
  def createAmortisationDefaultData(self):
    amo_data_module = self.getPortal().amortisation_default_data_module
    if len(amo_data_module.contentValues()) == 0:
      property_dict1 = {'amortisation_method':self.linear_method,
                      'amortisation_start_price':0.0,
                      'disposal_price':0.0,
                      'amortisation_duration':72,
                      'immobilisation_vat':0.0,
                      'product_line':'armoires',
                      }
      amo_data1 = amo_data_module.newContent()
      amo_data1.edit(**property_dict1)
      property_dict2 = {'amortisation_method':self.linear_method,
                      'amortisation_start_price':0.0,
                      'disposal_price':0.0,
                      'amortisation_duration':72,
                      'immobilisation_vat':0.0,
                      'product_line':'art_tableaux',
                      }
      amo_data2 = amo_data_module.newContent()
      amo_data2.edit(**property_dict2)
    
  def createItemList(self):
    """
    Create some items
    """
    item_module = self.getItemModule()
    if len(item_module.contentValues()) == 0:
      for i in range(30):
        item_id = 'item%i' % i
        item_module.newContent(id=item_id, reference=item_id)

  def stepPdb(self, sequence=None, sequence_list=None, **kw):
    import pdb;pdb.set_trace()
    
  def stepCreatePackingList(self, sequence=None, sequence_list=None, **kw):
    property_dict = {}
    for property in ('source_section','destination_section','datetime','destination'):
      value_list = sequence.get(property)
      if value_list is not None:
        if type(value_list) == type([]):
          value = value_list[0]
          value_list.remove(value)
        else:
          value = value_list
      else:
        value = value_list
      property_dict[property] = value
    pl_module = self.getPackingListModule()
    pl = pl_module.newContent(portal_type = self.packing_list_portal_type)
    pl.edit( source_section_value =      property_dict['source_section'],
             destination_section_value = property_dict['destination_section'],
             start_date =                property_dict['datetime'],
             stop_date =                 property_dict['datetime'],
             destination =               property_dict['destination'],
             )
    
    packing_list_list = sequence.get('packing_list_list', [])
    packing_list_list.append(pl)
    sequence.set('packing_list_list', packing_list_list)
    #LOG('createPL',0,[(ppl.getUid(),ppl.getRelativeUrl()) for ppl in pl_module.objectValues()])
    
  def stepDeliverPackingList(self, sequence=None, sequence_list=None, **kw):
    pl = sequence.get('packing_list')
    if pl is None: pl = sequence.get('packing_list_list', [])[-1]
    self.workflow_tool.doActionFor(pl, 'confirm_action', wf_id='packing_list_workflow')
    get_transaction().commit()
    self.tic()
    self.workflow_tool.doActionFor(pl, 'set_ready_action', wf_id='packing_list_workflow')
    self.workflow_tool.doActionFor(pl, 'start_action', wf_id='packing_list_workflow')
    #import pdb; pdb.set_trace()
    get_transaction().commit()
    self.tic()
    self.workflow_tool.doActionFor(pl, 'stop_action', wf_id='packing_list_workflow')
    get_transaction().commit()
    self.tic()
    #self.workflow_tool.doActionFor(pl, 'deliver_action', wf_id='packing_list_workflow')

  def stepTestItemValidationState(self, sequence=None, sequence_list=None, **kw):
    item = self.getItemModule()['item1']
    self.assertEquals(item.getValidationState(), 'exploited')


  def stepAggregateItems(self, sequence=None, sequence_list=None, **kw):
    pl = sequence.get('packing_list_list', [])[-1]
    parameter_dict = sequence.get('parameter_dict', {})
    if parameter_dict is None: parameter_dict = {}
    item_list_list = sequence.get('item_list_list') # This is a list of list in
                                                    # order to make multiple lines
    for item_list in item_list_list:
      pl_line = pl.newContent(portal_type = self.packing_list_line_portal_type)
      pl_line.edit(aggregate_value_list = item_list, **parameter_dict)
    get_transaction().commit()
    self.tic()
    pl.edit()
  
  def stepEditPackingList(self, sequence=None, sequence_list=None, **kw):
    pl = sequence.get('packing_list')
    if pl is None: pl = sequence.get('packing_list_list', [])[-1]
    pl.edit()
    
    
  def stepCreateComplexPackingListStructure(self, sequence=None, sequence_list=None, **kw):
    """
    Create a complex structure of PL and items
    Item    1    2    3   4
    PL 1    X    X
    PL 2                  X
    PL 3    X         X
    PL 4         X    X
    """
    sequence.edit(destination_section =  self.getOrganisationModule()["A"],
                  datetime= self.datetime,
                  item_list_list = [[ self.getItemModule()['item1'] ], [ self.getItemModule()['item2'] ]])
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    sequence.edit(item_list_list = [[self.getItemModule()['item4']]], datetime = self.datetime+5)
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    sequence.edit(item_list_list = [[ self.getItemModule()['item1'],self.getItemModule()['item3'] ]],
                  datetime = self.datetime+10)
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    sequence.edit(item_list_list = [[ self.getItemModule()['item2'],self.getItemModule()['item3'] ]],
                  datetime = self.datetime+15)
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)

  def stepDeletePackingList(self, sequence=None, sequence_list=None, **kw):
    pl = sequence.get('packing_list')
    pl_in_list = 0
    if pl is None:
      pl = sequence.get('packing_list_list', []) [-1]
      pl_in_list = 1
    pl_id = pl.getId()
    self.getPackingListModule().manage_delObjects([pl_id])
    if pl_in_list:
      sequence.set('packing_list_list', sequence.get('packing_list_list')[:-1])
    
  def stepUseFirstPackingList(self, sequence=None, sequence_list=None, **kw):
    pl = sequence.get('packing_list_list')[0]
    sequence.set('packing_list', pl)

  def stepUseSecondPackingList(self, sequence=None, sequence_list=None, **kw):
    pl = sequence.get('packing_list_list')[1]
    sequence.set('packing_list', pl)

  def stepUseThirdPackingList(self, sequence=None, sequence_list=None, **kw):
    pl = sequence.get('packing_list_list')[2]
    sequence.set('packing_list', pl)
    
  def stepUseFourthPackingList(self, sequence=None, sequence_list=None, **kw):
    pl = sequence.get('packing_list_list')[3]
    sequence.set('packing_list', pl)
    
  def stepDeleteCurrentPackingListFromSequence(self, sequence=None, sequence_list=None, **kw):
    sequence.set('packing_list', None)
    
  def stepDeleteAllPackingLists(self, sequence=None, sequence_list=None, **kw):
    id_list = self.getPackingListModule().contentIds()
    self.getPackingListModule().manage_delObjects(id_list)
    sequence.set('packing_list_list', [])
    
  def stepDeleteAccounting(self, sequence=None, sequence_list=None, **kw):
    id_list = self.getAccountingModule().contentIds()
    self.getAccountingModule().manage_delObjects(id_list)
    
  def stepValidateAccounting(self, sequence=None, sequence_list=None, **kw):
    for transaction in self.getAccountingModule().contentValues():
      transaction.stop()
      get_transaction().commit()
      self.tic()
      transaction.deliver()
      get_transaction().commit()
      self.tic()

  def stepTestPackingListInvalidImmobilisationState(self, sequence=None, sequence_list=None, **kw):
    pl = sequence.get('packing_list')
    if pl is None: pl=sequence.get('packing_list_list', [])[-1]
    self.stepTestPackingListImmobilisationState(pl, "invalid")
  
  def stepTestPackingListValidImmobilisationState(self, sequence=None, sequence_list=None, **kw):
    pl = sequence.get('packing_list')
    if pl is None: pl = sequence.get('packing_list_list', [])[-1]
    self.stepTestPackingListImmobilisationState(pl, "valid")
  
  def stepTestPackingListDeliveredSimulationState(self, sequence=None, sequence_list=None, **kw):
    pl = sequence.get('packing_list')
    if pl is None: pl = sequence.get('packing_list_list', [])[-1]
    self.stepTestPackingListSimulationState(pl, "delivered")
  
  def stepTestPackingListCalculatingImmobilisationState(self, sequence=None, sequence_list=None, **kw):
    pl = sequence.get('packing_list')
    if pl is None: pl = sequence.get('packing_list_list', [])[-1]
    self.stepTestPackingListImmobilisationState(pl, "calculating")
    
  def stepTestPackingListImmobilisationState(self, pl, state, **kw):
    self.assertEquals(pl.getImmobilisationState(), state)

  def stepTestPackingListSimulationState(self, pl, state, **kw):
    self.assertEquals(pl.getSimulationState(), state)
    
  def stepTestPackingListValidationState(self, pl, state, **kw):
    self.assertEquals(pl.getValidationState(), state)
    
  def stepCreatePackingListsForContinuousAmortisationPeriodList(self, sequence=None, sequence_list=None, **kw):
    """
    Create a list of packing lists describing a continuous period list :
    2000/01/01 : immobilisation (1)
    2001/01/01 : immobilisation with different values (2)
    2002/01/01 : immobilisation with no values  (3)
    2002/07/01 : owner change
    2002/10/01 : owner set to None
    2003/01/01 : immobilisation with no values (4)
    """
    
    item = sequence.get('item')
    amortisation_method = sequence.get('amortisation_method')
    parameter_dict = sequence.get('parameter_dict', {})
    parameter_dict.update(self.account_dict)
    parameter_dict.update( {'amortisation_method':amortisation_method,
                            'amortisation_start_price':10000,
                            'disposal_price':0,
                            'amortisation_duration':72,
                            'immobilisation_vat':0,
                          } )
    sequence.edit(item_list_list = [[item]],
                  datetime = DateTime('2000/01/01'),
                  parameter_dict = parameter_dict,
                  destination_section = self.getOrganisationModule()["A"])
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    #1
    parameter_dict.update( {'amortisation_start_price':12000,
                            'disposal_price':0,
                            'amortisation_duration':48,
                            'immobilisation_vat':0 })
    sequence.edit(datetime = DateTime('2001/01/01'),
                  parameter_dict = parameter_dict)
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    #2
    for parameter in ('amortisation_start_price', 'disposal_price', 'amortisation_duration', 'immobilisation_vat'):
      del parameter_dict[parameter]
    sequence.edit(datetime = DateTime('2002/01/01'),
                  parameter_dict = parameter_dict)
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    #3
    sequence.edit(datetime = DateTime('2003/01/01'))
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    #4
    # Create owner changing movements
    sequence.edit(datetime = DateTime('2002/07/01'),
                  destination_section=self.getOrganisationModule()["B"],
                  parameter_dict=None)
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    #5
    sequence.edit(datetime = DateTime('2002/10/01'),destination_section=None)
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    #6
    #sequence.edit(datetime = DateTime('2003/01/01'))
    #self.stepCreatePackingList(sequence=sequence)
    #self.stepAggregateItems(sequence=sequence)
    #self.stepDeliverPackingList(sequence=sequence)
    
  def stepCreatePackingListsForUncontinuousAmortisationPeriodList(self, sequence=None, sequence_list=None, **kw):
    """
    Create a list of packing lists describing an uncontinuous period list :
    2000/01/01 : immobilisation (1)
    2001/01/01 : unimmobilisation (2)
    2001/07/01 : unimmobilisation (3)
    2002/01/01 : owner change
    2003/01/01 : immobilisation (4)
    2004/01/01 : owner change
    """
    item = sequence.get('item')
    amortisation_method = sequence.get('amortisation_method')
    parameter_dict = sequence.get('parameter_dict', {})
    parameter_dict.update(self.account_dict)
    parameter_dict.update( {'amortisation_method':amortisation_method,
                            'amortisation_start_price':10000,
                            'disposal_price':0,
                            'amortisation_duration':72,
                            'immobilisation_vat':0,
                          } )
    sequence.edit(item_list_list = [[item]],
                  datetime = DateTime('2000/01/01'),
                  parameter_dict = parameter_dict,
                  destination_section = self.getOrganisationModule()["A"])
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    parameter_dict.update( {'amortisation_method':UNIMMOBILISING_METHOD,
                            'amortisation_start_price':12000,
                            'amortisation_start_price':0,
                            'amortisation_duration':48,
                            'immobilisation_vat':0 })
    for parameter in ('amortisation_start_price', 'disposal_price', 'amortisation_duration', 'immobilisation_vat'):
      del parameter_dict[parameter]
    sequence.edit(datetime = DateTime('2001/01/01'),
                  parameter_dict = parameter_dict)
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    sequence.edit(datetime = DateTime('2001/07/01'),
                  parameter_dict = parameter_dict)
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    parameter_dict.update( {'amortisation_method':amortisation_method,
                            'amortisation_start_price':10000,
                            'disposal_price':0,
                            'amortisation_duration':72,
                            'immobilisation_vat':0,
                          } )
    sequence.edit(datetime = DateTime('2003/01/01'),
                  parameter_dict = parameter_dict,
                  destination_section = self.getOrganisationModule()["B"])
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    
    # Create owner changing movements
    sequence.edit(datetime = DateTime('2002/01/01'),
                  parameter_dict=None,
                  destination_section=self.getOrganisationModule()["B"])
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    sequence.edit(datetime = DateTime('2004/01/01'),
                  destination_section=self.getOrganisationModule()["A"])
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
      
    
  def stepCreatePackingListsForSimpleItemImmobilisation(self, sequence=None, sequence_list=None, **kw):
    """
    Create a list of packing lists describing a continuous period list :
    2000/01/01 : immobilisation (1)
    2003/07/01 : immobilisation (2)
    """
    item = sequence.get('item')
    amortisation_method = sequence.get('amortisation_method')
    parameter_dict = sequence.get('parameter_dict', {})
    parameter_dict.update(self.account_dict)
    parameter_dict.update( {'amortisation_method':amortisation_method,
                            'amortisation_start_price':10000,
                            'disposal_price':0,
                            'amortisation_duration':72,
                            'immobilisation_vat':0,
                          } )
    sequence.edit(item_list_list = [[item]],
                  datetime = DateTime('2000/01/01'),
                  parameter_dict = parameter_dict,
                  destination_section = self.getOrganisationModule()["A"])
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    parameter_dict.update( {'amortisation_start_price':12000,
                            'amortisation_duration':84,
                            'immobilisation_vat':0,
                            'degressive_coefficient':2.5,
                            'durability':100 })
    sequence.edit(datetime = DateTime('2003/07/01'),
                  parameter_dict = parameter_dict)
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)

  """
  09BIS
  """
  def stepCreatePackingListsForSimpleItemImmobilisationBIS(self, sequence=None, sequence_list=None, **kw):
    """
    Create a list of packing lists describing a continuous period list :
    2000/01/01 : immobilisation (1)
    """
    item = sequence.get('item')
    amortisation_method = sequence.get('amortisation_method')
    parameter_dict = sequence.get('parameter_dict', {})
    parameter_dict.update(self.account_dict)
    parameter_dict.update( {'amortisation_method':amortisation_method,
                            'amortisation_start_price':10000,
                            'disposal_price':0,
                            'amortisation_duration':48,
                            'immobilisation_vat':0,
                          } )
    sequence.edit(item_list_list = [[item]],
                  datetime = DateTime('2000/07/01'),
                  parameter_dict = parameter_dict,
                  destination_section = self.getOrganisationModule()["orga"])
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
      
    
  def stepCreatePackingListsForSimulationTest(self, sequence=None, sequence_list=None, **kw):
    """
    Create a list of packing lists describing a continuous period list :
    2000/01/01 : immobilisation (1)
    2001/01/01 : immobilisation (2)
    The second movement changes some accounts
    """
    item = sequence.get('item')
    amortisation_method = sequence.get('amortisation_method')
    parameter_dict = sequence.get('parameter_dict', {})
    parameter_dict.update(self.account_dict)
    parameter_dict.update( {'amortisation_method':amortisation_method,
                            'amortisation_start_price':8000,
                            'disposal_price':0,
                            'amortisation_duration':36,
                            'immobilisation_vat':1000,
                            'extra_cost_price':2000,
                          } )
    sequence.edit(item_list_list = [[item]],
                  datetime = DateTime('2000/01/01'),
                  parameter_dict = parameter_dict,
                  destination_section = self.getOrganisationModule()["Aa1"])
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    parameter_dict.update( {'amortisation_start_price':12000,
                            'amortisation_duration':36,
                            'immobilisation_vat':0,
                            'extra_cost_price':0,
                            'degressive_coefficient':2,
                            'durability':100,
                            })
    parameter_dict.update(self.extra_account_dict)
    sequence.edit(datetime = DateTime('2001/01/01'),
                  parameter_dict = parameter_dict,
                  destination_section = self.getOrganisationModule()["Aa2"])
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    
    
  def stepCreatePackingListsForNoChangeMethodSimulationTest(self, sequence=None, sequence_list=None, **kw):
    """
    Create a list of packing lists describing a continuous period list :
    2000/01/01 : immobilisation (1)
    2001/01/01 : immobilisation (2)
    The second movement changes only the owner (or not)
    """
    item = sequence.get('item')
    amortisation_method = sequence.get('amortisation_method')
    parameter_dict = sequence.get('parameter_dict', {})
    parameter_dict.update(self.account_dict)
    parameter_dict.update( {'amortisation_method':amortisation_method,
                            'amortisation_start_price':8000,
                            'disposal_price':0,
                            'amortisation_duration':36,
                            'immobilisation_vat':1000,
                            'extra_cost_price':2000,
                          } )
    sequence.edit(item_list_list = [[item]],
                  datetime = DateTime('2000/01/01'),
                  parameter_dict = parameter_dict,
                  destination_section = self.getOrganisationModule()["Aa1"])
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    for property in ('amortisation_start_price','amortisation_duration','immobilisation_vat',
                     'extra_cost_price','disposal_price'):
      del parameter_dict[property]
    parameter_dict['amortisation_method'] = NO_CHANGE_METHOD
    sequence.edit(datetime = DateTime('2001/01/01'),
                  parameter_dict = parameter_dict,
                  destination_section = self.getOrganisationModule()["Aa2"])
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    
    
  def stepChangeCurrentPackingListDestinationSectionForOwnerChange(self, sequence=None, sequence_list=None, **kw):
    """
    Change the destination section of the packing list in order to make a owner change,
    but the actual owner (i.e. group) does not change
    """
    pl = sequence.get('packing_list_list')[-1]
    pl.edit(destination_section_value = self.getOrganisationModule()['Ab1'])
    pl.contentValues()[0].edit(**self.account_dict)
          
    
  def stepChangeCurrentPackingListDestinationSectionForActualOwnerChange(self, sequence=None, sequence_list=None, **kw):
    """
    Change the destination section of the packing list in order to make the actual owner (i.e. group) change
    """
    pl = sequence.get('packing_list_list')[-1]
    pl.edit(destination_section_value = self.getOrganisationModule()['Ba'])
    pl.contentValues()[0].edit(**self.account_dict)
          
  """
  TEST 17
  """
  def stepCreatePackingListsForMonthlyAmortisationTest(self, sequence=None, sequence_list=None, **kw):
    """
    Create a list of packing lists describing a continuous period list :
    2000/01/01 : immobilisation (1)
    2002/03/01 : immobilisation (2), owner does not change
    2002/04/16 : immobilisation (3), owner does not change
    2002/05/16 : immobilisation (3), owner changes
    2002/06/16 : immobilisation (4), actual owner changes
    """
    item = sequence.get('item')
    amortisation_method = sequence.get('amortisation_method')
    parameter_dict = sequence.get('parameter_dict', {})
    parameter_dict.update(self.account_dict)
    parameter_dict.update(self.monthly_dict)
    parameter_dict.update( {'amortisation_method':amortisation_method,
                            'amortisation_start_price':9000,
                            'disposal_price':1000,
                            'amortisation_duration':36,
                            'immobilisation_vat':1000,
                            'extra_cost_price':2000,
                          } )
    sequence.edit(item_list_list = [[item]],
                  datetime = DateTime('2000/01/01'),
                  parameter_dict = parameter_dict,
                  destination_section = self.getOrganisationModule()["Aa1"])
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    for property in ('amortisation_start_price','amortisation_duration','immobilisation_vat',
                     'extra_cost_price','disposal_price'):
      del parameter_dict[property]
    for property in self.account_dict.keys():
      del parameter_dict[property]
    parameter_dict.update(self.extra_monthly_dict)
    sequence.edit(datetime = DateTime('2002/03/01'),
                  parameter_dict = parameter_dict,
                  destination_section = self.getOrganisationModule()["Aa2"])
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    parameter_dict.update(self.monthly_dict)
    sequence.edit(datetime = DateTime('2002/04/16'),
                  parameter_dict = parameter_dict)
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    sequence.edit(datetime = DateTime('2002/05/16'),
                  parameter_dict = parameter_dict,
                  destination_section = self.getOrganisationModule()["Ab1"])
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    sequence.edit(datetime = DateTime('2002/06/16'),
                  parameter_dict = parameter_dict,
                  destination_section = self.getOrganisationModule()["Ba"])
    self.stepCreatePackingList(sequence=sequence)
    self.stepAggregateItems(sequence=sequence)
    self.stepDeliverPackingList(sequence=sequence)
    
    
  def stepBuildAccounting(self, sequence=None, sequence_list=None, **kw):
    """
    Build completely accounting
    """
    self.stepPartialBuildAccounting(sequence=sequence, sequence_list=sequence_list, build_parameter_dict={}, **kw)
  
  def stepPartialBuildAccounting(self, sequence=None, sequence_list=None, build_parameter_dict=None, **kw):
    """
    Build a part of the simulation according to sequence data
    """
    if build_parameter_dict is None:
      build_parameter_dict = sequence.get('build_parameter_dict',{})
      LOG('build_parameter_dict for PartialBuildAccounting', 0, build_parameter_dict)
    self.getPortal().AccountingTransactionModule_activateBuildAmortisationTransaction(**build_parameter_dict)
    
  def stepAdoptPrevision(self,sequence=None, sequence_list=None, **kw):
    """
    Launch adopt_prevision() on each Amortisation Transaction
    """
    for transaction in self.getAccountingModule().contentValues():
      if hasattr(transaction, 'adoptPrevision'):
        transaction.adoptPrevision()
        LOG('Launched adoptPrevision() for transaction', 0, transaction.getRelativeUrl())
      else:
        LOG('Cannot launch adoptPrevision() for transaction', 0, transaction.getRelativeUrl())
        
  def stepAcceptDecision(self, sequence=None, sequence_list=None, **kw):
    """
    Launch accept_decision() on each Amortisation Transaction
    """
    for transaction in self.getAccountingModule().contentValues():
      #LOG('transaction %s causality state :' % transaction, 0, transaction.getCausalityState())
      try:
        self.getPortal().portal_workflow.doActionFor(transaction,
                                                     'accept_decision_action',
                                                     'amortisation_transaction_causality_workflow')
        LOG('Launched acceptDecision() for transaction', 0, transaction.getRelativeUrl())
      except:
        LOG('Cannot launch acceptDecision() for transaction', 0, transaction.getRelativeUrl())
        
  def stepChangeAccountingPrice(self, sequence=None, sequence_list=None, **kw):
    """
    Modify a price on an accounting line
    """
    found = 0
    transaction_list = self.getAccountingModule().contentValues()
    for transaction in transaction_list:
      if transaction.getStopDate() == DateTime('2000/01/01'):
        for line in transaction.contentValues():
          if line.getSource() == self.account_dict['input_account'] and \
             line.getQuantity() == 10000 and not found:
            found = 1
            line.edit(quantity=15000)
  
  def stepTestAllAppliedRulesAreEmpty(self, sequence=None, sequence_list=None, **kw):
    """
    Test if all applied rules are empty
    """
    for item in self.getItemModule().contentValues():
      applied_rule_list = item.getCausalityRelatedValueList()
      for applied_rule in applied_rule_list:
        LOG('testing if applied rule is empty for item', 0, item)
        self.assertEquals(len(applied_rule.contentValues()), 0)
      
  
  def stepTestLinearAmortisationImmobilisationPeriods(self, sequence=None, sequence_list=None, **kw):
    """
    Test calculated immobilisation periods
    """
    item = sequence.get('item')
    c_period_list = item.getImmobilisationPeriodList()
    e_period_list = [ { 'start_date':DateTime('2000/01/01'), 'stop_date':DateTime('2001/01/01'),
                        'initial_date':DateTime('2000/01/01'),
                        'start_price':10000, 'owner':self.getOrganisationModule()["A"],
                        'initial_price':10000, 'start_method':'eu/linear',
                        'initial_method':'eu/linear', 'start_duration':72,
                        'initial_duration':72 },
                      { 'start_date':DateTime('2001/01/01'), 'stop_date':DateTime('2002/01/01'),
                        'initial_date':DateTime('2000/01/01'),
                        'start_price':12000, 'owner':self.getOrganisationModule()["A"],
                        'initial_price':10000, 'start_method':'eu/linear',
                        'initial_method':'eu/linear', 'start_duration':48,
                        'initial_duration':72 },
                      { 'start_date':DateTime('2002/01/01'), 'stop_date':DateTime('2002/07/01'),
                        'initial_date':DateTime('2000/01/01'),
                        'start_price':0, 'owner':self.getOrganisationModule()["A"],
                        'initial_price':10000, 'start_method':'eu/linear',
                        'initial_method':'eu/linear', 'start_duration':None,
                        'initial_duration':72 },
                      { 'start_date':DateTime('2002/07/01'), 'stop_date':DateTime('2002/10/01'),
                        'initial_date':DateTime('2002/07/01'),
                        'owner':self.getOrganisationModule()["B"],
                        'initial_price':5833.33, 'start_method':'eu/linear',
                        'initial_method':'eu/linear', 'start_duration':42,
                        'initial_duration':42 },
                    ]
    self._testImmobilisationPeriods(c_period_list, e_period_list)

        
  def stepTestLinearAmortisationImmobilisationPeriodsUncontinuous(self, sequence=None, sequence_list=None, **kw):
    """
    Test calculated immobilisation periods
    """
    item = sequence.get('item')
    c_period_list = item.getImmobilisationPeriodList()
    e_period_list = [ { 'start_date':DateTime('2000/01/01'), 'stop_date':DateTime('2001/01/01'),
                        'initial_date':DateTime('2000/01/01'),
                        'start_price':10000, 'owner':self.getOrganisationModule()["A"],
                        'initial_price':10000, 'start_method':'eu/linear',
                        'initial_method':'eu/linear', 'start_duration':72,
                        'initial_duration':72 },
                      { 'start_date':DateTime('2003/01/01'), 'stop_date':DateTime('2004/01/01'),
                        'initial_date':DateTime('2003/01/01'),
                        'start_price':10000, 'owner':self.getOrganisationModule()["B"],
                        'initial_price':10000, 'start_method':'eu/linear',
                        'initial_method':'eu/linear', 'start_duration':72,
                        'initial_duration':72 },
                      { 'start_date':DateTime('2004/01/01'),
                        'initial_date':DateTime('2004/01/01'),
                        'owner':self.getOrganisationModule()["A"],
                        'initial_price':8333.33, 'start_method':'eu/linear',
                        'initial_method':'eu/linear', 'start_duration':60,
                        'initial_duration':60 },
                    ]
    self._testImmobilisationPeriods(c_period_list, e_period_list)

            
  def stepTestDegressiveAmortisationImmobilisationPeriods(self, sequence=None, sequence_list=None, **kw):
    """
    Test calculated immobilisation periods
    """
    item = sequence.get('item')
    c_period_list = item.getImmobilisationPeriodList()
    
    e_period_list = [ { 'start_date':DateTime('2000/01/01'), 'stop_date':DateTime('2001/01/01'),
                        'initial_date':DateTime('2000/01/01'),
                        'start_price':10000, 'owner':self.getOrganisationModule()["A"],
                        'initial_price':10000, 'start_method':'fr/uncontinuous_degressive',
                        'initial_method':'fr/uncontinuous_degressive', 'start_duration':72,
                        'initial_duration':72 },
                      { 'start_date':DateTime('2001/01/01'), 'stop_date':DateTime('2002/07/01'),
                        'initial_date':DateTime('2001/01/01'),
                        'start_price':12000, 'owner':self.getOrganisationModule()["A"],
                        'initial_price':12000, 'start_method':'fr/uncontinuous_degressive',
                        'initial_method':'fr/uncontinuous_degressive', 'start_duration':48,
                        'initial_duration':48 },
                      { 'start_date':DateTime('2002/07/01'), 'stop_date':DateTime('2002/10/01'),
                        'initial_date':DateTime('2002/07/01'),
                        'start_price':4500, 'owner':self.getOrganisationModule()["B"],
                        'initial_price':4500, 'start_method':'fr/uncontinuous_degressive',
                        'initial_method':'fr/uncontinuous_degressive', 'start_duration':30,
                        'initial_duration':30 },
                    ]
    self._testImmobilisationPeriods(c_period_list, e_period_list)
      

  def stepTestDegressiveAmortisationImmobilisationPeriodsUncontinuous(self, sequence=None, sequence_list=None, **kw):
    """
    Test calculated immobilisation periods
    """
    item = sequence.get('item')
    c_period_list = item.getImmobilisationPeriodList()
    e_period_list = [ { 'start_date':DateTime('2000/01/01'), 'stop_date':DateTime('2001/01/01'),
                        'initial_date':DateTime('2000/01/01'),
                        'start_price':10000, 'owner':self.getOrganisationModule()["A"],
                        'initial_price':10000, 'start_method':'fr/uncontinuous_degressive',
                        'initial_method':'fr/uncontinuous_degressive', 'start_duration':72,
                        'initial_duration':72 },
                      { 'start_date':DateTime('2003/01/01'), 'stop_date':DateTime('2004/01/01'),
                        'initial_date':DateTime('2003/01/01'),
                        'start_price':10000, 'owner':self.getOrganisationModule()["B"],
                        'initial_price':10000, 'start_method':'fr/uncontinuous_degressive',
                        'initial_method':'fr/uncontinuous_degressive', 'start_duration':72,
                        'initial_duration':72 },
                      { 'start_date':DateTime('2004/01/01'),
                        'initial_date':DateTime('2004/01/01'),
                        'owner':self.getOrganisationModule()["A"],
                        'start_method':'fr/uncontinuous_degressive',
                        'initial_method':'fr/uncontinuous_degressive', 'start_duration':60,
                        'initial_duration':60 },
                    ]
    self._testImmobilisationPeriods(c_period_list, e_period_list)
      
      
  def _testImmobilisationPeriods(self,c_period_list,e_period_list):
    #LOG('c_period_list :', 0, c_period_list)
    e_period_cursor = 0
    for c_period in c_period_list:
      #LOG('c_period :', 0, c_period)
      if e_period_cursor >= len(e_period_list):
        LOG('More calculated periods than expected !', 0, '')
        self.assertEquals(len(c_period_list), len(e_period_list))
      e_period = e_period_list[e_period_cursor]
      #LOG('e_period :', 0, e_period)
      e_period_cursor += 1
      for key in e_period.keys():
        e_value = e_period[key]
        #LOG('testing c_period %s "%s" value' % (e_period_cursor-1, key), 0, '')
        self.failUnless(c_period.has_key(key))
        c_value = c_period[key]
        is_float = 0
        try:
          if type(c_value) != type(DateTime()):
            c_value=float(c_value)
            is_float = 1
        except:
          pass
        if is_float:
          self.assertEquals(round(c_value,2),e_value)
        else:
          self.assertEquals(c_value,e_value)
    if e_period_cursor != len(e_period_list):
      LOG('More expected periods than calculated !', 0, '')
      self.assertEquals(len(c_period_list), len(e_period_list))


  def stepTestLinearAmortisationPriceCalculation(self, sequence=None, sequence_list=None, **kw):
    """
    Test calculated prices
    """
    item = sequence.get('item')
    price_list = [
           (DateTime('2001/01/01'), 8333.33),
           (DateTime('2002/01/01'), 6666.67),
           (DateTime('2003/01/01'), 5000),
           (DateTime('2003/02/01'), 4861.11),
           (DateTime('2003/02/16'), 4791.67),
           (DateTime('2004/01/01'), 3333.33),
           (DateTime('2005/01/01'), 1666.67),
           (DateTime('2006/01/01'), 0),
           (DateTime('2020/01/01'), 0),
           ]
    for date, e_price in price_list:
      c_price = item.getAmortisationPrice(at_date=date)
      #LOG('testing amortisation price at date', 0, date)
      #LOG('c_price',0,c_price)
      self.assertEquals(round(c_price,2), e_price)
  
  """
  09BIS
  """
  def stepTestLinearAmortisationPriceCalculationBIS(self, sequence=None, sequence_list=None, **kw):
    """
    Test calculated prices
    """
    item = sequence.get('item')
    price_list = [
           (DateTime('2001/01/01'), 8750.00),
           (DateTime('2002/01/01'), 6250.00),
           (DateTime('2003/01/01'), 3750.00),
           (DateTime('2003/12/31'), 1250.00),
           (DateTime('2004/01/01'), 1243.17),
           (DateTime('2005/01/01'), 0),
           (DateTime('2006/01/01'), 0),
           (DateTime('2020/01/01'), 0),
           ]
    for date, e_price in price_list:
      c_price = item.getAmortisationPrice(at_date=date)
      #LOG('testing amortisation price at date', 0, date)
      #LOG('c_price',0,c_price)
      self.assertEquals(round(c_price,2), e_price)

  def stepTestDegressiveAmortisationPriceCalculation(self, sequence=None, sequence_list=None, **kw):
    """
    Test calculated prices
    """
    item = sequence.get('item')
    price_list = [
           (DateTime('2001/01/01'), 6666.67),
           (DateTime('2002/01/01'), 4444.44),
           (DateTime('2003/01/01'), 2962.96),
           (DateTime('2003/02/01'), 2880.66),
           (DateTime('2003/02/16'), 2839.51),
           (DateTime('2004/01/01'), 1975.31),
           (DateTime('2005/01/01'), 987.65),
           (DateTime('2006/01/01'), 0),
           (DateTime('2020/01/01'), 0),
           ]
    for date, e_price in price_list:
      c_price = item.getAmortisationPrice(at_date=date)
      #LOG('testing amortisation price at date', 0, date)
      self.assertEquals(round(c_price,2), e_price)
      
    
  def stepTestUncontinuousDegressiveAmortisationPriceCalculation(self, sequence=None, sequence_list=None, **kw):
    """
    Test calculated prices
    """
    item = sequence.get('item')
    price_list = [
           (DateTime('2001/01/01'), 6666.67),
           (DateTime('2002/01/01'), 4444.44),
           (DateTime('2003/01/01'), 2962.96),
           (DateTime('2003/02/01'), 2880.66),
           (DateTime('2003/02/16'), 2839.51),
           (DateTime('2004/01/01'), 9857.14),
           (DateTime('2005/01/01'), 6336.73),
           (DateTime('2006/01/01'), 4073.62),
           (DateTime('2020/01/01'), 0.),
           ]
    for date, e_price in price_list:
      c_price = item.getAmortisationPrice(at_date=date)
      #LOG('testing amortisation price at date', 0, date)
      self.assertEquals(round(c_price,2), e_price)
      
    
  def stepTestActualUseAmortisationPriceCalculation(self, sequence=None, sequence_list=None, **kw):
    """
    Test calculated prices
    """
    item = sequence.get('item')
    price_list = [
           (DateTime('2001/01/01'), 7428.57),
           (DateTime('2002/01/01'), 4857.14),
           (DateTime('2003/01/01'), 2285.71),
           (DateTime('2003/02/01'), 2071.43),
           (DateTime('2003/02/16'), 1964.29),
           (DateTime('2003/07/01'), 1000.00),
           (DateTime('2004/01/01'), 800),
           (DateTime('2005/01/01'), 400),
           (DateTime('2006/01/01'), 0),
           (DateTime('2020/01/01'), 0),
           ]
    for date, e_price in price_list:
      c_price = item.getAmortisationPrice(at_date=date)
      #LOG('testing amortisation price at date', 0, date)
      self.assertEquals(round(c_price,2), e_price)
      
    
  def stepTestNoAmortisationMethodPriceCalculation(self, sequence=None, sequence_list=None, **kw):
    """
    Test calculated prices
    """
    item = sequence.get('item')
    price_list = [
           (DateTime('2001/01/01'), 10000),
           (DateTime('2002/01/01'), 10000),
           (DateTime('2003/01/01'), 10000),
           (DateTime('2003/02/01'), 10000),
           (DateTime('2003/02/16'), 10000),
           (DateTime('2004/01/01'), 12000),
           (DateTime('2005/01/01'), 12000),
           (DateTime('2006/01/01'), 12000),
           (DateTime('2020/01/01'), 12000),
           ]
    for date, e_price in price_list:
      c_price = item.getAmortisationPrice(at_date=date)
      #LOG('testing amortisation price at date', 0, date)
      self.assertEquals(round(c_price,2), e_price)
      
  
  def _createExpectedMovement(self, date, quantity, source=None, destination=None,
                              source_section=None, destination_section=None):
    self.id_simulation+=1
    r_dict = {'id':self.id_simulation,'start_date':DateTime(date), 'stop_date':DateTime(date), 
              'quantity':quantity, 'resource':'currency_module/EUR'}
    my_account_dict = dict(self.account_dict)
    my_account_dict.update(self.monthly_dict)
    my_extra_account_dict = dict(self.extra_account_dict)
    my_extra_account_dict.update(self.extra_monthly_dict)
    for name, prop in (('source',source), ('destination',destination)):
      if prop is None:
        r_dict[name] = None
      elif prop.split('_')[-1] == 'extra':
        r_dict[name] = my_extra_account_dict['_'.join(prop.split('_')[:-1])]
      else:
        r_dict[name] = my_account_dict[prop]
    for name, prop in (('source_section_value', source_section), ('destination_section_value', destination_section)):
      if prop is None:
        r_dict[name] = None
      else:
        r_dict[name] = self.getOrganisationModule()[prop]
    return r_dict

        
  def stepTestLinearAmortisationSimulationBuild(self, sequence=None, sequence_list=None, **kw):
    """
    Test 09
    Test built simulation for linear amortisation
    """
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 10000, 'input_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'A', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 1666.67, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -1666.67, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 1666.67, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -1666.67, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 1666.67, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -1666.67, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 833.33, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -833.33, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 833.33, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -833.33, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2005/01/01', 1666.67, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2005/01/01', -1666.67, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2006/01/01', 1666.67, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2006/01/01', -1666.67, 'depreciation_account', None, 'A', None))
        
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
  
  """
  09BIS
  """
  def stepTestLinearAmortisationSimulationBuildBIS(self, sequence=None, sequence_list=None, **kw):
    """
    Test built simulation for linear amortisation
    """
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/07/01', 10000, 'input_account', None, 'orga', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/07/01', -10000, 'immobilisation_account', None, 'orga', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/12/31', 1250.00, 'amortisation_account', None, 'orga', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/12/31', -1250.00, 'depreciation_account', None, 'orga', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/12/31', 2500.00, 'amortisation_account', None, 'orga', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/12/31', -2500.00, 'depreciation_account', None, 'orga', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/12/31', 2500.00, 'amortisation_account', None, 'orga', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/12/31', -2500.00, 'depreciation_account', None, 'orga', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/12/31', 2500.00, 'amortisation_account', None, 'orga', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/12/31', -2500.00, 'depreciation_account', None, 'orga', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/12/31', 1250.00, 'amortisation_account', None, 'orga', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/12/31', -1250.00, 'depreciation_account', None, 'orga', None))


    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
    
  def stepTestUncontinuousDegressiveAmortisationSimulationBuild(self, sequence=None, sequence_list=None, **kw):
    """
    Test built simulation for uncontinuous degressive amortisation
    """
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 10000, 'input_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'A', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 3333.33, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -3333.33, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 2222.22, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -2222.22, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 1481.48, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -1481.48, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 493.83, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -493.83, 'depreciation_account', None, 'A', None))
    # Unimmobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/07/01', -7530.86, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/07/01', 10000, 'immobilisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/07/01', -2469.14, 'output_account', None, 'A', None))
    # New immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/07/01', 12000, 'input_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/07/01', -12000, 'immobilisation_account', None, 'A', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 2142.86, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -2142.86, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2005/01/01', 3520.41, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2005/01/01', -3520.41, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2006/01/01', 2263.12, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2006/01/01', -2263.12, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2007/01/01', 1454.86, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2007/01/01', -1454.86, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2008/01/01', 935.27, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2008/01/01', -935.27, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2009/01/01', 841.74, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2009/01/01', -841.74, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2010/01/01', 841.74, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2010/01/01', -841.74, 'depreciation_account', None, 'A', None))
    
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
    
  
  def stepTestNoAmortisationMethodSimulationBuild(self, sequence=None, sequence_list=None, **kw):
    """
    Test built simulation for no amortisation method
    """
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 10000, 'input_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'A', None))
    # No annuity
    # Unimmobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/07/01', 10000, 'immobilisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/07/01', -10000, 'output_account', None, 'A', None))
    # New immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/07/01', 12000, 'input_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/07/01', -12000, 'immobilisation_account', None, 'A', None))
    # No annuity
    
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
    
  
  def stepTestSimulationBuildForContinuousMethodWithoutOwnerChange(self, sequence=None, sequence_list=None, **kw):
    """
    Test built simulation for a linear amortisation method without owner change
    """
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 9000, 'input_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 2000, 'extra_cost_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -1000, 'immobilisation_vat_account', None, 'Aa', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 3333.33, 'amortisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -3333.33, 'depreciation_account', None, 'Aa', None))
    # Account transfer
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 3333.33, 'amortisation_account_extra', 'amortisation_account', 'Aa', 'Aa'))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -10000, 'immobilisation_account_extra', 'immobilisation_account', 'Aa', 'Aa'))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -3333.33, 'depreciation_account_extra', 'depreciation_account', 'Aa', 'Aa'))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 3333.33, 'amortisation_account_extra', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -3333.33, 'depreciation_account_extra', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 3333.33, 'amortisation_account_extra', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -3333.33, 'depreciation_account_extra', None, 'Aa', None))
    
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
    
  
  def stepTestSimulationBuildForContinuousMethodWithOwnerChange(self, sequence=None, sequence_list=None, **kw):
    """
    Test built simulation for a linear amortisation method with owner change but no actual owner (ie group) change
    """
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 9000, 'input_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 2000, 'extra_cost_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -1000, 'immobilisation_vat_account', None, 'Aa', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 3333.33, 'amortisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -3333.33, 'depreciation_account', None, 'Aa', None))
    # Account transfer
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 3333.33, 'amortisation_account', 'amortisation_account', 'Ab', 'Aa'))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -10000, 'immobilisation_account', 'immobilisation_account', 'Ab', 'Aa'))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 3333.33, 'amortisation_account', None, 'Ab', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -3333.33, 'depreciation_account', None, 'Ab', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 3333.33, 'amortisation_account', None, 'Ab', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -3333.33, 'depreciation_account', None, 'Ab', None))
    
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
    
  
  def stepTestSimulationBuildForContinuousMethodWithActualOwnerChange(self, sequence=None, sequence_list=None, **kw):
    """
    Test built simulation for a linear amortisation method with actual owner change (ie group)
    """
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 9000, 'input_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 2000, 'extra_cost_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -1000, 'immobilisation_vat_account', None, 'Aa', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 3333.33, 'amortisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -3333.33, 'depreciation_account', None, 'Aa', None))
    # Unimmobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -3333.33, 'amortisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 10000, 'immobilisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -6666.67, 'output_account', None, 'Aa', None))
    # New immobilisation for new owner
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 6666.67, 'input_account', None, 'Ba', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -6666.67, 'immobilisation_account', None, 'Ba', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 3333.33, 'amortisation_account', None, 'Ba', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -3333.33, 'depreciation_account', None, 'Ba', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 3333.33, 'amortisation_account', None, 'Ba', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -3333.33, 'depreciation_account', None, 'Ba', None))
    
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
    
  
  def stepTestSimulationBuildForUncontinuousMethodWithoutOwnerChange(self, sequence=None, sequence_list=None, **kw):
    """
    Test built simulation for a uncontinuous degressive amortisation method without owner change
    """
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 9000, 'input_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 2000, 'extra_cost_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -1000, 'immobilisation_vat_account', None, 'Aa', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 6666.67, 'amortisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -6666.67, 'depreciation_account', None, 'Aa', None))
    # Unimmobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -6666.67, 'amortisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 10000, 'immobilisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -3333.33, 'output_account', None, 'Aa', None))
    # New immobilisation for new owner
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 12000, 'input_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -12000, 'immobilisation_account_extra', None, 'Aa', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 8000, 'amortisation_account_extra', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -8000, 'depreciation_account_extra', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 2666.67, 'amortisation_account_extra', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -2666.67, 'depreciation_account_extra', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 1333.33, 'amortisation_account_extra', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -1333.33, 'depreciation_account_extra', None, 'Aa', None))
    
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
    
  
  def stepTestSimulationBuildForUncontinuousMethodWithOwnerChange(self, sequence=None, sequence_list=None, **kw):
    """
    Test built simulation for a uncontinuous degressive amortisation method with owner change but no actual owner change
    """
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 9000, 'input_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 2000, 'extra_cost_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -1000, 'immobilisation_vat_account', None, 'Aa', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 6666.67, 'amortisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -6666.67, 'depreciation_account', None, 'Aa', None))
    # Unimmobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -6666.67, 'amortisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 10000, 'immobilisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -3333.33, 'output_account', None, 'Aa', None))
    # New immobilisation for new owner
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 12000, 'input_account', None, 'Ab', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -12000, 'immobilisation_account', None, 'Ab', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 8000, 'amortisation_account', None, 'Ab', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -8000, 'depreciation_account', None, 'Ab', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 2666.67, 'amortisation_account', None, 'Ab', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -2666.67, 'depreciation_account', None, 'Ab', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 1333.33, 'amortisation_account', None, 'Ab', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -1333.33, 'depreciation_account', None, 'Ab', None))
    
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
    
    
  def stepTestSimulationBuildForUncontinuousMethodWithActualOwnerChange(self, sequence=None, sequence_list=None, **kw):
    """
    Test built simulation for a uncontinuous degressive amortisation method with actual owner change
    """
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 9000, 'input_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 2000, 'extra_cost_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -1000, 'immobilisation_vat_account', None, 'Aa', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 6666.67, 'amortisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -6666.67, 'depreciation_account', None, 'Aa', None))
    # Unimmobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -6666.67, 'amortisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 10000, 'immobilisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -3333.33, 'output_account', None, 'Aa', None))
    # New immobilisation for new owner
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 12000, 'input_account', None, 'Ba', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -12000, 'immobilisation_account', None, 'Ba', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 8000, 'amortisation_account', None, 'Ba', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -8000, 'depreciation_account', None, 'Ba', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 2666.67, 'amortisation_account', None, 'Ba', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -2666.67, 'depreciation_account', None, 'Ba', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 1333.33, 'amortisation_account', None, 'Ba', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -1333.33, 'depreciation_account', None, 'Ba', None))
    
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
        
  
  def stepTestSimulationBuildForNoChangeMethodWithoutOwnerChange(self, sequence=None, sequence_list=None, **kw):
    """
    Test built simulation for a no change amortisation method without owner change
    """
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 9000, 'input_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 2000, 'extra_cost_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -1000, 'immobilisation_vat_account', None, 'Aa', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 3333.33, 'amortisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -3333.33, 'depreciation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 3333.33, 'amortisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -3333.33, 'depreciation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 3333.33, 'amortisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -3333.33, 'depreciation_account', None, 'Aa', None))
    
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
    
  
  def stepTestSimulationBuildForNoChangeMethodWithOwnerChange(self, sequence=None, sequence_list=None, **kw):
    """
    Test built simulation for a no change amortisation method with owner change but no actual owner (ie group) change
    """
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 9000, 'input_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 2000, 'extra_cost_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -1000, 'immobilisation_vat_account', None, 'Aa', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 3333.33, 'amortisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -3333.33, 'depreciation_account', None, 'Aa', None))
    # Account transfer
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 3333.33, 'amortisation_account', 'amortisation_account', 'Ab', 'Aa'))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -10000, 'immobilisation_account', 'immobilisation_account', 'Ab', 'Aa'))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 3333.33, 'amortisation_account', None, 'Ab', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -3333.33, 'depreciation_account', None, 'Ab', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 3333.33, 'amortisation_account', None, 'Ab', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -3333.33, 'depreciation_account', None, 'Ab', None))
    
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
    
  
  def stepTestSimulationBuildForNoChangeMethodWithActualOwnerChange(self, sequence=None, sequence_list=None, **kw):
    """
    Test built simulation for a no change amortisation method with actual owner change (ie group)
    """
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 9000, 'input_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 2000, 'extra_cost_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -1000, 'immobilisation_vat_account', None, 'Aa', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 3333.33, 'amortisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -3333.33, 'depreciation_account', None, 'Aa', None))
    # Unimmobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -3333.33, 'amortisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 10000, 'immobilisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -6666.67, 'output_account', None, 'Aa', None))
    # New immobilisation for new owner
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 6666.67, 'input_account', None, 'Ba', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -6666.67, 'immobilisation_account', None, 'Ba', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 3333.33, 'amortisation_account', None, 'Ba', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -3333.33, 'depreciation_account', None, 'Ba', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 3333.33, 'amortisation_account', None, 'Ba', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -3333.33, 'depreciation_account', None, 'Ba', None))
    
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
    
  """
  TEST 17
  """
  def stepTestSimulationBuildForMonthlyAmortisation(self, sequence=None, sequence_list=None, **kw):
    """
    Test built simulation for a linear amortisation method with a monthly amortisation
    """
    def createMonthlyAnnuityList(start_date, stop_date, month_value, account, section):
      return_list = []
      current_date = start_date
      while DateTime(current_date) <= DateTime(stop_date):
        return_list.append(self._createExpectedMovement(
              current_date, month_value, account, None, section, None))
        year, month, day = [int(x) for x in current_date.split('/')]
        month += 1
        if month == 13:
          month = 1
          year += 1
        current_date = '%s/%s/%s' % (year, month, day)
      return return_list
        
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation 2000/01/01
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 10000, 'input_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 2000, 'extra_cost_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -11000, 'immobilisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -1000, 'immobilisation_vat_account', None, 'Aa', None))
    # Annuities
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2000/02/01', '2001/01/01', 277.78, 'amortisation_account', 'Aa'))  # 3333.33/12
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2000/02/01', '2001/01/01', -277.78, 'monthly_amortisation_account', 'Aa'))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 3333.33, 'monthly_amortisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -3333.33, 'depreciation_account', None, 'Aa', None))
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2001/02/01', '2002/01/01', 277.78, 'amortisation_account', 'Aa'))
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2001/02/01', '2002/01/01', -277.78, 'monthly_amortisation_account', 'Aa'))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 3333.33, 'monthly_amortisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -3333.33, 'depreciation_account', None, 'Aa', None))
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2002/02/01', '2002/03/01', 277.78, 'amortisation_account', 'Aa'))
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2002/02/01', '2002/03/01', -277.78, 'monthly_amortisation_account', 'Aa'))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 555.56, 'monthly_amortisation_account', None, 'Aa', None)) # 3333.33/6
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -555.56, 'depreciation_account', None, 'Aa', None))
    # Optional transfer 2002/03/01
    # Annuities
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2002/04/01', '2002/04/16', 277.78, 'amortisation_account', 'Aa'))
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2002/04/01', '2002/04/16', -277.78, 'monthly_amortisation_account_extra', 'Aa'))
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2002/05/01', '2002/05/01', 138.89, 'amortisation_account', 'Aa')) # 277.78 / 2
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2002/05/01', '2002/05/01', -138.89, 'monthly_amortisation_account_extra', 'Aa'))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 416.67, 'monthly_amortisation_account_extra', None, 'Aa', None)) # 277.78 * 1.5
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -416.67, 'depreciation_account', None, 'Aa', None))
    # Optional transfer 2002/04/16
    # Annuities
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2002/05/01', '2002/06/01', 138.89, 'amortisation_account', 'Aa')) # 277.78 / 2
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2002/05/01', '2002/06/01', -138.89, 'monthly_amortisation_account', 'Aa'))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 277.78, 'monthly_amortisation_account', None, 'Aa', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -277.78, 'depreciation_account', None, 'Aa', None))
    # Account transfer 2002/05/16
    e_simulation_movement_list.append(self._createExpectedMovement( # 6666.67 + 277.78 * 4.5
              '2002/05/16', 7916.67, 'amortisation_account', 'amortisation_account', 'Ab', 'Aa'))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/05/16', -11000, 'immobilisation_account', 'immobilisation_account', 'Ab', 'Aa'))
    # Annuities
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2002/06/01', '2002/07/01', 138.89, 'amortisation_account', 'Ab'))
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2002/06/01', '2002/07/01', -138.89, 'monthly_amortisation_account', 'Ab'))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 277.78, 'monthly_amortisation_account', None, 'Ab', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -277.78, 'depreciation_account', None, 'Ab', None))
    # Unimmobilisation 2002/06/16
    e_simulation_movement_list.append(self._createExpectedMovement( # 6666.67 + 277.78 * 5.5
              '2002/06/16', -8194.44, 'amortisation_account', None, 'Ab', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/06/16', 11000, 'immobilisation_account', None, 'Ab', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/06/16', -2805.56, 'output_account', None, 'Ab', None))
    # New immobilisation for new owner 2002/06/16
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/06/16', 2805.56, 'input_account', None, 'Ba', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/06/16', -2805.56, 'immobilisation_account', None, 'Ba', None))
    # Annuities
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2002/07/01', '2002/07/01', 150.46, 'amortisation_account', 'Ba')) # (1805.56 / 6) / 2
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2002/07/01', '2002/07/01', -150.46, 'monthly_amortisation_account', 'Ba'))
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2002/08/01', '2002/12/01', 300.93, 'amortisation_account', 'Ba')) # 1805.56 / 6
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2002/08/01', '2002/12/01', -300.93, 'monthly_amortisation_account', 'Ba'))
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2003/01/01', '2003/01/01', 150.46, 'amortisation_account', 'Ba'))
    e_simulation_movement_list.extend(createMonthlyAnnuityList(
              '2003/01/01', '2003/01/01', -150.46, 'monthly_amortisation_account', 'Ba'))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 1805.56, 'monthly_amortisation_account', None, 'Ba', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -1805.56, 'depreciation_account', None, 'Ba', None))

    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)


  def _testSimulationBuild(self, c_simulation_movement_list, e_simulation_movement_list):
    for c_movement in c_simulation_movement_list:
      LOG('c_movement %s :' % c_movement, 0, 
       'date=%s\n, source=%s\n, source_section=%s\n, destination=%s\n, destination_section=%s\n, quantity=%s\n, resource=%s\n, profit_quantity=%s\n' % (
          (c_movement.getStopDate(), c_movement.getSource(), c_movement.getSourceSection(),
           c_movement.getDestination(), c_movement.getDestinationSection(), c_movement.getQuantity(),
           c_movement.getResource(), c_movement.getProfitQuantity())
         )
      )
      e_found_movement = None
      e_cursor = 0
      LOG('len e_simulation_movement_list start',0,len(e_simulation_movement_list))
      while e_cursor < len(e_simulation_movement_list) and e_found_movement is None:
        e_movement = e_simulation_movement_list[e_cursor]
        wrong_movement = 0
        key_cursor = 0
        key_list = e_movement.keys()
        key_list.remove('id')
        while key_cursor < len(key_list) and not wrong_movement:
          key = key_list[key_cursor]
          e_value = e_movement[key]
          key = 'get' + ''.join([k.capitalize() for k in key.split('_')])
          c_value = getattr(c_movement,key)()
          is_float = 0
          try:
            if type(c_value) != type(DateTime()):
              c_value=float(c_value)
              is_float = 1
          except:
            pass
          if is_float:
            wrong_movement = (round(c_value,2) != round(e_value,2))
          else:
            wrong_movement = (c_value != e_value)
          key_cursor += 1 
          LOG('_testSimulationBuild',0,'key:%s, c_value:%s e_value:%s ' % (key, c_value,e_value))
        if not wrong_movement:
          e_found_movement = e_movement
        e_cursor += 1
        #LOG('_testSimulationBuild',0,'wrong movement %s' % wrong_movement)
      if e_found_movement is None:
        LOG('No expected movement found for this calculated one !',0,c_movement.getRelativeUrl())
        LOG('len e_simulation_movement_list after fail',0,len(e_simulation_movement_list))
        self.failUnless(e_found_movement is not None)
      e_simulation_movement_list.remove(e_found_movement)
    if len(e_simulation_movement_list) > 0:
      LOG('More expected movements than calculated ! Remaining expected ones are', 0, e_simulation_movement_list)
      self.assertEquals(len(e_simulation_movement_list),0)
      
  def _buildExpectedTransaction(self, date, source_section, destination_section, causality_state, causality_list=[]):
    self.id_transaction+=1
    r_dict = {'id':self.id_transaction,'start_date':DateTime(date), 'stop_date':DateTime(date), 
              'resource':'currency_module/EUR', 'line_list':[],
              'causality_state':causality_state}
    for name, prop in (('source_section_value', source_section), ('destination_section_value', destination_section)):
      if prop is None:
        r_dict[name] = None
      else:
        r_dict[name] = self.getOrganisationModule()[prop]
    causality_value_list = []
    for causality in causality_list:
      causality_value_list.append(self.getItemModule()[causality])
    if len(causality_value_list) != 0:
      r_dict['causality_value_list'] = causality_value_list
    return r_dict

  def _buildExpectedTransactionLine(self, source, destination, quantity):
    r_dict = {'quantity':quantity}
    my_account_dict = dict(self.account_dict)
    my_account_dict.update(self.monthly_dict)
    my_extra_account_dict = dict(self.extra_account_dict)
    my_extra_account_dict.update(self.extra_monthly_dict)
    for name, prop in (('source',source), ('destination',destination)):
      if prop is None:
        r_dict[name] = None
      elif prop.split('_')[-1] == 'extra':
        r_dict[name] = my_extra_account_dict['_'.join(prop.split('_')[:-1])]
      else:
        r_dict[name] = my_account_dict[prop]
    return r_dict

  def stepTestPartialAccountingBuild(self, sequence=None, sequence_list=None, **kw):
    """
    Test partial accounting build, based on a single movement of 10000 for a 4 year linear amortisation
    on the 2000/01/01, and partial build is done with at_date=2002/01/01 and items = 1 & 2
    """
    e_transaction_list = []
    transaction = self._buildExpectedTransaction('2000/01/01','A',None,self.solved,['item1','item2'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('input_account',None,20000),
                                self._buildExpectedTransactionLine('immobilisation_account',None,-20000)]
    e_transaction_list.append(transaction)
    transaction = self._buildExpectedTransaction('2001/01/01','A',None,self.solved,['item1','item2'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,5000),
                                self._buildExpectedTransactionLine('depreciation_account',None,-5000)]
    e_transaction_list.append(transaction)                                
    transaction = self._buildExpectedTransaction('2002/01/01','A',None,self.solved,['item1','item2'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,5000),
                                self._buildExpectedTransactionLine('depreciation_account',None,-5000)]
    e_transaction_list.append(transaction)
    
    c_transaction_list = self.getPortal().portal_catalog(portal_type='Amortisation Transaction')
    c_transaction_list = [o.getObject() for o in c_transaction_list]
    self._testAccountingBuild(c_transaction_list, e_transaction_list)
    
    
  def stepTestMultiItemAccountingBuild(self, sequence=None, sequence_list=None, **kw):
    """
    Test accounting build based on a single movement of 10000 for a 4 year linear amortisation
    on the 2000/01/01 for 3 items, with complete build
    """
    e_transaction_list = []
    transaction = self._buildExpectedTransaction('2000/01/01','A',None,self.solved,['item1','item2','item3'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('input_account',None,30000),
                                self._buildExpectedTransactionLine('immobilisation_account',None,-30000)]
    e_transaction_list.append(transaction)
    transaction = self._buildExpectedTransaction('2001/01/01','A',None,self.solved,['item1','item2','item3'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,7500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-7500)]
    e_transaction_list.append(transaction)                                
    transaction = self._buildExpectedTransaction('2002/01/01','A',None,self.solved,['item1','item2','item3'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,7500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-7500)]
    e_transaction_list.append(transaction)                                
    transaction = self._buildExpectedTransaction('2003/01/01','A',None,self.solved,['item1','item2','item3'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,7500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-7500)]
    e_transaction_list.append(transaction)                               
    transaction = self._buildExpectedTransaction('2004/01/01','A',None,self.solved,['item1','item2','item3'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,7500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-7500)]
    e_transaction_list.append(transaction)
    
    c_transaction_list = self.getPortal().portal_catalog(portal_type='Amortisation Transaction')
    c_transaction_list = [o.getObject() for o in c_transaction_list]
    c_transaction_list.sort(lambda a,b: cmp(a.getStopDate(),b.getStopDate()))
    self._testAccountingBuild(c_transaction_list, e_transaction_list)
  
    
  def stepTestSimpleAccountingBuild(self, sequence=None, sequence_list=None, **kw):
    """
    Test accounting build based on a single movement of 10000 for a 4 year linear amortisation
    on the 2000/01/01 for 1 item, with complete build
    """
    e_transaction_list = []
    transaction = self._buildExpectedTransaction('2000/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('input_account',None,10000),
                                self._buildExpectedTransactionLine('immobilisation_account',None,-10000)]
    e_transaction_list.append(transaction)
    transaction = self._buildExpectedTransaction('2001/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500)]
    e_transaction_list.append(transaction)                                
    transaction = self._buildExpectedTransaction('2002/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500)]
    e_transaction_list.append(transaction)                                
    transaction = self._buildExpectedTransaction('2003/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500)]
    e_transaction_list.append(transaction)                               
    transaction = self._buildExpectedTransaction('2004/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500)]
    e_transaction_list.append(transaction)
    
    c_transaction_list = self.getPortal().portal_catalog(portal_type='Amortisation Transaction')
    c_transaction_list = [o.getObject() for o in c_transaction_list]
    #c_transaction_list.sort(lambda a,b: cmp(a.getStopDate(),b.getStopDate()))
    self._testAccountingBuild(c_transaction_list, e_transaction_list)
  
    
  def stepTestSimulationBuildAfterFirstAccountingChange(self, sequence=None, sequence_list=None, **kw):
    """
    Test accounting build based on a single movement of 10000 for a 4 year linear amortisation
    on the 2000/01/01 for 1 item, with complete build.
    Then a movement is added, at 2002/01/01, changing the owner
    """
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 10000, 'input_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'A', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -2500, 'depreciation_account', None, 'A', None))
    # Annuities set to 0 due to their link with transactions
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 0, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -0, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 0, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -0, 'depreciation_account', None, 'A', None))
    # Unimmobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -5000, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 10000, 'immobilisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -5000, 'output_account', None, 'A', None))
    # New immobilisation for new owner
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 5000, 'input_account', None, 'B', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -5000, 'immobilisation_account', None, 'B', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 2500, 'amortisation_account', None, 'B', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -2500, 'depreciation_account', None, 'B', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 2500, 'amortisation_account', None, 'B', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -2500, 'depreciation_account', None, 'B', None))
              
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
    
    
  def stepTestSimulationBuildAfterSecondAccountingChange(self, sequence=None, sequence_list=None, **kw):
    """
    Test accounting build based on a single movement of 10000 for a 4 year linear amortisation
    on the 2000/01/01 for 1 item, with complete build.
    Then a movement is added, at 2002/01/01, changing the owner, and accounting is built again.
    Then the second movement is deleted
    """
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 10000, 'input_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'A', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -2500, 'depreciation_account', None, 'A', None))
    # Annuities reset to their real value
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -2500, 'depreciation_account', None, 'A', None))              
    # Unimmobilisation, set to 0 due to their link to transactions
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -0, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 0, 'immobilisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -0, 'output_account', None, 'A', None))
    # New immobilisation for new owner, set to 0 due to their link to transactions
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 0, 'input_account', None, 'B', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -0, 'immobilisation_account', None, 'B', None))
    # Annuities, set to 0 due to their link to transactions
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 0, 'amortisation_account', None, 'B', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -0, 'depreciation_account', None, 'B', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 0, 'amortisation_account', None, 'B', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -0, 'depreciation_account', None, 'B', None))
              
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
    
    
  def stepTestSimulationBuildAfterPackingListModification(self, sequence=None, sequence_list=None, **kw):
    """
    Test accounting build based on a single movement of 10000 for a 4 year linear amortisation
    on the 2000/01/01 for 1 item, with complete build.
    Then a movement is added, at 2002/01/01, changing the owner, and accounting is built again.
    Then the second movement is deleted, and the accounting is rebuilt
    Then adopt_prevision() is launched on accounting transactions
    Then the first movement is modified, setting amortisation_account to another value
    """
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 10000, 'input_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'A', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 2500, 'amortisation_account_extra', None, 'A', None))              
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -2500, 'depreciation_account', None, 'A', None))
    # Unimmobilisation, set to 0 before
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 0, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 0, 'immobilisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 0, 'output_account', None, 'A', None))
    # Still annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 2500, 'amortisation_account_extra', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 2500, 'amortisation_account_extra', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 2500, 'amortisation_account_extra', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -2500, 'depreciation_account', None, 'A', None))
    # Immobilisation on B, set to 0 previously
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 0, 'input_account', None, 'B', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -0, 'immobilisation_account', None, 'B', None))
    # Annuities to B set to 0 previously
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 0, 'amortisation_account', None, 'B', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -0, 'depreciation_account', None, 'B', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 0, 'amortisation_account', None, 'B', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -0, 'depreciation_account', None, 'B', None))
    
              
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
    
    
  def stepTestAccountingBuildAfterFirstChange(self, sequence=None, sequence_list=None, **kw):
    """
    Test accounting build based on a single movement of 10000 for a 4 year linear amortisation
    on the 2000/01/01 for 1 item, with complete build.
    Then a movement is added, at 2002/01/01, changing the owner, and the accounting is rebuilt
    """
    e_transaction_list = []
    # Immobilisation
    transaction = self._buildExpectedTransaction('2000/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('input_account',None,10000),
                                self._buildExpectedTransactionLine('immobilisation_account',None,-10000)]
    e_transaction_list.append(transaction)
    # Annuities
    transaction = self._buildExpectedTransaction('2001/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500)]
    e_transaction_list.append(transaction)
    transaction = self._buildExpectedTransaction('2002/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500),
                                # Unimmobilisation
                                self._buildExpectedTransactionLine('amortisation_account',None,-5000),
                                self._buildExpectedTransactionLine('immobilisation_account',None,10000),
                                self._buildExpectedTransactionLine('output_account',None,-5000)]
    # Annuities ; these ones are divergent
    e_transaction_list.append(transaction)
    transaction = self._buildExpectedTransaction('2003/01/01','A',None,self.diverged,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500)]
    e_transaction_list.append(transaction)
    transaction = self._buildExpectedTransaction('2004/01/01','A',None,self.diverged,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500)]
    e_transaction_list.append(transaction)
    # Immobilisation for new owner
    transaction = self._buildExpectedTransaction('2002/01/01','B',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('input_account',None,5000),
                                self._buildExpectedTransactionLine('immobilisation_account',None,-5000)]
    e_transaction_list.append(transaction)
    # Annuities
    transaction = self._buildExpectedTransaction('2003/01/01','B',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500)]
    e_transaction_list.append(transaction)
    transaction = self._buildExpectedTransaction('2004/01/01','B',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500)]
    e_transaction_list.append(transaction)
    
    c_transaction_list = self.getPortal().portal_catalog(portal_type='Amortisation Transaction')
    c_transaction_list = [o.getObject() for o in c_transaction_list]
    self._testAccountingBuild(c_transaction_list, e_transaction_list)
  
    
  def stepTestAccountingBuildAfterSecondChange(self, sequence=None, sequence_list=None, **kw):
    """
    Test accounting build based on a single movement of 10000 for a 4 year linear amortisation
    on the 2000/01/01 for 1 item, with complete build.
    Then a movement is added, at 2002/01/01, changing the owner, and the accounting is rebuilt
    Then the second movement is deleted and the account is built again
    """
    e_transaction_list = []
    # Immobilisation
    transaction = self._buildExpectedTransaction('2000/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('input_account',None,10000),
                                self._buildExpectedTransactionLine('immobilisation_account',None,-10000)]
    e_transaction_list.append(transaction)
    # Annuities
    transaction = self._buildExpectedTransaction('2001/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500)]
    e_transaction_list.append(transaction)                                
    transaction = self._buildExpectedTransaction('2002/01/01','A',None,self.diverged,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500),
                                # Unimmobilisation, divergent
                                self._buildExpectedTransactionLine('amortisation_account',None,-5000),
                                self._buildExpectedTransactionLine('immobilisation_account',None,10000),
                                self._buildExpectedTransactionLine('output_account',None,-5000)]
    # Annuities ; these ones were not solved but are now convergent again
    e_transaction_list.append(transaction)                                
    transaction = self._buildExpectedTransaction('2003/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500)]
    e_transaction_list.append(transaction)                               
    transaction = self._buildExpectedTransaction('2004/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500)]
    e_transaction_list.append(transaction)
    # Immobilisation for new owner, divergent
    transaction = self._buildExpectedTransaction('2002/01/01','B',None,self.diverged,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('input_account',None,5000),
                                self._buildExpectedTransactionLine('immobilisation_account',None,-5000)]
    e_transaction_list.append(transaction)
    # Annuities, divergent
    transaction = self._buildExpectedTransaction('2003/01/01','B',None,self.diverged,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500)]
    e_transaction_list.append(transaction)                                
    transaction = self._buildExpectedTransaction('2004/01/01','B',None,self.diverged,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500)]
    e_transaction_list.append(transaction)
    
    c_transaction_list = self.getPortal().portal_catalog(portal_type='Amortisation Transaction')
    c_transaction_list = [o.getObject() for o in c_transaction_list]
    self._testAccountingBuild(c_transaction_list, e_transaction_list)
  
    
  def stepTestAccountingBuildAfterAdoptPrevision(self, sequence=None, sequence_list=None, **kw):
    """
    Test accounting build based on a single movement of 10000 for a 4 year linear amortisation
    on the 2000/01/01 for 1 item, with complete build.
    Then a movement is added, at 2002/01/01, changing the owner, and the accounting is rebuilt
    Then the second movement is deleted and the accounting is built again
    Then adopt_prevision() is launched
    """
    e_transaction_list = []
    # Immobilisation
    transaction = self._buildExpectedTransaction('2000/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('input_account',None,10000),
                                self._buildExpectedTransactionLine('immobilisation_account',None,-10000)]
    e_transaction_list.append(transaction)
    # Annuities
    transaction = self._buildExpectedTransaction('2001/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500)]
    e_transaction_list.append(transaction)                                
    transaction = self._buildExpectedTransaction('2002/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500),
                                # Unimmobilisation, set to 0 by solver
                                self._buildExpectedTransactionLine('amortisation_account',None,-0),
                                self._buildExpectedTransactionLine('immobilisation_account',None,0),
                                self._buildExpectedTransactionLine('output_account',None,-0),
                                self._buildExpectedTransactionLine('immobilisation_account',None,0),
                                self._buildExpectedTransactionLine('output_account',None,-0)]
    # Annuities
    e_transaction_list.append(transaction)                                
    transaction = self._buildExpectedTransaction('2003/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500)]
    e_transaction_list.append(transaction)                               
    transaction = self._buildExpectedTransaction('2004/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500)]
    e_transaction_list.append(transaction)
    # Immobilisation for new owner, set to 0 by solver
    transaction = self._buildExpectedTransaction('2002/01/01','B',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('input_account',None,0),
                                self._buildExpectedTransactionLine('immobilisation_account',None,-0),
                                self._buildExpectedTransactionLine('input_account',None,0),
                                self._buildExpectedTransactionLine('immobilisation_account',None,-0)]
    e_transaction_list.append(transaction)
    # Annuities, set to 0 by solver
    transaction = self._buildExpectedTransaction('2003/01/01','B',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,0),
                                self._buildExpectedTransactionLine('depreciation_account',None,-0),
                                self._buildExpectedTransactionLine('amortisation_account',None,0),
                                self._buildExpectedTransactionLine('depreciation_account',None,-0)]
    e_transaction_list.append(transaction)                                
    transaction = self._buildExpectedTransaction('2004/01/01','B',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,0),
                                self._buildExpectedTransactionLine('depreciation_account',None,-0),
                                self._buildExpectedTransactionLine('amortisation_account',None,0),
                                self._buildExpectedTransactionLine('depreciation_account',None,-0)]
    e_transaction_list.append(transaction)
    
    c_transaction_list = self.getPortal().portal_catalog(portal_type='Amortisation Transaction')
    c_transaction_list = [o.getObject() for o in c_transaction_list]
    self._testAccountingBuild(c_transaction_list, e_transaction_list)
  
    
  def stepTestAccountingBuildAfterPackingListModification(self, sequence=None, sequence_list=None, **kw):
    """
    Test accounting build based on a single movement of 10000 for a 4 year linear amortisation
    on the 2000/01/01 for 1 item, with complete build.
    Then a movement is added, at 2002/01/01, changing the owner, and accounting is built again.
    Then the second movement is deleted, and the accounting is rebuilt
    Then adopt_prevision() is launched on accounting transactions
    Then the first movement is modified, setting amortisation_account to another value
    """
    e_transaction_list = []
    # Immobilisation
    transaction = self._buildExpectedTransaction('2000/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('input_account',None,10000),
                                self._buildExpectedTransactionLine('immobilisation_account',None,-10000)]
    e_transaction_list.append(transaction)
    # Annuities
    transaction = self._buildExpectedTransaction('2001/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,0),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500),
                                self._buildExpectedTransactionLine('amortisation_account_extra',None,2500)]
    e_transaction_list.append(transaction)
    transaction = self._buildExpectedTransaction('2002/01/01','A',None,self.diverged,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,2500),
                                self._buildExpectedTransactionLine('amortisation_account_extra',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500),
                                # Unimmobilisation
                                self._buildExpectedTransactionLine('amortisation_account',None,-0),
                                self._buildExpectedTransactionLine('immobilisation_account',None,0),
                                self._buildExpectedTransactionLine('output_account',None,-0),
                                self._buildExpectedTransactionLine('immobilisation_account',None,0),
                                self._buildExpectedTransactionLine('output_account',None,-0)]
    # Annuities
    e_transaction_list.append(transaction)
    transaction = self._buildExpectedTransaction('2003/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,0),
                                self._buildExpectedTransactionLine('amortisation_account_extra',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500)]
    e_transaction_list.append(transaction)
    transaction = self._buildExpectedTransaction('2004/01/01','A',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,0),
                                self._buildExpectedTransactionLine('amortisation_account_extra',None,2500),
                                self._buildExpectedTransactionLine('depreciation_account',None,-2500)]
    e_transaction_list.append(transaction)
    # Immobilisation for new owner, set to 0 by solver
    transaction = self._buildExpectedTransaction('2002/01/01','B',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('input_account',None,0),
                                self._buildExpectedTransactionLine('immobilisation_account',None,-0),
                                self._buildExpectedTransactionLine('input_account',None,0),
                                self._buildExpectedTransactionLine('immobilisation_account',None,-0)]
    e_transaction_list.append(transaction)
    # Annuities, set to 0 by solver
    transaction = self._buildExpectedTransaction('2003/01/01','B',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,0),
                                self._buildExpectedTransactionLine('depreciation_account',None,-0),
                                self._buildExpectedTransactionLine('amortisation_account',None,0),
                                self._buildExpectedTransactionLine('depreciation_account',None,-0)]
    e_transaction_list.append(transaction)
    transaction = self._buildExpectedTransaction('2004/01/01','B',None,self.solved,['item1'])
    transaction['line_list'] = [self._buildExpectedTransactionLine('amortisation_account',None,0),
                                self._buildExpectedTransactionLine('depreciation_account',None,-0),
                                self._buildExpectedTransactionLine('amortisation_account',None,0),
                                self._buildExpectedTransactionLine('depreciation_account',None,-0)]
    e_transaction_list.append(transaction)

    c_transaction_list = self.getPortal().portal_catalog(portal_type='Amortisation Transaction')
    c_transaction_list = [o.getObject() for o in c_transaction_list]
    self._testAccountingBuild(c_transaction_list, e_transaction_list)

  def stepTestSimulationBuildAfterAcceptDecision(self, sequence=None, sequence_list=None, **kw):
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 10000, 'input_account', None, 'A', None))
    e_simulation_movement_list[-1]['profit_quantity'] = -5000
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'A', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -2500, 'depreciation_account', None, 'A', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -2500, 'depreciation_account', None, 'A', None))              
              
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
    
    
  def stepTestFirstSimulationBuildAfterAccountingValidation(self, sequence=None, sequence_list=None, **kw):
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 10000, 'input_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'A', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -2500, 'depreciation_account', None, 'A', None))
    # Correction movements
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 833.33, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -833.33, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 833.33, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -833.33, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 833.33, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -833.33, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 2500, 'depreciation_account', None, 'A', None))
    
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
    
    
  def stepTestSecondSimulationBuildAfterAccountingValidation(self, sequence=None, sequence_list=None, **kw):
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 10000, 'input_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'A', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -2500, 'depreciation_account', None, 'A', None))
    # Correction movements
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 2500, 'depreciation_account', None, 'A', None))
    
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
    
    
  def stepTestThirdSimulationBuildAfterAccountingValidation(self, sequence=None, sequence_list=None, **kw):
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 10000, 'input_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'A', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -2500, 'depreciation_account', None, 'A', None))
    # No more correction movement
    
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
    
    
  def stepTestFourthSimulationBuildAfterAccountingValidation(self, sequence=None, sequence_list=None, **kw):
    item = sequence.get('item')
    e_simulation_movement_list = []
    # Immobilisation
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', 10000, 'input_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2000/01/01', -10000, 'immobilisation_account', None, 'A', None))
    # Annuities
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -2500, 'depreciation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -2500, 'depreciation_account', None, 'A', None))
    # Correction movements
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', -2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', -2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', -2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', -2500, 'amortisation_account', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2001/01/01', 2500, 'amortisation_account_extra', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2002/01/01', 2500, 'amortisation_account_extra', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2003/01/01', 2500, 'amortisation_account_extra', None, 'A', None))
    e_simulation_movement_list.append(self._createExpectedMovement(
              '2004/01/01', 2500, 'amortisation_account_extra', None, 'A', None))
    
    
    applied_rule_list = item.getCausalityRelatedValueList(portal_type='Applied Rule')
    #LOG('Check number of applied rules for item', 0, item.getRelativeUrl())
    self.assertEquals(len(applied_rule_list),1)
    applied_rule = applied_rule_list[0]
    c_simulation_movement_list = applied_rule.contentValues()
    self._testSimulationBuild(c_simulation_movement_list, e_simulation_movement_list)
    
    
  def _testAccountingBuild(self, c_transaction_list, e_transaction_list):
    #self.assertEquals(len(c_transaction_list),len(e_transaction_list))
    e_removed_list = []
    for c_transaction in c_transaction_list:
      LOG('c_transaction %s :' % c_transaction, 0, 
          'date=%s\n, source_section=%s\n, destination_section=%s\n, resource=%s\n, state=%s\n, causality_list=%s\n' % (
          (c_transaction.getStopDate(), c_transaction.getSourceSection(),
           c_transaction.getDestinationSection(), c_transaction.getResource(), c_transaction.getCausalityState(),
           c_transaction.getCausalityList())
         )
      )
      e_found_transaction = None
      e_cursor = 0
      while e_cursor < len(e_transaction_list) and e_found_transaction is None:
        e_transaction = e_transaction_list[e_cursor]
        wrong_transaction = 0
        key_cursor = 0
        key_list = e_transaction.keys()
        if 'line_list' in key_list:
          key_list.remove('line_list')
        if 'id' in key_list:
          key_list.remove('id')
        while key_cursor < len(key_list) and not wrong_transaction:
          key = key_list[key_cursor]
          #LOG('key : ',0,key)
          e_value = e_transaction[key]
          #LOG('e_value : ',0,e_value)
          key = 'get' + ''.join([k.capitalize() for k in key.split('_')])
          c_value = getattr(c_transaction,key)()
          #LOG('c_value : ',0,c_value)
          is_float = 0
          try:
            if type(c_value) != type(DateTime()):
              c_value=float(c_value)
              is_float = 1
          except:
            pass
          if type(c_value) == type([]):
            c_value.sort(lambda a,b: cmp(a.getId(), b.getId()))
          if type(e_value) == type([]):
            e_value.sort(lambda a,b: cmp(a.getId(), b.getId()))
          if is_float:
            wrong_transaction = (round(c_value,2) != round(e_value,2))
          else:
            wrong_transaction = (c_value != e_value)
          key_cursor += 1
        #LOG('wrong_transaction',0,wrong_transaction)
        if not wrong_transaction:
          e_found_transaction = e_transaction
        else:
          LOG('',0,'key:%s\ncalculated:%s\n expected:%s' % (key,c_value,e_value))
        e_cursor += 1
      if e_found_transaction is None:
        LOG('No expected transaction found for this calculated one !',0,'')
        self.failUnless(e_found_transaction is not None)
      #e_transaction_list.remove(e_transaction)
      e_removed_list.append(e_transaction_list.pop(e_transaction_list.index(e_transaction)))
      e_line_list = e_transaction['line_list']
      c_line_list = c_transaction.contentValues()
      for c_line in c_line_list:
        LOG('c_line %s :' % c_line, 0, 
          'source=%s\n,destination=%s\n,quantity=%s\n' % (
          (c_line.getSource(),c_line.getDestination(),c_line.getQuantity())
          )
         )
        e_found_line = None
        e_line_cursor = 0
        while e_line_cursor < len(e_line_list) and e_found_line is None:
          e_line = e_line_list[e_line_cursor]
          wrong_line = 0
          key_cursor = 0
          key_list = e_line.keys()
          while key_cursor < len(key_list) and not wrong_line:
            key = key_list[key_cursor]
            e_value = e_line[key]
            key = 'get' + ''.join([k.capitalize() for k in key.split('_')])
            c_value = getattr(c_line,key)()
            is_float = 0
            try:
              if type(c_value) != type(DateTime()):
                c_value=float(c_value)
                is_float = 1
            except:
              pass
            if is_float:
              wrong_line = (round(c_value,2) != round(e_value,2))
            else:
              wrong_line = (c_value != e_value)
            key_cursor += 1
          if not wrong_line:
            e_found_line = e_line
	  else:
	    LOG('',0,'key:%s\ncalculated:%s\n expected:%s' % (key,c_value,e_value))
          e_line_cursor += 1
        if e_found_line is None:
          LOG('No expected line found for this calculated one !',0,'')
          self.failUnless(e_found_line is not None)
        e_line_list.remove(e_found_line)
      if len(e_line_list) > 0:
        LOG('More expected lines than calculated ! Remaining expected ones are', 0, e_line_list)
        self.assertEquals(len(e_line_list),0)

    if len(e_transaction_list) > 0:
      LOG('More expected transaction than calculated ! Remaining expected ones are', 0, e_transaction_list)
      self.assertEquals(len(e_transaction_list),0)

class TestImmobilisation(TestImmobilisationMixin):

  run_all_test = 1
                
  def stepSetTest01SequenceData(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(destination_section = self.getOrganisationModule()["A"],
                  datetime = self.datetime,
                  item_list_list = [[ self.getItemModule()['item1'] ]]
                  )

  def test_01_singlePackingListImmobilisationStateChange(self, quiet=0, run=run_all_test):
    # Test if an added packing list has a correct immobilisation state
    if not run: return
    if not quiet:
      message = '\nTest Single Packing List Immobilisation State Change'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest01SequenceData \
                       CreatePackingList \
                       TestPackingListCalculatingImmobilisationState \
                       Tic \
                       TestPackingListValidImmobilisationState \
                       AggregateItems \
                       TestPackingListCalculatingImmobilisationState \
                       Tic \
                       TestPackingListValidImmobilisationState \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    
  
  def stepSetTest02SequenceData(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(destination_section = self.getOrganisationModule()["A"],
                  datetime= [self.datetime, self.datetime+5, self.datetime+10],
                  item_list_list = [[ self.getItemModule()['item2'] ]]
                  )

  def test_02_singleItemImmobilisationStateChange(self, quiet=0, run=run_all_test):
    # Test if an edit on a preceding delivery switches the following in calculating state
    if not run: return
    if not quiet:
      message = '\nTest Single Item Immobilisation State Change'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest02SequenceData \
                       DeleteAllPackingLists Tic \
                       CreatePackingList \
                       AggregateItems \
                       CreatePackingList \
                       AggregateItems \
                       CreatePackingList \
                       AggregateItems \
                       Tic \
                       UseSecondPackingList \
                       EditPackingList \
                       TestPackingListCalculatingImmobilisationState \
                       UseFirstPackingList \
                       TestPackingListValidImmobilisationState \
                       UseThirdPackingList \
                       TestPackingListCalculatingImmobilisationState \
                       Tic \
                       TestPackingListValidImmobilisationState \
                       UseSecondPackingList \
                       TestPackingListValidImmobilisationState \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    
                       
  def test_03_complexItemStructureImmobilisationStateChange(self, quiet=0, run=run_all_test):
    # Test on a complex structure if an edit on a PL changes correctly immobilisation states
    if not run: return
    if not quiet:
      message = '\nTest Complex Item Structure Immobilisation State Change'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'DeleteAllPackingLists Tic \
                       CreateComplexPackingListStructure \
                       Tic \
                       UseSecondPackingList \
                       EditPackingList \
                       TestPackingListCalculatingImmobilisationState \
                       UseFirstPackingList \
                       TestPackingListValidImmobilisationState \
                       UseThirdPackingList \
                       TestPackingListValidImmobilisationState \
                       UseFourthPackingList \
                       TestPackingListValidImmobilisationState \
                       Tic \
                       UseFirstPackingList \
                       EditPackingList \
                       TestPackingListCalculatingImmobilisationState \
                       UseSecondPackingList \
                       TestPackingListValidImmobilisationState \
                       UseThirdPackingList \
                       TestPackingListCalculatingImmobilisationState \
                       UseFourthPackingList \
                       TestPackingListCalculatingImmobilisationState \
                       Tic \
                       UseThirdPackingList \
                       EditPackingList \
                       TestPackingListCalculatingImmobilisationState \
                       UseFirstPackingList \
                       TestPackingListValidImmobilisationState \
                       UseSecondPackingList \
                       TestPackingListValidImmobilisationState \
                       UseFourthPackingList \
                       TestPackingListCalculatingImmobilisationState \
                       Tic \
                       EditPackingList \
                       TestPackingListCalculatingImmobilisationState \
                       UseFirstPackingList \
                       TestPackingListValidImmobilisationState \
                       UseSecondPackingList \
                       TestPackingListValidImmobilisationState \
                       UseThirdPackingList \
                       TestPackingListValidImmobilisationState \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    
    
  def stepSetTest04SequenceData(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(item = self.getItemModule()['item5'],
                  destination_section = self.getOrganisationModule()["A"],
                  amortisation_method = self.linear_method)

  def stepTest04ModifyPackingList(self, sequence=None, sequence_list=None, **kw):
    pl = sequence.get('packing_list')
    if pl is None: pl = sequence.get('packing_list_list', [])[-1]
    for line in pl.contentValues():
      line.edit(amortisation_start_price=None)

  def test_04_TestContinuousMethodMovementValidity(self, quiet=0, run=run_all_test):
    # Create a continuous method with some movements, then test their validity
    # by invalidating some of them
    if not run: return
    if not quiet:
      message = '\nTest Continuous Method Movement Validity'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest04SequenceData \
                       DeleteAllPackingLists Tic \
                       CreatePackingListsForContinuousAmortisationPeriodList \
                       Tic \
                       UseFirstPackingList \
                       TestPackingListValidImmobilisationState \
                       UseSecondPackingList \
                       TestPackingListValidImmobilisationState \
                       UseThirdPackingList \
                       TestPackingListValidImmobilisationState \
                       UseFourthPackingList \
                       TestPackingListValidImmobilisationState \
                       UseFirstPackingList \
                       Test04ModifyPackingList \
                       UseSecondPackingList \
                       TestPackingListCalculatingImmobilisationState \
                       UseThirdPackingList \
                       TestPackingListCalculatingImmobilisationState \
                       UseFourthPackingList \
                       TestPackingListCalculatingImmobilisationState \
                       Tic \
                       UseFirstPackingList \
                       TestPackingListInvalidImmobilisationState \
                       UseSecondPackingList \
                       TestPackingListValidImmobilisationState \
                       UseThirdPackingList \
                       TestPackingListValidImmobilisationState \
                       UseFourthPackingList \
                       TestPackingListValidImmobilisationState \
                       UseSecondPackingList \
                       DeletePackingList \
                       UseFirstPackingList \
                       TestPackingListInvalidImmobilisationState \
                       UseThirdPackingList \
                       TestPackingListCalculatingImmobilisationState \
                       UseFourthPackingList \
                       TestPackingListCalculatingImmobilisationState \
                       Tic \
                       UseThirdPackingList \
                       TestPackingListInvalidImmobilisationState \
                       UseFourthPackingList \
                       TestPackingListInvalidImmobilisationState \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    
    
  def stepSetTest05SequenceData(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(item = self.getItemModule()['item6'],
                  amortisation_method = self.linear_method)

  def test_05_TestImmobilisationPeriodsWithContinuousMethodDuringContinuousTime(self, quiet=0, run=run_all_test):
    # Test the calculated amortisation periods with a continuous amortisation method
    # and with no stop of immobilisation
    if not run: return
    if not quiet:
      message = '\nTest Immobilisation Periods With Continuous Method During Continuous Time'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest05SequenceData \
                       CreatePackingListsForContinuousAmortisationPeriodList \
                       Tic \
                       TestLinearAmortisationImmobilisationPeriods \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    

    
  def stepSetTest06SequenceData(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(item = self.getItemModule()['item7'],
                  amortisation_method = self.linear_method)

  def test_06_TestImmobilisationPeriodsWithContinuousMethodDuringUncontinuousTime(self, quiet=0, run=run_all_test):
    # Test the calculated amortisation periods with a continuous amortisation method
    # and with stops of immobilisation in the time
    if not run: return
    if not quiet:
      message = '\nTest Immobilisation Periods With Continuous Method During Uncontinuous Time'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest06SequenceData \
                       CreatePackingListsForUncontinuousAmortisationPeriodList \
                       Tic \
                       TestLinearAmortisationImmobilisationPeriodsUncontinuous \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    


  def stepSetTest07SequenceData(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(item = self.getItemModule()['item8'],
                  amortisation_method = self.uncontinuous_degressive_method,
                  parameter_dict = {'degressive_coefficient': 2})

  def test_07_TestImmobilisationPeriodsWithUncontinuousMethodDuringContinuousTime(self, quiet=0, run=run_all_test):
    # Test the calculated amortisation periods with a uncontinuous amortisation method
    # and with no stop of immobilisation in the time
    if not run: return
    if not quiet:
      message = '\nTest Immobilisation Periods With Uncontinuous Method During Continuous Time'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest07SequenceData \
                       CreatePackingListsForContinuousAmortisationPeriodList \
                       Tic \
                       TestDegressiveAmortisationImmobilisationPeriods \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    
        
    
  def stepSetTest08SequenceData(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(item = self.getItemModule()['item9'],
                  amortisation_method = self.uncontinuous_degressive_method,
                  parameter_dict = {'degressive_coefficient': 2})

  def test_08_TestImmobilisationPeriodsWithUncontinuousMethodDuringUncontinuousTime(self, quiet=0, run=run_all_test):
    # Test the calculated amortisation periods with an uncontinuous amortisation method
    # and with stops of immobilisation in the time
    if not run: return
    if not quiet:
      message = '\nTest Immobilisation Periods With Uncontinuous Method During Uncontinuous Time'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest08SequenceData \
                       CreatePackingListsForUncontinuousAmortisationPeriodList \
                       Tic \
                       TestDegressiveAmortisationImmobilisationPeriodsUncontinuous \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    
        
    
  def stepSetTest09SequenceData(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(item = self.getItemModule()['item10'],
                  amortisation_method = self.linear_method)

  def test_09_TestAmortisationPriceAndSimulationForLinearAmortisation(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nTest Amortisation Price And Simulation For Linear Amortisation'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest09SequenceData \
                       CreatePackingListsForSimpleItemImmobilisation \
                       Tic \
                       TestLinearAmortisationPriceCalculation \
                       TestLinearAmortisationSimulationBuild \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    
        
    
  def stepSetTest10SequenceData(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(item = self.getItemModule()['item11'],
                  amortisation_method = self.degressive_method,
                  parameter_dict={'degressive_coefficient':2})

  def test_10_TestAmortisationPriceForDegressiveAmortisation(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nTest Amortisation Price For Degressive Amortisation'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest10SequenceData \
                       CreatePackingListsForSimpleItemImmobilisation \
                       Tic \
                       TestDegressiveAmortisationPriceCalculation \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    
        
    
  def stepSetTest11SequenceData(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(item = self.getItemModule()['item12'],
                  amortisation_method = self.uncontinuous_degressive_method,
                  parameter_dict={'degressive_coefficient':2})

  def test_11_TestAmortisationPriceAndSimulationForUncontinuousDegressiveAmortisation(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nTest Amortisation Price And Simulation For Uncontinuous Degressive Amortisation'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest11SequenceData \
                       CreatePackingListsForSimpleItemImmobilisation \
                       Tic \
                       TestUncontinuousDegressiveAmortisationPriceCalculation \
                       TestUncontinuousDegressiveAmortisationSimulationBuild \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    
        
    
  def stepSetTest12SequenceData(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(item = self.getItemModule()['item13'],
                  amortisation_method = self.actual_use_method,
                  parameter_dict={'durability':1000})

  def test_12_TestAmortisationPriceForActualUseDegressiveAmortisation(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nTest Amortisation Price For Actual Use Amortisation'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest12SequenceData \
                       CreatePackingListsForSimpleItemImmobilisation \
                       Tic \
                       TestActualUseAmortisationPriceCalculation \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    
        
    
  def stepSetTest13SequenceData(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(item = self.getItemModule()['item14'],
                  amortisation_method = self.no_amortisation_method,
                 )
  def test_13_TestAmortisationPriceForNoAmortisationMethod(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nTest Amortisation Price For No Amortisation Method'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest13SequenceData \
                       CreatePackingListsForSimpleItemImmobilisation \
                       Tic \
                       TestNoAmortisationMethodPriceCalculation \
                       TestNoAmortisationMethodSimulationBuild \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    


  # Test owner changes. The expected behavior is the following :
  # ----------------------------------------------------------------------------------------------
  # |                   | Owner does not change |  Owner changes but the  | Actual owner changes |
  # |                   |                       |  actual owner does not  |                      |
  # ----------------------------------------------------------------------------------------------
  # |NO_CHANGE movement |     Nothing to do     |        Transfer         |Stop immo - start immo|
  # |Continuous movement|   Optional transfer   |        Transfer         |Stop immo - start immo|
  # |       Other       | Stop immo - start immo| Stop immo - start immo  |Stop immo - start immo|
  # ----------------------------------------------------------------------------------------------
  # "Optional Transfer" means "transfer from old accounts to new ones if they change"
  # "Transfer" means "transfer all non-solded accounts from a section to another"
  # "Continuous movement" means "same method as previous period and method is continuous"
  # Note that section can change without changing owner.
  # "Actual owner changes" means "the 'group' property of both owners differ"
  def stepSetTest14SequenceData(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(item = self.getItemModule()['item15'],
                  amortisation_method = self.linear_method)
  def test_14_TestOwnerChangeSimulationForContinuousAmortisationMethod(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nTest Owner Change Simulation For Continuous Amortisation Method'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest14SequenceData \
                       CreatePackingListsForSimulationTest \
                       Tic \
                       TestSimulationBuildForContinuousMethodWithoutOwnerChange \
                       ChangeCurrentPackingListDestinationSectionForOwnerChange \
                       Tic \
                       TestSimulationBuildForContinuousMethodWithOwnerChange \
                       ChangeCurrentPackingListDestinationSectionForActualOwnerChange \
                       Tic \
                       TestSimulationBuildForContinuousMethodWithActualOwnerChange \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    
        
    
  def stepSetTest15SequenceData(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(item = self.getItemModule()['item16'],
                  amortisation_method = self.uncontinuous_degressive_method,
                  parameter_dict = {'degressive_coefficient':2})

  def test_15_TestOwnerChangeSimulationForUnContinuousAmortisationMethod(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nTest Owner Change Simulation For Uncontinuous Amortisation Method'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest15SequenceData \
                       CreatePackingListsForSimulationTest \
                       Tic \
                       TestSimulationBuildForUncontinuousMethodWithoutOwnerChange \
                       ChangeCurrentPackingListDestinationSectionForOwnerChange \
                       Tic \
                       TestSimulationBuildForUncontinuousMethodWithOwnerChange \
                       ChangeCurrentPackingListDestinationSectionForActualOwnerChange \
                       Tic \
                       TestSimulationBuildForUncontinuousMethodWithActualOwnerChange \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    


  def stepSetTest16SequenceData(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(item = self.getItemModule()['item17'],
                  amortisation_method = self.linear_method)

  def test_16_TestOwnerChangeSimulationForContinuousAmortisationMethod(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nTest Owner Change Simulation For Continuous Amortisation Method'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest16SequenceData \
                       CreatePackingListsForNoChangeMethodSimulationTest \
                       Tic \
                       TestSimulationBuildForNoChangeMethodWithoutOwnerChange \
                       ChangeCurrentPackingListDestinationSectionForOwnerChange \
                       Tic \
                       TestSimulationBuildForNoChangeMethodWithOwnerChange \
                       ChangeCurrentPackingListDestinationSectionForActualOwnerChange \
                       Tic \
                       TestSimulationBuildForNoChangeMethodWithActualOwnerChange \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    


  def stepSetTest17SequenceData(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(item = self.getItemModule()['item18'],
                  amortisation_method = self.linear_method)

  def test_17_TestMonthlyAmortisation(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nTest Monthly Amortisation'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest17SequenceData \
                       CreatePackingListsForMonthlyAmortisationTest \
                       Tic \
                       TestSimulationBuildForMonthlyAmortisation \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    


  def stepSetTest18SequenceData(self, sequence=None, sequence_list=None, **kw):
    item_list = ['item1','item2','item3']
    item_list = [self.getItemModule()[item] for item in item_list]
    parameter_dict = dict(self.account_dict)
    parameter_dict.update( {'amortisation_method':self.linear_method,
                            'amortisation_start_price':10000,
                            'disposal_price':0,
                            'amortisation_duration':48,
                            'immobilisation_vat':0,
                          } )
    build_parameter_dict = { 'at_date':DateTime('2002/01/01'),
                             'item_uid_list': [x.getUid() for x in [self.getItemModule()[y] for y in ['item1','item2']]],
                           }
    sequence.edit(item_list_list = [item_list],
                  datetime = DateTime('2000/01/01'),
                  parameter_dict = parameter_dict,
                  destination_section = self.getOrganisationModule()["A"],
                  build_parameter_dict = build_parameter_dict)

  def test_18_TestAccountingBuilding(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nTest Simple Accounting Build'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest18SequenceData \
                       DeleteAllPackingLists \
                       Tic \
                       TestAllAppliedRulesAreEmpty \
                       CreatePackingList \
                       DeliverPackingList \
                       AggregateItems \
                       Tic \
                       PartialBuildAccounting \
                       Tic \
                       TestPartialAccountingBuild \
                       DeleteAccounting \
                       Tic \
                       BuildAccounting \
                       Tic \
                       TestMultiItemAccountingBuild \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    

  def stepSetTest19SequenceData(self, sequence=None, sequence_list=None, **kw):
    item_list = ['item1']
    item_list = [self.getItemModule()[item] for item in item_list]
    parameter_dict = dict(self.account_dict)
    parameter_dict.update( {'amortisation_method':self.linear_method,
                            'amortisation_start_price':10000,
                            'disposal_price':0,
                            'amortisation_duration':48,
                            'immobilisation_vat':0,
                          } )
    sequence.edit(item_list_list = [item_list],
                  item=self.getItemModule()['item1'],
                  datetime = DateTime('2000/01/01'),
                  parameter_dict = parameter_dict,
                  destination_section = self.getOrganisationModule()["A"])

  def stepSetTest19SequenceData2(self, sequence=None, sequence_list=None, **kw):
    """
    Add a section change packing_list at date 2002/01/01
    """
    parameter_dict = {}
    sequence.edit(datetime = DateTime('2002/01/01'),
                  parameter_dict = parameter_dict,
                  destination_section = self.getOrganisationModule()["B"])

  def stepTest19ModifyPackingList(self, sequence=None, sequence_list=None, **kw):
    pl = sequence.get('packing_list')
    if pl is None: pl = sequence.get('packing_list_list', [])[-1]
    for line in pl.contentValues():
      line.edit(amortisation_account=self.extra_account_dict['amortisation_account'])

  def test_19_TestAccountingBuildingAndDivergence(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nTest Accounting Build And Divergence Behavior'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest19SequenceData \
                       DeleteAccounting \
                       Tic \
                       DeleteAllPackingLists \
                       Tic \
                       TestAllAppliedRulesAreEmpty \
                       CreatePackingList \
                       DeliverPackingList \
                       AggregateItems \
                       Tic \
                       BuildAccounting \
                       Tic \
                       TestSimpleAccountingBuild \
                       SetTest19SequenceData2 \
                       CreatePackingList \
                       DeliverPackingList \
                       AggregateItems \
                       Tic \
                       TestSimulationBuildAfterFirstAccountingChange \
                       BuildAccounting \
                       Tic \
                       TestAccountingBuildAfterFirstChange \
                       DeletePackingList \
                       Tic \
                       TestSimulationBuildAfterSecondAccountingChange \
                       BuildAccounting \
                       Tic \
                       TestAccountingBuildAfterSecondChange \
                       AdoptPrevision \
                       Tic \
                       TestAccountingBuildAfterAdoptPrevision \
                       Test19ModifyPackingList \
                       Tic \
                       TestSimulationBuildAfterPackingListModification \
                       BuildAccounting \
                       Tic \
                       TestAccountingBuildAfterPackingListModification \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    


  def stepSetTest20SequenceData(self, sequence=None, sequence_list=None, **kw):
    item_list = ['item1']
    item_list = [self.getItemModule()[item] for item in item_list]
    parameter_dict = dict(self.account_dict)
    parameter_dict.update( {'amortisation_method':self.linear_method,
                            'amortisation_start_price':10000,
                            'disposal_price':0,
                            'amortisation_duration':48,
                            'immobilisation_vat':0,
                          } )
    sequence.edit(item_list_list = [item_list],
                  item=self.getItemModule()['item1'],
                  datetime = DateTime('2000/01/01'),
                  parameter_dict = parameter_dict,
                  destination_section = self.getOrganisationModule()["A"])

  def test_20_TestAccountingAcceptDecisionSolver(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\nTest Accounting Accept Decision Solver'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest20SequenceData \
                       DeleteAccounting \
                       Tic \
                       DeleteAllPackingLists \
                       Tic \
                       TestAllAppliedRulesAreEmpty \
                       CreatePackingList \
                       DeliverPackingList \
                       AggregateItems \
                       Tic \
                       BuildAccounting \
                       Tic \
                       TestSimpleAccountingBuild \
                       ChangeAccountingPrice \
                       Tic \
                       AcceptDecision \
                       Tic \
                       TestSimulationBuildAfterAcceptDecision \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    

  def stepSetTest21SequenceData(self, sequence=None, sequence_list=None, **kw):
    item_list = ['item1']
    item_list = [self.getItemModule()[item] for item in item_list]
    parameter_dict = dict(self.account_dict)
    parameter_dict.update( {'amortisation_method':self.linear_method,
                            'amortisation_start_price':10000,
                            'disposal_price':0,
                            'amortisation_duration':48,
                            'immobilisation_vat':0,
                          } )
    sequence.edit(item_list_list = [item_list],
                  item=self.getItemModule()['item1'],
                  datetime = DateTime('2000/01/01'),
                  parameter_dict = parameter_dict,
                  destination_section = self.getOrganisationModule()["A"])

  def stepTest21FirstModifyPackingList(self, sequence=None, sequence_list=None, **kw):
    pl = sequence.get('packing_list')
    if pl is None: pl = sequence.get('packing_list_list', [])[-1]
    for line in pl.contentValues():
      line.edit(amortisation_duration=36)

  def stepTest21SecondModifyPackingList(self, sequence=None, sequence_list=None, **kw):
    pl = sequence.get('packing_list')
    if pl is None: pl = sequence.get('packing_list_list', [])[-1]
    for line in pl.contentValues():
      line.edit(amortisation_duration=24)

  def stepTest21ThirdModifyPackingList(self, sequence=None, sequence_list=None, **kw):
    pl = sequence.get('packing_list')
    if pl is None: pl = sequence.get('packing_list_list', [])[-1]
    for line in pl.contentValues():
      line.edit(amortisation_duration=48)

  def stepTest21FourthModifyPackingList(self, sequence=None, sequence_list=None, **kw):
    pl = sequence.get('packing_list')
    if pl is None: pl = sequence.get('packing_list_list', [])[-1]
    for line in pl.contentValues():
      line.edit(amortisation_account=self.extra_account_dict['amortisation_account'])

  def test_21_TestSimulationBuildingWithValidatedTransactions(self, quiet=0, run=run_all_test):
    """
    The expand process takes care of already validated transactions : it creates
    some correction simulation movements in order to compensate simulation movements
    whose corresponding delivery is already validated.
    This test tests this behavior
    """
    if not run: return
    if not quiet:
      message = '\nTest Simulation Building With Validated Transactions'
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    sequence_list = SequenceList()
    sequence_string = 'SetTest21SequenceData \
                       DeleteAccounting \
                       Tic \
                       DeleteAllPackingLists \
                       Tic \
                       TestAllAppliedRulesAreEmpty \
                       CreatePackingList \
                       DeliverPackingList \
                       AggregateItems \
                       Tic \
                       BuildAccounting \
                       Tic \
                       TestSimpleAccountingBuild \
                       ValidateAccounting \
                       Tic \
                       Test21FirstModifyPackingList \
                       Tic \
                       TestFirstSimulationBuildAfterAccountingValidation \
                       Test21SecondModifyPackingList \
                       Tic \
                       TestSecondSimulationBuildAfterAccountingValidation \
                       Test21ThirdModifyPackingList \
                       Tic \
                       TestThirdSimulationBuildAfterAccountingValidation \
                       Test21FourthModifyPackingList \
                       Tic \
                       TestFourthSimulationBuildAfterAccountingValidation \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)    




if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestImmobilisation))
        return suite

