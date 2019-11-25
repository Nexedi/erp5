from ZTUtils import make_query

obj = brain.getObject()
if obj is None:
  return None

url = context.absolute_url()
method = context.getReportMethodId('Alarm_viewReport')
kw = { 'active_process' : 'portal_activities/%s' % obj.id,
       'reset' : '1', 
     }

return url + '/' + method + '?' + make_query(kw)
