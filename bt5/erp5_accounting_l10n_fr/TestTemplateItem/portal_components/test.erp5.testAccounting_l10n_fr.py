# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Nexedi SA and Contributors. All Rights Reserved.
#                       Jerome Perrin <jerome@nexedi.com>
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

"""Test suite for erp5_accounting_l10n_fr
"""

import unittest
import zipfile
import email
import os.path
from six.moves import cStringIO as StringIO
from DateTime import DateTime

from lxml import etree
from AccessControl.SecurityManagement import newSecurityManager

from erp5.component.test.testAccounting import AccountingTestCase

class TestAccounting_l10n_fr(AccountingTestCase):
  """Test Accounting L10N FR
  """
  username = 'bob'
  first_name = 'Bob <'
  recipient_email_address = 'invalid@example.com'

  def getBusinessTemplateList(self):
    return AccountingTestCase.getBusinessTemplateList(self) + (
        'erp5_deferred_style',
        'erp5_accounting_l10n_fr', )

  def afterSetUp(self):
    AccountingTestCase.afterSetUp(self)
    # set a corporate registration code (siret) on our section organisation
    # > Le numéro SIRET (ou système d'identification du répertoire des
    # > établissements) identifie chaque établissement de l'entreprise.
    # > Il se compose de 14 chiffres : les neuf chiffres du numéro SIREN +
    # > les cinq chiffres correspondant à un numéro NIC (numéro interne de
    # > classement).
    self.section.setCorporateRegistrationCode('12345689 12345')
    # set a french gap on test accounts
    account_module = self.portal.account_module
    account_module.payable.setGap('fr/pcg/4/40/401')
    account_module.refundable_vat.setGap('fr/pcg/4/44/445/4456')
    account_module.goods_purchase.setGap('fr/pcg/6/60/606/6063')
    account_module.receivable.setGap('fr/pcg/4/41/411')
    account_module.goods_sales.setGap('fr/pcg/7/70/706')
    account_module.collected_vat.setGap('fr/pcg/4/44/445/4457/44571')
    account_module.bank.setGap('fr/pcg/5/51/512')
    # and set french gap as preferred
    preference = self.portal.portal_preferences.getActivePreference()
    preference.edit(
      preferred_accounting_transaction_gap='gap/fr/pcg')


  def createUserAndlogin(self, name=username):
    # create a user with an email address
    person_module = self.portal.person_module
    person = person_module._getOb('pers', None)
    if person is None:
      person = person_module.newContent(id='pers', portal_type='Person',
                                        reference=self.username,
                                        first_name=self.first_name,
                                        default_email_text=self.recipient_email_address)
      assignment = person.newContent(portal_type='Assignment')
      assignment.open()
      person.newContent(portal_type='ERP5 Login', reference=self.username).validate()
    self.tic()

    uf = self.portal.acl_users
    uf.zodb_roles.assignRoleToPrincipal('Assignor', person.Person_getUserId())
    user = uf.getUser(self.username).__of__(uf)
    newSecurityManager(None, user)

  def validateFECXML(self, tree):
    # this "xsi:noNamespaceSchemaLocation" is used by xerces parser from
    # https://github.com/DGFiP/Test-Compta-Demat/
    noNamespaceSchemaLocation, = tree.xpath(
      './@xsi:noNamespaceSchemaLocation',
      namespaces={'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})

    import Products.ERP5.tests
    with open(os.path.join(
        os.path.dirname(Products.ERP5.tests.__file__),
        'test_data',
        noNamespaceSchemaLocation,
    )) as f:
      xmlschema_doc = etree.parse(f)
      xmlschema = etree.XMLSchema(xmlschema_doc)

    self.assertFalse(xmlschema.validate(etree.fromstring('<invalide/>')))
    xmlschema.assertValid(tree)

  def getFECFromMailMessage(self):
    last_message = self.portal.MailHost._last_message
    self.assertNotEqual((), last_message)
    _, mto, message_text = last_message
    self.assertEqual('"%s" <%s>' % (self.first_name, self.recipient_email_address), mto[0])
    mail_message = email.message_from_string(message_text)
    for part in mail_message.walk():
      content_type = part.get_content_type()
      file_name = part.get_filename()
      if file_name == 'FEC-20141231.zip':
        self.assertEqual('application/zip', content_type)
        data = part.get_payload(decode=True)
        zf = zipfile.ZipFile(StringIO(data))
        self.assertIn("12345689FEC20141231.xml", zf.namelist())
        return zf.open("12345689FEC20141231.xml").read()
    self.fail("Attachment not found")

  def test_FEC(self):
    account_module = self.portal.account_module
    self._makeOne(
              portal_type='Purchase Invoice Transaction',
              title='Premiere Ecriture',
              simulation_state='delivered',
              reference='1',
              source_section_value=self.organisation_module.supplier,
              stop_date=DateTime(2014, 2, 2),
              lines=(dict(destination_value=account_module.payable,
                          destination_debit=132.00),
                     dict(destination_value=account_module.refundable_vat,
                          destination_credit=22.00),
                     dict(destination_value=account_module.goods_purchase,
                          destination_credit=110.00)))

    self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Seconde Ecriture',
              simulation_state='delivered',
              reference='2',
              destination_section_value=self.organisation_module.client_2,
              start_date=DateTime(2014, 3, 1),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=240.00),
                     dict(source_value=account_module.collected_vat,
                          source_credit=40.00),
                     dict(source_value=account_module.goods_sales,
                          source_credit=200.00)))

    self.portal.accounting_module.AccountingTransactionModule_viewFrenchAccountingTransactionFile(
        section_category='group/demo_group',
        section_category_strict=False,
        at_date=DateTime(2014, 12, 31),
        simulation_state=['delivered'])
    self.tic()

    fec_xml = self.getFECFromMailMessage()

    tree = etree.fromstring(fec_xml)
    self.validateFECXML(tree)

    debit_list = tree.xpath("//Debit")
    self.assertEqual(6, len(debit_list))
    self.assertEqual(372, sum([float(x.text) for x in debit_list]))

    credit_list = tree.xpath("//Credit")
    self.assertEqual(6, len(credit_list))
    self.assertEqual(372, sum([float(x.text) for x in credit_list]))

  def _FECWithLedger(self, ledger_list=None, group_by=None):
    self.setUpLedger()
    account_module = self.portal.account_module
    self._makeOne(
              portal_type='Purchase Invoice Transaction',
              title='Premiere Ecriture',
              simulation_state='delivered',
              ledger='accounting/general',
              reference='1',
              source_section_value=self.organisation_module.supplier,
              stop_date=DateTime(2014, 2, 2),
              lines=(dict(destination_value=account_module.payable,
                          destination_debit=132.00),
                     dict(destination_value=account_module.refundable_vat,
                          destination_credit=22.00),
                     dict(destination_value=account_module.goods_purchase,
                          destination_credit=110.00)))

    self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Seconde Ecriture',
              simulation_state='delivered',
              ledger='accounting/general',
              reference='2',
              destination_section_value=self.organisation_module.client_2,
              start_date=DateTime(2014, 3, 1),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=240.00),
                     dict(source_value=account_module.collected_vat,
                          source_credit=40.00),
                     dict(source_value=account_module.goods_sales,
                          source_credit=200.00)))

    self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Troisieme Ecriture',
              simulation_state='delivered',
              ledger='accounting/detailed',
              reference='3',
              destination_section_value=self.organisation_module.client_2,
              start_date=DateTime(2014, 2, 16),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=185.00),
                     dict(source_value=account_module.collected_vat,
                          source_credit=37.00),
                     dict(source_value=account_module.goods_sales,
                          source_credit=148.00)))
    self.tic()

    self.portal.accounting_module.AccountingTransactionModule_viewFrenchAccountingTransactionFile(
        section_category='group/demo_group',
        section_category_strict=False,
        at_date=DateTime(2014, 12, 31),
        simulation_state=['delivered'],
        group_by=group_by,
        ledger=ledger_list)
    self.tic()

    tree = etree.fromstring(self.getFECFromMailMessage())
    self.validateFECXML(tree)
    return tree

  def test_FECWithOneLedger(self):
    tree = self._FECWithLedger(['accounting/general'])

    # 'Purchase Invoice Transaction' portal_type
    journal_list = tree.xpath("//JournalCode[text()='Purchase Invoice Transaction']/..")
    self.assertEqual(1, len(journal_list))
    journal = journal_list[0]

    ecriture_list = sorted([x.text.encode('utf-8') for x in journal.xpath(".//EcritureLib")])
    self.assertEqual(['Premiere Ecriture'], ecriture_list)

    debit_list = journal.xpath(".//Debit")
    self.assertEqual(3, len(debit_list))
    self.assertEqual(132, sum([float(x.text) for x in debit_list]))

    credit_list = journal.xpath(".//Credit")
    self.assertEqual(3, len(credit_list))
    self.assertEqual(132, sum([float(x.text) for x in credit_list]))

    # 'Sale Invoice Transaction' portal_type
    journal_list = tree.xpath("//JournalCode[text()='Sale Invoice Transaction']/..")
    self.assertEqual(1, len(journal_list))
    journal = journal_list[0]

    ecriture_list = sorted([x.text.encode('utf-8') for x in journal.xpath(".//EcritureLib")])
    self.assertEqual(['Seconde Ecriture'], ecriture_list)

    debit_list = journal.xpath(".//Debit")
    self.assertEqual(3, len(debit_list))
    self.assertEqual(240, sum([float(x.text) for x in debit_list]))

    credit_list = journal.xpath(".//Credit")
    self.assertEqual(3, len(credit_list))
    self.assertEqual(240, sum([float(x.text) for x in credit_list]))

  def test_FECWithMultipleLedger(self):
    # group_by=portal_type by default
    tree = self._FECWithLedger(['accounting/general', 'accounting/detailed'])

    # 'Purchase Invoice Transaction' portal_type
    journal_list = tree.xpath("//JournalCode[text()='Purchase Invoice Transaction']/..")
    self.assertEqual(1, len(journal_list))
    journal = journal_list[0]

    ecriture_list = sorted([x.text.encode('utf-8') for x in journal.xpath(".//EcritureLib")])
    self.assertEqual(['Premiere Ecriture'], ecriture_list)

    debit_list = journal.xpath(".//Debit")
    self.assertEqual(3, len(debit_list))
    self.assertEqual(132, sum([float(x.text) for x in debit_list]))

    credit_list = journal.xpath(".//Credit")
    self.assertEqual(3, len(credit_list))
    self.assertEqual(132, sum([float(x.text) for x in credit_list]))

    # 'Sale Invoice Transaction' portal_type
    journal_list = tree.xpath("//JournalCode[text()='Sale Invoice Transaction']/..")
    self.assertEqual(1, len(journal_list))
    journal = journal_list[0]

    ecriture_list = sorted([x.text.encode('utf-8') for x in journal.xpath(".//EcritureLib")])
    self.assertEqual(['Seconde Ecriture', 'Troisieme Ecriture'], ecriture_list)

    debit_list = journal.xpath(".//Debit")
    self.assertEqual(6, len(debit_list))
    self.assertEqual(425, sum([float(x.text) for x in debit_list]))

    credit_list = journal.xpath(".//Credit")
    self.assertEqual(6, len(credit_list))
    self.assertEqual(425, sum([float(x.text) for x in credit_list]))

  def test_FECWithMultipleLedgerGroupByLedger(self):
    tree = self._FECWithLedger(['accounting/general', 'accounting/detailed'], group_by='ledger')

    # 'accounting/general' ledger
    journal_list = tree.xpath("//JournalCode[text()='general']/..")
    self.assertEqual(1, len(journal_list))
    journal = journal_list[0]

    ecriture_list = sorted([x.text.encode('utf-8') for x in journal.xpath(".//EcritureLib")])
    self.assertEqual(['Premiere Ecriture', 'Seconde Ecriture'], ecriture_list)

    debit_list = journal.xpath(".//Debit")
    self.assertEqual(6, len(debit_list))
    self.assertEqual(372, sum([float(x.text) for x in debit_list]))

    credit_list = journal.xpath(".//Credit")
    self.assertEqual(6, len(credit_list))
    self.assertEqual(372, sum([float(x.text) for x in credit_list]))

    # 'accounting/detailed' ledger
    journal_list = tree.xpath("//JournalCode[text()='detailed']/..")
    self.assertEqual(1, len(journal_list))
    journal = journal_list[0]

    ecriture_list = sorted([x.text.encode('utf-8') for x in journal.xpath(".//EcritureLib")])
    self.assertEqual(['Troisieme Ecriture'], ecriture_list)

    debit_list = journal.xpath(".//Debit")
    self.assertEqual(3, len(debit_list))
    self.assertEqual(185, sum([float(x.text) for x in debit_list]))

    credit_list = journal.xpath(".//Credit")
    self.assertEqual(3, len(credit_list))
    self.assertEqual(185, sum([float(x.text) for x in credit_list]))

  def test_FECWithMultipleLedgerGroupByLedgerAndPortalType(self):
    tree = self._FECWithLedger(['accounting/general', 'accounting/detailed'], group_by='portal_type_ledger')

    # 'Purchase Invoice Transaction' portal_type and 'accounting/general' ledger
    journal_list = tree.xpath("//JournalCode[text()='Purchase Invoice Transaction: general']/..")
    self.assertEqual(1, len(journal_list))
    journal = journal_list[0]

    ecriture_list = sorted([x.text.encode('utf-8') for x in journal.xpath(".//EcritureLib")])
    self.assertEqual(['Premiere Ecriture'], ecriture_list)

    debit_list = journal.xpath(".//Debit")
    self.assertEqual(3, len(debit_list))
    self.assertEqual(132, sum([float(x.text) for x in debit_list]))

    credit_list = journal.xpath(".//Credit")
    self.assertEqual(3, len(credit_list))
    self.assertEqual(132, sum([float(x.text) for x in credit_list]))

    # 'Sale Invoice Transaction' portal_type and 'accounting/general' ledger
    journal_list = tree.xpath("//JournalCode[text()='Sale Invoice Transaction: general']/..")
    self.assertEqual(1, len(journal_list))
    journal = journal_list[0]

    ecriture_list = sorted([x.text.encode('utf-8') for x in journal.xpath(".//EcritureLib")])
    self.assertEqual(['Seconde Ecriture'], ecriture_list)

    debit_list = journal.xpath(".//Debit")
    self.assertEqual(3, len(debit_list))
    self.assertEqual(240, sum([float(x.text) for x in debit_list]))

    credit_list = journal.xpath(".//Credit")
    self.assertEqual(3, len(credit_list))
    self.assertEqual(240, sum([float(x.text) for x in credit_list]))

    # 'Sale Invoice Transaction' portal_type and 'accounting/detailed' ledger
    journal_list = tree.xpath("//JournalCode[text()='Sale Invoice Transaction: detailed']/..")
    self.assertEqual(1, len(journal_list))
    journal = journal_list[0]

    ecriture_list = sorted([x.text.encode('utf-8') for x in journal.xpath(".//EcritureLib")])
    self.assertEqual(['Troisieme Ecriture'], ecriture_list)

    debit_list = journal.xpath(".//Debit")
    self.assertEqual(3, len(debit_list))
    self.assertEqual(185, sum([float(x.text) for x in debit_list]))

    credit_list = journal.xpath(".//Credit")
    self.assertEqual(3, len(credit_list))
    self.assertEqual(185, sum([float(x.text) for x in credit_list]))

  def test_ValidDate(self):
    account_module = self.portal.account_module
    invoice = self._makeOne(
              portal_type='Purchase Invoice Transaction',
              title='Premiere Ecriture',
              simulation_state='delivered',
              reference='1',
              source_section_value=self.organisation_module.supplier,
              stop_date=DateTime(2014, 2, 2),
              lines=(dict(destination_value=account_module.payable,
                          destination_debit=132.00),
                     dict(destination_value=account_module.refundable_vat,
                          destination_credit=22.00),
                     dict(destination_value=account_module.goods_purchase,
                          destination_credit=110.00)))

    assert invoice.workflow_history['accounting_workflow'][-1]['action'] == 'deliver'
    invoice.workflow_history['accounting_workflow'][-1]['time'] = DateTime(2001, 2, 3)

    tree = etree.fromstring(
      invoice.AccountingTransaction_viewAsSourceFECXML(
        test_compta_demat_compatibility=True))
    self.assertEqual(tree.xpath('//ValidDate/text()'), ['2001-02-03'])
    tree = etree.fromstring(
      invoice.AccountingTransaction_viewAsDestinationFECXML(
        test_compta_demat_compatibility=True))
    self.assertEqual(tree.xpath('//ValidDate/text()'), ['2001-02-03'])

  def test_EscapeTestComptaDematUnsupportedCharacters(self):
    # Workaround bugs with Test Compta Demat
    # https://github.com/DGFiP/Test-Compta-Demat/issues/37
    # https://github.com/DGFiP/Test-Compta-Demat/issues/39

    account_module = self.portal.account_module
    self._makeOne(
      portal_type='Purchase Invoice Transaction',
      title='Le libéllé c’est çà: œufs, des Œufs, des Ÿ et des €',
      simulation_state='delivered',
      reference='1',
      source_section_value=self.organisation_module.supplier,
      stop_date=DateTime(2014, 2, 2),
      lines=(
        dict(
          destination_value=account_module.payable, destination_debit=132.00),
        dict(
          destination_value=account_module.refundable_vat,
          destination_credit=22.00),
        dict(
          destination_value=account_module.goods_purchase,
          destination_credit=110.00)))
    self.tic()
    self.portal.accounting_module.AccountingTransactionModule_viewFrenchAccountingTransactionFile(
      section_category='group/demo_group',
      section_category_strict=False,
      at_date=DateTime(2014, 12, 31),
      simulation_state=['delivered'])
    self.tic()

    tree = etree.fromstring(self.getFECFromMailMessage())
    self.validateFECXML(tree)
    self.assertEqual(
      tree.xpath('//EcritureLib/text()'),
      [u'Le libelle cest ca: ufs, des ufs, des Y et des EUR'])

  def test_Skip0QuantityLines(self):
    # Don't include lines with 0 quantity in the output, because they are
    # reported as invalid by Test Compta Demat
    account_module = self.portal.account_module
    destination_invoice = self._makeOne(
      portal_type='Purchase Invoice Transaction',
      title='destination 0',
      simulation_state='delivered',
      reference='destination',
      source_section_value=self.organisation_module.supplier,
      stop_date=DateTime(2014, 2, 2),
      lines=(
        dict(
          destination_value=account_module.payable, destination_debit=132.00),
        dict(
          destination_value=account_module.payable,
          destination_debit=10000.00,
          destination_asset_debit=0.00),
        dict(
          destination_value=account_module.refundable_vat,
          destination_credit=22.00),
        dict(
          destination_value=account_module.refundable_vat,
          destination_credit=0.00),
        dict(
          destination_value=account_module.goods_purchase,
          destination_credit=110.00)))

    self._makeOne(
      portal_type='Sale Invoice Transaction',
      title='source 0',
      simulation_state='delivered',
      reference='source',
      destination_section_value=self.organisation_module.client_2,
      start_date=DateTime(2014, 3, 1),
      lines=(
        dict(source_value=account_module.receivable, source_debit=240.00),
        dict(
          source_value=account_module.collected_vat,
          source_credit=10000.00,
          source_asset_credit=0.00),
        dict(source_value=account_module.collected_vat, source_credit=0.00),
        dict(source_value=account_module.collected_vat, source_credit=40.00),
        dict(source_value=account_module.goods_sales, source_credit=200.00)))

    self.tic()
    # make sure we don't have interaction removing the lines
    self.assertEqual(
      sorted(
        [
          (line.getDestinationDebit(), line.getSourceDebit())
          for line in destination_invoice.contentValues()
        ]), [
          (0.0, 0.0),
          (0.0, 22.0),
          (0.0, 110.0),
          (132.0, 0.0),
          (10000.0, 0.0),
        ])
    self.portal.accounting_module.AccountingTransactionModule_viewFrenchAccountingTransactionFile(
      section_category='group/demo_group',
      section_category_strict=False,
      at_date=DateTime(2014, 12, 31),
      simulation_state=['delivered'])
    self.tic()

    tree = etree.fromstring(self.getFECFromMailMessage())
    self.validateFECXML(tree)
    self.assertEqual(
      tree.xpath(
        '//ecriture/PieceRef[text()="destination"]/../ligne/Debit/text()'),
      ['132.00', '0.00', '0.00'])
    self.assertEqual(
      tree.xpath(
        '//ecriture/PieceRef[text()="destination"]/../ligne/Credit/text()'),
      ['0.00', '22.00', '110.00'])
    self.assertEqual(
      tree.xpath('//ecriture/PieceRef[text()="source"]/../ligne/Debit/text()'),
      ['240.00', '0.00', '0.00'])
    self.assertEqual(
      tree.xpath(
        '//ecriture/PieceRef[text()="source"]/../ligne/Credit/text()'),
      ['0.00', '40.00', '200.00'])

  def test_PieceRefDefaultValue(self):
    account_module = self.portal.account_module
    invoice = self._makeOne(
      portal_type='Purchase Invoice Transaction',
      title='Premiere Ecriture',
      simulation_state='delivered',
      source_section_value=self.organisation_module.supplier,
      stop_date=DateTime(2014, 2, 2),
      lines=(
        dict(
          destination_value=account_module.payable, destination_debit=132.00),
        dict(
          destination_value=account_module.refundable_vat,
          destination_credit=22.00),
        dict(
          destination_value=account_module.goods_purchase,
          destination_credit=110.00)))

    invoice.setSourceReference('source_reference')
    invoice.setDestinationReference('destination_reference')
    tree = etree.fromstring(
      invoice.AccountingTransaction_viewAsSourceFECXML(
        test_compta_demat_compatibility=True))
    self.assertEqual(tree.xpath('//EcritureNum/text()'), ['source_reference'])
    self.assertEqual(tree.xpath('//PieceRef/text()'), ['source_reference'])
    tree = etree.fromstring(
      invoice.AccountingTransaction_viewAsDestinationFECXML(
        test_compta_demat_compatibility=True))
    self.assertEqual(
      tree.xpath('//EcritureNum/text()'), ['destination_reference'])
    self.assertEqual(
      tree.xpath('//PieceRef/text()'), ['destination_reference'])

    tree = etree.fromstring(
      invoice.AccountingTransaction_viewAsSourceFECXML(
        test_compta_demat_compatibility=False))
    self.assertEqual(tree.xpath('//EcritureNum/text()'), ['source_reference'])
    self.assertEqual([n.text for n in tree.xpath('//PieceRef')], [None])
    tree = etree.fromstring(
      invoice.AccountingTransaction_viewAsDestinationFECXML(
        test_compta_demat_compatibility=False))
    self.assertEqual(
      tree.xpath('//EcritureNum/text()'), ['destination_reference'])
    self.assertEqual([n.text for n in tree.xpath('//PieceRef')], [None])

  def test_AssetPriceAndQuantityEdgeCase(self):
    # Edge case where we have an asset price and quantity of reverse sides.
    account_module = self.portal.account_module
    self._makeOne(
      portal_type='Purchase Invoice Transaction',
      title='destination 0',
      simulation_state='delivered',
      reference='destination',
      source_section_value=self.organisation_module.supplier,
      stop_date=DateTime(2014, 2, 2),
      lines=(
        dict(
          destination_value=account_module.payable,
          destination_debit=100,
          destination_asset_credit=123,
        ),
        dict(
          destination_value=account_module.goods_purchase,
          destination_credit=100,
          destination_asset_debit=123,
        )))

    self._makeOne(
      portal_type='Sale Invoice Transaction',
      title='source 0',
      simulation_state='delivered',
      reference='source',
      destination_section_value=self.organisation_module.client_2,
      start_date=DateTime(2014, 3, 1),
      lines=(
        dict(
          source_value=account_module.receivable,
          source_debit=200.00,
          source_asset_debit=345,
        ),
        dict(
          source_value=account_module.goods_sales,
          source_credit=200.00,
          source_asset_credit=345,
        )))

    self.tic()
    self.portal.accounting_module.AccountingTransactionModule_viewFrenchAccountingTransactionFile(
      section_category='group/demo_group',
      section_category_strict=False,
      at_date=DateTime(2014, 12, 31),
      simulation_state=['delivered'])
    self.tic()

    tree = etree.fromstring(self.getFECFromMailMessage())
    self.validateFECXML(tree)
    self.assertEqual(
      tree.xpath('//ecriture/PieceRef[text()="destination"]/../ligne/Debit/text()'),
      ['0.00', '123.00'])
    self.assertEqual(
      tree.xpath(
        '//ecriture/PieceRef[text()="destination"]/../ligne/Credit/text()'),
      ['123.00', '0.00'])
    self.assertEqual(
      tree.xpath('//ecriture/PieceRef[text()="source"]/../ligne/Debit/text()'),
      ['345.00', '0.00'])
    self.assertEqual(
      tree.xpath(
        '//ecriture/PieceRef[text()="source"]/../ligne/Credit/text()'),
      ['0.00', '345.00'])


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestAccounting_l10n_fr))
  return suite
