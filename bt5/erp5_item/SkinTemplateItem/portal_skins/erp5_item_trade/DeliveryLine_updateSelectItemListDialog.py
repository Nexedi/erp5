request = context.REQUEST
portal = context.getPortalObject()
Base_translateString = portal.Base_translateString

# FIXME: this is a workaround, because if listbox is present in request.form, 
#   editable fields will be empty when re-displaying the dialog.
request.form.pop('listbox', None)
request.other.pop('listbox', None)

context.Base_updateDialogForm()
return context.Base_renderForm(
  dialog_id,
  keep_items={'portal_status_message': Base_translateString('Updated')}
)
