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

import json
import httplib
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from erp5.component.extension import GoogleLoginUtility

CLIENT_ID = "a1b2c3"
SECRET_KEY = "3c2ba1"
ACCESS_TOKEN = "T1234"
CODE = "1234"

class MockHTTPSConnectionResponse(object):

  def __init__(self):
    self.status = 200

  def read(self):
    return json.dumps({"access_token": ACCESS_TOKEN})

class MockHTTPSConnection:

  def __init__(self, host, timeout):
    assert host == 'accounts.google.com'
    assert timeout == 30

  def request(self, method, url, body, headers):
    assert method == "POST"
    assert url == '/o/oauth2/token'
    assert "client_id=%s" % CLIENT_ID in body, "CLIENT_ID not found %s" % body
    assert "client_secret=%s" % SECRET_KEY in body, "SECRET_KEY not found %s" % body
    assert "code=%s" % CODE in body, "CODE not found %s" % body

  def getresponse(self):
    return MockHTTPSConnectionResponse()

def getUserId(access_token):
  return "1234"

httplib.HTTPSConnection = MockHTTPSConnection
GoogleLoginUtility.getUserId = getUserId

class TestGoogleLogin(ERP5TypeTestCase):

  def getTitle(self):
    return "Test Google Login"

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
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
    self.assertTrue(location.startswith("https://accounts.google.com/o/oauth2/auth"), location)
    self.assertIn("response_type=code", location)
    self.assertIn("client_id=%s" % CLIENT_ID, location)
    self.assertNotIn("secret_key=", location)
    self.assertIn("/ERP5Site_receiveGoogleCallback", location)

  def test_receive_google_callback(self):
    """
      Check if ERP5 set cookie properly after receive code from external service
    """
    self.logout()
    response = self.portal.ERP5Site_receiveGoogleCallback(code=CODE)
    self.assertEqual(self.portal.absolute_url(), response)

  def test_create_user_with_google_id(self):
    self.login()
    user_id = "go_" + getUserId(None)
    person = self.portal.portal_catalog.getResultValue(portal_type="Person",
                                                       reference=user_id,
                                                       validation_state="validated")
    if person:
      person.invalidate()
      self.tic()
    self.portal.Base_createOauth2User(
      '123_user_creation_in_progress',
      'User',
      'Last Name',
      user_id,
      'example@email.com',
      'Anonymous User')
    self.tic()
    google_login = self.portal.portal_catalog(portal_type="Google Login",
                                              reference=user_id,
                                              validation_state="validated")
    self.assertNotEqual(None, google_login)
    self.login(user_id)
    person = self.portal.ERP5Site_getAuthenticatedMemberPersonValue()
    self.assertEqual(user_id, person.getReference())