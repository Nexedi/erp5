import six
import time

request = container.REQUEST
response = request.RESPONSE

cache_factory = "openid_connect_server_auth_token_cache_factory"

def handleError(error, error_description="", state=None):
  if state:
    context.Base_setBearerToken(state, None, cache_factory)
  return context.getWebSiteValue().Base_redirect(
    'login_form',
    keep_items={"portal_status_message":
                context.Base_translateString(
                  "There was problem with your login: ${error} ${error_description}. Please contact your administrator.",
                  mapping={"error": error, "error_description": error_description})
               })


state = state or request.form["state"]
if not state:
  raise ValueError("Missing state value")

session = context.Base_getBearerToken(state, cache_factory)
if not session:
  raise ValueError("Unknown state Value")
error = error or request.form.get("error", None)
error_description = error_description or request.form.get("error_description", None)
code = code or request.form.get("code", None)

if error is not None:
  return handleError(error, error_description, state)

elif code is not None:
  response_dict = context.ERP5Site_getOpenIdConnectAccessTokenFromCode(
    context.REQUEST.environ['QUERY_STRING'],
    "{0}/hateoas/connection/oid_auth".format(context.absolute_url())
  )
  if response_dict is not None:
    """
    Here is an example of correct response dict:
    {
      'access_token': u'XXXX0koYI5hASXZaExeYsGlqz1bSIcGyEg',
      'token_type': u'Bearer',
      'expires_in': 3599,
      'refresh_token': u'XXXXXXQocR4zlxQUdrit5sZ1FutZcece9'
    }
    """
    if "error" in response_dict:
      return handleError(response_dict.get('error'), response_dict.get('error_description'), state)
    access_token = response_dict['access_token']
    if six.PY2:
      access_token = access_token.encode('utf-8')
    hash_str = context.Base_getHMAC(access_token.encode('utf-8'), access_token.encode('utf-8'))
    context.setAuthCookie(response, '__ac_openidconnect_hash', hash_str)
    # store timestamp in second since the epoch in UTC is enough
    response_dict["response_timestamp"] = time.time()
    context.Base_setBearerToken(hash_str,
                                response_dict,
                                "openid_connect_server_auth_token_cache_factory")
    user_dict = context.ERP5Site_getOpenIdUserEntry(token=access_token)
    user_reference = user_dict["sub"]
    if six.PY2:
      user_reference = user_reference.encode('utf-8')
    context.Base_setBearerToken(access_token,
                                {"reference": user_reference},
                                "openid_connect_server_auth_token_cache_factory")
    # XXX for ERP5JS web sites without a rewrite rule, we make sure there's a trailing /
    web_site_value = context.getWebSiteValue() or context
    person_relative_url = context.ERP5Site_getPersonFromOpenIdLogin(user_reference)
    if not person_relative_url:
      method = getattr(context, "ERP5Site_createOpenIdConnectUserToOAuth", None)
      if method is not None:
        method(user_reference, user_dict)
        # XXX CLN Hackish redirect
        return web_site_value.Base_redirect('hateoas/connection/login_form', keep_items={
          "portal_status_message": "Your user is being created, please retry clicking on 'Login with OpenId Connect' in 1 minute."
        })

    came_from = web_site_value.absolute_url() + "/#!login?n.me=%s" % person_relative_url

    response.setHeader('Location', came_from)
    response.setStatus(303)
else:
  return handleError('')
