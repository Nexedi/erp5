from Products.ERP5Type.Utils import str2bytes
portal = context.getPortalObject()

request = container.REQUEST
response = request.RESPONSE

def handleError(error):
  context.Base_redirect(
    'login_form',
    keep_items={"portal_status_message":
                context.Base_translateString(
                  "There was problem with Google login: ${error}. Please try again later.",
                  mapping={"error": error})
               })

if error is not None:
  return handleError(error)

elif code is not None:
  google_connector = portal.ERP5Site_getDefaultGoogleConnector()
  response_dict = google_connector.getTokenFromCode(
    state=state,
    code=code,
    redirect_uri="{}/ERP5Site_receiveGoogleCallback".format(portal.absolute_url()),
  )

  access_token = str2bytes(response_dict['access_token'])
  hash_str = portal.Base_getHMAC(access_token, access_token)
  portal.setAuthCookie(response, '__ac_google_hash', hash_str)
  portal.Base_setBearerToken(
    hash_str,
    response_dict,
    "google_server_auth_token_cache_factory")

  # XXX for ERP5JS web sites without a rewrite rule, we make sure there's a trailing /
  return response.redirect(request.get("came_from") or context.absolute_url() + '/')

return handleError('')
