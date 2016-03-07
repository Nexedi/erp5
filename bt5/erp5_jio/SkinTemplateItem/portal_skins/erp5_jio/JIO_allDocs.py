import json
#from Products.ERP5Type.Log import log
# use JSON.parse as json.loads and JSON.stringify as json.dumps

context.REQUEST.response.setHeader("Access-Control-Allow-Origin", "*")

jio = context.JIO_class()

try: option = jio.jsonUtf8Loads(context.REQUEST.form["option"])
except KeyError:
  option = {}

try: mode = str(context.REQUEST.form["mode"])
except KeyError: mode = "generic"
jio.setMode(mode)

metadata_json = jio.getAllDocuments(option)

return jio.sendSuccess(metadata_json)

# document_list = context.portal_catalog(portal_type="Web Page")

# return jio.sendSuccess(jio.getAllDocsFromDocumentList(document_list, include_docs=option.get("include_docs")))
