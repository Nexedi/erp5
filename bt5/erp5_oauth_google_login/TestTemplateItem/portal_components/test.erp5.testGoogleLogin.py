##############################################################################
#
# Copyright (c) 2002-2016 Nexedi SA and Contributors. All Rights Reserved.
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

import contextlib
import mock
import lxml
import json
import responses
import time
import six.moves.urllib as urllib
import six.moves.http_client
import six.moves.http_cookies
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class GoogleLoginTestCase(ERP5TypeTestCase):
  default_google_login_email_address = 'dummy@example.com'
  dummy_connector_id = 'test_google_connector'
  client_id = "a1b2c3"
  secret_key = "3c2ba1"

  def afterSetUp(self):
    self.portal.TemplateTool_checkGoogleExtractionPluginExistenceConsistency(fixit=True)

    # use random tokens because we can not clear the memcached cache
    self.access_token = 'access-token' + self.id() + self.newPassword()
    self.refresh_token = 'refresh-token' + self.id() + self.newPassword()

    self.default_user_person = self.portal.person_module.newContent(
      portal_type='Person',
      first_name=self.id(),
    )
    self.default_user_person.newContent(
      portal_type='Google Login',
      reference=self.default_google_login_email_address,
    ).validate()
    self.default_user_person.newContent(portal_type='Assignment').open()

    if getattr(self.portal.portal_oauth, self.dummy_connector_id, None) is None:
      connector = self.portal.portal_oauth.newContent(
        id=self.dummy_connector_id,
        portal_type="Google Connector",
        reference="default",
        client_id=self.client_id,
        secret_key=self.secret_key)
      connector.validate()
    self.tic()

  def beforeTearDown(self):
    self.abort()
    self.portal.portal_caches.getRamCacheRoot().get(
      self.portal.acl_users.erp5_google_extraction.cache_factory_name
    ).clearCache()
    self.portal.person_module.manage_delObjects([self.default_user_person.getId()])

    portal_catalog = self.portal.portal_catalog
    for connector in portal_catalog(portal_type="Google Connector",
                                    validation_state="validated",
                                    id="NOT %s" % self.dummy_connector_id,
                                    reference="default"):
      connector.invalidate()
    self.tic()

  @contextlib.contextmanager
  def _default_login_responses(self):
    with responses.RequestsMock() as rsps:
      rsps.add(
        method='POST',
        url='https://accounts.google.com/o/oauth2/token',
        json={
          'access_token': self.access_token,
          'refresh_token': self.refresh_token,
          'expires_in': 3600,
        },
      )
      rsps.add(
        method='GET',
        url='https://www.googleapis.com/oauth2/v1/userinfo',
        json={
          "first_name": "John",
          "last_name": "Doe",
          "email": self.default_google_login_email_address,
        }
      )
      yield


class TestGoogleLogin(GoogleLoginTestCase):
  def test_redirect(self):
    """
      Check URL generated to redirect to Google
    """
    self.logout()
    response = self.portal.REQUEST.RESPONSE
    self.portal.ERP5Site_redirectToGoogleLoginPage(RESPONSE=response)
    location = response.getHeader("Location")
    self.assertIn("https://accounts.google.com/o/oauth2/", location)
    self.assertIn("response_type=code", location)
    self.assertIn("client_id=%s" % self.client_id, location)
    self.assertNotIn("secret_key=", location)
    self.assertIn("ERP5Site_receiveGoogleCallback", location)

  def test_existing_user(self):
    request = self.portal.REQUEST
    response = request.RESPONSE

    redirect_url = urllib.parse.urlparse(
      self.portal.ERP5Site_redirectToGoogleLoginPage(RESPONSE=response))
    state = dict(urllib.parse.parse_qsl(redirect_url.query))['state']
    self.assertTrue(state)

    code = 'code-ABC'
    def token_callback(request):
      self.assertEqual(
        request.headers['Content-Type'],
        'application/x-www-form-urlencoded')
      self.assertEqual(
        dict(urllib.parse.parse_qsl(request.body)),
        {
          'client_id': self.client_id,
          'code': code,
          'grant_type': 'authorization_code',
          'client_secret': self.secret_key,
          'redirect_uri': self.portal.absolute_url() + '/ERP5Site_receiveGoogleCallback',
        },
      )
      return 200, {}, json.dumps({
        'access_token': self.access_token,
        'refresh_token': self.refresh_token,
        'expires_in': 3600,
      })

    with responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.POST,
        'https://accounts.google.com/o/oauth2/token',
        token_callback,
      )
      self.portal.ERP5Site_receiveGoogleCallback(code=code, state=state)

    def userinfo_callback(request):
      self.assertEqual(
        request.headers['Authorization'],
        'Bearer ' + self.access_token)
      return 200, {}, json.dumps({
        "first_name": "John",
        "last_name": "Doe",
        "email": self.default_google_login_email_address,
      })

    request['__ac_google_hash'] = response.cookies['__ac_google_hash']['value']
    with responses.RequestsMock() as rsps, \
      mock.patch(
        'Products.ERP5Security.ERP5ExternalOauth2ExtractionPlugin._setUserNameForAccessLog'
      ) as _setUserNameForAccessLog:
      rsps.add_callback(
        responses.GET,
        'https://www.googleapis.com/oauth2/v1/userinfo',
        userinfo_callback,
      )
      credentials = self.portal.acl_users.erp5_google_extraction.extractCredentials(
        request)

    self.assertEqual(credentials['login_portal_type'], 'Google Login')
    self.assertEqual(
      credentials['external_login'],
      self.default_google_login_email_address)

    # this is what will appear in Z2.log
    _setUserNameForAccessLog.assert_called_once_with(
      'erp5_google_extraction=dummy@example.com',
      request)

    user_id, user_name = self.portal.acl_users.erp5_login_users.authenticateCredentials(credentials)
    self.assertEqual(user_id, self.default_user_person.getUserId())
    self.assertEqual(user_name, self.default_google_login_email_address)

    self.login(user_id)
    self.assertEqual(self.portal.Base_getUserCaption(), user_name)

  def test_auth_cookie(self):
    request = self.portal.REQUEST
    response = request.RESPONSE

    # (the secure flag is only set if we accessed through https)
    request.setServerURL('https', 'example.com')

    redirect_url = urllib.parse.urlparse(
      self.portal.ERP5Site_redirectToGoogleLoginPage(RESPONSE=response))
    state = dict(urllib.parse.parse_qsl(redirect_url.query))['state']

    with self._default_login_responses():
      self.portal.ERP5Site_receiveGoogleCallback(code='code', state=state)
      ac_cookie, = [v for (k, v) in response.listHeaders() if k.lower() == 'set-cookie' and '__ac_google_hash=' in v]
      self.assertIn('; secure', ac_cookie.lower())
      self.assertIn('; httponly', ac_cookie.lower())
      self.assertIn('; samesite=lax', ac_cookie.lower())

      # make sure user info URL is called for _default_login_responses
      cookie = six.moves.http_cookies.SimpleCookie()
      cookie.load(ac_cookie)
      resp = self.publish(
        self.portal.getPath(),
        env={
          'HTTP_COOKIE': '__ac_google_hash="%s"' % cookie.get('__ac_google_hash').value
        }
      )
      self.assertEqual(resp.getStatus(), six.moves.http_client.OK)

  def test_non_existing_user(self):
    request = self.portal.REQUEST
    response = request.RESPONSE

    redirect_url = urllib.parse.urlparse(
      self.portal.ERP5Site_redirectToGoogleLoginPage(RESPONSE=response))
    state = dict(urllib.parse.parse_qsl(redirect_url.query))['state']

    with responses.RequestsMock() as rsps:
      rsps.add(
        method='POST',
        url='https://accounts.google.com/o/oauth2/token',
        json={
          'access_token': self.access_token,
          'refresh_token': self.refresh_token,
          'expires_in': 3600,
        },
      )
      self.portal.ERP5Site_receiveGoogleCallback(code='code', state=state)

    request['__ac_google_hash'] = response.cookies['__ac_google_hash']['value']
    with responses.RequestsMock() as rsps:
      rsps.add(
        method='GET',
        url='https://www.googleapis.com/oauth2/v1/userinfo',
        json={
          "first_name": "Bob",
          "last_name": "Doe",
          "email": "unknown@example.com",
        }
      )
      credentials = self.portal.acl_users.erp5_google_extraction.extractCredentials(
        request)

    self.assertEqual(credentials['login_portal_type'], 'Google Login')
    self.assertEqual(
      credentials['external_login'],
      "unknown@example.com")

    self.assertIsNone(
      self.portal.acl_users.erp5_login_users.authenticateCredentials(credentials))

  def test_invalid_cookie(self):
    request = self.portal.REQUEST
    request['__ac_google_hash'] = '???'
    credentials = self.portal.acl_users.erp5_google_extraction.extractCredentials(
      request)
    self.assertEqual(credentials, {})

  def test_refresh_token(self):
    request = self.portal.REQUEST
    response = request.RESPONSE

    redirect_url = urllib.parse.urlparse(
      self.portal.ERP5Site_redirectToGoogleLoginPage(RESPONSE=response))
    state = dict(urllib.parse.parse_qsl(redirect_url.query))['state']

    with self._default_login_responses():
      resp = self.publish(
        '%s/ERP5Site_receiveGoogleCallback?%s' % (
          self.portal.getPath(),
          urllib.parse.urlencode(
            {
              'code': 'code',
              'state': state,
            }
          )
        )
      )
      self.assertEqual(resp.getStatus(), six.moves.http_client.FOUND)
      env = {
        'HTTP_COOKIE': '__ac_google_hash="%s"' % resp.getCookie('__ac_google_hash')['value']
      }
      resp = self.publish(self.portal.getPath(), env=env)
      self.assertEqual(resp.getStatus(), six.moves.http_client.OK)

    def token_callback(request):
      self.assertEqual(
        request.headers['Content-Type'],
        'application/x-www-form-urlencoded')
      self.assertEqual(
        dict(urllib.parse.parse_qsl(request.body)),
        {
          'access_type': 'offline',
          'client_id': self.client_id,
          'client_secret': self.secret_key,
          'grant_type': 'refresh_token',
          'refresh_token': self.refresh_token,
        }
      )
      return 200, {}, json.dumps({
        'access_token': 'new' + self.access_token,
        'refresh_token': 'new' + self.refresh_token,
        'expires_in': 3600,
      })

    with mock.patch(
        'Products.ERP5Security.ERP5ExternalOauth2ExtractionPlugin.time.time',
        return_value=time.time() + 5000), \
        responses.RequestsMock() as rsps:
      rsps.add_callback(
        responses.POST,
        'https://accounts.google.com/o/oauth2/token',
        token_callback,
      )
      # refreshing the token calls userinfo again
      rsps.add(
        method='GET',
        url='https://www.googleapis.com/oauth2/v1/userinfo',
        json={
          "first_name": "John",
          "last_name": "Doe",
          "email": self.default_google_login_email_address,
        }
      )
      resp = self.publish(self.portal.getPath(), env=env)
      self.assertEqual(resp.getStatus(), six.moves.http_client.OK)

    resp = self.publish(self.portal.getPath(), env=env)
    self.assertEqual(resp.getStatus(), six.moves.http_client.OK)

  def test_refresh_token_expired(self):
    request = self.portal.REQUEST
    response = request.RESPONSE

    redirect_url = urllib.parse.urlparse(
      self.portal.ERP5Site_redirectToGoogleLoginPage(RESPONSE=response))
    state = dict(urllib.parse.parse_qsl(redirect_url.query))['state']

    with self._default_login_responses():
      resp = self.publish(
        '%s/ERP5Site_receiveGoogleCallback?%s' % (
          self.portal.getPath(),
          urllib.parse.urlencode(
            {
              'code': 'code',
              'state': state,
            }
          )
        )
      )
      self.assertEqual(resp.getStatus(), six.moves.http_client.FOUND)

      env = {
        'HTTP_COOKIE': '__ac_google_hash="%s"' % resp.getCookie('__ac_google_hash')['value']
      }
      resp = self.publish(self.portal.getPath(), env=env)
      self.assertEqual(resp.getStatus(), six.moves.http_client.OK)

    with mock.patch(
        'Products.ERP5Security.ERP5ExternalOauth2ExtractionPlugin.time.time',
        return_value=time.time() + 5000), \
        responses.RequestsMock() as rsps:
      rsps.add(
        method='POST',
        url='https://accounts.google.com/o/oauth2/token',
        status=six.moves.http_client.UNAUTHORIZED,
      )
      resp = self.publish(self.portal.getPath(), env=env)
      self.assertEqual(resp.getStatus(), six.moves.http_client.FOUND)
      self.assertIn('/login_form', resp.getHeader('Location'))

  def test_logout(self):
    resp = self.publish(self.portal.getId() + '/logout')
    self.assertEqual(resp.getCookie("__ac_google_hash")['value'], 'deleted')


class TestERP5JSGoogleLogin(GoogleLoginTestCase):
  def _getWebSite(self):
    return self.portal.web_site_module.renderjs_runner

  def test_login_form(self):
    resp = self.publish(self._getWebSite().getPath() + '/login_form')
    tree = lxml.etree.fromstring(resp.getBody(), parser=lxml.etree.HTMLParser())
    google_login_link, = [
        img.getparent().attrib['href']
        for img in tree.findall('.//a/img')
        if img.attrib['alt'] == 'Sign in with Google'
    ]
    self.assertIn('/ERP5Site_redirectToGoogleLoginPage', google_login_link)
    resp = self.publish(urllib.parse.urlparse(google_login_link).path)
    # this request redirects to google
    self.assertEqual(resp.getStatus(), six.moves.http_client.FOUND)
    self.assertIn('google.com', resp.getHeader('Location'))

  def test_logout(self):
    resp = self.publish(self._getWebSite().getPath() + '/WebSite_logout')
    self.assertEqual(resp.getCookie("__ac_google_hash")['value'], 'deleted')
