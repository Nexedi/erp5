from json import dumps, loads
artificial_task = context
simulation_state = artificial_task.getSimulationState()
content = ""
done = False
tool_message_list = []

if simulation_state ==  'processing':
  target_report_state = 'draft'
else:
  target_report_state = 'delivered'

artificial_task_report = artificial_task.getFollowUpRelatedValue(portal_type='Artificial Task Report')
if artificial_task_report is not None:
  report_line_list = artificial_task_report.objectValues(
    portal_type='Artificial Task Report Line',
    sort_on=[('creation_date', 'descending')],
  )
  if report_line_list and report_line_list[0].getSimulationState() == target_report_state:
    report_line = report_line_list[0]
    artificial_task_line = report_line.getFollowUpValue(portal_type='Artificial Task Line')
    message_list = loads(report_line.getTextContent() or "[]")
    if artificial_task_line:
      done = True
      content = artificial_task_line.getTextContent()
    else:
      done = False
      content = '\n'.join([m['content'] for m in message_list if m.get('role', '') == 'assistant'])
    tool_message_list = [m for m in message_list if m.get('role') == 'tool']

return dumps({
  "done": done,
  "content": content,
  "tool_message_list": tool_message_list,
})
