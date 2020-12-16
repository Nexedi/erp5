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
from erp5.component.test.testERP5TypeInterfaces import addTestMethodDynamically
from unittest import expectedFailure
import unittest

# this list can be generated automatically using introspection or can be set
# manually and treated as reference to what implements what
implements_tuple_list = [
  (('erp5.component.document.RoleDefinition', 'RoleDefinition'), 'ILocalRoleGenerator'),
  (('erp5.component.document.BusinessLink','BusinessLink'), 'IBusinessLink'),
  (('erp5.component.document.BusinessLink','BusinessLink'), 'ICategoryAccessProvider'),
  (('erp5.component.module.DivergenceMessage', 'DivergenceMessage'), 'IDivergenceMessage'),
  (('erp5.component.module.DivergenceMessage', 'DivergenceMessage'), 'IObjectMessage'),
  (('erp5.component.document.TradeCondition','TradeCondition'), 'IAmountGenerator'),
  (('erp5.component.document.TradeModelCell','TradeModelCell'), 'IAmountGenerator'),
  (('erp5.component.document.TradeModelCell','TradeModelCell'), 'IVariated'),
  (('erp5.component.document.TradeModelLine','TradeModelLine'), 'IAmountGenerator'),
  (('erp5.component.document.TradeModelLine','TradeModelLine'), 'IVariated'),
  (('erp5.component.document.TradeModelPath','TradeModelPath'), 'IArrowBase'),
  (('erp5.component.document.Transformation','Transformation'), 'IAmountGenerator'),
  (('erp5.component.document.Transformation','Transformation'), 'IVariated'),
  (('erp5.component.document.TransformedResource','TransformedResource'), 'IVariated'),
  #IDocument
  (('erp5.component.document.Document', 'Document'), 'IDocument'),
  (('erp5.component.document.Image', 'Image'), 'IDocument'),
  (('erp5.component.document.File', 'File'), 'IDocument'),
  (('erp5.component.document.OOoDocument', 'OOoDocument'), 'IDocument'),
  (('erp5.component.document.TextDocument', 'TextDocument'), 'IDocument'),
  (('erp5.component.document.EmailDocument', 'EmailDocument'), 'IDocument'),
  (('erp5.component.document.Event', 'Event'), 'IDocument'),
  # IAmountList
  (('erp5.component.module.GeneratedAmountList', 'GeneratedAmountList'), 'IAmountList'),
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
  implements_tuple_list.append((('erp5.component.document.%s' % \
      movement_group_class_name, movement_group_class_name),
      'IMovementGroup'))

class TestERP5Interfaces(ERP5TypeTestCase):
  """Tests implementation of interfaces"""
  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_pdm', 'erp5_simulation', 'erp5_trade')

addTestMethodDynamically(TestERP5Interfaces, implements_tuple_list)

for failing_method in [
    'test_erp5.component.module.GeneratedAmountList_GeneratedAmountList_implements_IAmountList',
    'test_erp5.component.document.BusinessLink_BusinessLink_implements_IBusinessLink',
    'test_erp5.component.document.BusinessLink_BusinessLink_implements_ICategoryAccessProvider',
    'test_erp5.component.document.TradeModelCell_TradeModelCell_implements_IVariated',
    'test_erp5.component.document.TradeModelLine_TradeModelLine_implements_IVariated',
    'test_erp5.component.document.Transformation_Transformation_implements_IVariated',
    'test_erp5.component.document.TransformedResource_TransformedResource_implements_IVariated',
  ]:
  setattr(TestERP5Interfaces, failing_method,
      expectedFailure(getattr(TestERP5Interfaces,failing_method)))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Interfaces))
  return suite
