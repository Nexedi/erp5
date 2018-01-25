portal = context.getPortalObject()
module = portal.accounting_module

module.manage_delObjects(list(module.objectIds()))

module.setProperty('current_content_script', script.getId())

# test depends on this
return "Accounting Transactions Created."
