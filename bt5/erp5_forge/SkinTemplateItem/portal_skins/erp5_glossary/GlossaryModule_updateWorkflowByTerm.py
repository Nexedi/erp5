prefix = 'field_listbox_term_'
prefix_length = len(prefix)
suffix = '_actbox_name'
suffix_length = len(suffix)
portal_workflow = context.portal_workflow
portal_catalog = context.portal_catalog

for i in kw.keys():
  is_action = 0
  if not(i.startswith(prefix) and kw[i]):
    continue

  term_uid = int(kw[i])
  term = portal_catalog(uid=term_uid)[0].getObject()

  wf_item_path = i[prefix_length:]
  if wf_item_path.endswith(suffix):
    wf_item_path = wf_item_path[:-suffix_length]
    is_action = 1
  wf_item = portal_workflow.restrictedTraverse(wf_item_path)

  if wf_item.meta_type == "Workflow":
    wf_item.setProperties(term.getTitle(), description=term.getDescription(), manager_bypass=wf_item.manager_bypass)
  elif wf_item.meta_type == "Workflow State":
    wf_item.setProperties(term.getTitle(), description=term.getDescription(),
        transitions=wf_item.getDestinationReferenceList(), type_list=wf_item.type_list)
  else: # wf_item.meta_type == "Workflow Transition"
    guard = getattr(wf_item, 'guard', None)
    if not is_action:
      title = term.getTitle()
      if wf_item_path.endswith('_action'):
        title += ' Action'
      wf_item.setProperties(
          title,
          wf_item.new_state_id,
          description=term.getDescription(),

          trigger_type=wf_item.trigger_type,
          script_name=wf_item.script_name,
          after_script_name=wf_item.after_script_name,
          actbox_name = wf_item.actbox_name,
          actbox_url = wf_item.actbox_url,
          actbox_category = wf_item.actbox_category,)
    else:
      wf_item.setProperties(
          wf_item.title,
          wf_item.new_state_id,
          description=term.getDescription(),

          trigger_type=wf_item.trigger_type,
          script_name=wf_item.script_name,
          after_script_name=wf_item.after_script_name,
          actbox_name = term.getTitle(),
          actbox_url = wf_item.actbox_url,
          actbox_category = wf_item.actbox_category,)
    if guard is not None:
      wf_item.Glossary_setGuard(guard)


portal_status_message = context.Base_translateString('Workflows updated.')
context.Base_redirect(keep_items={'portal_status_message':portal_status_message})
