import json

ADD_PREFIX = 'add '

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


def resolve_dialog(action):
  # Same resolution as ERP5Document_getActionList.resolve_dialog: the
  # action's own resolved url's last path segment, acquired directly on
  # the document. Returns None if that target is not itself a
  # Formulator Form (e.g. a bare transition with no dialog).
  url = action.get('url') or ''
  view_name = url.rstrip('/').rsplit('/', 1)[-1] if url else action.get('id')
  if view_name:
    view_name = view_name.split('?', 1)[0]
  if not view_name:
    return None, None
  target = getattr(document, view_name, None)
  if target is None:
    raise ValueError(
      "Could not find view '%s' (from action url %r) on document '%s'" % (
        view_name, url, document.getRelativeUrl()))
  if not hasattr(target, 'get_fields'):
    return None, view_name
  return target, view_name


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

  return json.dumps({
    'dry_run': False,
    'created': True,
    'relative_url': new_document.getRelativeUrl(),
    'portal_type': new_document.getPortalType(),
    'title': new_document.getTitle(),
  }, default=str)

# "edit" is not itself a real "view"/"workflow"/"object" action - it is
# ERP5Document_getActionList's action_id for "save this document's own
# view/edit form", via the document's own generic edit() (the same
# accessor-setting method used elsewhere in these tools), not the
# HTML-form-oriented Base_edit skin script. Resolve the document's
# actual "view" action to get its Formulator fields, strip their "my_"
# prefix to get the real property ids, apply their current/default
# values, then let any explicitly-passed overrides win.
if action_id == 'edit':
  action_dict = document.Base_filterDuplicateActions(
    portal.portal_actions.listFilteredActionsFor(document))
  object_view_action_list = action_dict.get('object_view', [])
  if not object_view_action_list:
    return json.dumps({
      'done': False,
      'relative_url': relative_url,
      'action_id': action_id,
      'message': 'This document has no "view" action to edit.',
    })

  dialog, _view_name = resolve_dialog(object_view_action_list[0])
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

  return json.dumps({
    'dry_run': False,
    'done': True,
    'relative_url': relative_url,
    'action_id': action_id,
  }, default=str)

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

if matched_action is not None:
  dialog, _view_name = resolve_dialog(matched_action)
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
}
if hasattr(document, 'getSimulationState'):
  result_dict['simulation_state'] = document.getSimulationState()

return json.dumps(result_dict, default=str)
