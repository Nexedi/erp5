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
from unittest import expectedFailure
from zLOG import LOG
from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
import os

class TestUbercartSynchronization(ERP5TypeTestCase):
  """
  """

  def getBusinessTemplateList(self):
    """ Return the list of BT required by unit tests. """
    return (
        'erp5_base',
	'erp5_core_proxy_field_legacy',
        'erp5_pdm',
        'erp5_simulation',
        'erp5_trade',
        'erp5_syncml',
        'erp5_tiosafe_core',
        'erp5_tiosafe_test',
        'erp5_tiosafe_ubercart',
        'erp5_tiosafe_ubercart_test',
    )

  def getTitle(self):
    return "Test Ubercart Synchronization"

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    self.portal = self.getPortal()
    self.ubercart = self.portal.portal_integrations.ubercart
    
    # Create a user for sync
    acl_users = self.portal.acl_users
    acl_users._doAddUser('TioSafeUser', 'TioSafeUserPassword', ['Manager'], [])
    user = acl_users.getUserById('TioSafeUser').__of__(acl_users)
    newSecurityManager(None, user)

    # Validate rules
    for rule in self.portal.portal_rules.objectValues():
      rule.validate()

    if self.ubercart.getValidationState() != "validated":
      self.ubercart.validate()

    self.ubercart.getDestinationValue().validate()
    self.default_node_id = self.ubercart.getDestinationValue().getId()
    self.ubercart.getResourceValue().validate()
    self.default_resource_id = self.ubercart.getResourceValue().getId()
    self.default_source_id = self.ubercart.getSourceAdministrationValue().getId()
    
    for connector in self.ubercart.contentValues(portal_type="Web Service Connector"):
      # use the test connector
      connector.setTransport("ubercart_test")

    # Update url of pub/sub & validate them
    utils = ZopeTestCase.utils
    portal_id = os.environ.get('erp5_tests_portal_id')
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
    for connector in self.ubercart.contentValues(portal_type="Web Service Connector"):
      # use the test connector
      connector.setTransport("ubercart")
    self.tic()



  def _runAndCheckNodeSynchronization(self, reset=True, conflict_dict=None):
    # run synchronization   
    for im in ['organisation_module','delivered_organisation_module',\
		'person_module', 'delivered_person_module']:
      LOG("RUNNING SYNCHRO FOR %s" %(im), 300, "")
      self.tic()
      self.ubercart.IntegrationSite_synchronize(reset=reset, synchronization_list=[im,],
                                              batch_mode=True)

      self.tic()
      if conflict_dict and conflict_dict.has_key(im):
        nb_pub_conflict, nb_sub_conflict, in_conflict = conflict_dict[im]
        self.checkConflicts(im, nb_pub_conflict, nb_sub_conflict, in_conflict)
      else:
        self.checkConflicts(im)
        self.assertEqual(self.ubercart[im].IntegrationModule_getSignatureDiff(), "No diff")
        self.assertEqual(self.ubercart[im].IntegrationModule_getTioSafeXMLDiff(), "No diff")

  def checkConflicts(self, module, nb_pub_conflicts=0, nb_sub_conflicts=0, in_conflict=True):
    module = self.ubercart[module]
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

  def _runAndCheckResourceSynchronization(self, reset=True, conflict_dict=None):
    # run synchronization
    self.tic()
    LOG("RUNNING SYNCHRO FOR product_module", 300, "")
    self.ubercart.IntegrationSite_synchronize(reset=reset, synchronization_list=['product_module',],
                                            batch_mode=True)

    self.tic()
    # Check fix point
    for im in ['product_module',]:
      if conflict_dict and conflict_dict.has_key(im):
        nb_pub_conflict, nb_sub_conflict, in_conflict = conflict_dict[im]
        self.checkConflicts(im, nb_pub_conflict, nb_sub_conflict, in_conflict)
      else:
        self.checkConflicts(im)
        self.assertEqual(self.ubercart[im].IntegrationModule_getSignatureDiff(), "No diff")
        self.assertEqual(self.ubercart[im].IntegrationModule_getTioSafeXMLDiff(), "No diff")
    self.checkSaleSupply()

  def checkSaleSupply(self):
    for document in self.getPortalObject().product_module.contentValues():
      if document.getValidationState() == 'validated' and document.getId() != self.default_resource_id:
        self.assertEqual(len([x for x in document.Base_getRelatedObjectList() if x.getPortalType() == "Sale Supply Line"]), 1)

  def checkSaleTradeConditionRelation(self, module, excluded_title_list=[]):
    for document in module.contentValues():
      if document.getValidationState() == 'validated' and \
             document.getId() != self.default_node_id:
        if document.getTitle() not in excluded_title_list:
          self.assertEqual(len([x for x in document.Base_getRelatedObjectList() if x.getPortalType() == "Sale Trade Condition"]), 1)
        else:
         self.assertEqual(len([x for x in document.Base_getRelatedObjectList() if x.getPortalType() == "Sale Trade Condition"]), 0) 

  def runPersonSync(self):
    """
    test synchronization of person
    """

    INITIAL_PERSON_TITLE = ["Simple person",
                            "Person into Organisation",
                            "Person into delivery organisation", 
			    "Person shipping to another person"]
    #
    # Initial cleanup & settings
    #
    ubercart_test_module = self.portal.ubercart_test_module
    person_portal_type_list = ["Ubercart Test Person", "Ubercart Test Delivery Person",]
    # Delete person & organisations
    org_ids = [x for x in self.portal.organisation_module.objectIds() if x != self.default_source_id]
    self.portal.organisation_module.manage_delObjects(org_ids)
    person_ids = [x for x in self.portal.person_module.objectIds() if x != self.default_node_id]
    self.portal.person_module.manage_delObjects(person_ids)
    # Validate some persons
    for person in ubercart_test_module.contentValues(portal_type=person_portal_type_list):
      if person.getId() != self.default_node_id and person.getValidationState() != "validated":
        person.validate()

    self.tic()
    # Check initial data
    self.assertEqual(len(ubercart_test_module.contentValues(portal_type="Ubercart Test Person")), 2)
    self.assertEqual(len(ubercart_test_module.contentValues(portal_type="Ubercart Test Delivery Person")), 2)
    self.assertEqual(len(self.ubercart.person_module.getObjectList()), 2)
    self.assertEqual(len(self.ubercart.delivered_person_module.getObjectList()), 2)
    self.assertEqual(len(self.ubercart.delivered_organisation_module.getObjectList()), 1)
    self.assertEqual(len(self.ubercart.organisation_module.getObjectList()), 1)
    original_person_module_length = len(self.portal.person_module.contentValues())
    self.assertEqual(len(self.portal.organisation_module.contentValues()), 1)
    # store person that will be synced
    person_dict = {}
    for person in ubercart_test_module.contentValues(portal_type="Ubercart Test Person"):
      person_dict[person.getFirstname()] = ('person', person.getPath())
      if person.getCompany(None):
        person_dict[person.getCompany()] = ('organisation', person.getPath())

    for person in ubercart_test_module.contentValues(portal_type="Ubercart Test Delivery Person"):
      person_dict[person.getFirstname()] = ('delivered_person', person.getPath())
      if person.getCompany(None):
        person_dict[person.getCompany()] = ('delivered_organisation', person.getPath())


    #
    # Do & Check initial synchronization
    #
    self._runAndCheckNodeSynchronization()
    self.checkSaleTradeConditionRelation(self.getPortalObject().person_module)
    self.checkSaleTradeConditionRelation(self.getPortalObject().organisation_module)
    self.assertEqual(len(self.portal.person_module.contentValues()), original_person_module_length+4)
    self.assertEqual(len(self.portal.organisation_module.contentValues()), 3)
    for person in self.portal.person_module.contentValues():
      if person.getId() != self.default_node_id:
        self.assertEqual(person.getValidationState(), 'validated')
        node_type, test_person = person_dict.get(person.getFirstName(), None)
        if node_type in ["person", "delivered_person"]:
          test_person = self.portal.restrictedTraverse(test_person)
          self.assertNotEqual(test_person, None)
          self.assertEqual(test_person.getLastname(), person.getLastName())
          self.assertEqual(test_person.getEmail(), person.getDefaultEmailText())
          if not person.getSubordinationValue(None):
            # Check default address
            default_address = person.get("default_address", None)
            self.assertNotEqual(default_address, None)
            self.assertEqual(test_person.getStreet(), default_address.getStreetAddress())
            self.assertEqual(test_person.getZip(), default_address.getZipCode())
            self.assertEqual(test_person.getCity(), default_address.getCity())
        elif node_type in ["organisation", "delivered_organisation",]:
          test_person = self.portal.restrictedTraverse(test_person)
          self.assertNotEqual(test_person, None)
          # Check default address
          default_address = person.get("default_address", None)
          self.assertNotEqual(default_address, None)
          self.assertEqual(test_person.getStreet(), default_address.getStreetAddress())
          self.assertEqual(test_person.getZip(), default_address.getZipCode())
          self.assertEqual(test_person.getCity(), default_address.getCity())
        else:
          raise ValueError, 'bad type'

    #
    # Modify persons on the plugin side
    #
    mapping_dict = {}
    for person in ubercart_test_module.contentValues(portal_type=person_portal_type_list):
      if person.getTitle() == 'Simple Person':
        # Change basic informations
        mapping_dict[person.getId()] = {"street":person.getStreet(),
                                        "zip":person.getZip(),
                                        "city":person.getCity(),
                                        "company":person.getCompany()}

        person.edit(street="10 rue jaune",
                    zip="56897",
                    city="Manhatan",
                    company="")
      elif person.getTitle() == 'Person into Organisation':
        # Change company name
        mapping_dict[person.getId()] = {"company":person.getCompany(),}
        person.edit(company="Etoile Noire", company_id="Etoile Noire")
      elif person.getTitle() == "Person into delivery organisation":
        # change shipping company address
        mapping_dict[person.getId()] = {"street":person.getStreet(),
                                        "zip":person.getZip(),
                                        "city":person.getCity(),
                                        "company":person.getCompany()}
      
        person.edit(street="101 rue de la forêt",
                    zip="567990",
                    city="Mânhatan",)
      elif person.getTitle() == "Person shipping to another person":
        mapping_dict[person.getId()] = {"street":person.getStreet(),
                                        "zip":person.getZip(),
                                        "city":person.getCity(),
                                        "company":person.getCompany()}

        person.edit(street="99 rue de la faillette",
                    zip="589799",
                    city="New Jersey",)
        


    # Validate remaining persons
    for person in ubercart_test_module.contentValues(portal_type=person_portal_type_list):
      if person.getId() != self.default_node_id and person.getValidationState() != "validated":
        person.validate()
   
    try:
      self.assertEqual(len(mapping_dict), 4)
      self._runAndCheckNodeSynchronization(reset=False)
      self.checkSaleTradeConditionRelation(self.getPortalObject().person_module)
      self.checkSaleTradeConditionRelation(self.getPortalObject().organisation_module)
      self.assertEqual(len(self.portal.person_module.contentValues()), original_person_module_length+4)
      self.assertEqual(len(self.portal.organisation_module.contentValues()), 4)
      #
      # Modify the delivery organisation
      #
      for person in ubercart_test_module.contentValues(portal_type=person_portal_type_list):
        if person.getTitle() == "Person into delivery organisation":
          mapping_dict[person.getId()] = {"street":person.getStreet(),
                                          "zip":person.getZip(),
					  "city":person.getCity()
                                          }
          person.edit(street="10 rue saint Andrêt",
                      zip="6555656",
		      city="York")

      self._runAndCheckNodeSynchronization(reset=False)
      self.checkSaleTradeConditionRelation(self.getPortalObject().person_module)
      self.checkSaleTradeConditionRelation(self.getPortalObject().organisation_module)
      self._runAndCheckNodeSynchronization(reset=True)
      #
      # Generates conflict on all properties
      #
      for person in ubercart_test_module.contentValues(portal_type=person_portal_type_list):
        if person.getTitle() == "Person into Organisation":
          person.edit(street="Street Conflict",
		      city="Lille",
		      zip="9999",	  
		     )
      for org in self.portal.organisation_module.searchFolder(validation_state="validated"):
        if org.getTitle() == "Etoile Noire":
          org.setDefaultAddressStreetAddress("addresse conflit")
          org.setDefaultAddressZipCode("6666")
	  org.setDefaultAddressCity("Paris")
      self._runAndCheckNodeSynchronization(reset=False, conflict_dict={'organisation_module' : (3,0, True)}, )
      self.checkSaleTradeConditionRelation(self.getPortalObject().person_module)
      self.checkSaleTradeConditionRelation(self.getPortalObject().organisation_module)
      # Fix all conflicts & run sync again
      for conflict in self.ubercart.organisation_module.getSourceSectionValue().getConflictList():
        if conflict.getParentValue().getValidationState() == "conflict":
          conflict.getParentValue().resolveConflictWithMerge()
      self._runAndCheckNodeSynchronization(reset=False, conflict_dict={'organisation_module' : (3,0, False)})
      self.assertEqual(self.ubercart.organisation_module.IntegrationModule_getSignatureDiff(), "No diff")
      self.checkSaleTradeConditionRelation(self.getPortalObject().person_module)
      self.checkSaleTradeConditionRelation(self.getPortalObject().organisation_module)
    finally:
      # Reset data on person
      for person in ubercart_test_module.contentValues(portal_type="Ubercart Test Person"):
        mapping = mapping_dict.get(person.getId(), None)
        if mapping is not None:
          person.edit(**mapping)

  def List_getObjectByTitle(self, object_list=None, title=""):
    if object_list==None:
      return None
    for object in object_list:
      if object.getTitle() == title:
        return object
    return None
    
  def runProductSync(self):
    """
    test synchronization of prodcut
    """
    # Delete products
    
    prod_ids = [x for x in self.portal.product_module.objectIds() if x != self.default_resource_id]
    self.portal.product_module.manage_delObjects(prod_ids)
    self.tic()
    # Check initial data
    for product in self.portal.ubercart_test_module.contentValues(portal_type="Ubercart Test Product"):
      if product.getValidationState() != "validated":
        product.validate()
    self.tic()

    self.assertEqual(len(self.portal.ubercart_test_module.contentValues(portal_type="Ubercart Test Product",
                                                                       validation_state="validated")), 2)
    original_product_module_lenght = len(self.portal.product_module.contentValues())
    # store product that will be synced
    product_dict = {}
    for product in self.portal.ubercart_test_module.contentValues(portal_type="Ubercart Test Product"):
      product_dict[product.getReference()] = product.getPath()
    # run synchronization
    self._runAndCheckResourceSynchronization(reset=True)
    self.assertEqual(len(self.portal.product_module.contentValues()), original_product_module_lenght+2)

    for product in self.portal.product_module.contentValues():
      if product.getId() != self.default_resource_id:
        self.assertEqual(product.getValidationState(), 'validated')
        test_product = product_dict.get(product.getReference(), None)
        self.assertNotEqual(test_product, None)
        test_product = self.portal.restrictedTraverse(test_product)
        self.assertNotEqual(test_product, None)
        self.assertEqual(test_product.getTitle(), product.getTitle())

    # Backup data
    mapping_dict = {}
    for product in self.portal.ubercart_test_module.contentValues(portal_type="Ubercart Test Product"):
      mapping_dict[product.getId()] = {"title": product.getTitle(),
                                       "reference": product.getReference()}
      if product.getTitle() == "Bague":
        product.edit(title="Bracelet")

    for product in self.portal.ubercart_test_module.contentValues(portal_type="Ubercart Test Product"):
      if product.getValidationState() != "validated":
        product.validate()

    self.assertEqual(len(self.portal.ubercart_test_module.contentValues(portal_type="Ubercart Test Product",
                                                                      validation_state="validated")), 2)
    try:
      self.assertEqual(len(mapping_dict), 2)
      self._runAndCheckResourceSynchronization(reset=False)
      self.assertEqual(len(self.portal.product_module.contentValues()), original_product_module_lenght+2)

      for product in self.portal.product_module.searchFolder(validation_state="validated"):
        if product.getTitle() == "Bracelet":
          product.edit(title="Bague")
      self._runAndCheckResourceSynchronization(reset=False)
    finally:
      # Reset data on product
      for product in self.portal.ubercart_test_module.contentValues(portal_type="Ubercart Test Product"):
        mapping = mapping_dict.get(product.getId(), None)
        if mapping is not None:
          product.edit(**mapping)
    
    flower = flower_test = None
    #verifying category creation after synchronisation pluging -> erp5
    for product in self.portal.product_module.objectValues():
      if product.getTitle() == "Fleure":
	flower = product
        category_list = product.contentValues(portal_type="Product Individual Variation")
        self.assertEqual(len(category_list), 1)
    
    #modifying category pluging -> erp5
    for product_test in self.portal.ubercart_test_module.contentValues(portal_type="Ubercart Test Product"):
      if product_test.getTitle() == "Fleure":
	flower_test = product_test
        flower_test.objectValues()[0].setCategory("Catalog/Fleure/Rose")
	self.tic()

    
    self._runAndCheckResourceSynchronization(reset=False)
    flower = self.List_getObjectByTitle(self.portal.product_module.objectValues(), "Fleure")
    flower_test = self.List_getObjectByTitle(self.portal.ubercart_test_module.contentValues( \
	                                 portal_type="Ubercart Test Product"), "Fleure")
    if flower is not None and flower_test is not None:
      tiosafe_category_list = flower.contentValues()
      plugin_category_list = flower_test.contentValues()
      self.assertEqual(len(tiosafe_category_list), len(plugin_category_list))
      cat = flower.objectValues()[0].getTitle()
      self.assertEqual(cat,"Fleure/Rose")
    
    #deleting category pluging -> erp5
    flower = self.List_getObjectByTitle(self.portal.product_module.objectValues(), "Fleure")
    flower_test = self.List_getObjectByTitle(self.portal.ubercart_test_module.contentValues( \
		                            portal_type="Ubercart Test Product"), "Fleure")
    if flower is not None and flower_test is not None:
      deleted_cat_list = [c.getId() for c in flower_test.objectValues()]
      flower_test.manage_delObjects(deleted_cat_list)
      self.tic()
      tiosafe_category_list = flower.contentValues()
      plugin_category_list = flower_test.contentValues()
      self.assertEqual(len(tiosafe_category_list), len(plugin_category_list)+1)
    self._runAndCheckResourceSynchronization(reset=False)

    flower = self.List_getObjectByTitle(self.portal.product_module.objectValues(), "Fleure")
    flower_test = self.List_getObjectByTitle(self.portal.ubercart_test_module.contentValues( \
		                            portal_type="Ubercart Test Product"), "Fleure")
    if flower is not None and flower_test is not None: 
      tiosafe_category_list = flower.contentValues()
      plugin_category_list = flower_test.contentValues()
      self.assertEqual(len(tiosafe_category_list), 0)
      self.assertEqual(len(tiosafe_category_list), len(plugin_category_list))

    ## test synchronisation for variation erp5 -> pluging
    # creation erp5 -> pluging  
    if flower is not None:
      piv = flower.newContent(portal_type="Product Individual Variation")
      piv.setTitle("Fleure/Calice")
      piv.setVariationBaseCategory("collection")
      self.tic()
    
    if flower is not None and flower_test is not None:
      tiosafe_category_list = flower.contentValues()
      plugin_category_list = flower_test.contentValues()
      self.assertEqual(len(tiosafe_category_list), 1)
      self.assertEqual(len(tiosafe_category_list), len(plugin_category_list)+1)
    self._runAndCheckResourceSynchronization(reset=False)

    flower = self.List_getObjectByTitle(self.portal.product_module.objectValues(), "Fleure")
    flower_test = self.List_getObjectByTitle(self.portal.ubercart_test_module.contentValues( \
                                            portal_type="Ubercart Test Product"), "Fleure")
    if flower is not None and flower_test is not None:
      tiosafe_category_list = flower.contentValues()
      plugin_category_list = flower_test.contentValues()
      self.assertEqual(len(plugin_category_list), 1)
      self.assertEqual(len(tiosafe_category_list), len(plugin_category_list))

    flower = self.List_getObjectByTitle(self.portal.product_module.objectValues(), "Fleure")
    flower_test = self.List_getObjectByTitle(self.portal.ubercart_test_module.contentValues( \
                                            portal_type="Ubercart Test Product"), "Fleure")
    # modification category erp5 -> pluging
    if flower is not None and flower_test is not None:
      flower.objectValues()[0].setTitle("Fleure/Samanta/Ndiondome")
      flower.objectValues()[0].setVariationBaseCategory("collection")
      self.tic()
      category = flower.objectValues()[0].getTitle()
      category_test = flower_test.objectValues()[0].getCategory()
      self.assertEqual(category_test, "Catalog/Fleure/Calice")
      self.assertEqual(category, "Fleure/Samanta/Ndiondome")
    self._runAndCheckResourceSynchronization(reset=False)
    flower = self.List_getObjectByTitle(self.portal.product_module.objectValues(), "Fleure")
    flower_test = self.List_getObjectByTitle(self.portal.ubercart_test_module.contentValues( \
                                            portal_type="Ubercart Test Product"), "Fleure")
    
    if flower is not None and flower_test is not None:
      tiosafe_category_list = flower.contentValues()
      plugin_category_list = flower_test.contentValues()
      self.assertEqual(len(plugin_category_list), 1)
      self.assertEqual(len(tiosafe_category_list), len(plugin_category_list))
      category = flower.objectValues()[0].getTitle()
      category_test = flower_test.objectValues()[0].getCategory()
      self.assertEqual(category_test, "Catalog/Fleure/Samanta/Ndiondome")
      self.assertEqual(category, "Fleure/Samanta/Ndiondome")
    
    # removing category erp5 -> pluging
    flower = self.List_getObjectByTitle(self.portal.product_module.objectValues(), "Fleure")
    flower_test = self.List_getObjectByTitle(self.portal.ubercart_test_module.contentValues( \
                                            portal_type="Ubercart Test Product"), "Fleure")
    if flower is not None and flower_test is not None:
      tiosafe_category_list = flower.contentValues()
      plugin_category_list = flower_test.contentValues()
      self.assertEqual(len(plugin_category_list), 1)
      self.assertEqual(len(tiosafe_category_list), len(plugin_category_list))
      deleted_category_list = [cat.getId() for cat in flower.contentValues()]     
      flower.manage_delObjects(deleted_category_list)
      tiosafe_category_list = flower.contentValues()
      self.assertEqual(len(tiosafe_category_list), 0)
    self._runAndCheckResourceSynchronization(reset=False)  
    flower = self.List_getObjectByTitle(self.portal.product_module.objectValues(), "Fleure")
    flower_test = self.List_getObjectByTitle(self.portal.ubercart_test_module.contentValues( \
                                            portal_type="Ubercart Test Product"), "Fleure")
    if flower is not None and flower_test is not None:
      tiosafe_category_list = flower.contentValues()
      plugin_category_list = flower_test.contentValues()
      self.assertEqual(len(plugin_category_list), 0)
      self.assertEqual(len(tiosafe_category_list), len(plugin_category_list))

    #
    # Generates conflicts
    #
    for product in self.portal.ubercart_test_module.contentValues(portal_type="Ubercart Test Product"):
      if product.getTitle() == "Bague":
        product.edit(title="Diaro conflit",)
    for prod in self.portal.product_module.searchFolder(validation_state="validated"):
      if prod.getTitle() == "Bague":
        prod.setTitle("Ring conflict")
    self._runAndCheckResourceSynchronization(reset=False, conflict_dict={'product_module' : (1,0, True)}, )
    # Fix all conflicts & run sync again
    for conflict in self.ubercart.product_module.getSourceSectionValue().getConflictList():
      if conflict.getParentValue().getValidationState() == "conflict":
        conflict.getParentValue().resolveConflictWithMerge()
    self._runAndCheckResourceSynchronization(reset=False, conflict_dict={'product_module' : (1,0, False)})
    self.assertEqual(self.ubercart.product_module.IntegrationModule_getSignatureDiff(), "No diff")

  def runSaleOrderSync(self):
    """
    test synchronization of sale order
    """
    # Delete sale_orders
    so_ids = list(self.portal.sale_order_module.objectIds())
    self.portal.sale_order_module.manage_delObjects(so_ids)
    # Define date on integration site
    self.ubercart.edit(stop_date="2010/12/01")
    self.tic()
    # Check initial data
    self.assertEqual(len(self.portal.ubercart_test_module.contentValues(portal_type="Ubercart Test Sale Order")), 1)
    self.assertEqual(len(self.portal.sale_order_module.contentValues()), 0)
    # store person that will be synced
    sale_order_dict = {}
    for sale_order in self.portal.ubercart_test_module.contentValues(portal_type="Ubercart Test Sale Order"):
      sale_order_dict[sale_order.getId()] = sale_order.getPath()

    # run synchronization
    self.ubercart.IntegrationSite_synchronize(reset=True, synchronization_list=['sale_order_module',],
                                            batch_mode=True)
    self.tic()

    # Check fix point
    for im in ['sale_order_module',]:
      self.assertEqual(self.ubercart[im].IntegrationModule_getTioSafeXMLDiff(), "No diff")
      self.assertEqual(self.ubercart[im].IntegrationModule_getSignatureDiff(), "No diff")

    self.assertEqual(len(self.portal.sale_order_module.contentValues()), 1)
    

    for sale_order in self.portal.sale_order_module.contentValues():
      self.assertEqual(sale_order.getSimulationState(), 'confirmed')
      test_sale_order = sale_order_dict.get(sale_order.getReference(), None)
      self.assertNotEqual(test_sale_order, None)
      test_sale_order = self.portal.restrictedTraverse(test_sale_order)
      self.assertNotEqual(test_sale_order, None)
      # Check amount
      total_price = float(getattr(test_sale_order, 'order_total'))
      self.assertEqual("%.2f" % (round(total_price, 2),), "%.2f" % (round(sale_order.getTotalPrice(),2),))
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
    self.ubercart.edit(stop_date="2010/10/31")
    self.tic()

    # run synchronization
    self.ubercart.IntegrationSite_synchronize(reset=False, synchronization_list=['sale_order_module',],
                                            batch_mode=True)
    self.tic()
    self.checkConflicts('sale_order_module')
    # Check fix point
    for im in ['sale_order_module',]:
      self.assertEqual(self.ubercart[im].IntegrationModule_getTioSafeXMLDiff(), "No diff")
      self.assertEqual(self.ubercart[im].IntegrationModule_getSignatureDiff(), "No diff")

    self.assertEqual(len(self.portal.sale_order_module.contentValues()), 1)
    for sale_order in self.portal.sale_order_module.contentValues():
      self.assertEqual(sale_order.getSimulationState(), 'confirmed')
      test_sale_order = sale_order_dict.get(sale_order.getReference(), None)
      self.assertNotEqual(test_sale_order, None)
      test_sale_order = self.portal.restrictedTraverse(test_sale_order)
      self.assertNotEqual(test_sale_order, None)
      # Check amount
      total_price = float(getattr(test_sale_order, 'order_total'))
      self.assertEqual("%.2f" % (round(total_price, 2),), "%.2f" % (round(sale_order.getTotalPrice(),2),))
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
      if sale_order.getReference() == "7":
        # Nothing must be linked to Unknown
        for line in sale_order.contentValues(portal_type="Sale Order Line"):
          self.assertNotEqual(line.getResource(), self.ubercart.getResource())
        self.assertEqual(sale_order.getSource(), self.ubercart.getSourceAdministration())
        self.assertEqual(sale_order.getSourceSection(), self.ubercart.getSourceAdministration())
        self.assertEqual(sale_order.getSourceDecision(), self.ubercart.getSourceAdministration())
        self.assertEqual(sale_order.getSourceAdministration(), self.ubercart.getSourceAdministration())
        self.assertNotEqual(sale_order.getDestination(), self.ubercart.getDestination())
        self.assertNotEqual(sale_order.getDestinationSection(), self.ubercart.getDestination())
        self.assertNotEqual(sale_order.getDestinationDecision(), self.ubercart.getDestination())
        self.assertNotEqual(sale_order.getDestinationAdministration(), self.ubercart.getDestination())


  @expectedFailure
  def testFullSync(self):
    self.runPersonSync()
    self.runProductSync()
    self.runSaleOrderSync()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestUbercartSynchronization))
  return suite

