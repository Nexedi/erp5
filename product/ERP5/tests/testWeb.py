# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
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
"""A unittest for erp5_web"""
import unittest
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager


def setLanguage(portal, language):
  from Products.iHotfix import Context, get_ident, contexts

  localizer = portal.Localizer
  if not language in localizer.get_supported_languages():
    localizer.add_language(language)

  request = portal.REQUEST
  request.environ['HTTP_ACCEPT_LANGUAGE'] = language
  request.environ['PATH_INFO'] = '/'
  
  context = Context(request)
  contexts[get_ident()] = context

  request.processInputs()


class TestWeb(ERP5TypeTestCase):
  """
  Test for erp5_web
  """
  run_all_test = 1
  quiet = 1

  def getBusinessTemplateList(self):
    return ('erp5_base',
            'erp5_dms_mysql_innodb_catalog',
            'erp5_web',
            )

  def getTitle(self):
    return "Web"

  def createUser(self, name, role_list):
    user_folder = self.getPortal().acl_users
    user_folder._doAddUser(name, 'password', role_list, [])

  def changeUser(self, name):
    self.old_user = getSecurityManager().getUser()
    user_folder = self.getPortal().acl_users
    user = user_folder.getUserById(name).__of__(user_folder)
    newSecurityManager(None, user)

  def afterSetUp(self):
    self.createUser('admin', ['Manager'])
    self.createUser('erp5user', ['Auditor', 'Author'])
    get_transaction().commit()
    self.tic()

  def beforeTearDown(self):
    get_transaction().abort()
    def clearModule(module):
      module.manage_delObjects(list(module.objectIds()))
      get_transaction().commit()
      self.tic()
    clearModule(self.portal.web_site_module)
    clearModule(self.portal.web_page_module)

  def testAccessWebPageByReference(self):
    self.changeUser('admin')
    site = self.portal.web_site_module.newContent(portal_type='Web Site',
                                                  id='site')
    section = site.newContent(portal_type='Web Section', id='section')

    get_transaction().commit()
    self.tic()

    section.setCriterionProperty('portal_type')
    section.setCriterion('portal_type', max='', identity=['Web Page'], min='')

    get_transaction().commit()
    self.tic()

    self.changeUser('erp5user')
    page_en = self.portal.web_page_module.newContent(portal_type='Web Page')
    page_en.edit(reference='my-first-web-page',
              language='en',
              version='1',
              text_format='text/plain',
              text_content='Hello, World!')

    get_transaction().commit()
    self.tic()

    page_en.publish()

    get_transaction().commit()
    self.tic()

    page_ja = self.portal.web_page_module.newContent(portal_type='Web Page')
    page_ja.edit(reference='my-first-web-page',
              language='ja',
              version='1',
              text_format='text/plain',
              text_content='こんにちは、世界！')

    get_transaction().commit()
    self.tic()

    page_ja.publish()

    get_transaction().commit()
    self.tic()

    setLanguage(self.portal, 'en')

    target = self.portal.restrictedTraverse('web_site_module/site/section/my-first-web-page')
    self.assertEqual('Hello, World!', target.getTextContent())

    setLanguage(self.portal, 'ja')

    target = self.portal.restrictedTraverse('web_site_module/site/section/my-first-web-page')
    self.assertEqual('こんにちは、世界！', target.getTextContent())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestWeb))
  return suite
