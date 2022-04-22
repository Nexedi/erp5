from Products.ERP5Type.Message import translateString
choosen = [choice for choice in list(editor.values()) if choice['workflow_action']]
if len(choosen) == 1:
  return True

# XXX listbox validator does not show the validation failed message, so use portal status message instead
if len(choosen) == 0:
  container.REQUEST.set('portal_status_message', translateString("You must select one action."))
else:
  container.REQUEST.set('portal_status_message', translateString("You must select only one action."))
return False
