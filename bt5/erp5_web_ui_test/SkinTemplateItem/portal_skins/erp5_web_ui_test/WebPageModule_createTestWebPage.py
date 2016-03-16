web_page = context.newContent(portal_type='Web Page', id=id, reference=reference)
if publish:
  web_page.publish()
return "Created Successfully."
