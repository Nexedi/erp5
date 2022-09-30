from Products.CMFActivity.ActiveResult import ActiveResult

portal = context.getPortalObject()
promise_url = portal.getPromiseParameter('external_service', 'kumofs_url')

if promise_url is None:
  return

plugin = portal.portal_memcached.restrictedTraverse("persistent_memcached_plugin", None)
if plugin is None:
  return

url = "memcached://%s/" % plugin.getUrlString()

active_result = ActiveResult()

if promise_url != url:
  severity = 1
  summary = "Kumofs not configured as expected"
else:
  severity = 0
  summary = "Nothing to do."

active_result.edit(
  summary=summary,
  severity=severity,
  detail="Expect %s\nGot %s" % (promise_url, url))

context.newActiveProcess().postResult(active_result)
