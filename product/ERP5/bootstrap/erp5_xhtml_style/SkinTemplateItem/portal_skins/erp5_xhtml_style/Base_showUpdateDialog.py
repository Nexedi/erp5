kw.update(context.REQUEST.form)
kw['dialog_method'] = update_method
return context.Base_callDialogMethod(**kw) #XXX: is enable_pickle=1 required ?
