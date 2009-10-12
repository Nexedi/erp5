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

implements_tuple_list = [
  (('Products.ERP5Type.ObjectMessage', 'ObjectMessage'), 'IObjectMessage'),
  (('Products.ERP5Type.ConsistencyMessage', 'ConsistencyMessage'),
    'IObjectMessage'),
  (('Products.ERP5Type.DivergenceMessage', 'DivergenceMessage'),
    'IObjectMessage'),
  (('Products.ERP5Type.ConsistencyMessage', 'ConsistencyMessage'),
    'IConsistencyMessage'),
  (('Products.ERP5Type.DivergenceMessage', 'DivergenceMessage'),
    'IDivergenceMessage'),
  (('Products.ERP5Type.Tool.TypesTool.TypesTool', 'TypesTool'),
    'IActionProvider'),
  (('Products.ERP5Type.ERP5Type.ERP5TypeInformation', 'ERP5TypeInformation'),
    'IActionProvider'),
  (('Products.ERP5Type.ERP5Type.ERP5TypeInformation', 'ERP5TypeInformation'),
    'ILocalRoleAssignor'),
  (('Products.ERP5Type.Document.ActionInformation', 'ActionInformation'),
    'IAction'),
  (('Products.ERP5Type.Document.RoleInformation', 'RoleInformation'),
    'ILocalRoleGenerator'),
]

class TestERP5TypeInterfaces(ERP5TypeTestCase):
  """Tests implementation of interfaces"""

def makeTestMethod(import_tuple, interface):
  """Common method which checks if documents implements interface"""
  def testMethod(self):
    _temp = __import__(import_tuple[0], globals(), locals(),
        ['%s' % import_tuple[1]])
    Klass = getattr(_temp, import_tuple[1])
    _temp = __import__('Products.ERP5Type.interfaces', globals(), locals(),
        ['%s' % interface])
    Interface = getattr(_temp, interface)

    verifyClass(Interface, Klass)

  return testMethod

def addTestMethodDynamically(test_class, implements_tuple_list):
  """Creates test methods on the fly

    Uses naming
    test_<ImportPathOfClass>_<ImplementationClass>_implements_<InterfaceClass>

    It is possible to use --run_only on those dynamically generated methods"""
  for import_tuple, interface in implements_tuple_list:
    method_name = '_'.join(
      ('test',) + import_tuple + ('implements',) + (interface, )
    )
    method = makeTestMethod(import_tuple, interface)
    setattr(test_class, method_name, method)

# Note: Enable this method when implements_tuple_list will be filled
addTestMethodDynamically(TestERP5TypeInterfaces, implements_tuple_list)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5TypeInterfaces))
  return suite
