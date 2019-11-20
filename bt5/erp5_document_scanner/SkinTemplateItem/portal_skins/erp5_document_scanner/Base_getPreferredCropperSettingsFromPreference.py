import json

portal = context.getPortalObject()

canvas_data = portal.portal_selections.getSelectionParamsFor(
  context.Base_getDocumentScannerSelectionName(),
  REQUEST=context.REQUEST) or {}

canvas_data["dialog_method"] = context.Base_storeDocumentFromCameraInActiveProcess.getId()

return json.dumps(canvas_data)
