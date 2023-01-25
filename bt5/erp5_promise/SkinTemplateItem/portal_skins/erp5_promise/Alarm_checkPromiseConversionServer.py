from Products.CMFActivity.ActiveResult import ActiveResult
import json

portal = context.getPortalObject()
portal_preferences = portal.portal_preferences
promise_url_list_string = portal.getPromiseParameter('external_service', 'cloudooo_url_list')
promise_url_list = json.loads(promise_url_list_string.replace('\'', '\"'))

if promise_url_list is None:
  return

url_list = portal_preferences.getPreferredDocumentConversionServerUrlList()

active_result = ActiveResult()

if promise_url_list != url_list:
  severity = 1
  summary = "Conversion Server not configured as expected"
  detail = "Expect %s\nGot %s" % (promise_url_list, url_list)
else:
  severity = 0
  summary = "Nothing to do."
  detail = ""

active_result.edit(
  summary=summary,
  severity=severity,
  detail=detail)


context.newActiveProcess().postResult(active_result)
