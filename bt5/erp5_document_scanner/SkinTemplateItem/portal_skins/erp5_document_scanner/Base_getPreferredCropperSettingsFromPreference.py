import json

portal = context.getPortalObject()

selection_mapping = portal.portal_selections.getSelectionParamsFor(
  context.Base_getDocumentScannerSelectionName(),
  REQUEST=context.REQUEST) or {}

canvas_data = selection_mapping.get(context.REQUEST["HTTP_USER_AGENT"]) or {}
canvas_data["dialog_method"] = context.Base_storeDocumentFromCameraInActiveProcess.getId()

return json.dumps(canvas_data)
