from AccessControl import getSecurityManager
from Products.ERP5Type.Document import newTempBase
from Products.ERP5Type.Utils import getTranslationStringWithContext
from zExceptions import Unauthorized

user = getSecurityManager().getUser()
is_manager = user.has_role('Manager')
allowed_zope_actor_set = ('System Processes', 'Anonymous User')
placeholder_actor = 'Unknown'
can_view_history = user.has_permission('View History', context)

marker = []
result = []
i = 1
portal_object = context.getPortalObject()
portal_workflow = portal_object.portal_workflow
workflow_id_list = [x[0] for x in context.getWorkflowStateItemList()]
if not workflow_id in workflow_id_list:
  return []

actor_name_cache = {}
def getActorName(actor):
  # returns the name of the actor. If it's a person, show the usual name of the person
  try:
    return actor_name_cache[actor]
  except KeyError:
    # Show only actor names:
    # - for existing ERP5 users: ...that the current security context can see
    # - for non-ERP5 users (which includes deleted users, but this should be rare):
    #   ...that are a few special users (which cannot be used to log in),
    #   unless the current security context has the Manager role in which case show all these users
    person = portal_object.Base_getUserValueByUserId(actor)
    if person is None:
      actor_name = (
        actor
        if is_manager or actor in allowed_zope_actor_set else
        placeholder_actor
      )
    else:
      try:
        actor_name = person.getTitle()
      except Unauthorized:
        actor_name = placeholder_actor
    actor_name_cache[actor] = actor_name
    return actor_name



# Get history
workflow_item_list = portal_workflow.getInfoFor(
    ob=context, name='history', wf_id=workflow_id)

workflow = getattr(portal_workflow, workflow_id)
wf_state_variable = workflow.getStateVariable()

next_serial = None
previous_obj = None
for workflow_item in workflow_item_list:
  # XXX removing str method generate a strange bug
  o = newTempBase(portal_object, str(i))
  i += 1
  for key, value in workflow_item.items():
    if key == 'serial' and not can_view_history:
      continue
    if key == wf_state_variable:
      state = workflow.getStateValueByReference(value)
      # Store locally the id of state, usefull for merging action and transition
      state_id = marker if state is None else value
      o.setProperty('state_id', state_id)

      key = 'state'
      if display:
        value = marker if state is None else state.getTitle()
      else:
        value = state_id
    if key == 'action':
      # Store locally the id of action, usefull for merging action and transition
      o.setProperty('action_id', value)
      if value != '' and value is not None:
        if value == "'edit'":
          value = "edit"
        transition = workflow.getTransitionValueByReference(value)
        if transition is not None:
          if display:
            value = transition.getTitle() or transition.getActionName() or value
          else:
            value = transition.getReference() or transition.getActionName() or value
    if display:
      if key == 'error_message':
        if same_type(value, ''):
          value = context.Localizer.erp5_ui.gettext(value)
        if same_type(value, []):
          value = '. '.join(['%s' % x for x in value])
        else:
          value = '%s' % value
      elif key == 'actor':
        value = getActorName(value)
      elif same_type(value, '') and key == 'state':
        value = getTranslationStringWithContext(context, value, key, workflow_id)
      elif same_type(value, '') and key == 'action':
        value = getTranslationStringWithContext(context, value, 'transition', workflow_id)
    if value is marker:
      value = 'Does not exist'
    o.setProperty(key, value)

  # record current serial as "next serial" for the previous revision
  if next_serial is not None and can_view_history:
    previous_obj.setProperty('next_serial', o.serial)
  next_serial = getattr(o, 'serial', None)
  previous_obj = o
  result.append(o)

return result
