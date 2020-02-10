# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import (
  ERP5TypeTestCase, failed_portal_installation)

class TestERP5Site(ERP5TypeTestCase):

  def getPortalName(self):
    return self._testMethodName

  def setUp(self): #pylint: disable=method-hidden
    pass

  def test_00_fillSQL(self):
    """
    A empty test that is run first, only to make sure that the other test
    tries to create an ERP5 Site with a non-empty SQL database.
    """
    super(TestERP5Site, self).setUp()
    self.assertNotIn(self.getPortalName(), failed_portal_installation)

  def test_01_do_not_wipe_SQL_data_by_default(self):
    """
    Unless wanted explicitely by the user, creating an ERP5 Site must fail
    if the given SQL parameters give access to a database that already contains
    data. This prevents existing SQL databases from being wiped mistakenly.
    """
    kw = self._getSiteCreationParameterDict()
    del kw['sql_reset']
    self._getSiteCreationParameterDict = lambda: kw
    self.assertRaisesRegexp(Exception, "not empty",
      super(TestERP5Site, self).setUp)
    self.assertFalse(hasattr(self, 'portal'))
    self.assertIn(self.getPortalName(), failed_portal_installation)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Site))
  return suite
