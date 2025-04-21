portal = context.getPortalObject()
module = portal.accounting_module

object_ids = list(module.objectIds())
if object_ids:
    module.manage_delObjects(object_ids)

module.setProperty('current_content_script', script.getId())

# test depends on this
return "Accounting Transactions Created."
