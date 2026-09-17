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

method = getattr(document, action_id, None)
if method is None or not callable(method):
  return json.dumps({
    'done': False,
    'relative_url': relative_url,
    'action_id': action_id,
    'message': 'Action "%s" is not available on this document. Re-check '
               'ERP5Document_getActionList for a valid action_id.' % action_id,
  })

if dry_run:
  return json.dumps({
    'dry_run': True,
    'done': False,
    'relative_url': relative_url,
    'action_id': action_id,
    'message': 'Preview only, the action was not invoked. Call again with dry_run=false to actually invoke it.',
  })

method(**kw)

result_dict = {
  'dry_run': False,
  'done': True,
  'relative_url': relative_url,
  'action_id': action_id,
}
if hasattr(document, 'getSimulationState'):
  result_dict['simulation_state'] = document.getSimulationState()

return json.dumps(result_dict, default=str)
