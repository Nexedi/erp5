#############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Aurelien Calonne <aurel@nexedi.com>
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

from DateTime import DateTime
from Products.ERP5.tests.testAccounting import AccountingTestCase
from AccessControl.SecurityManagement import newSecurityManager

class CurrencyExchangeTestCase(AccountingTestCase):

  username = 'username'

  def beforeTearDown(self):
    self.abort()
    # clear modules if necessary
    currency_list = ('euro', 'yen', 'usd')
    module = self.portal.currency_module
    module.manage_delObjects([x for x in module.objectIds()
                        if x not in currency_list])
    for currency_id in currency_list:
      currency = module._getOb(currency_id, None)
      if currency is not None:
        currency.manage_delObjects([x.getId() for x in
                currency.objectValues(
                 portal_type='Currency Exchange Line')])

    currency_exchange_type = \
      self.portal.portal_categories.currency_exchange_type
    currency_exchange_type.manage_delObjects(
                list(currency_exchange_type.objectIds()))

    self.tic()
 
  def login(self, name=username):
    uf = self.getPortal().acl_users
    uf._doAddUser(self.username, '', ['Assignee', 'Assignor',
       'Author','Manager'], [])
    user = uf.getUserById(self.username).__of__(uf)
    newSecurityManager(None, user)
   
  def getBusinessTemplateList(self):
    """
      Return the list of business templates we need to run the test.
      This method is called during the initialization of the unit test by
      the unit test framework in order to know which business templates
      need to be installed to run the test on.
    """
    return ('erp5_base',
            'erp5_pdm',
            'erp5_simulation',
            'erp5_trade',
            'erp5_accounting',
            'erp5_accounting_ui_test',
            'erp5_simulation_test'
            )


class TestCurrencyExchangeLine(CurrencyExchangeTestCase):
  """
  Test Currency exchange lines.
  """
  def test_CreateCurrencies(self):
    """
      Create currencies to be used for transactions
    """
    module = self.portal.currency_module
    currency1 = module.newContent(portal_type='Currency')
    currency1.setTitle('Euro')
    currency1.setReference('EUR')
    currency1.setBaseUnitQuantity(0.01)
    self.assertEquals(currency1.getTitle(), 'Euro')
    self.assertEquals(currency1.getReference(), 'EUR')
    self.assertEquals(currency1.getBaseUnitQuantity(), 0.01)
    currency1.validate()
    self.assertEquals(0, len(currency1.checkConsistency()))
    self.assertEquals(currency1.getValidationState(),'validated')
    currency2 = module.newContent(portal_type = 'Currency')
    currency2.setTitle('Francs CFA')
    currency2.setReference('XOF')
    currency2.setBaseUnitQuantity(1.00)
    self.assertEquals(currency2.getTitle(), 'Francs CFA')
    self.assertEquals(currency2.getReference(), 'XOF')
    self.assertEquals(currency2.getBaseUnitQuantity(), 1.00)
    currency2.validate()
    self.assertEquals(currency2.getValidationState(),'validated')
    self.assertEquals(0, len(currency2.checkConsistency()))


  def test_UseCurrencyExchangeLineForDestination(self):
    """
      Create a currency exchange line for a currency and then
      convert destination price using that currency exchange line
    """
    self.organisation_module = self.portal.organisation_module
    self.organisation1 = self.organisation_module.my_organisation
    new_currency = self.portal.currency_module.newContent(
                          portal_type='Currency')
    new_currency.setReference('XOF')
    new_currency.setTitle('Francs CFA')
    new_currency.setBaseUnitQuantity(1.00)
    self.tic()
    self.organisation1.edit(
                    price_currency=new_currency.getRelativeUrl())
    euro = self.portal.currency_module.euro
    x_curr_ex_line = euro.newContent(
                        portal_type='Currency Exchange Line',
                        price_currency=new_currency.getRelativeUrl())
    x_curr_ex_line.setTitle('Euro to Francs CFA')
    x_curr_ex_line.setBasePrice(655.957)
    x_curr_ex_line.setStartDate(DateTime(2008,9,8))
    x_curr_ex_line.setStopDate(DateTime(2008,9,10))
    self.assertEquals(x_curr_ex_line.getPriceCurrencyTitle(),
                          'Francs CFA')
    self.assertEquals(x_curr_ex_line.getBasePrice(),655.957)
    x_curr_ex_line.validate()
    self.assertEquals(x_curr_ex_line.getValidationState(),
                           'validated')
    accounting_module = self.portal.accounting_module
    invoice = self._makeOne(
               portal_type='Purchase Invoice Transaction',
               stop_date=DateTime('2008/09/08'),
            source_section_value=self.organisation_module.supplier,
               lines=(dict(
               destination_value=self.account_module.goods_purchase,
                           destination_debit=500),
              dict(destination_value=self.account_module.receivable,
                           destination_credit=500)))
    invoice.AccountingTransaction_convertDestinationPrice(form_id='view')
    line_list = invoice.contentValues(
           portal_type=self.portal.getPortalAccountingMovementTypeList())
    for line in line_list:
      self.assertEquals(line.getDestinationTotalAssetPrice(),
             round(655.957*line.getQuantity()))
                                        

  def test_CreateEmptyCurrencyExchangeLineForDestination(self):
    """
      Create empty currency exchange lines for currencies,
      and verify that only the one that matches the criteria will
      be selected for the conversion
    """
    self.organisation_module = self.portal.organisation_module
    self.organisation1 = self.organisation_module.my_organisation
    new_currency = self.portal.currency_module.newContent(
                   portal_type='Currency')
    new_currency.setReference('XOF')
    new_currency.setTitle('Francs CFA')
    new_currency.setBaseUnitQuantity(1.00)
    self.tic()
    self.organisation1.edit(
                   price_currency=new_currency.getRelativeUrl())
    euro = self.portal.currency_module.euro
    x_curr_ex_line = euro.newContent(
                      portal_type='Currency Exchange Line',
                     price_currency=new_currency.getRelativeUrl())
    x_curr_ex_line.setTitle('Euro to Francs CFA')
    x_curr_ex_line.setBasePrice(655.957)
    x_curr_ex_line.setStartDate(DateTime(2008,9,8))
    x_curr_ex_line.setStopDate(DateTime(2008,9,10))
    self.assertEquals(x_curr_ex_line.getPriceCurrencyTitle(),
                                         'Francs CFA')
    self.assertEquals(x_curr_ex_line.getBasePrice(),655.957)
    x_curr_ex_line.validate()
    self.assertEquals(x_curr_ex_line.getValidationState(),
                            'validated')
    yen = self.portal.currency_module.yen
    yen_line1 = yen.newContent(
                          portal_type='Currency Exchange Line')
    yen_line2 = yen.newContent(
                          portal_type='Currency Exchange Line')
                          
    usd = self.portal.currency_module.usd
    usd_line1 = usd.newContent(
                          portal_type='Currency Exchange Line')
    usd_line2 = usd.newContent(
                          portal_type='Currency Exchange Line')
    
    euro_line = euro.newContent(
                           portal_type='Currency Exchange Line')
    euro_line.validate()
    accounting_module = self.portal.accounting_module
    invoice = self._makeOne(
               portal_type='Purchase Invoice Transaction',
               stop_date=DateTime('2008/09/08'),
           source_section_value=self.organisation_module.supplier,
               lines=(dict(
              destination_value=self.account_module.goods_purchase,
                           destination_debit=500),
              dict(destination_value=self.account_module.receivable,
                           destination_credit=500)))
    invoice.AccountingTransaction_convertDestinationPrice(
                         form_id='view')
    line_list = invoice.contentValues(
           portal_type=self.portal.getPortalAccountingMovementTypeList())
    for line in line_list:
      self.assertEquals(line.getDestinationTotalAssetPrice(),
                   round(655.957*line.getQuantity()))

  def test_UseCurrencyExchangeLineForSource(self):
    """
      Create a currency exchange line for a currency and then
      convert
      source price using that currency exchange line
    """
    self.organisation_module = self.portal.organisation_module
    self.organisation1 = self.organisation_module.my_organisation
    new_currency = self.portal.currency_module.newContent(portal_type='Currency')
    new_currency.setReference('XOF')
    new_currency.setTitle('Francs CFA')
    new_currency.setBaseUnitQuantity(1.00)
    self.tic()
    self.organisation1.edit(
              price_currency=new_currency.getRelativeUrl())
    euro = self.portal.currency_module.euro
    x_curr_ex_line = euro.newContent(
                          portal_type='Currency Exchange Line',
                          price_currency=new_currency.getRelativeUrl())
    x_curr_ex_line.setTitle('Euro to Francs CFA')
    x_curr_ex_line.setBasePrice(655.957)
    x_curr_ex_line.setStartDate(DateTime(2008,9,8))
    x_curr_ex_line.setStopDate(DateTime(2008,9,10))
    self.assertEquals(x_curr_ex_line.getPriceCurrencyTitle(),
                            'Francs CFA')
    self.assertEquals(x_curr_ex_line.getBasePrice(),655.957)
    x_curr_ex_line.validate()
    self.assertEquals(x_curr_ex_line.getValidationState(),
                         'validated')
    accounting_module = self.portal.accounting_module
    invoice = self._makeOne(
               portal_type='Sale Invoice Transaction',
               start_date=DateTime('2008/09/08'),
        destination_section_value=self.organisation_module.supplier,
        lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=500),
                   dict(source_value=self.account_module.receivable,
                           source_credit=500)))
    invoice.AccountingTransaction_convertSourcePrice(
                   form_id='view')
    line_list = invoice.contentValues(
           portal_type=self.portal.getPortalAccountingMovementTypeList())
    for line in line_list:
      if line.getSourceValue() == self.account_module.goods_purchase:
        self.assertEquals(line.getSourceInventoriatedTotalAssetDebit(),
                           327979)
      elif line.getSourceValue() == self.account_module.receivable:
        self.assertEquals(line.getSourceInventoriatedTotalAssetCredit(),
                           327979)
      else:
        self.fail('line not found')

  def test_NoCurrencyExchangeLineForResourceCurrency(self):
    """
      Test that the conversion is not done when there is no currency 
      exchange line defined for the date of the transaction
    """
    self.organisation_module = self.portal.organisation_module
    self.organisation1 = self.organisation_module.my_organisation
    new_currency = self.portal.currency_module.newContent(
                portal_type='Currency')
    new_currency.setReference('XOF')
    new_currency.setTitle('Francs CFA')
    new_currency.setBaseUnitQuantity(1.00)
    self.tic()
    self.organisation1.edit(
                price_currency=new_currency.getRelativeUrl())
    euro = self.portal.currency_module.euro
    accounting_module = self.portal.accounting_module
    invoice = self._makeOne(
               portal_type='Purchase Invoice Transaction',
               stop_date=DateTime('2008/09/08'),
            source_section_value=self.organisation_module.supplier,
               lines=(dict(
                 destination_value=self.account_module.goods_purchase,
                           destination_debit=500),
              dict(destination_value=self.account_module.receivable,
                           destination_credit=500)))
    invoice.AccountingTransaction_convertDestinationPrice(
                        form_id='view')
    line_list = invoice.contentValues(
           portal_type=self.portal.getPortalAccountingMovementTypeList())
    for line in line_list:
      self.assertEquals(line.getDestinationTotalAssetPrice(),None)


  def test_DateOfCurrencyExchangeLineNotDateofTransaction(self):
    """
      Test that the conversion is not done when there is the start date
      and the end date of a currency exchange line don't correspond to
      the date of the transaction, but when the date of the transaction
      falls into the validity period of the currency exchange line,the
      conversion is done
    """
    self.organisation_module = self.portal.organisation_module
    self.organisation1 = self.organisation_module.my_organisation
    new_currency = self.portal.currency_module.newContent(
    portal_type='Currency')
    new_currency.setReference('XOF')
    new_currency.setTitle('Francs CFA')
    new_currency.setBaseUnitQuantity(1.00)
    self.tic()
    self.organisation1.edit(
               price_currency=new_currency.getRelativeUrl())
    euro = self.portal.currency_module.euro
    x_curr_ex_line = euro.newContent(
                      portal_type='Currency Exchange Line',
                      price_currency=new_currency.getRelativeUrl())
    x_curr_ex_line.setTitle('Euro to Francs CFA')
    x_curr_ex_line.setBasePrice(655.957)
    x_curr_ex_line.setStartDate(DateTime(2008,9,6))
    x_curr_ex_line.setStopDate(DateTime(2008,9,7))
    self.assertEquals(x_curr_ex_line.getPriceCurrencyTitle(),
               'Francs CFA')
    self.assertEquals(x_curr_ex_line.getBasePrice(),655.957)
    x_curr_ex_line.validate()
    self.assertEquals(x_curr_ex_line.getValidationState(),
                               'validated')
    accounting_module = self.portal.accounting_module
    transaction1 = self._makeOne(
               portal_type='Purchase Invoice Transaction',
               stop_date=DateTime('2008/09/08'),
            source_section_value=self.organisation_module.supplier,
            lines=(dict(
               destination_value=self.account_module.goods_purchase,
                           destination_debit=500),
              dict(destination_value=self.account_module.receivable,
                           destination_credit=500)))
    transaction1.AccountingTransaction_convertDestinationPrice(
                              form_id='view')
    line_list = transaction1.contentValues(
           portal_type=self.portal.getPortalAccountingMovementTypeList())
    for line in line_list:
      self.assertEquals(line.getDestinationTotalAssetPrice(),None)
    transaction2 = self._makeOne(
               portal_type='Purchase Invoice Transaction',
               stop_date=DateTime('2008/09/06'),
             source_section_value=self.organisation_module.supplier,
               lines=(dict(
               destination_value=self.account_module.goods_purchase,
                           destination_debit=500),
              dict(destination_value=self.account_module.receivable,
                           destination_credit=500)))
    transaction2.AccountingTransaction_convertDestinationPrice(
                  form_id='view')
    line_list = transaction2.contentValues(
        portal_type=self.portal.getPortalAccountingMovementTypeList())
    for line in line_list:
      if line.getDestinationValue() == self.account_module.goods_purchase:
        self.assertEquals(line.getDestinationInventoriatedTotalAssetDebit(),
                           327979)
      elif line.getDestinationValue() == self.account_module.receivable:
        self.assertEquals(line.getDestinationInventoriatedTotalAssetCredit(),
                           327979)
      else:
        self.fail('line not found')


  def test_CreateCELWithNoReferenceCurrency(self):
    """
      Create a currency exchange line with no reference currency
      and verify that the CEL won't apply for the currency
    """
    self.organisation_module = self.portal.organisation_module
    self.organisation1 = self.organisation_module.my_organisation
    new_currency = self.portal.currency_module.newContent(
               portal_type='Currency')
    new_currency.setReference('XOF')
    new_currency.setTitle('Francs CFA')
    new_currency.setBaseUnitQuantity(1.00)
    self.tic()
    self.organisation1.edit(
            price_currency=new_currency.getRelativeUrl())
    euro = self.portal.currency_module.euro
    x_curr_ex_line = euro.newContent(
                              portal_type='Currency Exchange Line')
    x_curr_ex_line.setTitle('Euro to Francs CFA')
    x_curr_ex_line.setBasePrice(655.957)
    x_curr_ex_line.setStartDate(DateTime(2008,9,8))
    x_curr_ex_line.setStopDate(DateTime(2008,9,10))
    self.assertEquals(x_curr_ex_line.getPriceCurrency(),None)
    self.assertEquals(x_curr_ex_line.getBasePrice(),655.957)
    x_curr_ex_line.validate()
    self.assertEquals(x_curr_ex_line.getValidationState(),
                          'validated')
    
    accounting_module = self.portal.accounting_module
    invoice = self._makeOne(
               portal_type='Purchase Invoice Transaction',
               stop_date=DateTime('2008/09/08'),
             source_section_value=self.organisation_module.supplier,
               lines=(dict(
               destination_value=self.account_module.goods_purchase,
                           destination_debit=500),
              dict(destination_value=self.account_module.receivable,
                           destination_credit=500)))
    
    invoice.AccountingTransaction_convertDestinationPrice(
                           form_id='view')
    line_list = invoice.contentValues(
           portal_type=self.portal.getPortalAccountingMovementTypeList())
    for line in line_list:
        self.assertEquals(line.getDestinationTotalAssetPrice(),
                 None)
  
   
  def test_CreateCELWithNoBasePrice(self):
    """
      Create two currency exchange lines with no base and 
      verify that only one of the CEL will apply for the currency
    """
    self.organisation_module = self.portal.organisation_module
    self.organisation1 = self.organisation_module.my_organisation
    new_currency = self.portal.currency_module.newContent(
                portal_type='Currency')
    new_currency.setReference('XOF')
    new_currency.setTitle('Francs CFA')
    new_currency.setBaseUnitQuantity(1.00)
    self.tic()
    self.organisation1.edit(
               price_currency=new_currency.getRelativeUrl())
    euro = self.portal.currency_module.euro
    
    euro_line1 = euro.newContent(
                              portal_type='Currency Exchange Line',
                       price_currency=new_currency.getRelativeUrl())
    euro_line1.setTitle('Euro to Francs CFA')
    euro_line1.setBasePrice(655.957)
    euro_line1.setStartDate(DateTime(2008,9,8))
    euro_line1.setStopDate(DateTime(2008,9,10))
    self.assertEquals(euro_line1.getPriceCurrencyTitle(),
                            'Francs CFA')
    self.assertEquals(euro_line1.getBasePrice(),655.957)
    euro_line1.validate()
    self.assertEquals(euro_line1.getValidationState(),
                                 'validated')
    euro_line2 = euro.newContent(
                              portal_type='Currency Exchange Line',
                       price_currency=new_currency.getRelativeUrl())
    euro_line2.setTitle('Euro to Francs CFA')
    euro_line2.setStartDate(DateTime(2008,9,8))
    euro_line2.setStopDate(DateTime(2008,9,10))
    self.assertEquals(euro_line2.getPriceCurrencyTitle(),
                            'Francs CFA')
    self.assertEquals(euro_line2.getBasePrice(),None)
    euro_line2.validate()
    
    self.assertEquals(euro_line2.getValidationState(),
                                 'validated')
    accounting_module = self.portal.accounting_module
    invoice = self._makeOne(
               portal_type='Purchase Invoice Transaction',
               stop_date=DateTime('2008/09/08'),
            source_section_value=self.organisation_module.supplier,
               lines=(dict(
               destination_value=self.account_module.goods_purchase,
                           destination_debit=500),
              dict(destination_value=self.account_module.receivable,
                           destination_credit=500)))
    invoice.AccountingTransaction_convertDestinationPrice(
                           form_id='view')
    line_list = invoice.contentValues(
        portal_type=self.portal.getPortalAccountingMovementTypeList())

    for line in line_list:
      if line.getDestinationValue() == self.account_module.goods_purchase:
        self.assertEquals(line.getDestinationInventoriatedTotalAssetDebit(),
                           327979)
      elif line.getDestinationValue() == self.account_module.receivable:
        self.assertEquals(line.getDestinationInventoriatedTotalAssetCredit(),
                           327979)
      else:
        self.fail('line not found')
  
class TestCurrencyExchangeCell(CurrencyExchangeTestCase):
  def afterSetUp(self):
    currency_exchange_type = \
      self.portal.portal_categories.currency_exchange_type
    currency_exchange_type.newContent(
          portal_type='Category',
          id='type_a',
          title='Type A',
          int_index=1)
    currency_exchange_type.newContent(
          portal_type='Category',
          id='type_b',
          title='Type B',
          int_index=2)
    
  def test_CreateCurrencyExchangeCell(self):
    module = self.portal.currency_module
    euro = module.euro
    usd = module.usd
    euro_to_usd = euro.newContent(portal_type='Currency Exchange Line')
    self.assertEquals(0, len(euro_to_usd.contentValues()))
    # when we set the target currency, currency exchange cells will be added
    euro_to_usd.setPriceCurrencyValue(usd)
    self.assertEquals(2, len(euro_to_usd.contentValues()))

    # cell range is like this:
    self.assertEquals([
      ['currency_exchange_type/type_a', 'currency_exchange_type/type_b'],
      ['resource/%s' % euro.getRelativeUrl()],
      ['price_currency/%s' % usd.getRelativeUrl()],
      ], euro_to_usd.getCellRange(base_id='path'))
    
    type_a_cell = euro_to_usd.getCell(
      'currency_exchange_type/type_a',
      'resource/%s' % euro.getRelativeUrl(),
      'price_currency/%s' % usd.getRelativeUrl(),
      base_id='path')
    self.assertNotEquals(None, type_a_cell)
    self.assertEquals('Currency Exchange Cell', type_a_cell.getPortalTypeName())

    # int index have been copied, so that listbox in CurrencyExchangeLine_view
    # displays currency exchange line in same order than int indexes on
    # currency_exchange_type categories.
    self.assertEquals(1, type_a_cell.getIntIndex())
 
    self.assertTrue('currency_exchange_type/type_a' in
        type_a_cell.getCategoryList())
    
    type_a_cell_predicate = type_a_cell.asPredicate()
    self.assertEquals(sorted(('price_currency',
                              'resource',
                              'currency_exchange_type')),
      sorted(type_a_cell_predicate.getMembershipCriterionBaseCategoryList()))

    self.assertEquals(sorted(('price_currency/currency_module/usd',
                              'resource/currency_module/euro',
                              'currency_exchange_type/type_a')),
          sorted(type_a_cell_predicate.getMembershipCriterionCategoryList()))


  def test_ConvertUsingCurrencyExchangeCell(self):
    module = self.portal.currency_module
    euro = module.euro
    usd = module.usd
    euro_to_usd = euro.newContent(portal_type='Currency Exchange Line')
    euro_to_usd.setPriceCurrencyValue(usd)
    euro_to_usd.validate()
  
    type_a_cell = euro_to_usd.getCell(
      'currency_exchange_type/type_a',
      'resource/%s' % euro.getRelativeUrl(),
      'price_currency/%s' % usd.getRelativeUrl(),
      base_id='path')
    type_a_cell.setBasePrice(0.98)

    type_b_cell = euro_to_usd.getCell(
      'currency_exchange_type/type_b',
      'resource/%s' % euro.getRelativeUrl(),
      'price_currency/%s' % usd.getRelativeUrl(),
      base_id='path')
    type_b_cell.setBasePrice(1.24)

    self.tic()

    # we need a base for asContext, we use the currency, but in real code you
    # might want to use a more meaningful context.
    context = euro.asContext(
                    categories=['resource/%s' % euro.getRelativeUrl(),
                                'price_currency/%s' % usd.getRelativeUrl(),
                                'currency_exchange_type/type_a'])

    exchange_ratio = euro.getPrice(context=context,
                                   portal_type='Currency Exchange Cell')
    self.assertEquals(0.98, exchange_ratio)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCurrencyExchangeLine))
  suite.addTest(unittest.makeSuite(TestCurrencyExchangeCell))
  return suite
