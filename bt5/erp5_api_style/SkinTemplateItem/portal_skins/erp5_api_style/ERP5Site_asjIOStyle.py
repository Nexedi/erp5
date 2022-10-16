# an external script is need to extract content from body: REQUEST.get('BODY')
mode = mode or context.REQUEST.form.get("mode", "get")
text_content = text_content or context.REQUEST.form.get("text_content", "")
document_id = document_id or context.REQUEST.form.get("document_id", "")
import json
portal = context.getPortalObject()

response = container.REQUEST.RESPONSE

# XXX Hardcoded, to be removed
def logError(e, error_name="", error_code=400, detail_list=None):
  return portal.ERP5Site_logApiErrorAndReturn(
    error_code=error_code,
    error_message=e,
    error_name=error_name,
    detail_list=detail_list,
  )

def getCorrespondingActionAndReturn(traversed_document, action_id, text_data, list_error=False):
  return traversed_document.getTypeInfo().getDefaultViewFor(
    traversed_document, view=action_id
  )(text_data, list_error=list_error)

# https://stackoverflow.com/a/33571117
def _byteify(data, ignore_dicts = False):
  if isinstance(data, str):
    return data

  # if this is a list of values, return list of byteified values
  if isinstance(data, list):
    return [ _byteify(item, ignore_dicts=True) for item in data ]
  # if this is a dictionary, return dictionary of byteified keys and values
  # but only if we haven't already byteified it
  if isinstance(data, dict) and not ignore_dicts:
    return {
      _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
      for key, value in data.items() # changed to .items() for python 2.7/3
    }

  # python 3 compatible duck-typing
  # if this is a unicode string, return its string representation
  if str(type(data)) == "<type 'unicode'>":
    return data.encode('utf-8')

  # if it's anything else, return it in its original form
  return data

def json_loads_byteified(json_text):
  return _byteify(
    json.loads(json_text, object_hook=_byteify),
    ignore_dicts=True
  )


mode_dict = {
  "put": "configuration_put_action_type",
  "get": "configuration_get_action_type",
  "post": "configuration_post_action_type",
  "allDocs": "configuration_alldocs_action_type",
}

if mode not in mode_dict:
  return "Used Mode is not defined in the mode list %s" % list(mode_dict.keys())

# Check JSON Form
try:
  data = json_loads_byteified(text_content)
except BaseException as e:
  return logError(str(e), error_name="API-JSON-INVALID-JSON")
if not isinstance(data, dict):
  return logError("Did not received a JSON Object", error_name="API-JSON-NOT-JSON-OBJECT")

# If get or put, valid Id is expected
if mode in ("get", "put"):
  if not document_id:
    try:
      document_id = data["id"]
    except KeyError:
      return logError("Cannot find id property", error_name="API-JSON-NO-ID-PROPERTY")
    except TypeError:
      return logError("Did not received a JSON Object", error_name="API-JSON-NOT-JSON-OBJECT")
  try:
    document = portal.restrictedTraverse(str(document_id))
  except KeyError:
    return logError("Document has not been found", error_name="API-DOCUMENT-NOT-FOUND", error_code=404)
else:
  document = context

result_list = []
error_dict = {}
match = False

# Get matching actions for current mode
action_type = context.getLayoutProperty(mode_dict[mode])
erp5_action_dict = portal.Base_filterDuplicateActions(
    portal.portal_actions.listFilteredActionsFor(document))

# Try to find an action matching the text_content
for erp5_action_key in erp5_action_dict.keys():
  for view_action in erp5_action_dict[erp5_action_key]:
    if (action_type == view_action['category']):
      try:
        result = getCorrespondingActionAndReturn(
          document, view_action['id'], data, list_error=True
        )
        match = True
        # If an object is created, 201 code is exptected
        if mode == "post":
          if response.getStatus() == 200:
            response.setStatus(201)
        # If not search, job is done and we can return result
        if mode != "allDocs":
          return result
        result_list += result
      except ValueError as e:
        try:
          error_dict.update(json.loads(str(e)))
        except ValueError:
          raise ValueError(e)

# Return error if no action found or text content did not match
if not match:
  error_kw = {
    "error_name":"API-NO-ACTION-FOUND"
  }
  if mode in ("put", "get"):
    error_message = "Unauthorized: No action with category %s found for %s" % (
      action_type,
      document.getRelativeUrl()
    )
  else:
    error_message = "Data did not validate against interface schemas"
    if error_dict:
      error_kw["detail_list"] = sorted(error_dict.items())
  return logError(error_message, **error_kw)

if mode == "allDocs":
  return json.dumps({
    "$schema": "alldocs-response-schema.json",
    "result_list":result_list
    },
    indent=2
  )

raise ValueError("Unreachable code reached")
