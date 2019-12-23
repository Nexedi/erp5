# -*- coding: utf-8 -*-
##############################################################################
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
import time
from unittest import expectedFailure, skip
from StringIO import StringIO
from urllib import urlencode
from AccessControl import Unauthorized
from Testing import ZopeTestCase
from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import DummyLocalizer
from Products.ERP5Type.tests.utils import createZODBPythonScript

LANGUAGE_LIST = ('en', 'fr', 'de', 'bg', )
HTTP_OK = 200
MOVED_TEMPORARILY = 302


class DummyTraversalHook(object):
  def __call__(self, container, request):
    return


class WebTraversalHookTestMixin(object):
  """Mixin class to test the WebSiteTraversalHook on both websection and website.
  """
  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_web', )

  def test_TraversalHook_on_newContent(self):
    """a WebSiteTraversalHook is added on websections and websites automatically.
    """
    self.assertEquals(1, len(self.web_section.__before_traverse__))
    self.assertIsInstance(
      self.web_section.__before_traverse__.values()[0],
      self.traversal_hook_class)

  def test_TraversalHook_on_clone(self):
    """a WebSiteTraversalHook is correctly updated after cloning a websection/website.
    """
    cloned_web_section = self.web_section.Base_createCloneDocument(batch_mode=True)
    self.assertEquals(1, len(cloned_web_section.__before_traverse__))

  def test_TraversalHook_on_change_id(self):
    """a TraversalHook is correctly updated after changing websection id.
    """
    self.tic()
    self.web_section.setId("new_id")
    self.assertEquals(1, len(self.web_section.__before_traverse__))

  def test_TraversalHook_cleanup_on_edit(self):
    """Old traversal hooks from cloned objects are automatically cleaned up
    when section is edited.
    """
    # artificially put this websection in a similar state that websection were before
    # we fix the bug keeping traversal hooks on clone.
    from ZPublisher import BeforeTraverse
    handle = '%s/different_id_than_%s' % (self.web_section.meta_type, self.web_section.getId())
    BeforeTraverse.registerBeforeTraverse(self.web_section, self.traversal_hook_class(), handle)

    BeforeTraverse.registerBeforeTraverse(
      self.web_section,
      DummyTraversalHook(),
      'unrelated_traversal_hook_that_should_be_kept')
    self.assertEquals(3, len(self.web_section.__before_traverse__))

    self.tic()
    self.web_section.edit(title=self.id())
    # We have cleaned up the useless before traversal hook, but keep the unrelated one
    self.assertEquals(2, len(self.web_section.__before_traverse__))
    self.assertEquals(1, len([hook for hook in
      self.web_section.__before_traverse__.values() if isinstance(hook, self.traversal_hook_class)]))
    self.assertEquals(1, len([hook for hook in
      self.web_section.__before_traverse__.values() if isinstance(hook, DummyTraversalHook)]))


class TestWebSiteTraversalHook(WebTraversalHookTestMixin, ERP5TypeTestCase):
  def afterSetUp(self):
    super(TestWebSiteTraversalHook, self).afterSetUp()
    self.web_section = self.portal.web_site_module.newContent(
      portal_type='Web Site',
    )
    from Products.ERP5Type.Document.WebSite import WebSiteTraversalHook
    self.traversal_hook_class = WebSiteTraversalHook


class TestWebSectionTraversalHook(WebTraversalHookTestMixin, ERP5TypeTestCase):
  def afterSetUp(self):
    super(TestWebSectionTraversalHook, self).afterSetUp()
    web_site = self.portal.web_site_module.newContent(
      portal_type='Web Site',
    )
    self.web_section = web_site.newContent(portal_type='Web Section')

    from Products.ERP5Type.Document.WebSection import WebSectionTraversalHook
    self.traversal_hook_class = WebSectionTraversalHook


class TestERP5Web(ERP5TypeTestCase):
  """Test for erp5_web business template.
  """
  manager_username = 'zope'
  manager_password = 'zope'
  website_id = 'test'
  credential = '%s:%s' % (manager_username, manager_password)

  def getTitle(self):
    return "ERP5Web"

  def getBusinessTemplateList(self):
    """
    Return the list of required business templates.
    """
    return ('erp5_core_proxy_field_legacy',
            'erp5_base',
            'erp5_jquery',
            'erp5_web',
            )

  def afterSetUp(self):
    portal = self.getPortal()

    uf = portal.acl_users
    uf._doAddUser(self.manager_username,
                  self.manager_password,
                  ['Manager'], [])
    self.loginByUserName(self.manager_username)

    self.web_page_module = self.portal.getDefaultModule('Web Page Module')
    self.web_site_module = self.portal.getDefaultModule('Web Site Module')
    portal.Localizer.manage_changeDefaultLang(language='en')
    self.portal_id = self.portal.getId()

  def clearModule(self, module):
    module.manage_delObjects(list(module.objectIds()))
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

    # add supported languages for Localizer
    localizer = portal.Localizer
    for language in LANGUAGE_LIST:
      localizer.manage_addLanguage(language=language)

    # create website
    if hasattr(self.web_site_module, self.website_id):
      self.web_site_module.manage_delObjects(self.website_id)
    website = self.web_site_module.newContent(portal_type='Web Site',
                                              id=self.website_id,
                                              **kw)
    website.publish()
    self.tic()
    return website

  def setupWebSection(self, **kw):
    """
      Setup Web Section
    """
    website = self.web_site_module[self.website_id]
    websection = website.newContent(portal_type='Web Section', **kw)
    self.websection = websection
    kw = dict(criterion_property_list='portal_type',
              membership_criterion_base_category_list='',
              membership_criterion_category_list='')
    websection.edit(**kw)
    websection.setCriterion(property='portal_type',
                            identity=['Web Page'],
                            max='',
                            min='')

    self.tic()
    return websection

  def setupWebSitePages(self, prefix, suffix=None, version='0.1',
                        language_list=LANGUAGE_LIST, **kw):
    """
      Setup some Web Pages.
    """
    webpage_list = []
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
      self.tic()
      self.assertEqual(language, webpage.getLanguage())
      self.assertEqual(reference, webpage.getReference())
      self.assertEqual(version, webpage.getVersion())
      self.assertEqual('published', webpage.getValidationState())
      webpage_list.append(webpage)

    return webpage_list

  def test_01_WebSiteRecatalog(self):
    """
      Test that a recataloging works for Web Site documents
    """
    self.setupWebSite()
    web_site = self.web_site_module[self.website_id]

    self.assertTrue(web_site is not None)
    # Recatalog the Web Site document
    portal_catalog = self.getCatalogTool()
    try:
      portal_catalog.catalog_object(web_site)
    except:
      self.fail('Cataloging of the Web Site failed.')



  def test_02_EditSimpleWebPage(self):
    """
      Simple Case of creating a web page.
    """
    page = self.web_page_module.newContent(portal_type='Web Page')
    page.edit(text_content='<b>OK</b>')
    self.assertEqual('text/html', page.getContentType())
    self.assertEqual('<b>OK</b>', page.getTextContent())

  def test_WebPageAsTextUTF8(self):
    """Check if Web Page's asText() returns utf-8 string correctly
    """
    page = self.web_page_module.newContent(portal_type='Web Page')
    page.edit(text_content='<p>Hé Hé Hé!</p>', content_type='text/html')
    self.tic()
    self.assertEqual('Hé Hé Hé!', page.asText().strip())

  def test_WebPageAsTextHTMLEntities(self):
    """Check if Web Page's asText() converts html entities properly
    """
    page = self.web_page_module.newContent(portal_type='Web Page')
    page.edit(text_content='<p>H&eacute;!</p>', content_type='text/html')
    self.tic()
    self.assertEqual('Hé!', page.asText().strip())

  def test_WebPageAsTextWrap(self):
    """Check if Web Page's asText() is wrapped by certain column width.
    """
    page = self.web_page_module.newContent(portal_type='Web Page')

    page.edit(text_content='<p>Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé!</p>')
    self.tic()
    self.assertEqual("""Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé Hé
Hé Hé Hé!""", page.asText().strip())

  @skip('WebSite_createWebSiteAccount is disabled by default.')
  def test_03_CreateWebSiteUser(self):
    """
      Create Web site User.
    """
    self.setupWebSite()
    portal = self.getPortal()
    request = self.app.REQUEST
    kw = dict(reference='web',
              first_name='TestFN',
              last_name='TestLN',
              default_email_text='test@test.com',
              password='abc',
              password_confirm='abc',)
    for key, item in kw.items():
      request.set('field_your_%s' % key, item)
    website = self.web_site_module[self.website_id]
    website.WebSite_createWebSiteAccount('WebSite_viewRegistrationDialog')

    self.tic()

    # find person object by reference
    person = website.Base_getUserValueByUserId(kw['reference'])
    self.assertEqual(person.getReference(), kw['reference'])
    self.assertEqual(person.getFirstName(), kw['first_name'])
    self.assertEqual(person.getLastName(), kw['last_name'])
    self.assertEqual(person.getDefaultEmailText(), kw['default_email_text'])
    self.assertEqual(person.getValidationState(), 'validated')

    # check if user account is 'loggable'
    uf = portal.acl_users
    user = uf.getUserById(kw['reference'])
    self.assertEqual(user.getIdOrUserName(), kw['reference'])
    self.assertEqual(1, user.has_role(('Member', 'Authenticated',)))
    self.loginByUserName(kw['reference'])
    self.assertEqual(kw['reference'],
                     portal.portal_membership.getAuthenticatedMember().getIdOrUserName())

    # test redirection to person oobject
    path = website.absolute_url_path() + '/WebSite_redirectToUserView'
    response = self.publish(path, '%s:%s' % (kw['reference'], kw['password']))
    self.assertTrue(person.getRelativeUrl() in response.getHeader("Location"))

    # test redirecting to new Person preference
    path = website.absolute_url_path() + '/WebSite_redirectToUserPreference'
    response = self.publish(path, '%s:%s' % (kw['reference'], kw['password']))
    self.assertTrue('portal_preferences' in response.getHeader("Location"))
    # one preference should be created for user
    self.assertEqual(1,
        self.portal.portal_catalog.countResults(**{'portal_type': 'Preference',
                                              'owner': kw['reference']})[0][0])

  def test_04_WebPageTranslation(self):
    """
      Simple Case of showing the proper Web Page based on
      current user selected language in browser.
    """
    portal = self.getPortal()
    website = self.setupWebSite()
    websection = self.setupWebSection()
    page_reference = 'default-webpage'
    webpage_list = self.setupWebSitePages(prefix=page_reference)

    # set default web page for section
    found_by_reference = portal.portal_catalog(reference=page_reference,
                                               portal_type='Web Page')
    found = found_by_reference[0].getObject()
    websection.edit(categories_list=['aggregate/%s' % found.getRelativeUrl()])
    self.assertEqual([found.getReference()],
                      websection.getAggregateReferenceList())
    # even though we create many pages we should get only one
    # this is the most recent one since all share the same reference
    self.assertEqual(1, len(websection.getDocumentValueList()))

    # use already created few pages in different languages with same reference
    # and check that we always get the right one based on selected
    # by us language
    for language in LANGUAGE_LIST:
      # set default language in Localizer only to check that we get
      # the corresponding web page for language.
      # XXX: Extend API so we can select language from REQUEST
      portal.Localizer.manage_changeDefaultLang(language=language)
      default_document = websection.getDefaultDocumentValue()
      self.assertEqual(language, default_document.getLanguage())

  def test_05_WebPageTextContentSubstitutions(self):
    """
      Simple Case of showing the proper text content with and without a
      substitution mapping method.
      In case of asText, the content should be replaced too
    """
    content = '<a href="${toto}">$titi</a>'
    asText_content = '$titi\n'
    substituted_content = '<a href="foo">bar</a>'
    substituted_asText_content = 'bar\n'
    mapping = dict(toto='foo', titi='bar')

    portal = self.getPortal()
    document = portal.web_page_module.newContent(portal_type='Web Page',
            text_content=content)

    # No substitution should occur.
    self.assertEqual(document.asStrippedHTML(), content)
    self.assertEqual(document.asText(), asText_content)

    klass = document.__class__
    klass.getTestSubstitutionMapping = lambda self, **kw: mapping
    document.setTextContentSubstitutionMappingMethodId('getTestSubstitutionMapping')

    # Substitutions should occur.
    self.assertEqual(document.asStrippedHTML(), substituted_content)
    self.assertEqual(document.asText(), substituted_asText_content)

    klass._getTestSubstitutionMapping = klass.getTestSubstitutionMapping
    document.setTextContentSubstitutionMappingMethodId('_getTestSubstitutionMapping')

    # Even with the same callable object, a restricted method
    # id should not be callable.
    self.assertRaises(Unauthorized, document.asStrippedHTML)

  def test_06_DefaultDocumentForWebSection(self):
    """
      Testing the default document for a Web Section.

      If a Web Section has a default document defined and if that default
      document is published, then getDefaultDocumentValue on that
      web section should return the latest version in the most
      appropriate language of that default document.

      Note: due to generic ERP5 Web implementation this test highly depends
      on WebSection_geDefaulttDocumentValueList
    """
    website = self.setupWebSite()
    websection = self.setupWebSection()
    publication_section_category_id_list = ['documentation', 'administration']

    # create pages belonging to this publication_section 'documentation'
    web_page_en = self.web_page_module.newContent(
             portal_type='Web Page',
             id='section_home',
             language='en',
             reference='NXD-DDP',
             publication_section_list=publication_section_category_id_list[:1])
    websection.setAggregateValue(web_page_en)
    self.tic()
    self.assertEqual(None, websection.getDefaultDocumentValue())
    # publish it
    web_page_en.publish()
    self.tic()
    self.assertEqual(web_page_en, websection.getDefaultDocumentValue())
    # and make sure that the base meta tag which is generated
    # uses the web section rather than the portal
    html_page = websection()
    from Products.ERP5.Document.Document import Document
    base_list = re.findall(Document.base_parser, str(html_page))
    base_url = base_list[0]
    self.assertEqual(base_url, "%s/%s/" % (websection.absolute_url(),
                                           web_page_en.getReference()))

  def test_06b_DefaultDocumentForWebSite(self):
    """
      Testing the default document for a Web Site.

      If a Web Section has a default document defined and if that default
      document is published, then getDefaultDocumentValue on that
      web section should return the latest version in the most
      appropriate language of that default document.

      Note: due to generic ERP5 Web implementation this test highly depends
      on WebSection_geDefaulttDocumentValueList
    """
    website = self.setupWebSite()
    publication_section_category_id_list = ['documentation', 'administration']

    # create pages belonging to this publication_section 'documentation'
    web_page_en = self.web_page_module.newContent(portal_type = 'Web Page',
                                                 id='site_home',
                                                 language = 'en',
                                                 reference='NXD-DDP-Site',
                                                 publication_section_list=publication_section_category_id_list[:1])
    website.setAggregateValue(web_page_en)
    self.tic()
    self.assertEqual(None, website.getDefaultDocumentValue())
    # publish it
    web_page_en.publish()
    self.tic()
    self.assertEqual(web_page_en, website.getDefaultDocumentValue())
    # and make sure that the base meta tag which is generated
    # uses the web site rather than the portal
    html_page = website()
    from Products.ERP5.Document.Document import Document
    base_list = re.findall(Document.base_parser, str(html_page))
    base_url = base_list[0]
    self.assertEqual(base_url, "%s/%s/" % (website.absolute_url(), web_page_en.getReference()))

  def test_07_getDocumentValueList(self):
    """ Check getting getDocumentValueList from Web Section.
    """
    portal = self.getPortal()
    website = self.setupWebSite()
    websection = self.setupWebSection()
    publication_section_category_id_list = ['documentation', 'administration']

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

    property_dict = {'01': dict(language='en', version="1", reference="A"),
                     '02': dict(language='en', version="2", reference="B"),
                     '03': dict(language='en', version="3", reference="C"),
                     '04': dict(language='pt', version="1", reference="A"),
                     '05': dict(language='pt', version="2", reference="C"),
                     '06': dict(language='pt', version="3", reference="B"),
                     '07': dict(language='ja', version="1", reference="C"),
                     '08': dict(language='ja', version="2", reference="A"),
                     '09': dict(language='ja', version="3", reference="B"),
                     '10': dict(language='en', version="2", reference="D"),
                     '11': dict(language='ja', version="3", reference="E"),
                     '12': dict(language='pt', version="3", reference="F"),
                     '13': dict(language='en', version="3", reference="D"),
                     '14': dict(language='ja', version="2", reference="E"),
                     '15': dict(language='pt', version="2", reference="F"),
                     '16': dict(language='', version="1", reference="A"),
                    }
    sequence_one = property_dict.keys()
    sequence_two = ['01', '13', '12', '09', '06', '15', '04', '11', '02',
                    '05', '03', '07', '10', '08', '14', '16']
    sequence_three = ['05', '12', '13', '14', '06', '09', '10', '07',
                      '03', '01', '02', '11', '04', '08', '15', '16']

    sequence_count = 0
    for sequence in [sequence_one, sequence_two, sequence_three]:
      sequence_count += 1
      message = '\ntest_07_getDocumentValueList (Sequence %s)' \
                                                              % (sequence_count)
      ZopeTestCase._print(message)

      web_page_list = []
      for key in sequence:
        web_page = self.web_page_module.newContent(
                                  title=key,
                                  portal_type = 'Web Page',
                                  publication_section_list=publication_section_category_id_list[:1])

        web_page.edit(**property_dict[key])
        self.tic()
        web_page_list.append(web_page)

      self.tic()
      # in draft state, no documents should belong to this Web Section
      self.assertEqual(0, len(websection.getDocumentValueList()))

      # when published, all web pages should belong to it
      for web_page in web_page_list:
        web_page.publish()
      self.tic()

      # Test for limit parameter
      self.assertEqual(2, len(websection.getDocumentValueList(limit=2)))

      # Testing for language parameter
      self.assertEqual(4, len(websection.getDocumentValueList()))
      self.assertEqual(['en', 'en', 'en', 'en'],
                       [w.getLanguage() for w in websection.getDocumentValueList()])

      # Check that receiving an empty string as language parameter (as done
      # when using listbox search) correctly returns user language documents.
      default_document_value_list = websection.getDocumentValueList(language='')
      self.assertEqual(4, len(default_document_value_list))
      self.assertEqual(['en', 'en', 'en', 'en'],
                       [w.getLanguage() for w in default_document_value_list])

      pt_document_value_list = websection.getDocumentValueList(language='pt')
      self.assertEqual(4, len(pt_document_value_list))
      self.assertEqual(['pt', 'pt', 'pt', 'pt'],
                           [w.getObject().getLanguage() for w in pt_document_value_list])

      ja_document_value_list = websection.getDocumentValueList(language='ja')
      self.assertEqual(4, len(ja_document_value_list))
      self.assertEqual(['ja', 'ja', 'ja', 'ja'],
                           [w.getLanguage() for w in ja_document_value_list])

      bg_document_value_list = websection.getDocumentValueList(language='bg')
      self.assertEqual(1, len(bg_document_value_list))
      self.assertEqual([''],
                       [w.getLanguage() for w in bg_document_value_list])

      # Testing for all_versions parameter
      en_document_value_list = websection.getDocumentValueList(all_versions=1)
      self.assertEqual(5, len(en_document_value_list))
      self.assertEqual(['en', 'en', 'en', 'en', 'en'],
                       [w.getLanguage() for w in en_document_value_list])

      pt_document_value_list = websection.getDocumentValueList(language='pt',
                                                               all_versions=1)
      self.assertEqual(5, len(pt_document_value_list))
      self.assertEqual(['pt', 'pt', 'pt', 'pt', 'pt'],
                       [w.getObject().getLanguage() for w in pt_document_value_list])

      ja_document_value_list = websection.getDocumentValueList(language='ja',
                                                               all_versions=1)
      self.assertEqual(5, len(ja_document_value_list))
      self.assertEqual(['ja', 'ja', 'ja', 'ja', 'ja'],
                           [w.getLanguage() for w in ja_document_value_list])

      # Tests for all_languages parameter (language parameter is simply ignored)
      en_document_value_list = websection.getDocumentValueList(all_languages=1)
      self.assertEqual(13, len(en_document_value_list))
      self.assertEqual(4, len([w.getLanguage() for w in en_document_value_list \
                              if w.getLanguage() == 'en']))
      self.assertEqual(4, len([w.getLanguage() for w in en_document_value_list \
                              if w.getLanguage() == 'pt']))
      self.assertEqual(4, len([w.getLanguage() for w in en_document_value_list \
                              if w.getLanguage() == 'ja']))

      pt_document_value_list = websection.getDocumentValueList(all_languages=1,
                                                                              language='pt')
      self.assertEqual(13, len(pt_document_value_list))
      self.assertEqual(4, len([w.getLanguage() for w in pt_document_value_list \
                              if w.getLanguage() == 'pt']))
      self.assertEqual(4, len([w.getLanguage() for w in pt_document_value_list \
                              if w.getLanguage() == 'en']))
      self.assertEqual(4, len([w.getLanguage() for w in pt_document_value_list \
                              if w.getLanguage() == 'ja']))

      # Tests for all_languages and all_versions
      en_document_value_list = websection.getDocumentValueList(all_languages=1,
                                                               all_versions=1)

      pt_document_value_list = websection.getDocumentValueList(all_languages=1,
                                                               all_versions=1,
                                                               language='pt')

      ja_document_value_list = websection.getDocumentValueList(all_languages=1,
                                                               all_versions=1,
                                                               language='ja')

      for document_value_list in [en_document_value_list, pt_document_value_list,
                                   ja_document_value_list]:

        self.assertEqual(16, len(document_value_list))
        self.assertEqual(5, len([w.getLanguage() for w in document_value_list \
                                if w.getLanguage() == 'en']))
        self.assertEqual(5, len([w.getLanguage() for w in en_document_value_list \
                                if w.getLanguage() == 'pt']))
        self.assertEqual(5, len([w.getLanguage() for w in en_document_value_list \
                                if w.getLanguage() == 'ja']))

      # Tests for strict_language=False
      fallback_document_value_list = websection.getDocumentValueList(strict_language=False, language='ja')
      self.assertEqual(
        [('en', 'D'), ('ja', 'A'), ('ja', 'B'), ('ja', 'C'), ('ja', 'E'), ('pt', 'F')],
        sorted([(x.getLanguage(), x.getReference()) for x in fallback_document_value_list])
      )

      # Tests for sort_on parameter
      self.assertEqual(['A', 'B', 'C', 'D'],
                       [w.getReference() for w in \
                         websection.getDocumentValueList(sort_on=[('reference', 'ASC')])])

      self.assertEqual(['01', '02', '03', '13'],
                       [w.getTitle() for w in \
                         websection.getDocumentValueList(sort_on=[('title', 'ASC')])])

      self.assertEqual(['D', 'C', 'B', 'A'],
                       [w.getReference() for w in \
                         websection.getDocumentValueList(sort_on=[('reference', 'DESC')])])

      self.assertEqual(['13', '03', '02', '01'],
                       [w.getTitle() for w in \
                         websection.getDocumentValueList(sort_on=[('reference', 'DESC')])])

      self.assertEqual(['A', 'A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C', 'D', 'E', 'F'],
                       [w.getReference() for w in \
                         websection.getDocumentValueList(all_languages=1,
                                            sort_on=[('reference', 'ASC')])])

      self.assertEqual(['01', '02', '03', '04', '05', '06', '07', '08', '09', '11', '12', '13', '16'],
                       [w.getTitle() for w in \
                         websection.getDocumentValueList(all_languages=1,
                                            sort_on=[('title', 'ASC')])])

      self.assertEqual(['F', 'E', 'D', 'C', 'C', 'C', 'B', 'B', 'B', 'A', 'A', 'A', 'A'],
                                              [w.getReference() for w in \
                         websection.getDocumentValueList(all_languages=1,
                                            sort_on=[('reference', 'DESC')])])

      self.assertEqual(['16', '13', '12', '11', '09', '08', '07', '06', '05', '04', '03', '02', '01'],
                       [w.getTitle() for w in \
                         websection.getDocumentValueList(all_languages=1,
                                            sort_on=[('title', 'DESC')])])

      self.web_page_module.manage_delObjects(list(self.web_page_module.objectIds()))

  def test_08_AcquisitionWrappers(self):
    """Test acquisition wrappers of documents.
    Check if documents obtained by getDefaultDocumentValue, getDocumentValue
    and getDocumentValueList are wrapped appropriately.
    """
    portal = self.getPortal()

    # Make its own publication section category.
    publication_section = portal.portal_categories['publication_section']
    if publication_section._getOb('my_test_category', None) is None:
      publication_section.newContent(portal_type='Category',
                                     id='my_test_category',
                                     title='Test')
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
      self.assertEqual(doc.aq_parent, websection)
      self.assertEqual(doc.aq_parent.aq_parent, website)

  def test_09_WebSiteSkinSelection(self):
    """Test skin selection through a Web Site.
    Check if a Web Site can change a skin selection based on a property.
    """
    portal = self.getPortal()
    ps = portal.portal_skins
    website = self.setupWebSite()

    # First, make sure that we use the default skin selection.
    portal.changeSkin(ps.getDefaultSkin())
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

    self.tic()

    path = website.absolute_url_path() + '/WebSite_test_13_WebSiteSkinSelection'
    request = portal.REQUEST

    # With the default skin.
    request['PARENTS'] = [self.app]
    self.assertEqual(request.traverse(path)(), 'foo')

    # With the test skin.
    website.setSkinSelectionName('Test ERP5 Web')
    self.tic()

    request['PARENTS'] = [self.app]
    self.assertEqual(request.traverse(path)(), 'bar')

  def test_10_getDocumentValueList(self):
    """Make sure that getDocumentValueList works."""
    self.setupWebSite()
    website = self.web_site_module[self.website_id]
    website.getDocumentValueList(
      portal_type='Document',
      sort_on=[('translated_portal_type', 'ascending')])

  def test_11_getWebSectionValueList(self):
    """ Check getWebSectionValueList from Web Site.
    Only visible web section should be returned.
    """
    portal = self.getPortal()
    web_site_portal_type = 'Web Site'
    web_section_portal_type = 'Web Section'
    web_page_portal_type = 'Web Page'

    # Create web site and web section
    web_site = self.web_site_module.newContent(portal_type=web_site_portal_type)
    web_section = web_site.newContent(portal_type=web_section_portal_type)
    sub_web_section = web_section.newContent(portal_type=web_section_portal_type)

    # Create a document
    web_page = self.web_page_module.newContent(portal_type=web_page_portal_type)

    # Commit transaction
    def _commit():
      portal.portal_caches.clearAllCache()
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

  def test_12_getWebSiteValue(self):
    """
      Test that getWebSiteValue() and getWebSectionValue() always
      include selected Language.
    """
    website_id = self.setupWebSite(default_available_language='en').getId()
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
    self.tic()

    webpage = self.portal.restrictedTraverse(
      'web_site_module/%s/%s' % (website_id, page_ref))
    webpage_fr = self.portal.restrictedTraverse(
      'web_site_module/%s/fr/%s' % (website_id, page_ref))

    webpage_module = self.portal.restrictedTraverse(
      'web_site_module/%s/web_page_module' % website_id)
    webpage_module_fr = self.portal.restrictedTraverse(
      'web_site_module/%s/fr/web_page_module' % website_id)

    self.assertEqual(website_relative_url,
                      website.getWebSiteValue().absolute_url(relative=1))
    self.assertEqual(website_relative_url_fr,
                      website_fr.getWebSiteValue().absolute_url(relative=1))
    self.assertEqual(website_relative_url,
                      webpage.getWebSiteValue().absolute_url(relative=1))
    self.assertEqual(website_relative_url_fr,
                      webpage_fr.getWebSiteValue().absolute_url(relative=1))
    self.assertEqual(website_relative_url,
                      webpage_module.getWebSiteValue().absolute_url(relative=1))
    self.assertEqual(website_relative_url_fr,
                      webpage_module_fr.getWebSiteValue().absolute_url(relative=1))

    webpage = self.portal.restrictedTraverse(
      'web_site_module/%s/%s/%s' % (website_id, websection_id, page_ref))
    webpage_fr = self.portal.restrictedTraverse(
      'web_site_module/%s/fr/%s/%s' % (website_id, websection_id, page_ref))

    webpage_module = self.portal.restrictedTraverse(
      'web_site_module/%s/%s/web_page_module' % (website_id, websection_id))
    webpage_module_fr = self.portal.restrictedTraverse(
      'web_site_module/%s/fr/%s/web_page_module' % (website_id, websection_id))

    self.assertEqual(websection_relative_url,
                      websection.getWebSectionValue().absolute_url(relative=1))
    self.assertEqual(websection_relative_url_fr,
                      websection_fr.getWebSectionValue().absolute_url(relative=1))
    self.assertEqual(websection_relative_url,
                      webpage.getWebSectionValue().absolute_url(relative=1))
    self.assertEqual(websection_relative_url_fr,
                      webpage_fr.getWebSectionValue().absolute_url(relative=1))
    self.assertEqual(websection_relative_url,
                      webpage_module.getWebSectionValue().absolute_url(relative=1))
    self.assertEqual(websection_relative_url_fr,
                      webpage_module_fr.getWebSectionValue().absolute_url(relative=1))

    # several languages in URL
    website_bg_fr = self.portal.restrictedTraverse(
      'web_site_module/%s/bg/fr' % website_id)
    self.assertEqual(website_bg_fr.getOriginalDocument(), website)
    websection_bg_fr = self.portal.restrictedTraverse(
      'web_site_module/%s/bg/fr/%s' % (website_id, websection_id))
    webpage_bg_fr = self.portal.restrictedTraverse(
      'web_site_module/%s/bg/fr/%s/%s' % (website_id, websection_id, page_ref))

    # change language without referer
    request = self.portal.REQUEST
    request['HTTP_REFERER'] = ''
    website_absolute_url = website.absolute_url()
    self.assertEqual(website_fr.Base_doLanguage('de'), '%s/de' % website_absolute_url)
    self.assertEqual(websection_fr.Base_doLanguage('de'), '%s/de' % website_absolute_url)
    self.assertEqual(webpage_fr.Base_doLanguage('de'), '%s/de' % website_absolute_url)
    self.assertEqual(website_fr.Base_doLanguage('en'), website_absolute_url)
    self.assertEqual(websection_fr.Base_doLanguage('en'), website_absolute_url)
    self.assertEqual(webpage_fr.Base_doLanguage('en'), website_absolute_url)
    self.assertEqual(website_bg_fr.Base_doLanguage('de'), '%s/de' % website_absolute_url)
    self.assertEqual(websection_bg_fr.Base_doLanguage('de'), '%s/de' % website_absolute_url)
    self.assertEqual(webpage_bg_fr.Base_doLanguage('de'), '%s/de' % website_absolute_url)
    self.assertEqual(website_bg_fr.Base_doLanguage('en'), website_absolute_url)
    self.assertEqual(websection_bg_fr.Base_doLanguage('en'), website_absolute_url)
    self.assertEqual(webpage_bg_fr.Base_doLanguage('en'), website_absolute_url)

    # change language with referer
    request['HTTP_REFERER'] = website_fr.absolute_url()
    self.assertEqual(website_fr.Base_doLanguage('de'), '%s/de' % website_absolute_url)
    request['HTTP_REFERER'] = websection_fr.absolute_url()
    self.assertEqual(websection_fr.Base_doLanguage('de'), websection_fr.absolute_url().replace('/fr/', '/de/'))
    request['HTTP_REFERER'] = webpage_fr.absolute_url()
    self.assertEqual(webpage_fr.Base_doLanguage('de'), webpage_fr.absolute_url().replace('/fr/', '/de/'))
    request['HTTP_REFERER'] = website_bg_fr.absolute_url()
    self.assertEqual(website_bg_fr.Base_doLanguage('de'), '%s/de' % website_absolute_url)
    request['HTTP_REFERER'] = websection_bg_fr.absolute_url()
    self.assertEqual(websection_bg_fr.Base_doLanguage('de'), websection_bg_fr.absolute_url().replace('/bg/fr/', '/de/'))
    request['HTTP_REFERER'] = webpage_bg_fr.absolute_url()
    self.assertEqual(webpage_bg_fr.Base_doLanguage('de'), webpage_bg_fr.absolute_url().replace('/bg/fr/', '/de/'))

    # /bg/en/fr/xxx should be redirected to /fr/xxx
    website_bg_en_fr = self.portal.restrictedTraverse(
      'web_site_module/%s/bg/en/fr' % website_id)
    websection_bg_en_fr = self.portal.restrictedTraverse(
      'web_site_module/%s/bg/en/fr/%s' % (website_id, websection_id))
    webpage_bg_en_fr = self.portal.restrictedTraverse(
      'web_site_module/%s/bg/en/fr/%s/%s' % (website_id, websection_id, page_ref))
    self.assertEqual(self.publish(website_bg_en_fr.absolute_url(relative=1)).getHeader('location'),
                     website_fr.absolute_url())
    self.assertEqual(self.publish(websection_bg_en_fr.absolute_url(relative=1)).getHeader('location'),
                     websection_fr.absolute_url())
    self.assertEqual(self.publish(webpage_bg_en_fr.absolute_url(relative=1)).getHeader('location'),
                     webpage_fr.absolute_url())
    self.assertEqual(self.publish(website_bg_en_fr.absolute_url(relative=1)+'?a=b&c=d').getHeader('location'),
                     website_fr.absolute_url()+'?a=b&c=d')

    # /bg/en/xxx should be redirected to /xxx where en is the default language
    website_bg_en = self.portal.restrictedTraverse(
      'web_site_module/%s/bg/en' % website_id)
    websection_bg_en = self.portal.restrictedTraverse(
      'web_site_module/%s/bg/en/%s' % (website_id, websection_id))
    webpage_bg_en = self.portal.restrictedTraverse(
      'web_site_module/%s/bg/en/%s/%s' % (website_id, websection_id, page_ref))
    self.assertEqual(self.publish(website_bg_en.absolute_url(relative=1)).getHeader('location'),
                     website.absolute_url())
    self.assertEqual(self.publish(websection_bg_en.absolute_url(relative=1)).getHeader('location'),
                     websection.absolute_url())
    self.assertEqual(self.publish(webpage_bg_en.absolute_url(relative=1)).getHeader('location'),
                     webpage.absolute_url())
    self.assertEqual(self.publish(websection_bg_en.absolute_url(relative=1)+'?a=b&c=d').getHeader('location'),
                     websection.absolute_url()+'?a=b&c=d')

    # /en/xxx should be redirected to /xxx where en is the default language
    website_en = self.portal.restrictedTraverse(
      'web_site_module/%s/en' % website_id)
    websection_en = self.portal.restrictedTraverse(
      'web_site_module/%s/en/%s' % (website_id, websection_id))
    webpage_en = self.portal.restrictedTraverse(
      'web_site_module/%s/en/%s/%s' % (website_id, websection_id, page_ref))
    self.assertEqual(self.publish(website_en.absolute_url(relative=1)).getHeader('location'),
                     website.absolute_url())
    self.assertEqual(self.publish(websection_en.absolute_url(relative=1)).getHeader('location'),
                     websection.absolute_url())
    self.assertEqual(self.publish(webpage_en.absolute_url(relative=1)).getHeader('location'),
                     webpage.absolute_url())
    self.assertEqual(self.publish(webpage_en.absolute_url(relative=1)+'?a=b&c=d').getHeader('location'),
                     webpage.absolute_url()+'?a=b&c=d')

  def test_13_DocumentCache(self):
    """
      Test that when a document is modified, it can be accessed through a
      web_site, a web_section or wathever and display the last content (not an
      old cache value of the document).
    """
    portal = self.getPortal()
    request = portal.REQUEST
    request['PARENTS'] = [self.app]
    website = self.setupWebSite()
    web_section_portal_type = 'Web Section'
    web_section = website.newContent(portal_type=web_section_portal_type)

    content = '<p>initial text</p>'
    new_content = '<p>modified text<p>'
    document = portal.web_page_module.newContent(portal_type='Web Page',
            id='document_cache',
            reference='NXD-Document.Cache',
            text_content=content)
    document.publish()
    self.tic()
    self.assertEqual(document.asText().strip(), 'initial text')

    # First make sure conversion already exists on the web site
    web_document = website.restrictedTraverse('NXD-Document.Cache')
    self.assertTrue(web_document.hasConversion(format='txt'))
    web_document = web_section.restrictedTraverse('NXD-Document.Cache')
    self.assertTrue(web_document.hasConversion(format='txt'))

    # Through the web_site.
    path = website.absolute_url_path() + '/NXD-Document.Cache'
    response = self.publish(path, self.credential)
    self.assertNotEquals(response.getBody().find(content), -1)

    # Through a web_section.
    path = web_section.absolute_url_path() + '/NXD-Document.Cache'
    response = self.publish(path, self.credential)
    self.assertNotEquals(response.getBody().find(content), -1)

    # modified the web_page content
    document.edit(text_content=new_content)
    self.assertEqual(document.asText().strip(), 'modified text')
    self.tic()

    # check the cache doesn't send again the old content
    # Through the web_site.
    path = website.absolute_url_path() + '/NXD-Document.Cache'
    response = self.publish(path, self.credential)
    self.assertNotEquals(response.getBody().find(new_content), -1)

    # Through a web_section.
    path = web_section.absolute_url_path() + '/NXD-Document.Cache'
    response = self.publish(path, self.credential)
    self.assertNotEquals(response.getBody().find(new_content), -1)

  def test_13a_DocumentMovedCache(self):
    """
      What happens to the cache if document is moved
      with a new ID. Can we still access content,
      or is the cache emptied. There is no reason
      that the cache should be regenerated or that the
      previous cache would not be emptied.

      Here, we test that the cache is not regenerated,
      not emptied, and still available.
    """
    portal = self.getPortal()
    request = portal.REQUEST
    request['PARENTS'] = [self.app]
    website = self.setupWebSite()
    web_section_portal_type = 'Web Section'
    web_section = website.newContent(portal_type=web_section_portal_type)

    content = '<p>initial text</p>'
    new_content = '<p>modified text<p>'
    document = portal.web_page_module.newContent(portal_type='Web Page',
            id='document_original_cache',
            reference='NXD-Document.Cache',
            text_content=content)
    document.publish()
    self.tic()
    self.assertEqual(document.asText().strip(), 'initial text')

    # Make sure document cache keeps converted content even if ID changes
    self.assertTrue(document.hasConversion(format='txt'))
    document.setId('document_new_cache')
    self.assertTrue(document.hasConversion(format='txt'))
    document.setId('document_original_cache')
    self.assertTrue(document.hasConversion(format='txt'))

  def test_13b_DocumentEditCacheKey(self):
    """
      What happens if a web page is edited on a web site ?
      Is converted content cleared and updated ? Or
      is a wrong cache key created ? Here, we make sure
      that the content is updated and the cache cleared
      and reset.
    """
    portal = self.getPortal()
    request = portal.REQUEST
    request['PARENTS'] = [self.app]
    website = self.setupWebSite()
    web_section_portal_type = 'Web Section'
    web_section = website.newContent(portal_type=web_section_portal_type)

    content = '<p>initial text</p>'
    new_content = '<p>modified text</p>'
    document = portal.web_page_module.newContent(portal_type='Web Page',
            id='document_cache',
            reference='NXD-Document.Cache',
            text_content=content)
    document.publish()
    self.tic()
    self.assertEqual(document.asText().strip(), 'initial text')

    # Through the web_site.
    path = website.absolute_url_path() + '/NXD-Document.Cache'
    response = self.publish(path, self.credential)
    self.assertNotEquals(response.getBody().find(content), -1)
    # Through a web_section.
    path = web_section.absolute_url_path() + '/NXD-Document.Cache'
    response = self.publish(path, self.credential)
    self.assertNotEquals(response.getBody().find(content), -1)

    # Modify the web_page content
    # Use unrestrictedTraverse (XXX-JPS reason unknown)
    web_document = website.unrestrictedTraverse('web_page_module/%s' % document.getId())
    web_document.edit(text_content=new_content)
    # Make sure cached is emptied
    self.assertFalse(web_document.hasConversion(format='txt'))
    self.assertFalse(document.hasConversion(format='txt'))
    # Make sure cache is regenerated
    self.assertEqual(web_document.asText().strip(), 'modified text')
    self.tic()

    # First make sure conversion already exists (since it should
    # have been generated previously)
    self.assertTrue(document.hasConversion(format='txt'))
    web_document = web_section.restrictedTraverse('NXD-Document.Cache')
    self.assertTrue(web_document.hasConversion(format='txt'))
    web_document = website.restrictedTraverse('NXD-Document.Cache')
    self.assertTrue(web_document.hasConversion(format='txt'))

    # check the cache doesn't send again the old content
    # test this fist on the initial document
    self.assertEqual(document.asText().strip(), 'modified text')

    # Through a web_section.
    web_document = web_section.restrictedTraverse('NXD-Document.Cache')
    self.assertEqual(web_document.asText().strip(), 'modified text')
    path = web_section.absolute_url_path() + '/NXD-Document.Cache'
    response = self.publish(path, self.credential)
    self.assertNotEquals(response.getBody().find(new_content), -1)

    # Through a web_site.
    web_document = website.restrictedTraverse('NXD-Document.Cache')
    self.assertEqual(web_document.asText().strip(), 'modified text')
    path = website.absolute_url_path() + '/NXD-Document.Cache'
    response = self.publish(path, self.credential)
    self.assertNotEquals(response.getBody().find(new_content), -1)

  def test_14_AccessWebSiteForWithDifferentUserPreferences(self):
    """Check that Ram Cache Manager do not mix websection
    rendering between users.
    This test enable different preferences per users and check that
    those preferences doesn't affect rendering for other users.
    user          | preference

    administrator | developper_mode activated
    webeditor     | translator_mode activated
    anonymous     | developper_mode & translator_mode disabled

    The Signature used to detect enabled preferences in HTML Body are
    manage_main for developper_mode
    manage_messages for translator_mode
    """
    user = self.createUser('administrator')
    self.createUserAssignement(user, {})
    user = self.createUser('webeditor')
    self.createUserAssignement(user, {})
    self.tic()
    preference_tool = self.getPreferenceTool()
    isTransitionPossible = self.portal.portal_workflow.isTransitionPossible

    # create or edit preference for administrator
    administrator_preference = self.portal.portal_catalog.getResultValue(
                                                 portal_type='Preference',
                                                 owner='administrator')
    if administrator_preference is None:
      self.loginByUserName('administrator')
      administrator_preference = preference_tool.newContent(
                                              portal_type='Preference')
    if isTransitionPossible(administrator_preference, 'enable_action'):
      administrator_preference.enable()

    administrator_preference.setPreferredHtmlStyleDevelopperMode(True)
    administrator_preference.setPreferredHtmlStyleTranslatorMode(False)

    # create or edit preference for webeditor
    webeditor_preference = self.portal.portal_catalog.getResultValue(
                                                  portal_type='Preference',
                                                  owner='webeditor')
    if webeditor_preference is None:
      self.loginByUserName('webeditor')
      webeditor_preference = preference_tool.newContent(
                                              portal_type='Preference')
    if isTransitionPossible(webeditor_preference, 'enable_action'):
      webeditor_preference.enable()

    webeditor_preference.setPreferredHtmlStyleDevelopperMode(False)
    webeditor_preference.setPreferredHtmlStyleTranslatorMode(True)
    self.login()
    self.tic()

    web_site = self.setupWebSite()
    websection = self.setupWebSection()

    websection_url = '%s/%s' % (self.portal.getId(), websection.getRelativeUrl())

    # connect as administrator and check that only developper_mode is enable
    response = self.publish(websection_url, 'administrator:administrator')
    self.assertTrue('manage_main' in response.getBody())
    self.assertTrue('manage_messages' not in response.getBody())

    # connect as webeditor and check that only translator_mode is enable
    response = self.publish(websection_url, 'webeditor:webeditor')
    self.assertTrue('manage_main' not in response.getBody())
    self.assertTrue('manage_messages' in response.getBody())

    # anonymous user doesn't exists, check anonymous access without preferences
    response = self.publish(websection_url, 'anonymous:anonymous')
    self.assertTrue('manage_main' not in response.getBody())
    self.assertTrue('manage_messages' not in response.getBody())

  def test_15_Check_LastModified_Header(self):
    """Checks that Last-Modified header set by caching policy manager
    is correctly filled with getModificationDate of content.
    This test check 2 Policy installed by erp5_web:
    Policy ID - unauthenticated web pages
                authenticated
    """
    website = self.setupWebSite()
    web_section_portal_type = 'Web Section'
    web_section = website.newContent(portal_type=web_section_portal_type)

    content = '<p>initial text</p>'
    document = self.portal.web_page_module.newContent(portal_type='Web Page',
            id='document_cache',
            reference='NXD-Document.Cache',
            text_content=content)
    document.publish()
    # clear cache used in Base_getWebDocumentDrivenModificationDate
    self.portal.portal_caches.clearAllCache()
    self.tic()
    path = website.absolute_url_path() + '/NXD-Document.Cache'
    # test Different Policy installed by erp5_web
    # unauthenticated web pages
    response = self.publish(path)
    last_modified_header = response.getHeader('Last-Modified')
    self.assertTrue(last_modified_header)
    from App.Common import rfc1123_date
    # Convert the Date into string according RFC 1123 Time Format
    modification_date = rfc1123_date(document.getModificationDate())
    self.assertEqual(modification_date, last_modified_header)

    # authenticated
    user = self.createUser('webmaster')
    self.createUserAssignement(user, {})
    response = self.publish(path, 'webmaster:webmaster')
    last_modified_header = response.getHeader('Last-Modified')
    self.assertTrue(last_modified_header)
    # Convert the Date into string according RFC 1123 Time Format
    modification_date = rfc1123_date(document.getModificationDate())
    self.assertEqual(modification_date, last_modified_header)

  def test_15a_CheckCachingPolicyManager(self):
    """
    Check if caching_policy_manager is well applied even if custom
    render method is used in Web Site or Web Section.
    """
    web_site = self.setupWebSite()
    web_section_portal_type = 'Web Section'
    web_section = web_site.newContent(portal_type=web_section_portal_type)
    self.assertTrue(self.publish(web_site.absolute_url_path()).getHeader('X-Cache-Headers-Set-By'))
    web_site.setCustomRenderMethodId('WebSection_viewAsWeb')
    self.assertTrue(self.publish(web_site.absolute_url_path()).getHeader('X-Cache-Headers-Set-By'))
    self.assertTrue(self.publish(web_section.absolute_url_path()).getHeader('X-Cache-Headers-Set-By'))
    web_section.setCustomRenderMethodId('WebSection_viewAsWeb')
    self.assertTrue(self.publish(web_section.absolute_url_path()).getHeader('X-Cache-Headers-Set-By'))

  def test_16_404ErrorPageIsReturned(self):
    """
      Test that when we try to access a non existing url trought a web site, a
      404 error page is returned
    """
    portal = self.getPortal()
    request = portal.REQUEST
    request['PARENTS'] = [self.app]
    website = self.setupWebSite()
    path = website.absolute_url_path() + '/a_non_existing_page'
    absolute_url = website.absolute_url() + '/a_non_existing_page'
    request = portal.REQUEST

    # Check a Not Found page is returned
    self.assertTrue('Not Found' in request.traverse(path)())
    # Check that we try to display a page with 404.error.page reference
    self.assertEqual(request.traverse(path).absolute_url().split('/')[-1],
    '404.error.page')

  @expectedFailure
  def test_17_WebSectionEditionWithLanguageInURL(self):
    """
    Check that editing a web section with the language in the URL
    does not prevent indexation.

    - Create a web site
    - Activate the language in the URL
    - Create a web section
    - Access it using another language and edit it
    - Check that web section is correctly indexed
    """
    language = 'de'

    website = self.setupWebSite()
    # Check that language in defined in the URL
    self.assertEqual(True, website.getStaticLanguageSelection())
    self.assertNotEquals(language, website.getDefaultAvailableLanguage())

    websection = self.setupWebSection()
    self.assertEqual(websection.getId(), websection.getTitle())

    self.tic()
    response = self.publish('/%s/%s/%s/%s/Base_editAndEditAsWeb' % \
                    (self.portal.getId(), website.getRelativeUrl(),
                     language, websection.getId()),
                     basic='ERP5TypeTestCase:',
                     request_method='POST',
                     stdin=StringIO(urlencode({
                       'form_id': 'WebSection_view',
                       'form_action': 'Base_edit',
                       'edit_document_url': '%s/%s/%s/WebSection_view' % \
                           (website.absolute_url(), language,
                             websection.getId()),
                       'field_my_title': '%s_edited' % websection.getId(),
                     }))
                    )

    self.assertEqual(MOVED_TEMPORARILY, response.getStatus())
    new_location = response.getHeader('Location')
    new_location = new_location.split('/', 3)[-1]

    self.tic()

    response = self.publish(new_location, basic='ERP5TypeTestCase:',)
    self.assertEqual(HTTP_OK, response.getStatus())
    self.assertEqual('text/html; charset=utf-8',
                      response.getHeader('content-type'))
    self.assertTrue("Data updated." in response.getBody())

    self.tic()

    self.assertEqual('%s_edited' % websection.getId(), websection.getTitle())
    self.assertEqual(1, len(self.portal.portal_catalog(
                                    relative_url=websection.getRelativeUrl(),
                                    title=websection.getTitle())))

  @expectedFailure
  def test_18_WebSiteEditionWithLanguageInURL(self):
    """
    Check that editing a web section with the language in the URL
    does not prevent indexation.

    - Create a web site
    - Activate the language in the URL
    - Access it using another language and edit it
    - Check that web site is correctly modified
    """
    language = 'de'

    website = self.setupWebSite()
    # Check that language in defined in the URL
    self.assertEqual(True, website.getStaticLanguageSelection())
    self.assertNotEquals(language, website.getDefaultAvailableLanguage())

    self.assertEqual(website.getId(), website.getTitle())

    self.tic()

    response = self.publish('/%s/%s/%s/Base_editAndEditAsWeb' % \
                    (self.portal.getId(), website.getRelativeUrl(),
                     language),
                     basic='ERP5TypeTestCase:',
                     request_method='POST',
                     stdin=StringIO(urlencode({
                       'form_id': 'WebSite_view',
                       'form_action': 'Base_edit',
                       'edit_document_url': '%s/%s/WebSite_view' % \
                           (website.absolute_url(), language),
                       'field_my_title': '%s_edited' % website.getId(),
                       'field_my_id': language,
                     }))
                    )

    self.assertEqual(MOVED_TEMPORARILY, response.getStatus())
    new_location = response.getHeader('Location')
    new_location = new_location.split('/', 3)[-1]

    self.tic()

    response = self.publish(new_location, basic='ERP5TypeTestCase:',)
    self.assertEqual(HTTP_OK, response.getStatus())
    self.assertEqual('text/html; charset=utf-8',
                      response.getHeader('content-type'))
    self.assertTrue("Data updated." in response.getBody())

    self.tic()

    self.assertEqual('%s_edited' % website.getId(), website.getTitle())
    self.assertEqual(1, len(self.portal.portal_catalog(
                                    relative_url=website.getRelativeUrl(),
                                    title=website.getTitle())))

  def test_19_WebModeAndEditableMode(self):
    """
    Check if isWebMode & isEditableMode API works.
    """
    request = self.app.REQUEST
    website = self.setupWebSite()

    # web mode
    self.assertEqual(False, self.portal.person_module.isWebMode())
    self.assertEqual(True, website.isWebMode())
    self.assertEqual(True, getattr(website, 'person_module').isWebMode())

    # editable mode
    self.assertEqual(False, self.portal.person_module.isEditableMode())
    self.assertEqual(False, website.isEditableMode())
    self.assertEqual(False, getattr(website, 'person_module').isEditableMode())

    request.set('editable_mode', 1)
    self.assertEqual(1, self.portal.person_module.isEditableMode())
    self.assertEqual(1, website.isEditableMode())
    self.assertEqual(1, getattr(website, 'person_module').isEditableMode())

  def test_20_reStructuredText(self):
    web_page = self.portal.web_page_module.newContent(portal_type='Web Page',
                                                      content_type='text/x-rst')
    web_page.edit(text_content="`foo`")
    self.assertTrue('<cite>foo</cite>' in web_page.asEntireHTML(charset='utf-8'))
    self.assertTrue('<cite>foo</cite>' in web_page.asEntireHTML())

  def test_21_WebSiteMap(self):
    """
      Test Web Site map script.
    """
    request = self.app.REQUEST
    website = self.setupWebSite()
    kw = {'depth': 5,
          'include_subsection': 1}

    website.setSiteMapSectionParent(1)
    websection1 = website.newContent(portal_type='Web Section',
                                     title='Section 1',
                                     site_map_section_parent=1,
                                     visible=1)
    websection1_1 = websection1.newContent(portal_type='Web Section',
                                     title='Section 1.1',
                                     site_map_section_parent=1,
                                     visible=1)
    self.tic()
    site_map = website.WebSection_getSiteMapTree(depth=5, include_subsection=1)
    self.assertSameSet([websection1.getTitle()],
                       [x['translated_title'] for x in site_map])
    self.assertSameSet([websection1_1.getTitle()],
                       [x['translated_title'] for x in site_map[0]['subsection']])
    self.assertEqual(1, site_map[0]['level'])
    self.assertEqual(2, site_map[0]['subsection'][0]['level'])

    # check depth works
    site_map = website.WebSection_getSiteMapTree(depth=1, include_subsection=1)
    self.assertEqual(None, site_map[0]['subsection'])
    self.assertSameSet([websection1.getTitle()],
                       [x['translated_title'] for x in site_map])

    # hide subsections
    websection1_1.setSiteMapSectionParent(0)
    websection1_1.setVisible(0)
    self.tic()
    site_map = website.WebSection_getSiteMapTree(depth=5, include_subsection=1)
    self.assertSameSet([websection1.getTitle()],
                       [x['translated_title'] for x in site_map])
    self.assertEqual(None, site_map[0]['subsection'])

  def test_future_publication_date_not_visible(self):
    portal = self.portal
    reference = 'test_future_publication_date_not_visible'
    newContent = portal.web_page_module.newContent
    date1 = DateTime()
    date2 = date1 + 1
    date3 = date2 + 1
    date4 = date3 + 1

    def new(**kw):
      result = newContent(
        portal_type='Web Page',
        reference=reference,
        **kw
      )
      self.tic()
      result.publish()
      self.tic()
      return result
    document1 = new(version=1)
    document2 = new(version=2, effective_date=date2)
    # Some more documents which should never be visible.
    # Bind them to local variables for quicker debugging, if needed.
    # Later than document2.
    document3 = new(version=3, effective_date=date4)
    # Like document1, but not published
    document4 = newContent(
      portal_type='Web Page',
      reference=reference,
    )
    # Like document2, but not published
    document5 = newContent(
      portal_type='Web Page',
      reference=reference,
      effective_date=date2,
    )
    self.tic()
    site = portal.web_site_module.newContent(
      portal_type='Web Site',
    )
    site.publish()
    section = site.newContent(
      portal_type='Web Section',
    )
    section.setCriterionProperty('reference')
    section.setCriterion(
      'reference',
      max='',
      identity=[reference],
      min='',
    )
    self.tic()

    self.assertEqual(document1.getValidationState(), 'published')
    self.assertEqual(document2.getValidationState(), 'published')
    self.assertEqual(document3.getValidationState(), 'published')
    self.assertEqual(document4.getValidationState(), 'draft')
    self.assertEqual(document5.getValidationState(), 'draft')
    def check(expected_document, date):
      document = section.WebSection_getDocumentValue(reference, now=date)
      self.assertNotEqual(document, None)
      self.assertEqual(document.getPath(), expected_document.getPath())
      document_list = section.getDocumentValueList(now=date)
      self.assertEqual(len(document_list), 1)
      self.assertEqual(document_list[0].getPath(), expected_document.getPath())
    # document1 is visible & listed before date2
    check(document1, date1)
    # document2 is visible & listed at and above date2
    check(document2, date2)
    check(document2, date3)

class TestERP5WebWithSimpleSecurity(ERP5TypeTestCase):
  """
  Test for erp5_web with simple security.
  """

  def getBusinessTemplateList(self):
    return ('erp5_base',
            'erp5_pdm',
            'erp5_trade',
            'erp5_project',
            'erp5_web',
            )

  def getTitle(self):
    return "Web"

  def createUser(self, name, role_list):
    user_folder = self.getPortal().acl_users
    user_folder._doAddUser(name, 'password', role_list, [])

  def afterSetUp(self):
    self.web_site_module = self.portal.web_site_module
    self.portal.Localizer = DummyLocalizer()
    self.createUser('admin', ['Manager'])
    self.createUser('erp5user', ['Auditor', 'Author'])
    self.createUser('webmaster', ['Assignor'])
    self.tic()

  def clearModule(self, module):
    module.manage_delObjects(list(module.objectIds()))
    self.tic()

  def beforeTearDown(self):
    self.clearModule(self.portal.web_site_module)
    self.clearModule(self.portal.web_page_module)

  def test_01_AccessWebPageByReference(self):
    self.loginByUserName('admin')
    site = self.portal.web_site_module.newContent(portal_type='Web Site',
                                                  id='site')
    section = site.newContent(portal_type='Web Section', id='section')

    self.tic()

    section.setCriterionProperty('portal_type')
    section.setCriterion('portal_type', max='', identity=['Web Page'], min='')

    self.tic()

    self.loginByUserName('erp5user')
    page_en = self.portal.web_page_module.newContent(portal_type='Web Page')
    page_en.edit(reference='my-first-web-page',
                 language='en',
                 version='1',
                 text_format='text/plain',
                 text_content='Hello, World!')

    self.tic()

    page_en.publish()

    self.tic()

    page_ja = self.portal.web_page_module.newContent(portal_type='Web Page')
    page_ja.edit(reference='my-first-web-page',
                 language='ja',
                 version='1',
                 text_format='text/plain',
                 text_content='こんにちは、世界！')

    self.tic()

    page_ja.publish()

    self.tic()

    # By Anonymous
    self.logout()

    self.portal.Localizer.changeLanguage('en')

    target = self.portal.unrestrictedTraverse('web_site_module/site/section/my-first-web-page')
    self.assertEqual('Hello, World!', target.getTextContent())

    self.portal.Localizer.changeLanguage('ja')

    target = self.portal.unrestrictedTraverse('web_site_module/site/section/my-first-web-page')
    self.assertEqual('こんにちは、世界！', target.getTextContent())

  def test_02_LocalRolesFromRoleDefinition(self):
    """ Test setting local roles on Web Site/ Web Sectio using ERP5 Role Definition objects . """
    portal = self.portal
    person_reference = 'webuser'
    site = portal.web_site_module.newContent(portal_type='Web Site',
                                                  id='site')
    section = site.newContent(portal_type='Web Section', id='section')
    person = portal.person_module.newContent(portal_type = 'Person',
                                             reference = person_reference)
    person_user_id = person.Person_getUserId()
    # add Role Definition for site and section
    site_role_definition = site.newContent(portal_type = 'Role Definition',
                                           role_name = 'Assignee',
                                           agent = person.getRelativeUrl())
    section_role_definition = section.newContent(portal_type = 'Role Definition',
                                                 role_name = 'Associate',
                                                 agent = person.getRelativeUrl())
    self.tic()
    # check if Role Definition have create local roles
    self.assertSameSet(('Assignee',),
                          site.get_local_roles_for_userid(person_user_id))
    self.assertSameSet(('Associate',),
                          section.get_local_roles_for_userid(person_user_id))
    self.assertRaises(Unauthorized, site_role_definition.edit,
                      role_name='Manager')

    # delete Role Definition and check again (local roles must be gone too)
    site.manage_delObjects(site_role_definition.getId())
    section.manage_delObjects(section_role_definition.getId())
    self.tic()
    self.assertSameSet((),
                       site.get_local_roles_for_userid(person_user_id))
    self.assertSameSet((),
                       section.get_local_roles_for_userid(person_user_id))

  def test_03_getDocumentValueListSecurity(self):
    """ Test getDocumentValueList behaviour and security"""
    self.loginByUserName('admin')
    site = self.portal.web_site_module.newContent(portal_type='Web Site',
                                      id='site')
    site.publish()

    section = site.newContent(portal_type='Web Section',
                              id='section')

    self.tic()

    section.setCriterionProperty('portal_type')
    section.setCriterion('portal_type', max='',
                         identity=['Web Page'], min='')

    self.tic()

    self.loginByUserName('erp5user')
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

    self.commit()
    self.loginByUserName('erp5user')
    self.tic()
    self.portal.Localizer.changeLanguage('en')

    self.assertEqual(0, len(section.getDocumentValueList()))

    self.loginByUserName('erp5user')
    page_en_0.publish()
    self.tic()

    self.portal.Localizer.changeLanguage('en')
    self.assertEqual(1, len(section.getDocumentValueList()))
    self.assertEqual(page_en_0.getUid(),
                      section.getDocumentValueList()[0].getUid())

    self.portal.Localizer.changeLanguage('jp')
    self.assertEqual(0, len(section.getDocumentValueList()))

    # By Anonymous
    self.logout()
    self.portal.Localizer.changeLanguage('en')
    self.assertEqual(1, len(section.getDocumentValueList()))
    self.assertEqual(page_en_0.getUid(),
                      section.getDocumentValueList()[0].getUid())
    self.portal.Localizer.changeLanguage('jp')
    self.assertEqual(0, len(section.getDocumentValueList()))

    # Second Object
    self.loginByUserName('erp5user')
    page_en_1.publish()
    self.tic()

    self.portal.Localizer.changeLanguage('en')
    self.assertEqual(1, len(section.getDocumentValueList()))
    self.assertEqual(page_en_1.getUid(),
                      section.getDocumentValueList()[0].getUid())
    self.portal.Localizer.changeLanguage('jp')
    self.assertEqual(0, len(section.getDocumentValueList()))

    # By Anonymous
    self.logout()
    self.portal.Localizer.changeLanguage('en')
    self.assertEqual(1, len(section.getDocumentValueList()))
    self.assertEqual(page_en_1.getUid(),
                      section.getDocumentValueList()[0].getUid())

    # Trird Object
    self.loginByUserName('erp5user')
    page_en_2.publish()
    self.tic()

    self.portal.Localizer.changeLanguage('en')
    self.assertEqual(2, len(section.getDocumentValueList()))
    self.portal.Localizer.changeLanguage('jp')
    self.assertEqual(0, len(section.getDocumentValueList()))

    # By Anonymous
    self.logout()
    self.portal.Localizer.changeLanguage('en')
    self.assertEqual(2, len(section.getDocumentValueList()))
    self.portal.Localizer.changeLanguage('jp')
    self.assertEqual(0, len(section.getDocumentValueList()))

    # First Japanese Object
    self.loginByUserName('erp5user')
    page_jp_0.publish()
    self.tic()

    self.portal.Localizer.changeLanguage('en')
    self.assertEqual(2, len(section.getDocumentValueList()))
    self.portal.Localizer.changeLanguage('jp')
    self.assertEqual(1, len(section.getDocumentValueList()))

    # By Anonymous
    self.logout()
    self.portal.Localizer.changeLanguage('en')
    self.assertEqual(2, len(section.getDocumentValueList()))
    self.portal.Localizer.changeLanguage('jp')
    self.assertEqual(1, len(section.getDocumentValueList()))
    self.assertEqual(page_jp_0.getUid(),
                      section.getDocumentValueList()[0].getUid())

  def test_04_ExpireUserAction(self):
    """ Test the expire user action"""
    self.loginByUserName('admin')
    site = self.portal.web_site_module.newContent(portal_type='Web Site', id='site')

    # create websections in a site and in anothers web sections
    section_1 = site.newContent(portal_type='Web Section', id='section_1')
    section_2 = site.newContent(portal_type='Web Section', id='section_2')
    section_3 = site.newContent(portal_type='Web Section', id='section_3')
    section_4 = site.newContent(portal_type='Web Section', id='section_4')
    section_5 = section_3.newContent(portal_type='Web Section', id='section_5')
    section_6 = section_4.newContent(portal_type='Web Section', id='section_6')
    self.tic()

    # test if a manager can expire them
    try:
      section_1.expire()
      section_5.expire()
    except Unauthorized:
      self.fail("Admin should be able to expire a Web Section.")

    # test if a user (ASSIGNOR) can expire them
    self.loginByUserName('webmaster')
    try:
      section_2.expire()
      section_6.expire()
    except Unauthorized:
      self.fail("An user should be able to expire a Web Section.")

  def test_05_createWebSite(self):
    """ Test to create or clone web sites with many users """
    self.loginByUserName('admin')
    web_site_module = self.portal.web_site_module

    # test for admin
    try:
      site_1 = web_site_module.newContent(portal_type='Web Site', id='site_1')
    except Unauthorized:
      self.fail("Admin should be able to create a Web Site.")

    # test as a web user (assignor)
    self.loginByUserName('webmaster')
    try:
      site_2 = web_site_module.newContent(portal_type='Web Site', id='site_2')
    except Unauthorized:
      self.fail("A webmaster should be able to create a Web Site.")

    site_2_copy = web_site_module.manage_copyObjects(ids=(site_2.getId(),))
    site_2_clone = web_site_module[web_site_module.manage_pasteObjects(
      site_2_copy)[0]['new_id']]
    self.assertEqual(site_2_clone.getPortalType(), 'Web Site')

  def test_06_createWebSection(self):
    """ Test to create or clone web sections with many users """
    self.loginByUserName('admin')
    site = self.portal.web_site_module.newContent(portal_type='Web Site', id='site')

    # test for admin
    try:
      section_1 = site.newContent(portal_type='Web Section', id='section_1')
      section_2 = section_1.newContent(portal_type='Web Section', id='section_2')
    except Unauthorized:
      self.fail("Admin should be able to create a Web Section.")

    # test as a webmaster (assignor)
    self.loginByUserName('webmaster')
    try:
      section_2 = site.newContent(portal_type='Web Section', id='section_2')
      section_3 = section_2.newContent(portal_type='Web Section', id='section_3')
    except Unauthorized:
      self.fail("A webmaster should be able to create a Web Section.")
    section_2_copy = site.manage_copyObjects(ids=(section_2.getId(),))
    section_2_clone = site[site.manage_pasteObjects(
      section_2_copy)[0]['new_id']]
    self.assertEqual(section_2_clone.getPortalType(), 'Web Section')
    section_3_copy = section_2.manage_copyObjects(ids=(section_3.getId(),))
    section_3_clone = section_2[section_2.manage_pasteObjects(
      section_3_copy)[0]['new_id']]
    self.assertEqual(section_3_clone.getPortalType(), 'Web Section')

  def test_07_createCategory(self):
    """ Test to create or clone categories with many users """
    self.loginByUserName('admin')
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
    self.assertEqual(category_1_clone.getPortalType(), 'Category')
    category_2_copy = category_1.manage_copyObjects(ids=(category_2.getId(),))
    category_2_clone = category_1[category_1.manage_pasteObjects(
      category_2_copy)[0]['new_id']]
    self.assertEqual(category_2_clone.getPortalType(), 'Category')

    # test as a web user (assignor)
    self.loginByUserName('webmaster')
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
    self.assertEqual(category_3_clone.getPortalType(), 'Category')
    # try to clone a sub category of the different owner
    category_2_copy = category_1.manage_copyObjects(ids=(category_2.getId(),))
    category_2_clone = category_1[category_1.manage_pasteObjects(
      category_2_copy)[0]['new_id']]
    self.assertEqual(category_2_clone.getPortalType(), 'Category')
    # try to clone a sub category of the same owner
    category_4_copy = category_3.manage_copyObjects(ids=(category_4.getId(),))
    category_4_clone = category_3[category_3.manage_pasteObjects(
      category_4_copy)[0]['new_id']]
    self.assertEqual(category_4_clone.getPortalType(), 'Category')

  def test_08_createAndrenameCategory(self):
    """ Test to create or rename categories with many users """
    self.loginByUserName('admin')
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
    self.tic()
    try:
      new_cat_1_renamed = new_category_1.edit(id='new_cat_1_renamed')
      new_cat_2_renamed = new_category_2.edit(id='new_cat_2_renamed')
    except Unauthorized:
      self.fail("Admin should be able to rename a Category.")
    # test as a web user (assignor)
    self.loginByUserName('webmaster')
    try:
      base_category_2 = portal_categories.newContent(portal_type='Base Category', id='base_category_2')
      self.fail("A webmaster should not be able to create a Base Category.")
    except Unauthorized:
      pass
    try:
      new_category_3 = publication_section.newContent(
      portal_type='Category', id='new_category_3')
      new_category_4 = new_category_3.newContent(portal_type='Category',
          id='new_category_4')
    except Unauthorized:
      self.fail("A webmaster should be able to create a Category.")
    self.tic()
    try:
      new_cat_3_renamed = new_category_3.edit(id='new_cat_3_renamed')
      new_cat_4_renamed = new_category_4.edit(id='new_cat_4_renamed')
    except Unauthorized:
      self.fail("A webmaster should be able to rename a Category.")

  def test_getDocumentValueList_AnonymousUser(self):
    """
      For a given Web Site with Predicates:
      - membership_criterion_base_category: follow_up
      - membership_criterion_document_list: follow_up/project/object_id

      When you access website/WebSection_viewContentListAsRSS:
      - with super user you get the correct result
      - with anonymous user you do not get the correct result

      In this case, both Web Pages are returned for Anonymous user and this
      it not the expected behavior.

      Note: The ListBox into WebSection_viewContentListAsRSS has
            getDocumentValueList defined as ListMethod.
    """
    project = self.portal.project_module.newContent(portal_type='Project')
    project.validate()
    self.tic()

    website = self.portal.web_site_module.newContent(portal_type='Web Site',
                                                     id='site')
    website.publish()
    website.setMembershipCriterionBaseCategory('follow_up')
    website.setMembershipCriterionDocumentList(['follow_up/%s' %
                                                  project.getRelativeUrl()])
    self.tic()

    web_page_module = self.portal.web_page_module
    web_page_follow_up = web_page_module.newContent(portal_type="Web Page",
                                      follow_up=project.getRelativeUrl(),
                                      id='test_web_page_with_follow_up',
                                      reference='NXD-Document.Follow.Up.Test',
                                      version='001',
                                      language='en',
                                      text_content='test content')
    web_page_follow_up.publish()
    self.tic()

    web_page_no_follow_up = web_page_module.newContent(portal_type="Web Page",
                                      id='test_web_page_no_follow_up',
                                      reference='NXD-Document.No.Follow.Up.Test',
                                      version='001',
                                      language='en',
                                      text_content='test content')
    web_page_no_follow_up.publish()
    self.tic()

    self.assertEqual(1, len(website.getDocumentValueList()))

    self.logout()
    self.assertEqual(1, len(website.getDocumentValueList()))

  def test_WebSiteModuleDefaultSecurity(self):
    """
      Test that by default Anonymous User cannot access Web Site Module
    """
    self.logout()
    self.assertRaises(Unauthorized, self.portal.web_site_module.view)


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

  def test_category_embedded_delete(self):
    """On category publication workflow, deletion are "real"
    """
    self.doActionFor(self.category, 'delete_action')
    self.assertEqual([], self.category.getParentValue().contentValues())


class ERP5WebUpgraderMixin(object):
  """Test mixin that checks that web site or web sections are upgraded.

  Subclasses must set `upgraded` attribute.
  """
  upgraded = None # type: erp5.portal_type.WebSection
  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_web', )

  def test_empty_constraint(self):
    self.assertEqual(
        [], [str(m.getMessage()) for m in self.upgraded.checkConsistency()])

  def test_upgrader_fix_modification_date(self):
    # Upgrader sets the modification date on the web section if
    # it's older than its default page.
    html_page = self.portal.web_page_module.newContent(
        portal_type='Web Page',
        reference=self.id(),
    )
    html_page.publish()
    self.tic()

    self.upgraded.edit(aggregate_value=html_page)
    self.tic()
    time.sleep(1)
    html_page.edit(text_content="<p>Hello again</p>")
    self.tic()
    self.assertLess(
        self.upgraded.getModificationDate(),
        html_page.getModificationDate()
        )
    self.assertEqual(
        ['Web Section {} is older than default page'.format(self.upgraded.getRelativeUrl())],
        [str(m.getMessage()) for m in self.upgraded.checkConsistency()])
    self.upgraded.fixConsistency()
    self.tic()

    self.assertEqual(
        [], [str(m.getMessage()) for m in self.upgraded.checkConsistency()])
    self.assertGreater(
        self.upgraded.getModificationDate(),
        html_page.getModificationDate())


class TestERP5WebSiteUpgrader(ERP5WebUpgraderMixin, ERP5TypeTestCase):
  def afterSetUp(self):
    super(ERP5WebUpgraderMixin, self).afterSetUp()
    self.upgraded = self.portal.web_site_module.newContent(
        portal_type='Web Site',
    )


class TestERP5WebSectionUpgrader(ERP5WebUpgraderMixin, ERP5TypeTestCase):
  def afterSetUp(self):
    super(ERP5WebUpgraderMixin, self).afterSetUp()
    self.upgraded = self.portal.web_site_module.newContent(
        portal_type='Web Site',
    ).newContent(
        portal_type='Web Section',
    )

class TestERP5StaticWebSiteUpgrader(ERP5WebUpgraderMixin, ERP5TypeTestCase):
  def afterSetUp(self):
    super(ERP5WebUpgraderMixin, self).afterSetUp()
    self.upgraded = self.portal.web_site_module.newContent(
        portal_type='Static Web Site',
    )


class TestERP5StaticWebSectionUpgrader(ERP5WebUpgraderMixin, ERP5TypeTestCase):
  def afterSetUp(self):
    super(ERP5WebUpgraderMixin, self).afterSetUp()
    self.upgraded = self.portal.web_site_module.newContent(
        portal_type='Web Site',
    ).newContent(
        portal_type='Static Web Section',
    )
