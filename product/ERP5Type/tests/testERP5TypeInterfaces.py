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
from zope.interface.verify import verifyClass
import unittest

class TestERP5TypeInterfaces(ERP5TypeTestCase):
  """Tests implementation of interfaces"""

  def test_ObjectMessage_implements_IObjectMessage(self):
    from Products.ERP5Type.interfaces.object_message import IObjectMessage
    from Products.ERP5Type.ObjectMessage import ObjectMessage
    verifyClass(IObjectMessage, ObjectMessage)

  def test_ConsistencyMessage_implements_IObjectMessage(self):
    from Products.ERP5Type.interfaces.object_message import IObjectMessage
    from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage
    verifyClass(IObjectMessage, ConsistencyMessage)

  def test_ConsistencyMessage_implements_IConsistencyMessage(self):
    from Products.ERP5Type.interfaces.consistency_message \
        import IConsistencyMessage
    from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage
    verifyClass(IConsistencyMessage, ConsistencyMessage)

  def test_DivergenceMessage_implements_IObjectMessage(self):
    from Products.ERP5Type.interfaces.object_message import IObjectMessage
    from Products.ERP5Type.DivergenceMessage import DivergenceMessage
    verifyClass(IObjectMessage, DivergenceMessage)

  def test_DivergenceMessage_implements_IDivergenceMessage(self):
    from Products.ERP5Type.interfaces.divergence_message import IDivergenceMessage
    from Products.ERP5Type.DivergenceMessage import DivergenceMessage
    verifyClass(IDivergenceMessage, DivergenceMessage)

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

    Uses naming test_<DocumentClass>_implements_<InterfaceClass>
    It is possible to use --run_only on those dynamically generated methods"""
  for document, interface in implements_tuple_list:
    method_name = 'test_%s_implements_%s' % (document, interface)
    method = makeTestMethod(document, interface)
    setattr(TestERP5Interfaces, method_name, method)

# Note: Enable this method when implements_tuple_list will be filled
#addTestMethodDynamically()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5TypeInterfaces))
  return suite
