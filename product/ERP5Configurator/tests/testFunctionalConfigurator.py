##############################################################################
#
# Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.
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

class TestZeleniumConfiguratorStandard(ERP5TypeFunctionalTestCase):
  foreground = 0
  run_only = "configurator_standard_zuite"

  def afterSetUp(self):
    url_list = []
    for x in self.portal.test_page_module.objectValues():
      if x.getId() == "user-Howto.Configure.ERP5.for.SMB.With.Configurator":
        url_list.append("test_page_module/"+x.getId())
    self.remote_code_url_list = url_list
    ERP5TypeFunctionalTestCase.afterSetUp(self)

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.
    """
    return ('erp5_core_proxy_field_legacy', 'erp5_full_text_mroonga_catalog',
            'erp5_base', 'erp5_workflow', 'erp5_configurator',
            'erp5_configurator_standard', 'erp5_jquery',
            'erp5_ui_test_core', 'erp5_accounting',
            'erp5_web', 'erp5_ingestion',
            'erp5_jquery', 'erp5_dms', 'erp5_jquery_ui', 'erp5_web',
            'erp5_slideshow_style', 'erp5_knowledge_pad', 'erp5_run_my_doc',
            'erp5_configurator_standard_ui_test',
           )

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestZeleniumConfiguratorStandard))
  return suite
