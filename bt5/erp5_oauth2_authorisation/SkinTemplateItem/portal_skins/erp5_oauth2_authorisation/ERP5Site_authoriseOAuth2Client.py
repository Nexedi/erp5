# Proxy Role: Auditor, to access connector document
"""
Mutate REQUEST to call standard OAuth2 /authorize endpoint from an ERP5 Form in dialog mode.
"""
import json
import six
from erp5.component.document.OAuth2AuthorisationServerConnector import substituteRequest
from Products.ERP5Type.Utils import unicode2str
# XXX: Accessing REQUEST from acquisition is bad. But Base_callDialogMethod
# does not propagate the request cleanly, so no other way so far.
REQUEST = context.REQUEST

form = {
  unicode2str(key): unicode2str(value)
  for key, value in six.iteritems(json.loads(request_info_json))
}
if scope_list:
  form['scopes'] = ' '.join(scope_list)
portal = context.getPortalObject()
from pprint import pprint
pprint(('substituteRequest form', substituteRequest))
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
