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
from testPackingList import TestPackingListMixin

class TestItemMixin(TestPackingListMixin):
  """
    Test business template erp5_trade 
  """
  item_portal_type = 'Item'

  default_sequence = 'stepCreateOrganisation1 \
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
                      stepOrderOrder \
                      stepTic \
                      stepCheckOrderLineAggregate \
                      stepConfirmOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      stepCheckDeliveryBuilding \
                      stepCheckPackingListIsNotDivergent \
                      stepCheckOrderPackingList '

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base','erp5_pdm', 'erp5_trade', 'erp5_apparel','erp5_item')
  
  def stepCreateItemList(self, sequence=None, sequence_list=None, **kw):
    """ Create some items """
    item_module = self.getPortal().item_module
    resource = sequence.get('resource')
    item = item_module.newContent(id='item', reference='0',
                                   portal_type=self.item_portal_type)

    item.setResourceValue(resource)
    sequence.edit(item_list=[item]) 

  def stepOrderLineSetAggregationList(self, sequence=None,
                                          sequence_list=None, **kw):
    """  items """
    order_line = sequence.get('order_line')
    item_list = sequence.get('item_list')
    order_line.setAggregateValueList(item_list)  

  def stepCheckOrderLineAggregate(self, sequence=None, 
                                          sequence_list=None, **kw):
    """ Check items """
    order_line = sequence.get('order_line')
    item_list = sequence.get('item_list')
    self.assertEquals(len(order_line.getAggregateList()),1)
    self.failUnless(item_list[0] in order_line.getAggregateValueList())


class TestItem(TestItemMixin, ERP5TypeTestCase) :

  run_all_test = 1
  quiet = 0

  def test_01_ItemSimpleTest(self, quiet=quiet, run=run_all_test):
    """
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence

    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

   
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestItem))
  return suite

