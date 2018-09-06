import time

def handleError(error):
  context.Base_redirect(
    'login_form',
    keep_items={"portal_status_message":
                context.Base_translateString(
                  "There was problem with Facebook login: ${error}. Please try again later.",
                  mapping={"error": error})
               })

if error is not None:
  return handleError(error)

elif code is not None:
  portal = context.getPortalObject()
  response_dict = context.ERP5Site_getFacebookAccessTokenFromCode(
    code,
    "{0}/ERP5Site_callbackFacebookLogin".format(context.absolute_url()))
  if response_dict is not None:
    access_token = response_dict['access_token'].encode('utf-8')
    hash_str = context.Base_getHMAC(access_token, access_token)

    context.REQUEST.RESPONSE.setCookie('__ac_facebook_hash', hash_str, path='/')
    # store timestamp in second since the epoch in UTC is enough
    response_dict["response_timestamp"] = time.time()

    context.Base_setBearerToken(hash_str,
                                response_dict,
                                "facebook_server_auth_token_cache_factory")

    user_dict = context.ERP5Site_getFacebookUserEntry(access_token)
    user_reference = user_dict["reference"]

    context.Base_setBearerToken(access_token,
                                {"reference": user_reference},
                                "facebook_server_auth_token_cache_factory")

    method = getattr(context, "ERP5Site_createFacebookUserToOAuth", None)
    if method is not None:
      method(user_reference, user_dict)

    # We intentionnally add this # to the URL because otherwise Facebook adds
    # #_=_ and it breaks renderjs hash based URL routing.
    # https://developers.facebook.com/support/bugs/318390728250352/?disable_redirect=0
    # https://stackoverflow.com/questions/7131909/facebook-callback-appends-to-return-url/33257076#33257076
    # https://lab.nexedi.com/nexedi/erp5/merge_requests/417#note_64365
    came_from = context.REQUEST.get("came_from",  portal.absolute_url() + "#")
    return context.REQUEST.RESPONSE.redirect(came_from)

return handleError('')
