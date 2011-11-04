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
from DateTime import DateTime
from Products.ERP5TioSafe.tests.testPrestashopMixin import testPrestashopMixin

class TestSaleOrderERP5Synchronization(testPrestashopMixin):
  """ This class allows to check different cases of Slae Order's sync. """

  def getBusinessTemplateList(self):
    return testPrestashopMixin.getBusinessTemplateList(self) + ('erp5_accounting',
                                                                'erp5_invoicing',
                                                                'erp5_simplified_invoicing',
                                                                'erp5_simulation',
                                                                'erp5_simulation_legacy',
                                                                'erp5_trade_simulation_legacy',
                                                                'erp5_accounting_simulation_legacy',
                                                                'erp5_invoicing_simulation_legacy',
                                                                )

  def afterSetUp(self):
    """ This method is called after the SetUp method. """
    # Shortcut for modules and tools
    self.person_module = self.portal.person_module
    self.organisation_module = self.portal.organisation_module
    self.product_module = self.portal.product_module
    self.service_module = self.portal.service_module
    self.sale_order_module = self.portal.sale_order_module
    self.currency_module = self.portal.currency_module
    self.sale_trade_condition_module = self.portal.sale_trade_condition_module
    self.portal_categories = self.portal.portal_categories
    self.connection = self.portal.erp5_sql_connection
    self.prestashop = self.portal.portal_integrations.prestashop
    self.root_xml = '<journal>\n%s\n</journal>'
    self.delivery = self.service_module.tiosafe_delivery_service
    self.discount = self.service_module.tiosafe_discount_service
    self.not_removable_id_list = [self.prestashop.getSourceAdministrationValue().getId(),
                                  self.prestashop.getResourceValue().getId(),
                                  self.prestashop.getDestinationValue().getId()]


  def test_PrestashopSimplestXMLSync(self):
    """ Check the sync of the simplest XML for a sale order. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.initMapping(self.prestashop)
    self.validateRules()
    self.loadSQLDump(
        self.connection,
        '%s/dump_sale_order_sync_01.sql' %  self.ps_dump_path,
    )
    transaction.commit()
    self.tic()

    # Run sync process and check result
    self.assertEqual(len(self.sale_order_module.contentValues()), 0)
    self.assertEqual(len(self.product_module.contentValues()), 1)
    self.assertEqual(len(self.person_module.contentValues()), 1)
    self.loadSync([
        getattr(self.prestashop, module)
        for module in ['person_module', 'product_module', 'sale_order_module']
    ])
    self.assertEqual(len(self.sale_order_module.contentValues()), 1)
    self.assertEqual(len(self.product_module.contentValues()), 5)
    self.assertEqual(len(self.person_module.contentValues()), 2)
    sale_order = self.sale_order_module.contentValues()[0]
    person = self.person_module.searchFolder(
        portal_type='Person',
        title='Jean GRAY',
    )[0].getObject()
    product = self.product_module.searchFolder(
        portal_type='Product',
        title='Stylo',
    )[0].getObject()
    currency = self.currency_module.contentValues()[0]
    trade_condition = self.prestashop.getSourceTradeValue()
    self.assertEqual(sale_order.getSourceValue(), self.organisation)
    self.assertEqual(sale_order.getSourceSectionValue(), self.organisation)
    self.assertEqual(sale_order.getDestinationValue(), person)
    self.assertEqual(sale_order.getDestinationSectionValue(), person)
    self.assertEqual(sale_order.getPriceCurrencyValue(), currency)
    self.assertEqual(sale_order.getSpecialiseValueList(), [trade_condition, ])
    self.assertEqual(sale_order.getReference(), '1')
    self.assertEqual(
        str(sale_order.getStartDate()), str(DateTime('2010-06-14')),
    )
    self.assertEqual(
        str(sale_order.getStopDate()), str(DateTime('2010-06-16')),
    )
    self.assertEqual(round(sale_order.getTotalPrice(), 6), 8.772241)
    self.assertEqual(sale_order.getSimulationState(), 'confirmed')
    sale_order_line_list  = sale_order.contentValues(
        portal_type='Sale Order Line',
    )
    self.assertEqual(len(sale_order_line_list), 2)
    for line in sale_order_line_list:
      if line.getTitle() == 'Delivery':
        self.assertEqual(line.getResourceValue(), self.delivery)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.getQuantity(), 1.0)
        self.assertEqual(round(line.getPrice(), 6), 6.672241)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
      elif line.getTitle() == 'Stylo':
        self.assertEqual(line.getResourceValue(), product)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.getQuantity(), 1.0)
        self.assertEqual(round(line.getPrice(), 6), 2.1)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
      else:
        self.failUnless(line.getTitle() in ['Delivery', 'Stylo'])
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        tiosafe_xml=self.root_xml % sale_order.Transaction_asTioSafeXML(context_document=self.portal.portal_synchronizations.ps_SaleOrder_pub.getPath()),
        plugin_xml=self.root_xml % self.prestashop.sale_order_module()[0].asXML(),
        xsd_path='../XSD/transactions.xsd',
    )

  def test_PrestashopSyncWithIndividualVariation(self):
    """
      Check the sync of sale order with individual variation on the product.
    """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.initMapping()
    self.validateRules()
    # Integration site country
    mapping_dict_list = [
        { 'title': 'Country',
          'path': 'Country',
          'source_reference': 'Country',
          'destination_reference': 'region', },
        { 'title': 'France',
          'path': 'Country/France',
          'source_reference': 'France',
          'destination_reference': 'france', },
       { 'title': 'Allemagne',
          'path': 'Country/Allemagne',
          'source_reference': 'Allemagne',
          'destination_reference': 'europe/western_europe/allemagne', },
        { 'title': 'Taille du Ballon',
          'path': 'TailleduBallon',
          'source_reference': 'Taille du Ballon',
          'destination_reference': 'ball_size', },
        { 'title': 'Couleur',
          'path': 'Couleur',
          'source_reference': 'Couleur',
          'destination_reference': 'colour', },
        { 'title': 'Payment Mode',
          'path': 'PaymentMode',
          'source_reference': 'Payment Mode',
          'destination_reference': 'payment_mode', },
        { 'title': 'CB',
          'path': 'PaymentMode/CB',
          'source_reference': 'CB',
          'destination_reference': 'cb', },
        { 'title': 'Cheque',
          'path': 'PaymentMode/Cheque',
          'source_reference': 'Cheque',
          'destination_reference': 'cb', },
    ]
    for mapping in mapping_dict_list:
      self.createMapping(integration_site=self.prestashop, **mapping)
    self.loadSQLDump(
        self.connection,
        '%s/dump_sale_order_sync_02.sql' %  self.ps_dump_path,
    )
    transaction.commit()
    self.tic()

    # Run sync process and check result
    self.assertEqual(len(self.sale_order_module.contentValues()), 0)
    self.assertEqual(len(self.product_module.contentValues()), 1)
    self.assertEqual(len(self.person_module.contentValues()), 1)
    self.loadSync([
        getattr(self.prestashop, module)
        for module in ['person_module', 'product_module', 'sale_order_module']
    ])
    self.assertEqual(len(self.sale_order_module.contentValues()), 1)
    self.assertEqual(len(self.product_module.contentValues()), 5)
    self.assertEqual(len(self.person_module.contentValues()), 2)
    sale_order = self.sale_order_module.contentValues()[0]
    person = self.person_module.searchFolder(
        portal_type='Person',
        title='Jean GRAY',
    )[0].getObject()
    product = self.product_module.searchFolder(
        portal_type='Product',
        title='Ballon',
    )[0].getObject()
    currency = self.currency_module.contentValues()[0]
    trade_condition = self.prestashop.getSourceTradeValue()
    self.assertEqual(sale_order.getSourceValue(), self.organisation)
    self.assertEqual(sale_order.getSourceSectionValue(), self.organisation)
    self.assertEqual(sale_order.getDestinationValue(), person)
    self.assertEqual(sale_order.getDestinationSectionValue(), person)
    self.assertEqual(sale_order.getPriceCurrencyValue(), currency)
    self.assertEqual(sale_order.getSpecialiseValueList(), [trade_condition, ])
    self.assertEqual(sale_order.getReference(), '1')
    self.assertEqual(
        str(sale_order.getStartDate()), str(DateTime('2010-06-14')),
    )
    self.assertEqual(
        str(sale_order.getStopDate()), str(DateTime('2010-06-16')),
    )
    self.assertEqual(round(sale_order.getTotalPrice(), 6), 87.472241)
    self.assertEqual(sale_order.getSimulationState(), 'confirmed')
    sale_order_line_list  = sale_order.contentValues(
        portal_type='Sale Order Line',
    )
    self.assertEqual(len(sale_order_line_list), 3)
    product_relative_url = product.getRelativeUrl()
    for line in sale_order_line_list:
      if line.getId() == '1': # Ballon / (Taille du Ballon/s4)
        self.assertEqual(line.getTitle(), 'Ballon - Taille du Ballon : s4')
        self.assertEqual(line.getResourceValue(), product)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.movement_0.getQuantity(), 2.0)
        self.assertEqual(round(line.movement_0.getPrice(), 6), 20.2)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
        self.assertEqual(
            line.getVariationCategoryList(),
            ['ball_size/%s/1' % product_relative_url, ],
        )
      elif line.getId() == '2': # Ballon / (Taille du Ballon/s5)
        self.assertEqual(line.getTitle(), 'Ballon - Taille du Ballon : s5')
        self.assertEqual(line.getResourceValue(), product)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.movement_0.getQuantity(), 2.0)
        self.assertEqual(round(line.movement_0.getPrice(), 6), 20.2)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
        self.assertEqual(
            line.getVariationCategoryList(),
            ['ball_size/%s/2' % product_relative_url, ],
        )
      elif line.getId() == '3':
        self.assertEqual(line.getTitle(), 'Delivery')
        self.assertEqual(line.getResourceValue(), self.delivery)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.getQuantity(), 1.0)
        self.assertEqual(round(line.getPrice(), 6), 6.672241)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
      else:
        raise 'A line has not been checked'
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        tiosafe_xml=self.root_xml % sale_order.Transaction_asTioSafeXML(context_document=self.portal.portal_synchronizations.ps_SaleOrder_pub.getPath()),
        plugin_xml=self.root_xml % self.prestashop.sale_order_module()[0].asXML(),
        xsd_path='../XSD/transactions.xsd',
    )

  def test_PrestashopSyncWithSharedVariation(self):
    """ Check the sync of sale order with shared variation. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.initMapping(self.prestashop)
    self.validateRules()
    self.loadSQLDump(
        self.connection,
        '%s/dump_sale_order_sync_03.sql' %  self.ps_dump_path,
    )
    transaction.commit()
    self.tic()

    # Run sync process and check result
    self.assertEqual(len(self.sale_order_module.contentValues()), 0)
    self.assertEqual(len(self.product_module.contentValues()), 1)
    self.assertEqual(len(self.person_module.contentValues()), 1)
    self.loadSync([
        getattr(self.prestashop, module)
        for module in ['person_module', 'product_module', 'sale_order_module']
    ])
    self.assertEqual(len(self.sale_order_module.contentValues()), 1)
    self.assertEqual(len(self.product_module.contentValues()), 5)
    self.assertEqual(len(self.person_module.contentValues()), 2)
    sale_order = self.sale_order_module.contentValues()[0]
    person = self.person_module.searchFolder(
        portal_type='Person',
        title='Jean GRAY',
    )[0].getObject()
    product = self.product_module.searchFolder(
        portal_type='Product',
        title='Ballon de Foot',
    )[0].getObject()
    currency = self.currency_module.contentValues()[0]
    trade_condition = self.prestashop.getSourceTradeValue()
    self.assertEqual(sale_order.getSourceValue(), self.organisation)
    self.assertEqual(sale_order.getSourceSectionValue(), self.organisation)
    self.assertEqual(sale_order.getDestinationValue(), person)
    self.assertEqual(sale_order.getDestinationSectionValue(), person)
    self.assertEqual(sale_order.getPriceCurrencyValue(), currency)
    self.assertEqual(sale_order.getSpecialiseValueList(), [trade_condition, ])
    self.assertEqual(sale_order.getReference(), '1')
    self.assertEqual(
        str(sale_order.getStartDate()), str(DateTime('2010-06-14')),
    )
    self.assertEqual(
        str(sale_order.getStopDate()), str(DateTime('2010-06-16')),
    )
    self.assertEqual(round(sale_order.getTotalPrice(), 6), 807.872241)
    self.assertEqual(sale_order.getSimulationState(), 'confirmed')
    sale_order_line_list  = sale_order.contentValues(
        portal_type='Sale Order Line',
    )
    self.assertEqual(len(sale_order_line_list), 3)
    for line in sale_order_line_list:
      if line.getId() == '1': # Ballon de Foot / (Couleur/Blanc)
        self.assertEqual(line.getTitle(), 'Ballon de Foot - Couleur : Blanc')
        self.assertEqual(line.getResourceValue(), product)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.movement_0.getQuantity(), 2.0)
        self.assertEqual(round(line.movement_0.getPrice(), 6), 200.3)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
        self.assertEqual(
            line.getVariationCategoryList(),
            ['colour/white', ],
        )
      elif line.getId() == '2': # Ballon de Foot / (Couleur/Noir)
        self.assertEqual(line.getTitle(), 'Ballon de Foot - Couleur : Noir')
        self.assertEqual(line.getResourceValue(), product)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.movement_0.getQuantity(), 2.0)
        self.assertEqual(round(line.movement_0.getPrice(), 6), 200.3)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
        self.assertEqual(
            line.getVariationCategoryList(),
            ['colour/black', ],
        )
      elif line.getId() == '3':
        self.assertEqual(line.getTitle(), 'Delivery')
        self.assertEqual(line.getResourceValue(), self.delivery)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.getQuantity(), 1.0)
        self.assertEqual(round(line.getPrice(), 6), 6.672241)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
      else:
        raise 'A line has not been checked'
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        tiosafe_xml=self.root_xml % sale_order.Transaction_asTioSafeXML(context_document=self.portal.portal_synchronizations.ps_SaleOrder_pub.getPath()),
        plugin_xml=self.root_xml % self.prestashop.sale_order_module()[0].asXML(),
        xsd_path='../XSD/transactions.xsd',
    )

  def test_PrestashopSyncDifferentKindVariation(self):
    """ Check the sync of sale order with the two kind of variations. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.initMapping()
    self.validateRules()
    # Integration site country
    mapping_dict_list = [
        { 'title': 'Country',
          'path': 'Country',
          'source_reference': 'Country',
          'destination_reference': 'region', },
        { 'title': 'France',
          'path': 'Country/France',
          'source_reference': 'France',
          'destination_reference': 'france', },
        { 'title': 'Allemagne',
          'path': 'Country/Allemagne',
          'source_reference': 'Allemagne',
          'destination_reference': 'europe/western_europe/allemagne', },
        { 'title': 'Taille du Ballon',
          'path': 'TailleduBallon',
          'source_reference': 'Taille du Ballon',
          'destination_reference': 'ball_size', },
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
        { 'title': 'Payment Mode',
          'path': 'PaymentMode',
          'source_reference': 'Payment Mode',
          'destination_reference': 'payment_mode', },
        { 'title': 'CB',
          'path': 'PaymentMode/CB',
          'source_reference': 'CB',
          'destination_reference': 'cb', },
        { 'title': 'Cheque',
          'path': 'PaymentMode/Cheque',
          'source_reference': 'Cheque',
          'destination_reference': 'cb', },
    ]
    for mapping in mapping_dict_list:
      self.createMapping(integration_site=self.prestashop, **mapping)
    self.loadSQLDump(
        self.connection,
        '%s/dump_sale_order_sync_04.sql' %  self.ps_dump_path,
    )
    transaction.commit()
    self.tic()

    # Run sync process and check result
    self.assertEqual(len(self.sale_order_module.contentValues()), 0)
    self.assertEqual(len(self.product_module.contentValues()), 1)
    self.assertEqual(len(self.person_module.contentValues()), 1)
    self.loadSync([
        getattr(self.prestashop, module)
        for module in ['person_module', 'product_module', 'sale_order_module']
    ])
    self.assertEqual(len(self.sale_order_module.contentValues()), 1)
    self.assertEqual(len(self.product_module.contentValues()), 5)
    self.assertEqual(len(self.person_module.contentValues()), 2)
    sale_order = self.sale_order_module.contentValues()[0]
    person = self.person_module.searchFolder(
        portal_type='Person',
        title='Jean GRAY',
    )[0].getObject()
    product = self.product_module.searchFolder(
        portal_type='Product',
        title='Ballon de Basket',
    )[0].getObject()
    currency = self.currency_module.contentValues()[0]
    trade_condition = self.prestashop.getSourceTradeValue()
    self.assertEqual(sale_order.getSourceValue(), self.organisation)
    self.assertEqual(sale_order.getSourceSectionValue(), self.organisation)
    self.assertEqual(sale_order.getDestinationValue(), person)
    self.assertEqual(sale_order.getDestinationSectionValue(), person)
    self.assertEqual(sale_order.getPriceCurrencyValue(), currency)
    self.assertEqual(sale_order.getSpecialiseValueList(), [trade_condition, ])
    self.assertEqual(sale_order.getReference(), '1')
    self.assertEqual(
        str(sale_order.getStartDate()), str(DateTime('2010-06-14')),
    )
    self.assertEqual(
        str(sale_order.getStopDate()), str(DateTime('2010-06-16')),
    )
    self.assertEqual(round(sale_order.getTotalPrice(), 6), 16009.872241)
    self.assertEqual(sale_order.getSimulationState(), 'confirmed')
    sale_order_line_list  = sale_order.contentValues(
        portal_type='Sale Order Line',
    )
    self.assertEqual(len(sale_order_line_list), 3)
    product_relative_url = product.getRelativeUrl()
    # See movement rather than line
    for line in sale_order_line_list:
      if line.getId() == '1': # Ballon de Foot / (Couleur/Blanc) / (Taille du Ballon/s5)
        self.assertEqual(
            line.getTitle(),
            'Ballon de Basket - Couleur : Blanc, Taille du Ballon : s4',
        )
        self.assertEqual(line.getResourceValue(), product)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.movement_0_0.getQuantity(), 4.0)
        self.assertEqual(round(line.movement_0_0.getPrice(), 6), 2000.4)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
        self.assertSameSet(
            line.getVariationCategoryList(),
            ['ball_size/%s/1' % product_relative_url, 'colour/white', ],
        )
      elif line.getId() == '2': # Ballon de Foot / (Couleur/Noir) / (Taille du Ballon/s4)
        self.assertEqual(
            line.getTitle(),
            'Ballon de Basket - Couleur : Noir, Taille du Ballon : s5',
        )
        self.assertEqual(line.getResourceValue(), product)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.movement_0_0.getQuantity(), 4.0)
        self.assertEqual(round(line.movement_0_0.getPrice(), 6), 2000.4)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
        self.assertSameSet(
            line.getVariationCategoryList(),
            ['ball_size/%s/2' % product_relative_url, 'colour/black', ],
        )
      elif line.getId() == '3':
        self.assertEqual(line.getTitle(), 'Delivery')
        self.assertEqual(line.getResourceValue(), self.delivery)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.getQuantity(), 1.0)
        self.assertEqual(round(line.getPrice(), 6), 6.672241)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
      else:
        raise 'A line has not been checked'
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        tiosafe_xml=self.root_xml % sale_order.Transaction_asTioSafeXML(context_document=self.portal.portal_synchronizations.ps_SaleOrder_pub.getPath()),
        plugin_xml=self.root_xml % self.prestashop.sale_order_module()[0].asXML(),
        xsd_path='../XSD/transactions.xsd',
    )

  def test_PrestashopDiscountSync(self):
    """ Check the sync of sale order with discount. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.initMapping(self.prestashop)
    self.validateRules()
    self.loadSQLDump(
        self.connection,
        '%s/dump_sale_order_sync_05.sql' %  self.ps_dump_path,
    )
    transaction.commit()
    self.tic()

    # Run sync process and check result
    self.assertEqual(len(self.sale_order_module.contentValues()), 0)
    self.assertEqual(len(self.product_module.contentValues()), 1)
    self.assertEqual(len(self.person_module.contentValues()), 1)
    self.loadSync([
        getattr(self.prestashop, module)
        for module in ['person_module', 'product_module', 'sale_order_module']
    ])
    self.assertEqual(len(self.sale_order_module.contentValues()), 1)
    self.assertEqual(len(self.product_module.contentValues()), 5)
    self.assertEqual(len(self.person_module.contentValues()), 2)
    sale_order = self.sale_order_module.contentValues()[0]
    person = self.person_module.searchFolder(
        portal_type='Person',
        title='Jean GRAY',
    )[0].getObject()
    product = self.product_module.searchFolder(
        portal_type='Product',
        title='Stylo',
    )[0].getObject()
    currency = self.currency_module.contentValues()[0]
    trade_condition = self.prestashop.getSourceTradeValue()
    self.assertEqual(sale_order.getSourceValue(), self.organisation)
    self.assertEqual(sale_order.getSourceSectionValue(), self.organisation)
    self.assertEqual(sale_order.getDestinationValue(), person)
    self.assertEqual(sale_order.getDestinationSectionValue(), person)
    self.assertEqual(sale_order.getPriceCurrencyValue(), currency)
    self.assertEqual(sale_order.getSpecialiseValueList(), [trade_condition, ])
    self.assertEqual(sale_order.getReference(), '1')
    self.assertEqual(
        str(sale_order.getStartDate()), str(DateTime('2010-06-14')),
    )
    self.assertEqual(
        str(sale_order.getStopDate()), str(DateTime('2010-06-16')),
    )
    self.assertEqual(round(sale_order.getTotalPrice(), 6), 3.772241)
    self.assertEqual(sale_order.getSimulationState(), 'confirmed')
    sale_order_line_list  = sale_order.contentValues(
        portal_type='Sale Order Line',
    )
    self.assertEqual(len(sale_order_line_list), 3)
    for line in sale_order_line_list:
      if line.getTitle() == 'Delivery':
        self.assertEqual(line.getTitle(), 'Delivery')
        self.assertEqual(line.getResourceValue(), self.delivery)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.getQuantity(), 1.0)
        self.assertEqual(round(line.getPrice(), 6), 6.672241)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
      elif line.getTitle() == 'Discount':
        self.assertEqual(line.getTitle(), 'Discount')
        self.assertEqual(line.getResourceValue(), self.discount)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_exempted',
        )
        self.assertEqual(line.getQuantity(), 1.0)
        self.assertEqual(round(line.getPrice(), 6), -5.0)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
      elif line.getTitle() == 'Stylo':
        self.assertEqual(line.getTitle(), 'Stylo')
        self.assertEqual(line.getResourceValue(), product)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.getQuantity(), 1.0)
        self.assertEqual(round(line.getPrice(), 6), 2.1)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
      else:
        self.failUnless(line.getTitle() in ['Delivery', 'Stylo', 'Discount'])
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        tiosafe_xml=self.root_xml % sale_order.Transaction_asTioSafeXML(context_document=self.portal.portal_synchronizations.ps_SaleOrder_pub.getPath()),
        plugin_xml=self.root_xml % self.prestashop.sale_order_module()[0].asXML(),
        xsd_path='../XSD/transactions.xsd',
    )

  def test_PrestashopSyncWithoutDestination(self):
    """ Check the sync of sale order without destination. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.initMapping(self.prestashop)
    self.validateRules()
    person_unknown = self.prestashop.getDestinationValue()
    self.loadSQLDump(
        self.connection,
        '%s/dump_sale_order_sync_06.sql' %  self.ps_dump_path,
    )
    transaction.commit()
    self.tic()

    # Run sync process and check result
    self.assertEqual(len(self.sale_order_module.contentValues()), 0)
    self.assertEqual(len(self.product_module.contentValues()), 1)
    self.assertEqual(len(self.person_module.contentValues()), 1)
    self.loadSync([
        getattr(self.prestashop, module)
        for module in ['person_module', 'product_module', 'sale_order_module']
    ])
    self.assertEqual(len(self.sale_order_module.contentValues()), 1)
    self.assertEqual(len(self.product_module.contentValues()), 5)
    self.assertEqual(len(self.person_module.contentValues()), 2)
    sale_order = self.sale_order_module.contentValues()[0]
    product = self.product_module.searchFolder(
        portal_type='Product',
        title='Stylo',
    )[0].getObject()
    currency = self.currency_module.contentValues()[0]
    trade_condition = self.prestashop.getSourceTradeValue()
    self.assertEqual(sale_order.getSourceValue(), self.organisation)
    self.assertEqual(sale_order.getSourceSectionValue(), self.organisation)
    self.assertEqual(sale_order.getDestinationValue(), person_unknown)
    self.assertEqual(sale_order.getDestinationSectionValue(), person_unknown)
    self.assertEqual(sale_order.getPriceCurrencyValue(), currency)
    self.assertEqual(sale_order.getSpecialiseValueList(), [trade_condition, ])
    self.assertEqual(sale_order.getReference(), '1')
    self.assertEqual(
        str(sale_order.getStartDate()), str(DateTime('2010-06-14')),
    )
    self.assertEqual(
        str(sale_order.getStopDate()), str(DateTime('2010-06-16')),
    )
    self.assertEqual(round(sale_order.getTotalPrice(), 6), 8.772241)
    self.assertEqual(sale_order.getSimulationState(), 'confirmed')
    sale_order_line_list  = sale_order.contentValues(
        portal_type='Sale Order Line',
    )
    self.assertEqual(len(sale_order_line_list), 2)
    for line in sale_order_line_list:
      if line.getTitle() == 'Delivery':
        self.assertEqual(line.getTitle(), 'Delivery')
        self.assertEqual(line.getResourceValue(), self.delivery)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.getQuantity(), 1.0)
        self.assertEqual(round(line.getPrice(), 6), 6.672241)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
      elif line.getTitle() == 'Stylo':
        self.assertEqual(line.getTitle(), 'Stylo')
        self.assertEqual(line.getResourceValue(), product)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.getQuantity(), 1.0)
        self.assertEqual(round(line.getPrice(), 6), 2.1)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
      else:
        self.failUnless(line.getTitle() in ['Delivery', 'Stylo'])
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        tiosafe_xml=self.root_xml % sale_order.Transaction_asTioSafeXML(context_document=self.portal.portal_synchronizations.ps_SaleOrder_pub.getPath()),
        plugin_xml=self.root_xml % self.prestashop.sale_order_module()[0].asXML(),
        xsd_path='../XSD/transactions.xsd',
    )

  def test_PrestashopSyncWithoutProduct(self):
    """ Check the sync of sale order with a non-existant product. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.initMapping(self.prestashop)
    self.validateRules()
    product_unknown = self.prestashop.getResourceValue()
    self.loadSQLDump(
        self.connection,
        '%s/dump_sale_order_sync_07.sql' %  self.ps_dump_path,
    )
    transaction.commit()
    self.tic()

    # Run sync process and check result
    self.assertEqual(len(self.sale_order_module.contentValues()), 0)
    self.assertEqual(len(self.product_module.contentValues()), 1)
    self.assertEqual(len(self.person_module.contentValues()), 1)
    self.loadSync([
        getattr(self.prestashop, module)
        for module in ['person_module', 'product_module', 'sale_order_module']
    ])
    self.assertEqual(len(self.sale_order_module.contentValues()), 1)
    self.assertEqual(len(self.product_module.contentValues()), 5)
    self.assertEqual(len(self.person_module.contentValues()), 2)
    sale_order = self.sale_order_module.contentValues()[0]
    person = self.person_module.searchFolder(
        portal_type='Person',
        title='Jean GRAY',
    )[0].getObject()
    currency = self.currency_module.contentValues()[0]
    trade_condition = self.prestashop.getSourceTradeValue()
    self.assertEqual(sale_order.getSourceValue(), self.organisation)
    self.assertEqual(sale_order.getSourceSectionValue(), self.organisation)
    self.assertEqual(sale_order.getDestinationValue(), person)
    self.assertEqual(sale_order.getDestinationSectionValue(), person)
    self.assertEqual(sale_order.getPriceCurrencyValue(), currency)
    self.assertEqual(sale_order.getSpecialiseValueList(), [trade_condition, ])
    self.assertEqual(sale_order.getReference(), '1')
    self.assertEqual(
        str(sale_order.getStartDate()), str(DateTime('2010-06-14')),
    )
    self.assertEqual(
        str(sale_order.getStopDate()), str(DateTime('2010-06-16')),
    )
    self.assertEqual(round(sale_order.getTotalPrice(), 6), 16009.872241)
    self.assertEqual(sale_order.getSimulationState(), 'confirmed')
    sale_order_line_list  = sale_order.contentValues(
        portal_type='Sale Order Line',
    )
    self.assertEqual(len(sale_order_line_list), 3)
    for line in sale_order_line_list:
      if line.getTitle() == 'Ballon de Basket - Couleur : Blanc, Taille du Ballon : s4':
        self.assertEqual(
            line.getTitle(),
            'Ballon de Basket - Couleur : Blanc, Taille du Ballon : s4',
        )
        self.assertEqual(line.getResourceValue(), product_unknown)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.getQuantity(), 4.0)
        self.assertEqual(round(line.getPrice(), 6), 2000.4)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
        # FIXME: Is variation are keep even if the product is removed ?? (cf. dump)
#        self.assertEqual(line.movement_0_0.getQuantity(), 4.0)
#        self.assertEqual(round(line.movement_0_0.getPrice(), 6), 2000.4)
#        self.assertEqual(
#            line.getVariationCategoryList(),
#            ['ball_size/product_module/2/1', 'colour/white', ],
#        )
      elif line.getTitle() == 'Ballon de Basket - Couleur : Noir, Taille du Ballon : s5':
        self.assertEqual(
            line.getTitle(),
            'Ballon de Basket - Couleur : Noir, Taille du Ballon : s5',
        )
        self.assertEqual(line.getResourceValue(), product_unknown)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.getQuantity(), 4.0)
        self.assertEqual(round(line.getPrice(), 6), 2000.4)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
        # FIXME: Is variation are keep even if the product is removed ?? (cf. dump)
#        self.assertEqual(line.movement_0_0.getQuantity(), 4.0)
#        self.assertEqual(round(line.movement_0_0.getPrice(), 6), 2000.4)
#        self.assertEqual(
#            line.getVariationCategoryList(),
#            ['ball_size/product_module/2/2', 'colour/black', ],
#        )
      elif line.getTitle() == 'Delivery': # Ballon de Basket / (Couleur/Noir) / (Taille du Ballon/s5)
        self.assertEqual(line.getTitle(), 'Delivery')
        self.assertEqual(line.getResourceValue(), self.delivery)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.getQuantity(), 1.0)
        self.assertEqual(round(line.getPrice(), 6), 6.672241)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
      else:
        raise 'A line has not been checked'
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        tiosafe_xml=self.root_xml % sale_order.Transaction_asTioSafeXML(context_document=self.portal.portal_synchronizations.ps_SaleOrder_pub.getPath()),
        plugin_xml=self.root_xml % self.prestashop.sale_order_module()[0].asXML(),
        xsd_path='../XSD/transactions.xsd',
    )

  def test_PrestashopGenerateAccounting(self):
    """
      This test realises a sync of sale order and generate the accounting to
      check that it works.
    """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.initMapping(self.prestashop)
    self.validateRules()
    self.loadSQLDump(
        self.connection,
        '%s/dump_sale_order_sync_08.sql' %  self.ps_dump_path,
    )
    transaction.commit()
    self.tic()

    # Run sync process and check result
    self.assertEqual(len(self.sale_order_module.contentValues()), 0)
    self.assertEqual(len(self.product_module.contentValues()), 1)
    self.assertEqual(len(self.person_module.contentValues()), 1)
    self.loadSync([
        getattr(self.prestashop, module)
        for module in ['person_module', 'product_module', 'sale_order_module']
    ])
    self.assertEqual(len(self.sale_order_module.contentValues()), 1)
    self.assertEqual(len(self.product_module.contentValues()), 5)
    self.assertEqual(len(self.person_module.contentValues()), 2)
    sale_order = self.sale_order_module.contentValues()[0]
    person = self.person_module.searchFolder(
        portal_type='Person',
        title='Jean GRAY',
    )[0].getObject()
    product = self.product_module.searchFolder(
        portal_type='Product',
        title='Stylo',
    )[0].getObject()
    # TODO: What about the vat ?????
    vat_normal = self.service_module.searchFolder(
        portal_type='Service',
        title='VAT Normal',
    )[0].getObject()
    vat_reduced = self.service_module.searchFolder(
        portal_type='Service',
        title='VAT Reduced',
    )[0].getObject()
    vat_exempted = self.service_module.searchFolder(
        portal_type='Service',
        title='VAT Exempted',
    )[0].getObject()

    currency = self.currency_module.contentValues()[0]
    trade_condition = self.prestashop.getSourceTradeValue()
    self.assertEqual(sale_order.getSourceValue(), self.organisation)
    self.assertEqual(sale_order.getSourceSectionValue(), self.organisation)
    self.assertEqual(sale_order.getDestinationValue(), person)
    self.assertEqual(sale_order.getDestinationSectionValue(), person)
    self.assertEqual(sale_order.getPriceCurrencyValue(), currency)
    self.assertEqual(sale_order.getSpecialiseValueList(), [trade_condition, ])
    self.assertEqual(sale_order.getReference(), '1')
    self.assertEqual(
        str(sale_order.getStartDate()), str(DateTime('2010-06-14')),
    )
    self.assertEqual(
        str(sale_order.getStopDate()), str(DateTime('2010-06-16')),
    )
    self.assertEqual(round(sale_order.getTotalPrice(), 6), 8.772241)
    self.assertEqual(sale_order.getSimulationState(), 'confirmed')
    sale_order_line_list  = sale_order.contentValues(
        portal_type='Sale Order Line',
    )
    self.assertEqual(len(sale_order_line_list), 2)
    for line in sale_order_line_list:
      if line.getTitle() == 'Delivery':
        self.assertEqual(line.getTitle(), 'Delivery')
        self.assertEqual(line.getResourceValue(), self.delivery)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.getQuantity(), 1.0)
        self.assertEqual(round(line.getPrice(), 6), 6.672241)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
      elif line.getTitle() == 'Stylo':
        self.assertEqual(line.getTitle(), 'Stylo')
        self.assertEqual(line.getResourceValue(), product)
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.getQuantity(), 1.0)
        self.assertEqual(round(line.getPrice(), 6), 2.1)
        self.assertEqual(line.getPriceCurrencyValue(), currency)
      else:
        self.failUnless(line.getTitle() in ['Delivery', 'Stylo'])

        raise 'A line has not been checked'
    # Check the accounting
    sale_packing_list = sale_order.getCausalityRelatedValue(
        portal_type='Sale Packing List',
    )
    self.assertNotEqual(sale_packing_list, None)
    # Ship the sale packing list
    sale_packing_list.start()
    self.assertEqual(sale_packing_list.getSimulationState(), 'started')
    transaction.commit()
    self.tic()
    self.assertEqual(len(sale_packing_list.contentValues()), 3) # Two SPL + Payment condition
    self.assertEqual(len(sale_packing_list.contentValues(portal_type='Sale Packing List Line'),), 2)
    # Check the sale invoice and the lines
    invoice = sale_packing_list.getCausalityRelatedValue(
        portal_type='Sale Invoice Transaction',
    )
    self.assertNotEqual(invoice, None)
    invoice_line_list = invoice.getMovementList(portal_type='Invoice Line')
    self.assertEqual(len(invoice_line_list), 5)
    for line in invoice_line_list:
      if line.getResourceValue() == self.delivery:
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.getQuantity(), 1.0)
        self.assertEqual(line.getPrice(), line.getTotalPrice(), 6.672241)
      elif line.getResourceValue() == product:
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/base/taxable/vat/vat_normal_rate',
        )
        self.assertEqual(line.getQuantity(), 1.0)
        self.assertEqual(line.getPrice(), line.getTotalPrice(), 2.1)
      elif line.getResourceValue() == vat_normal:
        self.assertEqual(
            line.getBaseContribution(),
            'base_amount/trade/l10n/fr/vat/purchase_sale/national',
        )
        self.assertEqual(line.getQuantity(), 6.672241 + 2.1)
        self.assertEqual(line.getPrice(), 0.196)
        self.assertEqual(line.getTotalPrice(), 6.672241 * 0.196 + 2.1 * 0.196)
      elif line.getResourceValue() in [vat_reduced, vat_exempted]:
        self.assertEqual(line.getQuantity(), 0.0)
        self.assertEqual(line.getPrice(), 0.0)
        self.assertEqual(line.getTotalPrice(), 0.0)
      else:
        raise 'The lines must contain VAT, Product or Delivery, nothing else.'
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        tiosafe_xml=self.root_xml % sale_order.Transaction_asTioSafeXML(context_document=self.portal.portal_synchronizations.ps_SaleOrder_pub.getPath()),
        plugin_xml=self.root_xml % self.prestashop.sale_order_module()[0].asXML(),
        xsd_path='../XSD/transactions.xsd',
    )

  def test_PrestashopUpdateDoNothing(self):
    """
      Check that the update of a sale order after the sync do nothing
    """
    # Initialize the instance and prestashop
    portal_sync = self.portal.portal_synchronizations
    self.initPrestashopTest()
    self.initMapping(self.prestashop)
    self.validateRules()
    self.loadSQLDump(
        self.connection,
        '%s/dump_sale_order_sync_01.sql' %  self.ps_dump_path,
    )
    transaction.commit()
    self.tic()
    # Run sync process and check result
    self.assertEqual(len(self.sale_order_module.contentValues()), 0)
    self.assertEqual(len(self.product_module.contentValues()), 1)
    self.assertEqual(len(self.person_module.contentValues()), 1)
    self.loadSync([
        getattr(self.prestashop, module)
        for module in ['person_module', 'product_module', 'sale_order_module']
    ])
    self.assertEqual(len(self.sale_order_module.contentValues()), 1)
    self.assertEqual(len(self.product_module.contentValues()), 5)
    self.assertEqual(len(self.person_module.contentValues()), 2)
    self.assertEqual(str(self.sale_order_module.objectValues()[0].getStartDate()), '2010/06/14')
    # Update the sale order
    self.loadSQLDump(
        self.connection,
        '%s/dump_sale_order_sync_09.sql' %  self.ps_dump_path,
    )
    transaction.commit()
    self.tic()
    self.loadSync([
        getattr(self.prestashop, module)
        for module in ['sale_order_module',]
    ])
    self.assertEqual(str(self.sale_order_module.objectValues()[0].getStartDate()), '2010/06/14')


  def test_PrestashopDeleteDoNothing(self):
    """
      Check that the delete of a sale order after the sync did nothing
    """
    # Initialize the instance and prestashop
    portal_sync = self.portal.portal_synchronizations
    self.initPrestashopTest()
    self.initMapping(self.prestashop)
    self.validateRules()
    self.loadSQLDump(
        self.connection,
        '%s/dump_sale_order_sync_01.sql' %  self.ps_dump_path,
    )
    transaction.commit()
    self.tic()
    # Run sync process and check result
    self.assertEqual(len(self.sale_order_module.contentValues()), 0)
    self.assertEqual(len(self.product_module.contentValues()), 1)
    self.assertEqual(len(self.person_module.contentValues()), 1)
    self.loadSync([
        getattr(self.prestashop, module)
        for module in ['person_module', 'product_module', 'sale_order_module']
    ])
    self.assertEqual(len(self.sale_order_module.contentValues()), 1)
    self.assertEqual(len(self.product_module.contentValues()), 5)
    self.assertEqual(len(self.person_module.contentValues()), 2)
    self.assertEqual(self.sale_order_module.objectValues()[0].getSimulationState(), "confirmed")
    # load a dump in which the sale order no longer exists
    self.loadSQLDump(
        self.connection,
        '%s/dump_sale_order_sync_10.sql' %  self.ps_dump_path,
    )
    transaction.commit()
    self.tic()
    self.loadSync([
        getattr(self.prestashop, module)
        for module in ['sale_order_module',]
    ])
    self.assertEqual(self.sale_order_module.objectValues()[0].getSimulationState(), "confirmed")

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestSaleOrderERP5Synchronization))
  return suite
