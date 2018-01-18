portal = context.getPortalObject()
module = portal.accounting_module

module.manage_delObjects(list(module.objectIds()))

# test depends on this
return "Accounting Transactions Created."
