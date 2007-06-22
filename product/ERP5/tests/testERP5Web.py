##############################################################################
#
# Copyright (c) 2004, 2005, 2006 Nexedi SARL and Contributors. 
# All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
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

import os
import sys
import unittest

from AccessControl.SecurityManagement import newSecurityManager
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

HTTP_OK = 200
HTTP_UNAUTHORIZED = 401
HTTP_REDIRECT = 302

class TestERP5Web(ERP5TypeTestCase, ZopeTestCase.Functional):
  """Test for erp5_web business template.
  """
  run_all_test = 1
  quiet = 1
  manager_username = 'zope'
  manager_password = 'zope'

  web_site_portal_type = 'Web Site'

  def getTitle(self):
    return "ERP5Web"

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser(self.manager_username, self.manager_password, ['Manager'], [])
    user = uf.getUserById(self.manager_username).__of__(uf)
    newSecurityManager(None, user)

  def getBusinessTemplateList(self):
    """
    Return the list of required business templates.
    """
    return ('erp5_base', 'erp5_web')

  def afterSetUp(self):
    self.login()
    self.portal = self.getPortal()
    self.web_page_module = self.portal.web_page_module
    self.portal_id = self.portal.getId()
    self.auth = '%s:%s' % (self.manager_username, self.manager_password)

  def test_01_WebSite_recatalog(self, quiet=quiet, run=run_all_test):
    """
      Test that a recataloging works for Web Site documents
    """
    if not run: return

    # Create new Web Site document
    portal = self.getPortal()
    web_site_module = self.portal.getDefaultModule(self.web_site_portal_type)
    web_site = web_site_module.newContent(portal_type=self.web_site_portal_type)
    self.assertTrue(web_site is not None)
    # Recatalog the Web Site document
    portal_catalog = self.getCatalogTool()
    try:
      portal_catalog.catalog_object(web_site)
    except:
      self.fail('Cataloging of the Web Site failed.')


  def test_SimpleWebPage(self):
    """Simple Case of creating a web page.
    """
    page = self.web_page_module.newContent(portal_type='Web Page')
    page.edit(text_content='<b>OK</b>')
    self.assertEquals('text/html', page.getTextFormat())
    self.assertEquals('<b>OK</b>', page.getTextContent())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Web))
  return suite

