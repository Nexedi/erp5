from Products.CMFActivity.ActiveResult import ActiveResult

portal = context.getPortalObject()
promise_url = portal.getPromiseParameter('external_service', 'memcached_url')

if promise_url is None:
  return

plugin = portal.portal_memcached.default_memcached_plugin

url = "memcached://%s/" % plugin.getUrlString()

active_result = ActiveResult()

if promise_url != url:
  severity = 1
  summary = "Memcached not configured as expected"
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
