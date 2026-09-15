"""Build the request line of one run of this Artificial Task.

The script moves the Artificial Task to the state `processing`. The script
finds or creates the Artificial Task Report. The script copies every comment
of the Artificial Task into one `user` line. The script then creates the first
`llm_request` line. The script leaves that line in the state `draft`.

`ArtificialTask_startAgent` calls this script and then starts the request
line. The test suite calls this script and starts the line later. There is
therefore one build path only.

The request line holds every parameter that reaches the provider. The send
path reads the line only. The script
`ArtificialTaskReportLine_writeRequestParameterList` writes those parameters.
That script is the one writer of the parameters.

The parameter `report` names the Artificial Task Report of the run. With no
value the script reads the report with `getFollowUpRelatedValue`. Production
passes no value.

The script answers the list `[report, request_line]`.

WARNING: one run must hold one open request only. Two open requests fork the
conversation and pay the Large Language Model twice. The script therefore
refuses a second build while one request is open. The script then answers
`[report, None]` and creates no line.
"""
import json

LINE_PORTAL_TYPE = 'Artificial Task Report Line'

artificial_task = context
portal = artificial_task.getPortalObject()

if report is None:
  report = artificial_task.getFollowUpRelatedValue(
    portal_type='Artificial Task Report')


def getRole(report_line):
  """Return the role of one line. Return an empty text on a broken line."""
  try:
    line_text_content = report_line.getTextContent()
    if not line_text_content:
      return ''
    return json.loads(line_text_content).get('role') or ''
  except Exception:
    return ''


def isRunOpen(open_report):
  """Return true when this report holds one request with no answer.

  One line in the state `started` is one open request. One line whose role is
  `llm_request` or `tool_request` and that has no answer is also one open
  request. An answer line points at the request line with the category
  `causality`.
  """
  answered_causality_list = []
  report_line_list = list(
    open_report.objectValues(portal_type=LINE_PORTAL_TYPE))
  for report_line in report_line_list:
    causality = report_line.getCausality()
    if causality:
      answered_causality_list.append(causality)
  for report_line in report_line_list:
    if report_line.getSimulationState() == 'started':
      return True
    if getRole(report_line) in ('llm_request', 'tool_request') and \
       report_line.getRelativeUrl() not in answered_causality_list:
      return True
  return False


if report is not None and isRunOpen(report):
  return [report, None]

if artificial_task.getSimulationState() == 'draft':
  artificial_task.plan()
if artificial_task.getSimulationState() != 'processing':
  artificial_task.start()

if report is None:
  report = portal.artificial_task_report_module.newContent(
    portal_type='Artificial Task Report',
    title=artificial_task.getTitle() or 'Artificial Task Report',
  )
  report.edit(follow_up_value=artificial_task)

next_int_index = 0
user_line_count = 0
for report_line in report.objectValues(portal_type=LINE_PORTAL_TYPE):
  int_index = report_line.getIntIndex() or 0
  if int_index > next_int_index:
    next_int_index = int_index
  if getRole(report_line) == 'user':
    user_line_count += 1
next_int_index += 1

def writeCausality(report_line, causality_document):
  """Write one causality link from one line to one Artificial Task Line."""
  if causality_document is None:
    return
  report_line.setCausalityValue(causality_document)


def getCommentLineList():
  """Return the Artificial Task Lines that hold the comments of the user.

  `ArtificialTask_getCommentPostList` reads the same list, in the same
  order. The position of one message is therefore the position of one
  Artificial Task Line.
  """
  # objectValues ignores simulation_state here, so filter in Python.
  try:
    return [x for x in artificial_task.objectValues(
      portal_type='Artificial Task Line',
      sort_on=[('creation_date', 'ascending')])
      if x.getSimulationState() in ('stopped', 'delivered')]
  except Exception:
    return []


comment_line_list = getCommentLineList()
message_list = artificial_task.ArtificialTask_getMessageList()
message_position = user_line_count
for message in message_list[user_line_count:]:
  user_line = report.newContent(
    portal_type=LINE_PORTAL_TYPE,
    int_index=next_int_index,
    text_content=json.dumps({
      'role': 'user',
      'content': message.get('content') or '',
    }, indent=1),
  )
  user_line.ArtificialTaskReportLine_writeRequestParameterList(
    artificial_task=artificial_task)
  if message_position < len(comment_line_list):
    writeCausality(user_line, comment_line_list[message_position])
  user_line.stop()
  next_int_index += 1
  message_position += 1

request_line = report.newContent(
  portal_type=LINE_PORTAL_TYPE,
  int_index=next_int_index,
  text_content=json.dumps({'role': 'llm_request'}, indent=1),
)
request_line.ArtificialTaskReportLine_writeRequestParameterList(
  artificial_task=artificial_task)

return [report, request_line]
