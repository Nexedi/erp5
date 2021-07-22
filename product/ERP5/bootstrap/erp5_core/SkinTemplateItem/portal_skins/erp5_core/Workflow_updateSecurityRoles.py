ACTIVITY_GROUPING_COUNT = 100
def updateRoleMappings(self, REQUEST=None):
  """
  Changes permissions of all objects related to this workflow
  """
  portal_type_id_list = self.getPortalTypeListForWorkflow()
  if portal_type_id_list:
    object_list = self.portal_catalog(portal_type=portal_type_id_list, limit=None)
    portal_activities = self.portal_activities
    object_path_list = [x.path for x in object_list]
    for i in xrange(0, len(object_list), ACTIVITY_GROUPING_COUNT):
      current_path_list = object_path_list[i:i+ACTIVITY_GROUPING_COUNT]
      portal_activities.activate(activity='SQLQueue',
                                  priority=3)\
            .callMethodOnObjectList(current_path_list,
                                    'updateRoleMappingsFor',
                                    wf_id = self.getId())
  else:
    object_list = []
  if REQUEST is not None:
    message = 'No object updated.'
    if object_list:
      message = '%d object(s) updated: \n %s.' % (len(object_list),
        ', '.join([o.getTitleOrId() + ' (' + o.getPortalType() + ')'
                   for o in object_list]))
    return message
  else:
    return len(object_list)

message = updateRoleMappings(context, context.REQUEST)
return context.Base_redirect(form_id, keep_items={'portal_status_message': message})
