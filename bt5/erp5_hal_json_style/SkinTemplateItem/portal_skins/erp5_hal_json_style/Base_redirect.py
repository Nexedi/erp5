"""UI Script to redirect the user to `context` with optional custom view `form_id`.

:param keep_items: is used mainly to pass "portal_status_message" to be showed to the user
                   the new UI supports "portal_status_level" with values "success" or "error"
"""
from zExceptions import Redirect
import json

if keep_items is None:
  keep_items = {}

request_form = context.REQUEST.form
previous_form_id = request_form.get('form_id', '')
request_form.update(kw)
request_form = context.ERP5Site_filterParameterList(request_form)
request_form.update(keep_items)


portal_status_level = keep_items.pop("portal_status_level", "success")
if portal_status_level in ("warning", "error", "fatal"):
  portal_status_level = "error"
if portal_status_level in ("info", "debug", "success"):
  portal_status_level = "success"


result_dict = {
  'portal_status_message': "%s" % keep_items.pop("portal_status_message", ""),
  'portal_status_level': "%s" % portal_status_level,
  '_links': {
    "self": {
      # XXX Include query parameters
      "href": context.Base_getRequestUrl()
    }
  }
}

# Put the web site in the acquisition context
# this occurs when doing a .getObject from the catalog for example
if (not context.isWebMode()) and (context.REQUEST.get('web_section_value', None) is not None):
  portal = context.getPortalObject()
  web_section = portal.restrictedTraverse("/".join(context.REQUEST['web_section_value']))
  context = web_section.restrictedTraverse(context.getRelativeUrl())

# form_id = 'view' means use default document view. Let the JS handle it
# In case of dialog submit, if redirecting to the original form, let the JS handle the navigation history
if (form_id not in [None, 'Base_viewFakePythonScriptActionForm', 'Base_viewFakeJumpForm']) and \
   ((form_id != 'view') or (keep_items)) and \
   (form_id != previous_form_id) and \
   (not form_id.startswith('http')) and \
   (context.isWebMode()):
  # Calculate the new view URL
  result_dict['_links']['location'] = {
    'href': context.ERP5Document_getHateoas(
      mode='url_generator',
      relative_url=context.getRelativeUrl(),
      view=form_id,
      keep_items=keep_items
    )
  }

# XXX Allow CORS
response = context.REQUEST.RESPONSE
context.Base_prepareCorsResponse(RESPONSE=response)

response.setHeader("X-Location", "urn:jio:get:%s" % context.getRelativeUrl())
# be explicit with the reponse content type because in case of reports - they
# can be in text/plain, application/pdf ... so the RJS form needs to know what
# is going exactly on. ERP5Document_getHateoas returns application/hal+json
# therefor we don't need to be afraid of clashes
response.setHeader("Content-type", "application/json; charset=utf-8")

result = json.dumps(result_dict, indent=2)
# http://en.wikipedia.org/wiki/Post/Redirect/Get
response.setStatus(201, lock=True)
if abort_transaction:
  response.setBody(result, lock=True)
  raise Redirect('')
return result
