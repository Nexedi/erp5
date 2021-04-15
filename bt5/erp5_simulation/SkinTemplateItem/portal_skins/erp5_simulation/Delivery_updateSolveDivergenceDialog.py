request = context.REQUEST
from Products.ERP5Type.Message import translateString

line_list = context.Delivery_getSolverDecisionList(listbox=listbox)

if len(line_list) == 0:
  kw["keep_items"] = {'portal_status_message': translateString("Workflow state may have been updated by other user. Please try again.")}
  return context.Base_redirect(form_id, **kw)

for listbox_dict in listbox:
  line = [x for x in line_list if x.getPath() == listbox_dict['listbox_key']][0]
  uid = line.getUid()
  for prop in ('solver', 'solver_configuration', 'delivery_solver', 'comment',):
    value = listbox_dict.get(prop, None)
    key = 'field_listbox_%s_%s' % (prop, uid)
    request.form[key] = request.other[key] = value
    if prop == 'solver_configuration':
      if value is not None:
        line.updateConfiguration(**value.as_dict())
    else:
      line.setProperty(prop, value)

return context.Base_renderForm('Delivery_viewSolveDivergenceDialog', keep_items={
  'your_dialog_updated': '1',
  'listbox': listbox
})
