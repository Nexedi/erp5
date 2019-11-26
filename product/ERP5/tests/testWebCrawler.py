# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Nicolas Delaby <nicolas@erp5.org>
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

import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import urlnorm # This library is imported to detect lack of
               # urlnorm availibility in python environment


# test files' home
FILENAME_REGULAR_EXPRESSION = "(?P<reference>[A-Z&é@{]{3,7})-(?P<language>[a-z]{2})-(?P<version>[0-9]{3})"
REFERENCE_REGULAR_EXPRESSION = "(?P<reference>[A-Z&é@{]{3,7})(-(?P<language>[a-z]{2}))?(-(?P<version>[0-9]{3}))?"

class TestWebCrawler(ERP5TypeTestCase):
  """
    Test Crawling mechanism
  """

  _path_to_delete_list = []

  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "ERP5 Live DMS - Web Crawling"

  def getBusinessTemplateList(self):
    """
      Return the list of required business templates.
    """
    return ('erp5_core_proxy_field_legacy',
            'erp5_base',
            'erp5_ingestion',
            'erp5_ingestion_test',
            'erp5_ingestion_mysql_innodb_catalog',
            'erp5_web',
            'erp5_dms')

  def afterSetUp(self):
    """
      Initialize the ERP5 site.
    """
    self.login()
    self.portal = self.getPortal()
    self.setSystemPreference()
    self.bootstrapWebSite()
    self.tic()

  def beforeTearDown(self):
    portal = self.portal
    module_id_list = [
      'web_page_module',
      'web_site_module',
      'external_source_module',
      'document_module',
      ]
    # delete created documents by test
    for module_id in module_id_list:
      module = portal[module_id]
      module.manage_delObjects(list(module.objectIds()))
    # Unindex deleted documents
    self.tic()

  def setSystemPreference(self):
    pref = self.getDefaultSystemPreference()
    pref.setPreferredDocumentFilenameRegularExpression(FILENAME_REGULAR_EXPRESSION)
    pref.setPreferredDocumentReferenceRegularExpression(REFERENCE_REGULAR_EXPRESSION)

  def bootstrapWebSite(self):
    """Create 1 Website
    live_test_web_site/section1/section1a
                      /section2
    create 2 web pages
      W-REFERENCE.PAGE
      W-REFERENCE.HOMEPAGE

    the website use light version of erp5_web_layout
    It keep just displaying sections and subsection
    And default Web page
    """
    web_site_portal_type = 'Web Site'
    web_section_portal_type = 'Web Section'
    web_page_portal_type = 'Web Page'
    web_site_module = self.portal.getDefaultModule(web_site_portal_type)
    web_page_module = self.portal.getDefaultModule(web_page_portal_type)

    text_content = """<p><a href="W-REFERENCE.PAGE">Page</a></p>"""
    web_page_id = 'live_test_home'
    home_page = web_page_module.newContent(portal_type=web_page_portal_type,
                                          title='Home Page',
                                          text_content=text_content,
                                          reference='W-REFERENCE.HOMEPAGE',
                                          version='001',
                                          language='en',
                                          id=web_page_id)
    home_page.submit()
    home_page.publish()

    web_site_id = 'live_test_web_site'
    web_site = web_site_module.newContent(portal_type=web_site_portal_type,
                      id=web_site_id,
                      title='Live Test Web Site',
                      visible=True,
                      default_page_displayed=True,
                      site_map_section_parent=True,
                      authorization_forced=True,
                      aggregate_value=home_page,
                      available_language_set=['en'],
                      container_layout='erp5_web_layout_test',
                      content_layout='erp5_web_content_layout_test')
    web_site.publish()

    text_content = """<p>
    <a href="%s/W-REFERENCE.HOMEPAGE">absolute link to HOME PAGE</a>
    </p>""" % web_site.absolute_url()
    section1a_page = web_page_module.newContent(
                                              portal_type=web_page_portal_type,
                                              title='Home Page',
                                              text_content=text_content,
                                              reference='W-REFERENCE.PAGE',
                                              version='001',
                                              language='en')
    section1a_page.submit()
    section1a_page.publish()
    web_section1 = web_site.newContent(portal_type=web_section_portal_type,
                                      title='Section 1',
                                      id='section1',
                                      aggregate_value=section1a_page)
    web_section2 = web_site.newContent(portal_type=web_section_portal_type,
                                      title='Section 2',
                                      id='section2',
                                      aggregate_value=section1a_page)
    web_section1a = web_section1.newContent(
                                          portal_type=web_section_portal_type,
                                          title='Section 1a',
                                          id='section 1a', #add a space in id
                                          aggregate_value=section1a_page)

  def test_01_check_URLTransformations(self):
    """Check crawlable functionalities regarding URL handling

    getContentBaseURL
    asNormalisedURL
    getContentNormalisedURLList
    """
    web_page_portal_type = 'Web Page'
    web_page_module = self.portal.getDefaultModule(web_page_portal_type)
    web_page = web_page_module.newContent(portal_type=web_page_portal_type)
    self.assertEqual(web_page.getContentBaseURL(), '')
    web_page.fromURL('http://www.example.com')
    self.assertEqual(web_page.getContentBaseURL(), 'http://www.example.com')
    web_page.fromURL('http://www.example.com/section/sub_section')
    self.assertEqual(web_page.getContentBaseURL(),
                      'http://www.example.com/section')
    text_content = """<html>
    <head>
      <base href="http://www.example.com"/>
    </head>
    <body>
      <p><a href="http://www.notexample.com/">External link</a></p>
      <p><a href="http://www.example.com//I don't care I put what/ I want/">
          Funny link</a></p>
      <p><a href="http://www.example.com/section">Internal link</a></p>
      <p><a href="section2">Relative Internal link</a></p>
      <p><a href="http://www.example.com/?title=%E9crit">With Encoding issue
      This link will be discarded</a></p>
      <img src="my_image_link"/>
      <script src="should_not_be_followed.js"/>
      <p><a href="http://http://www.example.com/section">Not a link</a></p>
    </body>
    </html>"""
    web_page.edit(text_content=text_content)
    self.assertEqual(web_page.getContentBaseURL(), "http://www.example.com")
    self.assertEqual(web_page.getContentNormalisedURLList(),
                    ["http://www.example.com/I don't care I put what/ I want/",
                     'http://www.example.com/section',
                     'http://www.example.com/section2',
                     'http://www.example.com/?title=\xc3\xa9crit',])
    # relative links without base tag
    text_content = """<html>
    <head>
    </head>
    <body>
      <p><a href="section2">Relative Internal link</a></p>
    </body>
    </html>"""
    web_page.edit(text_content=text_content)
    web_page.fromURL('http://www.example.com/#fffff')
    self.assertEqual(web_page.getContentBaseURL(), "http://www.example.com")
    self.assertEqual(web_page.getContentNormalisedURLList(),
                      ['http://www.example.com/section2',])
    self.assertEqual(web_page.asNormalisedURL(),
                      'http://www.example.com/#fffff')

  def test_02_crawlWebSite(self):
    """Call portal_contribution to crawl website hosted by itself.
    """
    web_site = self.portal.web_site_module.live_test_web_site
    external_source_portal_type = 'URL Crawler'
    web_crawler_module = self.portal.getDefaultModule(
                                                   external_source_portal_type)
    web_crawler = web_crawler_module.newContent(
                                       portal_type=external_source_portal_type,
                                       crawling_depth=5)
    web_crawler.fromURL(web_site.absolute_url())
    self.tic()
    web_crawler.crawlContent()
    self.tic()

    # 6 = 1 website
    #     + 3 Web Sections
    #     + 1 absolute link to home_page
    #     + 1 relative link from home_page to another web page
    self.assertEqual(len(web_crawler), 6)
    self.assertEqual(len(self.portal.portal_url_registry._getMappingDict()),
                      6)
    date_before = web_crawler.getModificationDate()
    web_crawler.crawlContent()
    self.tic()
    # Nothing happens, portal_url_registry keep crawling twice
    # the same url
    self.assertEqual(len(web_crawler), 6)
    self.assertEqual(len(self.portal.portal_url_registry._getMappingDict()),
                      6)
    # not modified
    self.assertEqual(date_before, web_crawler.getModificationDate())

    new_web_crawler = web_crawler_module.newContent(
                                       portal_type=external_source_portal_type,
                                       crawling_depth=5)
    new_web_crawler.fromURL(web_site.absolute_url())
    self.tic()
    new_web_crawler.crawlContent()
    self.tic()
    # check that portal_url_registry
    # block contribution of existing content
    self.assertFalse(len(new_web_crawler))

    # set another namespace on preference
    self.getDefaultSystemPreference().setPreferredIngestionNamespace('NEW')
    self.tic()
    new_web_crawler.crawlContent()
    self.tic()
    self.assertEqual(len(web_crawler), 6)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestWebCrawler))
  return suite
