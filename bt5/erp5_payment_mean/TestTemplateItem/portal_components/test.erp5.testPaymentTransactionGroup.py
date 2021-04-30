##############################################################################
#
# Copyright (c) 2002-2017 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class TestPaymentTransactionGroup(ERP5TypeTestCase):
  def test_source_reference_generated(self):
    ptg = self.portal.payment_transaction_group_module.newContent(
        portal_type='Payment Transaction Group')
    self.assertTrue(ptg.getSourceReference())

  def test_source_reference_reset_on_clone(self):
    ptg = self.portal.payment_transaction_group_module.newContent(
        portal_type='Payment Transaction Group')
    cloned_ptg = ptg.Base_createCloneDocument(batch_mode=True)
    # after clone, payment transaction group has a source reference
    self.assertTrue(cloned_ptg.getSourceReference())
    # a new source reference
    self.assertNotEqual(
        ptg.getSourceReference(), cloned_ptg.getSourceReference())


class TestPaymentTransactionGroupConstraint(ERP5TypeTestCase):
  def afterSetUp(self):
    ti = self.portal.portal_types['Payment Transaction Group']
    ti.setTypePropertySheetList(
        ti.getTypePropertySheetList() + ['PaymentTransactionGroupConstraint'])
    self.commit()

  def beforeTearDown(self):
    self.abort()
    ti = self.portal.portal_types['Payment Transaction Group']
    ti.setTypePropertySheetList(
        [ps for ps in ti.getTypePropertySheetList() if ps != 'PaymentTransactionGroupConstraint'])
    self.commit()
  
  def test_constraints(self):
    ptg = self.portal.payment_transaction_group_module.newContent(
        portal_type='Payment Transaction Group',
        stop_date=None,
    )
    self.assertEqual(
        sorted([str(m.getMessage()) for m in ptg.checkConsistency()]),
        [
          'Currency must be defined',
          'Date must be defined',
          'Payment Mode must be defined',
          'Payment Transaction Group Type must be defined',
          'Section bank account must be defined',
          'Section must be defined',
        ],
    )

    ptg.setPriceCurrencyValue(
        self.portal.currency_module.newContent(portal_type='Currency'))
    self.assertEqual(
        sorted([str(m.getMessage()) for m in ptg.checkConsistency()]),
        [
          'Date must be defined',
          'Payment Mode must be defined',
          'Payment Transaction Group Type must be defined',
          'Section bank account must be defined',
          'Section must be defined',
        ],
    )

    ptg.setStopDate(DateTime(2021, 1, 1))
    self.assertEqual(
        sorted([str(m.getMessage()) for m in ptg.checkConsistency()]),
        [
          'Payment Mode must be defined',
          'Payment Transaction Group Type must be defined',
          'Section bank account must be defined',
          'Section must be defined',
        ],
    )

    ptg.setPaymentModeValue(
        self.portal.portal_categories.payment_mode.newContent(portal_type='Category'))
    self.assertEqual(
        sorted([str(m.getMessage()) for m in ptg.checkConsistency()]),
        [
          'Payment Transaction Group Type must be defined',
          'Section bank account must be defined',
          'Section must be defined',
        ],
    )

    ptg.setPaymentTransactionGroupTypeValue(
        self.portal.portal_categories.payment_transaction_group_type.incoming)
    self.assertEqual(
        sorted([str(m.getMessage()) for m in ptg.checkConsistency()]),
        [
          'Section bank account must be defined',
          'Section must be defined',
        ],
    )

    section = self.portal.organisation_module.newContent(
        portal_type='Organisation'
    )
    ptg.setSourceSectionValue(section)
    self.assertEqual(
        sorted([str(m.getMessage()) for m in ptg.checkConsistency()]),
        [
          'Section bank account must be defined',
        ],
    )

    bank_account = section.newContent(
        portal_type='Bank Account'
    )
    ptg.setSourcePaymentValue(bank_account)
    self.assertEqual(
        sorted([str(m.getMessage()) for m in ptg.checkConsistency()]),
        [])
