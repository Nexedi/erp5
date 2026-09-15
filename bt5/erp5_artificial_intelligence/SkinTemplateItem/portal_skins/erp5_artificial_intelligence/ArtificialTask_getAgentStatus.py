"""Return the status of the agent of this Artificial Task as JSON.

The keys are `done`, `failed`, `failure_text`, `content`, `state`,
`line_count` and `tool_message_list`.

`done` means that the run ended. One failed run has ended, so `failed` and
`done` are both true for one failed run.

WARNING: this script must never raise on one broken line. One line that holds
no JSON is skipped.
"""
import json

# `ArtificialTaskReportLine_processRequest` writes this prefix on the last
# Artificial Task Line of one failed run.
FAILURE_PREFIX = 'The run failed.'


def getPayload(report_line):
  """Return the payload of one line. Return an empty map on a broken line."""
  try:
    line_text_content = report_line.getTextContent()
    if not line_text_content:
      return {}
    payload = json.loads(line_text_content)
    if not isinstance(payload, dict):
      return {}
    return payload
  except Exception:
    return {}


artificial_task = context
simulation_state = artificial_task.getSimulationState()

done = False
content = ''
line_count = 0
tool_message_list = []
error_text_list = []

report = artificial_task.getFollowUpRelatedValue(
  portal_type='Artificial Task Report')

if report is not None:
  sort_key_list = []
  for report_line in report.objectValues(
      portal_type='Artificial Task Report Line'):
    sort_key_list.append(
      (report_line.getIntIndex() or 0, report_line.getId(), report_line))
  sort_key_list.sort()
  line_count = len(sort_key_list)

  for int_index, line_id, report_line in sort_key_list:
    payload = getPayload(report_line)
    if payload.get('role') in ('assistant', 'tool'):
      tool_message_list.append(payload)
    elif payload.get('role') == 'error':
      error_text_list.append(payload.get('content') or '')

  if simulation_state == 'processing' and sort_key_list:
    newest_line = sort_key_list[-1][2]
    newest_payload = getPayload(newest_line)
    content = 'The newest line is %s. The role is %s. The state is %s.' % (
      newest_line.getRelativeUrl(),
      newest_payload.get('role') or 'none',
      newest_line.getSimulationState(),
    )

if simulation_state == 'responded':
  done = True
  artificial_task_line_list = list(artificial_task.objectValues(
    portal_type='Artificial Task Line',
    sort_on=[('creation_date', 'ascending')]))
  if artificial_task_line_list:
    content = artificial_task_line_list[-1].getTextContent() or ''

elif simulation_state == 'cancelled':
  done = True
  if report is not None:
    for report_line in report.objectValues(
        portal_type='Artificial Task Report Line'):
      payload = getPayload(report_line)
      if payload.get('role') == 'error':
        content = payload.get('content') or ''

# One failed run writes one error line on the report. The same run writes one
# Artificial Task Line that starts with FAILURE_PREFIX. One marker is enough.
failed = False
failure_text = ''
if done and (error_text_list or content.startswith(FAILURE_PREFIX)):
  failed = True
  if error_text_list:
    failure_text = error_text_list[-1]
  else:
    failure_text = content

return json.dumps({
  'done': done,
  'failed': failed,
  'failure_text': failure_text,
  'content': content,
  'state': simulation_state,
  'line_count': line_count,
  'tool_message_list': tool_message_list,
}, indent=1)
