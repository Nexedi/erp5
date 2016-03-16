"""
  XXX: Turn relative url into dom_id and pass through page with portal_status_message.
  This is used in Selenium tests and is a bit dirty way to have it handled.
"""
context.REQUEST.set('portal_status_message', knowledge_box_url.replace('/','_'))
return context.view()
