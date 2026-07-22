# Proxy Role: Auditor to get access to the connector
"""
Retry calling /authorize using the values in came_from
(which a previous call to /authorize generated, and is not a traditional came_from).
"""
from six.moves.urllib.parse import parse_qsl, urlsplit
from erp5.component.document.OAuth2AuthorisationServerConnector import substituteRequest
if not context.ERP5Site_isOAuth2CameFrom(came_from):
  # came_from is broken, there is no way to call /authorize , so escape to wherever.
  context.Base_redirect()
  return
parsed_came_from = urlsplit(came_from)
query_list = [
  (key, value)
  for key, value in parse_qsl(parsed_came_from.query)
  if key != 'portal_status_message'
]
if portal_status_message is not None:
  query_list.append(('portal_status_message', portal_status_message))
with substituteRequest(
  context=context,
  request=REQUEST,
  method='GET',
  query_list=query_list,
) as inner_request:
  inner_request.environ['CONTENT_TYPE'] = ''
  # Turn the ZODB path from came_from into a relative URL and base it context (and not portal) to
  # work as expected from within Web Sites without Virtual Host Monster relocating them above portal.
  return context.restrictedTraverse(parsed_came_from.path.lstrip('/')).authorize(
    REQUEST=inner_request,
    RESPONSE=inner_request.RESPONSE,
  )
