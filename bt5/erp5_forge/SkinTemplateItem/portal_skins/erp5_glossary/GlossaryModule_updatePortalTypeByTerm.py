prefix = 'field_listbox_term_'
prefix_length = len(prefix)
portal_catalog = context.portal_catalog

for i in kw.keys():
  if not(i.startswith(prefix) and kw[i]):
    continue
  term_uid = int(kw[i])
  term = portal_catalog(uid=term_uid)[0].getObject()

  field_path = i[prefix_length:]
  context.GlossaryModule_setPortalTypeDescription(field_path, term.getDescription())

portal_status_message = context.Base_translateString('Portal Types updated.')
context.Base_redirect(keep_items={'portal_status_message':portal_status_message})
