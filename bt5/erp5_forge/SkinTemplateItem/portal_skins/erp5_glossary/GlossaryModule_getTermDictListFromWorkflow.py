from Products.ERP5Type.Document import newTempBase
marker = []

portal_catalog = context.portal_catalog
portal_workflow = context.portal_workflow
portal_templates = context.portal_templates

def get_term_list(business_field, reference):
  reference = reference.rsplit('_action', 1)[0]
  term_list = portal_catalog(portal_type='Glossary Term',
                             validation_state='validated',
                             language_id='en',
                             business_field_title=('core', business_field),
                             reference=reference)
  return [i.getObject() for i in term_list]

def get_obj_and_reference_list(business_field):
  business_field = business_field.split('/')[0]
  result = []
  # XXX this might be too simple: some business template include more than one skin folder
  bt = portal_templates.getInstalledBusinessTemplate("erp5_%s" % business_field)
  if bt is None: return result
  for wf_id in bt.getTemplateWorkflowIdList():
    wf = getattr(portal_workflow, wf_id)
    if getattr(wf, "interactions", marker) is marker: # only way to make sure it is not an interaction workflow ?
      result.append((wf, wf_id, 'workflow'))
      for state in wf.getStateValueList():
        result.append((state, state.getReference(), 'state'))
      for transition in wf.getTransitionValueList():
        result.append((transition, transition.getReference(), 'transition'))
        if transition.getTriggerType() == 1 and transition.getActionName(): # 1 == TRIGGER_USER_ACTION
          result.append((transition, "%s_actbox_name" % transition.getReference(), 'action'))
  return result

line_list = []
c = 0
item_dict = {}
for business_field in template_list:
  if not business_field:
    continue
  for wf_item, reference, wf_item_type in get_obj_and_reference_list(business_field):
    term_list = get_term_list(business_field, reference)
    #if not term_list:
    #  continue
    if wf_item in item_dict:
      continue
    item_dict[wf_item] = True

    c += 1
    if wf_item_type == 'workflow':
      wf_item_path = wf_item.getId()
      wf_item_title = wf_item.getTitle()
    elif wf_item_type == 'state':
      wf_item_path = '%s/states/%s' % (wf_item.aq_parent.aq_parent.getId(), wf_item.getId())
      wf_item_title = wf_item.getTitle()
    elif wf_item_type == 'transition':
      wf_item_path = '%s/transitions/%s' % (wf_item.aq_parent.aq_parent.getId(), wf_item.getId())
      wf_item_title = wf_item.getTitle()
    else: # wf_item_type == 'action'
      wf_item_path = '%s/transitions/%s_actbox_name' % (wf_item.aq_parent.aq_parent.getId(), wf_item.getId())
      wf_item_title = wf_item.getActionName()
    wf_item_description = wf_item.getDescription()

    if wf_item_type == 'transition' and wf_item_path.endswith('_action'):
      if len(term_list) == 1 and \
          term_list[0].getTitle() + ' Action' == wf_item_title and \
          term_list[0].getDescription() == wf_item_description:
        continue
    else:
      if len(term_list) == 1 and \
          term_list[0].getTitle() == wf_item_title and \
          term_list[0].getDescription() == wf_item_description:
        continue

    line = newTempBase(context, 'tmp_glossary_wf_item_%s' %  c)
    line.edit(wf_item_path=wf_item_path,
              wf_item_type=wf_item_type,
              wf_item_title=wf_item_title,
              wf_item_edit_url = "%s/manage_main" % wf_item.absolute_url(),
              wf_item_description = wf_item_description,
              reference=reference,
              term_list=term_list
              )
    line.setUid(wf_item_path)
    line_list.append(line)

line_list.sort(key=lambda x:x.wf_item_path)
return line_list
