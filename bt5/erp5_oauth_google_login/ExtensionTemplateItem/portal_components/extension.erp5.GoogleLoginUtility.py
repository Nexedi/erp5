import json
import httplib2
import apiclient.discovery
import oauth2client.client
import socket
from zLOG import LOG, ERROR

SCOPE_LIST = ['https://www.googleapis.com/auth/userinfo.profile',
              'https://www.googleapis.com/auth/userinfo.email']

def redirectToGoogleLoginPage(self):
  portal = self.getPortalObject()
  flow = oauth2client.client.OAuth2WebServerFlow(
    client_id=portal.portal_preferences.getPreferredGoogleClientId(),
    client_secret=portal.portal_preferences.getPreferredGoogleSecretKey(),
    scope=SCOPE_LIST,
    redirect_uri="{0}/ERP5Site_receiveGoogleCallback".format(portal.absolute_url()),
    access_type="offline",
    prompt="consent",
    include_granted_scopes="true")
  self.REQUEST.RESPONSE.redirect(flow.step1_get_authorize_url())

def getAccessTokenFromCode(self, code, redirect_uri):
  portal = self.getPortalObject()
  flow = oauth2client.client.OAuth2WebServerFlow(
    client_id=portal.portal_preferences.getPreferredGoogleClientId(),
    client_secret=portal.portal_preferences.getPreferredGoogleSecretKey(),
    scope=SCOPE_LIST,
    redirect_uri=redirect_uri,
    access_type="offline",
    include_granted_scopes="true")
  credential = flow.step2_exchange(code)
  credential_data = json.loads(credential.to_json())
  return credential_data

def getUserId(access_token):
  timeout = socket.getdefaulttimeout()
  try:
    socket.setdefaulttimeout(10)
    http = oauth2client.client.AccessTokenCredentials(access_token, 'ERP5'
      ).authorize(httplib2.Http())
    service = apiclient.discovery.build("oauth2", "v1", http=http)
    google_entry = service.userinfo().get().execute()
  except Exception, error_str:
    google_entry = None
    LOG("GoogleLoginUtility", ERROR, error_str)
  finally:
    socket.setdefaulttimeout(timeout)

  if google_entry is not None:
    return google_entry['email'].encode('utf-8')
  return None