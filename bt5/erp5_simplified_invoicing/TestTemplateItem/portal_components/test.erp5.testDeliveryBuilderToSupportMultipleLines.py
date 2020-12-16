# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import unittest
from unittest import expectedFailure
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.tests.utils import createZODBPythonScript
from erp5.component.module.TestInvoiceMixin import TestSaleInvoiceMixin
from Products.ERP5.tests.utils import newSimulationExpectedFailure

class TestNestedLineMixin(TestSaleInvoiceMixin):

  """
  NestedLineMovementGroup is a mark only for controlling multiple lines in DeliveryBuilder.
  We need this feature to make multi-level "Invoice Line"s.
  """

  DEFAULT_SEQUENCE = TestSaleInvoiceMixin.PACKING_LIST_DEFAULT_SEQUENCE + \
    """
      stepSetReadyPackingList
      stepTic
      stepUpdateBuilderForMultipleLineList
      stepSetPythonScriptForDeliveryBuilder
      stepStartPackingList
      stepCheckInvoicingRule
      stepTic
      stepInvoiceBuilderAlarm
      stepTic
      stepGetRelatedInvoiceFromPackingList
    """
  delivery_builder_id = 'sale_invoice_builder'
  default_quantity = TestSaleInvoiceMixin.default_quantity
  new_order_quantity = TestSaleInvoiceMixin.default_quantity * 3
  new_packing_list_quantity = TestSaleInvoiceMixin.default_quantity * 5
  new_invoice_quantity = TestSaleInvoiceMixin.default_quantity * 2

  def afterSetUp(self):
    TestSaleInvoiceMixin.afterSetUp(self)
    # Necessary to allow Invoice Line to be included in Invoice Line.
    self.allowInvoiceLineContentTypeInInvoiceLine()

  @UnrestrictedMethod
  def allowInvoiceLineContentTypeInInvoiceLine(self):
    invoice_line_type = self.portal.portal_types['Invoice Line']
    content_type_set = set(invoice_line_type.getTypeAllowedContentTypeList())
    content_type_set.add('Invoice Line')
    invoice_line_type._setTypeAllowedContentTypeList(tuple(content_type_set))

  def stepGetRelatedInvoiceFromPackingList(self, sequence, **kw):
    packing_list = sequence.get('packing_list')
    related_invoice_list = packing_list \
      .getCausalityRelatedValueList(portal_type=self.invoice_portal_type)
    invoice = related_invoice_list[0].getObject()
    sequence.edit(invoice=invoice)

  def stepUpdateBuilderForMultipleLineList(self, **kw):
    self.updateBuilderForMultipleLineList()

  @UnrestrictedMethod
  def updateBuilderForMultipleLineList(self):
    delivery_builder = getattr(self.portal.portal_deliveries, self.delivery_builder_id)

    delivery_builder.deleteContent(delivery_builder.contentIds())
    delivery_builder.newContent(
      portal_type='Property Movement Group',
      collect_order_group='delivery',
      divergence_scope='property',
      tested_property_list=('start_date', 'stop_date'),
      int_index=1)
    delivery_builder.newContent(
      portal_type='Category Movement Group',
      collect_order_group='delivery',
      divergence_scope='category',
      tested_property_list=('specialise',
                            'delivery_mode',
                            'incoterm',
                            'source',
                            'destination',
                            'source_section',
                            'destination_section',
                            'destination_function',
                            'source_function',
                            'source_decision',
                            'destination_decision',
                            'source_administration',
                            'destination_administration',
                            'source_project',
                            'destination_project',
                            'source_payment',
                            'destination_payment',
                            'price_currency'),
      int_index=2)
    delivery_builder.newContent(
      portal_type='Delivery Causality Assignment Movement Group',
      collect_order_group='delivery',
      int_index=3)
    delivery_builder.newContent(
      portal_type='Property Movement Group',
      collect_order_group='line',
      divergence_scope='property',
      tested_property_list=('start_date', 'stop_date'),
      int_index=1)
    # *** test this ***
    delivery_builder.newContent(
      portal_type='Nested Line Movement Group',
      collect_order_group='line',
      int_index=2)
    delivery_builder.newContent(
      portal_type='Category Movement Group',
      collect_order_group='line',
      divergence_scope='category',
      tested_property_list=('resource', 'aggregate', 'base_contribution'),
      int_index=3)
    delivery_builder.newContent(
      portal_type='Base Variant Movement Group',
      collect_order_group='line',
      int_index=4)
    delivery_builder.newContent(
      portal_type='Property Movement Group',
      collect_order_group='line',
      divergence_scope='property',
      tested_property_list=('description'),
      int_index=5)
    delivery_builder.newContent(
      portal_type='Variant Movement Group',
      collect_order_group='cell',
      divergence_scope='category',
      int_index=1)

  def stepSetExistDeliveriesToSequence(self, sequence=None, **kw):
    order = self.portal.sale_order_module.contentValues(portal_type='Sale Order')[0]
    packing_list = self.portal.sale_packing_list_module \
      .contentValues(portal_type='Sale Packing List')[0]
    invoice = self.portal.accounting_module \
      .contentValues(portal_type='Sale Invoice Transaction')[0]
    sequence.edit(order=order, packing_list=packing_list, invoice=invoice)

  def stepUpdateOrder(self, sequence=None, **kw):
    movement = sequence.get('order').getMovementList(portal_type='Sale Order Line')[0]
    movement.edit(quantity=self.new_order_quantity,
                  price=self.default_price)

  def stepUpdatePackingList(self, sequence=None, **kw):
    movement = sequence.get('packing_list') \
               .getMovementList(portal_type='Sale Packing List Line')[0]
    movement.edit(quantity=self.new_packing_list_quantity)

  def stepSetFillContainerLine(self, sequence=None, **kw):
    movement = sequence.get('container_line')
    movement.edit(quantity=self.new_order_quantity)

  def stepUpdateInvoice(self, sequence=None, **kw):
    movement = sequence.get('invoice') \
      .getMovementList(portal_type='Invoice Line')[0]
    movement.edit(quantity=self.new_invoice_quantity)

  def stepSetPythonScriptForDeliveryBuilder(self, **kw):
    """
    Make a script which returns existing Sale Invoice Transactions,
    so that all movements are merged into existing ones.
    """
    delivery_select_method_id = 'Test_selectDelivery'
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      delivery_select_method_id,
      'movement_list=None',
      """
return context.getPortalObject().portal_catalog(portal_type='Sale Invoice Transaction')
""")
    delivery_builder = getattr(self.portal.portal_deliveries, self.delivery_builder_id)
    delivery_builder.delivery_select_method_id = delivery_select_method_id

  def stepSetSeparateMethodToDeliveryBuilder(self, **kw):
    """
    Merge multiple simulation movements into one movement.
    """
    delivery_builder = getattr(self.portal.portal_deliveries, self.delivery_builder_id)
    delivery_builder.delivery_cell_separate_order = ('calculateAddQuantity',)

  stepAdoptPrevisionPackingListQuantity = \
    TestSaleInvoiceMixin.stepAdoptPrevisionQuantity

  stepAcceptDecisionPackingListQuantity = \
    TestSaleInvoiceMixin.stepAcceptDecisionQuantity

  stepAdoptPrevisionInvoiceQuantity = \
    TestSaleInvoiceMixin.stepAdoptPrevisionQuantityInvoice

  stepAcceptDecisionInvoiceQuantity = \
    TestSaleInvoiceMixin.stepAcceptDecisionQuantityInvoice


class TestNestedLine(TestNestedLineMixin, ERP5TypeTestCase):

  quiet = 0

  def test_01_IfNested(self, quiet=quiet):
    sequence_list = SequenceList()
    sequence = sequence_list.addSequenceString(self.DEFAULT_SEQUENCE)
    sequence_list.play(self, quiet=quiet)

    # order = sequence.get('order')
    # packing_list = sequence.get('packing_list')
    document = sequence.get('invoice')
    self.assertEqual('Sale Invoice Transaction', document.getPortalType())
    line_list = document.objectValues(
      portal_type=self.portal.getPortalInvoiceMovementTypeList())
    self.assertEqual(1, len(line_list))

    line = line_list[0]
    self.assertEqual('Invoice Line', line.getPortalType())
    self.assertEqual(None, line.getQuantity(None))
    self.assertEqual(1, len(line))

    line_line = line.objectValues()[0]
    self.assertEqual('Invoice Line', line_line.getPortalType())

    self.assertEqual(self.default_price * self.default_quantity, document.getTotalPrice())
    self.assertEqual(self.default_quantity, document.getTotalQuantity())
    self.assertEqual(self.default_price, line_line.getPrice())
    self.assertEqual(self.default_quantity, line_line.getQuantity())


  def test_02_AdoptingPrevision(self, quiet=quiet):
    sequence_list = SequenceList()
    sequence = sequence_list.addSequenceString(self.DEFAULT_SEQUENCE + \
    """
      stepUpdatePackingList
      stepTic

      stepAcceptDecisionPackingListQuantity
      stepTic

      stepCheckInvoiceIsDivergent
      stepCheckInvoiceIsDiverged
      stepAdoptPrevisionInvoiceQuantity
      stepTic
    """
    )
    sequence_list.play(self, quiet=quiet)

    document = sequence.get('invoice')
    self.assertEqual('solved', document.getCausalityState())
    line_list = document.objectValues(
      portal_type=self.portal.getPortalInvoiceMovementTypeList())
    self.assertEqual(1, len(line_list))

    line = line_list[0]
    self.assertEqual('Invoice Line', line.getPortalType())
    self.assertEqual(None, line.getQuantity(None))
    self.assertEqual(1, len(line))

    line_line = line.objectValues()[0]
    self.assertEqual('Invoice Line', line_line.getPortalType())

    self.assertEqual(self.default_price * self.new_packing_list_quantity, document.getTotalPrice())
    self.assertEqual(self.new_packing_list_quantity, document.getTotalQuantity())
    self.assertEqual(self.new_packing_list_quantity, line_line.getQuantity())

  @newSimulationExpectedFailure
  def test_03_AcceptingDecision(self, quiet=quiet):
    sequence_list = SequenceList()
    sequence = sequence_list.addSequenceString(self.DEFAULT_SEQUENCE + \
    """
      stepUpdateInvoice
      stepTic

      stepCheckInvoiceIsDivergent
      stepAcceptDecisionInvoiceQuantity
      stepTic

      stepCheckInvoiceIsNotDivergent
      stepCheckPackingListIsDivergent
      stepAdoptPrevisionPackingListQuantity
      stepTic
    """
    )
    sequence_list.play(self, quiet=quiet)

    document = sequence.get('invoice')

    self.assertEqual('solved', document.getCausalityState())
    line_list = document.objectValues(
      portal_type=self.portal.getPortalInvoiceMovementTypeList())
    self.assertEqual(1, len(line_list))

    line = line_list[0]
    self.assertEqual('Invoice Line', line.getPortalType())
    self.assertEqual(None, line.getQuantity(None))
    self.assertEqual(1, len(line))

    line_line = line.objectValues()[0]
    self.assertEqual('Invoice Line', line_line.getPortalType())

    self.assertEqual(self.default_price * self.new_invoice_quantity, document.getTotalPrice())
    self.assertEqual(self.new_invoice_quantity, document.getTotalQuantity())
    self.assertEqual(self.new_invoice_quantity, line_line.getQuantity())

  def stepPrioritizeInvoiceUpdateCausalityStateTic(self, sequence):
    invoice = sequence['invoice']
    invoice_path = invoice.getPhysicalPath()
    prioritize_uid_list = []
    def stop_condition(message_list):
      for message in message_list:
        if (message.object_path == invoice_path and
            message.method_id == 'updateCausalityState'):
          prioritize_uid_list.append(message.uid)
          return True
        return False
    self.tic(stop_condition=stop_condition)
    self.assertEqual(len(prioritize_uid_list), 1)
    update_causality_message_uid = prioritize_uid_list[0]
    for table in 'message', 'message_queue':
      self.portal.cmf_activity_sql_connection.manage_test("""
        update %s
          set priority=-200
        where uid = %s
      """ % (table, update_causality_message_uid))
    self.tic()

  @newSimulationExpectedFailure
  @expectedFailure
  def test_04_MergingMultipleSaleOrders(self, quiet=quiet):
    sequence_list = SequenceList()
    sequence_list.addSequenceString(self.DEFAULT_SEQUENCE + \
    """
      stepCreateOrder
      stepSetOrderProfile
      stepSetOrderPriceCurrency
      stepTic
      stepCreateOrderLine
      stepSetOrderLineResource
      stepUpdateOrder
      stepOrderOrder
      stepTic
      stepCheckDeliveryBuilding
      stepConfirmOrder
      stepTic
      stepPackingListBuilderAlarm
      stepTic
      stepCheckOrderRule
      stepCheckOrderSimulation
      stepCheckDeliveryBuilding
      stepAddPackingListContainer
      stepAddPackingListContainerLine
      stepSetFillContainerLine
      stepTic

      stepSetReadyPackingList
      stepTic

      stepStartPackingList
      stepCheckInvoicingRule
      stepPrioritizeInvoiceUpdateCausalityStateTic

      stepCheckInvoiceIsDivergent
      stepCheckInvoiceIsDiverged
      stepAdoptPrevisionInvoiceQuantity
      stepTic
    """
    )
    sequence_list.play(self, quiet=quiet)

    self.assertEqual(1, len(self.portal.accounting_module))

    document = self.portal.accounting_module.objectValues()[0]
    self.assertEqual('solved', document.getCausalityState())
    line_list = document.objectValues(
      portal_type=self.portal.getPortalInvoiceMovementTypeList())
    self.assertEqual(1, len(line_list))

    line = line_list[0]
    self.assertEqual('Invoice Line', line.getPortalType())
    self.assertEqual(None, line.getQuantity(None))
    self.assertEqual(1, len(line))

    line_line = line.objectValues()[0]
    self.assertEqual('Invoice Line', line_line.getPortalType())

    # The sale invoice summed up from two sale orders.
    # The quantity of a sale order is self.default_quantity, and
    # that of the other one is self.new_order_quantity.
    self.assertEqual(self.default_price * (self.default_quantity + self.new_order_quantity), document.getTotalPrice())
    self.assertEqual(self.default_quantity + self.new_order_quantity, document.getTotalQuantity())
    self.assertEqual(self.default_quantity + self.new_order_quantity, line_line.getQuantity())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestNestedLine))
  return suite
