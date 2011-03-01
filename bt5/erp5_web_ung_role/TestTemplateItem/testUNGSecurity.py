##############################################################################
#
# Copyright (c) 2002-2011 Nexedi SA and Contributors. All Rights Reserved.
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
from zExceptions import Unauthorized

class TestUNGSecurity(ERP5TypeTestCase):
  """"""

  def getTitle(self):
    return "Test UNG Security"

  def getBusinessTemplateList(self):
    """Tuple of Business Templates we need to install"""
    return ('erp5_base',
            'erp5_web',
            'erp5_ingestion_mysql_innodb_catalog',
            'erp5_ingestion',
            'erp5_dms',
            'erp5_crm',
            'erp5_knowledge_pad',
            'erp5_jquery',
            'erp5_jquery_ui',
            'erp5_jquery_plugin_spinbtn',
            'erp5_jquery_plugin_jgraduate',
            'erp5_jquery_plugin_svgicon',
            'erp5_jquery_plugin_hotkey',
            'erp5_jquery_plugin_jquerybbq',
            'erp5_jquery_plugin_svg_editor',
            'erp5_jquery_plugin_sheet',
            'erp5_jquery_plugin_mbmenu',
            'erp5_jquery_plugin_jqchart',
            'erp5_jquery_plugin_colorpicker',
            'erp5_jquery_plugin_elastic',
            'erp5_jquery_plugin_wdcalendar',
            'erp5_jquery_sheet_editor',
            'erp5_xinha_editor',
            'erp5_svg_editor',
            'erp5_web_ung_core',
            'erp5_web_ung_theme',
            'erp5_web_ung_role')
  
  def testERP5Site_createNewWebDocumentAsAnnonymous(self):
    """ """
    self.logout()
    self.assertRaises(Unauthorized,
                      self.portal.ERP5Site_createNewWebDocument,
                      ("web_page_template"))