##############################################################################
#
# Copyright (c) 2004, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from testInvoice import TestInvoiceMixin

class TestItemMixin(TestInvoiceMixin):
  """
    Test business template erp5_trade 
  """
  item_portal_type = 'Item'

  def getBusinessTemplateList(self):
    """
    """
    return TestInvoiceMixin.getBusinessTemplateList(self) + ('erp5_item',)
  
  def stepCreateItemList(self, sequence=None, sequence_list=None, **kw):
    """ Create some items """
    item_module = self.getPortal().item_module
    resource = sequence.get('resource')
    item = item_module.newContent(portal_type=self.item_portal_type)

    item.setResourceValue(resource)
    sequence.edit(item_list=[item]) 

  def stepOrderLineSetAggregationList(self, sequence=None,
                                          sequence_list=None, **kw):
    """  Aggregate Items """
    order_line = sequence.get('order_line')
    item_list = sequence.get('item_list')
    order_line.setAggregateValueList(item_list)  

  def stepCheckOrderLineAggregate(self, sequence=None, 
                                          sequence_list=None, **kw):
    """ Check items """
    order_line = sequence.get('order_line')
    self.checkAggregate(line=order_line, sequence=sequence)

  def stepCheckSimulationAggregate(self, sequence=None,
                                          sequence_list=None, **kw):
    """ Check items """
    order_line = sequence.get('order_line')
    simulation_movement = order_line.getOrderRelatedValue()
    self.checkAggregate(line=simulation_movement, sequence=sequence)

  def stepCheckPackingListLineAggregate(self, sequence=None,
                                          sequence_list=None, **kw):
    """ Check items """
    packing_list_line = sequence.get('packing_list_line')
    self.checkAggregate(line=packing_list_line, sequence=sequence)

  def stepCheckInvoiceLineAggregate(self, sequence=None,
                                          sequence_list=None, **kw):
    """ Check items """
    invoice = sequence.get('invoice')
    invoice_line_list = invoice.contentValues(
                         portal_type=self.invoice_line_portal_type)
    self.checkAggregate(line=invoice_line_list[0], sequence=sequence)

  def checkAggregate(self, line=None, sequence=None):
    """ Check items """
    item_list = sequence.get('item_list')
    self.assertEquals(len(line.getAggregateList()),1)
    self.failUnless(item_list[0] in line.getAggregateValueList())    
    

class TestItem(TestItemMixin, ERP5TypeTestCase) :

  run_all_test = 1
  quiet = 0

  def test_01_ItemSimpleTest(self, quiet=quiet, run=run_all_test):
    """
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = 'stepCreateOrganisation1 \
                       stepCreateOrganisation2 \
                       stepCreateOrganisation3 \
                       stepCreateItemList \
                       stepCreateOrder \
                       stepSetOrderProfile \
                       stepCreateNotVariatedResource \
                       stepTic \
                       stepCreateOrderLine \
                       stepSetOrderLineResource \
                       stepSetOrderLineDefaultValues \
                       stepOrderLineSetAggregationList \
                       stepConfirmOrder \
                       stepTic \
                       stepCheckOrderLineAggregate \
                       stepCheckOrderSimulation \
                       stepCheckSimulationAggregate \
                       stepCheckDeliveryBuilding \
                       stepCheckPackingListLineAggregate \
                       stepCheckPackingListIsNotDivergent '

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)


  def test_02_ItemWithInvoice(self, quiet=quiet, run=run_all_test):
    """
    """
    if not run: return
    sequence_list = SequenceList()

    sequence_string = 'stepCreateEntities \
                       stepCreateCurrency \
                       stepCreateItemList \
                       stepCreateSaleInvoiceTransactionRule \
                       stepCreateOrder \
                       stepSetOrderProfile \
                       stepSetOrderPriceCurrency \
                       stepCreateNotVariatedResource \
                       stepTic \
                       stepCreateOrderLine \
                       stepSetOrderLineResource \
                       stepSetOrderLineDefaultValues \
                       stepOrderLineSetAggregationList \
                       stepConfirmOrder \
                       stepTic \
                       stepCheckOrderRule \
                       stepCheckOrderLineAggregate \
                       stepCheckOrderSimulation \
                       stepCheckSimulationAggregate \
                       stepCheckDeliveryBuilding \
                       stepCheckPackingListLineAggregate \
                       stepAddPackingListContainer \
                       stepAddPackingListContainerLine \
                       stepSetContainerLineFullQuantity \
                       stepTic \
                       stepCheckPackingListIsPacked \
                       stepSetReadyPackingList \
                       stepTic \
                       stepStartPackingList \
                       stepCheckInvoicingRule \
                       stepTic \
                       stepCheckInvoiceBuilding \
                       stepRebuildAndCheckNothingIsCreated \
                       stepCheckInvoicesConsistency \
                       stepCheckInvoiceLineAggregate \
                      ' 

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)


   
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestItem))
  return suite

