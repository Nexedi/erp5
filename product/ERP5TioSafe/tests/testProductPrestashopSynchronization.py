##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#               Hervé Poulain <herve@nexedi.com>
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

import transaction
from Products.ERP5TioSafe.tests.testPrestashopMixin import testPrestashopMixin

class TestProductPrestashopSynchronization(testPrestashopMixin):
  """ This class allows to check different cases of Product's sync. """

  def afterSetUp(self):
    """ This method is called after the SetUp method. """
    # Shortcut for modules and tools
    self.product_module = self.portal.product_module
    self.portal_categories = self.portal.portal_categories
    self.portal_sync = self.portal.portal_synchronizations
    self.connection = self.portal.erp5_sql_connection
    self.prestashop = self.portal.portal_integrations.prestashop
    self.root_xml = '<catalog>\n%s\n</catalog>'
    self.sale_supply = self.portal.sale_supply_module.newContent(title=self.prestashop.getTitle())
    self.sale_supply.validate()
    transaction.commit()
    self.tic()

  def beforeTearDown(self):
    testPrestashopMixin.beforeTearDown(self)
    self.sale_supply.invalidate()
    transaction.commit()
    self.tic()

  def createProduct(self, **kw):
    """
    Create product & add it to the sale supply
    """
    product = self.product_module.newContent(**kw)
    product.validate()
    self.sale_supply.newContent(resource=product.getRelativeUrl())
    return product

  def test_PrestashopSimplestXMLSync(self):
    """ This test checks the product sync with the simplest XML. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    product = self.createProduct(
        portal_type='Product',
        title='Tee-Shirt',
        reference='my_ref',
        use='sale',
    )
    
    transaction.commit()
    self.tic()

    # Run the sync of products and check product's data after sync
    self.assertEqual(len(self.prestashop.product_module()), 0)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.prestashop.product_module()), 1)
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.product_module()[0].asXML(),
        tiosafe_xml=self.root_xml % product.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )

  def test_PrestashopIndividualVariationSync(self):
    """ This test check the product sync with individual variations. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.loadSQLDump(
        self.connection,
        '%s/dump_product_sync_12.sql' % self.ps_dump_path,
    )
    # Define the specific mapping, initMapping declare the categories in ERP5
    self.initMapping()
    mapping_dict_list = [
        { 'title': 'Taille du Ballon',
          'path': 'TailleduBallon',
          'source_reference': 'Taille du Ballon',
          'destination_reference':'ball_size', },
        { 'title': 'Couleur',
          'path': 'Couleur',
          'source_reference': 'Couleur',
          'destination_reference': 'colour', },
    ]
    for mapping in mapping_dict_list:
      self.createMapping(integration_site=self.prestashop, **mapping)
    # create and init the product
    product = self.createProduct(
        portal_type='Product',
        title='Ballon de Foot',
        reference='0123456789',
        ean13_code='1234567890128',
        use='sale',
        sale_supply_line_base_price=2.123456,
        purchase_supply_line_base_price=1.123456,
    )
    
    individual_variation_dict_list = [
        {'variation_base_category': 'ball_size', 'title': 's4', },
        {'variation_base_category': 'ball_size', 'title': 's5', },
        {'variation_base_category': 'colour', 'title': 'Blanc', },
        {'variation_base_category': 'colour', 'title': 'Noir', },
    ]
    for individual_variation in individual_variation_dict_list:
      product.newContent(
          portal_type='Product Individual Variation',
          **individual_variation
      )
    transaction.commit()
    self.tic()

    # Run the sync of products and check product's data after sync
    self.assertEqual(len(self.prestashop.product_module()), 0)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.prestashop.product_module()), 1)
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.product_module()[0].asXML(),
        tiosafe_xml=self.root_xml % product.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )

  def test_PrestashopSharedVariationSync(self):
    """ This test check the product sync with shared variations. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.loadSQLDump(
        self.connection,
        '%s/dump_product_sync_12.sql' % self.ps_dump_path,
    )
    self.initMapping(self.prestashop)
    # create and init the product
    product = self.createProduct(
        portal_type='Product',
        title='Ballon de Foot',
        reference='0123456789',
        ean13_code='1234567890128',
        use='sale',
        sale_supply_line_base_price=2.123456,
        purchase_supply_line_base_price=1.123456,
    )
    
    product.setVariationBaseCategoryList(['ball_size', 'colour'])
    product.setVariationCategoryList(
        ['ball_size/x4', 'ball_size/x5', 'colour/black', 'colour/white'],
    )
    transaction.commit()
    self.tic()

    # Run the sync of products and check product's data after sync
    self.assertEqual(len(self.prestashop.product_module()), 0)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.prestashop.product_module()), 1)
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.product_module()[0].asXML(),
        tiosafe_xml=self.root_xml % product.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )

  def test_PrestashopDifferentKindVariationsSync(self):
    """ This test check the product sync with the two kind of variations. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.loadSQLDump(
        self.connection,
        '%s/dump_product_sync_12.sql' % self.ps_dump_path,
    )
    # Define the specific mapping, initMapping declare the categories in ERP5
    self.initMapping()
    mapping_dict_list = [
        { 'title': 'Taille du Ballon',
          'path': 'TailleduBallon',
          'source_reference': 'Taille du Ballon',
          'destination_reference':'ball_size', },
        { 'title': 'Couleur',
          'path': 'Couleur',
          'source_reference': 'Couleur',
          'destination_reference': 'colour', },
        { 'title': 'Blanc',
          'path': 'Couleur/Blanc',
          'source_reference': 'Blanc',
          'destination_reference': 'white', },
        { 'title': 'Noir',
          'path': 'Couleur/Noir',
          'source_reference': 'Noir',
          'destination_reference': 'black', },
    ]
    for mapping in mapping_dict_list:
      self.createMapping(integration_site=self.prestashop, **mapping)
    # create and init the product
    product = self.createProduct(
        portal_type='Product',
        title='Ballon de Foot',
        reference='0123456789',
        ean13_code='1234567890128',
        use='sale',
        sale_supply_line_base_price=2.123456,
        purchase_supply_line_base_price=1.123456,
    )
    
    product.setVariationBaseCategoryList(['colour'])
    product.setVariationCategoryList(['colour/black', 'colour/white'])
    individual_variation_dict_list = [
        {'variation_base_category': 'ball_size', 'title': 's4', },
        {'variation_base_category': 'ball_size', 'title': 's5', },
    ]
    for individual_variation in individual_variation_dict_list:
      product.newContent(
          portal_type='Product Individual Variation',
          **individual_variation
      )
    transaction.commit()
    self.tic()

    # Run the sync of products and check product's data after sync
    self.assertEqual(len(self.prestashop.product_module()), 0)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.prestashop.product_module()), 1)
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.product_module()[0].asXML(),
        tiosafe_xml=self.root_xml % product.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )

  def test_PrestashopMultipleSync(self):
    """ This test check the multiple product sync. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.loadSQLDump(
        self.connection,
        '%s/dump_product_sync_12.sql' % self.ps_dump_path,
    )
    # Define the specific mapping, initMapping declare the categories in ERP5
    self.initMapping()
    mapping_dict_list = [
        { 'title': 'Taille du Ballon',
          'path': 'TailleduBallon',
          'source_reference': 'Taille du Ballon',
          'destination_reference':'ball_size', },
        { 'title': 'Couleur',
          'path': 'Couleur',
          'source_reference': 'Couleur',
          'destination_reference': 'colour', },
        { 'title': 'Blanc',
          'path': 'Couleur/Blanc',
          'source_reference': 'Blanc',
          'destination_reference': 'white', },
        { 'title': 'Noir',
          'path': 'Couleur/Noir',
          'source_reference': 'Noir',
          'destination_reference': 'black', },
    ]
    for mapping in mapping_dict_list:
      self.createMapping(integration_site=self.prestashop, **mapping)
    # create and init the product one
    product_1 = self.createProduct(
        portal_type='Product',
        title='Stylo',
        reference='01111',
        use='sale',
        sale_supply_line_base_price=2.1,
        purchase_supply_line_base_price=1.1,
    )
    # create and init the product two
    product_2 = self.createProduct(
        portal_type='Product',
        title='Ballon',
        reference='02222',
        ean13_code='2222222222222',
        use='sale',
        sale_supply_line_base_price=20.2,
        purchase_supply_line_base_price=10.2,
    )
    individual_variation_dict_list = [
        {'variation_base_category': 'ball_size', 'title': 's4', },
        {'variation_base_category': 'ball_size', 'title': 's5', },
    ]
    for individual_variation in individual_variation_dict_list:
      product_2.newContent(
          portal_type='Product Individual Variation',
          **individual_variation
      )
    # create and init the product three
    product_3 = self.createProduct(
        portal_type='Product',
        title='Ballon de Foot',
        reference='03333',
        ean13_code='3333333333338',
        use='sale',
        sale_supply_line_base_price=200.3,
        purchase_supply_line_base_price=100.3,
    )
    product_3.setVariationBaseCategoryList(['colour', ])
    product_3.setVariationCategoryList(['colour/black', 'colour/white'])
    # create and init the product four
    product_4 = self.createProduct(
        portal_type='Product',
        title='Ballon de Basket',
        reference='04444',
        ean13_code='4444444444444',
        use='sale',
        sale_supply_line_base_price=2000.4,
        purchase_supply_line_base_price=1000.4,
    )
    product_4.setVariationBaseCategoryList(['colour'])
    product_4.setVariationCategoryList(['colour/black', 'colour/white'])
    individual_variation_dict_list = [
        {'variation_base_category': 'ball_size', 'title': 's4', },
        {'variation_base_category': 'ball_size', 'title': 's5', },
    ]
    for individual_variation in individual_variation_dict_list:
      product_4.newContent(
          portal_type='Product Individual Variation',
          **individual_variation
      )
    transaction.commit()
    self.tic()

    # Run the sync of products and check product's data after sync
    self.assertEqual(len(self.prestashop.product_module()), 0)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.prestashop.product_module()), 4)
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.product_module[10].asXML(),
        tiosafe_xml= self.root_xml % product_1.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.product_module[11].asXML(),
        tiosafe_xml= self.root_xml % product_2.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.product_module[12].asXML(),
        tiosafe_xml= self.root_xml % product_3.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.product_module[13].asXML(),
        tiosafe_xml= self.root_xml % product_4.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )

  def test_PrestashopDeleteProduct(self):
    """ Check that delete during a product's sync invalidate the product. """
    # Initialize the instance and prestashop
    product_module = self.portal.product_module
    self.initPrestashopTest()
    product = self.createProduct(
        portal_type='Product',
        title='Tee-Shirt',
        reference='0123456789',
        use='sale',
    )
    
    transaction.commit()
    self.tic()

    # Run the sync of products and check product's data after sync
    self.assertEqual(len(self.prestashop.product_module()), 0)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.prestashop.product_module()), 1)
    # Remove the product in ERP5 and check that after sync in prestashop
    self.product_module.manage_delObjects([product.getId(), ])
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.prestashop.product_module()), 0)

  def test_PrestashopUpdateSimpleElement(self):
    """ This test checks the simple update after sync of products. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.loadSQLDump(
        self.connection,
        '%s/dump_product_sync_12.sql' % self.ps_dump_path,
    )
    self.initMapping(self.prestashop)
    # create and init the product
    product = self.createProduct(
        portal_type='Product',
        title='Ballon de Foot',
        reference='0123456789',
        ean13_code='1234567890128',
        use='sale',
        sale_supply_line_base_price=2000.4,
        purchase_supply_line_base_price=1000.4,
    )
    
    product.setVariationBaseCategoryList(['ball_size', 'colour'])
    product.setVariationCategoryList(
        ['ball_size/x4', 'ball_size/x5', 'colour/black', 'colour/white'],
    )
    transaction.commit()
    self.tic()

    # Run the sync of products and check product's data after sync
    self.assertEqual(len(self.prestashop.product_module()), 0)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.prestashop.product_module()), 1)
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.product_module()[0].asXML(),
        tiosafe_xml=self.root_xml % product.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )
    # Update the data, run the sync and check the data after the update
    product.setSaleSupplyLineBasePrice(20.0)
    product.setPurchaseSupplyLineBasePrice(20.0)
    product.setEan13Code('0987654321098')
    self.assertEqual(len(self.prestashop.product_module()), 1)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.prestashop.product_module()), 1)
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.product_module()[0].asXML(),
        tiosafe_xml=self.root_xml % product.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )

  def updateSystemPreference(self, portal, base_category, individual=False):
    pref_list = portal.portal_preferences.searchFolder(portal_type="System Preference",
                                                       validation_state="enabled")
    if len(pref_list) > 1:
      raise ValueError, "Too many system preferences, does not know which to choose"
    elif len(pref_list) == 0:
      pref = portal.portal_preferences.newContent(portal_type="System Preference",
                                           title="default system preference for TioSafe",
                                           priority=1)
      pref.enable()
    else:
      pref = pref_list[0].getObject()
    self.system_pref = pref

    if individual:
      cat_list = self.system_pref.getPreferredProductIndividualVariationBaseCategoryList()
      if base_category not in cat_list:
        cat_list.append(base_category)
        self.system_pref.edit(preferred_product_individual_variation_base_category_list = cat_list)
    else:
      cat_list = self.system_pref.getPreferredProductVariationBaseCategoryList()
      if base_category not in cat_list:
        cat_list.append(base_category)
        self.system_pref.edit(preferred_product_variation_base_category_list = cat_list)

  def checkConflicts(self, module, nb_pub_conflicts=0, nb_sub_conflicts=0, in_conflict=True):
    module = self.prestashop[module]
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


  def test_PrestashopComplexeUpdateElement(self):
    """
      This test checks the complexe update after sync of products.
      It updates some element, adds others and removes the last.
    """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.loadSQLDump(
        self.connection,
        '%s/dump_product_sync_12.sql' % self.ps_dump_path,
    )
    # Define the specific mapping, initMapping declare the categories in ERP5
    self.initMapping()
    mapping_dict_list = [
        { 'title': 'Taille du Ballon',
          'path': 'TailleduBallon',
          'source_reference': 'Taille du Ballon',
          'destination_reference':'ball_size', },
        { 'title': 'Couleur',
          'path': 'Couleur',
          'source_reference': 'Couleur',
          'destination_reference': 'colour', },
        { 'title': 'Blanc',
          'path': 'Couleur/Blanc',
          'source_reference': 'Blanc',
          'destination_reference': 'white', },
        { 'title': 'Noir',
          'path': 'Couleur/Noir',
          'source_reference': 'Noir',
          'destination_reference': 'black', },
        { 'title': 'Rouge',
          'path': 'Couleur/Rouge',
          'source_reference': 'Rouge',
          'destination_reference': 'red', },
    ]
    for mapping in mapping_dict_list:
      self.createMapping(integration_site=self.prestashop, **mapping)
    # create and init the product
    product = self.createProduct(
        portal_type='Product',
        title='Ballon de Plage',
        reference='a5962z',
        use='sale',
        sale_supply_line_base_price=200.25,
        purchase_supply_line_base_price=100.25,
    )
    self.updateSystemPreference(self.getPortalObject(), 'colour')
    self.updateSystemPreference(self.getPortalObject(), 'ball_size', True)
    product.setVariationBaseCategoryList(['colour'])
    product.setVariationCategoryList(['colour/black', 'colour/white'])
    individual_variation_dict_list = [
      {'variation_base_category': 'ball_size', 'title': 's4', },
      {'variation_base_category': 'ball_size', 'title': 's5', },
      ]
    product.setIndividualVariationBaseCategoryList(['ball_size'])
    for individual_variation in individual_variation_dict_list:
      product.newContent(
          portal_type='Product Individual Variation',
          **individual_variation
      )
    transaction.commit()
    self.tic()

    # Run the sync of products and check product's data after sync
    self.assertEqual(len(self.prestashop.product_module()), 0)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.prestashop.product_module()), 1)
    self.checkConflicts('product_module')
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.product_module()[0].asXML(),
        tiosafe_xml=self.root_xml % product.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )
    # The first update remove, add and update some elements but not realise an
    # hard work on variations
    product.setEan13Code('1357913579130')
    product.setVariationCategoryList(['colour/white', 'colour/red'])
    individual_variation = product.portal_catalog(
        portal_type='Product Individual Variation',
        parent_uid=product.getUid(),
        title='s5',
    )[0].getObject()
    individual_variation.setTitle('s6')
    transaction.commit()
    self.tic()
    self.assertEqual(len(self.prestashop.product_module()), 1)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.prestashop.product_module()), 1)
    self.checkConflicts('product_module')
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.product_module()[0].asXML(),
        tiosafe_xml=self.root_xml % product.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )
    # The second update remove variations (individuals and shareds)
    product.setVariationCategoryList(['colour/white', ])
    product.manage_delObjects([individual_variation.getId(), ])
    transaction.commit()
    self.tic()
    self.assertEqual(len(self.prestashop.product_module()), 1)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.prestashop.product_module()), 1)
    self.checkConflicts('product_module')
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.product_module()[0].asXML(),
        tiosafe_xml=self.root_xml % product.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )
    # The third update allows to add variations (individuals and shareds)
    product.setVariationCategoryList(
        ['colour/white', 'colour/red', 'colour/white'],
    )
    individual_variation_dict_list = [
        {'variation_base_category': 'ball', 'title': 's5', },
        {'variation_base_category': 'ball', 'title': 's6', },
    ]
    for individual_variation in individual_variation_dict_list:
      product.newContent(
          portal_type='Product Individual Variation',
          **individual_variation
      )
    self.assertEqual(len(self.prestashop.product_module()), 1)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.prestashop.product_module()), 1)
    self.checkConflicts('product_module')
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.product_module()[0].asXML(),
        tiosafe_xml=self.root_xml % product.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestProductPrestashopSynchronization))
  return suite
