##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#                     Kazuhiko <kazuhiko@nexedi.com>
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

import os
import sys
import re
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestNamingConvention(ERP5TypeTestCase):
    def getBusinessTemplateList(self):
        """
          Return the list of business templates.
        """
        return ('erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_accounting',
                'erp5_apparel', 'erp5_mrp', 'erp5_project', 'erp5_dms',
                'erp5_web', 'erp5_csv_style', 'erp5_pdf_style', 'erp5_crm',
                'erp5_budget', 'erp5_item',)

    def testNamingConvention(self):
        result = 'installed templates: %s\n' % repr(self.getBusinessTemplateList())
        result += self.getPortal().portal_skins.erp5_core.ERP5Site_checkNamingConventions(html_output=None)
        problems_re = re.compile('([0-9]+) problems found')
        problems = int(problems_re.search(result).group(1))
        self.assertEquals(0, problems, result)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestNamingConvention))
        return suite
