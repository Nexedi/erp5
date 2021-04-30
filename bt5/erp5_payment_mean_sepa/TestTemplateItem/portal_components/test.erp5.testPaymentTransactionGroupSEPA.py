##############################################################################
#
# Copyright (c) 2021 Nexedi SA and Contributors. All Rights Reserved.
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

from DateTime import DateTime

from erp5.component.test.testAccounting import AccountingTestCase


class TestPaymentTransactionGroupPaymentSEPA(AccountingTestCase):

  def afterSetUp(self):
    AccountingTestCase.afterSetUp(self)
    self.login()
    self.bank_account = self.section.newContent(
        portal_type='Bank Account',
        iban='FR76 3000 6000 0112 3456 7890 189',
        bic_code='TESTXXXX',
        price_currency_value=self.portal.currency_module.euro)
    self.bank_account.validate()
    if 'FR' not in self.portal.portal_categories.region.objectIds():
      self.portal.portal_categories.region.newContent(
        portal_type='Category',
        id='FR',
        title='France',
        reference='FR',
      )
    self.tic()


  def test_PaymentTransactionGroup_viewAsSEPACreditTransferPain_001_001_02(self):
    ptg = self.portal.payment_transaction_group_module.newContent(
        portal_type='Payment Transaction Group',
        source_section_value=self.section,
        source_payment_value=self.bank_account,
        price_currency_value=self.portal.currency_module.euro,
        stop_date=DateTime(2021, 1, 31),
    )

    account_module = self.account_module
    invoice_1 = self._makeOne(
        portal_type='Sale Invoice Transaction',
        reference='INVOICE1'
    )
   
    supplier1 = self.portal.organisation_module.newContent(
        portal_type='Organisation',
        title='Supplier1',
        default_address_street_address='1 rue des pommes',
        default_address_city='LILLE',
        default_address_zip_code='59000',
        default_address_region='FR',        
    )
    bank_account_supplier1 = supplier1.newContent(
        portal_type='Bank Account',
        iban='FI1410093000123458',
        bic_code='TESTXXXX'
    )
    bank_account_supplier1.validate()
    payment_1 = self._makeOne(
        portal_type='Payment Transaction',
        simulation_state='delivered',
        title='one',
        specialise_value=invoice_1,
        source_section_value=self.section,
        source_payment_value=self.bank_account,
        destination_section_value=supplier1,
        destination_payment_value=bank_account_supplier1,
        start_date=DateTime(2021, 1, 1),
        lines=(
            dict(
                source_value=account_module.bank,
                source_debit=100,
                aggregate_value=ptg,
                id='bank'),
            dict(
                source_value=account_module.payable,
                source_credit=100)))

    supplier2 = self.portal.organisation_module.newContent(
        portal_type='Organisation',
        title='Supplier2'
    )
    bank_account_supplier2 = supplier2.newContent(
        portal_type='Bank Account',
        iban='CY21002001950000357001234567',
        bic_code='TESTXXXX'
    )
    bank_account_supplier2.validate()

    payment_2 = self._makeOne(
        portal_type='Payment Transaction',
        simulation_state='delivered',
        title='two',
        destination_section_value=self.section,
        destination_payment_value=self.bank_account,
        source_section_value=supplier2,
        source_payment_value=bank_account_supplier2,
        start_date=DateTime(2021, 1, 2),
        lines=(
            dict(
                destination_value=account_module.bank,
                destination_debit=200,
                aggregate_value=ptg,
                id='bank'),
            dict(
                destination_value=account_module.payable,
                destination_credit=200)))

    self.tic()
    xml = getattr(ptg, 'PaymentTransactionGroup_viewAsSEPACreditTransferPain.001.001.02')()
    self.assertTrue(xml)
    import pdb; pdb.set_trace()
