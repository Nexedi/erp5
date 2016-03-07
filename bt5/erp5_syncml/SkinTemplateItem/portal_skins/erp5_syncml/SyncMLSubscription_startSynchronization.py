from Products.CMFCore.utils import getToolByName
portal = context.getPortalObject()
synchronization_tool = getToolByName(portal, 'portal_synchronizations')
synchronization_tool.processClientSynchronization(context.getPath())

message = context.Base_translateString('Synchronization started')
return context.Base_redirect(form_id, keep_items={'portal_status_message' : message},  **kw)
