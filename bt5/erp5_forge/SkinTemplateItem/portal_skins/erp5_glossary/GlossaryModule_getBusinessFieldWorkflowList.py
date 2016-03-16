from Products.ERP5Type.Document import newTempBase
marker = []

result = []

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
      for state_id, state in wf.states.items():
        result.append((state, state_id, 'state'))
      for trans_id, trans in wf.transitions.items():
        result.append((trans, trans_id, 'transition'))
        if trans.trigger_type == 1 and trans.actbox_name: # 1 == TRIGGER_USER_ACTION
          result.append((trans, "%s_actbox_name" % trans_id, 'action'))
  return result

business_field_list = [i for i in business_field_list if i]

line_list = []
c = 0
item_dict = {}
for business_field in business_field_list:
  for wf_item, reference, type in get_obj_and_reference_list(business_field):
    term_list = get_term_list(business_field, reference)
    #if not term_list:
    #  continue
    if item_dict.has_key(wf_item):
      continue
    item_dict[wf_item] = True

    c += 1
    if type == 'workflow':
      wf_item_path = wf_item.id
      wf_item_title = wf_item.title
    elif type == 'state':
      wf_item_path = '%s/states/%s' % (wf_item.aq_parent.aq_parent.id, wf_item.id)
      wf_item_title = wf_item.title
    elif type == 'transition':
      wf_item_path = '%s/transitions/%s' % (wf_item.aq_parent.aq_parent.id, wf_item.id)
      wf_item_title = wf_item.title
    else: # type == 'action'
      wf_item_path = '%s/transitions/%s_actbox_name' % (wf_item.aq_parent.aq_parent.id, wf_item.id)
      wf_item_title = wf_item.actbox_name
    wf_item_description = wf_item.description

    if type == 'transition' and wf_item_path.endswith('_action'):
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
              wf_item_type=type,
              wf_item_title=wf_item_title,
              wf_item_edit_url = "%s/manage_properties" % wf_item.absolute_url(),
              wf_item_description = wf_item_description,
              reference=reference,
              term_list=term_list
              )
    line.setUid(wf_item_path)
    line_list.append(line)

line_list.sort(key=lambda x:x.wf_item_path)
return line_list
