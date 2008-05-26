##############################################################################
#
# Copyright (c) 2008 Nexedi SARL and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import unittest

from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.CMFCore.Expression import Expression
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class TestBug875(ERP5TypeTestCase):
  """#875: Unexpected Unauthorized exceptions in restricted code,
           probably due to a bug in Acquisition
  """
  expression = 'python: here.getPortalType() or 1'

  def getBusinessTemplateList(self):
    return 'erp5_base',

  def afterSetUp(self):
    self.login()

    self.getCatalogTool().getSQLCatalog().filter_dict['z_catalog_object_list'] \
      = dict(filtered=1, type=[], expression=self.expression,
             expression_instance=Expression(self.expression))

    createZODBPythonScript(self.getSkinsTool().custom,
                           'Base_immediateReindexObject',
                           '',
                           'context.immediateReindexObject()'
                          ).manage_proxy(('Manager',))

  def test(self):
    self.getPortal().person_module.newContent().Base_immediateReindexObject()


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestBug875))
  return suite
