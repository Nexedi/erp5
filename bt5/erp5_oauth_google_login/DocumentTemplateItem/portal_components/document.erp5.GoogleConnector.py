##############################################################################
# Copyright (c) 2024 Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo

import random
import string
import time

import oauthlib.oauth2
import requests
from zExceptions import Unauthorized

from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type import Permissions
from Products.ERP5Type.Utils import unicode2str
from Products.ERP5Type.Timeout import getTimeLeft



AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
USER_INFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'
SCOPE_LIST = ['https://www.googleapis.com/auth/userinfo.profile',
              'https://www.googleapis.com/auth/userinfo.email']
# Default timeout (in seconds) for the HTTP request made to google servers to
# exchange the authorization code for a token.
DEFAULT_HTTP_TIMEOUT = 10


class GoogleConnector(XMLObject):
  meta_type = 'ERP5 Google Connector'
  portal_type = 'Google Connector'
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  @security.public
  def redirectToGoogleLoginPage(self, redirect_uri, RESPONSE):
    """Redirect to authorization page.
    """
    authorization_url = self._getOAuthlibClient().prepare_request_uri(
      uri=AUTH_URL,
      redirect_uri=redirect_uri,
      scope=SCOPE_LIST,
      access_type="offline",
      include_granted_scopes='true',
      prompt="consent",
      state=self._getAuthorizationState(),
    )
    return RESPONSE.redirect(authorization_url)

  @security.public  # XXX public but not publishable
  def getTokenFromCode(self, state, code, redirect_uri):
    self._verifyAuthorizationState(state)
    body = self._getOAuthlibClient().prepare_request_body(
      code=code,
      client_secret=self.getSecretKey(),
      redirect_uri=redirect_uri,
    )
    resp = requests.post(
      TOKEN_URL,
      data=body,
      headers={'Content-Type': 'application/x-www-form-urlencoded'},
      timeout=self._getTimeout(),
    )
    __traceback_info__ = (resp.content, resp.status_code)
    resp.raise_for_status()
    return self._getGoogleTokenFromJSONResponse(resp.json())

  @security.private
  def refreshToken(self, token):
    """Refresh auth token.

    Used by Products.ERP5Security.ERP5ExternalOauth2ExtractionPlugin
    """
    body = self._getOAuthlibClient().prepare_refresh_body(
      client_id=self.getClientId(),
      client_secret=self.getSecretKey(),
      access_type="offline",
      refresh_token=token['refresh_token'],
    )
    resp = requests.post(
      TOKEN_URL,
      data=body,
      headers={'Content-Type': 'application/x-www-form-urlencoded'},
      timeout=self._getTimeout(),
    )
    if not resp.ok:
      return {}
    return self._getGoogleTokenFromJSONResponse(resp.json())

  @security.private
  def getUserEntry(self, access_token):
    resp = requests.get(
      USER_INFO_URL,
      headers={'Authorization': 'Bearer {}'.format(access_token)},
      timeout=self._getTimeout(),
    )
    resp.raise_for_status()
    google_entry = resp.json()
    user_entry = {}
    # remap user info
    for erp5_key, google_key in (
        ('first_name', 'given_name'),
        ('last_name', 'family_name'),
        ('email', 'email'),
        ('reference', 'email'),
      ):
      user_entry[erp5_key] = unicode2str(google_entry.get(google_key, ''))
    return user_entry

  def _getOAuthlibClient(self):
    return oauthlib.oauth2.WebApplicationClient(
      self.getClientId(),
      access_type="offline",
    )

  def _getGoogleTokenFromJSONResponse(self, token):
    return {
      'access_token': unicode2str(token['access_token']),
      'refresh_token': unicode2str(token['refresh_token']),
      'expires_in': token['expires_in'],
      'response_timestamp': time.time(),
      'connector_relative_url': self.getRelativeUrl(),
    }

  def _getAuthorizationState(self):
    alphabet = string.ascii_letters + string.digits
    state = ''.join(random.SystemRandom().choice(alphabet) for _ in range(32))
    self.getPortalObject().portal_sessions['google_login_auth_state'][state] = True
    return state

  def _verifyAuthorizationState(self, state):
    if not self.getPortalObject().portal_sessions['google_login_auth_state'].pop(state, False):
      raise Unauthorized

  def _getTimeout(self):
    """Compute the time left according to publisher deadline.
    """
    time_left = getTimeLeft()
    if time_left is None:
      time_left = DEFAULT_HTTP_TIMEOUT
    return min(self.getTimeout() or DEFAULT_HTTP_TIMEOUT, time_left)
