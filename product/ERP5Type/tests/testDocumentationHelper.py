##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                 Mayoro DIAGNE <mayoro@gmail.com>
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

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.DocumentationHelper.ERP5SiteDocumentationHelper \
    import ERP5SiteDocumentationHelper
from Products.ERP5Type.DocumentationHelper.BusinessTemplateDocumentationHelper \
    import BusinessTemplateDocumentationHelper
from zLOG import LOG


class TestDocumentationHelper(ERP5TypeTestCase):
  """
  This is the list of test

  """
  auth = "ERP5TypeTestCase:"
  run_all_test = 1
 
  def getTitle(self):
    return "DocumentationHelper"

  def afterSetUp(self):
    self.login()

  def getBusinessTemplateList(self):
    """return list of business templates to be installed. """
    return ( 'erp5_documentation',
             'erp5_core',
             'erp5_xhtml_style',
             'erp5_ui_test',
            )

  def test_01_ERP5Site(self):
    ZopeTestCase._print('\nTest Documentation ERP5Site')
    LOG('Testing... ', 0, 'Documentation of test_01_ERP5Site')
    site_uri = self.portal.getUrl()
    site_do = ERP5SiteDocumentationHelper(site_uri).__of__(self.portal)
    self.assertEquals(len(site_do.getSectionList()), 1)
    #just erp5_core, erp5_mysql_innodb_catalog, erp5_documentation
    #, erp5_xhtml_style and erp5_ui_test are installed 
    self.assertEquals(len(site_do.getBusinessTemplateIdList()), 5)
    self.portal.portal_classes.getDocumentationHelper(
        'ERP5SiteDocumentationHelper', site_uri)
    #test the report mode of the documentation of the whole site
    self.portal.REQUEST['class_name'] = 'ERP5SiteDocumentationHelper'
    self.portal.REQUEST['uri'] = site_uri
    self.portal.portal_classes.DocumentationHelper_viewReport()

  def test_02_bt(self):
    ZopeTestCase._print('\nTest Documentation Business Template')
    LOG('Testing... ', 0, 'Documentation of test_02_bt')
    bt_ui_test = self.portal.portal_templates.getInstalledBusinessTemplate('erp5_ui_test')
    bt_uri = bt_ui_test.getUrl()
    #do means documented_object
    bt_do = BusinessTemplateDocumentationHelper(bt_uri).__of__(self.portal)
    self.assertEquals(len(bt_do.getSectionList()), 7)
    self.assertTrue('Foo' in bt_do.getPortalTypeIdList())
    self.assertTrue('Bar' in bt_do.getPortalTypeIdList())
    self.assertTrue('foo_module' in bt_do.getModuleIdList())
    self.assertTrue('bar_module' in bt_do.getModuleIdList())
    self.portal.portal_classes.getDocumentationHelper(
        'BusinessTemplateDocumentationHelper', bt_uri)
    self.portal.REQUEST['class_name'] = 'ERP5SiteDocumentationHelper'
    self.portal.REQUEST['uri'] = bt_uri
    self.portal.portal_classes.DocumentationHelper_viewReport()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestDocumentationHelper))
  return suite

