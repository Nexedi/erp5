##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
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
import os

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList

class TestAmount(ERP5TypeTestCase):

  run_all_test = 1
  resource_portal_type = "Apparel Model"
  amount_portal_type = "Transformation Transformed Resource"
  amount_parent_portal_type = "Transformation"
  # It is important to use property which are not defined on amount.
  variation_property_list = ['composition', 'margin_ratio']
  variation_property_dict = {
    'composition': 'azertyuio',
    'margin_ratio': 2.4
  }
  failed_variation_property_dict = {
    'composition': 'azertyuio',
    'margin_ratio': 2.4,
    'sfdvdfbdgbfgbfgbfgbfg': None,
  }

  def getTitle(self):
    return "Amount"

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base', 'erp5_pdm', 'erp5_simulation', 'erp5_trade', 'erp5_apparel')

  def stepCreateResource(self, sequence=None, sequence_list=None, **kw):
    """
      Create a resource
    """
    portal = self.getPortal()
    module = portal.getDefaultModule(self.resource_portal_type)
    resource = module.newContent(portal_type=self.resource_portal_type)
    # As the current resource as no variation property,
    # we will create some for the test.
    resource.setVariationPropertyList(self.variation_property_list)
    sequence.edit(
        resource=resource,
    )

  def stepCreateAmount(self, sequence=None, sequence_list=None, **kw):
    """
      Create a amount to test
    """
    portal = self.getPortal()
    module = portal.getDefaultModule(self.amount_parent_portal_type)
    amount_parent = module.newContent(
                      portal_type=self.amount_parent_portal_type)
    amount = amount_parent.newContent(
                      portal_type=self.amount_portal_type)
    sequence.edit(
       amount=amount,
    )

  def stepSetAmountResource(self, sequence=None, sequence_list=None, **kw):
    """
      Add a resource to the amount.
    """
    amount = sequence.get('amount')
    resource = sequence.get('resource')
    amount.setResourceValue(resource)
    sequence.edit(
       variation_property_dict=dict.fromkeys(self.variation_property_dict)
    )

  def stepCheckEmptyGetVariationPropertyDict(self, sequence=None,
                                             sequence_list=None, **kw):
    """
      Test the method GetVariationPropertyDict.
    """
    amount = sequence.get('amount')
    vpd = amount.getVariationPropertyDict()
    self.assertEqual(vpd, {})

  def stepCheckEmptySetVariationPropertyDict(self, sequence=None,
                                             sequence_list=None, **kw):
    """
      Test the method GetVariationPropertyDict.
    """
    amount = sequence.get('amount')
    self.assertRaises(KeyError, amount.setVariationPropertyDict,
                      self.variation_property_dict)

  def stepSetVariationPropertyDict(self, sequence=None,
                                        sequence_list=None, **kw):
    """
      Test the method GetVariationPropertyDict.
    """
    amount = sequence.get('amount')
    amount.setVariationPropertyDict(self.variation_property_dict)
    sequence.edit(
       variation_property_dict=self.variation_property_dict
    )

  def stepCheckGetVariationPropertyDict(self, sequence=None,
                                        sequence_list=None, **kw):
    """
      Test the method GetVariationPropertyDict.
    """
    amount = sequence.get('amount')
    vpd = amount.getVariationPropertyDict()
    self.failIfDifferentSet(vpd.keys(),
                            sequence.get('variation_property_dict').keys())
    for key in vpd.keys():
      self.assertEqual(vpd[key], sequence.get('variation_property_dict')[key])

  def stepSetWrongVariationPropertyDict(self, sequence=None,
                                        sequence_list=None, **kw):
    """
      Test the method GetVariationPropertyDict.
    """
    amount = sequence.get('amount')
    self.assertRaises(KeyError, amount.setVariationPropertyDict,
                      self.failed_variation_property_dict)

  def stepCheckEdit(self, sequence=None, sequence_list=None, **kw):
    """
      Test edit method on amount.
    """
    amount = sequence.get('amount')
    # If edit doesn't raise a error, it's ok.
    amount.edit(**self.variation_property_dict)
    sequence.edit(
       variation_property_dict=self.variation_property_dict
    )

  def test_01_variationProperty(self, quiet=0, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()
    # Test setVariationPropertyDict and
    # getVariationPropertyDict without
    # resource on Amount.
    sequence_string = '\
              CreateAmount \
              CheckEmptyGetVariationPropertyDict \
              CheckEmptySetVariationPropertyDict \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test setVariationPropertyDict and
    # getVariationPropertyDict
    sequence_string = '\
              CreateResource \
              CreateAmount \
              SetAmountResource \
              CheckGetVariationPropertyDict \
              SetVariationPropertyDict \
              CheckGetVariationPropertyDict \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test setVariationPropertyDict with a wrong property
    sequence_string = '\
              CreateResource \
              CreateAmount \
              SetAmountResource \
              SetWrongVariationPropertyDict \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test edit method on amount
    sequence_string = '\
              CreateResource \
              CreateAmount \
              SetAmountResource \
              CheckEdit \
              CheckGetVariationPropertyDict \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)


class TestMovement(ERP5TypeTestCase):
  """Tests for Movement class
  """
  def afterSetUp(self):
    self.login()
    self.portal = self.getPortal()

    if getattr(self.portal, 'dummy_delivery_module', None) is None:
      types_tool = self.portal.portal_types
      types_tool.newContent(id="My Movement",
                            type_class="Movement")
      types_tool.newContent(id="My Delivery",
                            type_class="Delivery",
                            type_allowed_content_type_list=("My Movement",))
      types_tool.newContent(id="My Delivery Module",
                            type_class="Folder",
                            type_allowed_content_type_list=("My Delivery",))

      self.portal.newContent(id="dummy_delivery_module",
                             portal_type="My Delivery Module")
      self.commit()
    self.delivery_module = self.portal.dummy_delivery_module

  def getPortalName(self):
    forced_portal_id = os.environ.get('erp5_tests_portal_id')
    if forced_portal_id:
      return str(forced_portal_id)
    return 'movement_test'

  def _makeOne(self, **kw):
    # returns a Movement inside of a delivery
    delivery = self.delivery_module.newContent()
    return delivery.newContent(**kw)

  def testQuantity(self):
    mvt = self._makeOne()
    mvt.setQuantity(10)
    self.assertEqual(10, mvt.getQuantity())
    self.assertEqual(0, mvt.getTotalPrice())
    mvt.edit(quantity=20)
    self.assertEqual(20, mvt.getQuantity())

  def testPrice(self):
    mvt = self._makeOne()
    self.assertEqual(None, mvt.getPrice())
    mvt.setPrice(10)
    self.assertEqual(10, mvt.getPrice())
    self.assertEqual(0, mvt.getTotalPrice())
    mvt.setQuantity(1)
    self.assertEqual(10, mvt.getTotalPrice())

  def testSourceDebit(self):
    mvt = self._makeOne()
    mvt.setSourceDebit(10)
    self.assertEqual(10, mvt.getSourceDebit())
    self.assertEqual(0, mvt.getSourceCredit())
    self.assertEqual(-10, mvt.getQuantity())

    mvt.edit(source_debit=20)
    self.assertEqual(20, mvt.getSourceDebit())
    self.assertEqual(0, mvt.getSourceCredit())
    self.assertEqual(-20, mvt.getQuantity())

  def testSourceCredit(self):
    mvt = self._makeOne()
    mvt.setSourceCredit(10)
    self.assertEqual(0, mvt.getSourceDebit())
    self.assertEqual(10, mvt.getSourceCredit())
    self.assertEqual(10, mvt.getQuantity())

    mvt.edit(source_credit=20)
    self.assertEqual(0, mvt.getSourceDebit())
    self.assertEqual(20, mvt.getSourceCredit())
    self.assertEqual(20, mvt.getQuantity())

  def testSourceDebitCredit(self):
    mvt = self._makeOne()
    mvt.setSourceCredit(10)
    mvt.edit(source_credit=0, source_debit=10)
    self.assertEqual(10, mvt.getSourceDebit())
    self.assertEqual(0, mvt.getSourceCredit())
    self.assertEqual(-10, mvt.getQuantity())

  def testDestinationDebit(self):
    mvt = self._makeOne()
    mvt.setDestinationDebit(10)
    self.assertEqual(10, mvt.getDestinationDebit())
    self.assertEqual(0, mvt.getDestinationCredit())
    self.assertEqual(10, mvt.getQuantity())

    mvt.edit(destination_debit=20)
    self.assertEqual(20, mvt.getDestinationDebit())
    self.assertEqual(0, mvt.getDestinationCredit())
    self.assertEqual(20, mvt.getQuantity())

  def testDestinationCredit(self):
    mvt = self._makeOne()
    mvt.setDestinationCredit(10)
    self.assertEqual(0, mvt.getDestinationDebit())
    self.assertEqual(10, mvt.getDestinationCredit())
    self.assertEqual(-10, mvt.getQuantity())

    mvt.edit(destination_credit=20)
    self.assertEqual(0, mvt.getDestinationDebit())
    self.assertEqual(20, mvt.getDestinationCredit())
    self.assertEqual(-20, mvt.getQuantity())

  def testDestinationDebitCredit(self):
    mvt = self._makeOne()
    mvt.setDestinationCredit(10)
    mvt.edit(destination_credit=0, destination_debit=10)
    self.assertEqual(10, mvt.getDestinationDebit())
    self.assertEqual(0, mvt.getDestinationCredit())
    self.assertEqual(10, mvt.getQuantity())

  def testSourceAssetCredit(self):
    mvt = self._makeOne()
    mvt.edit(source_asset_credit=100)
    self.assertEqual(100, mvt.getSourceAssetCredit())
    self.assertEqual(0, mvt.getQuantity())
    self.assertEqual(0, mvt.getSourceInventoriatedTotalAssetDebit())
    self.assertEqual(100, mvt.getSourceInventoriatedTotalAssetCredit())
    self.assertEqual(-100, mvt.getSourceInventoriatedTotalAssetPrice())
    # reset and set quantity instead
    mvt.edit(source_asset_credit=None, source_credit=200)
    self.assertEqual(0.0, mvt.getSourceAssetCredit())
    self.assertEqual(200, mvt.getSourceCredit())

  def testSourceAssetDebit(self):
    mvt = self._makeOne()
    mvt.edit(source_asset_debit=100)
    self.assertEqual(100, mvt.getSourceAssetDebit())
    self.assertEqual(0, mvt.getQuantity())
    self.assertEqual(100, mvt.getSourceInventoriatedTotalAssetDebit())
    self.assertEqual(0, mvt.getSourceInventoriatedTotalAssetCredit())
    self.assertEqual(100, mvt.getSourceInventoriatedTotalAssetPrice())
    # reset and set quantity instead
    mvt.edit(source_asset_debit=None, source_debit=200)
    self.assertEqual(0.0, mvt.getSourceAssetDebit())
    self.assertEqual(200, mvt.getSourceDebit())

  def testEditSourceAssetDebitAndCredit(self):
    mvt = self._makeOne()
    mvt.edit(source_asset_debit=100, source_asset_credit=None)
    self.assertEqual(100, mvt.getSourceAssetDebit())
    mvt.edit(source_asset_debit=None, source_asset_credit=100)
    self.assertEqual(100, mvt.getSourceAssetCredit())
    mvt.edit(source_asset_debit=100, source_asset_credit='')
    self.assertEqual(100, mvt.getSourceAssetDebit())
    mvt.edit(source_asset_debit='', source_asset_credit=100)
    self.assertEqual(100, mvt.getSourceAssetCredit())

  def testDestinationAssetCredit(self):
    mvt = self._makeOne()
    mvt.edit(destination_asset_credit=100)
    self.assertEqual(100, mvt.getDestinationAssetCredit())
    self.assertEqual(0, mvt.getQuantity())
    self.assertEqual(0, mvt.getDestinationInventoriatedTotalAssetDebit())
    self.assertEqual(100, mvt.getDestinationInventoriatedTotalAssetCredit())
    self.assertEqual(-100, mvt.getDestinationInventoriatedTotalAssetPrice())
    # reset and set quantity instead
    mvt.edit(destination_asset_credit=None, destination_credit=200)
    self.assertEqual(0.0, mvt.getDestinationAssetCredit())
    self.assertEqual(200, mvt.getDestinationCredit())

  def testDestinationAssetDebit(self):
    mvt = self._makeOne()
    mvt.edit(destination_asset_debit=100)
    self.assertEqual(100, mvt.getDestinationAssetDebit())
    self.assertEqual(0, mvt.getQuantity())
    self.assertEqual(100, mvt.getDestinationInventoriatedTotalAssetDebit())
    self.assertEqual(0, mvt.getDestinationInventoriatedTotalAssetCredit())
    self.assertEqual(100, mvt.getDestinationInventoriatedTotalAssetPrice())
    # reset and set quantity instead
    mvt.edit(destination_asset_debit=None, destination_debit=200)
    self.assertEqual(0.0, mvt.getDestinationAssetDebit())
    self.assertEqual(200, mvt.getDestinationDebit())

  def testEditDestinationAssetDebitAndCredit(self):
    mvt = self._makeOne()
    mvt.edit(destination_asset_debit=100, destination_asset_credit=None)
    self.assertEqual(100, mvt.getDestinationAssetDebit())
    mvt.edit(destination_asset_debit=None, destination_asset_credit=100)
    self.assertEqual(100, mvt.getDestinationAssetCredit())
    mvt.edit(destination_asset_debit=100, destination_asset_credit='')
    self.assertEqual(100, mvt.getDestinationAssetDebit())
    mvt.edit(destination_asset_debit='', destination_asset_credit=100)
    self.assertEqual(100, mvt.getDestinationAssetCredit())

  def testCancellationAmountGetDestinationCredit(self):
    mvt = self._makeOne()
    mvt.setCancellationAmount(True)
    mvt.setQuantity(10)
    self.assertEqual(mvt.getQuantity(), 10)
    self.assertEqual(mvt.getDestinationDebit(), 0)
    self.assertEqual(mvt.getDestinationCredit(), -10)

  def testCancellationAmountGetDestinationDebit(self):
    mvt = self._makeOne()
    mvt.setCancellationAmount(True)
    mvt.setQuantity(-10)
    self.assertEqual(mvt.getQuantity(), -10)
    self.assertEqual(mvt.getDestinationDebit(), -10)
    self.assertEqual(mvt.getDestinationCredit(), 0)

  def testCancellationAmountGetSourceCredit(self):
    mvt = self._makeOne()
    mvt.setCancellationAmount(True)
    mvt.setQuantity(-10)
    self.assertEqual(mvt.getQuantity(), -10)
    self.assertEqual(mvt.getSourceDebit(), 0)
    self.assertEqual(mvt.getSourceCredit(), -10)

  def testCancellationAmountGetSourceDebit(self):
    mvt = self._makeOne()
    mvt.setCancellationAmount(True)
    mvt.setQuantity(10)
    self.assertEqual(mvt.getQuantity(), 10)
    self.assertEqual(mvt.getSourceDebit(), -10)
    self.assertEqual(mvt.getSourceCredit(), 0)

  def testCancellationAmountSetDestinationCredit(self):
    mvt = self._makeOne()
    mvt.setDestinationCredit(-10)
    self.assertTrue(mvt.isCancellationAmount())
    self.assertEqual(mvt.getDestinationDebit(), 0)
    self.assertEqual(mvt.getDestinationCredit(), -10)

    mvt.setDestinationCredit(10)
    self.assertFalse(mvt.isCancellationAmount())
    self.assertEqual(mvt.getDestinationDebit(), 0)
    self.assertEqual(mvt.getDestinationCredit(), 10)

  def testCancellationAmountSetDestinationDebit(self):
    mvt = self._makeOne()
    mvt.setDestinationDebit(-10)
    self.assertTrue(mvt.isCancellationAmount())
    self.assertEqual(mvt.getDestinationDebit(), -10)
    self.assertEqual(mvt.getDestinationCredit(), 0)

    mvt.setDestinationDebit(10)
    self.assertFalse(mvt.isCancellationAmount())
    self.assertEqual(mvt.getDestinationDebit(), 10)
    self.assertEqual(mvt.getDestinationCredit(), 0)

  def testCancellationAmountSetDestinationDebitCredit(self):
    mvt = self._makeOne()
    mvt.edit(destination_debit=-10, destination_credit=0)
    self.assertTrue(mvt.isCancellationAmount())
    self.assertEqual(mvt.getDestinationDebit(), -10)
    self.assertEqual(mvt.getDestinationCredit(), 0)

    mvt.edit(destination_debit=-10, destination_credit=None)
    self.assertTrue(mvt.isCancellationAmount())
    self.assertEqual(mvt.getDestinationDebit(), -10)
    self.assertEqual(mvt.getDestinationCredit(), 0)

  def testCancellationAmountSetSourceCredit(self):
    mvt = self._makeOne()
    mvt.setSourceCredit(-10)
    self.assertTrue(mvt.isCancellationAmount())
    self.assertEqual(mvt.getSourceDebit(), 0)
    self.assertEqual(mvt.getSourceCredit(), -10)

    mvt.setSourceCredit(10)
    self.assertFalse(mvt.isCancellationAmount())
    self.assertEqual(mvt.getSourceDebit(), 0)
    self.assertEqual(mvt.getSourceCredit(), 10)

  def testCancellationAmountSetSourceDebit(self):
    mvt = self._makeOne()
    mvt.setSourceDebit(-10)
    self.assertTrue(mvt.isCancellationAmount())
    self.assertEqual(mvt.getSourceDebit(), -10)
    self.assertEqual(mvt.getSourceCredit(), 0)

    mvt.setSourceDebit(10)
    self.assertFalse(mvt.isCancellationAmount())
    self.assertEqual(mvt.getSourceDebit(), 10)
    self.assertEqual(mvt.getSourceCredit(), 0)

  def testCancellationAmountSetSourceDebitCredit(self):
    mvt = self._makeOne()
    mvt.edit(source_debit=-10, source_credit=0)
    self.assertTrue(mvt.isCancellationAmount())
    self.assertEqual(mvt.getSourceDebit(), -10)
    self.assertEqual(mvt.getSourceCredit(), 0)

    mvt.edit(source_debit=-10, source_credit=None)
    self.assertTrue(mvt.isCancellationAmount())
    self.assertEqual(mvt.getSourceDebit(), -10)
    self.assertEqual(mvt.getSourceCredit(), 0)


class TestAccountingTransactionLine(TestMovement):
  """Tests for Accounting Transaction Line class, which have an overloaded
  'edit' method.
  """
  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base', 'erp5_simulation', 'erp5_accounting')

  def afterSetUp(self):
    self.login()
    self.portal = self.getPortal()

    if getattr(self.portal, 'accounting_transaction_line_module', None) is None:
      types_tool = self.portal.portal_types
      types_tool.newContent(id="My Accounting Transaction Line",
                            type_class="AccountingTransactionLine")
      types_tool.newContent(
          id="My Accounting Transaction Line Module",
          type_class="Folder",
          type_allowed_content_type_list=("My Accounting Transaction Line",))

      self.portal.newContent(id="accounting_transaction_line_module",
                             portal_type="My Accounting Transaction Line Module")
      self.commit()
    self.atl_module = self.portal.accounting_transaction_line_module

  def _makeOne(self, **kw):
    return self.atl_module.newContent(**kw)

  def testPrice(self):
    # price is always 1 for accounting transactions lines
    mvt = self._makeOne()
    self.assertEqual(1, mvt.getPrice())

  def testQuantity(self):
    mvt = self._makeOne()
    mvt.setQuantity(10)
    self.assertEqual(10, mvt.getQuantity())
    # self.assertEqual(None, mvt.getTotalPrice())
    # ... not with Accounting Transaction Lines, because price is 1
    mvt.edit(quantity=20)
    self.assertEqual(20, mvt.getQuantity())

  def testDefautSourceTotalAssetDebit(self):
    mvt = self._makeOne()
    mvt.edit(source_debit=100)
    self.assertEqual(100, mvt.getSourceInventoriatedTotalAssetDebit())
    self.assertEqual(0, mvt.getSourceInventoriatedTotalAssetCredit())
    self.assertEqual(100, mvt.getSourceInventoriatedTotalAssetPrice())
    self.assertEqual(None, mvt.getSourceTotalAssetPrice())
    self.assertEqual(None, mvt.getDestinationTotalAssetPrice())
    self.assertEqual(0.0, mvt.getSourceAssetDebit())
    self.assertEqual(0.0, mvt.getSourceAssetCredit())

  def testDefautSourceTotalAssetCredit(self):
    mvt = self._makeOne()
    mvt.edit(source_credit=100)
    self.assertEqual(0, mvt.getSourceInventoriatedTotalAssetDebit())
    self.assertEqual(100, mvt.getSourceInventoriatedTotalAssetCredit())
    self.assertEqual(-100, mvt.getSourceInventoriatedTotalAssetPrice())
    self.assertEqual(None, mvt.getSourceTotalAssetPrice())
    self.assertEqual(None, mvt.getDestinationTotalAssetPrice())
    self.assertEqual(0.0, mvt.getSourceAssetDebit())
    self.assertEqual(0.0, mvt.getSourceAssetCredit())

  def testDefautDestinationTotalAssetDebit(self):
    mvt = self._makeOne()
    mvt.edit(destination_debit=100)
    self.assertEqual(100, mvt.getDestinationInventoriatedTotalAssetDebit())
    self.assertEqual(0, mvt.getDestinationInventoriatedTotalAssetCredit())
    self.assertEqual(100, mvt.getDestinationInventoriatedTotalAssetPrice())
    self.assertEqual(None, mvt.getSourceTotalAssetPrice())
    self.assertEqual(None, mvt.getDestinationTotalAssetPrice())
    self.assertEqual(0.0, mvt.getDestinationAssetDebit())
    self.assertEqual(0.0, mvt.getDestinationAssetCredit())

  def testDefautDestinationTotalAssetCredit(self):
    mvt = self._makeOne()
    mvt.edit(destination_credit=100)
    self.assertEqual(0, mvt.getDestinationInventoriatedTotalAssetDebit())
    self.assertEqual(100, mvt.getDestinationInventoriatedTotalAssetCredit())
    self.assertEqual(-100, mvt.getDestinationInventoriatedTotalAssetPrice())
    self.assertEqual(None, mvt.getSourceTotalAssetPrice())
    self.assertEqual(None, mvt.getDestinationTotalAssetPrice())
    self.assertEqual(0.0, mvt.getDestinationAssetDebit())
    self.assertEqual(0.0, mvt.getDestinationAssetCredit())

  def testSourceAssetCredit(self):
    mvt = self._makeOne()
    mvt.edit(source_asset_credit=100)
    self.assertEqual(100, mvt.getSourceAssetCredit())
    self.assertEqual(0, mvt.getQuantity())
    self.assertEqual(0, mvt.getSourceInventoriatedTotalAssetDebit())
    self.assertEqual(100, mvt.getSourceInventoriatedTotalAssetCredit())
    self.assertEqual(-100, mvt.getSourceInventoriatedTotalAssetPrice())
    # reset and set quantity instead
    mvt.edit(source_asset_credit=None, source_credit=200)
    self.assertEqual(0.0, mvt.getSourceAssetCredit())
    self.assertEqual(200, mvt.getSourceCredit())
    # this is only true for Accounting Transaction Line:
    self.assertEqual(0, mvt.getSourceInventoriatedTotalAssetDebit())
    self.assertEqual(200, mvt.getSourceInventoriatedTotalAssetCredit())
    self.assertEqual(-200, mvt.getSourceInventoriatedTotalAssetPrice())

  def testSourceAssetDebit(self):
    mvt = self._makeOne()
    mvt.edit(source_asset_debit=100)
    self.assertEqual(100, mvt.getSourceAssetDebit())
    self.assertEqual(0, mvt.getQuantity())
    self.assertEqual(100, mvt.getSourceInventoriatedTotalAssetDebit())
    self.assertEqual(0, mvt.getSourceInventoriatedTotalAssetCredit())
    self.assertEqual(100, mvt.getSourceInventoriatedTotalAssetPrice())
    # reset and set quantity instead
    mvt.edit(source_asset_debit=None, source_debit=200)
    self.assertEqual(0.0, mvt.getSourceAssetDebit())
    self.assertEqual(200, mvt.getSourceDebit())
    # this is only true for Accounting Transaction Line:
    self.assertEqual(200, mvt.getSourceInventoriatedTotalAssetDebit())
    self.assertEqual(0, mvt.getSourceInventoriatedTotalAssetCredit())
    self.assertEqual(200, mvt.getSourceInventoriatedTotalAssetPrice())

  def testDestinationAssetCredit(self):
    mvt = self._makeOne()
    mvt.edit(destination_asset_credit=100)
    self.assertEqual(100, mvt.getDestinationAssetCredit())
    self.assertEqual(0, mvt.getQuantity())
    self.assertEqual(0, mvt.getDestinationInventoriatedTotalAssetDebit())
    self.assertEqual(100, mvt.getDestinationInventoriatedTotalAssetCredit())
    self.assertEqual(-100, mvt.getDestinationInventoriatedTotalAssetPrice())
    # reset and set quantity instead
    mvt.edit(destination_asset_credit=None, destination_credit=200)
    self.assertEqual(0.0, mvt.getDestinationAssetCredit())
    self.assertEqual(200, mvt.getDestinationCredit())
    # this is only true for Accounting Transaction Line:
    self.assertEqual(0, mvt.getDestinationInventoriatedTotalAssetDebit())
    self.assertEqual(200, mvt.getDestinationInventoriatedTotalAssetCredit())
    self.assertEqual(-200, mvt.getDestinationInventoriatedTotalAssetPrice())

  def testDestinationAssetDebit(self):
    mvt = self._makeOne()
    mvt.edit(destination_asset_debit=100)
    self.assertEqual(100, mvt.getDestinationAssetDebit())
    self.assertEqual(0, mvt.getQuantity())
    self.assertEqual(100, mvt.getDestinationInventoriatedTotalAssetDebit())
    self.assertEqual(0, mvt.getDestinationInventoriatedTotalAssetCredit())
    self.assertEqual(100, mvt.getDestinationInventoriatedTotalAssetPrice())
    # reset and set quantity instead
    mvt.edit(destination_asset_debit=None, destination_debit=200)
    self.assertEqual(0.0, mvt.getDestinationAssetDebit())
    self.assertEqual(200, mvt.getDestinationDebit())
    # this is only true for Accounting Transaction Line:
    self.assertEqual(200, mvt.getDestinationInventoriatedTotalAssetDebit())
    self.assertEqual(0, mvt.getDestinationInventoriatedTotalAssetCredit())
    self.assertEqual(200, mvt.getDestinationInventoriatedTotalAssetPrice())

  def testDestinationAssetDebitCancellation(self):
    mvt = self._makeOne()
    mvt.edit(destination_asset_debit=-100)
    self.assertTrue(mvt.isCancellationAmount())
    self.assertEqual(-100, mvt.getDestinationAssetDebit())
    self.assertEqual(0, mvt.getQuantity())
    self.assertEqual(-100, mvt.getDestinationInventoriatedTotalAssetDebit())
    self.assertEqual(0, mvt.getDestinationInventoriatedTotalAssetCredit())
    self.assertEqual(-100, mvt.getDestinationInventoriatedTotalAssetPrice())

  def testDestinationAssetCreditCancellation(self):
    mvt = self._makeOne()
    mvt.edit(destination_asset_credit=-100)
    self.assertTrue(mvt.isCancellationAmount())
    self.assertEqual(-100, mvt.getDestinationAssetCredit())
    self.assertEqual(0, mvt.getQuantity())
    self.assertEqual(-100, mvt.getDestinationInventoriatedTotalAssetCredit())
    self.assertEqual(0, mvt.getDestinationInventoriatedTotalAssetDebit())
    self.assertEqual(100, mvt.getDestinationInventoriatedTotalAssetPrice())

  def testSourceAssetDebitCancellation(self):
    mvt = self._makeOne()
    mvt.edit(source_asset_debit=-100)
    self.assertTrue(mvt.isCancellationAmount())
    self.assertEqual(-100, mvt.getSourceAssetDebit())
    self.assertEqual(0, mvt.getQuantity())
    self.assertEqual(-100, mvt.getSourceInventoriatedTotalAssetDebit())
    self.assertEqual(0, mvt.getSourceInventoriatedTotalAssetCredit())
    self.assertEqual(-100, mvt.getSourceInventoriatedTotalAssetPrice())

  def testSourceAssetCreditCancellation(self):
    mvt = self._makeOne()
    mvt.edit(source_asset_credit=-100)
    self.assertTrue(mvt.isCancellationAmount())
    self.assertEqual(-100, mvt.getSourceAssetCredit())
    self.assertEqual(0, mvt.getQuantity())
    self.assertEqual(-100, mvt.getSourceInventoriatedTotalAssetCredit())
    self.assertEqual(0, mvt.getSourceInventoriatedTotalAssetDebit())
    self.assertEqual(100, mvt.getSourceInventoriatedTotalAssetPrice())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestAmount))
  suite.addTest(unittest.makeSuite(TestMovement))
  suite.addTest(unittest.makeSuite(TestAccountingTransactionLine))
  return suite
