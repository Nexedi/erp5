import json
#from Products.ERP5Type.Log import log
# use JSON.parse as json.loads and JSON.stringify as json.dumps

context.REQUEST.response.setHeader("Access-Control-Allow-Origin", "*")

# dataType "json"
# when sending -> [{"name": stringA, "value": stringB}]
# context.REQUEST.form <- {stringA: stringB}

jio = context.JIO_class()

try: doc = jio.jsonUtf8Loads(context.REQUEST.form["doc"])
except KeyError:
  return jio.sendError(jio.createBadRequestDict("Cannot get document", "No document information received"))

try: mode = str(context.REQUEST.form["mode"])
except KeyError: mode = "generic"
jio.setMode(mode)

try:
  attachment_data = jio.getDocumentAttachment(doc)
except ValueError as e:
  return jio.sendError(jio.createConflictDict("Cannot get attachment", str(e)))
except LookupError as e:
  return jio.sendError(jio.createNotFoundDict("Cannot get attachment", str(e)))

return jio.sendSuccess(attachment_data)
