import json

data_dict = json.loads(data_json)
portal = context.getPortalObject()
translateString = portal.Base_translateString

active_process_url = data_dict.pop("active_process")
image_list = data_dict.pop("image_list")

preferred_cropped_canvas_data = data_dict.pop("preferred_cropped_canvas_data") or {}

selection_mapping = portal.portal_selections.getSelectionParamsFor(
  context.Base_getDocumentScannerSelectionName(),
  REQUEST=context.REQUEST) or {}

http_user_agent = context.REQUEST["HTTP_USER_AGENT"]
selection_mapping[http_user_agent] = preferred_cropped_canvas_data or {}
portal.portal_selections.setSelectionParamsFor(
  context.Base_getDocumentScannerSelectionName(),
  selection_mapping,
  context.REQUEST
)

# Avoid to pass huge images to the activity
kw.pop("your_document_scanner_gadget", None)

context.activate().Base_uploadDocumentFromCamera(
  publication_state=publication_state,
  active_process_url=active_process_url,
  image_list=image_list,
  **kw)

return context.Base_redirect('view',
                             keep_items={'portal_status_message':
                                         translateString('The document is being created in background.')})
