# prevent lose checked itens at listbox after click to print
# For backward compatibility, do nothing if
# Base_updateListboxSelection cannot be found.
Base_updateListboxSelection = getattr(context, 'Base_updateListboxSelection', None)
if Base_updateListboxSelection is not None:
  Base_updateListboxSelection()

kw.update(context.REQUEST.form)
keep_items=dict(
    dialog_category=dialog_category,
    form_id=form_id,
    cancel_url=cancel_url,
    object_path=context.REQUEST.get('object_path', context.getPath()))

return context.ERP5Site_redirect(select_dialog.split()[0], keep_items=keep_items, **kw)
