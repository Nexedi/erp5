from zLOG import LOG

def sendCrendentialsByEMail(self, login, password, user_email):
  activity_tool = self.getPortalObject().portal_activities
  from Products.MailHost.MailHost import MailHostError
  from Products.CMFActivity.ActivityTool import Message
  import socket
  portal = activity_tool.getPortalObject()

  mail_text="""From: %s
To: %s
Subject: %s

Thanks for registrering to SAFI, now you can connect in on www.safi.sn with the followin credentials :

Login: %s
Password: %s
""" % ('fabien@nexedi.com', user_email, 'your credential for www.safi.sn',
     login, password)

  try:
    activity_tool.MailHost.send( mail_text )
  except (socket.error, MailHostError), message:
    LOG('ActivityTool.notifyUser', 0, 'Mail containing failure information failed to be sent: %s.' % (message))

def getPoralTypeListForWorkflow(self, workflow):
  '''
    return a list of portal_types that use workflow
  '''
  pw = self.portal_workflow
  cbt = pw._chains_by_type
  ti = pw._listTypeInfo()

  portal_type_list = []
  for t in ti:
    id = t.getId()
    if cbt is not None and cbt.has_key(id) and workflow in cbt[id]:
      portal_type_list.append(id)

  return portal_type_list

def getPortalTypeWorklistDictForWorkflow(self, workflow):
  """
    return a dict containing portal_type and all informations about work_list
    of workflow :

    { 'Declaration TVA': {  'id':'applications_to_submit',
                            'description':'Applications to submit',
                            'validation_state':'draft',
                            'formated_name':'Applications to submit (%(count)s)'
                            'formated_url':'Base_viewSearchResultList?validation_state=submitted&local_roles=%(local_roles)s&reset=1&portal_type=%(portal_type)s',
                            'category':'global',
                            'count':2,
                            'roles':['Owner'],
                          },
              .....
    }
  """
  portal_type_list = self.getPoralTypeListForWorkflow(self, workflow=workflow)
  portal_workflow = self.getPortalObject().portal_workflow
  workflow = getattr(portal_workflow, workflow, None)

  portal_type_worklist_dict = {}

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

        result = self.getPortalObject().portal_catalog(portal_type=portal_type,
                                        local_roles=local_role_list,
                                        validation_state=state)
        if not len(result):
          continue

        if not portal_type_worklist_dict.has_key(portal_type):
          portal_type_worklist_dict[portal_type] = {}

        portal_type_worklist_dict[portal_type][worklist_id] = {}
        result_dict = portal_type_worklist_dict[portal_type][worklist_id]
        result_dict['id']=worklist_id
        result_dict['count']=len(result)
        result_dict['description']=worklist.description
        result_dict['validation_state']=state
        result_dict['formated_name']=worklist.actbox_name
        result_dict['formated_url']=worklist.actbox_url
        result_dict['formated_url']='Base_viewSearchResultList?validation_state=%s&local_roles=%s&reset=1&portal_type=%s'\
          % (state[0], local_role_list[0], portal_type)
        result_dict['category']=worklist.actbox_category
        result_dict.update(worklist.guard.__dict__)
  return portal_type_worklist_dict

