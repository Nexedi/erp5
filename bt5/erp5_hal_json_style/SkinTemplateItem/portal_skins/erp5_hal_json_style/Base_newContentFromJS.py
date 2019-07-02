redirect_document = context.newContent(portal_type=portal_type)
return redirect_document.Base_redirect(keep_items={'portal_status_message': 'Document created.'})
