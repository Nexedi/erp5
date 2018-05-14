from Acquisition import aq_self, aq_base, aq_inner

def Base_aqSelf(self):
  return aq_self(self)

def Base_aqBase(self):
  return aq_base(self)

def Base_aqInner(self):
  return aq_inner(self)

def Portal_abortTransaction(self):
  import transaction
  transaction.abort()

def Field_getSubFieldKeyDict(self, field, field_id, key=None):
  """XXX"""
  return field.generate_subfield_key(field_id, key=key)

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
