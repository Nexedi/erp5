from Products.ERP5Type.Utils import getMessageIdWithContext, str2unicode, unicode2str

supported_languages = context.Localizer.get_supported_languages()
translated_keys = {} # This dict prevents entering the same key twice

sql_catalog = context.portal_catalog.getSQLCatalog(sql_catalog_id)
sql_catalog.z0_drop_translation()
sql_catalog.z_create_translation()

z_catalog_translation_list = sql_catalog.z_catalog_translation_list
def catalog_translation_list(object_list):
  parameter_dict = {}
  for i in object_list:
    for property_ in ('language', 'message_context', 'portal_type',
                     'original_message', 'translated_message'):
      parameter_dict.setdefault(property_, []).append(i[property_])
  z_catalog_translation_list(**parameter_dict)

# Translate every workflow state in the context of the state variable
object_list = []
portal_workflow = context.portal_workflow
portal_type_list = context.portal_types.objectValues()
for portal_type in portal_type_list:
  associated_workflow_id_list = []
  associated_workflow_id_list.extend(portal_type.getTypeWorkflowList())
  for wf_id in associated_workflow_id_list:
    wf = getattr(portal_workflow, wf_id, None)
    if wf is None:
      continue
    state_var = wf.getStateVariable()

    for state in wf.getStateValueList():
      state_reference = state.getReference()
      for lang in supported_languages:
        key = (lang, portal_type.getId(), state_var, state_reference)
        if key not in translated_keys:
          translated_message = unicode2str(context.Localizer.erp5_ui.gettext(state_reference, lang=lang))
          translated_keys[key] = None # mark as translated
          object_list.append(dict(language=lang, message_context=state_var, portal_type=portal_type.getId(), original_message=state_reference,
                             translated_message=translated_message))

        # translate state title as well
        if state.getTitle() is not None and state.getTitle() != '':
          state_var_title = '%s_title' % state_var
          msg_id = getMessageIdWithContext(state.getTitle(), 'state', wf_id)
          translated_message = unicode2str(context.Localizer.erp5_ui.gettext(msg_id, default='', lang=lang))
          if translated_message == '':
            msg_id = state.getTitle()
            translated_message = unicode2str(context.Localizer.erp5_ui.gettext(str2unicode(state.getTitle()), lang=lang))
          key = (lang, portal_type.getId(), state_var_title, state_reference, msg_id)
          if key not in translated_keys:
            translated_keys[key] = None # mark as translated
            object_list.append(dict(language=lang, message_context=state_var_title, portal_type=portal_type.getId(), original_message=state_reference,
                               translated_message=translated_message))


if object_list:
  catalog_translation_list(object_list)

# Translate every portal type in the context of the portal type
object_list = []
for ptype in context.portal_types.objectValues():
  portal_type = ptype.title
  if not portal_type: portal_type = ptype.id
  for lang in supported_languages:
    key = (lang, 'portal_type', portal_type)
    if key not in translated_keys:
      translated_keys[key] = None # mark as translated
      object_list.append(dict(language=lang, message_context='portal_type', portal_type=portal_type, original_message=portal_type,
                         translated_message=unicode2str(context.Localizer.erp5_ui.gettext(portal_type, lang=lang))))
if object_list:
  catalog_translation_list(object_list)

print('Done')
return printed
