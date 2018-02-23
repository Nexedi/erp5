"""
Script to return json for response header while displying failure
"""
import json

response = request.RESPONSE if request is not None else context.REQUEST.RESPONSE
# Set the response code and header info in the response
response.setStatus(int(response_code))
response.setHeader("Content-type", "application/json; charset=utf-8")
return json.dumps({"portal_status_message": str(message)})
