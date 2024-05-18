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

import six.moves.urllib.parse
from DateTime import DateTime

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from erp5.component.test.testAccounting import AccountingTestCase


class TestPaymentTransactionGroupReferences(ERP5TypeTestCase):
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


class TestPaymentTransactionGroupWorkflow(ERP5TypeTestCase):
  def test_workflow_transitions(self):
    ptg = self.portal.payment_transaction_group_module.newContent(
        portal_type='Payment Transaction Group')
    self.assertEqual(ptg.getValidationState(), 'draft')
    self.portal.portal_workflow.doActionFor(ptg, 'open_action')
    self.assertEqual(ptg.getValidationState(), 'open')
    self.portal.portal_workflow.doActionFor(ptg, 'close_action')
    self.assertEqual(ptg.getValidationState(), 'closed')
    self.portal.portal_workflow.doActionFor(ptg, 'deliver_action')
    self.assertEqual(ptg.getValidationState(), 'delivered')


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


class TestRemoveFromPaymentTransactionGroup(AccountingTestCase):
  def afterSetUp(self):
    AccountingTestCase.afterSetUp(self)
    self.bank_account = self.main_section.newContent(
        portal_type='Bank Account',
        price_currency_value=self.portal.currency_module.euro)
    self.bank_account.validate()
    self.tic()

  def test_other_item_types(self):
    account_module = self.account_module
    payment = self._makeOne(
        portal_type='Payment Transaction',
        source_section_value=self.main_section,
        source_payment_value=self.bank_account,
        destination_section_value=self.organisation_module.client_1,
        start_date=DateTime(2014, 1, 1),
        lines=(
            dict(
                source_value=account_module.bank,
                source_debit=100,
                id='bank'),
            dict(
                source_value=account_module.receivable,
                source_credit=100)))
    self.tic()
    self.assertFalse(payment.getReference())

    ptg = self.portal.payment_transaction_group_module.newContent(
        portal_type='Payment Transaction Group',
        source_section_value=self.main_section,
        source_payment_value=self.bank_account,
        stop_date=DateTime(2014, 1, 31),)
    self.tic()
    item = self.portal.item_module.newContent(portal_type='Item')
    payment.bank.setAggregateValueList([ptg, item])
    self.tic()
    payment.PaymentTransaction_removeFromPaymentTransactionGroup()
    self.tic()
    self.assertEqual(
        payment.bank.getAggregateValueList(),
        [item])


class TestPaymentTransactionGroupPaymentSelection(AccountingTestCase):

  def afterSetUp(self):
    AccountingTestCase.afterSetUp(self)
    self.bank_account = self.main_section.newContent(
        portal_type='Bank Account',
        price_currency_value=self.portal.currency_module.euro)
    self.bank_account.validate()
    self.tic()

  # TODO: more PaymentTransactionGroup_getGroupablePaymentTransactionLineList test

  def test_PaymentTransactionGroup_getGroupablePaymentTransactionLineList_mapping_organisation(self):
    account_module = self.account_module
    payment_main_section = self._makeOne(
        portal_type='Payment Transaction',
        simulation_state='delivered',
        title='main section',
        reference='P1',
        source_section_value=self.main_section,
        source_payment_value=self.bank_account,
        destination_section_value=self.organisation_module.client_1,
        start_date=DateTime(2014, 1, 1),
        lines=(
            dict(
                source_value=account_module.bank,
                source_debit=100,
                id='bank'),
            dict(
                source_value=account_module.receivable,
                source_credit=100)))

    payment_section = self._makeOne(
        portal_type='Payment Transaction',
        simulation_state='delivered',
        title='section',
        reference='P2',
        source_section_value=self.section,
        source_payment_value=self.bank_account,
        destination_section_value=self.organisation_module.client_2,
        start_date=DateTime(2014, 1, 2),
        lines=(
            dict(
                source_value=account_module.bank,
                source_debit=200,
                id='bank'),
            dict(
                source_value=account_module.receivable,
                source_credit=200)))

    ptg = self.portal.payment_transaction_group_module.newContent(
        portal_type='Payment Transaction Group',
        source_section_value=self.main_section,
        source_payment_value=self.bank_account,
        stop_date=DateTime(2014, 1, 31),)
    self.tic()

    line_list = ptg.PaymentTransactionGroup_getGroupablePaymentTransactionLineList(
        limit=None,
        start_date_range_min=None,
        start_date_range_max=None,
        sign='incoming',
        select_mode='stopped_or_delivered',
    )
    self.assertEqual(
        sorted([line.getObject().getRelativeUrl() for line in line_list]),
        sorted([payment_main_section.bank.getRelativeUrl(), payment_section.bank.getRelativeUrl()]))

    # Add a payment to the group
    payment_section.bank.setAggregateValue(ptg)
    self.tic()
    # Now the listbox only remaining transactions
    line_list = ptg.PaymentTransactionGroup_getGroupablePaymentTransactionLineList(
        limit=None,
        start_date_range_min=None,
        start_date_range_max=None,
        sign='incoming',
        select_mode='stopped_or_delivered',
    )
    self.assertEqual(
        sorted([line.getObject().getRelativeUrl() for line in line_list]),
        sorted([payment_main_section.bank.getRelativeUrl()]))

    # Add the other payment to the group
    payment_main_section.bank.setAggregateValue(ptg)
    self.tic()
    # the listbox of the payment transaction group correctly show both payments.
    line_list = ptg.PaymentTransactionGroup_view.listbox.get_value(
        'default',
        render_format='list',)
    self.assertEqual(
        sorted([(line.is_stat_line, line['Movement_getMirrorSectionTitle'], line['total_quantity'])
                 for line in line_list if not line.is_title_line]),
        [(0, 'Client 1', 100.0), (0, 'Client 2', 200.0), (1, None, 300.0)],
    )

  def test_adding_to_payment_transaction_set_reference(self):
    account_module = self.account_module
    payment = self._makeOne(
        portal_type='Payment Transaction',
        simulation_state='delivered',
        source_section_value=self.main_section,
        source_payment_value=self.bank_account,
        payment_mode_value=self.portal.portal_categories.payment_mode.cash,
        resource_value=self.portal.currency_module.euro,
        destination_section_value=self.organisation_module.client_1,
        start_date=DateTime(2014, 1, 1),
        lines=(
            dict(
                source_value=account_module.bank,
                source_debit=100,
                id='bank'),
            dict(
                source_value=account_module.receivable,
                source_credit=100)))
    self.tic()
    self.assertFalse(payment.getReference())

    ptg = self.portal.payment_transaction_group_module.newContent(
        portal_type='Payment Transaction Group',
        source_section_value=self.main_section,
        source_payment_value=self.bank_account,
        payment_mode_value=self.portal.portal_categories.payment_mode.cash,
        price_currency_value=self.portal.currency_module.euro,
        stop_date=DateTime(2014, 1, 31),)
    self.tic()
    ptg.PaymentTransactionGroup_selectPaymentTransactionLineList(select_mode='stopped_or_delivered')
    self.tic()
    self.assertEqual(
        payment.bank.getAggregateValueList(),
        [ptg])
    self.assertTrue(payment.getReference())

  def test_select_payment_transaction_refused_when_activities_are_running(self):
    ptg1 = self.portal.payment_transaction_group_module.newContent(
        portal_type='Payment Transaction Group',)
    ptg2 = self.portal.payment_transaction_group_module.newContent(
        portal_type='Payment Transaction Group',)
    self.tic()
    ret = ptg1.PaymentTransactionGroup_selectPaymentTransactionLineList(select_mode='stopped_or_delivered')
    self.assertEqual(
        six.moves.urllib.parse.parse_qs(six.moves.urllib.parse.urlparse(ret).query)['portal_status_message'],
        ['Payment selection in progress.'])
    self.commit()
    ret = ptg1.PaymentTransactionGroup_selectPaymentTransactionLineList(select_mode='stopped_or_delivered')
    self.assertEqual(
        six.moves.urllib.parse.parse_qs(six.moves.urllib.parse.urlparse(ret).query)['portal_status_message'],
        ['Some payments are still beeing processed in the background, please retry later'])
    self.commit()
    # another PTG is same, because we also want to prevent things like two users selecting
    # payments at the same time.
    ret = ptg2.PaymentTransactionGroup_selectPaymentTransactionLineList(select_mode='stopped_or_delivered')
    self.assertEqual(
        six.moves.urllib.parse.parse_qs(six.moves.urllib.parse.urlparse(ret).query)['portal_status_message'],
        ['Some payments are still beeing processed in the background, please retry later'])
