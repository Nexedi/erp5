request = context.REQUEST
from Products.ERP5Type.Document import newTempBase
from AccessControl import getSecurityManager

u=getSecurityManager().getUser()
connected_person = context.portal_catalog.getResultValue(portal_type='Person', reference=u)
try:
  my_group = connected_person.Person_getPrimaryGroup()
except AttributeError:
  my_group = None


#workflow_id = "egov_universal_workflow"

my_group = context.getTypeInfo().getOrganisationDirectionService()

marker = []
result = []
i = 1

portal_object = context.getPortalObject()
portal_workflow = portal_object.portal_workflow
workflow_id_list = [x for x, y in context.getWorkflowStateItemList()]


if not workflow_id in workflow_id_list:
  return []
# Get history
# XXX Compatibility
for history_name in ['history', 'building_history', 'installation_history']:
  workflow_item_list = portal_workflow.getInfoFor(ob=context, 
                                          name='history', wf_id=workflow_id)
  if workflow_item_list != []:
    break

wf_states = portal_workflow[workflow_id].states
wf_transitions = portal_workflow[workflow_id].transitions

next_serial = None
previous_obj = None

for workflow_item in workflow_item_list:
  same_action = 0
  # XXX removing str method generate a strange bug
  o = newTempBase(portal_object, str(i))
  i += 1
  for key, value in workflow_item.items():
    # XXX Compatibility
    for compatibility_name in ['building_', 'installation_']:
      if key.startswith(compatibility_name):
        # Display the workflow state in the state columns
        key = key[len(compatibility_name):]
    if key.endswith('state'): 
      key = 'state'
      if display:
        value = wf_states.get(value, marker) and wf_states[value].title
      else:
        value = wf_states.get(value, marker) and wf_states[value].id
    if key == 'action':
      action_name = value
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
      elif same_type(value, '') and key in ( 'action', 'state' ): 
        value = context.Localizer.erp5_ui.gettext(value)
    if value is marker:
      value = 'Does not exist'
    o.setProperty(key, value)
  
  if getattr(previous_obj, 'state', None) is not None:
    if previous_obj.state ==  o.state:
      same_action = 1


  # record current serial as "next serial" for the previous revision
  if next_serial is not None:
    previous_obj.setProperty('next_serial', o.serial)
  next_serial = getattr(o, 'serial', None)
  previous_obj = o
  person = context.portal_catalog.getResultValue(portal_type='Person', reference=o.actor)
  try:
    group = person.Person_getPrimaryGroup()
  except AttributeError:
    group = None

  if not same_action:
    if group and my_group : 
      if group.startswith(my_group) or action_name in ['pending', 'submit_draft']:
        result.append(o)
    elif action_name in ['pending', 'submit_draft']:
      result.append(o)
return result
