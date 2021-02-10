portal = context.getPortalObject()

module_id, select_action = select_action.split(' ', 1)
module = portal.restrictedTraverse(module_id)

return module.Base_doAction(select_action, dialog_id, **kw)
