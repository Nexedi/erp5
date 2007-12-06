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

#
# Prepare ERP5 Zelenium Test.
#
# usage: python runUnitTest.py --save [OPTION]... prepareFunctionalTest.py
#

import os
import unittest

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

os.environ['erp5_tests_portal_id'] = 'erp5_portal'

class TestZelenium(ERP5TypeTestCase):
    def getBusinessTemplateList(self):
        """
          Return the list of business templates.
        """
        return ('erp5_base', 'erp5_ui_test', 'erp5_forge',
                'erp5_trade', 'erp5_pdm', 'erp5_pdf_style',
                'erp5_accounting', 'erp5_invoicing', 'erp5_accounting_ui_test',
                'erp5_pdm_ui_test',
                'erp5_web', 'erp5_web_ui_test',
                # 'erp5_accounting_l10n_fr', 'erp5_payroll',
                # 'erp5_payroll_ui_test',
                )

    def testInformation(self):
        self.assert_(False, 'This script is intended to be used with --save option.')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestZelenium))
    return suite
