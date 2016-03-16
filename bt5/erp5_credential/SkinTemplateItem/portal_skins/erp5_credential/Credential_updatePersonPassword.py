"""Use script with Proxy Role Manager to update password of related person. 
Clear 'erp5_content_short' cache too."""

person = context.getDestinationDecisionValue(portal_type="Person")

if context.getPassword():
  person.setEncodedPassword(context.getPassword())
  context.portal_caches.clearCache(('erp5_content_short',))
