##############################################################################
#
# Copyright (c) 2014 Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import unittest

from Products.ERP5Type.tests.testFunctionalCore import \
        TestZeleniumCore

# monkey patch SelectionTool.isAnonymous to render as anonymous selection.
from Products.ERP5Form.Tool.SelectionTool import SelectionTool
SelectionTool.isAnonymous = lambda *args, **kw:True

class TestAnonymousSelection(TestZeleniumCore):
  foreground = 0

  def getBusinessTemplateList(self):
    """
    Return the list of business templates.
    """
    return ('erp5_core_proxy_field_legacy',
            'erp5_base', 'erp5_ui_test_core', 'erp5_ui_test', 'erp5_crm', 'erp5_forge',
            'erp5_l10n_fa',
             )

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestAnonymousSelection))
  return suite