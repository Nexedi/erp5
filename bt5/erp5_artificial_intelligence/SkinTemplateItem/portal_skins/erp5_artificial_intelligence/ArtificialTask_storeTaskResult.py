import json

artificial_task = context
portal = artificial_task.getPortalObject()

if message_list and isinstance(message_list, str):
  message_list = json.loads(message_list)
message_list = message_list or []

line = artificial_task.newContent(
  portal_type='Artificial Task Line',
  text_content=content
)

artificial_task_report = artificial_task.getFollowUpRelatedValue(portal_type='Artificial Task Report')
if artificial_task_report is None:
  artificial_task_report = portal.artificial_task_report_module.newContent(portal_type='Artificial Task Report')
  artificial_task_report.edit(follow_up_value=artificial_task)

artificial_task_report_line = artificial_task_report.newContent(
  portal_type='Artificial Task Report Line',
  text_content=json.dumps(message_list, indent=2),
  follow_up_value=line
)

line.deliver()
artificial_task_report_line.deliver()
if artificial_task.getSimulationState() == 'planned':
  artificial_task.start()

artificial_task.respond()
