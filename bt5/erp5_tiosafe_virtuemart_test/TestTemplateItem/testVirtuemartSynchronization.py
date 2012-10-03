# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import unittest
from zLOG import LOG
from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
import os

from Products.ERP5Type.tests.backportUnittest import expectedFailure

class TestVirtuemartSynchronization(ERP5TypeTestCase):
  """
  """

  def getBusinessTemplateList(self):
    """ Return the list of BT required by unit tests. """
    return (
        'erp5_base',
        'erp5_pdm',
        'erp5_trade',
        'erp5_simulation',
        'erp5_syncml',
        'erp5_tiosafe_core',
        'erp5_tiosafe_test',
        'erp5_tiosafe_virtuemart',
        'erp5_tiosafe_virtuemart_test',
    )

  def getTitle(self):
    return "Test Virtuemart Synchronization"

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    self.portal = self.getPortal()
    self.virtuemart = self.portal.portal_integrations.virtuemart
    
    # Create a user for sync
    acl_users = self.portal.acl_users
    acl_users._doAddUser('TioSafeUser', 'TioSafeUserPassword', ['Manager'], [])
    user = acl_users.getUserById('TioSafeUser').__of__(acl_users)
    newSecurityManager(None, user)

    # Validate rules
    for rule in self.portal.portal_rules.objectValues():
      rule.validate()

    if self.virtuemart.getValidationState() != "validated":
      self.virtuemart.validate()

    self.virtuemart.getDestinationValue().validate()
    self.default_node_id = self.virtuemart.getDestinationValue().getId()
    self.virtuemart.getResourceValue().validate()
    self.default_resource_id = self.virtuemart.getResourceValue().getId()
    self.default_source_id = self.virtuemart.getSourceAdministrationValue().getId()
    
    for connector in self.virtuemart.contentValues(portal_type="Web Service Connector"):
      # use the test connector
      connector.setTransport("virtuemart_test")

    # Update url of pub/sub & validate them
    utils = ZopeTestCase.utils
    #portal_id = os.environ.get('erp5_tests_portal_id')
    portal_id = self.portal.getId() 
    url = "http://%s:%s/%s" %(utils._Z2HOST, utils._Z2PORT, portal_id)
    for sync in self.portal.portal_synchronizations.objectValues():
      if sync.getPortalType() == "SyncML Subscription":
        sync.edit(url_string=url,
                  subscription_url_string=url,
                  user_id='TioSafeUser',
                  password='TioSafeUserPassword',
                  )
      else:
        sync.edit(url_string=url)
      if sync.getValidationState() != "validated":
        sync.validate()

    self.tic()

  def beforeTearDown(self):
    """
    This is ran after anything, used to reset the environment
    """
    for connector in self.virtuemart.contentValues(portal_type="Web Service Connector"):
      # use the test connector
      connector.setTransport("virtuemart")
    self.tic()



  def _runAndCheckNodeSynchronization(self, reset=True, conflict_dict=None, node_type='Person'):
    # run synchronization
    node_module_list = []
    if node_type == 'Organisation':
      node_module_list = ['organisation_module', 'delivered_organisation_module',]
    else:
      node_module_list = ['person_module', 'delivered_person_module',]
    for im in node_module_list:
      LOG("RUNNING SYNCHRO FOR %s" %(im), 300, "")
      self.tic()
      self.virtuemart.IntegrationSite_synchronize(reset=reset, synchronization_list=[im,],
                                              batch_mode=True)

      self.tic()
      if conflict_dict and conflict_dict.has_key(im):
        nb_pub_conflict, nb_sub_conflict, in_conflict = conflict_dict[im]
        self.checkConflicts(im, nb_pub_conflict, nb_sub_conflict, in_conflict)
      else:
        self.checkConflicts(im)
        self.assertEqual(self.virtuemart[im].IntegrationModule_getSignatureDiff(), "No diff")
        self.assertEqual(self.virtuemart[im].IntegrationModule_getTioSafeXMLDiff(), "No diff")

  
  def checkConflicts(self, module, nb_pub_conflicts=0, nb_sub_conflicts=0, in_conflict=True):
    module = self.virtuemart[module]
    pub = module.getSourceSectionValue()
    sub = module.getDestinationSectionValue()
    self.assertEqual(len(pub.getConflictList()), nb_pub_conflicts)
    self.assertEqual(len(sub.getConflictList()), nb_sub_conflicts)
    for conflict in pub.getConflictList() + sub.getConflictList():
      state = conflict.getParentValue().getValidationState()
      if in_conflict:
        self.assertEqual(state, 'conflict')
      else:
        self.assertEqual(state, 'synchronized')

  def _runAndCheckResourceSynchronization(self, conflict_dict=None, reset=True):
    # run synchronization
    self.tic()
    self.virtuemart.IntegrationSite_synchronize(reset=reset, synchronization_list=['product_module',],
                                            batch_mode=True)

    self.tic()
    # Check fix point
    for im in ['product_module']:
      if conflict_dict and conflict_dict.has_key(im):
        nb_pub_conflict, nb_sub_conflict, in_conflict = conflict_dict[im]
        self.checkConflicts(im, nb_pub_conflict, nb_sub_conflict, in_conflict)
      else:
        self.checkConflicts(im)
        self.assertEqual(self.virtuemart[im].IntegrationModule_getTioSafeXMLDiff(), "No diff")
        self.assertEqual(self.virtuemart[im].IntegrationModule_getSignatureDiff(), "No diff")
        self.checkSaleSupply()

  def checkSaleSupply(self):
    for document in self.getPortalObject().product_module.contentValues():
      if document.getValidationState() == 'validated' and document.getId() != self.default_node_id:
        self.assertEqual(len([x for x in document.Base_getRelatedObjectList() if x.getPortalType() == "Sale Supply Line"]), 1)

  def checkSaleTradeConditionRelation(self, module, excluded_title_list=[]):
    for document in module.contentValues():
      if document.getValidationState() == 'validated' and \
             document.getId() != self.default_node_id:
        if document.getTitle() not in excluded_title_list:
          self.assertEqual(len([x for x in document.Base_getRelatedObjectList() if x.getPortalType() == "Sale Trade Condition"]), 1)
        else:
         self.assertEqual(len([x for x in document.Base_getRelatedObjectList() if x.getPortalType() == "Sale Trade Condition"]), 0) 


  def runOrganisationSync(self):
    """
    test synchronization of organisation
    """

    INITIAL_ORGANISATION_TITLE = ["Simple organisation 1",
                                  "Simple organisation 2",
                                  "Delivered Organisation"]
    #
    # Initial cleanup & settings
    #

    # Delete organisations
    org_ids = [x for x in self.portal.organisation_module.objectIds() if x != self.default_source_id]
    self.portal.organisation_module.manage_delObjects(org_ids)
    
    # Validate organisations
    for organisation in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Organisation"):
      if organisation.getTitle() in INITIAL_ORGANISATION_TITLE:
        if organisation.getValidationState() != "validated":
          organisation.validate()
    
    self.tic()
    # Check initial data
    self.assertEqual(len(self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Organisation")), 3)
    self.assertEqual(len(self.virtuemart.delivered_organisation_module.getObjectList()), 1)
    self.assertEqual(len(self.virtuemart.organisation_module.getObjectList()), 2)
    original_organisation_module_length = len(self.portal.organisation_module.contentValues())
    self.assertEqual(len(self.portal.organisation_module.contentValues()), 1)
    # store organisation that will be synced
    organisation_dict = {}
    for organisation in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Organisation"):
      #if organisation.getTitle().startswith("Delivered")     
      organisation_dict[organisation.getTitle()] = ('organisation', organisation.getPath())      

    #
    # Do & Check initial synchronization
    #
    self._runAndCheckNodeSynchronization(node_type='Organisation')
    self.checkSaleTradeConditionRelation(self.getPortalObject().organisation_module)


    self.assertEqual(len(self.portal.organisation_module.contentValues()), original_organisation_module_length+3)
    
    for organisation in self.portal.organisation_module.contentValues():
      if organisation.getId() != self.default_source_id:
        self.assertEqual(organisation.getValidationState(), 'validated')
        if organisation.getTitle() == 'Delivered Organisation':
          self.assertEqual(organisation.getRoleList(), ['virtuemart_delivery'])
          
        node_type, test_organisation = organisation_dict.get(organisation.getTitle(), None)
        test_organisation = self.portal.restrictedTraverse(test_organisation)
        self.assertNotEqual(test_organisation, None)
        self.assertEqual(test_organisation.getTitle(), organisation.getTitle())
        # Check phones
        self.assertEqual(test_organisation.getPhone(), organisation.getDefaultTelephoneText())
        # Check default address
        default_address = organisation.get("default_address", None)
        self.assertNotEqual(default_address, None)
        self.assertEqual(test_organisation.getStreet(), default_address.getStreetAddress())
        self.assertEqual(test_organisation.getZip(), default_address.getZipCode())
        self.assertEqual(test_organisation.getCity(), default_address.getCity())
        #self.assertEqual(test_organisation.getCountry(), default_address.getRegion())

    #
    # Modify organisation on the plugin side
    #
    mapping_dict = {}
    simple_organisation_update_dict={"street":"street updated by test",
                        "zip":"99999",
                        "city":"Test City",
                        "phone":"00221338215113"}
    organisation_update_dict={"zip":"11111"}
    delivered_organisation_update_dict={"phone":"00221339812031"}
    simple_organisation_conflict_dict = {"street":"street conflict",
                        "zip":"00000",
                        "city":"City conflict"}
    for organisation in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Organisation"):
      if organisation.getTitle() == 'Simple organisation 1':
        # Change basic informations
        mapping_dict[organisation.getId()] = {"street":organisation.getStreet(),
                                        "zip":organisation.getZip(),
                                        "city":organisation.getCity(),
                                        "phone":organisation.getPhone()}
        organisation.edit(**simple_organisation_update_dict)
      
      elif organisation.getTitle() == 'Simple organisation 2':
        # Change basic informations
        mapping_dict[organisation.getId()] = {"zip":organisation.getZip()}
        organisation.edit(**organisation_update_dict)
      
      elif organisation.getTitle() == 'Delivered Organisation':
        # Change basic informations
        mapping_dict[organisation.getId()] = {"phone":organisation.getPhone(),
                                              "country":"France"}
        organisation.edit(**delivered_organisation_update_dict)

    #self._runAndCheckNodeSynchronization(node_type='Organisation')
    #self.checkSaleTradeConditionRelation(self.getPortalObject().organisation_module)

    try:
      self.assertEqual(len(mapping_dict), 3)
      self._runAndCheckNodeSynchronization(reset=True, node_type="Organisation")
      self.checkSaleTradeConditionRelation(self.getPortalObject().organisation_module)
      self.assertEqual(len(self.portal.organisation_module.contentValues()), 4)
      
      for organisation in self.portal.organisation_module.contentValues():
        if organisation.getTitle() == 'Simple organisation 1':
          # Check phones
          self.assertEqual(simple_organisation_update_dict['phone'], organisation.getDefaultTelephoneText())
          # Check default address
          default_address = organisation.get("default_address", None)
          self.assertNotEqual(default_address, None)
          self.assertEqual(simple_organisation_update_dict['street'], default_address.getStreetAddress())
          self.assertEqual(simple_organisation_update_dict['zip'], default_address.getZipCode())
          self.assertEqual(simple_organisation_update_dict['city'], default_address.getCity())
        elif organisation.getTitle() == 'Delivered Organisation':
          # Check phones
          self.assertEqual(delivered_organisation_update_dict['phone'], organisation.getDefaultTelephoneText())
      #
      # Generates conflict on all properties
      #
      for organisation in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Organisation"):
        if organisation.getTitle() == 'Simple organisation 2':
          # Change basic informations
          organisation.edit(**simple_organisation_update_dict)                    
      for org in self.portal.organisation_module.searchFolder(validation_state="validated"):
        if org.getTitle() == 'Simple organisation 2':
          org.setDefaultAddressStreetAddress("address conflit")
          org.setDefaultAddressZipCode("9999")
          org.setDefaultAddressCity("ConflitVille")
      self._runAndCheckNodeSynchronization(reset=False, conflict_dict={'organisation_module' : (0,3, True)}, )
      self.checkSaleTradeConditionRelation(self.getPortalObject().organisation_module, excluded_title_list='New Organistion')
      # Fix all conflicts & run sync again
      for conflict in self.virtuemart.organisation_module.getSourceSectionValue().getConflictList():
        if conflict.getParentValue().getValidationState() == "conflict":
          LOG("changing %s to resolved" %(conflict.getParentValue().getPath(),), 300, "")
          conflict.getParentValue().resolveConflictWithMerge()
      self._runAndCheckNodeSynchronization(reset=False, conflict_dict={'organisation_module' : (3,0, False)})
      self.checkSaleTradeConditionRelation(self.getPortalObject().organisation_module, excluded_title_list='New Organistion')
      self.assertEqual(self.virtuemart['organisation_module'].IntegrationModule_getSignatureDiff(), "No diff")
      #self.assertEqual(self.virtuemart['organisation_module'].IntegrationModule_getTioSafeXMLDiff(), "No diff")
      
    finally:
      # Reset data on organanisation
      for organisation  in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Organisation"):
        mapping = mapping_dict.get(organisation.getId(), None)
        if mapping is not None:
          organisation.edit(**mapping)
          
     
  
  def runPersonSync(self):
    """
    test synchronization of person
    """

    INITIAL_PERSON_TITLE = ["Simple person",
                            "Person in an organisation",
                            "Delivered simple person",
                            "Delivered person in an organisation"]
    '''
           Plugin side                          ERP5 side
     Person in an organisation,             Mohamadou Mbengue
     Simple person,                         Aissatou Keita Mbengue
     Delivered simple person                Said Abdullah Mbengue
     Delivered person in an organisation    Moussa Jamal Mbengue
    '''
    #
    # Initial cleanup & settings
    #

    # Delete person & organisations
    person_ids = [x for x in self.portal.person_module.objectIds() if x != self.default_node_id]
    self.portal.person_module.manage_delObjects(person_ids)
    # Validate some persons
    for person in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Person"):
      if person.getTitle() in INITIAL_PERSON_TITLE:
        if person.getValidationState() != "validated":
          person.validate()
          
    self.tic()
    # Check initial data
    self.assertEqual(len(self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Person")), 4)
    self.assertEqual(len(self.virtuemart.person_module.getObjectList()), 2)
    self.assertEqual(len(self.virtuemart.delivered_person_module.getObjectList()), 2)
    self.assertEqual(len(self.virtuemart.delivered_organisation_module.getObjectList()), 1)
    self.assertEqual(len(self.virtuemart.organisation_module.getObjectList()), 2)
    original_person_module_length = len(self.portal.person_module.contentValues())
    original_organisation_module_length = len(self.portal.organisation_module.contentValues())
    self.assertEqual(len(self.portal.organisation_module.contentValues()), original_organisation_module_length)
    # store person that will be synced
    person_dict = {}
    for person in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Person"):
      person_dict[person.getFirstname()] = ('person', person.getPath())
      
    #
    # Do & Check initial synchronization
    #
    #Synchronize organisation
    self._runAndCheckNodeSynchronization(node_type="Organisation")
    #Synchronize persons
    self._runAndCheckNodeSynchronization()
    self.checkSaleTradeConditionRelation(self.getPortalObject().person_module)
    self.checkSaleTradeConditionRelation(self.getPortalObject().organisation_module)

     
    self.assertEqual(len(self.portal.person_module.contentValues()), original_person_module_length+4)
    self.assertEqual(len(self.portal.organisation_module.contentValues()), 4)
    
    for person in self.portal.person_module.contentValues():
      if person.getId() != self.default_node_id:
        self.assertEqual(person.getValidationState(), 'validated')
        node_type, test_person = person_dict.get(person.getFirstName(), None)
        if node_type == "person":
          test_person = self.portal.restrictedTraverse(test_person)
          self.assertNotEqual(test_person, None)
          self.assertEqual(test_person.getFirstname(), person.getFirstName())
          self.assertEqual(test_person.getLastname(), person.getLastName())
          self.assertEqual(test_person.getEmail(), person.getDefaultEmailText())
          if not person.getSubordinationValue(None):
            # Check default address
            default_address = person.get("default_address", None)
            self.assertNotEqual(default_address, None)
            self.assertEqual(test_person.getStreet(), default_address.getStreetAddress())
            self.assertEqual(test_person.getZip(), default_address.getZipCode())
            self.assertEqual(test_person.getCity(), default_address.getCity())
          else:
            subordination_organisation = person.getSubordinationValue(None)
            # Check phones
            #self.assertEqual(subordination_organisation.getPhone(), person.getDefaultTelephoneText())
            default_address = subordination_organisation.get("default_address", None)
            self.assertNotEqual(default_address, None)
            self.assertEqual(test_person.getStreet(), default_address.getStreetAddress())
            self.assertEqual(test_person.getZip(), default_address.getZipCode())
            self.assertEqual(test_person.getCity(), default_address.getCity())
        else:
          raise ValueError, 'bad type'
        
            
    mapping_dict = {}
    simple_person_update_dict={"street":"street updated by person test",
            "zip":"99999",
            "city":"Test City person test",
            "country":"France"
            }
    person_in_orga_update_dict={"street":"street updated 22",
            "zip":"22222",
            "city":"Test City 22",
            "country":"France"}
    delivered_person_update_dict={"company":"Simple organisation 1",
                      "country":"France"}
    for person in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Person"):
      if person.getTitle() == 'Simple person':
        # Change basic informations
        mapping_dict[person.getId()] = {"street":person.getStreet(),
                                        "zip":person.getZip(),
                                        "city":person.getCity(),
                                        "country":person.getCountry()}
      elif person.getTitle() == 'Delivered simple person':
        # Change basic informations
        mapping_dict[person.getId()] = {"street":person.getStreet(),
                                        "zip":person.getZip(),
                                        "city":person.getCity(),
                                        "country":person.getCountry()}
      elif person.getTitle() == 'Delivered person in an organisation':
        # Change company name
        mapping_dict[person.getId()] = {"company":person.getCompany(),
                                        "country":person.getCountry()}
                                        
    try:
      self.assertEqual(len(mapping_dict), 3)     
      #
      # Modify person address on the plugin side
      #
      for person in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Person"):
        if person.getTitle() == 'Simple person':
          person.edit(**simple_person_update_dict)
      self._runAndCheckNodeSynchronization(reset=False)
      self.assertEqual(len(self.portal.person_module.contentValues()), original_person_module_length+4)
      for im in ['person_module',]:
        self.assertEqual(self.virtuemart[im].IntegrationModule_getTioSafeXMLDiff(), "No diff")
        self.assertEqual(self.virtuemart[im].IntegrationModule_getSignatureDiff(), "No diff")
                                 
      #
      # Change subordination
      #                       
      for person in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Person"):
        if person.getTitle() == 'Delivered person in an organisation':
          person.edit(**delivered_person_update_dict)  
      self._runAndCheckNodeSynchronization(reset=False)
      self.assertEqual(len(self.portal.person_module.contentValues()), original_person_module_length+4) 
      '''     
      #
      # Modify addresses on both sides
      #
      for person in self.portal.person_module.searchFolder(validation_state="validated"):
        if person.getTitle() == "Aissatou Keita Mbengue":
          person.setDefaultAddressStreetAddress(person_in_orga_update_dict['street'])
          person.setDefaultAddressZipCode(person_in_orga_update_dict['zip'])
          #person.setDefaultAddressRegion('region/%s' % person_in_orga_update_dict['country'])
      for person in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Person"):
        if person.getTitle() == "Simple person":
          person.edit(city=person_in_orga_update_dict['city'])
      self.tic()
      
      #self._runAndCheckNodeSynchronization(reset=False)
      
      self.assertEqual(self.virtuemart['person_module'].IntegrationModule_getSignatureDiff(), "No diff1")
      '''  
           
      #
      # Generates conflict on all properties
      #
      for person in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Person"):
        if person.getTitle() == 'Delivered simple person':
          # Change basic informations
          person.edit(**simple_person_update_dict)                    
      for pers in self.portal.person_module.searchFolder(validation_state="validated"):
        if pers.getTitle() == "Said Abdullah Mbengue":
          pers.setDefaultAddressStreetAddress("address conflit")
          pers.setDefaultAddressZipCode("9999")
          pers.setDefaultAddressCity("ConflitVille")
      self._runAndCheckNodeSynchronization(reset=False, conflict_dict={'delivered_person_module' : (3,0, True)}, )
      self.checkSaleTradeConditionRelation(self.getPortalObject().person_module, excluded_title_list='New Person')
      self.checkSaleTradeConditionRelation(self.getPortalObject().organisation_module, excluded_title_list='New Organistion')
      # Fix all conflicts & run sync again
      for conflict in self.virtuemart.delivered_person_module.getSourceSectionValue().getConflictList():
        if conflict.getParentValue().getValidationState() == "conflict":
          LOG("changing %s to resolved" %(conflict.getParentValue().getPath(),), 300, "")
          conflict.getParentValue().resolveConflictWithMerge()
      self._runAndCheckNodeSynchronization(reset=False, conflict_dict={'delivered_person_module' : (3,0, False)})
      self.checkSaleTradeConditionRelation(self.getPortalObject().person_module, excluded_title_list='New Person')
      self.checkSaleTradeConditionRelation(self.getPortalObject().organisation_module, excluded_title_list='New Organistion')
      
      #self._runAndCheckNodeSynchronization(reset=False)
      #self.assertEqual(self.virtuemart['delivered_person_module'].IntegrationModule_getTioSafeXMLDiff(), "No diff")
      self.assertEqual(self.virtuemart['delivered_person_module'].IntegrationModule_getSignatureDiff(), "No diff")
      
      
    finally:
      # Reset data on person
      for person in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Person"):
        mapping = mapping_dict.get(person.getId(), None)
        if mapping is not None:
          person.edit(**mapping)

  def runProductSync(self):
    """
    test synchronization of prodcut
    """
    # Delete products
    prod_ids = [x for x in self.portal.product_module.objectIds() if x != self.default_resource_id]
    self.portal.product_module.manage_delObjects(prod_ids)
    
    for product in self.portal.product_module.contentValues():
      if product.getId() == self.default_resource_id:
        if product.getValidationState()== 'validated':
          product.invalidate()
      elif product.getValidationState() != 'validated':
        product.validate()
    
    self.tic()
    
    # Check initial data
    for product in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Product"):
      if product.getValidationState() != "validated":
        product.validate()
    
    self.tic()

    self.assertEqual(len(self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Product",
                                                                       validation_state="validated")), 5)
    original_product_module_lenght = len(self.portal.product_module.contentValues())
    # store product that will be synced
    product_dict = {}
    for product in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Product"):
      product_dict[product.getReference()] = product.getPath()

    # run synchronization
    self._runAndCheckResourceSynchronization(reset=True)
    self.assertEqual(len(self.portal.product_module.contentValues()), original_product_module_lenght+5)

    for product in self.portal.product_module.contentValues():
      if product.getId() != self.default_resource_id:
        self.assertEqual(product.getValidationState(), 'validated')
        test_product = product_dict.get(product.getReference(), None)
        self.assertNotEqual(test_product, None)
        test_product = self.portal.restrictedTraverse(test_product)
        self.assertNotEqual(test_product, None)
        self.assertEqual(test_product.getTitle(), product.getTitle())
        self.assertEqual(test_product.getDescription(), product.getDescription())

    # Backup data
    mapping_dict = {}
    for product in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Product"):
      mapping_dict[product.getId()] = {"title": product.getTitle(),
                                       "reference": product.getReference(),
                                       "description": product.getDescription(),}  

    self.assertEqual(len(self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Product",
                                                                      validation_state="validated")), 5)
    # Check fix point
    for im in ['product_module',]:
      self.assertEqual(self.virtuemart[im].IntegrationModule_getTioSafeXMLDiff(), "No diff")
      self.assertEqual(self.virtuemart[im].IntegrationModule_getSignatureDiff(), "No diff")
      
    try:
      self.assertEqual(len(mapping_dict), 5)
      #
      # Test update product from plugin
      #
      for product in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Product"):
        if product.getTitle() == "iPhone 4":
          product.edit(title="iPhone 4 Updated in plugin",
                       description="Ceci est un iPhone 4 Updated 1")
      self._runAndCheckResourceSynchronization(reset=False)
      self.assertEqual(len(self.portal.product_module.contentValues()), original_product_module_lenght+5)

      #
      # Test update product from erp5
      #
      for product in self.portal.product_module.searchFolder(validation_state="validated"):
        if product.getTitle() == "iPad1":
          product.edit(title="iPad1 Updated in erp5", description="ceci est un iPad1 Updated in erp5")
      self._runAndCheckResourceSynchronization(reset=False)
      self.assertEqual(len(self.portal.product_module.contentValues()), original_product_module_lenght+5)
      
      #
      # Add ERP5 Product
      #
      '''
      erp5_new_product={"title": "ERP5 Product Title",
                      "reference": "ERP5ProductReference",
                      "description": "ERP5 Product Description",}
      new_product = self.portal.product_module.newContent(portal_type='Product')
      new_product.edit(**erp5_new_product)
      new_product.validate() 
      self.tic()
      
      # add to sale supply
      sale_supply = self.getPortalObject().sale_supply_module.searchFolder(title='Virtuemart', validation_state='validated')[0].getObject()
      if len(sale_supply.searchFolder(resource_title=new_product.getTitle())) == 0:
        sale_supply.newContent(resource_value=new_product)
        
      self._runAndCheckResourceSynchronization(reset=False)
      
      for product in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Product"):
        if product.getReference() == "ERP5ProductReference":
          mapping_dict[product.getId()] = {"title": product.getTitle(),
                                       "reference": product.getReference(),
                                       "description": product.getDescription(),}  

      for product in self.portal.product_module.contentValues():
        if product.getId() != self.default_resource_id:
          self.assertEqual(product.getValidationState(), 'validated')
          test_product = mapping_dict.get(product.getReference(), None)
          self.assertNotEqual(test_product, None)
          test_product = self.portal.restrictedTraverse(test_product)
          self.assertNotEqual(test_product, None)
          self.assertEqual(test_product.getTitle(), product.getTitle())
          self.assertEqual(test_product.getDescription(), product.getDescription())
      '''
      #
      # Delete Product
      #
      #Delete erp5 product
      for product in self.portal.product_module.contentValues(portal_type="Product"):
        if product.getReference() == "PRDNew":
          if product.getValidationState() == "validated":
            product.invalidate()
      self.tic()
      
      self.assertEqual(len(self.portal.product_module.contentValues()), 6)      
      self.assertEqual(len(self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Product",
                                                                      validation_state="validated")), 5)
      self._runAndCheckResourceSynchronization(reset=False)
      self.assertEqual(self.virtuemart['product_module'].IntegrationModule_getSignatureDiff(), "No diff")
      self.assertEqual(self.virtuemart['product_module'].IntegrationModule_getTioSafeXMLDiff(), "No diff")
      
      #
      # Add attribute in plugin Product
      #
      for product in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Product"):
        if product.getReference() == "PRD4":
          attribut=product.newContent(portal_type="Virtuemart Test Product Variation")
          attribut.edit(category='Color/white')
          if attribut.getValidationState() == 'invalidated':
            attribut.validate()
      self.tic()
      self._runAndCheckResourceSynchronization(reset=False)
      self.assertEqual(len(self.portal.product_module.contentValues()), original_product_module_lenght+5)      
      
      #
      # Add attribute in erp5 Product
      #
      for product in self.portal.product_module.contentValues(portal_type="Product"):
        if product.getReference() == "PRD2":
          attribut=product.newContent(portal_type="Product Individual Variation")
          attribut.edit(title='blanc',
                        variation_base_category='colour')
          if attribut.getValidationState() != 'validated':
            attribut.validate()
      self.tic()
      self._runAndCheckResourceSynchronization(reset=False)
      self.assertEqual(len(self.portal.product_module.contentValues()), original_product_module_lenght+5)      
      
      
      #
      # Delete Attribute from erp5 product
      #
      for product in self.portal.product_module.contentValues(portal_type="Product"):
        if product.getReference() == "PRD3":
          for attribute in product.contentValues(portal_type="Product Individual Variation"):
            product.manage_delObjects(ids=[attribute.getId(),])
          
      self.tic()
      self._runAndCheckResourceSynchronization(reset=False)   
      
      
      #
      # Generates conflict on all properties
      #
      '''
      prod_update_dict_1={"title": "Conflict Product Title 1",
                          "reference": "ConflictRef1",
                          "description": "Conflict Product Description 1",}
      prod_update_dict_2={"title": "Conflict Product Title 2",
                          "reference": "ConflictRef2",
                          "description": "Conflict Product Description 2",}
      for product in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Product"):
        if product.getReference() == 'PRD2':
          product.edit(**prod_update_dict_1)                    
      for prod in self.portal.organisation_module.searchFolder(validation_state="validated"):
        if prod.getReference() == "PRD2":
          prod.edit(**prod_update_dict_2) 
      self._runAndCheckResourceSynchronization(reset=False, conflict_dict={'product_module' : (0,3, True)}, )
      # Fix all conflicts & run sync again
      for conflict in self.virtuemart.product_module.getSourceSectionValue().getConflictList():
        if conflict.getParentValue().getValidationState() == "conflict":
          LOG("changing %s to resolved" %(conflict.getParentValue().getPath(),), 300, "")
          conflict.getParentValue().resolveConflictWithMerge()
      self._runAndCheckResourceSynchronization(reset=False, conflict_dict={'product_module' : (3,0, False)})
      self.assertEqual(self.virtuemart["product_module"].IntegrationModule_getSignatureDiff(), "No diff")
      '''

    finally:
      # Reset data on product
      for product in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Product"):
        mapping = mapping_dict.get(product.getId(), None)
        if mapping is not None:
          product.edit(**mapping)


  def runSaleOrderSync(self):
    """
    test synchronization of sale order
    """
    # Delete sale_orders
    so_ids = list(self.portal.sale_order_module.objectIds())
    self.portal.sale_order_module.manage_delObjects(so_ids)
    # Define date on integration site
    self.virtuemart.edit(stop_date="2010/12/01")
    self.tic()
    # Check initial data
    self.assertEqual(len(self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Sale Order")), 1)
    self.assertEqual(len(self.portal.sale_order_module.contentValues()), 0)
    # store person that will be synced
    sale_order_dict = {}
    for sale_order in self.portal.virtuemart_test_module.contentValues(portal_type="Virtuemart Test Sale Order"):
      sale_order_dict[sale_order.getReference()] = sale_order.getPath()
      if sale_order.getValidationState() != "validated":
        sale_order.validate()
    
    # run synchronization
    self._runAndCheckResourceSynchronization(reset=True)
    
    #sale orders
    self.virtuemart.IntegrationSite_synchronize(reset=True, synchronization_list=['sale_order_module',],
                                            batch_mode=True)
    self.tic()

    # Check fix point
    for im in ['sale_order_module',]:
      self.assertEqual(self.virtuemart[im].IntegrationModule_getTioSafeXMLDiff(), "No diff")
      self.assertEqual(self.virtuemart[im].IntegrationModule_getSignatureDiff(), "No diff")

    self.assertEqual(len(self.portal.sale_order_module.contentValues()), 1)

    for sale_order in self.portal.sale_order_module.contentValues():
      self.assertEqual(sale_order.getSimulationState(), 'confirmed')
      test_sale_order = sale_order_dict.get(sale_order.getReference(), None)
      self.assertNotEqual(test_sale_order, None)
      test_sale_order = self.portal.restrictedTraverse(test_sale_order)
      self.assertNotEqual(test_sale_order, None)
      # Check amount
      '''
      total_price = float(getattr(test_sale_order, 'SubTotalNet')) - \
                    float(getattr(test_sale_order, 'SubTotalVAT')) + \
                    float(getattr(test_sale_order, 'ShippingPriceTaxExcl'))
      self.assertEqual("%.2f" % (round(total_price, 2),), "%.2f" % (round(sale_order.getTotalPrice(),2),))
      '''
      # Check ressource are defined
      for line in sale_order.contentValues(portal_type="Sale Order Line"):
        self.assertNotEqual(line.getResourceValue(), None)
      # Check category
      self.assertNotEqual(sale_order.getSource(), None)
      self.assertNotEqual(sale_order.getSourceSection(), None)
      self.assertNotEqual(sale_order.getSourceDecision(), None)
      self.assertNotEqual(sale_order.getSourceAdministration(), None)
      self.assertNotEqual(sale_order.getDestination(), None)
      self.assertNotEqual(sale_order.getDestinationSection(), None)
      self.assertNotEqual(sale_order.getDestinationDecision(), None)
      self.assertNotEqual(sale_order.getDestinationAdministration(), None)

    # Change date
    self.virtuemart.edit(stop_date="2010/12/31")
    self.tic()

    # run synchronization
    self.virtuemart.IntegrationSite_synchronize(reset=False, synchronization_list=['sale_order_module',],
                                            batch_mode=True)
    self.tic()
    self.checkConflicts('sale_order_module')
    # Check fix point
    for im in ['sale_order_module',]:
      self.assertEqual(self.virtuemart[im].IntegrationModule_getTioSafeXMLDiff(), "No diff")
      self.assertEqual(self.virtuemart[im].IntegrationModule_getSignatureDiff(), "No diff")

    self.assertEqual(len(self.portal.sale_order_module.contentValues()), 1)
    for sale_order in self.portal.sale_order_module.contentValues():
      self.assertEqual(sale_order.getSimulationState(), 'confirmed')
      test_sale_order = sale_order_dict.get(sale_order.getReference(), None)
      self.assertNotEqual(test_sale_order, None)
      test_sale_order = self.portal.restrictedTraverse(test_sale_order)
      self.assertNotEqual(test_sale_order, None)
      '''
      # Check amount
      total_price = float(getattr(test_sale_order, 'SubTotalNet')) - \
                    float(getattr(test_sale_order, 'SubTotalVAT')) + \
                    float(getattr(test_sale_order, 'ShippingPriceTaxExcl'))
      self.assertEqual("%.2f" % (round(total_price, 2),), "%.2f" % (round(sale_order.getTotalPrice(),2),))
      '''
      # Check ressource are defined
      for line in sale_order.contentValues(portal_type="Sale Order Line"):
        self.assertNotEqual(line.getResourceValue(), None)
      # Check category
      self.assertNotEqual(sale_order.getSource(), None)
      self.assertNotEqual(sale_order.getSourceSection(), None)
      self.assertNotEqual(sale_order.getSourceDecision(), None)
      self.assertNotEqual(sale_order.getSourceAdministration(), None)
      self.assertNotEqual(sale_order.getDestination(), None)
      self.assertNotEqual(sale_order.getDestinationSection(), None)
      self.assertNotEqual(sale_order.getDestinationDecision(), None)
      self.assertNotEqual(sale_order.getDestinationAdministration(), None)
      if sale_order.getReference() == "11":
        # Nothing must be linked to Unknown
        for line in sale_order.contentValues(portal_type="Sale Order Line"):
          self.assertNotEqual(line.getResource(), self.virtuemart.getResource())
        self.assertEqual(sale_order.getSource(), self.virtuemart.getSourceAdministration())
        self.assertEqual(sale_order.getSourceSection(), self.virtuemart.getSourceAdministration())
        self.assertEqual(sale_order.getSourceDecision(), self.virtuemart.getSourceAdministration())
        self.assertEqual(sale_order.getSourceAdministration(), self.virtuemart.getSourceAdministration())
        self.assertNotEqual(sale_order.getDestination(), self.virtuemart.getDestination())
        self.assertNotEqual(sale_order.getDestinationSection(), self.virtuemart.getDestination())
        self.assertNotEqual(sale_order.getDestinationDecision(), self.virtuemart.getDestination())
        self.assertNotEqual(sale_order.getDestinationAdministration(), self.virtuemart.getDestination())

  @expectedFailure
  def testFullSync(self):
    self.runOrganisationSync()
    self.runPersonSync()
    self.runProductSync()
    #self.runSaleOrderSync()
  
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestVirtuemartSynchronization))
  return suite
