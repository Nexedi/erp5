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
from erp5.component.extension import GoogleLoginUtility

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

GoogleLoginUtility.getUserId = getUserId
GoogleLoginUtility.getAccessTokenFromCode = getAccessTokenFromCode

class TestGoogleLogin(ERP5TypeTestCase):

  def getTitle(self):
    return "Test Google Login"

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    self.dummy_user_id = "dummy"
    person_module = self.portal.person_module
    if getattr(person_module, self.dummy_user_id, None) is None:
      person = person_module.newContent(first_name="Dummy",
                                        id=self.dummy_user_id,
                                        reference=self.dummy_user_id,
                                        user_id=self.dummy_user_id
                                       )
      assignment = person.newContent(portal_type="Assignment")
      assignment.open()
      login = person.newContent(portal_type="ERP5 Login", reference=self.dummy_user_id)
      login.validate()
      person.validate()
      self.tic()
    for obj in self.portal.portal_catalog(portal_type=["Google Login", "Person"],
                                          reference=getUserId(None),
                                          validation_state="validated"):
      obj.getObject().invalidate()
      uuid_str = uuid.uuid4().hex
      obj.setReference(uuid_str)
      obj.setUserId(uuid_str)
    system_preference = self.portal.portal_preferences.getActiveSystemPreference()
    if system_preference is None:
      system_preference = self.portal.portal_preferences.newContent(
        title="Global System Preference",
        portal_type="System Preference")
      system_preference.enable()

    system_preference.edit(
      preferred_google_client_id=CLIENT_ID,
      preferred_google_secret_key=SECRET_KEY,
    )
    self.tic()

  def test_redirect(self):
    """
      Check URL generate to redirect to Google
    """
    self.logout()
    self.portal.ERP5Site_redirectToGoogleLoginPage()
    location = self.portal.REQUEST.RESPONSE.getHeader("Location")
    self.assertTrue(location.startswith("https://accounts.google.com/o/oauth2/v2/auth"), location)
    self.assertIn("response_type=code", location)
    self.assertIn("client_id=%s" % CLIENT_ID, location)
    self.assertNotIn("secret_key=", location)
    self.assertIn("ERP5Site_receiveGoogleCallback", location)

  def test_receive_google_callback(self):
    """
      Check if ERP5 set cookie properly after receive code from external service
    """
    self.logout()
    self.portal.ERP5Site_receiveGoogleCallback(code=CODE)
    cookie = self.portal.REQUEST.RESPONSE.cookies.get("__ac_google_hash")
    self.assertEqual("b01533abb684a658dc71c81da4e67546", cookie["value"])
