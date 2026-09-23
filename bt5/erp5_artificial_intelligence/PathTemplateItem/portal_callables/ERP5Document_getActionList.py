import json


def resolve_dialog(document, action):
  # The action's own resolved url (e.g. ".../confirm" for a bare
  # transition with no dialog, or ".../SomeType_viewSomeDialog" when it
  # opens a dialog first) is what a human actually navigates to for
  # this action - not necessarily the same as its id/reference. Traverse
  # to whatever that url's last path segment names, acquired directly on
  # the document so field TALES expressions referring to "here" resolve
  # to it. Returns None if that target is not itself a Formulator Form
  # (e.g. a bare transition, or a Page Template rendering a form
  # internally rather than being one).
  url = action.get('url') or ''
  view_name = url.rstrip('/').rsplit('/', 1)[-1] if url else action.get('id')
  if view_name:
    # url may carry a query string, e.g.
    # "Bug_viewWorkflowActionDialog?workflow_action=confirm_action" -
    # keep only the traversable view id.
    view_name = view_name.split('?', 1)[0]
  if not view_name:
    return None
  target = getattr(document, view_name, None)
  if target is None:
    raise ValueError(
      "Could not find view '%s' (from action url %r) on document '%s'" % (
        view_name, url, document.getRelativeUrl()))
  if not hasattr(target, 'get_fields'):
    return None
  return target


def get_dialog_field_list(document, action):
  target = resolve_dialog(document, action)
  if target is None:
    return None

  field_list = []
  for field in target.get_fields():
    try:
      if field.get_value('hidden'):
        continue
      field_list.append({
        'field_id': field.id,
        'title': field.get_value('title') or field.id,
        'type': field.meta_type,
        'required': bool(field.get_value('required')),
        'editable': bool(field.get_value('editable')),
        'value': field.get_value('default'),
      })
    except Exception:
      # A field whose TALES expressions need request state we do not
      # have here (e.g. selection-dependent defaults) - skip it rather
      # than fail the whole action.
      continue
  return field_list or None


def build_action_list(document, action_source_list, action_id_override=None):
  result = []
  for action in action_source_list:
    action_id = action.get('id')
    if not action_id:
      continue
    result.append({
      'action_id': action_id_override or action_id,
      'title': action.get('title') or action.get('name'),
      'dialog_field_list': get_dialog_field_list(document, action),
    })
  return result


portal = context.getPortalObject()
document = portal.restrictedTraverse(relative_url)

# Same computation context_box_render.zpt uses to build the "Action" menu
# a human sees on this document right now (global_definitions.zpt):
#   actions = here.Base_filterDuplicateActions(
#     portal.portal_actions.listFilteredActionsFor(action_context))
# - live, workflow-state and permission aware, unlike a static per-
# portal_type declaration.
action_dict = document.Base_filterDuplicateActions(
  portal.portal_actions.listFilteredActionsFor(document))

# "Workflows" section of the Action menu: real state-machine
# transitions, invokable via ERP5Document_doAction as
# getattr(document, action_id)().
workflow_action_list = build_action_list(document, action_dict.get('workflow', []))

# "Object" section of the Action menu: custom per-portal_type actions
# (merged with their jio variant and de-duplicated the same way
# context_box_render.zpt does, via Base_fixDialogActions) - their
# action_id is a skin script acquired onto the document, so it is also
# invokable via ERP5Document_doAction the same way as a workflow
# transition.
object_action_list = build_action_list(
  document, document.Base_fixDialogActions(action_dict, 'object_action') or [])

# The document's own "view" action is not itself an invokable action -
# saving edited field values on an existing document is done via the
# document's own generic edit() method (action_id 'edit', handled
# specially by ERP5Document_doAction) - so report that as the action_id
# here rather than the view's own id, even though its dialog_field_list
# still comes from the real "view" action's form.
object_view_list = build_action_list(
  document, action_dict.get('object_view', []), action_id_override='edit')

return json.dumps({
  'relative_url': relative_url,
  'portal_type': document.getPortalType(),
  'workflow_action_list': workflow_action_list,
  'object_action_list': object_action_list,
  'object_view_list': object_view_list,
  'can_create_here': sorted(document.getVisibleAllowedContentTypeList()),
}, default=str)
