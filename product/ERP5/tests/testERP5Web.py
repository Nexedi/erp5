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

from AccessControl import Unauthorized
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import DummyLocalizer

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
            'erp5_ingestion', 'erp5_ingestion_mysql_innodb_catalog',
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
    website.WebSite_createWebSiteAccount('WebSite_viewRegistrationDialog')
    
    get_transaction().commit()
    self.tic()
    
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

  def test_06_WebSectionAuthorizationForced(self, quiet=quiet, run=run_all_test):
    """ Check that when a document is requested within a Web Section we have a chance to 
        require user to login.
        Whether or not an user will login is controlled by a property on Web Section (authorization_forced).
    """
    if not run:
      return
    if not quiet:
      message = '\ntest_06_WebSectionAuthorizationForced'
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
    
  def test_07_WebPageTextContentSubstituions(self, quiet=quiet, run=run_all_test):
    """
      Simple Case of showing the proper text content with and without a substitution
      mapping method.
    """
    if not run:
      return
    if not quiet:
      message = '\ntest_07_WebPageTextContentSubstituions'
      ZopeTestCase._print(message)

    content = '<a href="${toto}">$titi</a>'
    substituted_content = '<a href="foo">bar</a>'
    mapping = dict(toto='foo', titi='bar')

    portal = self.getPortal()
    document = portal.web_page_module.newContent(portal_type='Web Page', 
            text_content=content)
   
    # No substitution should occur.
    self.assertEquals(document.asStrippedHTML(), content)

    klass = document.__class__
    klass.getTestSubstitutionMapping = lambda self, **kw: mapping
    document.setTextContentSubstitutionMappingMethodId('getTestSubstitutionMapping')

    # Substitutions should occur.
    self.assertEquals(document.asStrippedHTML(), substituted_content)

    klass._getTestSubstitutionMapping = klass.getTestSubstitutionMapping
    document.setTextContentSubstitutionMappingMethodId('_getTestSubstitutionMapping')

    # Even with the same callable object, a restricted method id should not be callable.
    self.assertRaises(Unauthorized, document.asStrippedHTML)
    
  def test_08_LatestContent(self, quiet=quiet, run=run_all_test):
    """ Test latest content for a Web Section. Test different use case like languaeg, workflow state.
   """
    if not run: return
    if not quiet:
      message = '\ntest_08_LatestContent'
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
    self.assertEquals(1,  len(websection.getDocumentValueList(anguage='en')))
    self.assertEquals(web_page_en,  websection.getDocumentValueList(anguage='en')[0].getObject())
    
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

  def test_09_DefaultDocumentForWebSection(self, quiet=quiet, run=run_all_test):
    """ Testetting default document for a Web Section. Test  use case like workflow state of document.
         Note: due to generic ERP5 Web implementation this test highly depends on WebSection_geDefaulttDocumentValueList
    """
    if not run: return
    if not quiet:
      message = '\ntest_09_DefaultDocumentForWebSection'
      ZopeTestCase._print(message)    
    portal = self.getPortal()
    website = self.setupWebSite()
    websection = self.setupWebSection()
    publication_section_category_id_list = ['documentation',  'administration']
    
    # create pages belonging to this publication_section 'documentation'
    web_page_en = portal.web_page_module.newContent(portal_type = 'Web Page', 
                                                 language = 'en', 
                                                 reference='NXD-DDP', 
                                                 publication_section_list=publication_section_category_id_list[:1])    
    websection.setAggregateValue(web_page_en)
    get_transaction().commit()
    self.tic()
    self.assertEqual(None,   websection.getDefaultDocumentValue())
    # publish it
    web_page_en.publish()
    get_transaction().commit()
    self.tic()
    self.assertEqual(web_page_en,   websection.getDefaultDocumentValue())
    
  def test_10_WebSectionAuthorizationForcedForDefaultDocument(self, quiet=quiet, run=run_all_test):
    """ Check that when a Web Section contains a default document not accessible by user we have a chance to 
        require user to login.
        Whether or not an user will login is controlled by a property on Web Section (authorization_forced).
    """
    if not run:   return
    if not quiet:  
      message = '\ntest_10_WebSectionAuthorizationForcedForDefaultDocument'
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

class TestERP5WebWithSimpleSecurity(ERP5TypeTestCase):
  """
  Test for erp5_web with simple security.
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
    self.portal.Localizer = DummyLocalizer()
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

  def test_01_AccessWebPageByReference(self, quiet=quiet, run=run_all_test):
    if not run:
      return
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

    # By Anonymous
    self.logout()

    self.portal.Localizer.changeLanguage('en')

    target = self.portal.restrictedTraverse('web_site_module/site/section/my-first-web-page')
    self.assertEqual('Hello, World!', target.getTextContent())

    self.portal.Localizer.changeLanguage('ja')

    target = self.portal.restrictedTraverse('web_site_module/site/section/my-first-web-page')
    self.assertEqual('こんにちは、世界！', target.getTextContent())
    
  def test_02_LocalRolesFromRoleDefinition(self, quiet=quiet, run=run_all_test):
    """ Test setting local roles on Web Site/ Web Sectio using ERP5 Role Definition objects . """
    if not run:
      return
    portal = self.portal
    person_reference = 'webuser'
    site = portal.web_site_module.newContent(portal_type='Web Site',
                                                  id='site')
    section = site.newContent(portal_type='Web Section', id='section')
    person = portal.person_module.newContent(portal_type = 'Person', 
                                                                    reference = person_reference)
    # add Role Definition for site and section
    site_role_definition = site.newContent(portal_type = 'Role Definition', 
                                                           role_name = 'Assignee', 
                                                           agent = person.getRelativeUrl())
    section_role_definition = section.newContent(portal_type = 'Role Definition', 
                                                           role_name = 'Associate', 
                                                           agent = person.getRelativeUrl())                                                           
    get_transaction().commit()
    self.tic()
    # check if Role Definition have create local roles
    self.assertSameSet(('Assignee',),  
                                 site.get_local_roles_for_userid(person_reference))
    self.assertSameSet(('Associate',),  
                                 section.get_local_roles_for_userid(person_reference))
                                 
    # delete Role Definition and check again (local roles must be gone too)
    site.manage_delObjects(site_role_definition.getId())
    section.manage_delObjects(section_role_definition.getId())
    get_transaction().commit()
    self.tic()
    self.assertSameSet((),  
                                 site.get_local_roles_for_userid(person_reference))
    self.assertSameSet((),  
                                 section.get_local_roles_for_userid(person_reference))                                 

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Web))
  suite.addTest(unittest.makeSuite(TestERP5WebWithSimpleSecurity))
  return suite
