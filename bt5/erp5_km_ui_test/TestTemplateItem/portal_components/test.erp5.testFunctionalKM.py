##############################################################################
#
# Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.
#                     Kazuhiko <kazuhiko@nexedi.com>
#                     Rafael Monnerat <rafael@nexedi.com>
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

from Products.ERP5Type.tests.ERP5TypeFunctionalTestCase import \
        ERP5TypeFunctionalTestCase

class TestZeleniumKM(ERP5TypeFunctionalTestCase):
  foreground = 0
  # Run only the Knowledge Management Tests.
  run_only = "erp5_km_zuite"

  def getBusinessTemplateList(self):
    """
    Return the list of business templates.
    """
    # XXX This is a rough list, we should drop as much as we can, and
    # keep only minimal
    return ('erp5_core_proxy_field_legacy',
            'erp5_base', 'erp5_ui_test_core', 'erp5_ui_test',
            'erp5_dhtml_style', 'erp5_dhtml_ui_test',
            'erp5_jquery', 'erp5_jquery_ui',
            'erp5_knowledge_pad', 'erp5_pdm',
            'erp5_simulation', 'erp5_trade', 'erp5_ooo_import',
            'erp5_accounting', 'erp5_invoicing',
            'erp5_simplified_invoicing', 'erp5_project',
            'erp5_simulation', 'erp5_simulation_test',
            'erp5_ingestion', 'erp5_ingestion_mysql_innodb_catalog',
            'erp5_web', 'erp5_dms', 'erp5_dms_ui_test',
            'erp5_ui_test_data',
            'erp5_knowledge_pad_ui_test',
            'erp5_credential', 'erp5_rss_style', 'erp5_discussion',
            'erp5_km', 'erp5_km_ui_test_data', 'erp5_km_ui_test',
            'erp5_l10n_fr', 'erp5_crm',
            'erp5_forge',
            'erp5_web_renderjs_ui',
            'erp5_web_renderjs_ui_test_core',
            'erp5_web_renderjs_ui_test',
            )

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestZeleniumKM))
  return suite