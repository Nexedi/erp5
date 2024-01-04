def checkTopLevel():
  portal = context.getPortalObject()
  for o in portal.objectValues():
    error_list = o.checkFolderHandler(fixit=fixit)
    if len(error_list):
      portal.portal_activities.activate(active_process=active_process, priority=2) \
      .Base_makeActiveResult(title=o.absolute_url_path(), error_list=error_list)

if 'tag' not in kwargs:
  kwargs['tag'] = []

kwargs.update(
    method_id='checkFolderHandler',
    method_kw={'fixit': fixit},
)

if context.getPortalType() == 'Alarm':
  active_process = context.newActiveProcess().getPath()
  ERP5Site_checkDataWithScript = context.ERP5Site_checkDataWithScript
else:
  active_process = context.portal_activities.newActiveProcess().getPath()
  ERP5Site_checkDataWithScript = context.portal_activities.ERP5Site_checkDataWithScript
  print('Results will be saved to %s' % active_process)

checkTopLevel()
ERP5Site_checkDataWithScript(
  active_process=active_process,
  *args,
  **kwargs)

return printed
