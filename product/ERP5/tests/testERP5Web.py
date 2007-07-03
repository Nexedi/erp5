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
import unittest

from AccessControl.SecurityManagement import newSecurityManager
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

LANGUAGE_LIST = ('en', 'fr', 'de', 'bg',)

class TestERP5Web(ERP5TypeTestCase, ZopeTestCase.Functional):
  """Test for erp5_web business template.
  """
  run_all_test = 1
  quiet = 0
  manager_username = 'zope'
  manager_password = 'zope'
  website_id = 'test'


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
    return ('erp5_base', 'erp5_web', 
            'erp5_dms', 'erp5_dms_mysql_innodb_catalog',)

  def afterSetUp(self):
    self.login()
    portal = self.getPortal()
    self.web_page_module = self.portal.web_page_module
    self.web_site_module = self.portal.web_site_module
    self.portal_id = self.portal.getId()

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
    websection = website.newContent(portal_type = 'Web Section', **kw)
    self.websection = websection
    kw = dict(criterion_property_list = 'portal_type',
              membership_criterion_base_category_list = '',
              membership_criterion_category_list = '',)
    websection.edit(**kw)
    websection.setCriterion(property = 'portal_type',
                            identity = ['Web Page'],
                            max = '', 
                            min = '')
                            
    get_transaction().commit()
    self.tic()
    return websection
   

  def setupWebSitePages(self,
                        prefix,
                        suffix = None, 
                        version = '0.1', 
                        language_list = LANGUAGE_LIST):
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
        reference = '%s-%s' %(prefix, language)
      else:
        reference = prefix
      webpage = self.web_page_module.newContent(portal_type = 'Web Page', 
                                                reference = reference,
                                                version = version,
                                                language = language)
      webpage.publish()
      webpage.reindexObject()
      self.assertEquals(language, webpage.getLanguage())
      self.assertEquals(reference, webpage.getReference())
      self.assertEquals(version, webpage.getVersion())
      self.assertEquals('published', webpage.getValidationState())
      webpage_list.append(webpage)
    
    get_transaction().commit()
    self.tic()
    return webpage_list
    

  def test_01_WebSiteRecatalog(self, quiet=quiet, run=run_all_test):
    """
      Test that a recataloging works for Web Site documents
    """
    if not run:
      return
    if not quiet:
      message = '\ntest_01_WebSiteRecatalog'
      ZopeTestCase._print(message)
    
    self.setupWebSite()
    portal = self.getPortal()
    web_site_module = self.portal.getDefaultModule('Web Site')
    web_site = web_site_module[self.website_id]

    self.assertTrue(web_site is not None)
    # Recatalog the Web Site document
    portal_catalog = self.getCatalogTool()
    try:
      portal_catalog.catalog_object(web_site)
    except:
      self.fail('Cataloging of the Web Site failed.')


  def test_02_EditSimpleWebPage(self, quiet=quiet, run=run_all_test):
    """
      Simple Case of creating a web page.
    """
    if not run:
      return
    if not quiet:
      message = '\ntest_02_EditSimpleWebPage'
      ZopeTestCase._print(message)
    page = self.web_page_module.newContent(portal_type='Web Page')
    page.edit(text_content='<b>OK</b>')
    self.assertEquals('text/html', page.getTextFormat())
    self.assertEquals('<b>OK</b>', page.getTextContent())
    
  def test_03_CreateWebSiteUser(self, quiet=quiet, run=run_all_test):
    """
      Create Web site User.
    """
    if not run:
      return
    if not quiet:
      message = '\ntest_03_CreateWebSiteUser'
      ZopeTestCase._print(message)
    self.setupWebSite()
    portal = self.getPortal()
    request = self.app.REQUEST
    kw = dict(reference = 'web',
              first_name = 'TestFN',
              last_name = 'TestLN',
              default_email_text = 'test@test.com',
              password = 'abc',
              password_confirm = 'abc',)
    for key, item in kw.items():
      request.set('field_your_%s' %key, item)
    website = portal.web_site_module[self.website_id]
    website.WebSite_createWebSiteAccount()
    
    # find person object by reference
    person = website.ERP5Site_getAuthenticatedMemberPersonValue(kw['reference'])
    self.assertEquals(person.getReference(), kw['reference'])
    self.assertEquals(person.getFirstName(), kw['first_name'])
    self.assertEquals(person.getLastName(), kw['last_name'])
    self.assertEquals(person.getDefaultEmailText(), kw['default_email_text'])
    self.assertEquals(person.getValidationState(), 'validated')

    # check if user account is 'loggable' 
    uf = portal.acl_users
    user = uf.getUserById( kw['reference'])
    self.assertEquals(str(user),  kw['reference'])
    self.assertEquals(1, user.has_role(('Member', 'Authenticated',)))
    
  def test_04_WebPageTranslation(self, quiet=quiet, run=run_all_test):
    """
      Simple Case of showing the proper Web Page based on 
      current user selected language in browser.
    """
    if not run:
      return
    if not quiet:
      message = '\ntest_04_WebPageTranslation'
      ZopeTestCase._print(message)
    portal = self.getPortal()
    request = self.app.REQUEST
    website = self.setupWebSite()
    websection = self.setupWebSection()
    page_reference = 'default-webpage'
    webpage_list  = self.setupWebSitePages(prefix = page_reference)
   
    # set default web page for section
    found_by_reference = portal.portal_catalog(name = page_reference,
                                               portal_type = 'Web Page')
    found =  found_by_reference[0].getObject()
    websection.edit(categories_list = ['aggregate/%s' %found.getRelativeUrl(),])
    self.assertEqual([found.getReference(),],
                      websection.getAggregateReferenceList())
    # even though we create many pages we should get only one
    # this is the most recent one since all share the same reference
    self.assertEquals(1, len(websection.WebSection_getDocumentValueList()))
     
    # use already created few pages in different languages with same reference
    # and check that we always get the right one based on selected 
    # by us language
    for language in LANGUAGE_LIST:
      # set default language in Localizer only to check that we get
      # the corresponding web page for language. 
      # XXX: Extend API so we can select language from REQUEST
      portal.Localizer.manage_changeDefaultLang(language = language)
      default_document = websection.getDefaultDocumentValue()
      self.assertEquals(language, default_document.getLanguage())

  def test_05_WebPageVersioning(self, quiet=quiet, run=run_all_test):
    """
      Simple Case of showing the proper most recent public Web Page based on 
      (language, version
    """
    if not run:
      return
    if not quiet:
      message = '\ntest_05_WebPageVersioning'
      ZopeTestCase._print(message)
    portal = self.getPortal()
    request = self.app.REQUEST
    website = self.setupWebSite()
    websection = self.setupWebSection()
    page_reference = 'default-webpage-versionning'
    webpage_list  = self.setupWebSitePages(prefix = page_reference)
   
    # set default web page for section
    found_by_reference = portal.portal_catalog(name = page_reference,
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

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Web))
  return suite

