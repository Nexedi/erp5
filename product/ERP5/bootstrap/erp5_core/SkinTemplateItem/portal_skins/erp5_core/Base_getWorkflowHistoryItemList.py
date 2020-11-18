from Products.ERP5Type.Document import newTempBase
from Products.ERP5Type.Utils import getTranslationStringWithContext

from AccessControl import getSecurityManager

can_view_history = getSecurityManager().getUser().has_permission('View History', context)

marker = []
result = []
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
    actor_name_cache[actor] = actor
    person = portal_object.Base_getUserValueByUserId(actor)
    if person is not None:
      actor_name_cache[actor] = person.getTitle()
    return actor_name_cache[actor]



# Get history
workflow_item_list = portal_workflow.getInfoFor(
    ob=context, name='history', wf_id=workflow_id)

workflow = getattr(portal_workflow, workflow_id)
wf_state_variable = workflow.getStateVariable()

next_serial = None
previous_obj = None
for position, workflow_item in enumerate(workflow_item_list):
  # XXX removing str method generate a strange bug
  current_object = newTempBase(portal_object, str(position + 1))
  for key, value in workflow_item.items():
    if key == 'serial' and not can_view_history:
      continue
    if key == wf_state_variable:
      state = workflow.getStateValueById(value)
      # Store locally the id of state, usefull for merging action and transition
      state_id = marker if not state else value
      current_object.setProperty('state_id', state_id)

      key = 'state'
      if display:
        value = marker if not state else state.title
      else:
        value = state_id
    if key == 'action':
      # Store locally the id of action, usefull for merging action and transition
      current_object.setProperty('action_id', value)
      if value != '' and value is not None:
        if value == "'edit'":
          value = "edit"
        transition = workflow.getTransitionValueById(value)
        if transition:
          if display:
            value = transition.title or transition.actbox_name or value
          else:
            value = transition.getReference() or transition.actbox_name or value
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
    current_object.setProperty(key, value)
 
  # record current serial as "next serial" for the previous revision
  if next_serial is not None and can_view_history:
    previous_obj.setProperty('next_serial', current_object.serial)
  next_serial = getattr(current_object, 'serial', None)
  previous_obj = current_object
  result.append(current_object)

return result
