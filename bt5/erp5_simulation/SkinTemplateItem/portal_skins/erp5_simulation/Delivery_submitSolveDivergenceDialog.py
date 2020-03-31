from Products.ERP5Type.Message import translateString

request= context.REQUEST

if not listbox:
  listbox = request.get('listbox', [])
  if isinstance(listbox, dict):
    # structure of listbox value is different than the one fetch from parameters
    repaired_listbox = []
    for key in listbox:
      item = listbox[key]
      item['listbox_key'] = key
      repaired_listbox.append(item)
    listbox = repaired_listbox

line_list = context.Delivery_getSolverDecisionList(listbox=listbox)

def displayParallelChangeMessage():
  kw["keep_items"] = {'portal_status_message': translateString("Workflow state may have been updated by other user. Please try again.")}
  return context.Base_redirect(form_id, **kw)

# if we are not divergence any more
if len(line_list) == 0:
  return displayParallelChangeMessage()

line = None
for listbox_dict in listbox:
  listbox_key = listbox_dict['listbox_key']
  line = [x for x in line_list if x.getPath() == listbox_key][0]
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

# if divergence solving is already ongoing and will be fixed by activities
if line is None:
  return displayParallelChangeMessage()

solver_process = line.getParentValue()
solver_process.buildTargetSolverList()
solver_process.solve()

return context.Base_redirect(form_id,
  keep_items=dict(portal_status_message=
         translateString('Divergence solvers started in background.')))
