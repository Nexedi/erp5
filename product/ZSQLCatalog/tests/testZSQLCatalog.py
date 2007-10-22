##############################################################################
#
# Copyright (c) 2006 Nexedi SA and Contributors. All Rights Reserved.
#          Jerome Perrin <jerome@nexedi.com>
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
import sys

from Products.ZSQLMethods.SQL import SQL as ZSQLMethod
from Products.CMFCore.Expression import Expression

from Products.ZSQLCatalog.SQLCatalog import Catalog as SQLCatalog
from Products.ZSQLCatalog.ZSQLCatalog import ZCatalog as ZSQLCatalog
#from Products.ZSQLCatalog.SQLCatalog import Query

try:
  from transaction import get as get_transaction
except ImportError:
  pass

class TestZSQLCatalog(unittest.TestCase):
  """Tests for ZSQL Catalog.
  """
  def setUp(self):
    self._catalog = ZSQLCatalog()


class TestSQLCatalog(unittest.TestCase):
  """Tests for SQL Catalog.
  """
  def setUp(self):
    self._catalog = SQLCatalog('dummy_catalog')
    self._catalog._setObject('z_dummy_method',
                             ZSQLMethod('z_dummy_method', '', '', '', ''))
    self._catalog.sql_catalog_object_list = ('z_dummy_method', )

  def test_getFilterableMethodList(self):
    self.failUnless(self._catalog.z_dummy_method in
                    self._catalog.getFilterableMethodList())

  def test_manage_editFilter(self):
    request = dict(z_dummy_method_box=1, z_dummy_method_expression='python: 1')
    self._catalog.manage_editFilter(REQUEST=request)
    self.assertTrue(self._catalog.filter_dict.has_key('z_dummy_method'))

  def test_isMethodFiltered(self):
    request = dict(z_dummy_method_box=1, z_dummy_method_expression='python: 1')
    self._catalog.manage_editFilter(REQUEST=request)
    self.assertTrue(self._catalog.isMethodFiltered('z_dummy_method'))
    self.assertFalse(self._catalog.isMethodFiltered('not_exist'))

  def test_getFilterExpression(self):
    request = dict(z_dummy_method_box=1, z_dummy_method_expression='python: 1')
    self._catalog.manage_editFilter(REQUEST=request)
    self.assertEquals('python: 1', self._catalog.getExpression('z_dummy_method'))
    self.assertEquals('', self._catalog.getExpression('not_exists'))

  def test_getFilterExpressionInstance(self):
    request = dict(z_dummy_method_box=1, z_dummy_method_expression='python: 1')
    self._catalog.manage_editFilter(REQUEST=request)
    self.assertTrue(isinstance(
        self._catalog.getExpressionInstance('z_dummy_method'), Expression))
    self.assertEquals(None, self._catalog.getExpressionInstance('not_exists'))

  def test_isPortalTypeSelected(self):
    request = dict(z_dummy_method_box=1, z_dummy_method_type=['Selected'])
    self._catalog.manage_editFilter(REQUEST=request)
    self.assertTrue(
        self._catalog.isPortalTypeSelected('z_dummy_method', 'Selected'))
    self.assertFalse(
        self._catalog.isPortalTypeSelected('z_dummy_method', 'Not Selected'))
    self.assertFalse(
        self._catalog.isPortalTypeSelected('not_exists', 'Selected'))


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestSQLCatalog))
  suite.addTest(unittest.makeSuite(TestZSQLCatalog))
  return suite

