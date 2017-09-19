"""
   This script factorises code required to redirect to the appropriate
   page from a script. It should probably be extended, reviewed and documented
   so that less code is copied and pasted in dialog scripts.

   TODO: improve API and extensively document. ERP5Site_redirect may 
   be redundant.
"""
from ZTUtils import make_query
import json

request_form = context.REQUEST.form
request_form.update(kw)
request_form = context.ERP5Site_filterParameterList(request_form)
request_form.update(keep_items)

if form_id == 'view':
  redirect_url = "%s/ERP5Document_getHateoas" % context.absolute_url()
else:
  redirect_url = '%s/%s' % (context.absolute_url(), form_id)

parameters = make_query(dict([(k, v) for k, v in request_form.items() if k and v is not None]))
if len(parameters):
  if '?' in redirect_url:
    separator = '&'
  else:
    separator = '?'
  redirect_url = '%s%s%s' % (redirect_url, separator, parameters)


# XXX Allow CORS
response = context.REQUEST.RESPONSE
context.Base_prepareCorsResponse(RESPONSE=response)
# http://en.wikipedia.org/wiki/Post/Redirect/Get
response.setStatus(201)
response.setHeader("X-Location", "urn:jio:get:%s" % context.getRelativeUrl())
# be explicit with the reponse content type because in case of reports - they
# can be in text/plain, application/pdf ... so the RJS form needs to know what
# is going exactly on. ERP5Document_getHateoas returns application/hal+json
# therefor we don't need to be afraid of clashes
response.setHeader("Content-type", "application/json; charset=utf-8")

result_dict = {
  'portal_status_message': "%s" % keep_items.pop("portal_status_message", ""),
  '_links': {
    "self": {
      # XXX Include query parameters
      "href": context.Base_getRequestUrl()
    }
  }
}
return json.dumps(result_dict, indent=2)
