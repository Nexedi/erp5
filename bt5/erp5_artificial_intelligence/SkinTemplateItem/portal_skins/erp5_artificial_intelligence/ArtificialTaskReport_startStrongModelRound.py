"""Start one new round of this Artificial Task Report on one other model.

Two callers use this script. The tool
`ArtificialTask_escalateToStrongModel` calls this script when the model asks
for one stronger model. The failure path of
`ArtificialTaskReportLine_processRequest` calls this script for the three
escalation triggers.

The script creates one `llm_request` line, writes the new model on that line,
and starts the line. The conversation does not change. The model of the next
round changes. The send path reads the line only, so the write of the model on
the line is the write that changes the round.

The script also writes one `Artificial Task Line` that records the escalation.
That line rests in the state `Stopped`. That line waits for no human. That
line is the escalation counter.

The parameter `source_line` names the line of the run that runs now. The new
line copies the send parameters of that line. The parameter `model` names the
new model. The parameter `reason` holds the text of the model, or the text of
the failure.

The script answers the new line. The script answers None when one guard
refuses. A refusal writes nothing.

WARNING: one run must hold one open request only. Two open requests fork the
conversation and pay the Large Language Model two times. The script therefore
refuses while one other line of this report is started.
"""
import json

ESCALATION_TOOL_ID = 'ArtificialTask_escalateToStrongModel'
ESCALATION_PATH = 'portal_callables/ArtificialTask_escalateToStrongModel'
LINE_PORTAL_TYPE = 'Artificial Task Report Line'
MAXIMUM_LLM_REQUEST_COUNT = 20

report = context
portal = report.getPortalObject()
artificial_task = report.getFollowUpValue(portal_type='Artificial Task')


def getRole(report_line):
  """Return the role of one line. Return an empty text on a broken line."""
  try:
    line_text_content = report_line.getTextContent()
    if not line_text_content:
      return ''
    return json.loads(line_text_content).get('role') or ''
  except Exception:
    return ''


def getNextIntIndex():
  """Return the next free value of int_index in this report."""
  next_int_index = 0
  for report_line in report.objectValues(portal_type=LINE_PORTAL_TYPE):
    int_index = report_line.getIntIndex() or 0
    if int_index > next_int_index:
      next_int_index = int_index
  return next_int_index + 1


def countEscalation():
  """Return how many escalations this Artificial Task already holds."""
  count = 0
  for task_line in artificial_task.objectValues(
      portal_type='Artificial Task Line'):
    if task_line.getSpecialise() == ESCALATION_PATH:
      count += 1
  return count


def countLlmRequest():
  """Return how many `llm_request` lines this report holds."""
  count = 0
  for report_line in report.objectValues(portal_type=LINE_PORTAL_TYPE):
    if getRole(report_line) == 'llm_request':
      count += 1
  return count


def isOtherRequestOpen():
  """Return true when one line that is not the source line is started."""
  source_url = source_line.getRelativeUrl()
  for report_line in report.objectValues(portal_type=LINE_PORTAL_TYPE):
    if report_line.getRelativeUrl() == source_url:
      continue
    if report_line.getSimulationState() == 'started':
      return True
  return False


def getModelResource(model_reference):
  """Return the validated Service of one model, or None.

  No Service document is needed. A line with
  no Service holds the model in the property `model` only.
  """
  try:
    service_brain_list = list(portal.portal_catalog(
      portal_type='Service', reference=model_reference,
      validation_state='validated', limit=2))
  except Exception:
    return None
  for service_brain in service_brain_list:
    return service_brain.getObject()
  return None


def getEscalationCallable():
  """Return the Python Script of the escalation tool, or None.

  WARNING: do not call `getattr` on `portal_callables`. That folder acquires.
  This function reads the own identifiers of the folder only.
  """
  try:
    callable_folder = portal.portal_callables
    if ESCALATION_TOOL_ID not in list(callable_folder.objectIds()):
      return None
    for candidate in callable_folder.objectValues():
      if candidate.getId() == ESCALATION_TOOL_ID:
        return candidate
  except Exception:
    return None
  return None


def newEscalationLine(new_model):
  """Write the record of one escalation on the Artificial Task.

  The state is `Stopped` and not `Planned`. `Planned` is the state of one
  deferred line that waits for one human. One escalation needs no human.
  """
  task_line = artificial_task.newContent(
    portal_type='Artificial Task Line',
    text_content=json.dumps({
      'escalation': ESCALATION_TOOL_ID,
      'model': new_model,
      'reason': reason or '',
    }, indent=1),
  )
  tool_document = getEscalationCallable()
  if tool_document is not None:
    task_line.setSpecialiseValue(tool_document)
  causality_document = source_line.getCausalityValue()
  if causality_document is not None:
    task_line.setCausalityValue(causality_document)
  task_line.stop()
  return task_line


# Each guard answers None and writes nothing.
if artificial_task is None:
  return None
if source_line is None:
  return None
if not model:
  return None
# A run that ended must never escalate. The end of the run deleted the file
# at the provider, so a later round names a file that does not exist.
if artificial_task.getSimulationState() != 'processing':
  return None
if countEscalation() >= 1:
  return None
if isOtherRequestOpen():
  return None
if countLlmRequest() >= MAXIMUM_LLM_REQUEST_COUNT:
  return None

request_line = report.newContent(
  portal_type=LINE_PORTAL_TYPE,
  int_index=getNextIntIndex(),
  text_content=json.dumps({'role': 'llm_request'}, indent=1),
)
request_line.ArtificialTaskReportLine_writeRequestParameterList(
  source_line=source_line)

# The source line holds the old model. Write the new model on the property,
# on the resource and in the JSON record of the line.
request_line.setModel(model)
model_service = getModelResource(model)
if model_service is not None:
  request_line.setResourceValue(model_service)
else:
  # The source line can hold the Service of the old model.
  request_line.setResourceValue(None)
payload = json.loads(request_line.getTextContent() or '{}')
payload['model'] = model
request_line.setTextContent(json.dumps(payload, indent=1))

newEscalationLine(model)
request_line.start()
return request_line
