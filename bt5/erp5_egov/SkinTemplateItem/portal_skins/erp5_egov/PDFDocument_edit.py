form_id = 'view'
return context.asContext(edit=context.edit,
  **{form_id: context.getTypeInfo().getERP5Form()}).Base_edit(form_id=form_id, *args, **kw)
