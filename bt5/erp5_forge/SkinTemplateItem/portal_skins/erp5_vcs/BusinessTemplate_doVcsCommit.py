kw = {}
request = container.REQUEST
for k in 'added', 'modified', 'removed':
  file_list = request.get(k, ())
  # XXX: ERP5VCS_doCreateJavaScriptStatus should send lists
  if isinstance(file_list, basestring):
    file_list = file_list != 'none' and filter(None, file_list.split(',')) or ()
  kw[k] = file_list

changelog = request.get('changelog', '')
if not changelog.strip():
  from Products.ERP5Type.Message import translateString
  error_msg = "Please set a ChangeLog message."
  request.set('portal_status_message', translateString(error_msg))
  request.set('cancel_url', context.absolute_url() +
    '/BusinessTemplate_viewVcsStatus?do_extract:int=0'
    '&portal_status_message=Commit%20cancelled.')
  return context.asContext(**kw).BusinessTemplate_viewVcsChangelog()

try:
  return context.getVcsTool().commit(changelog, **kw)
except Exception, error:
  return context.BusinessTemplate_handleException(error, script.id)
