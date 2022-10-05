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

import uuid
import mock
import lxml
import urlparse
import httplib
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript


CLIENT_ID = "a1b2c3"
SECRET_KEY = "3c2ba1"
ACCESS_TOKEN = "T1234"
CODE = "1234"

def getUserId(access_token):
  return "dummy@example.com"

def getAccessTokenFromCode(code, redirect_uri):
  assert code == CODE, "Invalid code"
  # This is an example of a Google response
  return  {'_module': 'oauth2client.client',
           'scopes': ['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
           'revoke_uri': 'https://accounts.google.com/o/oauth2/revoke',
           'access_token': ACCESS_TOKEN,
           'token_uri': 'https://www.googleapis.com/oauth2/v4/token',
           'token_info_uri': 'https://www.googleapis.com/oauth2/v3/tokeninfo',
           'invalid': False,
           'token_response': {
             'access_token': ACCESS_TOKEN,
             'token_type': 'Bearer',
             'expires_in': 3600,
             'refresh_token': "111",
             'id_token': '222'
           },
           'client_id': CLIENT_ID,
           'id_token': {
             'picture': '',
             'sub': '',
             'aud': '',
             'family_name': 'D',
             'iss': 'https://accounts.google.com',
             'email_verified': True,
             'at_hash': 'p3vPYQkVuqByBA',
             'given_name': 'John',
             'exp': 123,
             'azp': '123.apps.googleusercontent.com',
             'iat': 455,
             'locale': 'pt',
             'email': getUserId(None),
             'name': 'John D'
           },
           'client_secret': 'secret',
           'token_expiry': '2017-03-31T16:06:28Z',
           '_class': 'OAuth2Credentials',
           'refresh_token': '111',
           'user_agent': None
          }

def getUserEntry(access_token):
  return {
    "first_name": "John",
    "last_name": "Doe",
    "email": getUserId(None),
    "reference": getUserId(None)
  }


class GoogleLoginTestCase(ERP5TypeTestCase):
  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    self.login()
    self.portal.TemplateTool_checkGoogleExtractionPluginExistenceConsistency(fixit=True)

    self.dummy_connector_id = "test_google_connector"
    portal_catalog = self.portal.portal_catalog
    for obj in portal_catalog(portal_type=["Google Login", "Person"],
                              reference=getUserId(None),
                              validation_state="validated"):
      obj.getObject().invalidate()
      uuid_str = uuid.uuid4().hex
      obj.setReference(uuid_str)
      obj.setUserId(uuid_str)
    for connector in portal_catalog(portal_type="Google Connector",
                                    validation_state="validated",
                                    id="NOT %s" % self.dummy_connector_id,
                                    reference="default"):
      connector.invalidate()

    if getattr(self.portal.portal_oauth, self.dummy_connector_id, None) is None:
      connector = self.portal.portal_oauth.newContent(id=self.dummy_connector_id,
                                                      portal_type="Google Connector",
                                                      reference="default",
                                                      client_id=CLIENT_ID,
                                                      secret_key=SECRET_KEY)
      connector.validate()
    self.tic()
    self.logout()


class TestGoogleLogin(GoogleLoginTestCase):
  def test_redirect(self):
    """
      Check URL generate to redirect to Google
    """
    self.logout()
    self.portal.ERP5Site_redirectToGoogleLoginPage()
    location = self.portal.REQUEST.RESPONSE.getHeader("Location")
    self.assertIn("https://accounts.google.com/o/oauth2/", location)
    self.assertIn("response_type=code", location)
    self.assertIn("client_id=%s" % CLIENT_ID, location)
    self.assertNotIn("secret_key=", location)
    self.assertIn("ERP5Site_receiveGoogleCallback", location)

  def test_existing_user(self):
    self.login()
    person = self.portal.person_module.newContent(
        portal_type='Person',
    )
    person.newContent(
        portal_type='Google Login',
        reference=getUserId(None)
    ).validate()
    person.newContent(portal_type='Assignment').open()
    self.tic()
    self.logout()

    request = self.portal.REQUEST
    response = request.RESPONSE
    with mock.patch(
        'erp5.component.extension.GoogleLoginUtility.getAccessTokenFromCode',
        side_effect=getAccessTokenFromCode,
    ) as getAccessTokenFromCode_mock, \
      mock.patch(
        'erp5.component.extension.GoogleLoginUtility.getUserEntry',
        side_effect=getUserEntry
      ) as getUserEntry_mock:
      getAccessTokenFromCode_mock.__code__ = getAccessTokenFromCode.__code__
      getUserEntry_mock.__code__ = getUserEntry.__code__
      self.portal.ERP5Site_receiveGoogleCallback(code=CODE)
    getAccessTokenFromCode_mock.assert_called_once()
    getUserEntry_mock.assert_called_once()

    request["__ac_google_hash"] = response.cookies["__ac_google_hash"]["value"]

    with mock.patch(
        'Products.ERP5Security.ERP5ExternalOauth2ExtractionPlugin._setUserNameForAccessLog'
      ) as _setUserNameForAccessLog:
      credentials = self.portal.acl_users.erp5_google_extraction.extractCredentials(request)
    self.assertEqual(
        'Google Login',
        credentials['login_portal_type'])
    self.assertEqual(
        getUserId(None),
        credentials['external_login'])
    # this is what will appear in Z2.log
    _setUserNameForAccessLog.assert_called_once_with(
        'erp5_google_extraction=%s' % getUserId(None),
        request)

    user_id, login = self.portal.acl_users.erp5_login_users.authenticateCredentials(credentials)
    self.assertEqual(person.getUserId(), user_id)
    self.assertEqual(getUserId(None), login)

    self.login(user_id)
    self.assertEqual(self.portal.Base_getUserCaption(), login)

  def test_auth_cookie(self):
    request = self.portal.REQUEST
    response = request.RESPONSE
    # (the secure flag is only set if we accessed through https)
    request.setServerURL('https', 'example.com')

    with mock.patch(
        'erp5.component.extension.GoogleLoginUtility.getAccessTokenFromCode',
        side_effect=getAccessTokenFromCode,
    ) as getAccessTokenFromCode_mock, \
      mock.patch(
        'erp5.component.extension.GoogleLoginUtility.getUserEntry',
        side_effect=getUserEntry
      ) as getUserEntry_mock:
      getAccessTokenFromCode_mock.__code__ = getAccessTokenFromCode.__code__
      getUserEntry_mock.__code__ = getUserEntry.__code__
      self.portal.ERP5Site_receiveGoogleCallback(code=CODE)

    getAccessTokenFromCode_mock.assert_called_once()
    getUserEntry_mock.assert_called_once()

    ac_cookie, = [v for (k, v) in response.listHeaders() if k.lower() == 'set-cookie' and '__ac_google_hash=' in v]
    self.assertIn('; secure', ac_cookie.lower())
    self.assertIn('; httponly', ac_cookie.lower())
    self.assertIn('; samesite=lax', ac_cookie.lower())

  def test_create_user_in_ERP5Site_createGoogleUserToOAuth(self):
    """
      Check if ERP5 set cookie properly after receive code from external service
    """
    self.login()
    id_list = []
    for result in self.portal.portal_catalog(portal_type="Credential Request",
                                                         reference=getUserId(None)):
      id_list.append(result.getObject().getId())
    self.portal.credential_request_module.manage_delObjects(ids=id_list)
    skin = self.portal.portal_skins.custom
    createZODBPythonScript(skin, "CredentialRequest_createUser", "", """
person = context.getDestinationDecisionValue(portal_type="Person")

login_list = [x for x in person.objectValues(portal_type='Google Login') \
              if x.getValidationState() == 'validated']

if len(login_list):
  login = login_list[0]
else:
  login = person.newContent(portal_type='Google Login')

reference = context.getReference()
if not login.hasReference():
  if not reference:
    raise ValueError("Impossible to create an account without login")
  login.setReference(reference)
  if not person.Person_getUserId():
    person.setUserId(reference)

  if login.getValidationState() == 'draft':
    login.validate()

return reference, None
""")

    createZODBPythonScript(skin, "ERP5Site_createGoogleUserToOAuth", "user_reference, user_dict", """
module = context.getPortalObject().getDefaultModule(portal_type='Credential Request')
credential_request = module.newContent(
  portal_type="Credential Request",
  first_name=user_dict["first_name"],
  last_name=user_dict["last_name"],
  reference=user_reference,
  default_email_text=user_dict["email"],
)
credential_request.submit()
context.portal_alarms.accept_submitted_credentials.activeSense()
return credential_request
""")
    self.logout()

    with mock.patch(
        'erp5.component.extension.GoogleLoginUtility.getAccessTokenFromCode',
        side_effect=getAccessTokenFromCode,
    ) as getAccessTokenFromCode_mock, \
      mock.patch(
        'erp5.component.extension.GoogleLoginUtility.getUserEntry',
        side_effect=getUserEntry
      ) as getUserEntry_mock:
      getAccessTokenFromCode_mock.__code__ = getAccessTokenFromCode.__code__
      getUserEntry_mock.__code__ = getUserEntry.__code__
      response = self.portal.ERP5Site_receiveGoogleCallback(code=CODE)
    getAccessTokenFromCode_mock.assert_called_once()
    getUserEntry_mock.assert_called_once()

    google_hash = self.portal.REQUEST.RESPONSE.cookies.get("__ac_google_hash")["value"]
    self.assertEqual("b01533abb684a658dc71c81da4e67546", google_hash)
    absolute_url = self.portal.absolute_url()
    self.assertNotEqual(absolute_url[-1], '/')
    self.assertEqual(absolute_url + '/', response)
    cache_dict = self.portal.Base_getBearerToken(google_hash, "google_server_auth_token_cache_factory")
    self.assertEqual(CLIENT_ID, cache_dict["client_id"])
    self.assertEqual(ACCESS_TOKEN, cache_dict["access_token"])
    self.assertEqual({'reference': getUserId(None)},
      self.portal.Base_getBearerToken(ACCESS_TOKEN, "google_server_auth_token_cache_factory")
    )
    self.portal.REQUEST["__ac_google_hash"] = google_hash
    erp5_google_extractor = self.portal.acl_users.erp5_google_extraction
    self.assertEqual({'external_login': getUserId(None),
      'login_portal_type': 'Google Login',
      'remote_host': '',
      'remote_address': ''}, erp5_google_extractor.extractCredentials(self.portal.REQUEST))
    self.tic()
    self.login()
    credential_request = self.portal.portal_catalog(portal_type="Credential Request",
                                                    reference=getUserId(None))[0].getObject()
    credential_request.accept()
    person = credential_request.getDestinationDecisionValue()
    google_login = person.objectValues(portal_types="Google Login")[0]
    self.assertEqual(getUserId(None), google_login.getReference())

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
    resp = self.publish(urlparse.urlparse(google_login_link).path)
    # this request redirects to google
    self.assertEqual(resp.getStatus(), httplib.FOUND)
    self.assertIn('google.com', resp.getHeader('Location'))

  def test_logout(self):
    resp = self.publish(self._getWebSite().getPath() + '/WebSite_logout')
    self.assertEqual(resp.getCookie("__ac_google_hash")['value'], 'deleted')
