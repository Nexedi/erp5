from ZTUtils import make_query
from Products.PythonScripts.standard import html_quote


portal = context.getPortalObject()

translateString = portal.Base_translateString
request = portal.REQUEST

query_kw = {
    'portal_status_message': translateString('Version from ${time}', mapping={'time': request['time']}),
  }
ignore_layout = request.get('ignore_layout')
if ignore_layout is not None:
  query_kw['ignore_layout'] = ignore_layout

return '%s/HistoricalRevisions/%s?%s' % (
  context.absolute_url(),
  html_quote(request['serial']),
  make_query(query_kw)
)
