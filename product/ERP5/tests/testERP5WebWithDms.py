##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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
import re
import unittest
import random

from AccessControl import Unauthorized
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import DummyLocalizer
from Products.ERP5Type.tests.utils import createZODBPythonScript

LANGUAGE_LIST = ('en', 'fr', 'de', 'bg',)

class TestERP5WebWithDms(ERP5TypeTestCase, ZopeTestCase.Functional):
  """Test for erp5_web business template.
  """
  run_all_test = 1
  quiet = 0
  manager_username = 'zope'
  manager_password = 'zope'
  website_id = 'test'


  def getTitle(self):
    return "ERP5WebWithDms"

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser(self.manager_username, self.manager_password, ['Manager'], [])
    user = uf.getUserById(self.manager_username).__of__(uf)
    newSecurityManager(None, user)

  def getBusinessTemplateList(self):
    """
    Return the list of required business templates.
    """
    return ('erp5_base',
            'erp5_web',
            'erp5_dms',
            'erp5_dms_mysql_innodb_catalog',
            )

  def afterSetUp(self):
    self.login()
    portal = self.getPortal()
    self.web_page_module = self.portal.web_page_module
    self.web_site_module = self.portal.web_site_module
    self.portal_id = self.portal.getId()

  def beforeTearDown(self):
    get_transaction().abort()
    def clearModule(module):
      module.manage_delObjects(list(module.objectIds()))
      get_transaction().commit()
      self.tic()
    clearModule(self.portal.web_site_module)
    clearModule(self.portal.web_page_module)

  def setupWebSite(self, **kw):
    """
      Setup Web Site
    """
    portal = self.getPortal()
    request = self.app.REQUEST

    # add supported languages for Localizer
    localizer = portal.Localizer
    for language in LANGUAGE_LIST:
      localizer.manage_addLanguage(language = language)

    # create website
    if hasattr(self.web_site_module, self.website_id):
      self.web_site_module.manage_delObjects(self.website_id)
    website = self.getPortal().web_site_module.newContent(portal_type = 'Web Site',
                                                          id = self.website_id,
                                                          **kw)
    get_transaction().commit()
    self.tic()
    return website

  def setupWebSection(self, **kw):
    """
      Setup Web Section
    """
    web_site_module = self.portal.getDefaultModule('Web Site')
    website = web_site_module[self.website_id]
    websection = website.newContent(portal_type='Web Section', **kw)
    self.websection = websection
    kw = dict(criterion_property_list = 'portal_type',
              membership_criterion_base_category_list='',
              membership_criterion_category_list='')
    websection.edit(**kw)
    websection.setCriterion(property='portal_type',
                            identity=['Web Page'],
                            max='',
                            min='')

    get_transaction().commit()
    self.tic()
    return websection


  def setupWebSitePages(self, prefix, suffix=None, version='0.1',
                        language_list=LANGUAGE_LIST, **kw):
    """
      Setup some Web Pages.
    """
    webpage_list = []
    portal = self.getPortal()
    request = self.app.REQUEST
    web_site_module = self.portal.getDefaultModule('Web Site')
    website = web_site_module[self.website_id]

    # create sample web pages
    for language in language_list:
      if suffix is not None:
        reference = '%s-%s' % (prefix, language)
      else:
        reference = prefix
      webpage = self.web_page_module.newContent(portal_type='Web Page',
                                                reference=reference,
                                                version=version,
                                                language=language,
                                                **kw)
      webpage.publish()
      get_transaction().commit()
      self.tic()
      self.assertEquals(language, webpage.getLanguage())
      self.assertEquals(reference, webpage.getReference())
      self.assertEquals(version, webpage.getVersion())
      self.assertEquals('published', webpage.getValidationState())
      webpage_list.append(webpage)

    return webpage_list

  def test_01_WebPageVersioning(self, quiet=quiet, run=run_all_test):
    """
      Simple Case of showing the proper most recent public Web Page based on
      (language, version)
    """
    if not run: return
    if not quiet:
      message = '\ntest_01_WebPageVersioning'
      ZopeTestCase._print(message)
    portal = self.getPortal()
    request = self.app.REQUEST
    website = self.setupWebSite()
    websection = self.setupWebSection()
    page_reference = 'default-webpage-versionning'
    webpage_list  = self.setupWebSitePages(prefix = page_reference)

    # set default web page for section
    found_by_reference = portal.portal_catalog(reference = page_reference,
                                               language = 'en',
                                               portal_type = 'Web Page')
    en_01 =  found_by_reference[0].getObject()
    # set it as default web page for section
    websection.edit(categories_list = ['aggregate/%s' %en_01.getRelativeUrl(),])
    self.assertEqual([en_01.getReference(),],
                      websection.getAggregateReferenceList())

    # create manually a copy of 'en_01' with higher version and check that
    # older version is archived and new one is show as default web page for section
    en_02 = self.web_page_module.newContent(portal_type = 'Web Page',
                                            reference = page_reference,
                                            version = 0.2,
                                            language = 'en')
    en_02.publish()
    en_02.reindexObject()
    get_transaction().commit()
    self.tic()

    # is old archived?
    self.assertEquals('archived', en_01.getValidationState())

    # is new public and default web page for section?
    portal.Localizer.manage_changeDefaultLang(language = 'en')
    default_document = websection.getDefaultDocumentValue()
    self.assertEquals(en_02, default_document)
    self.assertEquals('en', default_document.getLanguage())
    self.assertEquals('0.2', default_document.getVersion())
    self.assertEquals('published', default_document.getValidationState())

  def test_02_WebSectionAuthorizationForced(self, quiet=quiet, run=run_all_test):
    """ Check that when a document is requested within a Web Section we have a chance to
        require user to login.
        Whether or not an user will login is controlled by a property on Web Section (authorization_forced).
    """
    if not run: return
    if not quiet:
      message = '\ntest_02_WebSectionAuthorizationForced'
      ZopeTestCase._print(message)
    request = self.app.REQUEST
    website = self.setupWebSite()
    websection = self.setupWebSection()
    webpage_list  = self.setupWebSitePages(prefix = 'test-web-page')
    webpage = webpage_list[0]
    document_reference = 'default-document-reference'
    document = self.portal.web_page_module.newContent(
                                      portal_type = 'Web Page',
                                      reference = document_reference)
    document.release()
    website.setAuthorizationForced(0)
    websection.setAuthorizationForced(0)
    get_transaction().commit()
    self.tic()

    # make sure that _getExtensibleContent will return the same document
    # there's not other way to test otherwise URL traversal
    self.assertEqual(document.getUid(),
                           websection._getExtensibleContent(request,  document_reference).getUid())

    # Anonymous User should have in the request header for not found when
    # viewing non available document in Web Section (with no authorization_forced)
    self.logout()
    self.assertEqual(None,  websection._getExtensibleContent(request,  document_reference))
    self.assertEqual('404 Not Found',  request.RESPONSE.getHeader('status'))

    # set authorization_forced flag
    self.login()
    websection.setAuthorizationForced(1)

    # check Unauthorized exception is raised for anonymous
    # this exception is usually caught and user is redirecetd to login form
    self.logout()
    self.assertRaises(Unauthorized,  websection._getExtensibleContent,  request,  document_reference)

  def test_03_LatestContent(self, quiet=quiet, run=run_all_test):
    """ Test latest content for a Web Section. Test different use case like languaeg, workflow state.
   """
    if not run: return
    if not quiet:
      message = '\ntest_03_LatestContent'
      ZopeTestCase._print(message)
    portal = self.getPortal()
    website = self.setupWebSite()
    websection = self.setupWebSection()
    portal_categories = portal.portal_categories
    publication_section_category_id_list = ['documentation',  'administration']
    for category_id in publication_section_category_id_list:
      portal_categories.publication_section.newContent(portal_type = 'Category',
                                                                             id = category_id)
    #set predicate on web section using 'publication_section'
    websection.edit(membership_criterion_base_category = ['publication_section'],
                            membership_criterion_category=['publication_section/%s'
                                                                              %publication_section_category_id_list[0]])
    get_transaction().commit()
    self.tic()

    self.assertEquals(0,  len(websection.getDocumentValueList()))
    # create pages belonging to this publication_section 'documentation'
    web_page_en = portal.web_page_module.newContent(portal_type = 'Web Page',
                                                 language = 'en',
                                                 publication_section_list=publication_section_category_id_list[:1])
    web_page_en.publish()
    get_transaction().commit()
    self.tic()
    self.assertEquals(1,  len(websection.getDocumentValueList(language='en')))
    self.assertEquals(web_page_en,  websection.getDocumentValueList(language='en')[0].getObject())

    # create pages belonging to this publication_section 'documentation' but for 'bg' language
    web_page_bg = portal.web_page_module.newContent(portal_type = 'Web Page',
                                                 language = 'bg',
                                                 publication_section_list=publication_section_category_id_list[:1])
    web_page_bg.publish()
    get_transaction().commit()
    self.tic()
    self.assertEquals(1,  len(websection.getDocumentValueList(language='bg')))
    self.assertEquals(web_page_bg,  websection.getDocumentValueList(language='bg')[0].getObject())

    # reject page
    web_page_bg.reject()
    get_transaction().commit()
    self.tic()
    self.assertEquals(0,  len(websection.getDocumentValueList(language='bg')))

    # publish page and search without a language (by default system should return 'en' docs only)
    web_page_bg.publish()
    get_transaction().commit()
    self.tic()
    self.assertEquals(1,  len(websection.getDocumentValueList()))
    self.assertEquals(web_page_en,  websection.getDocumentValueList()[0].getObject())

  def test_04_WebSectionAuthorizationForcedForDefaultDocument(self, quiet=quiet, run=run_all_test):
    """ Check that when a Web Section contains a default document not accessible by user we have a chance to
        require user to login.
        Whether or not an user will login is controlled by a property on Web Section (authorization_forced).
    """
    if not run: return
    if not quiet:
      message = '\ntest_04_WebSectionAuthorizationForcedForDefaultDocument'
      ZopeTestCase._print(message)
    request = self.app.REQUEST
    website = self.setupWebSite()
    websection = self.setupWebSection()
    web_page_reference = 'default-document-reference'
    web_page_en = self.portal.web_page_module.newContent(
                                      portal_type = 'Web Page',
                                      language = 'en',
                                      reference = web_page_reference)
    # this way it's not viewable by anonymous and we can test
    web_page_en.releaseAlive()
    websection.setAggregateValue(web_page_en)
    websection.setAuthorizationForced(1)
    get_transaction().commit()
    self.tic()

    # make sure that getDefaultDocumentValue() will return the same document for logged in user
    # if default document is accessible
    self.assertEqual(web_page_en.getUid(),
                           websection.getDefaultDocumentValue().getUid())

    # check Unauthorized exception is raised for anonymous when authorization_forced is set
    self.logout()
    self.assertEqual(None,  websection.getDefaultDocumentValue())
    self.assertRaises(Unauthorized,  websection)

    # Anonymous User should not get Unauthorized when authorization_forced is not set
    self.login()
    websection.setAuthorizationForced(0)
    get_transaction().commit()
    self.tic()

    self.logout()
    self.assertEqual(None,  websection.getDefaultDocumentValue())
    try:
      websection()
    except Unauthorized:
      self.fail("Web Section should not prompt user for login.")

    self.login()
    web_page_list = []
    for iteration in range(0, 10):
      web_page =self.getPortal().web_page_module.newContent(portal_type = 'Web Page',
                                                            reference = "%s_%s" % (web_page_reference, iteration),
                                                            language = 'en',)
      web_page.publish()
      self.tic()
      get_transaction().commit()
      web_page_list.append(web_page)
    websection.setAggregateValueList(web_page_list)
    self.tic()
    get_transaction().commit()
    self.assertEqual(5, len(websection.getDocumentValueList(limit=5)))

  def test_05_deadProxyFields(self, quiet=quiet, run=run_all_test):
    """
    check that all proxy fields defined in business templates have a valid
     target
    """
    if not run: return
    if not quiet:
      message = '\ntest_05_deadProxyFields'
      ZopeTestCase._print(message)
    skins_tool = self.portal.portal_skins
    for field_path, field in skins_tool.ZopeFind(
              skins_tool, obj_metatypes=['ProxyField'], search_sub=1):
      self.assertNotEqual(None, field.getTemplateField(),
          '%s\nform_id:%s\nfield_id:%s\n' % (field_path,
                                             field.get_value('form_id'),
                                             field.get_value('field_id')))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5WebWithDms))
  return suite
