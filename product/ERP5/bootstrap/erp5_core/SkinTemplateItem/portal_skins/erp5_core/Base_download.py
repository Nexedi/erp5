request = container.REQUEST
response = request.RESPONSE

from zExceptions import Unauthorized

try:
  return context.index_html(request, response, format=None, inline=inline)
except Unauthorized:
  msg = context.Base_translateString("You do not have enough permission for converting this document.")
  return context.Base_redirect(keep_items=dict(portal_status_message=msg))
