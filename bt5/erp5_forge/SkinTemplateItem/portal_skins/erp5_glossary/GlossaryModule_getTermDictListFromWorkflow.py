marker = []
prefix = 'erp5_'
language = 'en'

term_dict = {}
result = []

for bt_id in template_list:
  # XXX this might be too simple: some business template include more than one skin folder
  bt = context.portal_templates.getInstalledBusinessTemplate(bt_id)
  if bt is None: continue
  if bt_id.startswith(prefix):
    bt_id = bt_id[len(prefix):]

  for wf_id in bt.getTemplateWorkflowIdList():
    wf = getattr(context.portal_workflow, wf_id)
    if getattr(wf, "interactions", marker) is marker: # only way to make sure it is not an interaction workflow ?
      term_dict[(wf_id, bt_id, wf.title, wf.description)] = wf_id
      for state_id, state in wf.states.items():
        term_dict[(state_id, bt_id, state.title, state.description)] = wf_id
      for trans_id, trans in wf.transitions.items():
        term_dict[(trans_id, bt_id, trans.title, trans.description)] = wf_id
        if trans.trigger_type == 1 and trans.actbox_name: # 1 == TRIGGER_USER_ACTION
          term_dict[('%s_actbox_name' % trans_id, bt_id, trans.actbox_name, '')] = wf_id

for (reference, business_field, title, description), workflow_id in term_dict.items():
  result.append({'reference': reference,
                 'language': language,
                 'business_field': business_field,
                 'title': title,
                 'description': description,
                 'workflow_id':workflow_id})

return result
