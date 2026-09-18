import json

ADD_PREFIX = 'add '
context.log(kw)

portal = context.getPortalObject()
document = portal.restrictedTraverse(relative_url)


def resolve_value(key, value):
  if key.endswith('_value') and isinstance(value, str):
    try:
      return portal.restrictedTraverse(value)
    except Exception:
      return value
  return value


def strip_field_prefix(field_id):
  # Formulator field ids are conventionally "my_<property_id>" (e.g.
  # "my_title" for the "title" property) - document.edit() takes the
  # plain property id, not the field id.
  if field_id.startswith('my_'):
    return field_id[len('my_'):]
  return field_id


def resolve_dialog(target, action):
  # The action's own resolved url's last path segment, acquired
  # directly on the target document. Returns None if that target is not
  # itself a Formulator Form (e.g. a bare transition with no dialog).
  url = action.get('url') or ''
  view_name = url.rstrip('/').rsplit('/', 1)[-1] if url else action.get('id')
  if view_name:
    view_name = view_name.split('?', 1)[0]
  if not view_name:
    return None
  view = getattr(target, view_name, None)
  if view is None:
    raise ValueError(
      "Could not find view '%s' (from action url %r) on document '%s'" % (
        view_name, url, target.getRelativeUrl()))
  if not hasattr(view, 'get_fields'):
    return None
  return view


def resolve_own_view_dialog(target):
  # Same as resolve_dialog, but for target's own "view" action (used to
  # read back its current field values after a change, generically -
  # no assumption about which properties matter, e.g. title is just one
  # of them).
  action_dict = target.Base_filterDuplicateActions(
    portal.portal_actions.listFilteredActionsFor(target))
  object_view_action_list = action_dict.get('object_view', [])
  if not object_view_action_list:
    return None
  return resolve_dialog(target, object_view_action_list[0])


def read_current_property_dict(target):
  # Re-read whatever a document's own "view" form currently shows,
  # generically - this is a genuine read-back of what is actually
  # stored now, not an echo of whatever kwargs a caller sent (which
  # could be wrong, ignored, or only partially applied).
  dialog = resolve_own_view_dialog(target)
  if dialog is None:
    return None
  property_dict = {}
  for field in dialog.get_fields():
    try:
      if field.get_value('hidden'):
        continue
      property_dict[strip_field_prefix(field.id)] = field.get_value('default')
    except Exception:
      continue
  return property_dict


# "add <portal_type>" is the same convention context_box_render.zpt uses
# for its "Add X" menu entries (built from getVisibleAllowedContentTypeList)
# and Base_doAction.py's own dispatch (doAction0 == 'add' -> Folder_create) -
# treated here as just another action, so there is no separate create tool.
if action_id.startswith(ADD_PREFIX):
  new_portal_type = action_id[len(ADD_PREFIX):]

  if dry_run:
    return json.dumps({
      'dry_run': True,
      'created': False,
      'relative_url': relative_url,
      'portal_type': new_portal_type,
      'property_dict': kw,
      'message': 'Preview only, nothing was created. Call again with dry_run=false to actually create the document.',
    }, default=str)

  new_document = document.newContent(portal_type=new_portal_type)
  if kw:
    new_document.edit(**{key: resolve_value(key, value) for key, value in kw.items()})

  result_dict = {
    'dry_run': False,
    'created': True,
    'relative_url': new_document.getRelativeUrl(),
    'portal_type': new_document.getPortalType(),
    'property_dict': read_current_property_dict(new_document),
  }
  if not kw:
    result_dict['warning'] = (
      'No field values were passed - this document was created with only '
      'default values (see property_dict). If you already know values '
      'for it (e.g. a title or other detail the user gave you), call '
      'ERP5Document_doAction again on relative_url \'%s\' with '
      'action_id \'edit\' and those values as keyword arguments.'
    ) % new_document.getRelativeUrl()
  return json.dumps(result_dict, default=str)

# "edit" is not itself a real "view"/"workflow"/"object" action - it is
# ERP5Document_getActionList's action_id for "save this document's own
# view/edit form", via the document's own generic edit() (the same
# accessor-setting method used elsewhere in these tools), not the
# HTML-form-oriented Base_edit skin script. Resolve the document's
# actual "view" action to get its Formulator fields, strip their "my_"
# prefix to get the real property ids, apply their current/default
# values, then let any explicitly-passed overrides win.
if action_id == 'edit':
  dialog = resolve_own_view_dialog(document)
  if dialog is None:
    return json.dumps({
      'done': False,
      'relative_url': relative_url,
      'action_id': action_id,
      'message': 'Could not resolve this document\'s own view form.',
    })

  final_kw = {}
  for field in dialog.get_fields():
    try:
      if field.get_value('hidden') or not field.get_value('editable'):
        continue
      final_kw[strip_field_prefix(field.id)] = field.get_value('default')
    except Exception:
      continue
  # kw keys may themselves still carry the "my_" prefix (e.g. copied
  # verbatim from a dialog_field_list entry's field_id), so strip them
  # the same way before merging - otherwise an override would land
  # under a different key instead of replacing the matching default.
  final_kw.update({strip_field_prefix(key): value for key, value in kw.items()})

  if dry_run:
    return json.dumps({
      'dry_run': True,
      'done': False,
      'relative_url': relative_url,
      'action_id': action_id,
      'property_dict': final_kw,
      'message': 'Preview only, nothing was saved. Call again with dry_run=false to actually save.',
    }, default=str)

  document.edit(**{key: resolve_value(key, value) for key, value in final_kw.items()})

  result_dict = {
    'dry_run': False,
    'done': True,
    'relative_url': relative_url,
    'action_id': action_id,
    'property_dict': read_current_property_dict(document),
  }
  if not kw:
    result_dict['warning'] = (
      'No field values were passed - this call only re-saved the '
      'existing values shown in property_dict, nothing changed. If you '
      'intended to set a specific value (e.g. from what the user asked '
      'for), call again with it as a keyword argument.'
    )
  return json.dumps(result_dict, default=str)

method = getattr(document, action_id, None)
if method is None or not callable(method):
  return json.dumps({
    'done': False,
    'relative_url': relative_url,
    'action_id': action_id,
    'message': 'Action "%s" is not available on this document. Re-check '
               'ERP5Document_getActionList for a valid action_id.' % action_id,
  })

# Fill in the dialog's own default field values (the same ones
# ERP5Document_getActionList's dialog_field_list reports), then let any
# explicitly-passed kw override them - mirroring how a human submitting
# the real dialog gets its defaults for every field they did not touch.
final_kw = {}
action_dict = document.Base_filterDuplicateActions(
  portal.portal_actions.listFilteredActionsFor(document))
matched_action = None
for action_source_list in (
  action_dict.get('workflow', []),
  document.Base_fixDialogActions(action_dict, 'object_action') or []
):
  for candidate in action_source_list:
    if candidate.get('id') == action_id:
      matched_action = candidate
      break
  if matched_action is not None:
    break

dialog = resolve_dialog(document, matched_action) if matched_action is not None else None
if dialog is not None:
  for field in dialog.get_fields():
    try:
      if field.get_value('hidden') or not field.get_value('editable'):
        continue
      final_kw[field.id] = field.get_value('default')
    except Exception:
      continue
final_kw.update(kw)

if dry_run:
  return json.dumps({
    'dry_run': True,
    'done': False,
    'relative_url': relative_url,
    'action_id': action_id,
    'property_dict': final_kw,
    'message': 'Preview only, the action was not invoked. Call again with dry_run=false to actually invoke it.',
  }, default=str)

method(**{key: resolve_value(key, value) for key, value in final_kw.items()})

result_dict = {
  'dry_run': False,
  'done': True,
  'relative_url': relative_url,
  'action_id': action_id,
  # A bare workflow transition/object action has no form of its own to
  # re-read (dialog is None in that case) - fall back to echoing what
  # was sent so the response is never empty, but prefer the document's
  # own current view whenever that action had a real dialog.
  'property_dict': read_current_property_dict(document) if dialog is not None else final_kw,
}
if hasattr(document, 'getSimulationState'):
  result_dict['simulation_state'] = document.getSimulationState()

return json.dumps(result_dict, default=str)
