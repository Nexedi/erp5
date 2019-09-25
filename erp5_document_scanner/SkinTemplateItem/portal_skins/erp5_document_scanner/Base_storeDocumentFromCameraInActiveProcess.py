from base64 import decodestring
from Products.CMFActivity.ActiveResult import ActiveResult

portal = context.getPortalObject()
active_result = ActiveResult(
  detail=decodestring(document_scanner_gadget)
)

if not active_process_url:
  active_process = portal.portal_activities.newActiveProcess()
  context.REQUEST.form["your_active_process_url"] = active_process.getRelativeUrl()
else:
  active_process = portal.restrictedTraverse(active_process_url)

active_process.postResult(active_result)
return context.Base_renderForm('Base_viewUploadDocumentFromCameraDialog',
                               message='Captured')
