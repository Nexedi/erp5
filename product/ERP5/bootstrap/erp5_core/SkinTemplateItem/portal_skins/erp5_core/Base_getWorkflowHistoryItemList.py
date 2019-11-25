from Products.ERP5Type.Document import newTempBase
from Products.ERP5Type.Utils import getTranslationStringWithContext

from AccessControl import getSecurityManager

can_view_history = getSecurityManager().getUser().has_permission('View History', context)

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
    actor_name_cache[actor] = actor
    person = portal_object.Base_getUserValueByUserId(actor)
    if person is not None:
      actor_name_cache[actor] = person.getTitle()
    return actor_name_cache[actor]



# Get history
workflow_item_list = portal_workflow.getInfoFor(
    ob=context, name='history', wf_id=workflow_id)

wf_state_var = portal_workflow[workflow_id].variables.getStateVar()
wf_states = portal_workflow[workflow_id].states
wf_transitions = portal_workflow[workflow_id].transitions

next_serial = None
previous_obj = None
for workflow_item in workflow_item_list:
  # XXX removing str method generate a strange bug
  o = newTempBase(portal_object, str(i))
  i += 1
  for key, value in workflow_item.items():
    if key == 'serial' and not can_view_history:
      continue
    # XXX Compatibility
    for compatibility_name in ['building_', 'installation_']:
      if key.startswith(compatibility_name):
        # Display the workflow state in the state columns
        key = key[len(compatibility_name):]
    if key == wf_state_var: 
      # Store locally the id of state, usefull for merging action and transition
      state_id = wf_states.get(value, marker) and wf_states[value].id
      o.setProperty('state_id', state_id)

      key = 'state'
      if display:
        value = wf_states.get(value, marker) and wf_states[value].title
      else:
        value = state_id
    if key == 'action':
      # Store locally the id of action, usefull for merging action and transition
      o.setProperty('action_id', value)
      if value != '' and value is not None:
        if value == "'edit'":
          value = "edit"
        if display:
          value = wf_transitions.get(value, marker) and (wf_transitions[value].title or wf_transitions[value].actbox_name) or value
        else:
          value = wf_transitions.get(value, marker) and (wf_transitions[value].id or wf_transitions[value].actbox_name) or value
    if display:
      if key == 'error_message' and same_type(value, ''):
        value = context.Localizer.erp5_ui.gettext(value)    
      elif key == 'error_message' and same_type(value, []):
        value = '. '.join(['%s' % x for x in value])
      elif key == 'error_message':
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
