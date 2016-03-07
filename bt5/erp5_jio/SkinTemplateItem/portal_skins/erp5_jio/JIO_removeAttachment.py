import json
#from Products.ERP5Type.Log import log
# use JSON.parse as json.loads and JSON.stringify as json.dumps

context.REQUEST.response.setHeader("Access-Control-Allow-Origin", "*")

jio = context.JIO_class()

try: doc = jio.jsonUtf8Loads(context.REQUEST.form["doc"])
except KeyError:
  return jio.sendError(jio.createBadRequestDict("Cannot get document", "No document information received"))

try: mode = str(context.REQUEST.form["mode"])
except KeyError: mode = "generic"
jio.setMode(mode)

try:
  response_json = jio.removeAttachment(doc)
except (ValueError, TypeError) as e:
  return jio.sendError(jio.createConflictDict("Cannot remove attachment", str(e)))
except LookupError as e:
  return jio.sendError(jio.createNotFoundDict("Cannot remove attachment", str(e)))

return jio.sendSuccess(response_json)
