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
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from erp5.component.extension import FacebookLoginUtility
from Products.ERP5Type.tests.utils import createZODBPythonScript

CLIENT_ID = "a1b2c3"
SECRET_KEY = "3c2ba1"
ACCESS_TOKEN = "EAAF10h0gIiQZDZD"
CODE = "1235"

def getUserId(access_token):
  return "1234567890123456"

def getAccessTokenFromCode(code, redirect_uri):
  assert code == CODE, "Invalid code"
  # This is an example of a Facebook response
  return  {u'access_token': u'EAAF10h0gIiQZDZD',
           u'token_type': u'bearer',
           u'expires_in': 5138578}

def getUserEntry(access_token):
  return {'name': 'John Doe',
          'reference': getUserId(None),
          'email': "dummy@example.org"}

FacebookLoginUtility_getAccessTokenFromCode = FacebookLoginUtility.getAccessTokenFromCode
FacebookLoginUtility_getUserEntry = FacebookLoginUtility.getUserEntry

class TestFacebookLogin(ERP5TypeTestCase):

  def getTitle(self):
    return "Test Facebook Login"

  def beforeTearDown(self):
    FacebookLoginUtility.getAccessTokenFromCode = FacebookLoginUtility_getAccessTokenFromCode
    FacebookLoginUtility.getUserEntry = FacebookLoginUtility_getUserEntry

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    self.login()
    self.portal.TemplateTool_checkFacebookExtractionPluginExistenceConsistency(fixit=True)
    # Patch extension to avoid external connection
    FacebookLoginUtility.getUserId = getUserId
    FacebookLoginUtility.getAccessTokenFromCode = getAccessTokenFromCode
    FacebookLoginUtility.getUserEntry = getUserEntry

    self.dummy_connector_id = "test_facebook_connector"
    person_module = self.portal.person_module
    portal_catalog = self.portal.portal_catalog
    for obj in portal_catalog(portal_type=["Facebook Login", "Person"],
                              reference=getUserId(None),
                              validation_state="validated"):
      obj.getObject().invalidate()
      uuid_str = uuid.uuid4().hex
      obj.setReference(uuid_str)
      obj.setUserId(uuid_str)
    for connector in portal_catalog(portal_type="Facebook Connector",
                                    validation_state="validated",
                                    id="NOT %s" % self.dummy_connector_id,
                                    reference="default"):
      connector.invalidate()

    if getattr(self.portal.portal_oauth, self.dummy_connector_id, None) is None:
      connector = self.portal.portal_oauth.newContent(id=self.dummy_connector_id,
                                                      portal_type="Facebook Connector",
                                                      reference="default",
                                                      client_id=CLIENT_ID,
                                                      secret_key=SECRET_KEY)
      connector.validate()
    self.tic()
    self.logout()

  def test_redirect(self):
    """
      Check URL generate to redirect to Facebook
    """
    self.logout()
    self.portal.ERP5Site_redirectToFacebookLoginPage()
    location = self.portal.REQUEST.RESPONSE.getHeader("Location")
    self.assertIn("https://www.facebook.com/v2.10/dialog/oauth?", location)
    self.assertIn("scope=email&redirect_uri=", location)
    self.assertIn("client_id=%s" % CLIENT_ID, location)
    self.assertNotIn("secret_key=", location)
    self.assertIn("ERP5Site_callbackFacebookLogin", location)

  def test_create_user_in_ERP5Site_createFacebookUserToOAuth(self):
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

login_list = [x for x in person.objectValues(portal_type='Facebook Login') \
              if x.getValidationState() == 'validated']

if len(login_list):
  login = login_list[0]
else:
  login = person.newContent(portal_type='Facebook Login')

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

    createZODBPythonScript(skin, "ERP5Site_createFacebookUserToOAuth", "user_reference, user_dict", """
module = context.getPortalObject().getDefaultModule(portal_type='Credential Request')
credential_request = module.newContent(
  portal_type="Credential Request",
  first_name=user_dict["name"],
  reference=user_reference,
  default_email_text=user_dict["email"],
)
credential_request.submit()
context.portal_alarms.accept_submitted_credentials.activeSense()
return credential_request
""")
    self.logout()
    response = self.portal.ERP5Site_callbackFacebookLogin(code=CODE)
    facebook_hash = self.portal.REQUEST.RESPONSE.cookies.get("__ac_facebook_hash")["value"]
    self.assertEqual("8cec04e21e927f1023f4f4980ec11a77", facebook_hash)
    self.assertEqual(self.portal.absolute_url(), response)
    cache_dict = self.portal.Base_getBearerToken(facebook_hash, "facebook_server_auth_token_cache_factory")
    self.assertEqual(ACCESS_TOKEN, cache_dict["access_token"])
    self.assertEqual({'reference': getUserId(None)},
      self.portal.Base_getBearerToken(ACCESS_TOKEN, "facebook_server_auth_token_cache_factory")
    )
    self.portal.REQUEST["__ac_facebook_hash"] = facebook_hash
    erp5_facebook_extractor = self.portal.acl_users.erp5_facebook_extraction
    self.assertEqual({'external_login': getUserId(None),
      'login_portal_type': 'Facebook Login',
      'remote_host': '',
      'remote_address': ''}, erp5_facebook_extractor.extractCredentials(self.portal.REQUEST))
    self.tic()
    self.login()
    credential_request = self.portal.portal_catalog(portal_type="Credential Request",
                                                    reference=getUserId(None))[0].getObject()
    if credential_request.getValidationState() != "accepted":
      credential_request.accept()
    person = credential_request.getDestinationDecisionValue()
    facebook_login = person.objectValues(portal_types="Facebook Login")[0]
    self.assertEqual(getUserId(None), facebook_login.getReference())
