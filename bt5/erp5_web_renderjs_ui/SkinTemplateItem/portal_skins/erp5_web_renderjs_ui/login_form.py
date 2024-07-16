# Short-circuit old (pre-oauth2) web-mode "login_form"s
from six.moves.urllib.parse import urlencode
web_section_value = context.getWebSectionValue()
client_id = context.getPortalObject().ERP5Site_getOAuth2ClientConnectorClientId(
  connector_id=(
    None
    if web_section_value is None else
    web_section_value.getLayoutProperty('configuration_oauth2_client_connector_id', default=None)
  ),
)
if client_id is None:
  # BBB: OAuth2 is not enabled
  return context.login_once_form(has_oauth2=False)
if came_from:
  # Make the user go through WebSite_login after authentication, so it does its url de-templatification magic
  came_from = context.absolute_url() + '/WebSite_login?' + urlencode((('came_from', came_from), ))
return context.skinSuper('erp5_web_renderjs_ui', script.id)(
  REQUEST=REQUEST,
  RESPONSE=RESPONSE,
  client_id=client_id,
  came_from=came_from,
  portal_status_message=portal_status_message,
)
