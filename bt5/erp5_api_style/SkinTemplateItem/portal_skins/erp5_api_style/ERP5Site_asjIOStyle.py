# an external script is need to extract content from body: REQUEST.get('BODY')
mode = mode or context.REQUEST.form.get("mode", "get")
text_content = text_content or context.REQUEST.form.get("text_content", "")
document_id = document_id or context.REQUEST.form.get("document_id", "")
import json
portal = context.getPortalObject()

response = container.REQUEST.RESPONSE

# XXX Hardcoded, to be removed
def logError(e, error_name=""):
  return portal.ERP5Site_logApiErrorAndReturn(
    error_code=400,
    error_message=e,
    error_name=error_name,
  )

def getCorrespondingActionAndReturn(traversed_document, action_id, text_data, list_error=False):
  return traversed_document.getTypeInfo().getDefaultViewFor(
    traversed_document, view=action_id
  )(text_data, list_error=list_error)

def post(text_data):
  # Make sure we received JSON
  # XXX Add view on person/organisation to check all message received from them
  # Check JSON Data
  try:
    data = json.loads(text_data)
  except BaseException as e:
    return logError(str(e), error_name="API-JSON-INVALID-JSON")
  if not isinstance(data, dict):
    return logError("Did not received a JSON Object", error_name="API-JSON-NOT-JSON-OBJECT")
  # Make sure we have the portal_type property and it match one of the authorized portal types of the web section
  # XXX Needs to add constraint to check validity of property
  error_dict = {}
  post_entry_point_list = context.getLayoutProperty("configuration_post_action_type")
  erp5_action_dict = portal.Base_filterDuplicateActions(
      portal.portal_actions.listFilteredActionsFor(context))
  for erp5_action_key in erp5_action_dict.keys():
    for view_action in erp5_action_dict[erp5_action_key]:
      # Try to embed the form in the result
      if (post_entry_point_list == view_action['category']):
        try:
          search_result = getCorrespondingActionAndReturn(
            context, view_action['id'], text_data, list_error=True
          )
          result = search_result
          if response.getStatus() == 200:
            response.setStatus(201)
          return result
        except ValueError, e:
          context.log("failed %s" % view_action['id'])
          context.log(e)
          try:
            error_dict.update(json.loads(str(e)))
          except ValueError:
            raise ValueError(e)
  # No match found
  return logError(error_dict, error_name="API-NO-ACTION-FOUND")

def get(document_url, text_data):
  try:
    data = json.loads(text_data)
  except BaseException as e:
    return logError(str(e), error_name="API-JSON-INVALID-JSON")

  # Make sure we have the portal_type property and it match one of the authorized portal types of the web section
  # XXX Needs to add constraint to check validity of property
  if not document_url:
    try:
      document_url = data["id"]
    except KeyError:
      return logError("Cannot find id property", error_name="API-JSON-NO-ID-PROPERTY")
    except TypeError:
      return logError("Did not received a JSON Object", error_name="API-JSON-NOT-JSON-OBJECT")
  try:
    document = portal.restrictedTraverse(str(document_url))
  except KeyError:
    return logError("Document has not been found", error_name="API-DOCUMENT-NOT-FOUND")
  get_action_category = context.getLayoutProperty("configuration_get_action_type")
  erp5_action_dict = portal.Base_filterDuplicateActions(
      portal.portal_actions.listFilteredActionsFor(document))
  for erp5_action_key in erp5_action_dict.keys():
    for view_action in erp5_action_dict[erp5_action_key]:
      # Try to embed the form in the result
      if (get_action_category == view_action['category']):
        return getCorrespondingActionAndReturn(document, view_action['id'], "")
  return logError(
    "Unauthorized: No action with category %s found for %s" % (
      get_action_category,
      document.getRelativeUrl()
    ),
    error_name="API-NO-ACTION-FOUND"
  )

def put(document_url, text_data):
  try:
    data = json.loads(text_data)
  except BaseException as e:
    return logError(str(e), error_name="API-JSON-INVALID-JSON")

  # Make sure we have the portal_type property and it match one of the authorized portal types of the web section
  # XXX Needs to add constraint to check validity of property
  if not document_url:
    try:
      document_url = data["id"]
    except KeyError:
      return logError("Cannot find id property", error_name="API-JSON-NO-ID-PROPERTY")
    except TypeError:
      return logError("Did not received a JSON Object", error_name="API-JSON-NOT-JSON-OBJECT")
  try:
    document = portal.restrictedTraverse(str(document_url))
  except KeyError:
    return logError("Document has not been found", error_name="API-DOCUMENT-NOT-FOUND")
  put_action_category = context.getLayoutProperty("configuration_put_action_type")
  erp5_action_dict = portal.Base_filterDuplicateActions(
      portal.portal_actions.listFilteredActionsFor(document))
  for erp5_action_key in erp5_action_dict.keys():
    for view_action in erp5_action_dict[erp5_action_key]:
      # Try to embed the form in the result
      if (put_action_category == view_action['category']):
        return getCorrespondingActionAndReturn(document, view_action['id'], text_data)
  return logError(
    "Unauthorized: No action with category %s found for %s" % (
      put_action_category,
      document.getRelativeUrl()
    ),
    error_name="API-NO-ACTION-FOUND"
  )

def allDocs(text_data):
  try:
    data = json.loads(text_data)
  except BaseException as e:
    return logError(str(e), error_name="API-JSON-INVALID-JSON")
  if not isinstance(data, dict):
    return logError("Did not received a JSON Object", error_name="API-JSON-NOT-JSON-OBJECT")
  # Make sure we have the portal_type property and it match one of the authorized portal types of the web section
  # XXX Needs to add constraint to check validity of property
  result_list = []
  error_dict = {}
  match = False

  alldocs_entry_point_list = context.getLayoutProperty("configuration_alldocs_action_type")
  erp5_action_dict = portal.Base_filterDuplicateActions(
      portal.portal_actions.listFilteredActionsFor(context))
  for erp5_action_key in erp5_action_dict.keys():
    for view_action in erp5_action_dict[erp5_action_key]:
      # Try to embed the form in the result
      if (alldocs_entry_point_list == view_action['category']):
        try:
          search_result = getCorrespondingActionAndReturn(
            context, view_action['id'], text_data, list_error=True
          )
          result_list += search_result
          match = True
        except ValueError, e:
          try:
            error_dict.update(json.loads(str(e)))
          except ValueError:
            raise ValueError(e)
  if not match:
    return logError(
      json.dumps(error_dict, indent=2),
      error_name="API-NO-ACTION-FOUND"
    )
  return json.dumps({
    "$schema": "alldocs-response-schema.json",
    "result_list":result_list
    },
    indent=2
  )

mode_dict = {
  "put": lambda : put(document_id, text_content),
  "get": lambda : get(document_id, text_content),
  "post": lambda : post(text_content),
  "allDocs": lambda : allDocs(text_content),
}
if mode not in mode_dict:
  return "Used Mode is not defined in the mode list %s" % mode_dict.keys()

return mode_dict[mode]()
