##############################################################################
# coding: utf-8
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

import six.moves.urllib.parse
import lxml.etree
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

  def _createPTG(self):
    ptg = self.portal.payment_transaction_group_module.newContent(
        portal_type='Payment Transaction Group',
        source_section_value=self.section,
        source_payment_value=self.bank_account,
        price_currency_value=self.portal.currency_module.euro,
        stop_date=DateTime('2021/01/02 03:04:05 Europe/Paris'),
    )
    ptg.open()

    account_module = self.account_module
    invoice_1 = self._makeOne(
        portal_type='Sale Invoice Transaction',
        reference='INVOICE1'
    )

    supplier1 = self.portal.organisation_module.newContent(
        portal_type='Organisation',
        title='Supplier1',
        default_address_street_address='1 rue des pommes\n3ème étage',
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
    self._makeOne(
        portal_type='Payment Transaction',
        simulation_state='delivered',
        title='one',
        reference='PT-1',
        causality_value=invoice_1,
        source_section_value=self.section,
        source_payment_value=self.bank_account,
        destination_section_value=supplier1,
        destination_payment_value=bank_account_supplier1,
        start_date=DateTime(2021, 1, 1),
        lines=(
            dict(
                source_value=account_module.payable,
                source_debit=100),
            dict(
                source_value=account_module.bank,
                source_credit=100,
                aggregate_value=ptg)))

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

    self._makeOne(
        portal_type='Payment Transaction',
        simulation_state='delivered',
        title='two',
        reference='PT-2',
        destination_section_value=self.section,
        destination_payment_value=self.bank_account,
        source_section_value=supplier2,
        source_payment_value=bank_account_supplier2,
        start_date=DateTime(2021, 1, 1),
        lines=(
            dict(
                destination_value=account_module.payable,
                destination_debit=200),
            dict(
                destination_value=account_module.bank,
                destination_credit=200,
                aggregate_value=ptg)))
    self.tic()
    return ptg

  def test_PaymentTransactionGroup_viewAsSEPACreditTransferPain_001_001_02(self):
    ptg = self._createPTG()
    pain = lxml.etree.fromstring(
        getattr(ptg, 'PaymentTransactionGroup_viewAsSEPACreditTransferPain.001.001.02')().encode('utf-8'))

    # this XML validates against the schema
    xmlschema = lxml.etree.XMLSchema(
        lxml.etree.fromstring(str(getattr(self.portal, 'pain.001.001.02.xsd').data)))
    xmlschema.assertValid(pain)

    self.assertEqual(
        [node.text for node in pain.findall('.//{*}GrpHdr/{*}MsgId')],
        [ptg.getSourceReference()],
    )
    self.assertEqual(
        [node.text for node in pain.findall('.//{*}GrpHdr/{*}NbOfTxs')],
        ['2'],
    )
    self.assertEqual(
        [node.text for node in pain.findall('.//{*}GrpHdr/{*}CtrlSum')],
        ['300.00'],
    )

    self.assertEqual(
        [node.text for node in pain.findall('.//{*}CreDtTm')],
        ['2021-01-02T02:04:05+00:00'],
    )

    self.assertEqual(
        [node.text for node in pain.findall('.//{*}InitgPty/{*}Nm')],
        ['My Organisation Inc.'],
    )
    self.assertEqual(
        [node.text for node in pain.findall('.//{*}DbtrAcct/{*}Id/{*}IBAN')],
        ['FR7630006000011234567890189'],
    )

    self.assertEqual(
        sorted([node.text for node in pain.findall('.//{*}CdtTrfTxInf/{*}CdtrAcct/{*}Id/{*}IBAN')]),
        ['CY21002001950000357001234567', 'FI1410093000123458'],
    )
    self.assertEqual(
        sorted([node.text for node in pain.findall('.//{*}CdtTrfTxInf/{*}Amt/{*}InstdAmt')]),
        ['100.00', '200.00'],
    )

    self.assertEqual(
        sorted([node.text for node in pain.findall('.//{*}CdtTrfTxInf/{*}Cdtr/{*}Nm')]),
        ['Supplier1', 'Supplier2'],
    )
    self.assertEqual(
        [node.text for node in pain.findall('.//{*}CdtTrfTxInf/{*}Cdtr/{*}PstlAdr/{*}AdrLine')],
        [u'1 rue des pommes', u'3ème étage', u'59000 LILLE'],
    )

    self.assertEqual(
        sorted([node.text for node in pain.findall('.//{*}CdtTrfTxInf/{*}RmtInf/{*}Ustrd')]),
        ['INVOICE1 Supplier1', 'Supplier2'],
    )

    self.assertEqual(
        sorted([node.text for node in pain.findall('.//{*}CdtTrfTxInf/{*}PmtId/{*}EndToEndId')]),
        ['PT-1', 'PT-2'],
    )

  def test_PaymentTransactionGroup_viewAsSEPACreditTransferPain_001_001_02_with_person(self):
    ptg = self._createPTG()
    person = self.portal.person_module.newContent(
        portal_type='Person',
        first_name='John',
        last_name='Doe',
    )
    bank_account_person = person.newContent(
        portal_type='Bank Account',
        iban='FR4610096000306768831487U66',
        bic_code='TESTXXXX'
    )
    bank_account_person.validate()

    self._makeOne(
        portal_type='Payment Transaction',
        simulation_state='delivered',
        title='three',
        reference='PT-3',
        destination_section_value=self.section,
        destination_payment_value=self.bank_account,
        source_section_value=person,
        source_payment_value=bank_account_person,
        start_date=DateTime(2021, 1, 2),
        lines=(
            dict(
                destination_value=self.portal.account_module.payable,
                destination_debit=300),
            dict(
                destination_value=self.portal.account_module.bank,
                destination_credit=300,
                aggregate_value=ptg)))
    self.tic()
    pain = lxml.etree.fromstring(
        getattr(ptg, 'PaymentTransactionGroup_viewAsSEPACreditTransferPain.001.001.02')().encode('utf-8'))
    xmlschema = lxml.etree.XMLSchema(
        lxml.etree.fromstring(str(getattr(self.portal, 'pain.001.001.02.xsd').data)))
    xmlschema.assertValid(pain)

    self.assertEqual(
        sorted([node.text for node in pain.findall('.//{*}CdtTrfTxInf/{*}Cdtr/{*}Nm')]),
        ['John Doe', 'Supplier1', 'Supplier2'],
    )
    self.assertEqual(
      sorted([node.text for node in pain.findall('.//{*}CdtTrfTxInf/{*}RmtInf/{*}Ustrd')]),
      ['INVOICE1 Supplier1', 'John Doe', 'Supplier2'],
    )

  def test_generate_sepa_credit_transfer_action(self):
    ptg = self._createPTG()
    ret = ptg.PaymentTransactionGroup_generateSEPACreditTransferFile(
      version='pain.001.001.02')
    self.assertEqual(
        six.moves.urllib.parse.parse_qs(six.moves.urllib.parse.urlparse(ret).query)['portal_status_message'],
        ['SEPA Credit Transfer File generated.'])
    self.tic()

    f, = ptg.getFollowUpRelatedValueList(
        portal_type='File',
    )
    self.assertEqual(f.getReference(), ptg.getSourceReference())

    pain = lxml.etree.fromstring(f.getData())

    xmlschema = lxml.etree.XMLSchema(
        lxml.etree.fromstring(str(getattr(self.portal, 'pain.001.001.02.xsd').data)))
    xmlschema.assertValid(pain)

    self.assertEqual(
        [node.text for node in pain.findall('.//{*}GrpHdr/{*}CtrlSum')],
        ['300.00'],
    )

  def test_generate_sepa_credit_transfer_refused_when_activities_are_pending(self):
    ptg = self._createPTG()
    ptg.PaymentTransactionGroup_selectPaymentTransactionLineList(
        select_mode='stopped_or_delivered')
    self.commit()
    ret = ptg.PaymentTransactionGroup_generateSEPACreditTransferFile(
        version='pain.001.001.02')
    self.assertEqual(
        six.moves.urllib.parse.parse_qs(six.moves.urllib.parse.urlparse(ret).query)['portal_status_message'],
        ['Some payments are still beeing processed in the background, please retry later'])
    self.tic()


class TestSEPAConstraints(AccountingTestCase):
  def afterSetUp(self):
    AccountingTestCase.afterSetUp(self)
    ti = self.portal.portal_types['Accounting Transaction Line']
    ti.setTypePropertySheetList(
        ti.getTypePropertySheetList() + ['AccountingTransactionLineSEPACreditTransferConstraint'])
    if 'wire_transfer' not in self.portal.portal_categories.payment_mode.objectIds():
      self.portal.portal_categories.payment_mode.newContent(
          portal_type='Category',
          id='wire_transfer',
          title='Wire Transfer',
      )
    self.portal.portal_preferences.getActiveSystemPreference().setPreferredSepaCreditTransferPaymentMode('wire_transfer')
    self.tic()

  def beforeTearDown(self):
    self.abort()
    ti = self.portal.portal_types['Accounting Transaction Line']
    ti.setTypePropertySheetList(
        [ps for ps in ti.getTypePropertySheetList() if ps != 'AccountingTransactionLineSEPACreditTransferConstraint'])
    self.commit()

  def test_payment_transaction_constraint(self):
    section_bank_account = self.section.newContent(
        portal_type='Bank Account',
        bic_code='X',
        iban='FR76...',
    )
    section_bank_account.validate()
    supplier = self.portal.organisation_module.newContent(
        portal_type='Organisation',
    )
    supplier_bank_account = supplier.newContent(
        portal_type='Bank Account',
    )

    payment_transaction = self._makeOne(
        portal_type='Payment Transaction',
        resource_value=self.currency_module.euro,
        source_section_value=self.section,
        source_payment_value=section_bank_account,
        destination_section_value=supplier,
        start_date=DateTime(2021, 1, 1),
        lines=(
            dict(
                source_value=self.portal.account_module.payable,
                source_debit=100),
            dict(
                source_value=self.portal.account_module.bank,
                source_credit=100)))

    self.assertEqual(
        sorted([str(m.getMessage()) for m in payment_transaction.checkConsistency()]),
        [],
    )
    payment_transaction.setPaymentModeValue(self.portal.portal_categories.payment_mode.wire_transfer)
    self.assertEqual(
        sorted([str(m.getMessage()) for m in payment_transaction.checkConsistency()]),
        ['Bank Accounts must be validated', 'Bank Accounts must have IBAN and BIC', ],
    )

    payment_transaction.setDestinationPaymentValue(supplier_bank_account)
    supplier_bank_account.setBicCode('X')
    supplier_bank_account.setIban('FR76...')
    self.assertEqual(
        sorted([str(m.getMessage()) for m in payment_transaction.checkConsistency()]),
        ['Bank Accounts must be validated', ],
    )
    supplier_bank_account.validate()
    self.assertEqual(
        sorted([str(m.getMessage()) for m in payment_transaction.checkConsistency()]),
        [],
    )

    payment_transaction.setSourcePaymentValue(supplier_bank_account)
    self.assertEqual(
        sorted([str(m.getMessage()) for m in payment_transaction.checkConsistency()]),
        ['Bank Account must belong to Section', ],
    )
    payment_transaction.setSourcePaymentValue(section_bank_account)
    self.assertEqual(
        sorted([str(m.getMessage()) for m in payment_transaction.checkConsistency()]),
        [],
    )
    payment_transaction.setDestinationPaymentValue(section_bank_account)
    self.assertEqual(
        sorted([str(m.getMessage()) for m in payment_transaction.checkConsistency()]),
        ['Bank Account must belong to Section', ],
    )
    payment_transaction.setDestinationPaymentValue(supplier_bank_account)
    self.assertEqual(
        sorted([str(m.getMessage()) for m in payment_transaction.checkConsistency()]),
        [],
    )

    section_bank_account.setIban('')
    self.assertEqual(
        sorted([str(m.getMessage()) for m in payment_transaction.checkConsistency()]),
        ['Bank Accounts must have IBAN and BIC', ],
    )

    section_bank_account.invalidate()
    self.assertEqual(
        sorted([str(m.getMessage()) for m in payment_transaction.checkConsistency()]),
        ['Bank Accounts must be validated', 'Bank Accounts must have IBAN and BIC', ],
    )
