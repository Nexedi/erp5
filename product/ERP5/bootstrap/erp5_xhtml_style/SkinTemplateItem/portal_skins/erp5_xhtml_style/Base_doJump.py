# prevent lose checked itens after click to print
# For backward compatibility, do nothing if
# Base_updateListboxSelection cannot be found.
Base_updateListboxSelection = getattr(context, 'Base_updateListboxSelection', None)
if Base_updateListboxSelection is not None:
  Base_updateListboxSelection()

if select_jump is None:
  select_jump = context.REQUEST.form["Base_doJump"]

if select_jump == '':
  return

request = container.REQUEST
return context.ERP5Site_redirect(select_jump,
     keep_items=dict(form_id=request.get('form_id', 'view')), **kw)
