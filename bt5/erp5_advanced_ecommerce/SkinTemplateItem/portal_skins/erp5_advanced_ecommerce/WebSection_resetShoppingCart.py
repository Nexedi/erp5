"""
  Reset section by removing shopping cart
"""
from DateTime import DateTime

request = context.REQUEST
if session_id is None:
  session_id = request.get('session_id', None)

request.RESPONSE.expireCookie('session_id')
return context.portal_sessions.manage_delObjects(session_id)
