import json
import oauth2client.client
from Products.ERP5Security.ERP5ExternalOauth2ExtractionPlugin import getGoogleUserEntry
from zExceptions import Unauthorized


SCOPE_LIST = ['https://www.googleapis.com/auth/userinfo.profile',
              'https://www.googleapis.com/auth/userinfo.email']


def _getGoogleClientIdAndSecretKey(portal, reference="default"):
  """Returns google client id and secret key.

  Internal function.
  """
  result_list = unrestrictedSearchGoogleConnector(portal, reference=reference)
  assert result_list, "Google Connector not found"
  if len(result_list) == 2:
    raise ValueError("Impossible to select one Google Connector")

  google_connector = result_list[0].getObject()
  return google_connector.getClientId(), google_connector.getSecretKey()

def redirectToGoogleLoginPage(self):
  client_id, secret_key = _getGoogleClientIdAndSecretKey(self.getPortalObject())
  flow = oauth2client.client.OAuth2WebServerFlow(
    client_id=client_id,
    client_secret=secret_key,
    scope=SCOPE_LIST,
    redirect_uri="{0}/ERP5Site_receiveGoogleCallback".format(self.absolute_url()),
    access_type="offline",
    prompt="consent",
    include_granted_scopes="true")
  self.REQUEST.RESPONSE.redirect(flow.step1_get_authorize_url())

def getAccessTokenFromCode(self, code, redirect_uri):
  client_id, secret_key = _getGoogleClientIdAndSecretKey(self.getPortalObject())
  flow = oauth2client.client.OAuth2WebServerFlow(
    client_id=client_id,
    client_secret=secret_key,
    scope=SCOPE_LIST,
    redirect_uri=redirect_uri,
    access_type="offline",
    include_granted_scopes="true")
  credential = flow.step2_exchange(code)
  credential_data = json.loads(credential.to_json())
  return credential_data

def unrestrictedSearchGoogleConnector(self, reference="default"):
  return self.getPortalObject().portal_catalog.unrestrictedSearchResults(
            portal_type="Google Connector",
            reference=reference,
            validation_state="validated",
            limit=2)

def unrestrictedSearchGoogleLogin(self, login, REQUEST=None):
  if REQUEST is not None:
    raise Unauthorized

  return self.getPortalObject().portal_catalog.unrestrictedSearchResults(
    portal_type="Google Login",
    reference=login,
    validation_state="validated", limit=1)

def getUserEntry(access_token):
  return getGoogleUserEntry(access_token)