from base64 import decodestring

portal = context.getPortalObject()

if not active_process_url:
  active_process = portal.portal_activities.newActiveProcess()
  context.REQUEST.form["your_active_process_url"] = active_process.getRelativeUrl()
else:
  active_process = portal.restrictedTraverse(active_process_url)

active_process.postActiveResult(detail=decodestring(document_scanner_gadget))
return context.Base_renderForm('Base_viewUploadDocumentFromCameraDialog',
                               message='Captured')
