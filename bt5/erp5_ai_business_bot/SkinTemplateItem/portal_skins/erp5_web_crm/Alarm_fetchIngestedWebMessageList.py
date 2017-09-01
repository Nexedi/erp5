portal = context.getPortalObject()

sql_kw = {'portal_type': 'Web Message',
          'source_carrier_portal_type': ('Web Section', 'Web Site',),
          'simulation_state': 'draft'}


result_list = list(portal.portal_catalog(**sql_kw))
MAX_IN_ACTIVITIES = 5
starting_index = 0
while True:
  local_path_list = [r.getPath() for r in result_list[starting_index:starting_index+MAX_IN_ACTIVITIES]]
  if not local_path_list:
    break
  context.activate(activity='SQLQueue').Alarm_processIngestedWebMessageList(local_path_list)
  starting_index += MAX_IN_ACTIVITIES
