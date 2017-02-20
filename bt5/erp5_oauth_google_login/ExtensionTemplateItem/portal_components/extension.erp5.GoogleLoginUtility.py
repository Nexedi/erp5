import httplib
import urllib
import json
import httplib2
import apiclient.discovery
import oauth2client.client
import socket
from zLOG import LOG, ERROR

def getAccessTokenFromCode(self, code, redirect_uri):
  connection_kw = {'host': 'accounts.google.com', 'timeout': 30}
  connection = httplib.HTTPSConnection(**connection_kw)
  data = {
      'client_id': self.portal_preferences.getPreferredGoogleClientId(),
      'client_secret': self.portal_preferences.getPreferredGoogleSecretKey(),
      'grant_type': 'authorization_code',
      'redirect_uri': redirect_uri,
      'code': code
      }
  data = urllib.urlencode(data)
  headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "*/*"
  }
  connection.request('POST', '/o/oauth2/token', data, headers)
  response = connection.getresponse()
  status = response.status
  if status != 200:
    return status, None

  try:
    body = json.loads(response.read())
  except Exception, error_str:
    return status, {"error": error_str}

  try:
    return status, body
  except Exception:
    return status, None

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