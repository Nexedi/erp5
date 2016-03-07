from ZTUtils import make_query

object = brain.getObject()
if object is None:
  return None

url = context.absolute_url()
method = context.getReportMethodId('Alarm_viewReport')
kw = { 'active_process' : 'portal_activities/%s' % object.id,
       'reset' : '1', 
     }

return url + '/' + method + '?' + make_query(kw)
