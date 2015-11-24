def Listbox_getListMethodName(self, field):
  """ XXXX"""
  list_method = field.get_value('list_method')
  try:
    list_method_name = getattr(list_method, 'method_name')
  except AttributeError:
    list_method_name = list_method

  return list_method_name

def Field_getSubFieldKeyDict(self, field, field_id, key=None):
  """XXX"""
  return field.generate_subfield_key(field_id, key=key)

def Field_getDefaultValue(self, field, key, value, REQUEST):
  return field._get_default(key, value, REQUEST)

def WorkflowTool_listActionParameterList(self):
  action_list = self.listActions()
  info = self._getOAI(None)

  workflow_dict = {}
  result_list = []

  for action in action_list:
    if (action['workflow_id'] not in workflow_dict):
      workflow = self.getWorkflowById(action['workflow_id'])
      workflow_dict[action['workflow_id']] = workflow.getWorklistVariableMatchDict(info, check_guard=False)

    query = workflow_dict[action['workflow_id']][action['worklist_id']]
    query.pop('metadata')
    result_list.append({
      'count': action['count'],
      'name': action['name'],
      'local_roles': query.pop('local_roles'),
      'query': query
    })


  return result_list
