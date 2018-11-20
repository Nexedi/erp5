import time

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
  response_dict = context.ERP5Site_getAccessTokenFromCode(
    code,
    "{0}/ERP5Site_receiveGoogleCallback".format(context.absolute_url()))
  if response_dict is not None:
    access_token = response_dict['access_token'].encode('utf-8')
    hash_str = context.Base_getHMAC(access_token, access_token)
    context.setAuthCookie(response, '__ac_google_hash', hash_str)
    # store timestamp in second since the epoch in UTC is enough
    response_dict["response_timestamp"] = time.time()
    context.Base_setBearerToken(hash_str,
                                response_dict,
                                "google_server_auth_token_cache_factory")
    user_dict = context.ERP5Site_getGoogleUserEntry(access_token)
    user_reference = user_dict["email"]
    context.Base_setBearerToken(access_token,
                                {"reference": user_reference},
                                "google_server_auth_token_cache_factory")
    method = getattr(context, "ERP5Site_createGoogleUserToOAuth", None)
    if method is not None:
      method(user_reference, user_dict)
    return response.redirect(request.get("came_from") or context.absolute_url())

return handleError('')
