##############################################################################
#
# Copyright (c) 2002-2018 Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

import six.moves.urllib.parse
import six.moves.http_client
import unittest
import ssl

LOCATION = "Location"
WEB_SITE_ID = "bouncer"

class TestStaticWebSiteRedirection(ERP5TypeTestCase):

  def getTitle(self):
    return "Test Static Web Site Redirection."

  def getBusinessTemplateList(self):
    return (
      "erp5_base",
      "erp5_web",
      "erp5_ui_test_core"
    )

  def afterSetup(self):
    """
    This is ran before anything, used to set the environment
    """
    self.portal = self.getPortalObject()

  def setupWebSite(self, use_moved_temporarily=None, **kw):
    """
    Setup Web Site
    """

    if WEB_SITE_ID in self.portal.web_site_module.objectIds():
      self.portal.web_site_module.manage_delObjects(WEB_SITE_ID)

    website = self.portal.web_site_module.newContent(
      portal_type="Static Web Site",
      id=WEB_SITE_ID,
      redirect_domain="https://www.example.org",
      use_moved_temporarily=use_moved_temporarily or 0,
      **kw
    )
    website.publish()

    self.tic()
    return website

  def runTestRedirect(self, source_path, expected_failure=None,
                      use_moved_temporarily=None,
                      configuration_service_worker_url=None, **kw):
    """
    Redirect to backend configuration redirect_domain
    """
    # create website and websection
    website = self.setupWebSite(use_moved_temporarily=use_moved_temporarily,
                                configuration_service_worker_url=configuration_service_worker_url)

    absolute_url = website.absolute_url()

    # XXX can't handle "?" at path end, swallowed before __bobo_traverse__
    if source_path.endswith("/?"):
      source_path = source_path[:-2]
    if source_path.endswith("?"):
      source_path = source_path[:-1]

    api_scheme, api_netloc, api_path, _, _ = six.moves.urllib.parse.urlsplit(absolute_url)
    redirect_url = website.getLayoutProperty("redirect_domain")
    redirect_location = "/".join([redirect_url, source_path])

    status_to_assert = six.moves.http_client.MOVED_PERMANENTLY
    if use_moved_temporarily:
      status_to_assert = six.moves.http_client.FOUND

    api_netloc = '[ERP5_IPV6]:ERP5_PORT'
    for url_to_check in [
      # Direct
      # '%s://%s/%s/%s' % (api_scheme, api_netloc, website.getPath(), source_path),
      # direct VirtualHostMonster
      # '%s://%s/VirtualHostBase/http/example.org:1234%s/VirtualHostRoot/%s' % (api_scheme, api_netloc, website.getPath(), source_path),
      # not direct VirtualHostMonster
      '%s/%s' % (absolute_url, source_path),
      # '%s://%s/VirtualHostBase/http/example.org:1234/erp5/VirtualHostRoot/%s/%s' % (api_scheme, api_netloc, website.getRelativeUrl(), source_path),
      # '%s://%s/VirtualHostBase/http/example.org:1234/erp5/web_site_module/VirtualHostRoot/%s/%s' % (api_scheme, api_netloc, website.getId(), source_path)
    ]:

      scheme_to_check, netloc_to_check, _, _, _ = six.moves.urllib.parse.urlsplit(url_to_check)

      if (scheme_to_check == 'https'):
        connection = six.moves.http_client.HTTPSConnection(netloc_to_check, context=ssl._create_unverified_context(), timeout=10)
      else:
        connection = six.moves.http_client.HTTPConnection(netloc_to_check, timeout=10)
      self.addCleanup(connection.close)
      connection.request(
        method="GET",
        url=url_to_check
      )
      response = connection.getresponse()
      response_body = response.read()

      if (source_path == configuration_service_worker_url):
        # Test service worker URL
        self.assertEqual(response.status, six.moves.http_client.OK, '%s: %s' % (response.status, url_to_check))
        self.assertEqual(response.getheader('Content-Type'), 'application/javascript')
        self.assertTrue('self.registration.unregister()' in response_body,
                        response_body)

      else:
        self.assertEqual(response.status, status_to_assert, '%s: %s' % (response.status, url_to_check))
        self.assertEqual(response.getheader(LOCATION), redirect_location)
        self.assertEqual(response.getheader('Content-Type'), 'text/plain; charset=utf-8')
        self.assertEqual(response_body, redirect_location)

  ##############################################################################

  def test_plainRedirect(self):
    self.runTestRedirect("")

  def test_plainRedirectIndex(self):
    self.runTestRedirect("index.html")

  def test_plainRedirectQuery(self):
    self.runTestRedirect("?")

  def test_plainRedirectQueryWithParams(self):
    self.runTestRedirect("?a=b&c=&amp;d=e&")

  def test_plainRedirectFolderNoSlash(self):
    self.runTestRedirect("foo")

  def test_plainRedirectFolderSlash(self):
    self.runTestRedirect("foo/")

  def test_plainRedirectFolderNested(self):
    self.runTestRedirect("foo/bar")

  def test_plainRedirectFolderDeepNested(self):
    self.runTestRedirect("foo/bar/baz")

  def test_plainRedirectFolderNestedWithIndex(self):
    self.runTestRedirect("foo/bar/index.html")

  def test_queryStringRedirectFolder(self):
    self.runTestRedirect("foo?baz=bam")

  def test_queryStringRedirectFolderSlash(self):
    self.runTestRedirect("foo/?baz=bam")

  def test_queryStringRedirectFolderNested(self):
    self.runTestRedirect("foo/bar?baz=bam")

  def test_queryStringRedirectFolderDeepNested(self):
    self.runTestRedirect("foo/bar/baz?baz=bam&cous=cous&amp;the=end")

  def test_queryStringRedirectSlashQuestion(self):
    self.runTestRedirect("foo/bar/?")

  def test_queryStringRedirectWithEqual(self):
    self.runTestRedirect("foo/bar=")

  @unittest.expectedFailure
  def test_queryStringIgnoreLayout(self):
    self.runTestRedirect("?ignore_layout=1")

  def test_queryStringPortalSkin(self):
    self.runTestRedirect("?portal_skin=FOOBAR")

  def test_queryStringIgnoreLayoutWithQueryStringPortalSkin(self):
    self.runTestRedirect("?portal_skin=FOOBAR&ignore_layout=1")

  def test_queryStringEditableModeWithQueryStringPortalSkin(self):
    self.runTestRedirect("?portal_skin=FOOBAR&editable_mode=1")

  def test_plainRedirectGetId(self):
    self.runTestRedirect("getId")

  def test_plainRedirectWebSiteView(self):
    self.runTestRedirect("WebSite_view")

  def test_302queryStringRedirectFolderDeepNested(self):
    self.runTestRedirect("foo/bar/baz?baz=bam&cous=cous&amp;the=end", use_moved_temporarily=1)

  def test_unregisterServiceWorker(self):
    worker_url = 'worker.js'
    self.runTestRedirect(worker_url,
                         configuration_service_worker_url=worker_url)

class TestStaticWebSectionRedirection(TestStaticWebSiteRedirection):

  def getTitle(self):
    return "Test Static Web Section Redirection."

  def setupWebSite(self, use_moved_temporarily=None, **kw):
    """
    Setup Web Site
    """

    if WEB_SITE_ID in self.portal.web_site_module.objectIds():
      self.portal.web_site_module.manage_delObjects(WEB_SITE_ID)

    website = self.portal.web_site_module.newContent(
      portal_type="Web Site",
      id=WEB_SITE_ID
    )
    websection = website.newContent(
      portal_type="Static Web Section",
      id='foobarsection',
      layout_configuration_form_id="StaticWebSite_viewRedirectAssistConfiguration",
      skin_selection_name="RedirectAssist",
      custom_render_method_id="StaticWebSite_getRedirectSourceUrl",
      redirect_domain="https://www.example.org",
      use_moved_temporarily=use_moved_temporarily or 0,
      **kw
    )
    website.publish()

    self.tic()
    return websection
