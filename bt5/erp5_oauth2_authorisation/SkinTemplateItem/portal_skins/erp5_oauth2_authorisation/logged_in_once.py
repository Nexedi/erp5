# Proxy Role: Auditor to get access to the connector
"""
Similar to logged_in, but user authentication will only last for current request if nothing else is done.
So came_from must be honoured within the current request, and not redirected to.
"""
from six.moves.urllib.parse import parse_qsl, urlsplit
from erp5.component.document.OAuth2AuthorisationServerConnector import substituteRequest
portal = context.getPortalObject()
if portal.portal_skins.updateSkinCookie():
  portal.setupCurrentSkin()

if REQUEST is None:
  # BBB: support Base_callDialogMethod-style caller
  REQUEST = context.REQUEST
  # Note: RESPONSE agument is present for API consistency purposes, but unused.
  # So do not bother setting it here.
environ = REQUEST.environ
if (
  environ['REQUEST_METHOD'] != 'POST' or
  environ.get('CONTENT_TYPE', '').split(';', 1)[0].rstrip() not in ('application/x-www-form-urlencoded', 'multipart/form-data') or
  environ['QUERY_STRING']
):
  # There may be foul play, so escape to wherever.
  context.Base_redirect()
  return
came_from = REQUEST.get('came_from')
if not came_from or not context.ERP5Site_isOAuth2CameFrom(came_from):
  # came_from is broken, there is no way to call authorize, so escape to wherever.
  context.Base_redirect()
  return
parsed_came_from = urlsplit(came_from)
# Turn the ZODB path from came_from into a relative URL and base it on context (and not portal) to
# work as expected from within Web Sites without Virtual Host Monster relocating them above portal.
connector_value = context.restrictedTraverse(parsed_came_from.path.lstrip('/'))
if (
  connector_value.getPortalType() != 'OAuth2 Authorisation Server Connector' or
  connector_value.getValidationState() != 'validated'
):
  context.Base_redirect()
  return
# Note: query string generation should not have produce any duplicate
# entries, so directly use to update form dict for code simplicity.
form = dict(parse_qsl(parsed_came_from.query))
login_retry_url = REQUEST.form.get('login_retry_url')
if login_retry_url is not None:
  form['login_retry_url'] = login_retry_url
from pprint import pprint
pprint(('logged_in_once substituteRequest', form))
with substituteRequest(
  context=portal,
  request=REQUEST,
  method='POST',
  form=form,
) as inner_request:
  # XXX: Zope request to oauthlib request compatibility layer (see document.erp5.OAuth2AuthorisationServerConnector)
  # only supports application/x-www-form-urlencoded, so force this content-type while accepting multipart/form-data input.
  # Non-basestring values are ignored, so it will ignore any posted file.
  inner_request.environ['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
  return connector_value.authorize(
    REQUEST=inner_request,
    RESPONSE=inner_request.RESPONSE,
  )
