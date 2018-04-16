"""
Return HTTP Redirect with message to be displayed.

Unfortunately XHTML UI cannot distinguish between error levels - everything is a message so we ignore
most of the parameters here.

:param message: {str}
:param level: {str | int} use ERP5Type.Log levels or simply strings like "info", "warning", or "error"
"""

return context.Base_redirect(
  keep_items={"portal_status_message": str(message)})
