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
from io import StringIO
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

  def test_FEC(self):
    account_module = self.portal.account_module
    self._makeOne(
              portal_type='Purchase Invoice Transaction',
              title='Première Écriture',
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
              title='Seconde Écriture',
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

    fec_xml = ''
    last_message = self.portal.MailHost._last_message
    self.assertNotEquals((), last_message)
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
        fec_xml = zf.open("FEC.xml").read()
        break
    else:
      self.fail("Attachment not found")

    # validate against official schema
    import Products.ERP5.tests
    schema = etree.XMLSchema(etree.XML(open(os.path.join(
        os.path.dirname(Products.ERP5.tests.__file__), 'test_data',
        'formatA47A-I-VII-1.xsd')).read()))

    # this raise if invalid
    tree = etree.fromstring(fec_xml, etree.XMLParser(schema=schema))

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
              title='Première Écriture',
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
              title='Seconde Écriture',
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
              title='Troisième Écriture',
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

    fec_xml = ''
    last_message = self.portal.MailHost._last_message
    self.assertNotEquals((), last_message)
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
        fec_xml = zf.open("FEC.xml").read()
        break
    else:
      self.fail("Attachment not found")

    # validate against official schema
    import Products.ERP5.tests
    schema = etree.XMLSchema(etree.XML(open(os.path.join(
        os.path.dirname(Products.ERP5.tests.__file__), 'test_data',
        'formatA47A-I-VII-1.xsd')).read()))

    # this raise if invalid
    tree = etree.fromstring(fec_xml, etree.XMLParser(schema=schema))

    return tree

  def test_FECWithOneLedger(self):
    tree = self._FECWithLedger(['accounting/general'])

    # 'Purchase Invoice Transaction' portal_type
    journal_list = tree.xpath("//JournalCode[text()='Purchase Invoice Transaction']/..")
    self.assertEqual(1, len(journal_list))
    journal = journal_list[0]

    ecriture_list = sorted([x.text.encode('utf-8') for x in journal.xpath(".//EcritureLib")])
    self.assertEqual(['Première Écriture'], ecriture_list)

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
    self.assertEqual(['Seconde Écriture'], ecriture_list)

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
    self.assertEqual(['Première Écriture'], ecriture_list)

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
    self.assertEqual(['Seconde Écriture', 'Troisième Écriture'], ecriture_list)

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
    self.assertEqual(['Première Écriture', 'Seconde Écriture'], ecriture_list)

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
    self.assertEqual(['Troisième Écriture'], ecriture_list)

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
    self.assertEqual(['Première Écriture'], ecriture_list)

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
    self.assertEqual(['Seconde Écriture'], ecriture_list)

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
    self.assertEqual(['Troisième Écriture'], ecriture_list)

    debit_list = journal.xpath(".//Debit")
    self.assertEqual(3, len(debit_list))
    self.assertEqual(185, sum([float(x.text) for x in debit_list]))

    credit_list = journal.xpath(".//Credit")
    self.assertEqual(3, len(credit_list))
    self.assertEqual(185, sum([float(x.text) for x in credit_list]))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestAccounting_l10n_fr))
  return suite

