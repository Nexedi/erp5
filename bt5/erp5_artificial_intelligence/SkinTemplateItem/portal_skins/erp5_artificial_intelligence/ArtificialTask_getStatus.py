from json import dumps, loads
artificial_task = context
simulation_state = artificial_task.getSimulationState()

streaming_content = ""
tool_message_list = []
if simulation_state == 'processing':
  artificial_task_report = artificial_task.getFollowUpRelatedValue(portal_type='Artificial Task Report')
  if artificial_task_report is not None:
    report_line_list = artificial_task_report.objectValues(
      portal_type='Artificial Task Report Line',
      sort_on=[('creation_date', 'descending')]
    )
    if report_line_list and report_line_list[0].getFollowUpValue() is None:
      report_line = report_line_list[0]
      streaming_content = getattr(report_line, 'streaming_content', '')
      message_list = loads(report_line.getTextContent() or "[]")
      tool_message_list = [m for m in message_list if m.get('role') == 'tool']

return dumps({
  "simulation_state": simulation_state,
  "responded": simulation_state == "responded",
  "streaming_content": streaming_content,
  "tool_message_list": tool_message_list,
})
