portal = context.getPortalObject()
translateString = portal.Base_translateString

# Avoid to pass huge images to the activity
kw.pop("your_document_scanner_gadget", None)

context.activate().Base_uploadDocumentFromCamera(
  active_process_url=active_process_url, **kw)

return context.Base_redirect('view',
                             keep_items={'portal_status_message':
                                         translateString('The document is being created in background.')})
