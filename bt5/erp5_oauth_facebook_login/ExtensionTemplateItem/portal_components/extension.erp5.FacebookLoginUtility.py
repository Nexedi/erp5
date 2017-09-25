import facebook
from Products.ERP5Security.ERP5ExternalOauth2ExtractionPlugin import getFacebookUserEntry

def getAccessTokenFromCode(self, code, redirect_uri):
  return facebook.GraphAPI(version="2.7").get_access_token_from_code(
    code=code, redirect_uri=redirect_uri,
    app_id=self.getClientId(),
    app_secret=self.getSecretKey())

def getUserEntry(token):
  return getFacebookUserEntry(token)