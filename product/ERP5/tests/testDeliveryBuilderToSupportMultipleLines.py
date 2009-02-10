##############################################################################
# -*- coding: utf8 -*-
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

from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5.tests.testInvoice import TestSaleInvoiceMixin

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

  def allowInvoiceLineContentTypeInInvoiceLine(self):
    return UnrestrictedMethod(self._allowInvoiceLineContentTypeInInvoiceLine)()

  def _allowInvoiceLineContentTypeInInvoiceLine(self):
    invoice_line_type = self.portal.portal_types['Invoice Line']
    if 'Invoice Line' not in invoice_line_type.allowed_content_types:
      invoice_line_type.allowed_content_types += ('Invoice Line',)

  def stepGetRelatedInvoiceFromPackingList(self, sequence, **kw):
    packing_list = sequence.get('packing_list')
    related_invoice_list = packing_list \
      .getCausalityRelatedValueList(portal_type=self.invoice_portal_type)
    invoice = related_invoice_list[0].getObject()
    sequence.edit(invoice=invoice)

  def stepUpdateBuilderForMultipleLineList(self, **kw):
    self.updateBuilderForMultipleLineList()

  def updateBuilderForMultipleLineList(self):
    return UnrestrictedMethod(self._updateBuilderForMultipleLineList)()

  def _updateBuilderForMultipleLineList(self):
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
      tested_property_list=('delivery_mode',
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

  def stepAdoptPrevisionPackingListQuantity(self,sequence=None, sequence_list=None):
    document = sequence.get('packing_list')
    self._solveDivergence(document, 'quantity', 'adopt')

  def stepAcceptDecisionPackingListQuantity(self,sequence=None, sequence_list=None):
    document = sequence.get('packing_list')
    self._solveDivergence(document, 'quantity', 'accept')

  def stepAdoptPrevisionInvoiceQuantity(self,sequence=None, sequence_list=None):
    document = sequence.get('invoice')
    self._solveDivergence(document, 'quantity', 'adopt')

  def stepAcceptDecisionInvoiceQuantity(self,sequence=None, sequence_list=None):
    document = sequence.get('invoice')
    self._solveDivergence(document, 'quantity', 'accept')


class TestNestedLine(TestNestedLineMixin, ERP5TypeTestCase):

  quiet = 0

  def test_01_IfNested(self, quiet=quiet):
    sequence_list = SequenceList()
    sequence = sequence_list.addSequenceString(self.DEFAULT_SEQUENCE)
    sequence_list.play(self, quiet=quiet)

    # order = sequence.get('order')
    # packing_list = sequence.get('packing_list')
    document = sequence.get('invoice')
    self.assertEquals('Sale Invoice Transaction', document.getPortalType())
    self.assertEquals(1, len(document))

    line = document.objectValues()[0]
    self.assertEquals('Invoice Line', line.getPortalType())
    self.assertEquals(None, line.getQuantity(None))
    self.assertEquals(1, len(line))

    line_line = line.objectValues()[0]
    self.assertEquals('Invoice Line', line_line.getPortalType())

    self.assertEquals(self.default_price * self.default_quantity, document.getTotalPrice())
    self.assertEquals(self.default_quantity, document.getTotalQuantity())
    self.assertEquals(self.default_price, line_line.getPrice())
    self.assertEquals(self.default_quantity, line_line.getQuantity())


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
    self.assertEquals('solved', document.getCausalityState())
    self.assertEquals(1, len(document))

    line = document.objectValues()[0]
    self.assertEquals('Invoice Line', line.getPortalType())
    self.assertEquals(None, line.getQuantity(None))
    self.assertEquals(1, len(line))

    line_line = line.objectValues()[0]
    self.assertEquals('Invoice Line', line_line.getPortalType())

    self.assertEquals(self.default_price * self.new_packing_list_quantity, document.getTotalPrice())
    self.assertEquals(self.new_packing_list_quantity, document.getTotalQuantity())
    self.assertEquals(self.new_packing_list_quantity, line_line.getQuantity())

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
    
    self.assertEquals('solved', document.getCausalityState())
    self.assertEquals(1, len(document))

    line = document.objectValues()[0]
    self.assertEquals('Invoice Line', line.getPortalType())
    self.assertEquals(None, line.getQuantity(None))
    self.assertEquals(1, len(line))

    line_line = line.objectValues()[0]
    self.assertEquals('Invoice Line', line_line.getPortalType())

    self.assertEquals(self.default_price * self.new_invoice_quantity, document.getTotalPrice())
    self.assertEquals(self.new_invoice_quantity, document.getTotalQuantity())
    self.assertEquals(self.new_invoice_quantity, line_line.getQuantity())

  def test_04_MergingMultipleSaleOrders(self, quiet=quiet):
    sequence_list = SequenceList()
    sequence = sequence_list.addSequenceString(self.DEFAULT_SEQUENCE + \
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
      stepTic

      stepCheckInvoiceIsDivergent
      stepAdoptPrevisionInvoiceQuantity
      stepTic
    """
    )
    sequence_list.play(self, quiet=quiet)

    self.assertEquals(1, len(self.portal.accounting_module))

    document = self.portal.accounting_module.objectValues()[0]
    self.assertEquals('solved', document.getCausalityState())
    self.assertEquals(1, len(document))

    line = document.objectValues()[0]
    self.assertEquals('Invoice Line', line.getPortalType())
    self.assertEquals(None, line.getQuantity(None))
    self.assertEquals(1, len(line))

    line_line = line.objectValues()[0]
    self.assertEquals('Invoice Line', line_line.getPortalType())

    # The sale invoice summed up from two sale orders.
    # The quantity of a sale order is self.default_quantity, and
    # that of the other one is self.new_order_quantity.
    self.assertEquals(self.default_price * (self.default_quantity + self.new_order_quantity), document.getTotalPrice())
    self.assertEquals(self.default_quantity + self.new_order_quantity, document.getTotalQuantity())
    self.assertEquals(self.default_quantity + self.new_order_quantity, line_line.getQuantity())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestNestedLine))
  return suite
