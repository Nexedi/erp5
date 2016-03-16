if select_module == None:
  select_module = context.REQUEST.form["Base_doModule"]
if select_module == '':
  return
return context.ERP5Site_redirect(select_module, **kw)
