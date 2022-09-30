task_list = [x.getObject() for x in \
  context.portal_catalog(selection_report=selection_report,
                         portal_type='Task',
                         simulation_state=context.getPortalDraftOrderStateList()+
                                          context.getPortalPlannedOrderStateList())]
task_list.extend([x.getObject() for x in \
  context.portal_catalog(selection_report=selection_report,
                         portal_type='Task Report',
                         simulation_state=context.getPortalReservedInventoryStateList()+
                                          context.getPortalCurrentInventoryStateList())])
task_line_list = []
for task in task_list:
  current_task_line_list = task.objectValues(portal_type=('Task Line', 'Task Report Line'))
  for task_line in current_task_line_list:
    update_kw = {}
    if task_line.getPortalType() == 'Task Report Line':
      simulation_related_list = task_line.getDeliveryRelatedValueList()
      causality_list = []
      for simulation_movement in simulation_related_list:
        causality_list.extend(simulation_movement.getOrderValueList())
      causality_len = len(causality_list)
      if causality_len == 0:
        # No task, so this was not decided at the beginning
        pass
      elif causality_len == 1:
        # There is a task, we should be able to compare quantity
        # date, resources....
        causality = causality_list[0]
        update_kw['initial_quantity'] = causality.getQuantity()
        update_kw['initial_start_date'] = causality.getStartDate()
        update_kw['initial_stop_date'] = causality.getStopDate()
        update_kw['real_quantity'] = task_line.getQuantity()
        update_kw['real_start_date'] = task_line.getStartDate()
        update_kw['real_stop_date'] = task_line.getStopDate()
      else:
        raise ValueError("This script more than one causality yet")
    elif task_line.getPortalType() == 'Task Line':
      update_kw['initial_quantity'] = task_line.getQuantity()
      update_kw['initial_start_date'] = task_line.getStartDate()
      update_kw['initial_stop_date'] = task_line.getStopDate()
    task_line_list.append(task_line.asContext(**update_kw))

return task_line_list
