import facebook
from ZTUtils import make_query

from Products.ERP5Security.ERP5ExternalOauth2ExtractionPlugin import getFacebookUserEntry
from zExceptions import Unauthorized

def _getFacebookClientIdAndSecretKey(portal, reference="default"):
  """Returns facebook client id and secret key.

  Internal function.
  """
  facebook_connector = unrestrictedSearchFacebookConnector(portal, reference=reference)
  assert facebook_connector, "Facebook Connector not found"
  return facebook_connector.getClientId(), facebook_connector.getSecretKey()

def redirectToFacebookLoginPage(self, came_from=None):
  client_id, _ = _getFacebookClientIdAndSecretKey(self.getPortalObject())
  query = make_query({
    # Call at he context of the appropriate web_service.
    'client_id': client_id,
    'redirect_uri': "{0}/ERP5Site_callbackFacebookLogin".format(came_from or self.absolute_url()),
    'scope': 'email'
  })

  return self.REQUEST.RESPONSE.redirect("https://www.facebook.com/v2.10/dialog/oauth?{}".format(query))

def getAccessTokenFromCode(self, code, redirect_uri):
  client_id, secret_key = _getFacebookClientIdAndSecretKey(self.getPortalObject())
  return facebook.GraphAPI(version="2.7").get_access_token_from_code(
    code=code, redirect_uri=redirect_uri,
    app_id=client_id, app_secret=secret_key)

def unrestrictedSearchFacebookConnector(self, reference="default"):
  result_list = self.getPortalObject().portal_catalog.unrestrictedSearchResults(
            portal_type="Facebook Connector",
            reference=reference,
            validation_state="validated",
            limit=2)
  if not result_list:
    return

  if len(result_list) != 1:
    raise ValueError('Impossible to select Facebook Connector')

  return result_list[0].getObject()

def unrestrictedSearchFacebookLogin(self, login, REQUEST=None):
  if REQUEST is not None:
    raise Unauthorized

  return self.getPortalObject().portal_catalog.unrestrictedSearchResults(
    portal_type="Facebook Login",
    reference=login,
    validation_state="validated", limit=1)

def getUserEntry(token):
  return getFacebookUserEntry(token)
