import json
artifical_task = context
comment_list = []
for line in artifical_task.objectValues(
  portal_type='Artificial Task Line',
  sort_on=[('creation_date', 'ascending')],
  simulation_state = ('stopped', 'delivered')
 ):
  report_line = line.getFollowUpRelatedValue(portal_type='Artificial Task Report Line')
  if report_line:
    report_message_list = json.loads(report_line.getTextContent())
    tool_message_list = [x for x in report_message_list if x.get('role', '') in ('tool', 'assistant')]
  else:
    tool_message_list = []

  comment_list.append((dict(
    date=line.getCreationDate().ISO8601(),
    text=line.getTextContent(),
    tool_message_list = json.dumps(tool_message_list),
    response = True if line.getSimulationState() == 'delivered' else False
  )))

return comment_list
