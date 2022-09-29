request = context.REQUEST

# FIXME: this is a workaround, because if listbox is present in request.form,
#   editable fields will be empty when re-displaying the dialog.
request.form.pop('listbox', None)
request.other.pop('listbox', None)

return getattr(context, dialog_id)(**kw)
