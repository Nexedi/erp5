request = context.REQUEST
now = DateTime()
expire_timeout_days = 1
session_id = request.get('session_id', None)
if session_id is None or not session_id.startswith("erp5zuite"):
  ## first call so generate session_id and send back via cookie
  session_id = 'erp5zuite_' + context.REQUEST.other['AUTHENTICATED_USER'].getIdOrUserName()
  request.RESPONSE.setCookie('erp5_session_id', session_id, expires=(now +expire_timeout_days).fCommon(), path='/')
  
session = context.portal_sessions[session_id]
if 'tempfolder' not in session or session['tempfolder'] == '':
  session['tempfolder'] = context.Zuite_createTempFolder() + '/'

return session['tempfolder'] + str(context.portal_ids.generateNewId(id_generator='zuite', id_group=context.getId(), default=1)) + '.png'
