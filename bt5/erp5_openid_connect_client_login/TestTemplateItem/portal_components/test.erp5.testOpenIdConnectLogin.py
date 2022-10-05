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
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript


CLIENT_ID = "a1b2c3"
SECRET_KEY = "3c2ba1"
SCOPE = ('username', 'openid', 'prd:test')
URL_STRING = 'https://openidtest.example.org:443'
DESCRIPTION = """{
  "redirect_uris": ["https://testdomain.erp5.net/hateoas/connection/oid_auth"],
  "response_types": "form_post",
  "contacts": ["testuser@nexedi.com"],
  "client_name": "test"
}"""
ACCESS_TOKEN = "XXXX0koYI5hASXZaExeYsGlqz1bSIcGyEg"
CODE = "1234"

def getUserId(access_token):
  return "ETEST234"

def getAccessTokenFromCode(code, redirect_uri):
  # This is an example of an OpenId response
  return {
      'access_token': u'XXXX0koYI5hASXZaExeYsGlqz1bSIcGyEg',
      'token_type': u'Bearer',
      'expires_in': 3599,
      'refresh_token': u'XXXXXXe4TlPbNSXQocR4zlxQUdrit5sZ1FutZcece9'
    }


def getUserEntry(token):
  return {
    "sub": getUserId(None)
  }

class OpenIdConnectLoginTestCase(ERP5TypeTestCase):

  cache_factory = "openid_connect_server_auth_token_cache_factory"

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    self.login()
    self.portal.TemplateTool_checkOpenIdConnectExtractionPluginExistenceConsistency(fixit=True)

    self.dummy_connector_id = "test_openid_connect_connector"
    portal_catalog = self.portal.portal_catalog
    for obj in portal_catalog(portal_type=["OpenId Connect Login", "Person"],
                              reference=getUserId(None),
                              validation_state="validated"):
      obj.getObject().invalidate()
      uuid_str = uuid.uuid4().hex
      obj.setReference(uuid_str)
      obj.setUserId(uuid_str)
    for connector in portal_catalog(portal_type="OpenId Connect Connector",
                                    validation_state="validated",
                                    id="NOT %s" % self.dummy_connector_id,
                                    reference="default"):
      connector.invalidate()

    if getattr(self.portal.portal_web_services, self.dummy_connector_id, None) is None:
      connector = self.portal.portal_web_services.newContent(id=self.dummy_connector_id,
                                                      portal_type="OpenId Connect Connector",
                                                      reference="default",
                                                      user_id=CLIENT_ID,
                                                      password=SECRET_KEY,
                                                      url_string=URL_STRING,
                                                      scope=SCOPE,
                                                      description=DESCRIPTION,
                                                     )
      connector.validate()
    self.tic()
    self.logout()

  def setStateInCache(self, state):
    self.portal.Base_setBearerToken(state, "12234", self.cache_factory)


class TestOpenIdConnectLogin(OpenIdConnectLoginTestCase):

  def test_auth_cookie(self):
    state=uuid.uuid4().hex
    self.setStateInCache(state)
    self.portal.REQUEST.environ['QUERY_STRING'] = "Couscous"

    request = self.portal.REQUEST
    response = request.RESPONSE
    # (the secure flag is only set if we accessed through https)
    request.setServerURL('https', 'example.com')
    with mock.patch(
        'erp5.component.extension.OpenIdConnectLoginUtility.getAccessTokenFromCode',
        side_effect=getAccessTokenFromCode,
    ) as getAccessTokenFromCode_mock, \
      mock.patch(
        'erp5.component.extension.OpenIdConnectLoginUtility.getUserEntry',
        side_effect=getUserEntry
      ) as getUserEntry_mock:
      getAccessTokenFromCode_mock.__code__ = getAccessTokenFromCode.__code__
      getUserEntry_mock.__code__ = getUserEntry.__code__
      self.portal.ERP5Site_receiveOpenIdCallback(code=CODE, state=state)

    getAccessTokenFromCode_mock.assert_called_once()
    getUserEntry_mock.assert_called_once()

    ac_cookie, = [v for (k, v) in response.listHeaders() if k.lower() == 'set-cookie' and '__ac_openidconnect_hash=' in v]
    self.assertIn('; secure', ac_cookie.lower())
    self.assertIn('; httponly', ac_cookie.lower())
    self.assertIn('; samesite=lax', ac_cookie.lower())

  def test_existing_user(self):
    state=uuid.uuid4().hex
    self.setStateInCache(state)
    self.portal.REQUEST.environ['QUERY_STRING'] = "Couscous"

    self.login()
    person = self.portal.person_module.newContent(
        portal_type='Person',
    )
    person.newContent(
        portal_type='OpenId Connect Login',
        reference=getUserId(None)
    ).validate()
    person.newContent(portal_type='Assignment').open()
    self.tic()
    self.logout()

    request = self.portal.REQUEST
    response = request.RESPONSE
    with mock.patch(
        'erp5.component.extension.OpenIdConnectLoginUtility.getAccessTokenFromCode',
        side_effect=getAccessTokenFromCode,
    ) as getAccessTokenFromCode_mock, \
      mock.patch(
        'erp5.component.extension.OpenIdConnectLoginUtility.getUserEntry',
        side_effect=getUserEntry
      ) as getUserEntry_mock:
      getAccessTokenFromCode_mock.__code__ = getAccessTokenFromCode.__code__
      getUserEntry_mock.__code__ = getUserEntry.__code__
      self.portal.ERP5Site_receiveOpenIdCallback(code=CODE, state=state)
    getAccessTokenFromCode_mock.assert_called_once()
    getUserEntry_mock.assert_called_once()

    request["__ac_openidconnect_hash"] = response.cookies["__ac_openidconnect_hash"]["value"]

    with mock.patch(
        'Products.ERP5Security.ERP5ExternalOauth2ExtractionPlugin._setUserNameForAccessLog'
      ) as _setUserNameForAccessLog:
      credentials = self.portal.acl_users.erp5_openid_connect_extraction.extractCredentials(request)
    self.assertEqual(
        'OpenId Connect Login',
        credentials['login_portal_type'])
    self.assertEqual(
        getUserId(None),
        credentials['external_login'])
    # this is what will appear in Z2.log
    _setUserNameForAccessLog.assert_called_once_with(
        'erp5_openid_connect_extraction=%s' % getUserId(None),
        request)

    user_id, login = self.portal.acl_users.erp5_login_users.authenticateCredentials(credentials)
    self.assertEqual(person.getUserId(), user_id)
    self.assertEqual(getUserId(None), login)

    self.login(user_id)
    self.assertEqual(self.portal.Base_getUserCaption(), login)

  def test_logout(self):
    resp = self.publish(self.portal.getId() + '/logout')
    self.assertEqual(resp.getCookie("__ac_openidconnect_hash")['value'], 'deleted')

  def test_create_user_in_ERP5Site_createOpenIdConnectUserToOAuth(self):
    """
      Check if ERP5 set cookie properly after receive code from external service
    """
    state=uuid.uuid4().hex
    self.setStateInCache(state)
    self.portal.REQUEST.environ['QUERY_STRING'] = "Couscous"

    self.login()
    id_list = []
    for result in self.portal.portal_catalog(portal_type="Credential Request",
                                                         reference=getUserId(None)):
      id_list.append(result.getObject().getId())
    self.portal.credential_request_module.manage_delObjects(ids=id_list)
    skin = self.portal.portal_skins.custom
    createZODBPythonScript(skin, "CredentialRequest_createUser", "", """
person = context.getDestinationDecisionValue(portal_type="Person")

login_list = [x for x in person.objectValues(portal_type='OpenId Connect Login') \
              if x.getValidationState() == 'validated']

if len(login_list):
  login = login_list[0]
else:
  login = person.newContent(portal_type='OpenId Connect Login')

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

    createZODBPythonScript(skin, "ERP5Site_createOpenIdConnectUserToOAuth", "user_reference, user_dict", """
module = context.getPortalObject().getDefaultModule(portal_type='Credential Request')
credential_request = module.newContent(
  portal_type="Credential Request",
  first_name=user_dict["sub"],
  reference=user_reference,
)
credential_request.submit()
context.portal_alarms.accept_submitted_credentials.activeSense()
return credential_request
""")
    self.logout()

    with mock.patch(
        'erp5.component.extension.OpenIdConnectLoginUtility.getAccessTokenFromCode',
        side_effect=getAccessTokenFromCode,
    ) as getAccessTokenFromCode_mock, \
      mock.patch(
        'erp5.component.extension.OpenIdConnectLoginUtility.getUserEntry',
        side_effect=getUserEntry
      ) as getUserEntry_mock:
      getAccessTokenFromCode_mock.__code__ = getAccessTokenFromCode.__code__
      getUserEntry_mock.__code__ = getUserEntry.__code__
      self.portal.ERP5Site_receiveOpenIdCallback(code=CODE, state=state)
    getAccessTokenFromCode_mock.assert_called_once()
    getUserEntry_mock.assert_called_once()

    open_id_connect_hash = self.portal.REQUEST.RESPONSE.cookies.get("__ac_openidconnect_hash")["value"]
    self.assertEqual("917b08e860593a6d0530c4cad5758f54", open_id_connect_hash)
    absolute_url = self.portal.absolute_url()
    self.assertNotEqual(absolute_url[-1], '/')
    cache_dict = self.portal.Base_getBearerToken(open_id_connect_hash, "openid_connect_server_auth_token_cache_factory")
    self.assertEqual(ACCESS_TOKEN, cache_dict["access_token"])
    self.assertEqual({'reference': getUserId(None)},
      self.portal.Base_getBearerToken(ACCESS_TOKEN, "openid_connect_server_auth_token_cache_factory")
    )
    self.portal.REQUEST["__ac_openidconnect_hash"] = open_id_connect_hash
    erp5_openid_connect_extraction = self.portal.acl_users.erp5_openid_connect_extraction
    self.assertEqual({'external_login': getUserId(None),
      'login_portal_type': 'OpenId Connect Login',
      'remote_host': '',
      'remote_address': ''}, erp5_openid_connect_extraction.extractCredentials(self.portal.REQUEST))
    self.tic()
    self.login()
    credential_request = self.portal.portal_catalog(portal_type="Credential Request",
                                                    reference=getUserId(None))[0].getObject()
    credential_request.accept()
    person = credential_request.getDestinationDecisionValue()
    oidc_login = person.objectValues(portal_types="OpenId Connect Login")[0]
    self.assertEqual(getUserId(None), oidc_login.getReference())


class TestERP5JSOpenIdConnectLogin(OpenIdConnectLoginTestCase):
  def _getWebSite(self):
    return self.portal.web_site_module.renderjs_runner

  def test_login_form(self):
    resp = self.publish(self._getWebSite().getPath() + '/login_form')
    tree = lxml.etree.fromstring(resp.getBody(), parser=lxml.etree.HTMLParser())
    openid_connect_login_link_list = [
        link
        for link in tree.findall('.//a')
        if '/ERP5Site_redirectToOpenIdLoginPage' in link.attrib['href']
    ]
    self.assertEqual(len(openid_connect_login_link_list), 1)

  def test_logout(self):
    resp = self.publish(self._getWebSite().getPath() + '/WebSite_logout')
    self.assertEqual(resp.getCookie("__ac_openidconnect_hash")['value'], 'deleted')
