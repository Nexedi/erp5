# -*- coding: utf8 -*-
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
from cStringIO import StringIO
from DateTime import DateTime

from lxml import etree
from AccessControl.SecurityManagement import newSecurityManager

from Products.ERP5.tests.testAccounting import AccountingTestCase

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
    if person_module._getOb('pers', None) is None:
      person = person_module.newContent(id='pers', portal_type='Person',
                                        reference=self.username,
                                        first_name=self.first_name,
                                        default_email_text=self.recipient_email_address)
      assignment = person.newContent(portal_type='Assignment')
      assignment.open()
    self.tic()

    uf = self.portal.acl_users
    uf.zodb_roles.assignRoleToPrincipal('Assignor', self.username)
    user = uf.getUserById(self.username).__of__(uf)
    newSecurityManager(None, user)

  def test_FEC(self):
    account_module = self.portal.account_module
    first = self._makeOne(
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

    second = self._makeOne(
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
    mfrom, mto, message_text = last_message
    self.assertEqual('"%s" <%s>' % (self.first_name, self.recipient_email_address), mto[0])
    mail_message = email.message_from_string(message_text)
    for part in mail_message.walk():
      content_type = part.get_content_type()
      file_name = part.get_filename()
      if file_name == 'FEC-2014.zip':
        self.assertEqual('application/zip', content_type)
        data = part.get_payload(decode=True)
        zf = zipfile.ZipFile(StringIO(data))
        fec_xml = zf.open("FEC.xml").read()
        break
    else:
      self.fail("Attachment not found")

    # validate against official schema
    schema = etree.XMLSchema(etree.XML(open(os.path.join(
        os.path.dirname(__file__), 'test_data',
        'formatA47A-I-VII-1.xsd')).read()))

    # this raise if invalid
    tree = etree.fromstring(fec_xml, etree.XMLParser(schema=schema))

    debit_list = tree.xpath("//Debit")
    self.assertEqual(6, len(debit_list))
    self.assertEqual(372, sum([float(x.text) for x in debit_list]))

    credit_list = tree.xpath("//Credit")
    self.assertEqual(6, len(credit_list))
    self.assertEqual(372, sum([float(x.text) for x in credit_list]))


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestAccounting_l10n_fr))
  return suite

