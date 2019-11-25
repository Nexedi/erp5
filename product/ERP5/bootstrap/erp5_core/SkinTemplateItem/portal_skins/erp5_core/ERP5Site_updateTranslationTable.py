from Products.ERP5Type.Utils import getMessageIdWithContext

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
for wf_id, portal_type_list in portal_workflow.getChainDict().items():
  wf = getattr(portal_workflow, wf_id, None)
  if wf is None:
    continue
  state_var = wf.variables.getStateVar()
  if wf.states:
    for state_id, state in wf.states.items():
      for lang in supported_languages:
        for portal_type in portal_type_list:
          key = (lang, portal_type, state_var, state_id)
          if not translated_keys.has_key(key):
            translated_message = context.Localizer.erp5_ui.gettext(state_id, lang=lang).encode('utf-8')
            translated_keys[key] = None # mark as translated
            object_list.append(dict(language=lang, message_context=state_var, portal_type=portal_type, original_message=state_id,
                               translated_message=translated_message))

          # translate state title as well
          if state.title != '' :
            state_var_title = '%s_title' % state_var
            msg_id = getMessageIdWithContext(state.title, 'state', wf.id)
            translated_message = context.Localizer.erp5_ui.gettext(msg_id, default='', lang=lang).encode('utf-8')
            if translated_message == '':
              msg_id = state.title
              translated_message = context.Localizer.erp5_ui.gettext(state.title.decode('utf-8'), lang=lang).encode('utf-8')
            key = (lang, portal_type, state_var_title, state_id, msg_id)
            if not translated_keys.has_key(key):
              translated_keys[key] = None # mark as translated
              object_list.append(dict(language=lang, message_context=state_var_title, portal_type=portal_type, original_message=state_id,
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
    if not translated_keys.has_key(key):
      translated_keys[key] = None # mark as translated
      object_list.append(dict(language=lang, message_context='portal_type', portal_type=portal_type, original_message=portal_type,
                         translated_message=context.Localizer.erp5_ui.gettext(portal_type, lang=lang).encode('utf-8')))
if object_list:
  catalog_translation_list(object_list)

print 'Done'
return printed
