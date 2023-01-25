"""
  Get session data
"""

request = context.REQUEST
now = DateTime()
expire_timeout_days = 90
session_id = request.get('session_id', None)
if session_id is None:
  ## first call so generate session_id and send back via cookie
  session_id = 'erp5runmydocs_' + context.REQUEST.other['AUTHENTICATED_USER'].getIdOrUserName()
  request.RESPONSE.setCookie('erp5_session_id',
                             session_id,
                             expires=(now +expire_timeout_days).fCommon(), path='/')

if attribute is None or not attribute:
  return context.portal_sessions[session_id]
else:
  return context.portal_sessions[session_id][attribute]
