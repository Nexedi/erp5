from Products.CMFCore.utils import getToolByName
context.resetSubscriberList()

message = context.Base_translateString('Publication reseting')
return context.Base_redirect(form_id, keep_items={'portal_status_message' : message},  **kw)
