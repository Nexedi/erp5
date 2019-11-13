portal = context.getPortalObject()

preference = portal.portal_preferences.getActivePreference()
if preference is None\
    or preference.getPreferenceState() != 'enabled'\
    or not portal.portal_membership.checkPermission(
      'Add portal content', preference):
  p = portal.portal_preferences.newContent(portal_type='Preference')
  p.setTitle('Document Template Container')
  p.enable()
  preference = p

message = context.Base_translateString("Templated created.")

# if the preference already contains a template with the same name, making
# another template will replace it
document_title = context.getTitle()
for existing_template in preference.contentValues(
    portal_type=context.getPortalType()):
  if existing_template.getTitle() == document_title:
    preference.manage_delObjects(ids=[existing_template.getId()])
    message = context.Base_translateString("Templated updated.")
    break

parent = context.getParentValue()
document_id = context.getId()
cp = parent.manage_copyObjects(ids=[document_id])
paste_info, = preference.manage_pasteObjects(cb_copy_data=cp, is_indexable=False)

template = getattr(preference, paste_info['new_id'])
template.makeTemplate()

portal.portal_preferences.clearCache(preference)

kw['keep_items'] = dict(portal_status_message=message)
return context.Base_redirect(form_id,
                             **kw)
