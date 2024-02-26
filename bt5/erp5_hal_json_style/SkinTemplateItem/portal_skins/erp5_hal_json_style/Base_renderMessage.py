"""
Return JSON with message to be displayed and set according HTTP STATUS for message severity.

:param message: {str}
:param level: {str | int} use ERP5Type.Log levels or simply strings like "info", "warning", or "error"
"""
import json
from erp5.component.module.Log import WARNING, ERROR
import six

if isinstance(level, (str, six.text_type)):
  if level.lower() == "error":
    response_code = 500
  elif level.lower().startswith("warn"):
    response_code = 403
  else:
    response_code = 200
else:
  if level == ERROR:
    response_code = 500
  elif level == WARNING:
    response_code = 403
  else:
    response_code = 200


response = request.RESPONSE if request is not None else context.REQUEST.RESPONSE
# Set the response code and header info in the response
response.setStatus(response_code)
response.setHeader("Content-type", "application/json; charset=utf-8")
return json.dumps({"portal_status_message": str(message)})
