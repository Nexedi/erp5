translateString = context.Base_translateString

if document_url is not None or not document_url:
  context.setTextContent(context.ERP5RunMyDocs_importWebPage(document_url))
  context.fromURL(document_url)
  portal_status_message = "Web Page successfully imported"
else:
  portal_status_message = "Url was not Provided."

context.Base_redirect('view', keep_items = dict(portal_status_message=translateString(portal_status_message)))
