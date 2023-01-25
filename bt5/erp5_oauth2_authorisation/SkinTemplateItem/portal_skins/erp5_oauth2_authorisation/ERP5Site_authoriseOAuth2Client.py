# Proxy Role: Auditor, to access connector document
"""
Mutate REQUEST to call standard OAuth2 /authorize endpoint from an ERP5 Form in dialog mode.
"""
import json
import six
from erp5.component.document.OAuth2AuthorisationServerConnector import substituteRequest
# XXX: Accessing REQUEST from acquisition is bad. But Base_callDialogMethod
# does not propagate the request cleanly, so no other way so far.
REQUEST = context.REQUEST

form = {
  key.encode('utf-8'): value.encode('utf-8')
  for key, value in six.iteritems(json.loads(request_info_json))
}
if scope_list:
  form['scopes'] = ' '.join(scope_list)
portal = context.getPortalObject()
with substituteRequest(
  context=portal,
  request=REQUEST,
  method='POST',
  form=form,
) as inner_request:
  # XXX: hardcoded content-type
  inner_request.environ['HTTP_CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
  return portal.restrictedTraverse(server_connector_path).authorize(
    REQUEST=inner_request,
    RESPONSE=inner_request.RESPONSE,
  )
