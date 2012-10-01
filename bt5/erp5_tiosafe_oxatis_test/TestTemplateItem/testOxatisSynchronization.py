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

from Products.ERP5Type.tests.backportUnittest import expectedFailure

class TestOxatisSynchronization(ERP5TypeTestCase):
  """
  """

  def getBusinessTemplateList(self):
    """ Return the list of BT required by unit tests. """
    return (
      'erp5_core_proxy_field_legacy',
      'erp5_full_text_myisam_catalog',
      'erp5_base',
      'erp5_pdm',
      'erp5_simulation',
      'erp5_trade',
      'erp5_syncml',
      'erp5_tiosafe_core',
      'erp5_tiosafe_pdm',
      'erp5_tiosafe_test',
      'erp5_tiosafe_oxatis',
      'erp5_tiosafe_oxatis_test',
      )

  def getTitle(self):
    return "Test Oxatis Synchronization"

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    self.portal = self.getPortal()
    self.oxatis = self.portal.portal_integrations.oxatis

    # Create a user for sync
    acl_users = self.portal.acl_users
    acl_users._doAddUser('TioSafeUser', 'TioSafeUserPassword', ['Manager'], [])
    user = acl_users.getUserById('TioSafeUser').__of__(acl_users)
    newSecurityManager(None, user)

    # Validate rules
    for rule in self.portal.portal_rules.objectValues():
      rule.validate()

    if self.oxatis.getValidationState() != "validated":
      self.oxatis.validate()

    self.oxatis.getDestinationValue().validate()
    self.default_node_id = self.oxatis.getDestinationValue().getId()
    self.oxatis.getResourceValue().validate()
    self.default_resource_id = self.oxatis.getResourceValue().getId()
    self.default_source_id = self.oxatis.getSourceAdministrationValue().getId()

    for connector in self.oxatis.contentValues(portal_type="Web Service Connector"):
      # use the test connector
      connector.setTransport("oxatis_test")

    # Update url of pub/sub & validate them
    utils = ZopeTestCase.utils
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
    for connector in self.oxatis.contentValues(portal_type="Web Service Connector"):
      # use the test connector
      connector.setTransport("oxatis")
    self.tic()



  def _runAndCheckNodeSynchronization(self, reset=True, conflict_dict=None):
    # run synchronization
    for im in ['organisation_module', 'delivered_organisation_module',
               'person_module', 'delivered_person_module',]:
      LOG("RUNNING SYNCHRO FOR %s" %(im), 300, "")
      self.tic()
      self.oxatis.IntegrationSite_synchronize(reset=reset, synchronization_list=[im,],
                                              batch_mode=True)

      self.tic()
      if conflict_dict and conflict_dict.has_key(im):
        nb_pub_conflict, nb_sub_conflict, in_conflict = conflict_dict[im]
        self.checkConflicts(im, nb_pub_conflict, nb_sub_conflict, in_conflict)
      else:
        self.checkConflicts(im)
        self.assertEqual(self.oxatis[im].IntegrationModule_getSignatureDiff(), "No diff")
        try:
          self.assertEqual(self.oxatis[im].IntegrationModule_getTioSafeXMLDiff(html=False), "No diff")
        except AssertionError:
          diff = "\n"
          for line in self.oxatis[im].IntegrationModule_getTioSafeXMLDiff(html=False).split('\n'):
            diff += "%s\n" %(line)
          raise AssertionError, diff



  def checkConflicts(self, module, nb_pub_conflicts=0, nb_sub_conflicts=0, in_conflict=True):
    module = self.oxatis[module]
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

  def _runAndCheckResourceSynchronization(self, reset=True):
    # run synchronization
    self.tic()
    self.oxatis.IntegrationSite_synchronize(reset=reset, synchronization_list=['product_module',],
                                            batch_mode=True)

    self.tic()
    # Check fix point
    for im in ['product_module']:
      self.assertEqual(self.oxatis[im].IntegrationModule_getTioSafeXMLDiff(html=False), "No diff")
      self.assertEqual(self.oxatis[im].IntegrationModule_getSignatureDiff(), "No diff")
    self.checkConflicts(im)
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

  def runPersonSync(self):
    """
    test synchronization of person
    """

    INITIAL_PERSON_TITLE = ["Simple person",
                            "Person shipping to another person",
                            "Person into an organisation",
                            "Person with shipping into org"]
    #
    # Initial cleanup & settings
    #

    # Delete person & organisations
    org_ids = [x for x in self.portal.organisation_module.objectIds() if x != self.default_source_id]
    self.portal.organisation_module.manage_delObjects(org_ids)
    person_ids = [x for x in self.portal.person_module.objectIds() if x != self.default_node_id]
    self.portal.person_module.manage_delObjects(person_ids)
    # Validate some persons
    for person in self.portal.oxatis_test_module.contentValues(portal_type="Oxatis Test Person"):
      if person.getTitle() in INITIAL_PERSON_TITLE:
        if person.getValidationState() != "validated":
          person.validate()
      else:
        if person.getValidationState() == "validated":
          person.invalidate()
    self.tic()
    # Check initial data
    self.assertEqual(len(self.portal.oxatis_test_module.contentValues(portal_type="Oxatis Test Person")), 6)
    self.assertEqual(len(self.oxatis.person_module.getObjectList()), 4)
    self.assertEqual(len(self.oxatis.delivered_person_module.getObjectList()), 2)
    self.assertEqual(len(self.oxatis.delivered_organisation_module.getObjectList()), 1)
    self.assertEqual(len(self.oxatis.organisation_module.getObjectList()), 1)
    original_person_module_length = len(self.portal.person_module.contentValues())
    self.assertEqual(len(self.portal.organisation_module.contentValues()), 1)
    # store person that will be synced
    person_dict = {}
    for person in self.portal.oxatis_test_module.contentValues(portal_type="Oxatis Test Person"):
      person_dict[person.getFirstname()] = ('person', person.getPath())
      if person.getCompany(None):
        person_dict[person.getCompany()] = ('organisation', person.getPath())
      if person.getShippingcompany(None):
        person_dict[person.getShippingcompany()] = ('delivered_organisation', person.getPath())
      if person.getShippingfirstname(None) and \
         person.getShippingfirstname() != person.getFirstname():
        person_dict[person.getShippingfirstname()] = ('delivered_person', person.getPath())


    #
    # Do & Check initial synchronization
    #
    self._runAndCheckNodeSynchronization()
    self.checkSaleTradeConditionRelation(self.getPortalObject().person_module)
    self.checkSaleTradeConditionRelation(self.getPortalObject().organisation_module)


    self.assertEqual(len(self.portal.person_module.contentValues()), original_person_module_length+6)
    self.assertEqual(len(self.portal.organisation_module.contentValues()), 2)
    for person in self.portal.person_module.contentValues():
      if person.getId() != self.default_node_id:
        self.assertEqual(person.getValidationState(), 'validated')
        node_type, test_person = person_dict.get(person.getFirstName(), None)
        if node_type == "person":
          test_person = self.portal.restrictedTraverse(test_person)
          self.assertNotEqual(test_person, None)
          self.assertEqual(test_person.getLastname(), person.getLastName())
          self.assertEqual(test_person.getEmail(), person.getDefaultEmailText())
          if not person.getSubordinationValue(None):
            # Check phones
            self.assertEqual(test_person.getBillingphone(), person.getDefaultTelephoneText())
            self.assertEqual(test_person.getBillingcellphone(), person.getMobileTelephoneText())
            self.assertEqual(test_person.getBillingfax(), person.getDefaultFaxText())
            # Check default address
            default_address = person.get("default_address", None)
            self.assertNotEqual(default_address, None)
            self.assertEqual(test_person.getBillingaddress(), default_address.getStreetAddress())
            self.assertEqual(test_person.getBillingzipcode(), default_address.getZipCode())
            self.assertEqual(test_person.getBillingcity(), default_address.getCity())
        elif node_type == "delivered_person":
          test_person = self.portal.restrictedTraverse(test_person)
          self.assertNotEqual(test_person, None)
          self.assertEqual(test_person.getShippinglastname(), person.getLastName())
          self.assertEqual(test_person.getEmail(), person.getDefaultEmailText())
          if not person.getSubordinationValue(None):
            # Check phones
            self.assertEqual(test_person.getShippingphone(), person.getDefaultTelephoneText())
            # Check default address
            default_address = person.get("default_address", None)
            self.assertNotEqual(default_address, None)
            self.assertEqual(test_person.getShippingaddress(), default_address.getStreetAddress())
            self.assertEqual(test_person.getShippingzipcode(), default_address.getZipCode())
            self.assertEqual(test_person.getShippingcity(), default_address.getCity())
        elif node_type == "organisation":
          test_person = self.portal.restrictedTraverse(test_person)
          self.assertNotEqual(test_person, None)
          # Check phones
          self.assertEqual(test_person.getBillingphone(), person.getDefaultTelephoneText())
          self.assertEqual(test_person.getBillingcellphone(), person.getMobileTelephoneText())
          self.assertEqual(test_person.getBillingfax(), person.getDefaultFaxText())
          # Check default address
          default_address = person.get("default_address", None)
          self.assertNotEqual(default_address, None)
          self.assertEqual(test_person.getBillingaddress(), default_address.getStreetAddress())
          self.assertEqual(test_person.getBillingzipcode(), default_address.getZipCode())
          self.assertEqual(test_person.getBillingcity(), default_address.getCity())
        elif node_type == "delivered_organisation":
          test_person = self.portal.restrictedTraverse(test_person)
          self.assertNotEqual(test_person, None)
          # Check phones
          self.assertEqual(test_person.getShippingphone(), person.getDefaultTelephoneText())
          # Check default address
          default_address = person.get("default_address", None)
          self.assertNotEqual(default_address, None)
          self.assertEqual(test_person.getShippingaddress(), default_address.getStreetAddress())
          self.assertEqual(test_person.getShippingzipcode(), default_address.getZipCode())
          self.assertEqual(test_person.getShippingcity(), default_address.getCity())
        else:
          raise ValueError, 'bad type'

    #
    # Modify persons on the plugin side
    #
    mapping_dict = {}
    for person in self.portal.oxatis_test_module.contentValues(portal_type="Oxatis Test Person"):
      if person.getTitle() == 'Simple person':
        # Change basic informations
        mapping_dict[person.getId()] = {"billingaddress":person.getBillingaddress(),
                                        "billingzipcode":person.getBillingzipcode(),
                                        "billingcity":person.getBillingcity(),
                                        "billingphone":person.getBillingphone(),
                                        "billingcellphone":person.getBillingcellphone(),
                                        "billingfax":person.getBillingfax(),
                                        "company":person.getCompany()}

        person.edit(billingaddress="10 rue jaune",
                    billingzipcode="59000",
                    billingcity="Lille",
                    billingphone="",
                    billingcellphone="1111111",
                    billingfax="2222222",
                    company="SNCF")
      elif person.getTitle() == 'Person shipping to another person':
        # Change shipping person
        mapping_dict[person.getId()] = {"shippingfirstname":person.getShippingfirstname(),
                                        "shippinglastname":person.getShippinglastname(),}
        person.edit(shippingfirstname="Chew",
                    shippinglastname="Baccâl")

      elif person.getTitle() == 'Person into an organisation':
        # Change company name
        mapping_dict[person.getId()] = {"company":person.getCompany(),}
        person.edit(company="Etoile Noire")
      elif person.getTitle() == "Person with shipping into org":
        # change shipping company address
        mapping_dict[person.getId()] = {"shippingaddress":person.getShippingaddress(),
                                        "shippingzipcode":person.getShippingzipcode(),
                                        "shippingcity":person.getShippingcity(),
                                        "shippingphone":person.getShippingphone(),}
        person.edit(shippingaddress="101 rue de la forêt",
                    shippingzipcode="59000",
                    shippingcity="Lîlle",
                    shippingphone="",)

    # Validate remaining persons
    for person in self.portal.oxatis_test_module.contentValues(portal_type="Oxatis Test Person"):
      if person.getValidationState() != "validated":
        person.validate()

    try:
      self.assertEqual(len(mapping_dict), 4)
      self._runAndCheckNodeSynchronization(reset=False)
      self.checkSaleTradeConditionRelation(self.getPortalObject().person_module, excluded_title_list='luke skywalker')
      self.checkSaleTradeConditionRelation(self.getPortalObject().organisation_module)
      self.assertEqual(len(self.portal.person_module.contentValues()), original_person_module_length+10)
      self.assertEqual(len(self.portal.organisation_module.contentValues()), 5)


      #
      # Modify person on both side
      #
      for person in self.portal.person_module.searchFolder(validation_state="validated"):
        if person.getTitle() == "test-Aurélien Calonne":
          # remove company link
          person.default_career.setSubordination("")
          # define phone and adress
          person.setDefaultTelephoneText("454545445")
          person.setDefaultAddressStreetAddress("10 Route 66")
          person.setDefaultAddressZipCode("534322")
          person.setDefaultAddressCity("Paris")
          person.setDefaultAddressRegion("france")
      for person in self.portal.oxatis_test_module.contentValues(portal_type="Oxatis Test Person"):
        if person.getTitle() == "Simple person":
          person.edit(billingcellphone="0129834765")

      #
      # Modify the organisation with multiple addresses on both sides
      #
      for person in self.portal.oxatis_test_module.contentValues(portal_type="Oxatis Test Person"):
        if person.getTitle() == "Organisation witth two address":
          mapping_dict[person.getId()] = {"billingaddress":person.getBillingaddress(),
                                          "shippingaddress":person.getShippingaddress(),
                                          }
          person.edit(billingaddress="10 rue saint Andrêt",
                      shippingaddress="1 rue saint Médart",)

      self._runAndCheckNodeSynchronization(reset=False)
      self.checkSaleTradeConditionRelation(self.getPortalObject().person_module, excluded_title_list='luke skywalker')
      self.checkSaleTradeConditionRelation(self.getPortalObject().organisation_module)

      #
      # Generates conflict on all properties
      #
      for person in self.portal.oxatis_test_module.contentValues(portal_type="Oxatis Test Person"):
        if person.getTitle() == "Organisation witth two address":
          person.edit(billingaddress="billing conflict",
                      billingzipcode="0000",
                      billingcity="ConflictTown",
                      billingphone="0000",
                      billingcellphone="00000",
                      billingfax="000000",
                      shippingaddress="shipping conflict",
                      shippingzipcode="0000",
                      shippingcity="ConflictTown",
                      shippingphone="0000",
                      )
      for org in self.portal.organisation_module.searchFolder(validation_state="validated"):
        if org.getTitle() == "WEE":
          org.setDefaultTelephoneText("9999")
          org.setMobileTelephoneText("9999")
          org.setDefaultFaxText("9999")
          org.setDefaultAddressStreetAddress("address conflit")
          org.setDefaultAddressZipCode("9999")
          org.setDefaultAddressCity("ConflitVille")
      self._runAndCheckNodeSynchronization(reset=False, conflict_dict={'organisation_module' : (7,0, True)}, )
      self.checkSaleTradeConditionRelation(self.getPortalObject().person_module, excluded_title_list='luke skywalker')
      self.checkSaleTradeConditionRelation(self.getPortalObject().organisation_module, excluded_title_list='SNCF')
      # Fix all conflicts & run sync again
      for conflict in self.oxatis.organisation_module.getSourceSectionValue().getConflictList():
        if conflict.getParentValue().getValidationState() == "conflict":
          LOG("changing %s to resolved" %(conflict.getParentValue().getPath(),), 300, "")
          conflict.getParentValue().resolveConflictWithMerge()
      self._runAndCheckNodeSynchronization(reset=False, conflict_dict={'organisation_module' : (7,0, False)})
      self.checkSaleTradeConditionRelation(self.getPortalObject().person_module, excluded_title_list='luke skywalker')
      self.checkSaleTradeConditionRelation(self.getPortalObject().organisation_module, excluded_title_list='SNCF')

    finally:
      # Reset data on person
      for person in self.portal.oxatis_test_module.contentValues(portal_type="Oxatis Test Person"):
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
    self.tic()
    # Check initial data
    for product in self.portal.oxatis_test_module.contentValues(portal_type="Oxatis Test Product"):
      if product.getTitle() == "Robe":
        if product.getValidationState() != "validated":
          product.validate()
      else:
        if product.getValidationState() == "validated":
          product.invalidate()
    self.tic()

    self.assertEqual(len(self.portal.oxatis_test_module.searchFolder(portal_type="Oxatis Test Product",
                                                                     validation_state="validated")), 1)
    original_product_module_lenght = len(self.portal.product_module.contentValues())
    # store product that will be synced
    product_dict = {}
    for product in self.portal.oxatis_test_module.contentValues(portal_type="Oxatis Test Product"):
      product_dict[product.getItemsku()] = product.getPath()

    # run synchronization
    self._runAndCheckResourceSynchronization(reset=True)
    self.assertEqual(len(self.portal.product_module.contentValues()), original_product_module_lenght+1)

    for product in self.portal.product_module.contentValues():
      if product.getId() != self.default_node_id:
        self.assertEqual(product.getValidationState(), 'validated')
        test_product = product_dict.get(product.getReference(), None)
        self.assertNotEqual(test_product, None)
        test_product = self.portal.restrictedTraverse(test_product)
        self.assertNotEqual(test_product, None)
        self.assertEqual(test_product.getName(), product.getTitle())
        self.assertEqual(test_product.getDescription(), product.getDescription())

    # Backup data
    mapping_dict = {}
    for product in self.portal.oxatis_test_module.contentValues(portal_type="Oxatis Test Product"):
      mapping_dict[product.getId()] = {"name": product.getName(),
                                       "itemsku": product.getItemsku(),
                                       "description": product.getDescription(),}
      if product.getTitle() == "Robe":
        product.edit(name="Robe longue",
                     description="Ceci est une robe longue")

    for product in self.portal.oxatis_test_module.contentValues(portal_type="Oxatis Test Product"):
      if product.getValidationState() != "validated":
        product.validate()
    self.tic()

    self.assertEqual(len(self.portal.oxatis_test_module.searchFolder(portal_type="Oxatis Test Product",
                                                                     validation_state="validated")), 7)

    try:
      self.assertEqual(len(mapping_dict), 7)
      self._runAndCheckResourceSynchronization(reset=False)
      self.assertEqual(len(self.portal.product_module.contentValues()), original_product_module_lenght+2)
      # Specific check for mapping
      for product in self.portal.product_module.searchFolder(validation_state="validated"):
        if product.getTitle() == "Jupe":
          self.assertEqual(len(product.objectValues(portal_type="Mapped Property Type")), 1)
          mapping = product.objectValues(portal_type="Mapped Property Type")[0]
          self.assertEqual(len(mapping.objectValues()), 5)
      # Modify on both side
      for product in self.portal.product_module.searchFolder(validation_state="validated"):
        if product.getTitle() == "Jupe":
          product.edit(title="Jupe courte", description="ceci est une jupe courte")
      for product in self.portal.oxatis_test_module.objectValues(portal_type="Oxatis Test Product"):
        if product.getReference() == "111126":
          product.edit(optionsvalues2="1", itemsku="R002-nr-pt")

      self._runAndCheckResourceSynchronization(reset=False)
    finally:
      # Reset data on product
      for product in self.portal.oxatis_test_module.contentValues(portal_type="Oxatis Test Product"):
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
    self.oxatis.edit(stop_date="2010/12/01")
    self.tic()
    # Check initial data
    self.assertEqual(len(self.portal.oxatis_test_module.contentValues(portal_type="Oxatis Test Sale Order")), 2)
    self.assertEqual(len(self.portal.sale_order_module.contentValues()), 0)
    # store person that will be synced
    sale_order_dict = {}
    for sale_order in self.portal.oxatis_test_module.contentValues(portal_type="Oxatis Test Sale Order"):
      sale_order_dict[sale_order.getReference()] = sale_order.getPath()

    # run synchronization
    self.oxatis.IntegrationSite_synchronize(reset=True, synchronization_list=['sale_order_module',],
                                            batch_mode=True)
    self.tic()

    # Check fix point
    for im in ['sale_order_module',]:
      self.assertEqual(self.oxatis[im].IntegrationModule_getTioSafeXMLDiff(html=False), "No diff")
      self.assertEqual(self.oxatis[im].IntegrationModule_getSignatureDiff(), "No diff")

    self.assertEqual(len(self.portal.sale_order_module.contentValues()), 1)

    for sale_order in self.portal.sale_order_module.contentValues():
      self.assertEqual(sale_order.getSimulationState(), 'confirmed')
      test_sale_order = sale_order_dict.get(sale_order.getReference(), None)
      self.assertNotEqual(test_sale_order, None)
      test_sale_order = self.portal.restrictedTraverse(test_sale_order)
      self.assertNotEqual(test_sale_order, None)
      # Check amount
      total_price = float(getattr(test_sale_order, 'SubTotalNet')) - \
                    float(getattr(test_sale_order, 'SubTotalVAT')) + \
                    float(getattr(test_sale_order, 'ShippingPriceTaxExcl'))
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
    self.oxatis.edit(stop_date="2010/12/31")
    self.tic()

    # run synchronization
    self.oxatis.IntegrationSite_synchronize(reset=False,
                                            synchronization_list=['sale_order_module',],
                                            batch_mode=True)
    self.tic()
    self.checkConflicts('sale_order_module')
    # Check fix point
    for im in ['sale_order_module',]:
      self.assertEqual(self.oxatis[im].IntegrationModule_getTioSafeXMLDiff(html=False), "No diff")
      self.assertEqual(self.oxatis[im].IntegrationModule_getSignatureDiff(), "No diff")

    self.assertEqual(len(self.portal.sale_order_module.contentValues()), 2)
    for sale_order in self.portal.sale_order_module.contentValues():
      self.assertEqual(sale_order.getSimulationState(), 'confirmed')
      test_sale_order = sale_order_dict.get(sale_order.getReference(), None)
      self.assertNotEqual(test_sale_order, None)
      test_sale_order = self.portal.restrictedTraverse(test_sale_order)
      self.assertNotEqual(test_sale_order, None)
      # Check amount
      total_price = float(getattr(test_sale_order, 'SubTotalNet')) - \
                    float(getattr(test_sale_order, 'SubTotalVAT')) + \
                    float(getattr(test_sale_order, 'ShippingPriceTaxExcl'))
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
      if sale_order.getReference() == "666":
        # Nothing must be linked to Unknown
        for line in sale_order.contentValues(portal_type="Sale Order Line"):
          self.assertNotEqual(line.getResource(), self.oxatis.getResource())
        self.assertEqual(sale_order.getSource(), self.oxatis.getSourceAdministration())
        self.assertEqual(sale_order.getSourceSection(), self.oxatis.getSourceAdministration())
        self.assertEqual(sale_order.getSourceDecision(), self.oxatis.getSourceAdministration())
        self.assertEqual(sale_order.getSourceAdministration(), self.oxatis.getSourceAdministration())
        self.assertNotEqual(sale_order.getDestination(), self.oxatis.getDestination())
        self.assertNotEqual(sale_order.getDestinationSection(), self.oxatis.getDestination())
        self.assertNotEqual(sale_order.getDestinationDecision(), self.oxatis.getDestination())
        self.assertNotEqual(sale_order.getDestinationAdministration(), self.oxatis.getDestination())


  @expectedFailure
  def testFullSync(self):
    self.runPersonSync()
    self.runProductSync()
    self.runSaleOrderSync()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestOxatisSynchronization))
  return suite
