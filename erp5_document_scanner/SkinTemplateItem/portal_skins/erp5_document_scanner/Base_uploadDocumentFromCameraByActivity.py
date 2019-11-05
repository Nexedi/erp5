portal = context.getPortalObject()
translateString = portal.Base_translateString

active_process = context.Base_storeDocumentFromCameraInActiveProcess(
  active_process_url=active_process_url,
  batch_mode=True,
  **kw)

if active_process is None and active_process_url:
  active_process = portal.restrictedTraverse(active_process_url)

# Avoid to pass huge images to the activity
kw.pop("your_document_scanner_gadget", None)

context.activate().Base_uploadDocumentFromCamera(
  active_process_url=active_process.getRelativeUrl(),
  **kw)

return context.Base_redirect('view',
                             keep_items={'portal_status_message':
                                         translateString('The document is being created in background.')})
