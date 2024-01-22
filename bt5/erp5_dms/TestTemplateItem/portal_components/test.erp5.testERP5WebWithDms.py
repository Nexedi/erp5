# -*- coding: utf-8 -*-
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

import unittest
import os
import quopri
import functools
import requests
from six.moves import cStringIO as StringIO
from lxml import etree
from base64 import b64decode, b64encode
from email.parser import Parser as EmailParser

import transaction
from AccessControl import Unauthorized
from AccessControl.SecurityManagement import newSecurityManager
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import FileUpload, createZODBPythonScript
from erp5.component.document.Document import ConversionError

from PIL import Image
from six.moves import range

LANGUAGE_LIST = ('en', 'fr', 'de', 'bg',)
IMAGE_COMPARE_TOLERANCE = 850

XSMALL_SVG_IMAGE_ICON_DATA = '''<svg width="30" height="35" xmlns="http://www.w3.org/2000/svg">
  <path d="m5,5l15,0l0,5l5,0l0,20l-20,0z" stroke-width="1.5" stroke="gray" fill="skyblue"/>
  <path d="m6,29l8,-8l5,5l2,-2l3,3l0,2z" stroke-width="0" fill="green"/>
  <path d="m25,10l0,-1l-4,-4l-1,0l0,5z" stroke-width="1.5" stroke="gray" fill="white"/>
  <path d="m8,15c5,-8 10,-2 10,0z" stroke-width="0" fill="white"/>
</svg>'''
XSMALL_PNG_IMAGE_ICON_DATA = b64decode('''
iVBORw0KGgoAAAANSUhEUgAAAB4AAAAjCAIAAAAMti2GAAABkElEQVRIiWP8//8/A20AE43MHbJG
syBzduzY8fLlSyJ1vnv3joGBQUtLy93dnbDRL168ePj0OSO/CDFG///8meH//xMnTvz48cPf35+A
0QwMDIz8ImzWgcQY/XPbbHlpSQEBgQsXLjAwMGCajm40qSAgIICBgQGr6ZQajWw6Ozu7h4cHdYx+
+fLlwoUL4dxr165Rx2hGLr4f3z49ePIMxmdEU0DAaHZmRlNRThMxTg5mxo+//p1+9f3M6+8QKTaH
cGSVv46uF+JhJdZodmbGKFV+cU6oGn42JhcZbnEulq0PPxPwEQMDA57ciGYuHOgKsZuIclJktIsM
D6a5EGAqRpTROANk68PPRHocFxiaJd+o0WQaffbR8jUX8kgymqgyBNncEINJRBpN2NXI5pLkdgJG
Y5pFvE34AgSXzrOPljMwMCgKWeIPJZxG43fR2UfLIRbAbfJjcERTgz1ASE0PcGsIGE1GOsMK0APk
/6e3ek9E9ERmk2rQv49vGHgkcBotISHBQDbglkDTzjjaCKab0QBziJyFukqO6AAAAABJRU5ErkJg
gg==''')


def makeFilePath(name):
  from Products.ERP5 import tests
  return os.path.join(tests.__path__[0], 'test_data', name)

def makeFileUpload(name, as_name=None):
  if as_name is None:
    as_name = name
  path = makeFilePath(name)
  return FileUpload(path, as_name)

def process_image(image, size=(40, 40)):
  # open the images to compare, resize them, and convert to grayscale
  # get the rgb values of the pixels in the image
  image = Image.open(image)
  return list(image.resize(size).convert("L").getdata())

def compare_image(image_data_1, image_data_2):
  """ Find the total difference in RGB value for all pixels in the images
      and return the "amount" of differences that the 2 images contains. """
  data1 = process_image(image_data_1)
  data2 = process_image(image_data_2)
  return abs(sum([data1[x] - data2[x] for x in range(len(data1))]))

def customScript(script_id, script_param, script_code):
  def wrapper(func):
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
      if script_id in self.portal.portal_skins.custom.objectIds():
        raise ValueError('Precondition failed: %s exists in custom' % script_id)
      createZODBPythonScript(
        self.portal.portal_skins.custom,
        script_id,
        script_param,
        script_code,
      )
      try:
        func(self, *args, **kwargs)
      finally:
        if script_id in self.portal.portal_skins.custom.objectIds():
          self.portal.portal_skins.custom.manage_delObjects(script_id)
        transaction.commit()
    return wrapped
  return wrapper

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
    return ('erp5_core_proxy_field_legacy',
            'erp5_base',
            'erp5_jquery',
            'erp5_knowledge_pad',
            'erp5_web',
            'erp5_ingestion',
            'erp5_ingestion_mysql_innodb_catalog',
            'erp5_svg_editor',
            'erp5_dms',
            )

  def afterSetUp(self):
    self.login()
    self.web_page_module = self.portal.web_page_module
    self.web_site_module = self.portal.web_site_module
    self.portal_id = self.portal.getId()

  def clearModule(self, module):
    module.manage_delObjects(list(module.objectIds()))
    self.tic()

  def beforeTearDown(self):
    self.clearModule(self.portal.web_site_module)
    self.clearModule(self.portal.web_page_module)

  def setupWebSite(self, **kw):
    """
      Setup Web Site
    """
    portal = self.getPortal()

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
    website.publish()
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
    self.setupWebSite()
    websection = self.setupWebSection()
    page_reference = 'default-webpage-versionning'
    self.setupWebSitePages(prefix = page_reference)

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
    self.tic()

    # is old archived?
    self.assertEqual('archived', en_01.getValidationState())

    # is new public and default web page for section?
    portal.Localizer.manage_changeDefaultLang(language = 'en')
    default_document = websection.getDefaultDocumentValue()
    self.assertEqual(en_02, default_document)
    self.assertEqual('en', default_document.getLanguage())
    self.assertEqual('0.2', default_document.getVersion())
    self.assertEqual('published', default_document.getValidationState())

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
    self.setupWebSitePages(prefix = 'test-web-page')
    document_reference = 'default-document-reference'
    document = self.portal.web_page_module.newContent(
                                      portal_type = 'Web Page',
                                      reference = document_reference)
    document.release()
    website.setAuthorizationForced(0)
    websection.setAuthorizationForced(0)
    self.tic()

    # make sure that _getExtensibleContent will return the same document
    # there's not other way to test otherwise URL traversal
    self.assertEqual(document.getUid(),
                           websection._getExtensibleContent(request,  document_reference).getUid())

    # Anonymous User should have in the request header for not found when
    # viewing non available document in Web Section (with no authorization_forced)
    self.logout()
    self.assertEqual(None,  websection._getExtensibleContent(request,  document_reference))
    path = websection.absolute_url_path() + '/' + document_reference
    response = self.publish(path)
    self.assertEqual(404, response.getStatus())

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
    self.setupWebSite()
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
    self.tic()

    self.assertEqual(0,  len(websection.getDocumentValueList()))
    # create pages belonging to this publication_section 'documentation'
    web_page_en = portal.web_page_module.newContent(portal_type = 'Web Page',
                                                 language = 'en',
                                                 publication_section_list=publication_section_category_id_list[:1])
    web_page_en.publish()
    self.tic()
    self.assertEqual(1,  len(websection.getDocumentValueList(language='en')))
    self.assertEqual(web_page_en,  websection.getDocumentValueList(language='en')[0].getObject())

    # create pages belonging to this publication_section 'documentation' but for 'bg' language
    web_page_bg = portal.web_page_module.newContent(portal_type = 'Web Page',
                                                 language = 'bg',
                                                 publication_section_list=publication_section_category_id_list[:1])
    web_page_bg.publish()
    self.tic()
    self.assertEqual(1,  len(websection.getDocumentValueList(language='bg')))
    self.assertEqual(web_page_bg,  websection.getDocumentValueList(language='bg')[0].getObject())

    # reject page
    web_page_bg.reject()
    self.tic()
    self.assertEqual(0,  len(websection.getDocumentValueList(language='bg')))

    # publish page and search without a language (by default system should return 'en' docs only)
    web_page_bg.publish()
    self.tic()
    self.assertEqual(1,  len(websection.getDocumentValueList()))
    self.assertEqual(web_page_en,  websection.getDocumentValueList()[0].getObject())

  def test_04_WebSectionAuthorizationForcedForDefaultDocument(self, quiet=quiet, run=run_all_test):
    """ Check that when a Web Section contains a default document not accessible by user we have a chance to
        require user to login.
        Whether or not an user will login is controlled by a property on Web Section (authorization_forced).
    """
    if not run: return
    if not quiet:
      message = '\ntest_04_WebSectionAuthorizationForcedForDefaultDocument'
      ZopeTestCase._print(message)
    self.setupWebSite()
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
      self.commit()
      web_page_list.append(web_page)
    websection.setAggregateValueList(web_page_list)
    self.tic()
    self.commit()
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

  def test_06_Check_LastModified_Header(self):
    """Checks that Last-Modified header set by caching policy manager
    is correctly filled with getModificationDate of content.
    This test check "unauthenticated" Policy installed by erp5_web:
    """
    website = self.setupWebSite()
    website_url = website.absolute_url_path()
    response = self.publish(website_url)
    self.assertTrue(response.getHeader('x-cache-headers-set-by'),
                    'CachingPolicyManager: /erp5/caching_policy_manager')

    web_section_portal_type = 'Web Section'
    web_section = website.newContent(portal_type=web_section_portal_type)
    response = self.publish(web_section.absolute_url_path())
    self.assertTrue(response.getHeader('x-cache-headers-set-by'),
                    'CachingPolicyManager: /erp5/caching_policy_manager')

    # unauthenticated
    document_portal_type = 'Text'
    document_module = self.portal.getDefaultModule(document_portal_type)
    document = document_module.newContent(portal_type=document_portal_type,
                                          reference='NXD-Document-TEXT.Cache')
    document.publish()
    # Evaluation of last modification date for the site is cached
    self.portal.portal_caches.clearCache(cache_factory_list=('erp5_content_short', ))
    self.tic()
    response = self.publish(website_url + '/NXD-Document-TEXT.Cache')
    last_modified_header = response.getHeader('Last-Modified')
    self.assertTrue(last_modified_header)
    from App.Common import rfc1123_date
    # Convert the Date into string according RFC 1123 Time Format
    modification_date = rfc1123_date(document.getModificationDate())
    self.assertEqual(modification_date, last_modified_header)

    # Upload a presentation with 3 pages.
    upload_file = makeFileUpload('P-DMS-Presentation.3.Pages-001-en.odp')
    document = document_module.newContent(portal_type='Presentation',
                                          file=upload_file)
    reference = 'P-DMS-Presentation.3.Pages'
    document.edit(reference=reference)
    document.publish()
    self.portal.portal_caches.clearCache(cache_factory_list=('erp5_content_short', ))
    self.tic()
    # Check we can access to the 3 drawings converted into images.
    # Those images can be accessible through extensible content
    # url : path-of-document + '/' + 'img' + page-index + '.png'
    policy_list = self.portal.caching_policy_manager.listPolicies()
    policy = [policy[1] for policy in policy_list\
                if policy[0] == 'unauthenticated no language'][0]
    for i in range(3):
      path = '/'.join((website_url,
                       reference,
                       'img%s.png' % i))
      response = self.publish(path)
      policy_list = self.portal.caching_policy_manager.listPolicies()
      policy = [policy for policy in policy_list\
                                          if policy[0] == 'unauthenticated no language'][0]
      self.assertEqual(response.getHeader('Content-Type'), 'image/png')
      self.assertEqual(
        response.getHeader('Cache-Control'),
        'max-age=%s, stale-while-revalidate=%s, public' % (
          policy[1].getMaxAgeSecs(),
          policy[1].getStaleWhileRevalidateSecs(),
        )
      )

  def test_07_TestDocumentViewBehaviour(self):
    """All Documents shared the same downloading behaviour
    The rules are.
      a document is allways returned in its web_site envrironment
      except if conversion parameters are passed like format, display, ...

    All links to an image must be write with a parameter in its url
    ../REFERENCE.TO.IMAGE?format=png or ../REFERENCE.TO.IMAGE?display=small
    """
    portal = self.getPortal()
    request = portal.REQUEST
    request['PARENTS'] = [self.app]
    website = self.setupWebSite()
    web_section_portal_type = 'Web Section'
    website.newContent(portal_type=web_section_portal_type)

    web_page_reference = 'NXD-WEB-PAGE'
    content = '<p>initial text</p>'
    web_page_module = portal.getDefaultModule(portal_type='Web Page')
    web_page = web_page_module.newContent(portal_type='Web Page',
                                          reference=web_page_reference,
                                          text_content=content)
    web_page.publish()

    document_reference = 'NXD-Presentation'
    document_module = portal.getDefaultModule(portal_type='Presentation')
    upload_file = makeFileUpload('P-DMS-Presentation.3.Pages-001-en.odp')
    document = document_module.newContent(portal_type='Presentation',
                                          reference=document_reference,
                                          file=upload_file)
    document.publish()

    image_reference = 'NXD-IMAGE'
    image_module = portal.getDefaultModule(portal_type='Image')
    upload_file = makeFileUpload('tiolive-ERP5.Freedom.TioLive.Logo-001-en.png')
    image = image_module.newContent(portal_type='Image',
                                    file=upload_file,
                                    reference=image_reference)
    image.publish()
    self.tic()
    credential = 'ERP5TypeTestCase:'
    # testing TextDocument
    response = self.publish(website.absolute_url_path() + '/' +\
                            web_page_reference, credential)
    self.assertEqual(response.getHeader('content-type'),
                                         'text/html; charset=utf-8')
    self.assertIn('<form', response.getBody()) # means the web_page
                                      # is rendered in web_site context

    response = self.publish(website.absolute_url_path() + '/' +\
                            web_page_reference, credential)
    self.assertEqual(response.getHeader('content-type'),
                                         'text/html; charset=utf-8')
    self.assertIn('<form', response.getBody()) # means the web_page
                                      # is rendered in web_site context

    response = self.publish(website.absolute_url_path() + '/' +\
                            web_page_reference + '?format=pdf', credential)
    self.assertEqual(response.getHeader('content-type'), 'application/pdf')

    # testing Image
    response = self.publish(website.absolute_url_path() + '/' +\
                            image_reference, credential)
    # image is rendered in web_site context
    self.assertEqual(response.getHeader('content-type'),
                                         'text/html; charset=utf-8')

    response = self.publish(website.absolute_url_path() + '/' +\
                            image_reference + '?format=png', credential)
    # image is downloaded because format parameter is passed
    self.assertEqual(response.getHeader('content-type'), 'image/png')

    response = self.publish(website.absolute_url_path() + '/' +\
                            image_reference + '?display=small', credential)
    # image is downloaded because display parameter is passed
    self.assertEqual(response.getHeader('content-type'), 'image/png')

    # image is rendered in web_site context
    response = self.publish(website.absolute_url_path() + '/' +\
                            image_reference, credential)
    self.assertEqual(response.getHeader('content-type'),
                                         'text/html; charset=utf-8')

    # testing OOoDocument
    # Document is downloaded
    response = self.publish(website.absolute_url_path() + '/' +\
                            document_reference, credential)
    self.assertEqual(response.getHeader('content-type'),
                                         'text/html; charset=utf-8')
    response = self.publish(website.absolute_url_path() + '/' +\
                            document_reference + '?format=odp', credential)
    # document is resturned because format parameter is passed
    self.assertEqual(response.getHeader('content-type'),
                      'application/vnd.oasis.opendocument.presentation')
    # Document is rendered in web_site context
    response = self.publish(website.absolute_url_path() + '/' +\
                            document_reference, credential)
    self.assertEqual(response.getHeader('content-type'),
                                         'text/html; charset=utf-8')

  def test_08_RFC5861(self):
    """
    Checks that RFC5861 is well implemented
    """
    website = self.setupWebSite()
    website_url = website.absolute_url_path()
    response = self.publish(website_url)
    self.assertTrue(response.getHeader('x-cache-headers-set-by'),
                    'CachingPolicyManager: /erp5/caching_policy_manager')
    web_section_portal_type = 'Web Section'
    web_section = website.newContent(portal_type=web_section_portal_type)
    response = self.publish(web_section.absolute_url_path())
    self.assertTrue(response.getHeader('x-cache-headers-set-by'),
                    'CachingPolicyManager: /erp5/caching_policy_manager')

    # unauthenticated
    document_portal_type = 'Text'
    document_module = self.portal.getDefaultModule(document_portal_type)
    document = document_module.newContent(portal_type=document_portal_type,
                                          reference='NXD-Document-1-TEXT.Cache')
    document.publish()
    # Evaluation of last modification date for the site is cached
    self.portal.portal_caches.clearCache(cache_factory_list=('erp5_content_short', ))
    self.tic()
    response = self.publish(website_url + '/NXD-Document-1-TEXT.Cache')
    last_modified_header = response.getHeader('Last-Modified')
    self.assertTrue(last_modified_header)
    from App.Common import rfc1123_date
    # Convert the Date into string according RFC 1123 Time Format
    modification_date = rfc1123_date(document.getModificationDate())
    self.assertEqual(modification_date, last_modified_header)

    # Upload a presentation with 3 pages.
    upload_file = makeFileUpload('P-DMS-Presentation.3.Pages-001-en.odp')
    document = document_module.newContent(portal_type='Presentation',
                                          file=upload_file)
    reference = 'P-DMS-Presentation-001-.3.Pages'
    document.edit(reference=reference)
    document.publish()
    self.portal.portal_caches.clearCache(cache_factory_list=('erp5_content_short', ))
    self.tic()
    # Check we can access to the 3 drawings converted into images.
    # Those images can be accessible through extensible content
    # url : path-of-document + '/' + 'img' + page-index + '.png'
    # Update policy to have stale values
    policy_orig = self.portal.caching_policy_manager._policies['unauthenticated no language']
    try:
      self.portal.caching_policy_manager._updatePolicy(
        "unauthenticated no language", "python: member is None",
        "python: getattr(object, 'getModificationDate', object.modified)()",
        1200, 30, 600, 0, 0, 0, "Accept-Language, Cookie", "", None,
        0, 1, 0, 0, 1, 1, None, None)
      self.tic()
      policy_list = self.portal.caching_policy_manager.listPolicies()
      policy = [policy[1] for policy in policy_list\
                  if policy[0] == 'unauthenticated no language'][0]
      # Check policy has been updated
      self.assertEqual(policy.getMaxAgeSecs(), 1200)
      self.assertEqual(policy.getStaleWhileRevalidateSecs(), 30)
      self.assertEqual(policy.getStaleIfErrorSecs(), 600)
      for i in range(3):
        path = '/'.join((website_url,
                         reference,
                         'img%s.png' % i))
        response = self.publish(path)
        self.assertEqual(response.getHeader('Content-Type'), 'image/png')
        self.assertEqual(response.getHeader('Cache-Control'),
              'max-age=%d, stale-while-revalidate=%d, stale-if-error=%d, public' % \
                            (policy.getMaxAgeSecs(),
                             policy.getStaleWhileRevalidateSecs(),
                             policy.getStaleIfErrorSecs()))
    finally:
      self.portal.caching_policy_manager._policies['unauthenticated no language'] = policy_orig
      transaction.commit()

  def test_PreviewOOoDocumentWithEmbeddedImage(self):
    """Tests html preview of an OOo document with images as extensible content.
    For this test, Presentation_checkConversionFormatPermission does not allow
    access to original format for Unauthenticated users.
    Check that user can still access to other format.
    """
    portal = self.portal
    script_id = 'Presentation_checkConversionFormatPermission'
    python_code = """from AccessControl import getSecurityManager
user = getSecurityManager().getUser()
if (not user or not user.getId()) and not format:
  return False
return True
"""
    createZODBPythonScript(portal.portal_skins.custom, script_id,
                           'format, **kw', python_code)

    request = portal.REQUEST
    request['PARENTS'] = [self.app]
    self.getPortalObject().aq_parent.acl_users._doAddUser(
      'zope_user', '', ['Manager',], [])
    website = self.setupWebSite()
    web_section_portal_type = 'Web Section'
    website.newContent(portal_type=web_section_portal_type)

    document_reference = 'tiolive-ERP5.Freedom.TioLive'
    upload_file = makeFileUpload('tiolive-ERP5.Freedom.TioLive-001-en.odp')
    document = self.portal.document_module.newContent(
                                          portal_type='Presentation',
                                          reference=document_reference,
                                          file=upload_file)
    self.tic()
    credential_list = ['ERP5TypeTestCase:', 'zope_user:']

    for credential in credential_list:
      # first, preview the draft in its physical location (in document module)
      response = self.publish('%s/asEntireHTML' % document.absolute_url_path(),
                              credential)
      self.assertTrue(response.getHeader('content-type').startswith('text/html'))
      html = response.getBody()
      self.assertTrue('<img' in html, html)

      # find the img src
      img_list = etree.HTML(html).findall('.//img')
      self.assertEqual(1, len(img_list))
      src = img_list[0].get('src')

      # and make another query for this img
      response = self.publish('%s/%s' % ( document.absolute_url_path(), src),
                              credential)
      self.assertEqual(response.getHeader('content-type'), 'image/png')
      png = response.getBody()
      self.assertTrue(png.startswith('\x89PNG'))

    # then publish the document and access it anonymously by reference through
    # the web site
    document.publish()

    self.tic()

    response = self.publish('%s/%s/asEntireHTML' % (
              website.absolute_url_path(), document_reference))
    self.assertTrue(response.getHeader('content-type').startswith('text/html'))
    html = response.getBody()
    self.assertTrue('<img' in html, html)

    # find the img src
    img_list = etree.HTML(html).findall('.//img')
    self.assertEqual(1, len(img_list))
    src = img_list[0].get('src')

    # and make another query for this img
    response = self.publish('%s/%s/%s' % (
           website.absolute_url_path(), document_reference, src))
    self.assertEqual(response.getHeader('content-type'), 'image/png')
    png = response.getBody()
    self.assertTrue(png.startswith('\x89PNG'))

    # Now purge cache and let Anonymous user converting the document.
    self.login()
    document.edit() # Reset cache key
    self.tic()
    response = self.publish('%s/%s/asEntireHTML' % (
                            website.absolute_url_path(), document_reference))
    self.assertTrue(response.getHeader('content-type').startswith('text/html'))
    html = response.getBody()
    self.assertTrue('<img' in html, html)

    # find the img src
    img_list = etree.HTML(html).findall('.//img')
    self.assertEqual(1, len(img_list))
    src = img_list[0].get('src')

  def test_ImageConversionThroughWebSite_using_file(self):
    """Check that conversion parameters pass in url
    are hounoured to display an image in context of a website
    """
    self.test_ImageConversionThroughWebSite("File")

  def test_ImageConversionThroughWebSite(self, image_portal_type="Image"):
    """Check that conversion parameters pass in url
    are hounoured to display an image in context of a website
    """
    portal = self.getPortal()
    request = portal.REQUEST
    request['PARENTS'] = [self.app]
    website = self.setupWebSite()
    web_section_portal_type = 'Web Section'
    website.newContent(portal_type=web_section_portal_type)

    web_page_reference = 'NXD-WEB-PAGE'
    content = '<p>initial text</p>'
    web_page_module = portal.getDefaultModule(portal_type='Web Page')
    web_page = web_page_module.newContent(portal_type='Web Page',
                                          reference=web_page_reference,
                                          text_content=content)
    web_page.publish()


    image_reference = 'NXD-IMAGE'
    module = portal.getDefaultModule(portal_type=image_portal_type)
    upload_file = makeFileUpload('tiolive-ERP5.Freedom.TioLive.Logo-001-en.png')
    image = module.newContent(portal_type=image_portal_type,
                                    file=upload_file,
                                    reference=image_reference)
    image.publish()
    self.tic()
    credential = 'ERP5TypeTestCase:'

    # testing Image conversions, raw

    response = self.publish(website.absolute_url_path() + '/' +\
                            image_reference + '?format=', credential)
    self.assertEqual(response.getHeader('content-type'), 'image/png')

    # testing Image conversions, png
    response = self.publish(website.absolute_url_path() + '/' +\
                            image_reference + '?format=png', credential)
    self.assertEqual(response.getHeader('content-type'), 'image/png')

    # testing Image conversions, jpg
    response = self.publish(website.absolute_url_path() + '/' +\
                            image_reference + '?format=jpg', credential)
    self.assertEqual(response.getHeader('content-type'), 'image/jpeg')

    # testing Image conversions, resizing
    response = self.publish(website.absolute_url_path() + '/' +\
                            image_reference + '?display=large', credential)
    self.assertEqual(response.getHeader('content-type'), 'image/png')
    large_image = response.getBody()
    response = self.publish(website.absolute_url_path() + '/' +\
                            image_reference + '?display=small', credential)
    self.assertEqual(response.getHeader('content-type'), 'image/png')
    small_image = response.getBody()
    # if larger image is longer than smaller, then
    # Resizing works
    self.assertTrue(len(large_image) > len(small_image))

  def _test_document_publication_workflow(self, portal_type, transition):
    super(TestERP5WebWithDms, self).login()
    document = self.portal.web_page_module.newContent(portal_type=portal_type)
    self.portal.portal_workflow.doActionFor(document, transition)

  def test_document_publication_workflow_WebPage_publish(self):
    self._test_document_publication_workflow('Web Page', 'publish_action')

  def test_document_publication_workflow_WebPage_publish_alive(self):
    self._test_document_publication_workflow('Web Page',
        'publish_alive_action')

  def test_document_publication_workflow_WebPage_release(self):
    self._test_document_publication_workflow('Web Page', 'release_action')

  def test_document_publication_workflow_WebPage_release_alive(self):
    self._test_document_publication_workflow('Web Page',
        'release_alive_action')

  def test_document_publication_workflow_WebPage_share(self):
    self._test_document_publication_workflow('Web Page', 'share_action')

  def test_document_publication_workflow_WebPage_share_alive(self):
    self._test_document_publication_workflow('Web Page',
        'share_alive_action')

  def _testImageConversionFromSVGToPNG(self, portal_type="Image",
                                       filename="user-TESTSVG-CASE-EMBEDDEDDATA"):
    """ Test Convert one SVG Image (Image, TextDocument, File ...) to
        PNG and compare the generated image is well generated.
    """
    portal = self.portal
    module = portal.getDefaultModule(portal_type=portal_type)
    upload_file = makeFileUpload('%s.svg' % filename)
    image = module.newContent(portal_type=portal_type,
                                    file=upload_file,
                                    reference="NXD-DOCUMENT")
    image.publish()
    self.tic()
    self.assertEqual(image.getContentType(), 'image/svg+xml')
    mime, converted_data = image.convert("png")
    self.assertEqual(mime, 'image/png')
    expected_image = makeFileUpload('%s.png' % filename)

    # Compare images and accept some minimal difference,
    difference_value = compare_image(StringIO(converted_data), expected_image)
    self.assertTrue(difference_value < IMAGE_COMPARE_TOLERANCE,
      "Conversion from svg to png create one too small image, " + \
      "so it failed to download the image. (%s >= %s)" % (difference_value,
                                                          IMAGE_COMPARE_TOLERANCE))

  def _testImageConversionFromSVGToPNG_url(self, image_url, portal_type="Image"):
    """ Test Convert one SVG Image with an image url. ie:
         <image xlink:href="xxx:///../../user-XXX-XXX"
    """
    portal = self.portal
    module = portal.getDefaultModule(portal_type=portal_type)
    upload_file = makeFileUpload('user-TESTSVG-CASE-URL-TEMPLATE.svg')
    svg_content = upload_file.read().replace("REPLACE_THE_URL_HERE", image_url)

    # Add image using data instead file this time as it is not the goal of
    # This test assert this topic.
    image = module.newContent(portal_type=portal_type,
                                    data=svg_content,
                                    filename=upload_file.filename,
                                    content_type="image/svg+xml",
                                    reference="NXD-DOCYMENT")
    image.publish()
    self.tic()
    self.assertEqual(image.getContentType(), 'image/svg+xml')
    mime, converted_data = image.convert("png")
    self.assertEqual(mime, 'image/png')
    expected_image = makeFileUpload('user-TESTSVG-CASE-URL.png')

    # Compare images and accept some minimal difference,
    difference_value = compare_image(StringIO(converted_data), expected_image)
    self.assertTrue(difference_value < IMAGE_COMPARE_TOLERANCE,
      "Conversion from svg to png create one too small image, " + \
      "so it failed to download the image. (%s >= %s)" % (difference_value,
                                                           IMAGE_COMPARE_TOLERANCE))

  def _testImageConversionFromSVGToPNG_file_url(self, portal_type="Image"):
    """ Test Convert one SVG Image with an image using local path (file)
        at the url of the image tag. ie:
         <image xlink:href="file:///../../user-XXX-XXX"

        This is not used by ERP5 in production, but this is way that
        prooves that conversion from SVG to PNG can use external images.
    """
    image_url = "file://" + makeFilePath("user-TESTSVG-BACKGROUND-IMAGE.png")
    self._testImageConversionFromSVGToPNG_url(image_url, portal_type)

  def _testImageConversionFromSVGToPNG_http_url(self, portal_type="Image"):
    """ Test Convert one SVG Image with an image with a full
        url at the url of the image tag. ie:
         <image xlink:href="http://www.erp5.com/user-XXX-XXX"
    """
    portal = self.portal
    module = portal.getDefaultModule(portal_type=portal_type)
    upload_file = makeFileUpload('user-TESTSVG-BACKGROUND-IMAGE.png')
    background_image = module.newContent(portal_type=portal_type,
                                    file=upload_file,
                                    reference="NXD-BACKGROUND")
    background_image.publish()
    self.tic()

    image_url = background_image.absolute_url() + "?format="
    self._testImageConversionFromSVGToPNG_url(image_url, portal_type)

  def _testImageConversionFromSVGToPNG_broken_url(self, portal_type="Image"):
    """ Test Convert one broken SVG into PNG. The expected outcome is a
        conversion error when an SVG contains one unreacheble xlink:href like.
        at the url of the image tag. ie:
         <image xlink:href="http://soidjsoidjqsoijdqsoidjqsdoijsqd.idjsijds/../user-XXX-XXX"

        This is not used by ERP5 in production, but this is way that
        prooves that conversion from SVG to PNG can use external images.
    """
    portal = self.portal
    module = portal.getDefaultModule(portal_type=portal_type)
    upload_file = makeFileUpload('user-TESTSVG-CASE-URL-TEMPLATE.svg')
    svg_content = upload_file.read().replace("REPLACE_THE_URL_HERE",
                           "http://soidjsoidjqsoijdqsoidjqsdoijsqd.idjsijds/../user-XXX-XXX")

    upload_file = makeFileUpload('user-TESTSVG-CASE-URL-TEMPLATE.svg')
    svg2_content = upload_file.read().replace("REPLACE_THE_URL_HERE",
                           "https://www.erp5.com/usXXX-XXX")


    # Add image using data instead file this time as it is not the goal of
    # This test assert this topic.
    image = module.newContent(portal_type=portal_type,
                                    data=svg_content,
                                    filename=upload_file.filename,
                                    content_type="image/svg+xml",
                                    reference="NXD-DOCYMENT")
    # Add image using data instead file this time as it is not the goal of
    # This test assert this topic.
    image2 = module.newContent(portal_type=portal_type,
                                    data=svg2_content,
                                    filename=upload_file.filename,
                                    content_type="image/svg+xml",
                                    reference="NXD-DOCYMENT2")

    image.publish()
    image2.publish()
    self.tic()
    self.assertEqual(image.getContentType(), 'image/svg+xml')
    self.assertEqual(image2.getContentType(), 'image/svg+xml')
    self.assertRaises(ConversionError, image.convert, "png")
    self.assertRaises(ConversionError, image2.convert, "png")

  def _testImageConversionFromSVGToPNG_empty_file(self, portal_type="Image"):
    """ Test Convert one empty SVG into PNG. The expected outcome is ???
    """
    portal = self.portal
    module = portal.getDefaultModule(portal_type=portal_type)


    # Add image using data instead file this time as it is not the goal of
    # This test assert this topic.
    image = module.newContent(portal_type=portal_type,
                                    content_type="image/svg+xml",
                                    reference="NXD-DOCYMENT")

    image.publish()
    self.tic()
    self.assertEqual(image.getContentType(), 'image/svg+xml')
    self.assertRaises(ConversionError, image.convert, "png")

  def test_ImageConversionFromSVGToPNG_embeeded_data(self):
    """ Test Convert one SVG Image with an image with the data
        at the url of the image tag.ie:
         <image xlink:href="data:...." >
    """
    self._testImageConversionFromSVGToPNG("Image")

  def test_FileConversionFromSVGToPNG_embeeded_data(self):
    """ Test Convert one SVG Image with an image with the data
        at the url of the image tag.ie:
         <image xlink:href="data:...." >
    """
    self._testImageConversionFromSVGToPNG("File")

  def test_WebPageConversionFromSVGToPNG_embeeded_data(self):
    """ Test Convert one SVG Image with an image with the data
        at the url of the image tag.ie:
         <image xlink:href="data:...." >
    """
    self._testImageConversionFromSVGToPNG("Web Page")

  def test_ImageConversionFromSVGToPNG_broken_url(self):
    """ Test Convert one SVG Image with an broken image href
    """
    self._testImageConversionFromSVGToPNG_broken_url("Image")

  def test_FileConversionFromSVGToPNG_broken_url(self):
    """ Test Convert one SVG Image with an broken image href
    """
    self._testImageConversionFromSVGToPNG_broken_url("File")

  def test_WebPageConversionFromSVGToPNG_broken_url(self):
    """ Test Convert one SVG Image with an broken image href
    """
    self._testImageConversionFromSVGToPNG_broken_url("Web Page")

  def test_ImageConversionFromSVGToPNG_empty_file(self):
    """ Test Convert one SVG Image with an empty svg
    """
    self._testImageConversionFromSVGToPNG_empty_file("Image")

  def test_FileConversionFromSVGToPNG_empty_file(self):
    """ Test Convert one SVG Image with an empty svg
    """
    self._testImageConversionFromSVGToPNG_empty_file("File")

  def test_ImageConversionFromSVGToPNG_file_url(self):
    """ Test Convert one SVG Image with an image using local path (file)
        at the url of the image tag. ie:
         <image xlink:href="file:///../../user-XXX-XXX"

        This is not used by ERP5 in production, but this is way that
        prooves that conversion from SVG to PNG can use external images.
    """
    self._testImageConversionFromSVGToPNG_file_url("Image")

  def test_FileConversionFromSVGToPNG_file_url(self):
    """ Test Convert one SVG Image with an image using local path (file)
        at the url of the image tag. ie:
         <image xlink:href="file:///../../user-XXX-XXX"

        This is not used by ERP5 in production, but this is way that
        prooves that conversion from SVG to PNG can use external images.
    """
    self._testImageConversionFromSVGToPNG_file_url("File")

  def test_WebPageConversionFromSVGToPNG_file_url(self):
    """ Test Convert one SVG Image with an image using local path (file)
        at the url of the image tag. ie:
         <image xlink:href="file:///../../user-XXX-XXX"

        This is not used by ERP5 in production, but this is way that
        prooves that conversion from SVG to PNG can use external images.
    """
    self._testImageConversionFromSVGToPNG_file_url("Web Page")

  def test_ImageConversionFromSVGToPNG_http_url(self):
    """ Test Convert one SVG Image with an image with a full
        url at the url of the image tag. ie:
         <image xlink:href="http://www.erp5.com/user-XXX-XXX"
    """
    self._testImageConversionFromSVGToPNG_http_url("Image")

  def test_FileConversionFromSVGToPNG_http_url(self):
    """ Test Convert one SVG Image with an image with a full
        url at the url of the image tag. ie:
         <image xlink:href="http://www.erp5.com/user-XXX-XXX"
    """
    self._testImageConversionFromSVGToPNG_http_url("File")

  def test_WebPageConversionFromSVGToPNG_http_url(self):
    """ Test Convert one SVG Image with an image with a full
        url at the url of the image tag. ie:
         <image xlink:href="http://www.erp5.com/user-XXX-XXX"
    """
    self._testImageConversionFromSVGToPNG_http_url("Web Page")

  def test_WebPageAsEmbeddedHtml_simplePage(self):
    """Test convert one simple html page to embedded html file"""
    # Test init part
    web_page_module = self.portal.getDefaultModule(portal_type="Web Page")
    html_data = "<p>World</p>"
    page = web_page_module.newContent(portal_type="Web Page")
    page.edit(text_content=html_data)
    # Test part
    ehtml_data = page.WebPage_exportAsSingleFile(format="embedded_html")
    self.assertEqual(ehtml_data, html_data)

  def test_WebPageAsMhtml_simplePage(self):
    """Test convert one simple html page to mhtml file"""
    # Test init part
    web_page_module = self.portal.getDefaultModule(portal_type="Web Page")
    title = "Hello"
    html_data = "<p>World</p>"
    page = web_page_module.newContent(portal_type="Web Page")
    page.edit(title=title, text_content=html_data)
    # Test part
    mhtml_data = page.WebPage_exportAsSingleFile(format="mhtml")
    message = EmailParser().parsestr(mhtml_data)
    self.assertEqual(message.get_params(), [
      ("multipart/related", ""),
      ("type", "text/html"),
      ("boundary", message.get_boundary()),
    ])
    self.assertEqual(message.get("Subject"), title)
    htmlmessage, = message.get_payload()
    self.assertEqual(  # should have only one content transfer encoding header
      len([h for h in htmlmessage.keys() if h == "Content-Transfer-Encoding"]),
      1,
    )
    self.assertEqual(
      htmlmessage.get("Content-Transfer-Encoding"),
      "quoted-printable",
    )
    self.assertEqual(htmlmessage.get("Content-Location"), page.absolute_url())
    self.assertEqual(quopri.decodestring(htmlmessage.get_payload()), html_data)

  def test_WebPageAsEmbeddedHtml_pageWithLink(self):
    """Test convert one html page with links to embedded html file"""
    # Test init part
    web_page_module = self.portal.getDefaultModule(portal_type="Web Page")
    page = web_page_module.newContent(portal_type="Web Page")
    page.edit(text_content="".join([
      "<p>Hello</p>",
      '<a href="//a.a/">aa</a>',
      '<a href="/b">bb</a>',
      '<a href="c">cc</a>',
    ]))
    # Test part
    ehtml_data = page.WebPage_exportAsSingleFile(format="embedded_html")
    self.assertEqual(ehtml_data, "".join([
      "<p>Hello</p>",
      '<a href="%s//a.a/">aa</a>' % self.portal.absolute_url().split("/", 1)[0],
      '<a href="%s/b">bb</a>' % self.portal.absolute_url(),
      '<a href="%s/c">cc</a>' % page.absolute_url(),
    ]))
    ehtml_data = page.WebPage_exportAsSingleFile(format="embedded_html", base_url="https://hel.lo/world/dummy")
    self.assertEqual(ehtml_data, "".join([
      "<p>Hello</p>",
      '<a href="https://a.a/">aa</a>',
      '<a href="https://hel.lo/b">bb</a>',
      '<a href="https://hel.lo/world/c">cc</a>',
    ]))

  def test_WebPageAsMhtml_pageWithLink(self):
    """Test convert one html page with links to mhtml file"""
    # Test init part
    web_page_module = self.portal.getDefaultModule(portal_type="Web Page")
    title = "Hello"
    page = web_page_module.newContent(portal_type="Web Page")
    page.edit(title=title, text_content="".join([
      "<p>Hello</p>",
      '<a href="//a.a/">aa</a>',
      '<a href="/b">bb</a>',
      '<a href="c">cc</a>',
    ]))
    # Test part
    mhtml_data = page.WebPage_exportAsSingleFile(format="mhtml")
    message = EmailParser().parsestr(mhtml_data)
    htmlmessage, = message.get_payload()
    self.assertEqual(  # should have only one content transfer encoding header
      len([h for h in htmlmessage.keys() if h == "Content-Transfer-Encoding"]),
      1,
    )
    self.assertEqual(
      htmlmessage.get("Content-Transfer-Encoding"),
      "quoted-printable",
    )
    self.assertEqual(htmlmessage.get("Content-Location"), page.absolute_url())
    self.assertEqual(quopri.decodestring(htmlmessage.get_payload()), "".join([
      "<p>Hello</p>",
      '<a href="%s//a.a/">aa</a>' % self.portal.absolute_url().split("/", 1)[0],
      '<a href="%s/b">bb</a>' % self.portal.absolute_url(),
      '<a href="%s/c">cc</a>' % page.absolute_url(),
    ]))
    mhtml_data = page.WebPage_exportAsSingleFile(format="mhtml", base_url="https://hel.lo/world/dummy")
    message = EmailParser().parsestr(mhtml_data)
    htmlmessage, = message.get_payload()
    self.assertEqual(htmlmessage.get("Content-Location"), "https://hel.lo/world")
    self.assertEqual(quopri.decodestring(htmlmessage.get_payload()), "".join([
      "<p>Hello</p>",
      '<a href="https://a.a/">aa</a>',
      '<a href="https://hel.lo/b">bb</a>',
      '<a href="https://hel.lo/world/c">cc</a>',
    ]))

  def test_WebPageAsEmbeddedHtml_pageWithScript(self):
    """Test convert one html page with script to embedded html file"""
    # Test init part
    web_page_module = self.portal.getDefaultModule(portal_type="Web Page")
    html_data = "<script>alert('Hello');</script><p>World</p>"
    page = web_page_module.newContent(portal_type="Web Page")
    page.edit(text_content=html_data)
    # Test part
    ehtml_data = page.WebPage_exportAsSingleFile(format="embedded_html")
    self.assertEqual(ehtml_data, "<p>World</p>")

  def test_WebPageAsMhtml_pageWithScript(self):
    """Test convert one html page with script to mhtml file"""
    # Test init part
    web_page_module = self.portal.getDefaultModule(portal_type="Web Page")
    title = "Hello"
    html_data = "<script>alert('Hello');</script><p>World</p>"
    page = web_page_module.newContent(portal_type="Web Page")
    page.edit(title=title, text_content=html_data)
    # Test part
    mhtml_data = page.WebPage_exportAsSingleFile(format="mhtml")
    message = EmailParser().parsestr(mhtml_data)
    htmlmessage, = message.get_payload()
    self.assertEqual(  # should have only one content transfer encoding header
      len([h for h in htmlmessage.keys() if h == "Content-Transfer-Encoding"]),
      1,
    )
    self.assertEqual(
      htmlmessage.get("Content-Transfer-Encoding"),
      "quoted-printable",
    )
    self.assertEqual(htmlmessage.get("Content-Location"), page.absolute_url())
    self.assertEqual(quopri.decodestring(htmlmessage.get_payload()), "<p>World</p>")

  def test_WebPageAsEmbeddedHtml_pageWithMoreThanOneImage(self):
    """Test convert one html page with images to embedded html file"""
    # Test init part
    web_page_module = self.portal.getDefaultModule(portal_type="Web Page")
    image_module = self.portal.getDefaultModule(portal_type="Image")
    svg = image_module.newContent(portal_type="Image")
    svg.edit(content_type="image/svg+xml", data=XSMALL_SVG_IMAGE_ICON_DATA)
    svg.publish()
    png = image_module.newContent(portal_type="Image")
    png.edit(content_type="image/png", data=XSMALL_PNG_IMAGE_ICON_DATA)
    png.publish()
    page = web_page_module.newContent(portal_type="Web Page")
    page.edit(text_content="".join([
      "<p>Hello</p>",
      '<img src="/%s?format=" />' % svg.getRelativeUrl(),
      '<img src="/%s?format=" />' % png.getRelativeUrl(),
      '<img src="/%s?format=png" />' % svg.getRelativeUrl(),
    ]))
    # Test part
    ehtml_data = page.WebPage_exportAsSingleFile(format="embedded_html")
    self.assertTrue(ehtml_data.startswith("".join([
      "<p>Hello</p>",
      '<img src="data:image/svg+xml;base64,%s" />' % b64encode(XSMALL_SVG_IMAGE_ICON_DATA),
      '<img src="data:image/png;base64,%s" />' % b64encode(XSMALL_PNG_IMAGE_ICON_DATA),
      '<img src="data:image/png;base64,'
    ])))

  def test_WebPageAsMhtml_pageWithMoreThanOneImage(self):
    """Test convert one html page with images to mhtml file"""
    # Test init part
    web_page_module = self.portal.getDefaultModule(portal_type="Web Page")
    image_module = self.portal.getDefaultModule(portal_type="Image")
    svg = image_module.newContent(portal_type="Image")
    svg.edit(content_type="image/svg+xml", data=XSMALL_SVG_IMAGE_ICON_DATA)
    svg.publish()
    png = image_module.newContent(portal_type="Image")
    png.edit(content_type="image/png", data=XSMALL_PNG_IMAGE_ICON_DATA)
    png.publish()
    page = web_page_module.newContent(portal_type="Web Page")
    page.edit(text_content="".join([
      "<p>Hello</p>",
      '<img src="/%s?format=" />' % svg.getRelativeUrl(),
      '<img src="/%s?format=" />' % png.getRelativeUrl(),
      '<img src="/%s?format=png" />' % svg.getRelativeUrl(),
    ]))
    # Test part
    mhtml_data = page.WebPage_exportAsSingleFile(format="mhtml")
    message = EmailParser().parsestr(mhtml_data)
    htmlmessage, svgmessage, pngmessage, svgtopngmessage = message.get_payload()
    self.assertEqual(
      quopri.decodestring(htmlmessage.get_payload()),
      "".join([
        "<p>Hello</p>",
        '<img src="%s?format=" />' % svg.absolute_url(),
        '<img src="%s?format=" />' % png.absolute_url(),
        '<img src="%s?format=png" />' % svg.absolute_url(),
      ]),
    )
    for content_type, ext, message, obj, data in [
          ("image/svg+xml", "", svgmessage, svg, XSMALL_SVG_IMAGE_ICON_DATA),
          ("image/png", "", pngmessage, png, XSMALL_PNG_IMAGE_ICON_DATA),
          ("image/png", "png", svgtopngmessage, svg, None),
        ]:
      __traceback_info__ = (content_type, "?format=" + ext)
      self.assertEqual(
        message.get("Content-Location"),
        obj.absolute_url() + "?format=" + ext,
      )
      self.assertEqual(  # should have only one content transfer encoding header
        len([h for h in message.keys() if h == "Content-Transfer-Encoding"]),
        1,
      )
      self.assertEqual(message.get("Content-Type"), content_type)
      encoding = message.get("Content-Transfer-Encoding")
      self.assertIn(encoding, ("base64", "quoted-printable"))
      # quoted printable encoding is accepted for svg images
      if data:
        if encoding == "base64":
          self.assertEqual(
            b64decode(message.get_payload()),
            data,
          )
        elif encoding == "quoted-printable":
          self.assertEqual(
            quopri.decodestring(message.get_payload()),
            data,
          )
        else:
          raise ValueError("unhandled encoding %r" % encoding)
      else:
        self.assertTrue(len(message.get_payload()) > 0)

  @customScript("ERP5Site_getWebSiteDomainDict", "", 'return {"test.portal.erp": context.getPortalObject()}')
  def test_WebPageAsEmbeddedHtml_pageWithDifferentHref(self):
    """Test convert one html page with images to embedded html file"""
    # Test init part
    # XXX use web site domain properties instead of @customScript
    web_page_module = self.portal.getDefaultModule(portal_type="Web Page")
    image_module = self.portal.getDefaultModule(portal_type="Image")
    svg = image_module.newContent(portal_type="Image")
    svg.edit(content_type="image/svg+xml", data=XSMALL_SVG_IMAGE_ICON_DATA)
    svg.publish()
    page = web_page_module.newContent(portal_type="Web Page")
    page.edit(text_content="".join([
      "<p>Hello</p>",
      '<img src="%s?format=" />' % svg.getRelativeUrl(),
      '<img src="%s?display=" />' % svg.getRelativeUrl(),
      '<img src="/%s?format=" />' % svg.getRelativeUrl(),
      '<img src="//test.portal.erp/%s?format=" />' % svg.getRelativeUrl(),
      '<img src="http://test.portal.erp/%s?format=" />' % svg.getRelativeUrl(),
      '<img src="https://test.portal.erp/%s?format=" />' % svg.getRelativeUrl(),
      '<img src="//example.com/%s?format=" />' % svg.getRelativeUrl(),
      '<img src="http://example.com/%s?format=" />' % svg.getRelativeUrl(),
      '<img src="https://example.com/%s?format=" />' % svg.getRelativeUrl(),
      '<img src="data:image/svg+xml,&lt;svg&gt;&lt;/svg&gt;" />',
      '<img src="tel:1234567890" />',
      '<img src="mailto:me" />',
    ]))
    protocol = page.absolute_url().split(":", 1)[0] + ":"
    # Test part
    ehtml_data = page.WebPage_exportAsSingleFile(format="embedded_html")
    self.assertEqual(ehtml_data, "".join([
      "<p>Hello</p>",
    ] + ([
      '<img src="data:image/svg+xml;base64,%s" />' % b64encode(XSMALL_SVG_IMAGE_ICON_DATA),
    ] * 6) + [
      '<img src="%s//example.com/%s?format=" />' % (protocol, svg.getRelativeUrl()),
      '<img src="http://example.com/%s?format=" />' % svg.getRelativeUrl(),
      '<img src="https://example.com/%s?format=" />' % svg.getRelativeUrl(),
      '<img src="data:image/svg+xml,&lt;svg&gt;&lt;/svg&gt;" />',
      '<img src="tel:1234567890" />',
      '<img src="mailto:me" />',
    ]))

  @customScript("ERP5Site_getWebSiteDomainDict", "", 'return {"test.portal.erp": context.getPortalObject()}')
  def test_WebPageAsMhtml_pageWithDifferentHref(self):
    """Test convert one html page with images to mhtml file"""
    # Test init part
    # XXX use web site domain properties instead of @customScript
    web_page_module = self.portal.getDefaultModule(portal_type="Web Page")
    image_module = self.portal.getDefaultModule(portal_type="Image")
    svg = image_module.newContent(portal_type="Image")
    svg.edit(content_type="image/svg+xml", data=XSMALL_SVG_IMAGE_ICON_DATA)
    svg.publish()
    page = web_page_module.newContent(portal_type="Web Page")
    page.edit(text_content="".join([
      "<p>Hello</p>",
      '<img src="%s?format=" />' % svg.getRelativeUrl(),
      '<img src="%s?display=" />' % svg.getRelativeUrl(),
      '<img src="/%s?format=" />' % svg.getRelativeUrl(),
      '<img src="//test.portal.erp/%s?format=" />' % svg.getRelativeUrl(),
      '<img src="http://test.portal.erp/%s?format=" />' % svg.getRelativeUrl(),
      '<img src="https://test.portal.erp/%s?format=" />' % svg.getRelativeUrl(),
      '<img src="//example.com/%s?format=" />' % svg.getRelativeUrl(),
      '<img src="http://example.com/%s?format=" />' % svg.getRelativeUrl(),
      '<img src="https://example.com/%s?format=" />' % svg.getRelativeUrl(),
      '<img src="data:image/svg+xml,&lt;svg&gt;&lt;/svg&gt;" />',
      '<img src="tel:1234567890" />',
      '<img src="mailto:me" />',
    ]))
    protocol = page.absolute_url().split(":", 1)[0] + ":"
    # Test part
    mhtml_data = page.WebPage_exportAsSingleFile(format="mhtml")
    message = EmailParser().parsestr(mhtml_data)
    self.assertEqual(len(message.get_payload()), 7)
    htmlmessage = message.get_payload()[0]
    self.assertEqual(
      quopri.decodestring(htmlmessage.get_payload()),
      "".join([
        "<p>Hello</p>",
        '<img src="%s/%s?format=" />' % (page.absolute_url(), svg.getRelativeUrl()),
        '<img src="%s/%s?display=" />' % (page.absolute_url(), svg.getRelativeUrl()),
        '<img src="%s?format=" />' % svg.absolute_url(),
        '<img src="%s//test.portal.erp/%s?format=" />' % (protocol, svg.getRelativeUrl()),
        '<img src="http://test.portal.erp/%s?format=" />' % svg.getRelativeUrl(),
        '<img src="https://test.portal.erp/%s?format=" />' % svg.getRelativeUrl(),
        '<img src="%s//example.com/%s?format=" />' % (protocol, svg.getRelativeUrl()),
        '<img src="http://example.com/%s?format=" />' % svg.getRelativeUrl(),
        '<img src="https://example.com/%s?format=" />' % svg.getRelativeUrl(),
        '<img src="data:image/svg+xml,&lt;svg&gt;&lt;/svg&gt;" />',
        '<img src="tel:1234567890" />',
        '<img src="mailto:me" />',
      ]),
    )
    for message, location in [
          (message.get_payload()[1], "%s/%s?format=" % (page.absolute_url(), svg.getRelativeUrl())),
          (message.get_payload()[2], "%s/%s?display=" % (page.absolute_url(), svg.getRelativeUrl())),
          (message.get_payload()[3], "%s?format=" % svg.absolute_url()),
          (message.get_payload()[4], "%s//test.portal.erp/%s?format=" % (protocol, svg.getRelativeUrl())),
          (message.get_payload()[5], "http://test.portal.erp/%s?format=" % svg.getRelativeUrl()),
          (message.get_payload()[6], "https://test.portal.erp/%s?format=" % svg.getRelativeUrl()),
        ]:
      self.assertEqual(
        message.get("Content-Location"),
        location,
      )
      self.assertEqual(  # should have only one content transfer encoding header
        len([h for h in message.keys() if h == "Content-Transfer-Encoding"]),
        1,
      )
      encoding = message.get("Content-Transfer-Encoding")
      self.assertIn(encoding, ("base64", "quoted-printable"))
      # quoted printable encoding is accepted for svg images
      if encoding == "base64":
        self.assertEqual(
          b64decode(message.get_payload()),
          XSMALL_SVG_IMAGE_ICON_DATA,
        )
      elif encoding == "quoted-printable":
        self.assertEqual(
          quopri.decodestring(message.get_payload()),
          XSMALL_SVG_IMAGE_ICON_DATA,
        )
      else:
        raise ValueError("unhandled encoding %r" % encoding)

  def test_WebPageAsEmbeddedHtml_pageWith1000Image(self):
    """Test convert one html page with 1000 images to embedded html file"""
    # Test init part
    web_page_module = self.portal.getDefaultModule(portal_type="Web Page")
    image_module = self.portal.getDefaultModule(portal_type="Image")
    page = web_page_module.newContent(portal_type="Web Page")
    text_content_list = ["<p>Hello</p>"]
    for _ in range(0, 1000, 5):
      svg = image_module.newContent(portal_type="Image")
      svg.edit(content_type="image/svg+xml", data=XSMALL_SVG_IMAGE_ICON_DATA)
      svg.publish()
      png = image_module.newContent(portal_type="Image")
      png.edit(content_type="image/png", data=XSMALL_PNG_IMAGE_ICON_DATA)
      png.publish()
      text_content_list += [
        '<img src="/%s?format=" />' % svg.getRelativeUrl(),
        '<img src="/%s?format=" />' % png.getRelativeUrl(),
        '<img src="/%s?format=png" />' % svg.getRelativeUrl(),
        '<img src="/%s?format=jpg" />' % png.getRelativeUrl(),
        '<img src="/%s?format=jpg" />' % svg.getRelativeUrl(),
      ]
    page.edit(text_content="".join(text_content_list))
    # Test part
    ehtml_data = page.WebPage_exportAsSingleFile(format="embedded_html")
    self.assertEqual(ehtml_data.count("<img"), 1000)

  def test_WebPageAsMhtml_pageWith1000Image(self):
    """Test convert one html page with 1000 images to mhtml file"""
    # Test init part
    web_page_module = self.portal.getDefaultModule(portal_type="Web Page")
    image_module = self.portal.getDefaultModule(portal_type="Image")
    page = web_page_module.newContent(portal_type="Web Page")
    text_content_list = ["<p>Hello</p>"]
    for _ in range(0, 1000, 5):
      svg = image_module.newContent(portal_type="Image")
      svg.edit(content_type="image/svg+xml", data=XSMALL_SVG_IMAGE_ICON_DATA)
      svg.publish()
      png = image_module.newContent(portal_type="Image")
      png.edit(content_type="image/png", data=XSMALL_PNG_IMAGE_ICON_DATA)
      png.publish()
      text_content_list += [
        '<img src="/%s?format=" />' % svg.getRelativeUrl(),
        '<img src="/%s?format=" />' % png.getRelativeUrl(),
        '<img src="/%s?format=png" />' % svg.getRelativeUrl(),
        '<img src="/%s?format=jpg" />' % png.getRelativeUrl(),
        '<img src="/%s?format=jpg" />' % svg.getRelativeUrl(),
      ]
    page.edit(text_content="".join(text_content_list))
    # Test part
    mhtml_data = page.WebPage_exportAsSingleFile(format="mhtml")
    message = EmailParser().parsestr(mhtml_data)
    self.assertEqual(len(message.get_payload()), 1001)

  def test_WebPageAsEmbeddedHtml_pageWithStyle(self):
    """Test convert one html page with style tag to embedded html file"""
    # Test init part
    web_page_module = self.portal.getDefaultModule(portal_type="Web Page")
    image_module = self.portal.getDefaultModule(portal_type="Image")
    img = image_module.newContent(portal_type="Image")
    img.edit(content_type="image/svg+xml", data=XSMALL_SVG_IMAGE_ICON_DATA)
    img.publish()
    page = web_page_module.newContent(portal_type="Web Page")
    page.edit(
      text_content="<style>%s</style><p>Hello</p>" % (
        'body { background-image: url(  "/%s?format=" ); }' % (
          img.getRelativeUrl())),
    )
    # Test part
    ehtml_data = page.WebPage_exportAsSingleFile(format="embedded_html")
    self.assertEqual(
      ehtml_data,
      "<style>%s</style><p>Hello</p>" % (
        'body { background-image: url(data:image/svg+xml;base64,%s); }' % (
          b64encode(XSMALL_SVG_IMAGE_ICON_DATA))),
    )

  def test_WebPageAsMhtml_pageWithStyle(self):
    """Test convert one html page with style tag to mhtml file"""
    # Test init part
    web_page_module = self.portal.getDefaultModule(portal_type="Web Page")
    image_module = self.portal.getDefaultModule(portal_type="Image")
    img = image_module.newContent(portal_type="Image")
    img.edit(content_type="image/svg+xml", data=XSMALL_SVG_IMAGE_ICON_DATA)
    img.publish()
    page = web_page_module.newContent(portal_type="Web Page")
    page.edit(
      text_content="<style>%s</style><p>Hello</p>" % (
        'body { background-image: url(  "/%s?format=" ); }' % (
          img.getRelativeUrl())),
    )
    # Test part
    mhtml_data = page.WebPage_exportAsSingleFile(format="mhtml")
    message = EmailParser().parsestr(mhtml_data)
    htmlmessage, imagemessage = message.get_payload()
    self.assertEqual(
      quopri.decodestring(htmlmessage.get_payload()),
      "<style>%s</style><p>Hello</p>" % (
        "body { background-image: url(%s?format=); }" % (
          img.absolute_url())),
    )
    self.assertEqual(
      imagemessage.get("Content-Location"),
      img.absolute_url() + "?format=",
    )
    self.assertEqual(  # should have only one content transfer encoding header
      len([h for h in imagemessage.keys() if h == "Content-Transfer-Encoding"]),
      1,
    )
    encoding = imagemessage.get("Content-Transfer-Encoding")
    self.assertIn(encoding, ("base64", "quoted-printable"))
    # quoted printable encoding is accepted for svg images
    if encoding == "base64":
      self.assertEqual(
        b64decode(imagemessage.get_payload()),
        XSMALL_SVG_IMAGE_ICON_DATA,
      )
    elif encoding == "quoted-printable":
      self.assertEqual(
        quopri.decodestring(imagemessage.get_payload()),
        XSMALL_SVG_IMAGE_ICON_DATA,
      )
    else:
      raise ValueError("unhandled encoding %r" % encoding)

  @customScript("ERP5Site_getWebSiteDomainDict", "", """return {
    "test.portal.erp": context.getPortalObject(),
    "test.site.erp": context.getPortalObject().web_site_module.test,
  }""")
  def test_WebPageImplicitSuccessorValueList(self):
    # Test init part
    # XXX use web site domain properties instead of @customScript
    self.setupWebSite()
    web_page_module = self.portal.getDefaultModule(portal_type="Web Page")
    image_module = self.portal.getDefaultModule(portal_type="Image")
    img_list = []
    for i in range(14):
      img = image_module.newContent(
        data=XSMALL_SVG_IMAGE_ICON_DATA,
        reference="P-IMG-implicit.successor.value.list.test.%d" % i,
        version="001",
        language="en",
      )
      img.publish()
      img_list.append(img)
    page = web_page_module.newContent(
      portal_type="Web Page",
      reference="P-WP-implicit.successor.value.list.test",
      version="001",
      language="en",
      text_content="".join([
        "<p>Hello</p>",
        '<a href="%s" />' % img_list[0].getRelativeUrl(),
        '<a href="%s" />' % img_list[0].getRelativeUrl(),
        '<a href="./%s" />' % img_list[1].getRelativeUrl(),
        '<a href="/%s" />' % img_list[2].getRelativeUrl(),
        '<a href="%s/view" />' % img_list[3].getRelativeUrl(),
        '<a href="P-IMG-implicit.successor.value.list.test.4" />',
        '<a href="./P-IMG-implicit.successor.value.list.test.5" />',
        '<a href="./P-IMG-implicit.successor.value.list.test.6/view" />',
        '<a href="/P-IMG-implicit.successor.value.list.test.7/view" />',
        '<a href="//test.site.erp/P-IMG-implicit.successor.value.list.test.8/view" />',
        '<a href="http://test.site.erp/P-IMG-implicit.successor.value.list.test.9/view" />',
        '<img src="P-IMG-implicit.successor.value.list.test.10?format=" />',
        '<iframe src="/%s" />' % img_list[11].getRelativeUrl(),
        '<style>body { background-image: url("P-IMG-implicit.successor.value.list.test.12?format=png"); }</style>',
        '<script src="P-IMG-implicit.successor.value.list.test.13" type="text/javascript"></script>',
      ]),
    )
    page.publish()
    self.tic()

    # Test part
    self.maxDiff = None
    successor_list = self.portal.web_site_module.test\
      .restrictedTraverse("P-WP-implicit.successor.value.list.test")\
      .getImplicitSuccessorValueList()
    self.assertEqual(
      sorted([s.getReference() for s in successor_list]),
      sorted([i.getReference() for i in img_list]),
    )

    # same with the web page retrieved with getDocumentValue
    successor_list = self.portal.web_site_module.test.getDocumentValue(
        "P-WP-implicit.successor.value.list.test"
    ).getImplicitSuccessorValueList()
    self.assertEqual(
      sorted([s.getReference() for s in successor_list]),
      sorted([i.getReference() for i in img_list]),
    )

  def checkWebSiteDocumentViewConsistency(self, portal_type, module_id="document_module"):
    """
      Checks that the default view action of a <portal_type>, viewing from a web site,
      is `web_view`.
      (e.g. output of .../document_module/1/ differs if `web_view` visible or not)
    """
    portal = self.portal
    web_site = self.setupWebSite()

    # extract script id from `web_view` action
    # Use `contentValues` because `searchFolder` does not find any web_view action.
    for action in portal.portal_types[portal_type].contentValues(portal_type="Action Information"):
      if action.getReference() == "web_view":
        break
    else:
      raise LookupError("No action with reference 'web_view' found")
    assert action.getVisible() is 1

    # check when the file is empty
    document_object = portal[module_id].newContent(portal_type=portal_type)
    document_object.publish()
    self.tic()
    path = '%s/%s/%s/' % (
      web_site.absolute_url_path(),
      module_id,
      document_object.getId())
    response_a = self.publish(path)
    action.setVisible(0)
    self.tic()
    response_b = self.publish(path)
    self.assertNotEqual(response_a.getBody(), response_b.getBody())

  def test_checkWebSiteFileViewConsistency(self):
    """
      Checks that the default view action of a File, viewing from a web site,
      is `web_view`.
    """
    self.checkWebSiteDocumentViewConsistency("File")

  def test_checkWebSiteImageViewConsistency(self):
    """
      Checks that the default view action of a Image, viewing from a web site,
      is `web_view`.
    """
    self.checkWebSiteDocumentViewConsistency("Image", module_id="image_module")

  def test_checkWebSiteTextViewConsistency(self):
    """
      Checks that the default view action of a Text, viewing from a web site,
      is `web_view`.
    """
    self.checkWebSiteDocumentViewConsistency("Text")

  def test_checkWebSitePresentationViewConsistency(self):
    """
      Checks that the default view action of a Presentation, viewing from a web
      site, is `web_view`.
    """
    self.checkWebSiteDocumentViewConsistency("Presentation")

  def test_checkWebSiteSpreadsheetViewConsistency(self):
    """
      Checks that the default view action of a Spreadsheet, viewing from a web
      site, is `web_view`.
    """
    self.checkWebSiteDocumentViewConsistency("Spreadsheet")

  def test_checkWebSiteDrawingViewConsistency(self):
    """
      Checks that the default view action of a Drawing, viewing from a web site,
      is `web_view`.
    """
    self.checkWebSiteDocumentViewConsistency("Drawing")

  def test_cache_control(self):
    # Cache-Control header is set to 'private' by CookieCrumbler for authenticated user.
    # but can be overridden by Caching Policy Manager.
    website = self.setupWebSite()
    released_page = self.portal.web_page_module.newContent(
      portal_type='Web Page',
      reference='released_page',
    )
    released_page.release()
    published_page = self.portal.web_page_module.newContent(
      portal_type='Web Page',
      reference='published_page',
    )
    published_page.publish()
    self.tic()
    auth_cookie = {'__ac': b64encode(b'ERP5TypeTestCase:').decode()}

    # ERP5 portal, not through Caching Policy Manager
    response = requests.get(
      self.portal.absolute_url(),
      cookies=auth_cookie,
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.headers['Cache-Control'], 'private')

    # released page
    response = requests.get(
      '%s/%s' % (website.absolute_url(), 'released_page'),
      cookies=auth_cookie,
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.headers['Cache-Control'], 'max-age=0, no-store')

    # converted released page
    response = requests.get(
      '%s/%s?format=txt' % (website.absolute_url(), 'released_page'),
      cookies=auth_cookie,
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.headers['Cache-Control'], 'max-age=0, no-store')

    # published page
    response = requests.get(
      '%s/%s' % (website.absolute_url(), 'published_page'),
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.headers['Cache-Control'], 'max-age=600, stale-while-revalidate=360000, public')
    response = requests.get(
      '%s/%s' % (website.absolute_url(), 'published_page'),
      cookies=auth_cookie,
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.headers['Cache-Control'], 'max-age=0, no-store')

    # converted published page
    response = requests.get(
      '%s/%s?format=txt' % (website.absolute_url(), 'published_page'),
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.headers['Cache-Control'], 'max-age=600, stale-while-revalidate=360000, public')
    response = requests.get(
      '%s/%s?format=txt' % (website.absolute_url(), 'published_page'),
      cookies=auth_cookie,
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.headers['Cache-Control'], 'max-age=600, stale-while-revalidate=360000, public')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5WebWithDms))
  return suite
