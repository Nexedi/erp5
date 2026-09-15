"""Return the comment list of this Artificial Task.

One dictionary per Artificial Task Line: `date`, `text`, `tool_message_list`,
`response`. BBB: the script also reads `follow_up` and one JSON list, for old
runs.

WARNING: this script must never raise. One caller is the user interface of the
agent. A defect of one line must not stop the whole list.
"""
import json

LINE_PORTAL_TYPE = 'Artificial Task Report Line'
MESSAGE_ROLE_TUPLE = ('tool', 'assistant')
COMMENT_STATE_TUPLE = ('stopped', 'delivered')

artificial_task = context
comment_list = []


def getReportLine(task_line):
  """Return the Artificial Task Report Line of one Artificial Task Line.

  BBB: `follow_up` is the last read.
  """
  report_line = task_line.getCausalityValue(portal_type=LINE_PORTAL_TYPE)
  if report_line is not None:
    return report_line
  report_line = task_line.getCausalityRelatedValue(
    portal_type=LINE_PORTAL_TYPE)
  if report_line is not None:
    return report_line
  return task_line.getFollowUpRelatedValue(portal_type=LINE_PORTAL_TYPE)


def getToolMessageList(report_line):
  """Return the tool messages and the assistant messages of one line.

  BBB: one line holds a JSON list or a JSON map.
  """
  if report_line is None:
    return []
  try:
    payload = json.loads(report_line.getTextContent() or 'null')
  except Exception:
    return []
  if isinstance(payload, dict):
    payload = [payload]
  if not isinstance(payload, list):
    return []
  message_list = []
  for message in payload:
    if not isinstance(message, dict):
      continue
    if message.get('role', '') in MESSAGE_ROLE_TUPLE:
      message_list.append(message)
  return message_list


# objectValues ignores simulation_state here, so filter in Python.
for task_line in artificial_task.objectValues(
    portal_type='Artificial Task Line',
    sort_on=[('creation_date', 'ascending')]):
  if task_line.getSimulationState() not in COMMENT_STATE_TUPLE:
    continue
  comment_list.append(dict(
    date=task_line.getCreationDate().ISO8601(),
    text=task_line.getTextContent(),
    tool_message_list=json.dumps(getToolMessageList(
      getReportLine(task_line))),
    response=task_line.getSimulationState() == 'delivered',
  ))

return comment_list
