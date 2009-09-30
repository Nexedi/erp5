# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Łukasz Nowak <luke@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.testERP5TypeInterfaces import makeTestMethod, \
  addTestMethodDynamically
from zope.interface.verify import verifyClass
import unittest

# this list can be generated automatically using introspection or can be set
# manually and treated as reference to what implements what
implements_tuple_list = [
  ('BusinessPath', 'IArrowBase'),
  ('BusinessPath', 'IBusinessPath'),
  ('BusinessPath', 'ICategoryAccessProvider'),
  ('DeliveryLine', 'IDivergenceSolver'),
  ('TradeCondition', 'ITransformation'),
  ('TradeModelCell', 'ITransformation'),
  ('TradeModelCell', 'IVariated'),
  ('TradeModelLine', 'ITransformation'),
  ('TradeModelLine', 'IVariated'),
  ('TradeModelRule', 'IPredicate'),
  ('TradeModelRule', 'IRule'),
  ('Transformation', 'ITransformation'),
  ('Transformation', 'IVariated'),
  ('TransformationRule', 'IPredicate'),
  ('TransformationRule', 'IRule'),
  ('TransformedResource', 'IVariated'),
  #IDocument
  ('Document', 'IDocument'),
  ('Image', 'IDocument'),
  ('File', 'IDocument'),
  ('OOoDocument', 'IDocument'),
  ('TextDocument', 'IDocument'),
  ('EmailDocument', 'IDocument'),
  ('Event', 'IDocument'),
  #IMovementGroup
  ('MovementGroup', 'IMovementGroup'),
  ('BaseVariantMovementGroup', 'IMovementGroup'),
  ('CategoryMovementGroup', 'IMovementGroup'),
  ('CausalityAssignmentMovementGroup', 'IMovementGroup'),
  ('CausalityMovementGroup', 'IMovementGroup'),
  ('DayMovementGroup', 'IMovementGroup'),
  ('DeliveryCausalityAssignmentMovementGroup', 'IMovementGroup'),
  ('FirstCausalityMovementGroup', 'IMovementGroup'),
  ('MonthlyRangeMovementGroup', 'IMovementGroup'),
  ('NestedLineMovementGroup', 'IMovementGroup'),
  ('OrderMovementGroup', 'IMovementGroup'),
  ('ParentExplanationMovementGroup', 'IMovementGroup'),
  ('PropertyAssignmentMovementGroup', 'IMovementGroup'),
  ('PropertyMovementGroup', 'IMovementGroup'),
  ('QuantitySignMovementGroup', 'IMovementGroup'),
  ('RequirementMovementGroup', 'IMovementGroup'),
  ('RootAppliedRuleCausalityMovementGroup', 'IMovementGroup'),
  ('SplitMovementGroup', 'IMovementGroup'),
  ('TaxLineDeliveryMovementGroup', 'IMovementGroup'),
  ('TitleMovementGroup', 'IMovementGroup'),
  ('VariantMovementGroup', 'IMovementGroup'),
  ('VariationPropertyMovementGroup', 'IMovementGroup'),
]

class TestERP5Interfaces(ERP5TypeTestCase):
  """Tests implementation of interfaces"""

  def test_AggregatedAmountList_implements_IAggregatedAmountList(self):
    # AggregatedAmountList is not a document
    from Products.ERP5.interfaces.aggregated_amount_list \
        import IAggregatedAmountList
    from Products.ERP5.AggregatedAmountList import AggregatedAmountList
    verifyClass(IAggregatedAmountList, AggregatedAmountList)

addTestMethodDynamically()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Interfaces))
  return suite
