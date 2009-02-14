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
      (language, version)
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
    
  def test_07_WebPageTextContentSubstitutions(self, quiet=quiet, run=run_all_test):
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

  def test_09_DefaultDocumentForWebSection(self, quiet=quiet, run=run_all_test):
    """
      Testing the default document for a Web Section.

      If a Web Section has a default document defined and if that default
      document is published, then getDefaultDocumentValue on that 
      web section should return the latest version in the most 
      appropriate language of that default document.
        
      Note: due to generic ERP5 Web implementation this test highly depends 
      on WebSection_geDefaulttDocumentValueList
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
                                                 id='section_home',
                                                 language = 'en', 
                                                 reference='NXD-DDP', 
                                                 publication_section_list=publication_section_category_id_list[:1])    
    websection.setAggregateValue(web_page_en)
    get_transaction().commit()
    self.tic()
    self.assertEqual(None, websection.getDefaultDocumentValue())
    # publish it
    web_page_en.publish()
    get_transaction().commit()
    self.tic()
    self.assertEqual(web_page_en, websection.getDefaultDocumentValue())
    # and make sure that the base meta tag which is generated
    # uses the web section rather than the portal
    html_page = websection()
    from Products.ERP5.Document.Document import Document
    base_list = re.findall(Document.base_parser, str(html_page))
    base_url = base_list[0]
    self.assertEqual(base_url, "%s/%s/" % (websection.absolute_url(), websection.getId()))
    
  def test_09b_DefaultDocumentForWebSite(self, quiet=quiet, run=run_all_test):
    """
      Testing the default document for a Web Site.

      If a Web Section has a default document defined and if that default
      document is published, then getDefaultDocumentValue on that 
      web section should return the latest version in the most 
      appropriate language of that default document.
        
      Note: due to generic ERP5 Web implementation this test highly depends 
      on WebSection_geDefaulttDocumentValueList
    """
    if not run: return
    if not quiet:
      message = '\ntest_09b_DefaultDocumentForWebSite'
      ZopeTestCase._print(message)    
    portal = self.getPortal()
    website = self.setupWebSite()
    publication_section_category_id_list = ['documentation',  'administration']
    
    # create pages belonging to this publication_section 'documentation'
    web_page_en = portal.web_page_module.newContent(portal_type = 'Web Page', 
                                                 id='site_home',
                                                 language = 'en', 
                                                 reference='NXD-DDP-Site', 
                                                 publication_section_list=publication_section_category_id_list[:1])    
    website.setAggregateValue(web_page_en)
    get_transaction().commit()
    self.tic()
    self.assertEqual(None, website.getDefaultDocumentValue())
    # publish it
    web_page_en.publish()
    get_transaction().commit()
    self.tic()
    self.assertEqual(web_page_en, website.getDefaultDocumentValue())
    # and make sure that the base meta tag which is generated
    # uses the web site rather than the portal
    html_page = website()
    from Products.ERP5.Document.Document import Document
    base_list = re.findall(Document.base_parser, str(html_page))
    base_url = base_list[0]
    self.assertEqual(base_url, "%s/%s/" % (website.absolute_url(), website.getId()))

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


    self.assertEqual(5, len(websection.getDocumentValueList(limit=5)))

  def test_11_WebSection_getDocumentValueList(self, quiet=quiet, run=run_all_test):
    """ Check getting getDocumentValueList from Web Section.
    """
    if not run:   return
    if not quiet:
      message = '\ntest_11_WebSection_getDocumentValueList'
      ZopeTestCase._print(message)
    portal = self.getPortal()
    website = self.setupWebSite()
    websection = self.setupWebSection()
    publication_section_category_id_list = ['documentation',  'administration']

    #set predicate on web section using 'publication_section'
    websection.edit(membership_criterion_base_category = ['publication_section'],
                     membership_criterion_category=['publication_section/%s' \
                                                    % publication_section_category_id_list[0]])
    # clean up
    self.web_page_module.manage_delObjects(list(self.web_page_module.objectIds()))
    portal.portal_categories.publication_section.manage_delObjects(
                                      list(portal.portal_categories.publication_section.objectIds()))
    # create categories
    for category_id in publication_section_category_id_list:
      portal.portal_categories.publication_section.newContent(portal_type = 'Category',
                                                              id = category_id)

    web_page_list = []
    property_dict = { '01' : dict(language = 'en' , version = "1" , reference = "A"),
                      '02' : dict(language = 'en' , version = "2" , reference = "B"),
                      '03' : dict(language = 'en' , version = "3" , reference = "C"),
                      '04' : dict(language = 'pt' , version = "1" , reference = "A"),
                      '05' : dict(language = 'pt' , version = "2" , reference = "C"),
                      '06' : dict(language = 'pt' , version = "3" , reference = "B"),
                      '07' : dict(language = 'ja' , version = "1" , reference = "C"),
                      '08' : dict(language = 'ja' , version = "2" , reference = "A"),
                      '09' : dict(language = 'ja' , version = "3" , reference = "B"),
                      '10' : dict(language = 'en' , version = "2" , reference = "D"),
                      '11' : dict(language = 'ja' , version = "3" , reference = "E"),
                      '12' : dict(language = 'pt' , version = "3" , reference = "F"),
                      '13' : dict(language = 'en' , version = "3" , reference = "D"),
                      '14' : dict(language = 'ja' , version = "2" , reference = "E"),
                      '15' : dict(language = 'pt' , version = "2" , reference = "F"),
                    }
    sequence_one = property_dict.keys()
    sequence_two = ['01', '13', '12', '09', '06', '15' , '04', '11', '02', '05', '03',
                    '07', '10', '08', '14' ]
    sequence_three = ['05', '12', '13', '14',  '06', '09', '10', '07', '03', '01', '02',
                    '11', '04', '08' , '15']
    
    sequence_count = 0
    for sequence in [ sequence_one , sequence_two , sequence_three ]:
      sequence_count += 1
      if not quiet:
        message = '\ntest_11_WebSection_getDocumentValueList (Sequence %s)' \
                                                                % (sequence_count)
        ZopeTestCase._print(message)

      for key in sequence:
        web_page = self.portal.web_page_module.newContent(
                                  title=key,
                                  portal_type = 'Web Page',
                                  publication_section_list=publication_section_category_id_list[:1])
  
        web_page.edit(**property_dict[key])
        get_transaction().commit()
        self.tic()
        web_page_list.append(web_page)
  
      get_transaction().commit()
      self.tic()
      # in draft state no documents should belong to this Web Section
      self.assertEqual(0, len(websection.getDocumentValueList()))
  
      # when published all web pages should belong to it
      for web_page in web_page_list:
        web_page.publish()
      get_transaction().commit()
      self.tic()
      
      # Test for limit parameter
      self.assertEqual(2, len(websection.getDocumentValueList(limit=2)))

      # Testing for language parameter
      self.assertEqual(4, len(websection.getDocumentValueList()))
      self.assertEqual(['en' , 'en', 'en', 'en'], 
                       [ w.getLanguage()  for w in websection.getDocumentValueList()])
  
      pt_document_value_list = websection.getDocumentValueList(language='pt')
      self.assertEqual(4, len(pt_document_value_list))
      self.assertEqual(['pt' , 'pt', 'pt', 'pt'],
                           [ w.getObject().getLanguage() for w in pt_document_value_list])
  
      ja_document_value_list = websection.getDocumentValueList(language='ja')
      self.assertEqual(4, len(ja_document_value_list))
      self.assertEqual(['ja' , 'ja', 'ja', 'ja'],
                           [ w.getLanguage() for w in ja_document_value_list])

      # Testing for all_versions parameter
      en_document_value_list = websection.getDocumentValueList(all_versions=1)
      self.assertEqual(5, len(en_document_value_list))
      self.assertEqual(['en' , 'en', 'en', 'en', 'en'],
                       [ w.getLanguage()  for w in en_document_value_list])

      pt_document_value_list = websection.getDocumentValueList(language='pt',
                                                               all_versions=1)
      self.assertEqual(5, len(pt_document_value_list))
      self.assertEqual(['pt' , 'pt', 'pt', 'pt', 'pt'],
                           [ w.getObject().getLanguage() for w in pt_document_value_list])

      ja_document_value_list = websection.getDocumentValueList(language='ja', 
                                                               all_versions=1)
      self.assertEqual(5, len(ja_document_value_list))
      self.assertEqual(['ja' , 'ja', 'ja', 'ja', 'ja'],
                           [ w.getLanguage() for w in ja_document_value_list])

      # Tests for all_languages parameter
      en_document_value_list = websection.WebSection_getDocumentValueListBase(all_languages=1)
      self.assertEqual(6, len(en_document_value_list))
      self.assertEqual(4, len([ w.getLanguage() for w in en_document_value_list \
                              if w.getLanguage() == 'en']))
      self.assertEqual(1, len([ w.getLanguage() for w in en_document_value_list \
                              if w.getLanguage() == 'pt']))
      self.assertEqual(['3'], [ w.getVersion() for w in en_document_value_list \
                              if w.getLanguage() == 'pt'])
      self.assertEqual(1, len([ w.getLanguage() for w in en_document_value_list \
                              if w.getLanguage() == 'ja']))
      self.assertEqual(['3'], [ w.getVersion() for w in en_document_value_list \
                              if w.getLanguage() == 'ja'])

      pt_document_value_list = websection.WebSection_getDocumentValueListBase(all_languages=1,
                                                                              language='pt')
      self.assertEqual(6, len(pt_document_value_list))
      self.assertEqual(4, len([ w.getLanguage() for w in pt_document_value_list \
                              if w.getLanguage() == 'pt']))
      self.assertEqual(1, len([ w.getLanguage() for w in pt_document_value_list \
                              if w.getLanguage() == 'en']))
      self.assertEqual(['3'], [ w.getVersion() for w in pt_document_value_list \
                              if w.getLanguage() == 'en'])
      self.assertEqual(1, len([ w.getLanguage() for w in pt_document_value_list \
                              if w.getLanguage() == 'ja']))
      self.assertEqual(['3'], [ w.getVersion() for w in pt_document_value_list \
                              if w.getLanguage() == 'ja'])
  
      ja_document_value_list = websection.WebSection_getDocumentValueListBase(all_languages=1,
                                                                              language='ja')
      self.assertEqual(6, len(ja_document_value_list))
      self.assertEqual(4, len([ w.getLanguage() for w in ja_document_value_list \
                              if w.getLanguage() == 'ja']))
      self.assertEqual(1, len([ w.getLanguage() for w in ja_document_value_list \
                              if w.getLanguage() == 'pt']))
      self.assertEqual(['3'], [ w.getVersion() for w in ja_document_value_list \
                              if w.getLanguage() == 'pt'])
      self.assertEqual(1, len([ w.getLanguage() for w in ja_document_value_list \
                              if w.getLanguage() == 'en']))
      self.assertEqual(['3'], [ w.getVersion() for w in ja_document_value_list \
                            if w.getLanguage() == 'en'])

      # Tests for all_languages and all_versions 
      en_document_value_list = websection.WebSection_getDocumentValueListBase(all_languages=1,
                                                                              all_versions=1)

      pt_document_value_list = websection.WebSection_getDocumentValueListBase(all_languages=1,
                                                                              all_versions=1,
                                                                              language='pt')

      ja_document_value_list = websection.WebSection_getDocumentValueListBase(all_languages=1,
                                                                              all_versions=1,
                                                                              language='ja')

      for document_value_list in [ en_document_value_list, pt_document_value_list , 
                                   ja_document_value_list]:

        self.assertEqual(15, len(document_value_list))
        self.assertEqual(5, len([ w.getLanguage() for w in document_value_list \
                                if w.getLanguage() == 'en']))
        self.assertEqual(5, len([ w.getLanguage() for w in en_document_value_list \
                                if w.getLanguage() == 'pt']))
        self.assertEqual(5, len([ w.getLanguage() for w in en_document_value_list \
                                if w.getLanguage() == 'ja']))

      # Tests for sort_on parameter
      self.assertEqual(['A' , 'B', 'C', 'D'],
                       [ w.getReference()  for w in \
                         websection.getDocumentValueList(sort_on=[('reference', 'ASC')])])

      self.assertEqual(['01' , '02', '03', '13'],
                       [ w.getTitle()  for w in \
                         websection.getDocumentValueList(sort_on=[('title', 'ASC')])])

      self.assertEqual(['D' , 'C', 'B', 'A'],
                       [ w.getReference()  for w in \
                         websection.getDocumentValueList(sort_on=[('reference', 'DESC')])])


      self.assertEqual(['13' , '03', '02', '01'],
                       [ w.getTitle()  for w in \
                         websection.getDocumentValueList(sort_on=[('reference', 'DESC')])])

      self.assertEqual(['A' , 'B', 'C', 'D' , 'E' , 'F'],
                       [ w.getReference()  for w in \
                         websection.WebSection_getDocumentValueListBase(all_languages=1,
                                            sort_on=[('reference', 'ASC')])])
     
      self.assertEqual(['01' , '02', '03', '11' , '12' , '13'],
                       [ w.getTitle()  for w in \
                         websection.WebSection_getDocumentValueListBase(all_languages=1,
                                            sort_on=[('title', 'ASC')])])


      self.assertEqual(['F' , 'E', 'D', 'C' , 'B' , 'A'],
                       [ w.getReference()  for w in \
                         websection.WebSection_getDocumentValueListBase(all_languages=1,
                                            sort_on=[('reference', 'DESC')])])

      self.assertEqual(['13' , '12', '11', '03' , '02' , '01'],
                       [ w.getTitle()  for w in \
                         websection.WebSection_getDocumentValueListBase(all_languages=1,
                                            sort_on=[('title', 'DESC')])])

      self.web_page_module.manage_delObjects(list(self.web_page_module.objectIds()))

  def test_12_AcquisitionWrappers(self, quiet=quiet, run=run_all_test):
    """Test acquisition wrappers of documents.
    Check if documents obtained by getDefaultDocumentValue, getDocumentValue
    and getDocumentValueList are wrapped appropriately.
    """
    if not run: return
    if not quiet:
      message = '\ntest_12_AcquisitionWrappers'
      ZopeTestCase._print(message)    

    portal = self.getPortal()

    # Make its own publication section category.
    publication_section = portal.portal_categories['publication_section']
    if publication_section._getOb('my_test_category', None) is None:
      publication_section.newContent(portal_type='Category',
                                     id='my_test_category',
                                     title='Test')
      get_transaction().commit()
      self.tic()

    website = self.setupWebSite()
    websection = self.setupWebSection(
            membership_criterion_base_category_list=('publication_section',),
            membership_criterion_category=('publication_section/my_test_category',),
            )
    
    # Create at least two documents which belong to the publication section
    # category.
    web_page_list = self.setupWebSitePages('test1',
            language_list=('en',),
            publication_section_list=('my_test_category',))
    web_page_list2 = self.setupWebSitePages('test2',
            language_list=('en',),
            publication_section_list=('my_test_category',))

    # We need a default document.
    websection.setAggregateValue(web_page_list[0])
    get_transaction().commit()
    self.tic()
    
    # Obtain documens in various ways.
    default_document = websection.getDefaultDocumentValue()
    self.assertNotEquals(default_document, None)

    document1 = websection.getDocumentValue('test1')
    self.assertNotEquals(document1, None)
    document2 = websection.getDocumentValue('test2')
    self.assertNotEquals(document2, None)

    document_list = websection.getDocumentValueList()
    self.assertNotEquals(document_list, None)
    self.assertNotEquals(len(document_list), 0)

    # Check if they have good acquisition wrappers.
    for doc in (default_document, document1, document2) + tuple(document_list):
      self.assertEquals(doc.aq_parent, websection)
      self.assertEquals(doc.aq_parent.aq_parent, website)

  def test_13_WebSiteSkinSelection(self, quiet=quiet, run=run_all_test):
    """Test skin selection through a Web Site.
    Check if a Web Site can change a skin selection based on a property.
    """
    if not run: return
    if not quiet:
      message = '\ntest_13_WebSiteSkinSelection'
      ZopeTestCase._print(message)    

    portal = self.getPortal()
    ps = portal.portal_skins
    website = self.setupWebSite()

    # First, make sure that we use the default skin selection.
    portal.changeSkin(ps.getDefaultSkin())
    get_transaction().commit()
    self.tic()

    # Make some skin stuff.
    if ps._getOb('test_erp5_web', None) is not None:
      ps.manage_delObjects(['test_erp5_web'])

    addFolder = ps.manage_addProduct['OFSP'].manage_addFolder
    addFolder(id='test_erp5_web')

    if ps.getSkinPath('Test ERP5 Web') is not None:
      ps.manage_skinLayers(del_skin=1, chosen=('Test ERP5 Web',))
      
    path = ps.getSkinPath(ps.getDefaultSkin())
    self.assertNotEquals(path, None)
    ps.manage_skinLayers(add_skin=1, skinname='Test ERP5 Web',
            skinpath=['test_erp5_web'] + path.split(','))

    # Now we need skins which don't conflict with any other.
    createZODBPythonScript(ps.erp5_web,
            'WebSite_test_13_WebSiteSkinSelection',
            '', 'return "foo"')
    createZODBPythonScript(ps.test_erp5_web,
            'WebSite_test_13_WebSiteSkinSelection',
            '', 'return "bar"')

    get_transaction().commit()
    self.tic()

    path = website.absolute_url_path() + '/WebSite_test_13_WebSiteSkinSelection'
    request = portal.REQUEST

    # With the default skin.
    request['PARENTS'] = [self.app]
    self.assertEquals(request.traverse(path)(), 'foo')

    # With the test skin.
    website.setSkinSelectionName('Test ERP5 Web')
    get_transaction().commit()
    self.tic()

    request['PARENTS'] = [self.app]
    self.assertEquals(request.traverse(path)(), 'bar')

  def test_14_deadProxyFields(self):
    # check that all proxy fields defined in business templates have a valid
    # target
    skins_tool = self.portal.portal_skins
    for field_path, field in skins_tool.ZopeFind(
              skins_tool, obj_metatypes=['ProxyField'], search_sub=1):
      self.assertNotEqual(None, field.getTemplateField(),
          '%s\nform_id:%s\nfield_id:%s\n' % (field_path,
                                             field.get_value('form_id'),
                                             field.get_value('field_id')))

  def test_15_getDocumentValueList(self, quiet=quiet, run=run_all_test):
    """Make sure that getDocumentValueList works."""
    self.setupWebSite()
    website = self.web_site_module[self.website_id]
    website.getDocumentValueList(
      portal_type='Document',
      sort_on=[('translated_portal_type', 'ascending')])


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


  def test_03_WebSection_getDocumentValueListSecurity(self, quiet=quiet, run=run_all_test):
    """ Test WebSection_getDocumentValueList behaviour and security"""
    if not run:
      return
    self.changeUser('admin')
    web_site_module = self.portal.web_site_module
    site = web_site_module.newContent(portal_type='Web Site',
                                      id='site')

    section = site.newContent(portal_type='Web Section', 
                              id='section')

    get_transaction().commit()
    self.tic()

    section.setCriterionProperty('portal_type')
    section.setCriterion('portal_type', max='', 
                         identity=['Web Page'], min='')

    get_transaction().commit()
    self.tic()

    self.changeUser('erp5user')
    page_en_0 = self.portal.web_page_module.newContent(portal_type='Web Page')
    page_en_0.edit(reference='my-first-web-page',
                 language='en',
                 version='1',
                 text_format='text/plain',
                 text_content='Hello, World!')

    page_en_1 = self.portal.web_page_module.newContent(portal_type='Web Page')
    page_en_1.edit(reference='my-first-web-page',
                 language='en',
                 version='2',
                 text_format='text/plain',
                 text_content='Hello, World!')

    page_en_2 = self.portal.web_page_module.newContent(portal_type='Web Page')
    page_en_2.edit(reference='my-second-web-page',
                 language='en',
                 version='2',
                 text_format='text/plain',
                 text_content='Hello, World!')

    page_jp_0 = self.portal.web_page_module.newContent(portal_type='Web Page')
    page_jp_0.edit(reference='my-first-japonese-page',
                 language='jp',
                 version='1',
                 text_format='text/plain',
                 text_content='Hello, World!')



    get_transaction().commit()
    self.changeUser('erp5user')
    self.tic()
    self.portal.Localizer.changeLanguage('en')
      
    self.assertEquals(0, len(section.WebSection_getDocumentValueList()))    

    self.changeUser('erp5user')
    page_en_0.publish()
    get_transaction().commit()
    self.tic()

    self.portal.Localizer.changeLanguage('en')
    self.assertEquals(1, len(section.WebSection_getDocumentValueList()))
    self.assertEquals(page_en_0.getUid(),
                      section.WebSection_getDocumentValueList()[0].getUid())

    self.portal.Localizer.changeLanguage('jp')
    self.assertEquals(0, len(section.WebSection_getDocumentValueList()))

    # By Anonymous
    self.logout()
    self.portal.Localizer.changeLanguage('en')
    self.assertEquals(1, len(section.WebSection_getDocumentValueList()))
    self.assertEquals(page_en_0.getUid(), 
                      section.WebSection_getDocumentValueList()[0].getUid())
    self.portal.Localizer.changeLanguage('jp')
    self.assertEquals(0, len(section.WebSection_getDocumentValueList()))

    # Second Object
    self.changeUser('erp5user')
    page_en_1.publish()
    get_transaction().commit()
    self.tic()

    self.portal.Localizer.changeLanguage('en')
    self.assertEquals(1, len(section.WebSection_getDocumentValueList()))
    self.assertEquals(page_en_1.getUid(), 
                      section.WebSection_getDocumentValueList()[0].getUid())
    self.portal.Localizer.changeLanguage('jp')
    self.assertEquals(0, len(section.WebSection_getDocumentValueList()))

    # By Anonymous
    self.logout()
    self.portal.Localizer.changeLanguage('en')
    self.assertEquals(1, len(section.WebSection_getDocumentValueList()))
    self.assertEquals(page_en_1.getUid(), 
                      section.WebSection_getDocumentValueList()[0].getUid())

    # Trird Object
    self.changeUser('erp5user')
    page_en_2.publish()
    get_transaction().commit()
    self.tic()

    self.portal.Localizer.changeLanguage('en')
    self.assertEquals(2, len(section.WebSection_getDocumentValueList()))
    self.portal.Localizer.changeLanguage('jp')
    self.assertEquals(0, len(section.WebSection_getDocumentValueList()))

    # By Anonymous
    self.logout()
    self.portal.Localizer.changeLanguage('en')
    self.assertEquals(2, len(section.WebSection_getDocumentValueList()))
    self.portal.Localizer.changeLanguage('jp')
    self.assertEquals(0, len(section.WebSection_getDocumentValueList()))

    # First Japanese Object
    self.changeUser('erp5user')
    page_jp_0.publish()
    get_transaction().commit()
    self.tic()

    self.portal.Localizer.changeLanguage('en')
    self.assertEquals(2, len(section.WebSection_getDocumentValueList()))
    self.portal.Localizer.changeLanguage('jp')
    self.assertEquals(1, len(section.WebSection_getDocumentValueList()))

    # By Anonymous
    self.logout()
    self.portal.Localizer.changeLanguage('en')
    self.assertEquals(2, len(section.WebSection_getDocumentValueList()))
    self.portal.Localizer.changeLanguage('jp')
    self.assertEquals(1, len(section.WebSection_getDocumentValueList()))
    self.assertEquals(page_jp_0.getUid(), 
                      section.WebSection_getDocumentValueList()[0].getUid())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Web))
  suite.addTest(unittest.makeSuite(TestERP5WebWithSimpleSecurity))
  return suite
