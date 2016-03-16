from Products.CMFActivity.ActiveResult import ActiveResult

portal = context.getPortalObject()
portal_preferences = portal.portal_preferences
promise_url = portal.getPromiseParameter('external_service', 'cloudooo_url')

if promise_url is None:
  return

url = "cloudooo://%s:%s/" % (portal_preferences.getPreferredOoodocServerAddress(), portal_preferences.getPreferredOoodocServerPortNumber())

active_result = ActiveResult()

if promise_url != url:
  severity = 1
  summary = "Conversion Server not configured as expected"
  detail = "Expect %s\nGot %s" % (promise_url, url)
else:
  severity = 0
  summary = "Nothing to do."
  detail = ""

active_result.edit(
  summary=summary, 
  severity=severity, 
  detail=detail)


context.newActiveProcess().postResult(active_result)
