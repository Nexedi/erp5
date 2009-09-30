# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Łukasz Nowak <luke@nexedi.com>
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
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
]

class TestERP5Interfaces(ERP5TypeTestCase):
  """Tests implementation of interfaces"""

  def test_AggregatedAmountList_implements_IAggregatedAmountList(self):
    # AggregatedAmountList is not a document
    from Products.ERP5.interfaces.aggregated_amount_list \
        import IAggregatedAmountList
    from Products.ERP5.AggregatedAmountList import AggregatedAmountList
    verifyClass(IAggregatedAmountList, AggregatedAmountList)
  
def makeTestMethod(document, interface):
  """Common method which checks if documents implements interface"""
  def testMethod(self):
    _temp = __import__('Products.ERP5Type.Document.%s' % document, globals(),
        locals(), ['%s' % document])
    Document = getattr(_temp, document)
    _temp = __import__('Products.ERP5Type.interfaces', globals(), locals(),
        ['%s' % interface])
    Interface = getattr(_temp, interface)

    verifyClass(Interface, Document)

  return testMethod

def addTestMethodDynamically():
  """Creates test methods on the fly 

    Uses naming test_TradeCondition_implements_ITransformation
    It is possible to use --run_only on those dynamically generated methods"""
  for document, interface in implements_tuple_list:
    method_name = 'test_%s_implements_%s' % (document, interface)
    method = makeTestMethod(document, interface)
    setattr(TestERP5Interfaces, method_name, method)

addTestMethodDynamically()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Interfaces))
  return suite
