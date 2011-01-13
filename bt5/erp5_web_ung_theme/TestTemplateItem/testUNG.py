##############################################################################
#
# Copyright (c) 2002-2011 Nexedi SA and Contributors. All Rights Reserved.
#                         Gabriel M. Monnerat <gabriel@tiolive.com>
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from DateTime import DateTime
import transaction

class TestUNG(ERP5TypeTestCase):
  """
    UNG Test Case
  """

  def getTitle(self):
    return "UNG Tests"

  def getBusinessTemplateList(self):
    return ('erp5_base',
            'erp5_ingestion',
            'erp5_web',
            'erp5_dms',
            'erp5_jquery',
            'erp5_jquery_plugin_mbmenu',
            'erp5_jquery_plugin_sheet',
            'erp5_jquery_ui',
            'erp5_jquery_plugin_jqchart',
            'erp5_jquery_plugin_colorpicker',
            'erp5_jquery_plugin_elastic',
            'erp5_jquery_sheet_editor',
            'erp5_jquery_plugin_hotkey',
            'erp5_jquery_plugin_jgraduate',
            'erp5_jquery_plugin_svgicon',
            'erp5_jquery_plugin_jquerybbq',
            'erp5_jquery_plugin_spinbtn',
            'erp5_jquery_plugin_svg_editor',
            'erp5_svg_editor',
            'erp5_xinha_editor',
            'erp5_knowledge_pad',
            'erp5_ingestion_mysql_innodb_catalog',
            'erp5_web_ung_core',
            'erp5_web_ung_role',
            'erp5_web_ung_theme')

  def createDocumentUsingTemplate(self, template):
    self.portal.ERP5Site_createNewWebDocument(template)
    transaction.commit()
    self.tic()

  def testERP5Site_createNewWebDocument(self):
    """
      Test if the script creates the objects using Templates correctly
      XXX - Refactor tests to better validate the creation of objects
    """
    self.createDocumentUsingTemplate("web_page_template")
    web_page_search = self.portal.portal_catalog(portal_type="Web Page",
                                                reference="default-Web.Page.Reference")
    self.assertEquals(2, len(web_page_search))
    self.createDocumentUsingTemplate("web_table_template")
    web_table_search = self.portal.portal_catalog(portal_type="Web Table",
                                                reference="default-Web.Table.Reference")
    self.assertEquals(2, len(web_table_search))
    self.createDocumentUsingTemplate("web_illustration_template")
    web_illustration_search = self.portal.portal_catalog(portal_type="Web Illustration",
                                                reference="default-Web.Illustration.Reference")
    self.assertEquals(2, len(web_illustration_search))