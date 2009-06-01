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


class TestERP5Interfaces(ERP5TypeTestCase):
  """Test that every class implements interfaces properly"""

#  TODO: Do it automagic way, maybe introspection:
#  Like in testXHTMLStyle add test methods
#  for interface in interface_list:
#    for class in class_list:
#      if interface.implementedBy(class):
#        self.createInterfaceTest(interface, class)
#
#  and then nice result of declared interfaces

  def test_TradeModelCell_implements_ITransformation(self):
    from Products.ERP5Type.Document.TradeModelCell import TradeModelCell
    from Products.ERP5Type.interfaces import ITransformation
    verifyClass(ITransformation, TradeModelCell)

  def test_TradeModelCell_implements_IVariated(self):
    from Products.ERP5Type.Document.TradeModelCell import TradeModelCell
    from Products.ERP5Type.interfaces import IVariated
    verifyClass(IVariated, TradeModelCell)

  def test_TradeModelLine_implements_ITransformation(self):
    from Products.ERP5Type.Document.TradeModelLine import TradeModelLine
    from Products.ERP5Type.interfaces import ITransformation
    verifyClass(ITransformation, TradeModelLine)

  def test_TradeModelLine_implements_IVariated(self):
    from Products.ERP5Type.Document.TradeModelLine import TradeModelLine
    from Products.ERP5Type.interfaces import IVariated
    verifyClass(IVariated, TradeModelLine)

  def test_Transformation_implements_ITransformation(self):
    from Products.ERP5Type.Document.Transformation import Transformation
    from Products.ERP5Type.interfaces import ITransformation
    verifyClass(ITransformation, Transformation)

  def test_Transformation_implements_IVariated(self):
    from Products.ERP5Type.Document.Transformation import Transformation
    from Products.ERP5Type.interfaces import IVariated
    verifyClass(IVariated, Transformation)

  def test_BusinessPath_implements_IBusinessPath(self):
    from Products.ERP5Type.Document.BusinessPath import BusinessPath
    from Products.ERP5Type.interfaces import IBusinessPath
    verifyClass(IBusinessPath, BusinessPath)

  def test_BusinessPath_implements_IArrow(self):
    from Products.ERP5Type.Document.BusinessPath import BusinessPath
    from Products.ERP5Type.interfaces import IArrow
    verifyClass(IArrow, BusinessPath)

  def test_BusinessPath_implements_ICategoryAccessProvider(self):
    from Products.ERP5Type.Document.BusinessPath import BusinessPath
    from Products.ERP5Type.interfaces import ICategoryAccessProvider
    verifyClass(ICategoryAccessProvider, BusinessPath)

  def test_TradeModelRule_implements_IRule(self):
    from Products.ERP5Type.Document.TradeModelRule import TradeModelRule
    from Products.ERP5Type.interfaces import IRule
    verifyClass(IRule, TradeModelRule)

  def test_TradeModelRule_implements_IPredicate(self):
    from Products.ERP5Type.Document.TradeModelRule import TradeModelRule
    from Products.ERP5Type.interfaces import IPredicate
    verifyClass(IPredicate, TradeModelRule)

  def test_TransformationRule_implements_IRule(self):
    from Products.ERP5Type.Document.TransformationRule import TransformationRule
    from Products.ERP5Type.interfaces import IRule
    verifyClass(IRule, TransformationRule)

  def test_TransformationRule_implements_IPredicate(self):
    from Products.ERP5Type.Document.TransformationRule import TransformationRule
    from Products.ERP5Type.interfaces import IPredicate
    verifyClass(IPredicate, TransformationRule)

  def test_TransformedResource_implements_IVariated(self):
    from Products.ERP5Type.Document.TransformedResource import TransformedResource
    from Products.ERP5Type.interfaces import IVariated
    verifyClass(IVariated, TransformedResource)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Interfaces))
  return suite
