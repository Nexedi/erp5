request= context.REQUEST
from Products.ERP5Type.Message import translateString

listbox = request.get('listbox')
line_list = context.Delivery_getSolverDecisionList(listbox=listbox)

if len(line_list) == 0:
  kw["keep_items"] = {'portal_status_message': translateString("Workflow state may have been updated by other user. Please try again.")}
  return context.Base_redirect(form_id, **kw)

for listbox_key in listbox:
  listbox_dict = listbox[listbox_key]
  line = [x for x in line_list if x.getPath() == listbox_key][0]
  uid = line.getUid()
  for property in ('solver', 'solver_configuration', 'delivery_solver', 'comment',):
    value = listbox_dict.get(property, None)
    key = 'field_listbox_%s_%s' % (property, uid)
    request.form[key] = request.other[key] = value
    if property == 'solver_configuration':
      if value is not None:
        line.updateConfiguration(**value.as_dict())
    else:
      line.setProperty(property, value)
request.set('your_dialog_updated', '1')
request.form['dialog_updated'] = '1'
request.form['listbox'] = listbox
return context.Base_renderForm('Delivery_viewSolveDivergenceDialog')
