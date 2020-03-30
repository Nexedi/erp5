from Products.DCWorkflow.DCWorkflow import ValidationFailed

delivery = state_change['object']
divergence_list =  delivery.getDivergenceList()
Base_translateString = delivery.Base_translateString
if not len(divergence_list):
  delivery.converge()
  raise ValidationFailed(Base_translateString('No divergence found.'))

delivery_solve_property_dict = {}
listbox = state_change['kwargs'].get('delivery_group_listbox')
if listbox is not None:
  for k, v in listbox.items():
    object_url = v['choice']
    if object_url != 'ignore':
      delivery_solve_property_dict[k] = delivery.restrictedTraverse(object_url).getPropertyList(k)

divergence_to_accept_list = []
divergence_to_adopt_list = []

divergence_dict = {}
for divergence in divergence_list:
  simulation_movement_url = divergence.getProperty('simulation_movement').getRelativeUrl()
  divergence_dict['%s&%s' % (simulation_movement_url, divergence.getProperty('tested_property'))] = divergence

for listbox in [state_change['kwargs'].get('line_group_listbox'),
                state_change['kwargs'].get('cell_group_listbox')]:
  if listbox is None:
    continue
  for k, v in listbox.items():
    divergence = divergence_dict.get(k, None)
    if divergence is None:
      raise ValidationFailed(Base_translateString('Some divergences seem already solved. Please retry.'))
    choice = v['choice']
    if choice == 'accept':
      divergence_to_accept_list.append(divergence)
    elif choice == 'adopt':
      divergence_to_adopt_list.append(divergence)

delivery.solveDivergence(delivery_solve_property_dict=delivery_solve_property_dict,
                         divergence_to_accept_list=divergence_to_accept_list,
                         divergence_to_adopt_list=divergence_to_adopt_list,
                         comment='')
