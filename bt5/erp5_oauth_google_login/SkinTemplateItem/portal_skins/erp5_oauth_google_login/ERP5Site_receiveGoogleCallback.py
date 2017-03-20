import time

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
  portal = context.getPortalObject()
  response_dict = context.ERP5Site_getAccessTokenFromCode(
    code,
    "{0}/ERP5Site_receiveGoogleCallback".format(portal.absolute_url()))
  if response_dict is not None:
    access_token = response_dict['access_token'].encode('utf-8')
    hash_str = context.Base_getHMAC(access_token, access_token)
    context.REQUEST.RESPONSE.setCookie('__ac_google_hash', hash_str, path='/')
    # store timestamp in second since the epoch in UTC is enough
    response_dict["response_timestamp"] = time.time()
    context.Base_setBearerToken(hash_str,
                                response_dict,
                                "google_server_auth_token_cache_factory")
    context.Base_setBearerToken(access_token,
                                {"reference": context.ERP5Site_getGoogleUserId(access_token)},
                                "google_server_auth_token_cache_factory")
    return context.REQUEST.RESPONSE.redirect(
      context.REQUEST.get("came_from") or portal.absolute_url())

return handleError('')
