from zLOG import LOG, WARNING

def Alarm_updatePersonModulePasswordInformation(self, **kw):
  """
    Decoupling a TioLive Instance, we need to make sure that all the
    users must have the password updated from TioLive Master.
  """
  portal = self.getPortalObject()
  person_list = portal.person_module.searchFolder(portal_type="Person",
                                                  reference="!= Null")
  person_dict = {}
  for person in person_list:
    person_dict[person.getReference()] = person.getObject()
  
  kw = dict(reference_list=person_dict.keys())
  result = eval(portal.portal_wizard.callRemoteProxyMethod(
                       'WitchTool_getUserPasswordInformationDict',
                       use_cache=0,
                       ignore_exceptions=0,
                       **kw))
  if result is None:
    return False

  for reference, password in result.iteritems():
    person_dict[reference].password = password

  return result.keys()

def Alarm_hideChangePasswordAction(self):
  """
    The TioLive Instance has an action to change the user password 
    and it redirects to TioLive Master.

    Once the instance is going to be decoupled, such action must be hidden,
    because the password management must be done locally instead of
    Tiolive Master.
  """
  for action in self.portal_actions.listActions():
    if action.id == 'tiolive_change_password':
      action.visible = 0
