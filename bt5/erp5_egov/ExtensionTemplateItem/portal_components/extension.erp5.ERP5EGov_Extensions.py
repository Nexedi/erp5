from zLOG import LOG
from Products.CMFCore.utils import getToolByName

def getPortalTypeWorklistDictForWorkflow(self, workflow_list):
  """
    return a dict containing portal_type and all informations about work_list
    of workflow :

    {'Subscription Form': {'signed': {'category': 'global',
                                         'count': 1,
                                         'description': 'Subscription Forms to archive',
                                         'formated_name': 'Subscription Forms to archive (%(count)s)',
                                         'formated_url': 'Base_viewSearchResultList?validation_state=signed&local_roles=Assignor&reset=1&portal_type=Subscription Form
',
                                         'id': 'subscription_forms_to_archive',
                                         'roles': ('Assignor',),
                                         'validation_state': 'signed'}
                          },
              .....

    }
  """
  portal_type_worklist_dict = {}
  portal_workflow = self.getPortalObject().portal_workflow
  types_tool = self.getPortalObject().portal_types

  if not isinstance(workflow_list, list):
    workflow = [workflow_list]

  for workflow in workflow_list:

    portal_type_list = [
      type_object.id for type_object in types_tool.listTypeInfo()
      if workflow in type_object.getTypeWorkflowList()
    ]

    workflow = getattr(portal_workflow, workflow, None)

    if workflow is not None:
      worklist_dict = workflow.worklists._mapping
      for portal_type in portal_type_list:
        for worklist_id, worklist in worklist_dict.items():
          state = None
          if worklist.var_matches.has_key('validation_state'):
            state=worklist.var_matches['validation_state']
          local_role_list=worklist.guard.roles
          if state is None:
            continue
          else:
            state=state[0]

          result = self.getPortalObject().portal_catalog(\
                                          portal_type=portal_type,
                                          local_roles=local_role_list,
                                          validation_state=state)
          if not len(result):
            continue

          if not portal_type_worklist_dict.has_key(portal_type):
            portal_type_worklist_dict[portal_type] = {}

          portal_type_worklist_dict[portal_type][state] = {}
          result_dict = portal_type_worklist_dict[portal_type][state]
          result_dict['id']=worklist_id
          result_dict['count']=len(result)
          result_dict['description']=worklist.description
          result_dict['validation_state']=state
          result_dict['formated_name']=worklist.actbox_name
          result_dict['formated_url']=worklist.actbox_url
          result_dict['formated_url']='Base_viewSearchResultList?validation_state=%s&local_roles=%s&reset=1&portal_type=%s'\
            % (state, local_role_list[0], portal_type)
          result_dict['category']=worklist.actbox_category
          result_dict.update(worklist.guard.__dict__)
  return portal_type_worklist_dict

def gessPortalType(self, attachment):
  portal = self.getPortalObject()
  portal_contributions = getToolByName(portal, 'portal_contributions', None)
  if portal_contributions is None:
    return None
  else:
    filename = attachment.filename
    mime_type = attachment.headers["Content-Type"]
    data = attachment.read()
    return portal_contributions._guessPortalType(filename, mime_type, data)

def setWorkflowList(self, portal_type_name, workflow_list=()):
  types_tool = self.getPortalObject().portal_types
  type_object = types_tool.getTypeInfo(portal_type_name)
  type_object.setTypeWorkflowList(list(workflow_list))

