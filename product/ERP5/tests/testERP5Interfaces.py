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
from Products.ERP5Type.tests.testERP5TypeInterfaces import addTestMethodDynamically
from unittest import expectedFailure
import unittest

# this list can be generated automatically using introspection or can be set
# manually and treated as reference to what implements what
implements_tuple_list = [
  (('Products.ERP5.Document.RoleDefinition', 'RoleDefinition'), 'ILocalRoleGenerator'),
  (('Products.ERP5.Document.BusinessLink','BusinessLink'), 'IBusinessLink'),
  (('Products.ERP5.Document.BusinessLink','BusinessLink'), 'ICategoryAccessProvider'),
  (('Products.ERP5.Document.TradeCondition','TradeCondition'), 'IAmountGenerator'),
  (('Products.ERP5.Document.TradeModelCell','TradeModelCell'), 'IAmountGenerator'),
  (('Products.ERP5.Document.TradeModelCell','TradeModelCell'), 'IVariated'),
  (('Products.ERP5.Document.TradeModelLine','TradeModelLine'), 'IAmountGenerator'),
  (('Products.ERP5.Document.TradeModelLine','TradeModelLine'), 'IVariated'),
  (('Products.ERP5.Document.TradeModelPath','TradeModelPath'), 'IArrowBase'),
  (('Products.ERP5.Document.Transformation','Transformation'), 'IAmountGenerator'),
  (('Products.ERP5.Document.Transformation','Transformation'), 'IVariated'),
  (('Products.ERP5.Document.TransformedResource','TransformedResource'), 'IVariated'),
  #IDocument
  (('Products.ERP5.Document.Document', 'Document'), 'IDocument'),
  (('Products.ERP5.Document.Image', 'Image'), 'IDocument'),
  (('Products.ERP5.Document.File', 'File'), 'IDocument'),
  (('Products.ERP5OOo.Document.OOoDocument', 'OOoDocument'), 'IDocument'),
  (('Products.ERP5.Document.TextDocument', 'TextDocument'), 'IDocument'),
  (('Products.ERP5.Document.EmailDocument', 'EmailDocument'), 'IDocument'),
  (('Products.ERP5.Document.Event', 'Event'), 'IDocument'),
  # IAmountList
  (('Products.ERP5.GeneratedAmountList', 'GeneratedAmountList'), 'IAmountList'),
]
# IMovementGroup
for movement_group_class_name in ['MovementGroup', 'BaseVariantMovementGroup',
    'CategoryMovementGroup', 'CausalityAssignmentMovementGroup',
    'CausalityMovementGroup', 'DayMovementGroup',
    'DeliveryCausalityAssignmentMovementGroup', 'FirstCausalityMovementGroup',
    'MonthlyRangeMovementGroup', 'NestedLineMovementGroup',
    'OrderMovementGroup', 'ParentExplanationMovementGroup',
    'PropertyAssignmentMovementGroup', 'PropertyMovementGroup',
    'QuantitySignMovementGroup', 'RequirementMovementGroup',
    'RootAppliedRuleCausalityMovementGroup', 'SplitMovementGroup',
    'TitleMovementGroup',
    'VariantMovementGroup', 'VariationPropertyMovementGroup']:
  implements_tuple_list.append((('Products.ERP5Type.Document.%s' % \
      movement_group_class_name, movement_group_class_name),
      'IMovementGroup'))

class TestERP5Interfaces(ERP5TypeTestCase):
  """Tests implementation of interfaces"""

addTestMethodDynamically(TestERP5Interfaces, implements_tuple_list)

for failing_method in [
    'test_Products.ERP5.GeneratedAmountList_GeneratedAmountList_implements_IAmountList',
    'test_Products.ERP5.Document.BusinessLink_BusinessLink_implements_IBusinessLink',
    'test_Products.ERP5.Document.BusinessLink_BusinessLink_implements_ICategoryAccessProvider',
    'test_Products.ERP5.Document.TradeModelCell_TradeModelCell_implements_IVariated',
    'test_Products.ERP5.Document.TradeModelLine_TradeModelLine_implements_IVariated',
    'test_Products.ERP5.Document.Transformation_Transformation_implements_IVariated',
    'test_Products.ERP5.Document.TransformedResource_TransformedResource_implements_IVariated',
  ]:
  setattr(TestERP5Interfaces, failing_method,
      expectedFailure(getattr(TestERP5Interfaces,failing_method)))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Interfaces))
  return suite
