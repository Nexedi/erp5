##############################################################################
# -*- coding: utf-8 -*-
#
# Copyright (c) 2004, 2005, 2006 Nexedi SARL and Contributors.
# All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import re
import unittest

import transaction
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
    return ('erp5_base',
            'erp5_web',
            )

  def afterSetUp(self):
    self.login()
    portal = self.getPortal()
    self.web_page_module = self.portal.web_page_module
    self.web_site_module = self.portal.web_site_module
    portal.Localizer.manage_changeDefaultLang(language = 'en')
    self.portal_id = self.portal.getId()

  def clearModule(self, module):
    module.manage_delObjects(list(module.objectIds()))
    transaction.commit()
    self.tic()

  def beforeTearDown(self):
    self.clearModule(self.portal.web_site_module)
    self.clearModule(self.portal.web_page_module)
    self.clearModule(self.portal.person_module)

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
    transaction.commit()
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

    transaction.commit()
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
      transaction.commit()
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
    if not run: return
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
    if not run: return
    if not quiet:
      message = '\ntest_02_EditSimpleWebPage'
      ZopeTestCase._print(message)
    page = self.web_page_module.newContent(portal_type='Web Page')
    page.edit(text_content='<b>OK</b>')
    self.assertEquals('text/html', page.getTextFormat())
    self.assertEquals('<b>OK</b>', page.getTextContent())

  def test_02a_WebPageAsText(self, quiet=quiet, run=run_all_test):
    """
      Check if Web Page's asText() returns utf-8 string correctly and
      if it is wrapped by certian column width.
    """
    if not run: return
    if not quiet:
      message = '\ntest_02a_WebPageAsText'
      ZopeTestCase._print(message)
    # disable portal_transforms cache
    self.portal.portal_transforms.max_sec_in_cache=-1
    page = self.web_page_module.newContent(portal_type='Web Page')
    page.edit(text_content='<p>Hé Hé Hé!</p>')
    transaction.commit()
    self.tic()
    self.assertEquals('Hé Hé Hé!', page.asText().strip())
    page.edit(text_content='<p>Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé!</p>')
    transaction.commit()
    self.tic()
    self.assertEquals("""Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé
Hé Hé Hé!""", page.asText().strip())

  def test_03_CreateWebSiteUser(self, quiet=quiet, run=run_all_test):
    """
      Create Web site User.
    """
    if not run: return
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

    transaction.commit()
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
    if not run: return
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

  def test_05_WebPageTextContentSubstitutions(self, quiet=quiet, run=run_all_test):
    """
      Simple Case of showing the proper text content with and without a substitution
      mapping method.
    """
    if not run: return
    if not quiet:
      message = '\ntest_05_WebPageTextContentSubstituions'
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

  def test_06_DefaultDocumentForWebSection(self, quiet=quiet, run=run_all_test):
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
      message = '\ntest_06_DefaultDocumentForWebSection'
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
    transaction.commit()
    self.tic()
    self.assertEqual(None, websection.getDefaultDocumentValue())
    # publish it
    web_page_en.publish()
    transaction.commit()
    self.tic()
    self.assertEqual(web_page_en, websection.getDefaultDocumentValue())
    # and make sure that the base meta tag which is generated
    # uses the web section rather than the portal
    html_page = websection()
    from Products.ERP5.Document.Document import Document
    base_list = re.findall(Document.base_parser, str(html_page))
    base_url = base_list[0]
    self.assertEqual(base_url, "%s/%s/" % (websection.absolute_url(), web_page_en.getReference()))

  def test_06b_DefaultDocumentForWebSite(self, quiet=quiet, run=run_all_test):
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
      message = '\ntest_06b_DefaultDocumentForWebSite'
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
    transaction.commit()
    self.tic()
    self.assertEqual(None, website.getDefaultDocumentValue())
    # publish it
    web_page_en.publish()
    transaction.commit()
    self.tic()
    self.assertEqual(web_page_en, website.getDefaultDocumentValue())
    # and make sure that the base meta tag which is generated
    # uses the web site rather than the portal
    html_page = website()
    from Products.ERP5.Document.Document import Document
    base_list = re.findall(Document.base_parser, str(html_page))
    base_url = base_list[0]
    self.assertEqual(base_url, "%s/%s/" % (website.absolute_url(), web_page_en.getReference()))

  def test_07_WebSection_getDocumentValueList(self, quiet=quiet, run=run_all_test):
    """ Check getting getDocumentValueList from Web Section.
    """
    if not run: return
    if not quiet:
      message = '\ntest_07_WebSection_getDocumentValueList'
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
        message = '\ntest_07_WebSection_getDocumentValueList (Sequence %s)' \
                                                                % (sequence_count)
        ZopeTestCase._print(message)

      web_page_list = []
      for key in sequence:
        web_page = self.portal.web_page_module.newContent(
                                  title=key,
                                  portal_type = 'Web Page',
                                  publication_section_list=publication_section_category_id_list[:1])

        web_page.edit(**property_dict[key])
        transaction.commit()
        self.tic()
        web_page_list.append(web_page)

      transaction.commit()
      self.tic()
      # in draft state, no documents should belong to this Web Section
      self.assertEqual(0, len(websection.getDocumentValueList()))

      # when published, all web pages should belong to it
      for web_page in web_page_list:
        web_page.publish()
      transaction.commit()
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

  def test_08_AcquisitionWrappers(self, quiet=quiet, run=run_all_test):
    """Test acquisition wrappers of documents.
    Check if documents obtained by getDefaultDocumentValue, getDocumentValue
    and getDocumentValueList are wrapped appropriately.
    """
    if not run: return
    if not quiet:
      message = '\ntest_08_AcquisitionWrappers'
      ZopeTestCase._print(message)

    portal = self.getPortal()

    # Make its own publication section category.
    publication_section = portal.portal_categories['publication_section']
    if publication_section._getOb('my_test_category', None) is None:
      publication_section.newContent(portal_type='Category',
                                     id='my_test_category',
                                     title='Test')
      transaction.commit()
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
    transaction.commit()
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

  def test_09_WebSiteSkinSelection(self, quiet=quiet, run=run_all_test):
    """Test skin selection through a Web Site.
    Check if a Web Site can change a skin selection based on a property.
    """
    if not run: return
    if not quiet:
      message = '\ntest_09_WebSiteSkinSelection'
      ZopeTestCase._print(message)

    portal = self.getPortal()
    ps = portal.portal_skins
    website = self.setupWebSite()

    # First, make sure that we use the default skin selection.
    portal.changeSkin(ps.getDefaultSkin())
    transaction.commit()
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

    transaction.commit()
    self.tic()

    path = website.absolute_url_path() + '/WebSite_test_13_WebSiteSkinSelection'
    request = portal.REQUEST

    # With the default skin.
    request['PARENTS'] = [self.app]
    self.assertEquals(request.traverse(path)(), 'foo')

    # With the test skin.
    website.setSkinSelectionName('Test ERP5 Web')
    transaction.commit()
    self.tic()

    request['PARENTS'] = [self.app]
    self.assertEquals(request.traverse(path)(), 'bar')

  def test_10_getDocumentValueList(self, quiet=quiet, run=run_all_test):
    """Make sure that getDocumentValueList works."""
    if not run: return
    if not quiet:
      message = '\ntest_10_getDocumentValueList'
      ZopeTestCase._print(message)

    self.setupWebSite()
    website = self.web_site_module[self.website_id]
    website.getDocumentValueList(
      portal_type='Document',
      sort_on=[('translated_portal_type', 'ascending')])

  def test_11_getWebSectionValueList(self, quiet=quiet, run=run_all_test):
    """ Check getWebSectionValueList from Web Site.
    Only visible web section should be returned.
    """
    if not run: return
    if not quiet:
      message = 'test_11_getWebSectionValueList'
      ZopeTestCase._print(message)

    portal = self.getPortal()
    web_site_portal_type = 'Web Site'
    web_section_portal_type = 'Web Section'
    web_page_portal_type = 'Web Page'

    # Create web site and web section
    web_site_module = portal.getDefaultModule(web_site_portal_type)
    web_site = web_site_module.newContent(portal_type=web_site_portal_type)
    web_section = web_site.newContent(portal_type=web_section_portal_type)
    sub_web_section = web_section.newContent(portal_type=web_section_portal_type)

    # Create a document
    web_page_module = portal.getDefaultModule(web_page_portal_type)
    web_page = web_page_module.newContent(portal_type=web_page_portal_type)

    # Commit transaction
    def _commit():
      portal.portal_caches.clearAllCache()
      transaction.commit()
      self.tic()

    # By default, as now Web Section is visible, nothing should be returned
    _commit()
    self.assertSameSet([], web_site.getWebSectionValueList(web_page))

    # Explicitely set both web section invisible
    web_section.setVisible(0)
    sub_web_section.setVisible(0)
    _commit()
    self.assertSameSet([], web_site.getWebSectionValueList(web_page))

    # Set parent web section visible
    web_section.setVisible(1)
    sub_web_section.setVisible(0)
    _commit()
    self.assertSameSet([web_section],
                       web_site.getWebSectionValueList(web_page))

    # Set both web section visible
    # Only leaf web section is returned
    web_section.setVisible(1)
    sub_web_section.setVisible(1)
    _commit()
    self.assertSameSet([sub_web_section],
                       web_site.getWebSectionValueList(web_page))

    # Set leaf web section visible, which should be returned even if parent is
    # not visible
    web_section.setVisible(0)
    sub_web_section.setVisible(1)
    _commit()
    self.assertSameSet([sub_web_section],
                       web_site.getWebSectionValueList(web_page))

  def test_12_getWebSiteValue(self, quiet=quiet, run=run_all_test):
    """
      Test that getWebSiteValue() and getWebSectionValue() always
      include selected Language.
    """
    if not run: return
    if not quiet:
      message = '\ntest_12_getWebSiteValue'
      ZopeTestCase._print(message)

    website_id = self.setupWebSite().getId()
    website = self.portal.restrictedTraverse(
      'web_site_module/%s' % website_id)
    website_relative_url = website.absolute_url(relative=1)
    website_fr = self.portal.restrictedTraverse(
      'web_site_module/%s/fr' % website_id)
    website_relative_url_fr = '%s/fr' % website_relative_url

    websection_id = self.setupWebSection().getId()
    websection = self.portal.restrictedTraverse(
      'web_site_module/%s/%s' % (website_id, websection_id))
    websection_relative_url = websection.absolute_url(relative=1)
    websection_fr = self.portal.restrictedTraverse(
      'web_site_module/%s/fr/%s' % (website_id, websection_id))
    websection_relative_url_fr = '%s/%s' % (website_relative_url_fr,
                                            websection.getId())

    page_ref = 'foo'
    page = self.web_page_module.newContent(portal_type='Web Page',
                                           reference='foo',
                                           text_content='<b>OK</b>')
    page.publish()
    transaction.commit()
    self.tic()

    webpage = self.portal.restrictedTraverse(
      'web_site_module/%s/%s' % (website_id, page_ref))
    webpage_fr = self.portal.restrictedTraverse(
      'web_site_module/%s/fr/%s' % (website_id, page_ref))

    webpage_module = self.portal.restrictedTraverse(
      'web_site_module/%s/web_page_module' % website_id)
    webpage_module_fr = self.portal.restrictedTraverse(
      'web_site_module/%s/fr/web_page_module' % website_id)

    self.assertEquals(website_relative_url,
                      website.getWebSiteValue().absolute_url(relative=1))
    self.assertEquals(website_relative_url_fr,
                      website_fr.getWebSiteValue().absolute_url(relative=1))
    self.assertEquals(website_relative_url,
                      webpage.getWebSiteValue().absolute_url(relative=1))
    self.assertEquals(website_relative_url_fr,
                      webpage_fr.getWebSiteValue().absolute_url(relative=1))
    self.assertEquals(website_relative_url,
                      webpage_module.getWebSiteValue().absolute_url(relative=1))
    self.assertEquals(website_relative_url_fr,
                      webpage_module_fr.getWebSiteValue().absolute_url(relative=1))

    webpage = self.portal.restrictedTraverse(
      'web_site_module/%s/%s/%s' % (website_id, websection_id, page_ref))
    webpage_fr = self.portal.restrictedTraverse(
      'web_site_module/%s/fr/%s/%s' % (website_id, websection_id, page_ref))

    webpage_module = self.portal.restrictedTraverse(
      'web_site_module/%s/%s/web_page_module' % (website_id, websection_id))
    webpage_module_fr = self.portal.restrictedTraverse(
      'web_site_module/%s/fr/%s/web_page_module' % (website_id, websection_id))

    self.assertEquals(websection_relative_url,
                      websection.getWebSectionValue().absolute_url(relative=1))
    self.assertEquals(websection_relative_url_fr,
                      websection_fr.getWebSectionValue().absolute_url(relative=1))
    self.assertEquals(websection_relative_url,
                      webpage.getWebSectionValue().absolute_url(relative=1))
    self.assertEquals(websection_relative_url_fr,
                      webpage_fr.getWebSectionValue().absolute_url(relative=1))
    self.assertEquals(websection_relative_url,
                      webpage_module.getWebSectionValue().absolute_url(relative=1))
    self.assertEquals(websection_relative_url_fr,
                      webpage_module_fr.getWebSectionValue().absolute_url(relative=1))

class TestERP5WebWithSimpleSecurity(ERP5TypeTestCase):
  """
  Test for erp5_web with simple security.
  """
  run_all_test = 1
  quiet = 0

  def getBusinessTemplateList(self):
    return ('erp5_base',
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
    self.createUser('webmaster', ['Assignor'])
    transaction.commit()
    self.tic()

  def clearModule(self, module):
    module.manage_delObjects(list(module.objectIds()))
    transaction.commit()
    self.tic()

  def beforeTearDown(self):
    self.clearModule(self.portal.web_site_module)
    self.clearModule(self.portal.web_page_module)

  def test_01_AccessWebPageByReference(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = '\ntest_01_AccessWebPageByReference'
      ZopeTestCase._print(message)

    self.changeUser('admin')
    site = self.portal.web_site_module.newContent(portal_type='Web Site',
                                                  id='site')
    section = site.newContent(portal_type='Web Section', id='section')

    transaction.commit()
    self.tic()

    section.setCriterionProperty('portal_type')
    section.setCriterion('portal_type', max='', identity=['Web Page'], min='')

    transaction.commit()
    self.tic()

    self.changeUser('erp5user')
    page_en = self.portal.web_page_module.newContent(portal_type='Web Page')
    page_en.edit(reference='my-first-web-page',
                 language='en',
                 version='1',
                 text_format='text/plain',
                 text_content='Hello, World!')

    transaction.commit()
    self.tic()

    page_en.publish()

    transaction.commit()
    self.tic()

    page_ja = self.portal.web_page_module.newContent(portal_type='Web Page')
    page_ja.edit(reference='my-first-web-page',
                 language='ja',
                 version='1',
                 text_format='text/plain',
                 text_content='こんにちは、世界！')

    transaction.commit()
    self.tic()

    page_ja.publish()

    transaction.commit()
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
    if not run: return
    if not quiet:
      message = '\ntest_02_LocalRolesFromRoleDefinition'
      ZopeTestCase._print(message)
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
    transaction.commit()
    self.tic()
    # check if Role Definition have create local roles
    self.assertSameSet(('Assignee',),
                          site.get_local_roles_for_userid(person_reference))
    self.assertSameSet(('Associate',),
                          section.get_local_roles_for_userid(person_reference))
    self.assertRaises(Unauthorized, site_role_definition.edit,
                      role_name='Manager')

    # delete Role Definition and check again (local roles must be gone too)
    site.manage_delObjects(site_role_definition.getId())
    section.manage_delObjects(section_role_definition.getId())
    transaction.commit()
    self.tic()
    self.assertSameSet((),
                       site.get_local_roles_for_userid(person_reference))
    self.assertSameSet((),
                       section.get_local_roles_for_userid(person_reference))

  def test_03_WebSection_getDocumentValueListSecurity(self, quiet=quiet, run=run_all_test):
    """ Test WebSection_getDocumentValueList behaviour and security"""
    if not run: return
    if not quiet:
      message = '\ntest_03_WebSection_getDocumentValueListSecurity'
      ZopeTestCase._print(message)
    self.changeUser('admin')
    web_site_module = self.portal.web_site_module
    site = web_site_module.newContent(portal_type='Web Site',
                                      id='site')

    section = site.newContent(portal_type='Web Section',
                              id='section')

    transaction.commit()
    self.tic()

    section.setCriterionProperty('portal_type')
    section.setCriterion('portal_type', max='',
                         identity=['Web Page'], min='')

    transaction.commit()
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

    transaction.commit()
    self.changeUser('erp5user')
    self.tic()
    self.portal.Localizer.changeLanguage('en')

    self.assertEquals(0, len(section.WebSection_getDocumentValueList()))

    self.changeUser('erp5user')
    page_en_0.publish()
    transaction.commit()
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
    transaction.commit()
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
    transaction.commit()
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
    transaction.commit()
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

  def test_04_ExpireUserAction(self, quiet=quiet, run=run_all_test):
    """ Test the expire user action"""
    if not run: return
    if not quiet:
      message = '\ntest_04_ExpireUserAction'
      ZopeTestCase._print(message)

    self.changeUser('admin')
    web_site_module = self.portal.web_site_module
    site = web_site_module.newContent(portal_type='Web Site', id='site')

    # create websections in a site and in anothers web sections
    section_1 = site.newContent(portal_type='Web Section', id='section_1')
    section_2 = site.newContent(portal_type='Web Section', id='section_2')
    section_3 = site.newContent(portal_type='Web Section', id='section_3')
    section_4 = site.newContent(portal_type='Web Section', id='section_4')
    section_5 = section_3.newContent(portal_type='Web Section', id='section_5')
    section_6 = section_4.newContent(portal_type='Web Section', id='section_6')
    transaction.commit()
    self.tic()

    # test if a manager can expire them
    try:
      section_1.expire()
      section_5.expire()
    except Unauthorized:
      self.fail("Admin should be able to expire a Web Section.")

    # test if a user (ASSIGNOR) can expire them
    self.changeUser('webmaster')
    try:
      section_2.expire()
      section_6.expire()
    except Unauthorized:
      self.fail("An user should be able to expire a Web Section.")

  def test_05_createWebSite(self, quiet=quiet, run=run_all_test):
    """ Test to create or clone web sites with many users """
    if not run: return
    if not quiet:
      message = '\ntest_05_createWebSite'
      ZopeTestCase._print(message)

    self.changeUser('admin')
    web_site_module = self.portal.web_site_module

    # test for admin
    try:
      site_1 = web_site_module.newContent(portal_type='Web Site', id='site_1')
    except Unauthorized:
      self.fail("Admin should be able to create a Web Site.")

    # test as a web user (assignor)
    self.changeUser('webmaster')
    try:
      site_2 = web_site_module.newContent(portal_type='Web Site', id='site_2')
    except Unauthorized:
      self.fail("A webmaster should be able to create a Web Site.")

    site_2_copy = web_site_module.manage_copyObjects(ids=(site_2.getId(),))
    site_2_clone = web_site_module[web_site_module.manage_pasteObjects(
      site_2_copy)[0]['new_id']]
    self.assertEquals(site_2_clone.getPortalType(), 'Web Site')

  def test_06_createWebSection(self, quiet=quiet, run=run_all_test):
    """ Test to create or clone web sections with many users """
    if not run: return
    if not quiet:
      message = '\ntest_06_createWebSection'
      ZopeTestCase._print(message)

    self.changeUser('admin')
    web_site_module = self.portal.web_site_module
    site = web_site_module.newContent(portal_type='Web Site', id='site')

    # test for admin
    try:
      section_1 = site.newContent(portal_type='Web Section', id='section_1')
      section_2 = section_1.newContent(portal_type='Web Section', id='section_2')
    except Unauthorized:
      self.fail("Admin should be able to create a Web Section.")

    # test as a webmaster (assignor)
    self.changeUser('webmaster')
    try:
      section_2 = site.newContent(portal_type='Web Section', id='section_2')
      section_3 = section_2.newContent(portal_type='Web Section', id='section_3')
    except Unauthorized:
      self.fail("A webmaster should be able to create a Web Section.")
    section_2_copy = site.manage_copyObjects(ids=(section_2.getId(),))
    section_2_clone = site[site.manage_pasteObjects(
      section_2_copy)[0]['new_id']]
    self.assertEquals(section_2_clone.getPortalType(), 'Web Section')
    section_3_copy = section_2.manage_copyObjects(ids=(section_3.getId(),))
    section_3_clone = section_2[section_2.manage_pasteObjects(
      section_3_copy)[0]['new_id']]
    self.assertEquals(section_3_clone.getPortalType(), 'Web Section')

  def test_07_createCategory(self, quiet=quiet, run=run_all_test):
    """ Test to create or clone categories with many users """
    if not run: return
    if not quiet:
      message = '\ntest_07_createCategory'
      ZopeTestCase._print(message)

    self.changeUser('admin')
    portal_categories = self.portal.portal_categories
    publication_section = portal_categories.publication_section

    # test for admin
    try:
      base_category_1 = portal_categories.newContent(portal_type='Base Category', id='base_category_1')
    except Unauthorized:
      self.fail("Admin should be able to create a Base Category.")
    try:
      category_1 = publication_section.newContent(portal_type='Category', id='category_1')
      category_2 = category_1.newContent(portal_type='Category', id='category_3')
    except Unauthorized:
      self.fail("Admin should be able to create a Category.")
    category_1_copy = publication_section.manage_copyObjects(ids=(category_1.getId(),))
    category_1_clone = publication_section[publication_section.manage_pasteObjects(
      category_1_copy)[0]['new_id']]
    self.assertEquals(category_1_clone.getPortalType(), 'Category')
    category_2_copy = category_1.manage_copyObjects(ids=(category_2.getId(),))
    category_2_clone = category_1[category_1.manage_pasteObjects(
      category_2_copy)[0]['new_id']]
    self.assertEquals(category_2_clone.getPortalType(), 'Category')

    # test as a web user (assignor)
    self.changeUser('webmaster')
    try:
      base_category_2 = portal_categories.newContent(portal_type='Base Category', id='base_category_2')
      self.fail("A webmaster should not be able to create a Base Category.")
    except Unauthorized:
      pass
    try:
      category_3 = publication_section.newContent(portal_type='Category', id='category_3')
      category_4 = category_3.newContent(portal_type='Category', id='category_4')
    except Unauthorized:
      self.fail("A webmaster should be able to create a Category.")
    # try to clone a sub category of the same owner whose parent is a
    # base category.
    category_3_copy = publication_section.manage_copyObjects(ids=(category_3.getId(),))
    category_3_clone = publication_section[publication_section.manage_pasteObjects(
      category_3_copy)[0]['new_id']]
    self.assertEquals(category_3_clone.getPortalType(), 'Category')
    # try to clone a sub category of the different owner
    category_2_copy = category_1.manage_copyObjects(ids=(category_2.getId(),))
    category_2_clone = category_1[category_1.manage_pasteObjects(
      category_2_copy)[0]['new_id']]
    self.assertEquals(category_2_clone.getPortalType(), 'Category')
    # try to clone a sub category of the same owner
    category_4_copy = category_3.manage_copyObjects(ids=(category_4.getId(),))
    category_4_clone = category_3[category_3.manage_pasteObjects(
      category_4_copy)[0]['new_id']]
    self.assertEquals(category_4_clone.getPortalType(), 'Category')

  def test_08_createAndrenameCategory(self, quiet=quiet, run=run_all_test):
    """ Test to create or rename categories with many users """
    if not run: return
    if not quiet:
      message = '\ntest_08_createAndrenameCategory'
      ZopeTestCase._print(message)

    self.changeUser('admin')
    portal_categories = self.portal.portal_categories
    publication_section = portal_categories.publication_section

    # test for admin
    try:
      new_base_category_1 = portal_categories.newContent(portal_type='Base Category', id='new_base_category_1')
    except Unauthorized:
      self.fail("Admin should be able to create a Base Category.")
    try:
      new_category_1 = publication_section.newContent(portal_type='Category', id='new_category_1')
      new_category_2 = new_category_1.newContent(portal_type='Category',
      id='new_category_2')
    except Unauthorized:
      self.fail("Admin should be able to create a Category.")
    transaction.commit()
    self.tic()
    try:
      new_cat_1_renamed = new_category_1.edit(id='new_cat_1_renamed')
      new_cat_2_renamed = new_category_2.edit(id='new_cat_2_renamed')
    except Unauthorized:
      self.fail("Admin should be able to rename a Category.")
    # test as a web user (assignor)
    self.changeUser('webmaster')
    try:
      base_category_2 = portal_categories.newContent(portal_type='Base Category', id='base_category_2')
      self.fail("A webmaster should not be able to create a Base Category.")
    except Unauthorized:
      pass
    try:
      new_category_3 = publication_section.newContent(
      portal_type='Category',id='new_category_3')
      new_category_4 = new_category_3.newContent(portal_type='Category',
          id='new_category_4')
    except Unauthorized:
      self.fail("A webmaster should be able to create a Category.")
    transaction.commit()
    self.tic()
    try:
      new_cat_3_renamed = new_category_3.edit(id='new_cat_3_renamed')
      new_cat_4_renamed = new_category_4.edit(id='new_cat_4_renamed')
    except Unauthorized:
      self.fail("A webmaster should be able to rename a Category.")

class TestERP5WebCategoryPublicationWorkflow(ERP5TypeTestCase):
  """Tests possible transitions for category_publication_workflow"""
  def getBusinessTemplateList(self):
    return ('erp5_base',
            'erp5_web',
            )

  def afterSetUp(self):
    base_category = self.getPortal().portal_categories\
        .newContent(portal_type='Base Category')
    self.doActionFor = self.getPortal().portal_workflow.doActionFor
    self.category = base_category.newContent(portal_type='Category')
    self.assertEqual('embedded', self.category.getValidationState())

  def test_category_embedded_expired(self):
    self.doActionFor(self.category, 'expire_action')
    self.assertEqual('expired', self.category.getValidationState())

  def test_category_embedded_protected_expired(self):
    self.doActionFor(self.category, 'protect_action')
    self.assertEqual('protected', self.category.getValidationState())
    self.doActionFor(self.category, 'expire_action')
    self.assertEqual('expired_protected', self.category.getValidationState())

  def test_category_embedded_published_expired(self):
    self.doActionFor(self.category, 'publish_action')
    self.assertEqual('published', self.category.getValidationState())
    self.doActionFor(self.category, 'expire_action')
    self.assertEqual('expired_published', self.category.getValidationState())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Web))
  suite.addTest(unittest.makeSuite(TestERP5WebWithSimpleSecurity))
  suite.addTest(unittest.makeSuite(TestERP5WebCategoryPublicationWorkflow))
  return suite
