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

class TestProductERP5Synchronization(testPrestashopMixin):
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
    self.not_removable_id_list = [self.prestashop.getSourceAdministrationValue().getId(),
                                  self.prestashop.getResourceValue().getId(),
                                  self.prestashop.getDestinationValue().getId()]

  def test_PrestashopSimplestXMLSync(self):
    """ This test checks the product sync with the simplest XML. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.loadSQLDump(
        self.connection,
        '%s/dump_product_sync_01.sql' % self.ps_dump_path,
    )
    transaction.commit()
    self.tic()

    # Run the sync of products and check product's data after sync
    self.assertEqual(len(self.product_module.contentValues()), 1)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.product_module.contentValues()), 2)
    product = self.product_module.contentValues()[0]
    self.assertEqual(product.getTitle(), 'Tee-Shirt')
    self.assertEqual(product.getReference(), 'my_ref')
    self.assertEqual(product.getUse(), 'sale')
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml= self.root_xml % product.Resource_asTioSafeXML(),
        tiosafe_xml=self.root_xml % self.prestashop.product_module()[0].asXML(),
        xsd_path='../XSD/resources.xsd',
    )

  def test_PrestashopIndividualVariationSync(self):
    """ This test check the product sync with individual variations. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.loadSQLDump(
        self.connection,
        '%s/dump_product_sync_02.sql' % self.ps_dump_path,
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
    transaction.commit()
    self.tic()

    # Run the sync of products and check product's data after sync
    self.assertEqual(len(self.product_module.contentValues()), 1)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.product_module.contentValues()), 2)
    product = self.product_module.contentValues()[0]
    self.assertEqual(product.getTitle(), 'Ballon de Foot')
    self.assertEqual(product.getReference(), '0123456789')
    self.assertEqual(product.getEan13Code(), '1234567890128')
    self.assertEqual(product.getUse(), 'sale')
    # Check the individual variations
    # FIXME: When no mapping is created between ERP5 and Prestashop, the full
    # variation is created as individual variation, ie:
    # Ball Size/s4 and Ball Size/s5 will be an individual variations,
    individual_variation_list = product.searchFolder(
        portal_type='Product Individual Variation',
        sort_on=(['id', 'ASC'], ),
    )
    self.assertEqual(len(individual_variation_list), 4)
    for individual_variation in individual_variation_list:
      # Use shortcut for the checking
      individual_variation = individual_variation.getObject()
      title = individual_variation.getTitle()
      base_category_list = individual_variation.getVariationBaseCategoryList()
      index = individual_variation.getId()
      # check through the order
      if index == '1':
        self.assertEqual(title, 's4')
        self.assertEqual(base_category_list, ['ball_size', ])
      elif index == '2':
        self.assertEqual(title, 's5')
        self.assertEqual(base_category_list, ['ball_size', ])
      elif index == '3':
        self.assertEqual(title, 'Blanc')
        self.assertEqual(base_category_list, ['colour', ])
      elif index == '4':
        self.assertEqual(title, 'Noir')
        self.assertEqual(base_category_list, ['colour', ])
      else:
        raise ValueError, 'Can not check variation: %s of the product: %s' % \
            (index, product.getTitle())
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml= self.root_xml % product.Resource_asTioSafeXML(),
        tiosafe_xml=self.root_xml % self.prestashop.product_module()[0].asXML(),
        xsd_path='../XSD/resources.xsd',
    )

  def test_PrestashopSharedVariationSync(self):
    """ This test check the product sync with shared variations. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.loadSQLDump(
        self.connection,
        '%s/dump_product_sync_02.sql' % self.ps_dump_path,
    )
    self.initMapping(self.prestashop)
    transaction.commit()
    self.tic()

    # Run the sync of products and check product's data after sync
    self.assertEqual(len(self.product_module.contentValues()), 1)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.product_module.contentValues()), 2)
    product = self.product_module.contentValues()[0]
    self.assertEqual(product.getTitle(), 'Ballon de Foot')
    self.assertEqual(product.getReference(), '0123456789')
    self.assertEqual(product.getEan13Code(), '1234567890128')
    self.assertEqual(product.getUse(), 'sale')
    # Check the shared variations
    self.assertEqual(
        product.contentValues(portal_type='Product Individual Variation'),
        [],
    )
    sorted_shared_category_list = product.getVariationCategoryList()
    sorted_shared_category_list.sort()
    self.assertEqual(len(sorted_shared_category_list), 4)
    for i, variation in enumerate(sorted_shared_category_list):
      if i == 0:
        self.assertEqual(variation, 'ball_size/x4')
      elif i == 1:
        self.assertEqual(variation, 'ball_size/x5')
      elif i == 2:
        self.assertEqual(variation, 'colour/black')
      elif i == 3:
        self.assertEqual(variation, 'colour/white')
      else:
        raise ValueError, 'Can not check variation: %s of the product: %s' % \
            (variation, product.getTitle())
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml= self.root_xml % product.Resource_asTioSafeXML(),
        tiosafe_xml=self.root_xml % self.prestashop.product_module()[0].asXML(),
        xsd_path='../XSD/resources.xsd',
    )

  def test_PrestashopDifferentKindVariationsSync(self):
    """ This test check the product sync with the two kind of variations. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.loadSQLDump(
        self.connection,
        '%s/dump_product_sync_02.sql' % self.ps_dump_path,
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
    transaction.commit()
    self.tic()

    # Run the sync of products and check product's data after sync
    self.assertEqual(len(self.product_module.contentValues()), 1)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.product_module.contentValues()), 2)
    product = self.product_module.contentValues()[0]
    self.assertEqual(product.getTitle(), 'Ballon de Foot')
    self.assertEqual(product.getReference(), '0123456789')
    self.assertEqual(product.getEan13Code(), '1234567890128')
    self.assertEqual(product.getUse(), 'sale')
    # Check the shared variations
    sorted_shared_category_list = product.getVariationCategoryList()
    sorted_shared_category_list.sort()
    self.assertEqual(len(sorted_shared_category_list), 2)
    for i, variation in enumerate(sorted_shared_category_list):
      if i == 0:
        self.assertEqual(variation, 'colour/black')
      elif i == 1:
        self.assertEqual(variation, 'colour/white')
      else:
        raise ValueError, 'Can not check variation: %s of the product: %s' % \
            (variation, product.getTitle())
    individual_variation_list = product.searchFolder(
        portal_type='Product Individual Variation',
        sort_on=(['id', 'ASC'], ),
    )
    self.assertEqual(len(individual_variation_list), 2)
    for individual_variation in individual_variation_list:
      # Use shortcut for the checking
      individual_variation = individual_variation.getObject()
      title = individual_variation.getTitle()
      base_category_list = individual_variation.getVariationBaseCategoryList()
      index = individual_variation.getId()
      # check through the order
      if index == '1':
        self.assertEqual(title, 's4')
        self.assertEqual(base_category_list, ['ball_size'])
      elif index == '2':
        self.assertEqual(title, 's5')
        self.assertEqual(base_category_list, ['ball_size'])
      else:
        raise ValueError, 'Can not check variation: %s of the product: %s' % \
            (index, product.getTitle())
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml= self.root_xml % product.Resource_asTioSafeXML(),
        tiosafe_xml=self.root_xml % self.prestashop.product_module()[0].asXML(),
        xsd_path='../XSD/resources.xsd',
    )

  def test_PrestashopMultipleSync(self):
    """ This test check the multiple product sync. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.loadSQLDump(
        self.connection,
        '%s/dump_product_sync_03.sql' % self.ps_dump_path,
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
    transaction.commit()
    self.tic()

    # Run the sync of products and check product's data after sync
    self.assertEqual(len(self.product_module.contentValues()), 1)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.product_module.contentValues()), 5)
    # Check the product 'Stylo'
    product_1 = self.product_module.searchFolder(
        portal_type='Product',
        title='Stylo',
    )[0].getObject()
    self.assertEqual(product_1.getTitle(), 'Stylo')
    self.assertEqual(product_1.getReference(), '01111')
    self.assertEqual(product_1.getUse(), 'sale')
    # Check the product 'Ballon'
    product_2 = self.product_module.searchFolder(
        portal_type='Product',
        title='Ballon',
    )[0].getObject()
    self.assertEqual(product_2.getTitle(), 'Ballon')
    self.assertEqual(product_2.getReference(), '02222')
    self.assertEqual(product_2.getEan13Code(), '2222222222222')
    self.assertEqual(product_2.getUse(), 'sale')
    self.assertEqual(product_2.getVariationCategoryList(), [])
    individual_variation_list = product_2.searchFolder(
        portal_type='Product Individual Variation',
        sort_on=(['id', 'ASC'], ),
    )
    for individual_variation in individual_variation_list:
      # Use shortcut for the checking
      individual_variation = individual_variation.getObject()
      title = individual_variation.getTitle()
      base_category_list = individual_variation.getVariationBaseCategoryList()
      index = individual_variation.getId()
      # check through the order
      if index == '1':
        self.assertEqual(title, 's4')
        self.assertEqual(base_category_list, ['ball_size'])
      elif index == '2':
        self.assertEqual(title, 's5')
        self.assertEqual(base_category_list, ['ball_size'])
      else:
        raise ValueError, 'Can not check variation: %s of the product: %s' % \
            (index, product_2.getTitle())
    # Check the product 'Ballon de foot'
    product_3 = self.product_module.searchFolder(
        portal_type='Product',
        title='Ballon de Foot',
    )[0].getObject()
    self.assertEqual(product_3.getTitle(), 'Ballon de Foot')
    self.assertEqual(product_3.getReference(), '03333')
    self.assertEqual(product_3.getEan13Code(), '3333333333338')
    self.assertEqual(product_3.getUse(), 'sale')
    self.assertEqual(
        product_3.contentValues(portal_type='Product Individual Variation'),
        [],
    )
    sorted_shared_category_list = product_3.getVariationCategoryList()
    sorted_shared_category_list.sort()
    self.assertEqual(len(sorted_shared_category_list), 2)
    for i, variation in enumerate(sorted_shared_category_list):
      if i == 0:
        self.assertEqual(variation, 'colour/black')
      elif i == 1:
        self.assertEqual(variation, 'colour/white')
      else:
        raise ValueError, 'Can not check variation: %s of the product: %s' % \
            (variation, product_3.getTitle())
    # Check the product 'Ballon de Basket'
    product_4 = self.product_module.searchFolder(
        portal_type='Product',
        title='Ballon de Basket',
    )[0].getObject()
    self.assertEqual(product_4.getTitle(), 'Ballon de Basket')
    self.assertEqual(product_4.getReference(), '04444')
    self.assertEqual(product_4.getEan13Code(), '4444444444444')
    self.assertEqual(product_4.getUse(), 'sale')
    shared_variation_list = product_4.getVariationCategoryList()
    shared_variation_list.sort()
    self.assertEqual(len(shared_variation_list), 2)
    for i, variation in enumerate(shared_variation_list):
      if i == 0:
        self.assertEqual(variation, 'colour/black')
      elif i == 1:
        self.assertEqual(variation, 'colour/white')
      else:
        raise ValueError, 'Can not check variation: %s of the product: %s' % \
            (variation, product_4.getTitle())
    individual_variation_list = product_4.searchFolder(
        portal_type='Product Individual Variation',
        sort_on=(['id', 'ASC'], ),
    )
    self.assertEqual(len(individual_variation_list), 2)
    for individual_variation in individual_variation_list:
      # Use shortcut for the checking
      individual_variation = individual_variation.getObject()
      title = individual_variation.getTitle()
      base_category_list = individual_variation.getVariationBaseCategoryList()
      index = individual_variation.getId()
      # check through the order
      if index == '1':
        self.assertEqual(title, 's4')
        self.assertEqual(base_category_list, ['ball_size'])
      elif index == '2':
        self.assertEqual(title, 's5')
        self.assertEqual(base_category_list, ['ball_size'])
      else:
        raise ValueError, 'Can not check variation: %s of the product: %s' % \
            (index, product_4.getTitle())
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml= self.root_xml % product_1.Resource_asTioSafeXML(),
        tiosafe_xml=self.root_xml % self.prestashop.product_module[1].asXML(),
        xsd_path='../XSD/resources.xsd',
    )
    self.checkTioSafeXML(
        plugin_xml= self.root_xml % product_2.Resource_asTioSafeXML(),
        tiosafe_xml=self.root_xml % self.prestashop.product_module[2].asXML(),
        xsd_path='../XSD/resources.xsd',
    )
    self.checkTioSafeXML(
        plugin_xml= self.root_xml % product_3.Resource_asTioSafeXML(),
        tiosafe_xml=self.root_xml % self.prestashop.product_module[3].asXML(),
        xsd_path='../XSD/resources.xsd',
    )
    self.checkTioSafeXML(
        plugin_xml= self.root_xml % product_4.Resource_asTioSafeXML(),
        tiosafe_xml=self.root_xml % self.prestashop.product_module[4].asXML(),
        xsd_path='../XSD/resources.xsd',
    )

  def test_PrestashopDeleteProduct(self):
    """ Check that delete during a product's sync invalidate the product. """
    # Initialize the instance and prestashop
    product_module = self.portal.product_module
    self.initPrestashopTest()
    self.loadSQLDump(
        self.connection,
        '%s/dump_product_sync_04.sql' % self.ps_dump_path,
    )
    transaction.commit()
    self.tic()

    # Run the sync of products
    self.assertEqual(len(self.product_module.contentValues()), 1)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.product_module.contentValues()), 4)
    # Move the products as validated and invalidated state
    tee_shirt = product_module.searchFolder(
        portal_type='Product',
        title='Tee-Shirt',
    )[0].getObject()
    short = product_module.searchFolder(
        portal_type='Product',
        title='Short',
    )[0].getObject()
    pull_over = product_module.searchFolder(
        portal_type='Product',
        title='Pull-Over',
    )[0].getObject()
    pull_over.invalidate()
    # Remove the products in prestashop and check that after sync the states
    self.loadSQLDump(
        self.connection,
        '%s/dump_product_sync_05.sql' % self.ps_dump_path,
    )
    self.assertEqual(tee_shirt.getValidationState(), 'validated')
    self.assertEqual(short.getValidationState(), 'validated')
    self.assertEqual(pull_over.getValidationState(), 'invalidated')
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.product_module.contentValues()), 4)
    self.assertEqual(tee_shirt.getValidationState(), 'invalidated')
    self.assertEqual(short.getValidationState(), 'invalidated')
    self.assertEqual(pull_over.getValidationState(), 'invalidated')

  def test_PrestashopUpdateSimpleElement(self):
    """ This test checks the simple update after sync of products. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.loadSQLDump(
        self.connection,
        '%s/dump_product_sync_06.sql' % self.ps_dump_path,
    )
    self.initMapping(self.prestashop)
    transaction.commit()
    self.tic()

    # Run the sync of persons and check person's data after sync
    self.assertEqual(len(self.product_module.contentValues()), 1)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.product_module.contentValues()), 2)
    product = self.product_module.contentValues()[0]
    self.assertEqual(product.getTitle(), 'Ballon de Basket')
    self.assertEqual(product.getReference(), 'b246b')
    self.assertEqual(product.getEan13Code(), '1234567890128')
    self.assertEqual(product.getUse(), 'sale')
    base_category_list = product.getVariationBaseCategoryList()
    base_category_list.sort()
    self.assertEqual(len(base_category_list), 2)
    self.assertEqual(base_category_list, ['ball_size', 'colour'])
    variation_category_list = product.getVariationCategoryList()
    variation_category_list.sort()
    self.assertEqual(len(variation_category_list), 4)
    self.assertEqual(
        variation_category_list,
        ['ball_size/x4', 'ball_size/x5', 'colour/black', 'colour/white'],
    )
    # Update the data, run the sync and check the data after the update
    self.loadSQLDump(
        self.connection,
        '%s/dump_product_sync_07.sql' % self.ps_dump_path,
    )
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.product_module.contentValues()), 2)
    self.assertEqual(product.getTitle(), 'Ballon de Basket')
    self.assertEqual(product.getReference(), 'b246b')
    self.assertEqual(product.getEan13Code(), '0987654321098')
    self.assertEqual(product.getUse(), 'sale')
    base_category_list = product.getVariationBaseCategoryList()
    base_category_list.sort()
    self.assertEqual(len(base_category_list), 2)
    self.assertEqual(base_category_list, ['ball_size', 'colour'])
    variation_category_list = product.getVariationCategoryList()
    variation_category_list.sort()
    self.assertEqual(len(variation_category_list), 4)
    self.assertEqual(
        variation_category_list,
        ['ball_size/x4', 'ball_size/x5', 'colour/black', 'colour/white'],
    )
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml= self.root_xml % product.Resource_asTioSafeXML(),
        tiosafe_xml=self.root_xml % self.prestashop.product_module()[0].asXML(),
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
        '%s/dump_product_sync_08.sql' % self.ps_dump_path,
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
    transaction.commit()
    self.tic()

    # Run the sync of persons and check person's data after sync
    self.assertEqual(len(self.product_module.contentValues()), 1)
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.product_module.contentValues()), 2)
    product = self.product_module.contentValues()[0]
    self.assertEqual(product.getTitle(), 'Ballon de Plage')
    self.assertEqual(product.getReference(), 'a5962z')
    self.assertEqual(product.getEan13Code(), None)
    self.assertEqual(product.getUse(), 'sale')
    base_category_list = product.getVariationBaseCategoryList(omit_individual_variation=True)
    self.assertEqual(len(base_category_list), 1)
    self.assertEqual(base_category_list, ['colour'])
    shared_variation_list = product.getVariationCategoryList()
    shared_variation_list.sort()
    self.assertEqual(len(shared_variation_list), 2)
    self.assertEqual(
        shared_variation_list,
        ['colour/black', 'colour/white'],
    )
    individual_base_category_list = product.getIndividualVariationBaseCategoryList()
    self.assertEqual(len(individual_base_category_list), 1)
    self.assertEqual(individual_base_category_list, ['ball_size'])
    individual_variation_list = product.searchFolder(
        portal_type='Product Individual Variation',
        sort_on=(['id', 'ASC'], ),
    )
    self.assertEqual(len(individual_variation_list), 2)
    for individual_variation in individual_variation_list:
      # Use shortcut for the checking
      individual_variation = individual_variation.getObject()
      title = individual_variation.getTitle()
      base_category_list = individual_variation.getVariationBaseCategoryList()
      index = individual_variation.getId()
      # check through the order
      if index == '1':
        self.assertEqual(title, 's4')
        self.assertEqual(base_category_list, ['ball_size'])
      elif index == '2':
        self.assertEqual(title, 's5')
        self.assertEqual(base_category_list, ['ball_size'])
      else:
        raise ValueError, 'Can not check variation: %s of the product: %s' % \
            (individual_variation.getId(), product.getTitle())
    # The first update remove, add and update some elements but not realise an
    # hard work on variations
    self.loadSQLDump(
        self.connection,
        '%s/dump_product_sync_09.sql' % self.ps_dump_path,
    )
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.product_module.contentValues()), 2)
    self.assertEqual(product.getTitle(), 'Ballon de Plage')
    self.assertEqual(product.getReference(), 'a5962z')
    self.assertEqual(product.getEan13Code(), '1357913579130')
    self.assertEqual(product.getUse(), 'sale')
    base_category_list = product.getVariationBaseCategoryList()
    base_category_list.sort()
    self.assertEqual(len(base_category_list), 2)
    self.assertEqual(base_category_list, ['ball_size', 'colour'])
    shared_variation_list = product.getVariationCategoryList()
    shared_variation_list.sort()
    self.assertEqual(len(shared_variation_list), 2)
    self.assertEqual(
        shared_variation_list,
        ['colour/red', 'colour/white'],
    )
    individual_variation_list = product.searchFolder(
        portal_type='Product Individual Variation',
        sort_on=(['id', 'ASC'], ),
    )
    self.assertEqual(len(individual_variation_list), 2)
    for individual_variation in individual_variation_list:
      # Use shortcut for the checking
      individual_variation = individual_variation.getObject()
      title = individual_variation.getTitle()
      base_category_list = individual_variation.getVariationBaseCategoryList()
      index = individual_variation.getId()
      # check through the order
      if index == '1':
        self.assertEqual(title, 's4')
        self.assertEqual(base_category_list, ['ball_size'])
      elif index == '2':
        self.assertEqual(title, 's6')
        self.assertEqual(base_category_list, ['ball_size'])
      else:
        raise ValueError, 'Can not check variation: %s of the product: %s' % \
            (index, product.getTitle())
    # The second update remove variations (individuals and shareds)
    self.loadSQLDump(
        self.connection,
        '%s/dump_product_sync_10.sql' % self.ps_dump_path,
    )
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.product_module.contentValues()), 2)
    base_category_list = product.getVariationBaseCategoryList()
    base_category_list.sort()
    self.assertEqual(len(base_category_list), 2)
    self.assertEqual(base_category_list, ['ball_size', 'colour'])
    shared_variation_list = product.getVariationCategoryList()
    shared_variation_list.sort()
    self.assertEqual(len(shared_variation_list), 1)
    self.assertEqual(shared_variation_list, ['colour/white', ])
    individual_variation_list = product.searchFolder(
        portal_type='Product Individual Variation',
        sort_on=(['id', 'ASC'], ),
    )
    self.assertEqual(len(individual_variation_list), 1)
    individual_variation = individual_variation_list[0].getObject()
    self.assertEqual(individual_variation.getTitle(), 's4')
    self.assertEqual(
        individual_variation.getVariationBaseCategoryList(), ['ball_size'],
    )
    # The third update allows to add variations (individuals and shareds)
    self.loadSQLDump(
        self.connection,
        '%s/dump_product_sync_11.sql' % self.ps_dump_path,
    )
    self.loadSync([self.prestashop.product_module, ])
    self.assertEqual(len(self.product_module.contentValues()), 2)
    base_category_list = product.getVariationBaseCategoryList()
    base_category_list.sort()
    self.assertEqual(len(base_category_list), 2)
    self.assertEqual(base_category_list, ['ball_size', 'colour'])
    shared_variation_list = product.getVariationCategoryList()
    shared_variation_list.sort()
    self.assertEqual(len(shared_variation_list), 3)
    self.assertEqual(
        shared_variation_list,
        ['colour/black', 'colour/red', 'colour/white', ])
    individual_variation_list = product.searchFolder(
        portal_type='Product Individual Variation',
        sort_on=(['id', 'ASC'], ),
    )
    self.assertEqual(len(individual_variation_list), 3)
    for index, individual_variation in enumerate(individual_variation_list):
      # Use shortcut for the checking
      individual_variation = individual_variation.getObject()
      title = individual_variation.getTitle()
      base_category_list = individual_variation.getVariationBaseCategoryList()
      # check through the order
      if index == 0:
        self.assertEqual(title, 's4')
        self.assertEqual(base_category_list, ['ball_size'])
      elif index == 1:
        self.assertEqual(title, 's5')
        self.assertEqual(base_category_list, ['ball_size'])
      elif index == 2:
        self.assertEqual(title, 's6')
        self.assertEqual(base_category_list, ['ball_size'])
      else:
        raise ValueError, 'Can not check variation: %s of the product: %s' % \
            (individual_variation.getId(), product.getTitle())
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml= self.root_xml % product.Resource_asTioSafeXML(),
        tiosafe_xml=self.root_xml % self.prestashop.product_module()[0].asXML(),
        xsd_path='../XSD/resources.xsd',
    )

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestProductERP5Synchronization))
  return suite
