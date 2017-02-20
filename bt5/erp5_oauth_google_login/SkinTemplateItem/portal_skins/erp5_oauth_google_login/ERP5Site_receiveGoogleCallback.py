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
  status, response_dict = context.ERP5Site_getAccessTokenFromCode(
    code,
    "{0}/ERP5Site_receiveGoogleCallback".format(portal.absolute_url()))
  if status != 200 and response_dict is not None:
    return handleError(
      " ".join(["%s : %s" % (k,v) for k,v in response_dict.iteritems()]))
  if response_dict is not None:
    access_token = response_dict['access_token'].encode('utf-8')
    response_dict['login'] = context.ERP5Site_getGoogleUserId(access_token)
    hash_str = context.Base_getHMAC(access_token, access_token)
    context.REQUEST.RESPONSE.setCookie('__ac_google_hash', hash_str, path='/')
    context.Base_setBearerToken(hash_str,
                                response_dict,
                                "google_server_auth_token_cache_factory")
    return context.REQUEST.RESPONSE.redirect(
      context.REQUEST.get("came_from") or portal.absolute_url())

return handleError('')
