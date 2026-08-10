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
    report_text_content_list = json.loads(report_line.getTextContent())
    report_text_content_list = [x for x in report_text_content_list if x.get('role', '') == 'tool']
  else:
    report_text_content_list = []

  comment_list.append((dict(
    date=line.getCreationDate().ISO8601(),
    text=line.getTextContent(),
    report_text_content_list = json.dumps(report_text_content_list),
    response = True if line.getSimulationState() == 'delivered' else False
  )))

return comment_list
