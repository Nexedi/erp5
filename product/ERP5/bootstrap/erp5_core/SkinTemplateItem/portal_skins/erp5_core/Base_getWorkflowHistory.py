from ZODB.POSException import ConflictError

history_name_list = ['building_history', ' installation_history', 'history']

history = {}

portal_workflow = context.getPortalObject().portal_workflow
workflow_id_list = [x[0] for x in context.getWorkflowStateItemList()]

for history_name in history_name_list:
  
  for wf_id in workflow_id_list:
    
    list_history_item = None
    try:
      list_history_item = portal_workflow.getInfoFor(ob=context, name=history_name, wf_id=wf_id)
    except ConflictError:
      raise
    except Exception:
      pass

    if list_history_item not in ((), None):
      
      history_element_title_list = []
      for history_element_title in list_history_item[-1].keys():
        if history_element_title <> history_name:
          new_title = history_element_title.replace('_', ' ').title()
          history_element_title_list.append(new_title)

      history_item_list = []
      for history_item in list_history_item:
        history_item_info = ()
        for history_element_title in list_history_item[-1].keys():
          if history_element_title <> history_name:
            history_item_info += (history_item.get(history_element_title),)
        history_item_list.append(history_item_info)
      history_item_list.reverse()

      wf_history = {}
      wf_history['title_list'] = history_element_title_list
      wf_history['item_list']  = history_item_list
      history[wf_id] = wf_history


return history
