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

class testProductPrestashopSynchronization(testPrestashopMixin):
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

  def test_PrestashopSimplestXMLSync(self):
    """ This test checks the product sync with the simplest XML. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    product = self.product_module.newContent(
        portal_type='Product',
        title='Tee-Shirt',
        reference='my_ref',
        use='sale',
    )
    product.validate()
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
    product = self.product_module.newContent(
        portal_type='Product',
        title='Ballon de Foot',
        reference='0123456789',
        ean13_code='1234567890128',
        use='sale',
        sale_supply_line_base_price=2.123456,
        purchase_supply_line_base_price=1.123456,
    )
    product.validate()
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
    product = self.product_module.newContent(
        portal_type='Product',
        title='Ballon de Foot',
        reference='0123456789',
        ean13_code='1234567890128',
        use='sale',
        sale_supply_line_base_price=2.123456,
        purchase_supply_line_base_price=1.123456,
    )
    product.validate()
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
    product = self.product_module.newContent(
        portal_type='Product',
        title='Ballon de Foot',
        reference='0123456789',
        ean13_code='1234567890128',
        use='sale',
        sale_supply_line_base_price=2.123456,
        purchase_supply_line_base_price=1.123456,
    )
    product.validate()
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
    product_1 = self.product_module.newContent(
        portal_type='Product',
        title='Stylo',
        reference='01111',
        use='sale',
        sale_supply_line_base_price=2.1,
        purchase_supply_line_base_price=1.1,
    )
    product_1.validate()
    # create and init the product two
    product_2 = self.product_module.newContent(
        portal_type='Product',
        title='Ballon',
        reference='02222',
        ean13_code='2222222222222',
        use='sale',
        sale_supply_line_base_price=20.2,
        purchase_supply_line_base_price=10.2,
    )
    product_2.validate()
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
    product_3 = self.product_module.newContent(
        portal_type='Product',
        title='Ballon de Foot',
        reference='03333',
        ean13_code='3333333333338',
        use='sale',
        sale_supply_line_base_price=200.3,
        purchase_supply_line_base_price=100.3,
    )
    product_3.validate()
    product_3.setVariationBaseCategoryList(['colour', ])
    product_3.setVariationCategoryList(['colour/black', 'colour/white'])
    # create and init the product four
    product_4 = self.product_module.newContent(
        portal_type='Product',
        title='Ballon de Basket',
        reference='04444',
        ean13_code='4444444444444',
        use='sale',
        sale_supply_line_base_price=2000.4,
        purchase_supply_line_base_price=1000.4,
    )
    product_4.validate()
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
        plugin_xml=self.root_xml % self.prestashop.product_module[13].asXML(),
        tiosafe_xml= self.root_xml % product_1.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.product_module[12].asXML(),
        tiosafe_xml= self.root_xml % product_2.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.product_module[11].asXML(),
        tiosafe_xml= self.root_xml % product_3.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.product_module[10].asXML(),
        tiosafe_xml= self.root_xml % product_4.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )

  def test_PrestashopDeleteProduct(self):
    """ Check that delete during a product's sync invalidate the product. """
    # Initialize the instance and prestashop
    product_module = self.portal.product_module
    self.initPrestashopTest()
    product = self.product_module.newContent(
        portal_type='Product',
        title='Tee-Shirt',
        reference='0123456789',
        use='sale',
    )
    product.validate()
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
    product = self.product_module.newContent(
        portal_type='Product',
        title='Ballon de Foot',
        reference='0123456789',
        ean13_code='1234567890128',
        use='sale',
        sale_supply_line_base_price=2000.4,
        purchase_supply_line_base_price=1000.4,
    )
    product.validate()
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
          'destination_reference':'ball', },
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
    product = self.product_module.newContent(
        portal_type='Product',
        title='Ballon de Plage',
        reference='a5962z',
        use='sale',
        sale_supply_line_base_price=200.25,
        purchase_supply_line_base_price=100.25,
    )
    product.validate()
    product.setVariationBaseCategoryList(['colour'])
    product.setVariationCategoryList(['colour/black', 'colour/white'])
    individual_variation_dict_list = [
        {'variation_base_category': 'ball', 'title': 's4', },
        {'variation_base_category': 'ball', 'title': 's5', },
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
    self.assertEqual(len(self.prestashop.product_module()), 1)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.prestashop.product_module()), 1)
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.product_module()[0].asXML(),
        tiosafe_xml=self.root_xml % product.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )
    # The second update remove variations (individuals and shareds)
    product.setVariationCategoryList(['colour/white', ])
    product.manage_delObjects([individual_variation.getId(), ])
    self.assertEqual(len(self.prestashop.product_module()), 1)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.prestashop.product_module()), 1)
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
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.product_module()[0].asXML(),
        tiosafe_xml=self.root_xml % product.Resource_asTioSafeXML(),
        xsd_path='../XSD/resources.xsd',
    )

