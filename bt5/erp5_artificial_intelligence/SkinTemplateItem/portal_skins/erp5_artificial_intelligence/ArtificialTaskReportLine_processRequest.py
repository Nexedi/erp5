"""Run one request of one Artificial Task Report.

The script runs inside one activity. The script performs one outward call.
The script writes the answer as a new Artificial Task Report Line. The script
then decides the next step and starts one new activity.

WARNING: this script must never raise. A raise fails the activity for good
(`max_retry=0`). The line stays `started` and the paid answer is lost. Every
failure becomes an `error` line and ends the Artificial Task.

WARNING: this script must never run inside one web request. A web request
bypasses the workflow, the permission and the serialization tag. Two guards
stop a web request. The first guard raises `Unauthorized` when the caller
passes `REQUEST`. The second guard reads the simulation state of the line.

The parameter `response` holds one answer of the connector. The Alarm gives
that answer after the provider ends the work. A failed job is one response
with the status `failed`. There is no second parameter for an error. A
transport error is not an answer, and a transport error must never end one
run.

WARNING: the private key `_llm_file` must never reach the provider. The
script `ArtificialTaskReport_getMessageList` puts the binary of the aggregate
under that key. This script removes every such key before the send. This
script then passes the binary as `attachment_data`.

WARNING: never pass `file_id` to `retrieveResponse`. That method deletes the
file on the first done answer. This script calls `removeFile` at the end of
the run.

WARNING: the model chooses the name of the tool. The function `resolveTool`
is the only allow list. Do not call `getattr` on `portal_callables` with a
name that comes from the model. `getattr` on that folder acquires. A name
such as `Base_edit` resolves through acquisition to one skin script.
"""
import json
from DateTime import DateTime
from zExceptions import Unauthorized

# The tools that need one human validation come from a script, not a
# constant. A customer skin folder overrides it.
DEFERRABLE_TOOL_SCRIPT_ID = 'ArtificialTask_getDeferrableToolIdList'

MAXIMUM_TOOL_REQUEST_COUNT = 8
MAXIMUM_LLM_REQUEST_COUNT = 20

LINE_PORTAL_TYPE = 'Artificial Task Report Line'
TOOL_NAME_CHARACTER_SET = (
  'abcdefghijklmnopqrstuvwxyz'
  'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  '0123456789_')

# The escalation tool writes the round of the strong model itself.
ESCALATION_TOOL_ID = 'ArtificialTask_escalateToStrongModel'
ESCALATION_ACCEPTED_PREFIX = u'escalation accepted'
ESCALATION_AFTER_DEFER_TEXT = (
  u'escalation refused. this run already deferred one tool call.')
STRONG_MODEL_SCRIPT_ID = 'ArtificialTask_getStrongModel'
STRONG_ROUND_SCRIPT_ID = 'ArtificialTaskReport_startStrongModelRound'

line = context

# Zope passes `REQUEST` to every published script. One activity passes no
# `REQUEST`. The raise therefore stops every call that comes over HTTP.
if REQUEST is not None:
  raise Unauthorized

if line.getSimulationState() != 'started':
  return 'refused: the line is not started'

portal = line.getPortalObject()
report = line.getParentValue()
artificial_task = report.getFollowUpValue(portal_type='Artificial Task')
line_relative_url = line.getRelativeUrl()

# A list, because a nested function writes the token count of this response.
total_token_count_list = [0]


def safeText(value):
  """Return one text of one value. This function never raises.

  A message of one exception can hold a character that is not ASCII. The
  built in function `str` raises on such a message.
  """
  try:
    return u'%s' % (value, )
  except Exception:
    pass
  try:
    return u'%s' % (repr(value), )
  except Exception:
    return u'the text of this value is not readable'


def getRole(report_line):
  """Return the role of one line. Return an empty text on a broken line."""
  try:
    line_text_content = report_line.getTextContent()
    if not line_text_content:
      return ''
    return json.loads(line_text_content).get('role') or ''
  except Exception:
    return ''


def getSortedLineList():
  """Return every line of this report, in the order of int_index."""
  sort_key_list = []
  for report_line in report.objectValues(portal_type=LINE_PORTAL_TYPE):
    sort_key_list.append(
      (report_line.getIntIndex() or 0, report_line.getId(), report_line))
  sort_key_list.sort()
  return [x[2] for x in sort_key_list]


def getTurnLineList():
  """Return the lines of the current turn.

  One turn starts after the newest line whose role is `user`. A bound counts
  the lines of the current turn only. A bound must not count the lines of an
  earlier turn.
  """
  report_line_list = getSortedLineList()
  start_position = 0
  position = 0
  for report_line in report_line_list:
    position += 1
    if getRole(report_line) == 'user':
      start_position = position
  return report_line_list[start_position:]


def countTurnRole(wanted_role):
  """Return how many lines of the current turn hold this role."""
  count = 0
  for report_line in getTurnLineList():
    if getRole(report_line) == wanted_role:
      count += 1
  return count


def getNextIntIndex():
  """Return the next free value of int_index in this report."""
  next_int_index = 0
  for report_line in report.objectValues(portal_type=LINE_PORTAL_TYPE):
    int_index = report_line.getIntIndex() or 0
    if int_index > next_int_index:
      next_int_index = int_index
  return next_int_index + 1


def getTokenQuantityUnit():
  """Return `unit/token`, or None when that category does not exist.

  No business template of this repository holds the quantity unit `token`,
  so the unit can be absent. A write of one unit that does not exist raises.
  """
  try:
    if portal.portal_categories.quantity_unit.restrictedTraverse(
        'unit/token', None) is None:
      return None
  except Exception:
    return None
  return 'unit/token'


def writeQuantity(report_line, quantity):
  """Write one token quantity on one line. Never raise.

  The Artificial Task Report Line is one Movement. ERP5 therefore holds the
  token count in `quantity`. ERP5 gives every new Movement the default
  `quantity=1.0`. A line that keeps 1.0 holds one false count. This function
  therefore writes on every line of this script, also when the count is 0.
  """
  try:
    quantity_unit = getTokenQuantityUnit()
    if quantity_unit is None:
      report_line.setQuantity(quantity)
    else:
      report_line.edit(quantity=quantity, quantity_unit=quantity_unit)
  except Exception:
    pass


def writeTokenCount(report_line):
  """Write the token count of the response on one terminal line.

  The count is 0 in three cases. The provider answers a `usage` of zeros for
  one cancelled response. A tool answer reads no provider. An error before the
  read of `usage` holds no count.
  """
  writeQuantity(report_line, total_token_count_list[0])


def writeCausality(document, causality_document):
  """Write one causality link from one document to one other document."""
  if document is None or causality_document is None:
    return
  document.setCausalityValue(causality_document)


def getModelResource(model_reference):
  """Return the validated Service of one model, or None.

  A draft Service and a cancelled Service are not one usable resource. The
  caller then writes no resource, and the text property `model` stays the
  only record of the model.
  """
  if not model_reference:
    return None
  try:
    service_brain_list = list(portal.portal_catalog(
      portal_type='Service', reference=model_reference,
      validation_state='validated', limit=2))
  except Exception:
    return None
  for service_brain in service_brain_list:
    return service_brain.getObject()
  return None


def writeAnswerModel(report_line, model_reference):
  """Write the model that the provider answered on one line.

  The provider can answer one model name that is longer than the name of the
  request. The answer line holds the answer of the provider.
  """
  if not model_reference:
    return
  report_line.setModel(model_reference)
  model_service = getModelResource(model_reference)
  if model_service is not None:
    report_line.setResourceValue(model_service)


def copySendParameterList(report_line):
  """Copy the send parameters of the request line on one other line.

  Every line of one run holds the same model and the same connector. A
  reader of one answer line therefore needs no other document.
  """
  report_line.edit(
    connector_value=line.getConnectorValue(),
    model=line.getModel(),
    request_parameter=line.getRequestParameter(),
    is_background_enabled=line.getIsBackgroundEnabled(),
  )
  resource_value = line.getResourceValue()
  if resource_value is not None:
    report_line.setResourceValue(resource_value)


def newAnswerLine(answer_payload):
  """Create one answer line in the state `stopped`.

  The answer line holds the model and the connector of the request line.
  The answer line also holds the token count.
  """
  answer_line = report.newContent(
    portal_type=LINE_PORTAL_TYPE,
    int_index=getNextIntIndex(),
    causality_value=line,
    text_content=json.dumps(answer_payload, indent=1),
  )
  copySendParameterList(answer_line)
  writeTokenCount(answer_line)
  answer_line.stop()
  return answer_line


def stopRequestLine():
  """Move the request line to the state `stopped`."""
  if line.getSimulationState() == 'started':
    line.stop()
  line.edit(stop_date=DateTime())


def removeProviderFile():
  """Delete the file of this run at the provider. This function never raises.

  The key `file_id` lives inside the property `request_parameter`. The value
  comes from the upload of the first round. Every line of the run copies the
  property, so the terminal line also holds the value.

  A failed delete leaves one paid file at the provider. A raise ends one
  finished run. The cost of one file is smaller than the cost of one lost
  run. This function therefore never raises.
  """
  try:
    request_parameter = line.getRequestParameter()
    if not request_parameter:
      return
    parameter_dict = json.loads(request_parameter)
    if not isinstance(parameter_dict, dict):
      return
    file_id = parameter_dict.get('file_id')
    if not file_id:
      return
    file_connector = line.getConnectorValue()
    if file_connector is None:
      return
    file_connector.removeFile(file_id)
  except Exception:
    pass


def finishRun(final_text, answer_document=None):
  """Write the final Artificial Task Line and answer the Artificial Task.

  The Artificial Task Line points at the Artificial Task Report Line that
  holds the answer. The category is `causality`. The reader of the Artificial
  Task Report Line calls `getCausalityRelatedValue`.

  This line is the terminal line of the run. Delete the file of the run here.
  """
  removeProviderFile()
  if artificial_task is None:
    return
  artificial_task_line = artificial_task.newContent(
    portal_type='Artificial Task Line',
    text_content=final_text,
  )
  writeCausality(artificial_task_line, answer_document)
  artificial_task_line.stop()
  if artificial_task.getSimulationState() == 'processing':
    artificial_task.respond()


def failRun(error_text):
  """Write one error line and end the Artificial Task.

  WARNING: this function must never raise. This function runs in the last
  `except` block of the script.

  The run ends here. Delete the file of the run before the error line.
  """
  removeProviderFile()
  safe_error_text = u'the text of this error is not readable'
  error_line = None
  try:
    safe_error_text = safeText(error_text)
  except Exception:
    pass
  try:
    error_line = report.newContent(
      portal_type=LINE_PORTAL_TYPE,
      int_index=getNextIntIndex(),
      causality_value=line,
      text_content=json.dumps(
        {'role': 'error', 'content': safe_error_text}, indent=1),
    )
    copySendParameterList(error_line)
    writeTokenCount(error_line)
    error_line.stop()
  except Exception:
    pass
  try:
    stopRequestLine()
  except Exception:
    pass
  if artificial_task is None:
    return
  try:
    if artificial_task.getSimulationState() != 'processing':
      return
  except Exception:
    return
  try:
    artificial_task.cancel(comment=safe_error_text)
    return
  except Exception:
    pass
  # WARNING: `artificial_task_workflow` holds no `cancel` from `processing`.
  # Write the error as the answer, or the task stays `processing` for ever.
  try:
    failure_line = artificial_task.newContent(
      portal_type='Artificial Task Line',
      text_content=u'The run failed. %s' % (safe_error_text, ),
    )
    writeCausality(failure_line, error_line)
    failure_line.stop()
    artificial_task.respond()
  except Exception:
    pass


def tryRuleDrivenEscalation(reason_text):
  """Start one round on the strong model after one failure. Never raise.

  A model that fails calls no tool. Three triggers need this function. The
  triggers are one provider error, one answer that does not parse, and one
  answer with no tool call and no text.

  The function answers 1 when the strong round started. The function answers
  0 in every other case, and the caller then ends the run.

  The script `ArtificialTaskReport_startStrongModelRound` holds every guard.
  One run therefore escalates one time at most, by the tool or by this rule,
  and never by both.
  """
  if artificial_task is None:
    return 0
  try:
    strong_model_method = getattr(
      artificial_task, STRONG_MODEL_SCRIPT_ID, None)
    if strong_model_method is None:
      return 0
    strong_model = strong_model_method()
  except Exception:
    return 0
  if not strong_model:
    return 0
  try:
    strong_round_method = getattr(report, STRONG_ROUND_SCRIPT_ID, None)
    if strong_round_method is None:
      return 0
    request_line = strong_round_method(
      source_line=line, model=strong_model, reason=reason_text)
  except Exception:
    return 0
  if request_line is None:
    return 0
  try:
    stopRequestLine()
  except Exception:
    pass
  return 1


def getToolCallName(tool_call):
  """Return the name of the tool of one tool call, or one empty text."""
  try:
    function_dict = tool_call.get('function') or {}
    return safeText(function_dict.get('name') or '')
  except Exception:
    return u''


def getDeferrableToolIdTuple():
  """Answer the tools that need one human validation, or None on one error.

  None means that the caller must stop the run. A missing script must never
  let one tool that writes run with no human validation.
  """
  try:
    method = getattr(portal, DEFERRABLE_TOOL_SCRIPT_ID, None)
    if method is None:
      return None
    answer = method()
    if answer is None:
      return ()
    return tuple([safeText(x) for x in answer])
  except Exception:
    return None


def isDeferredToolCall(tool_call, deferrable_tool_id_tuple):
  """Answer 1 when one human must approve this tool call."""
  return getToolCallName(tool_call) in deferrable_tool_id_tuple


def getCallableDocument(tool_name):
  """Return one own Python Script of `portal_callables`, or None.

  WARNING: do not call `getattr` on `portal_callables`. `getattr` acquires.
  This function reads the own identifiers of the folder only.
  """
  try:
    callable_folder = portal.portal_callables
    if tool_name not in list(callable_folder.objectIds()):
      return None
    for candidate in callable_folder.objectValues():
      if candidate.getId() == tool_name:
        return candidate
  except Exception:
    return None
  return None


def newDeferredLine(tool_call, answer_document):
  """Write one Artificial Task Line in the state Planned for one tool call.

  The harness must never run one deferred tool. One user reads the line and
  clicks Confirm. That click runs the tool.

  The line holds the tool call as text in `text_content`. The category
  `specialise` names the Python Script of `portal_callables`. The category
  `causality` names the answer line of the model.

  WARNING: do not use the category `resource` here. One Artificial Task Line
  is one Amount. `Amount.getQuantityUnit` calls `resource.getQuantityUnit()`.
  One Python Script has no such method, and the catalog indexing of the line
  then fails.

  WARNING: this function must never raise.
  """
  if artificial_task is None:
    return None
  tool_name = getToolCallName(tool_call)
  try:
    request_text = json.dumps(tool_call, indent=1)
  except Exception:
    request_text = safeText(tool_call)
  try:
    deferred_line = artificial_task.newContent(
      portal_type='Artificial Task Line',
      text_content=request_text,
    )
  except Exception:
    return None
  try:
    tool_document = getCallableDocument(tool_name)
    if tool_document is not None:
      deferred_line.setSpecialiseValue(tool_document)
  except Exception:
    pass
  try:
    writeCausality(deferred_line, answer_document)
  except Exception:
    pass
  try:
    deferred_line.plan()
  except Exception:
    pass
  return deferred_line


def endRunAfterDefer():
  """End the run when every tool call of the answer was deferred.

  No new request line exists. No answer arrives. The Artificial Task must not
  wait. The Artificial Task goes to the state `responded`.

  WARNING: this function must never raise.
  """
  removeProviderFile()
  if artificial_task is None:
    return
  try:
    if artificial_task.getSimulationState() == 'processing':
      artificial_task.respond()
  except Exception:
    pass


def newRequestLine(request_payload, causality_document):
  """Create one request line in the state `draft` and start the line.

  A request line reads no provider. The line holds the quantity 0.

  The new line holds the send parameters of the line that runs now. The
  send path of the new line therefore reads the new line only.
  """
  request_line = report.newContent(
    portal_type=LINE_PORTAL_TYPE,
    int_index=getNextIntIndex(),
    text_content=json.dumps(request_payload, indent=1),
  )
  request_line.ArtificialTaskReportLine_writeRequestParameterList(
    source_line=line)
  if causality_document is not None:
    request_line.setCausalityValue(causality_document)
  request_line.start()
  return request_line


def normaliseText(value):
  """Return one text for one result of one tool."""
  if isinstance(value, dict) or isinstance(value, list) or \
     isinstance(value, tuple):
    try:
      return json.dumps(value, default=str)
    except Exception:
      return safeText(value)
  return safeText(value)


def resolveTool(tool_name):
  """Return one tuple of the tool and the refusal text.

  The first item is the callable object, or None. The second item is the
  text that says why the tool is not allowed, or an empty text.

  WARNING: this function is the only allow list of this script. The name of
  the tool comes from the model. The function applies five checks.
  1. The Artificial Task must exist.
  2. The name must hold only letters, digits and the low line.
  3. The name must be in the property `tool_list` of the Artificial Task.
  4. The name must be one own identifier of `portal_callables`. This check
     stops acquisition. `getattr` on `portal_callables` acquires.
  5. The object must be one Python Script whose callable type is `script`.
  """
  if artificial_task is None:
    return None, (u'This Artificial Task Report has no Artificial Task. '
                  u'No tool is allowed.')
  if not tool_name:
    return None, u'The model asked for one tool with no name.'
  for character in tool_name:
    if character not in TOOL_NAME_CHARACTER_SET:
      return None, (u'The tool name "%s" holds one character that is not '
                    u'allowed.' % (safeText(tool_name), ))
  if tool_name not in (artificial_task.getToolList() or []):
    return None, (u'The tool "%s" is not in the tool list of this Artificial '
                  u'Task.' % (safeText(tool_name), ))
  callable_tool = portal.portal_callables
  if tool_name not in list(callable_tool.objectIds()):
    return None, (u'The tool "%s" is not one own object of portal_callables.'
                  % (safeText(tool_name), ))
  tool_document = None
  for candidate in callable_tool.objectValues():
    if candidate.getId() == tool_name:
      tool_document = candidate
      break
  if tool_document is None:
    return None, (u'The tool "%s" is not one own object of portal_callables.'
                  % (safeText(tool_name), ))
  get_callable_type = getattr(tool_document, 'getCallableType', None)
  if get_callable_type is None or get_callable_type() != 'script':
    return None, (u'The tool "%s" is not one script.'
                  % (safeText(tool_name), ))
  if tool_document.getPortalType() != 'Python Script':
    return None, (u'The tool "%s" is not one Python Script.'
                  % (safeText(tool_name), ))
  return tool_document, u''


def runRequest(response):
  """Run the request of this line. Return one text that says what happened.

  `response` is the answer of the connector, or None. This function assigns
  the name `response`, so the name must be one parameter of this function.
  A nested function that assigns one name of the script makes that name
  local, and a read before the assignment then raises.
  """
  # WARNING: keep this guard before the read of `text_content`. A line with
  # an answer and no payload must also stop.
  for sibling in report.objectValues(portal_type=LINE_PORTAL_TYPE):
    if sibling.getCausality() == line_relative_url:
      # A `started` line with an answer waits for ever. Stop the line.
      stopRequestLine()
      return 'answer already exists'

  text_content = line.getTextContent()
  if not text_content:
    stopRequestLine()
    return 'no payload'
  payload = json.loads(text_content)
  role = payload.get('role')

  if role == 'llm_request':

    # WARNING: the send path reads this line only, never the Artificial Task.
    # BBB: a line with no connector gives one error line.
    connector = line.getConnectorValue()

    response_id = line.getDestinationReference()

    # A stale answer or a foreign answer must change nothing.
    if response is not None:
      if not response_id or response.get('id') != response_id:
        return 'refused: the response does not name this line'

    # WARNING: a paid answer from the Alarm must reach the report, also when
    # the line holds no connector.
    if response is None and connector is None:
      failRun(u'This line holds no connector. The send path reads the line '
              u'only, and reads no connector of the Artificial Task.')
      return 'error'

    if response is None and response_id:
      # Never create a second response. A second response pays a second time.
      try:
        response = connector.retrieveResponse(response_id)
      except Exception as retrieve_error:
        # A transport error is not an answer. The Alarm reads again later.
        return 'the response is not known yet: %s' % (
          safeText(retrieve_error), )

    if response is None:
      model = line.getModel()
      if not model:
        # The reference of the `resource` Service is the name of the model.
        try:
          resource_value = line.getResourceValue()
          if resource_value is not None:
            model = resource_value.getReference()
        except Exception:
          model = None
      if not model:
        failRun(u'This line holds no model. The send path reads the line '
                u'only, and reads no model of the Artificial Task.')
        return 'error'
      request_parameter = line.getRequestParameter()

      keyword_dict = {}
      if request_parameter:
        try:
          for key, value in json.loads(request_parameter).items():
            keyword_dict[str(key)] = value
        except Exception as parameter_error:
          failRun(u'The property request_parameter is not one JSON object: %s'
                  % (safeText(parameter_error), ))
          return 'error'

      # The line holds the tool definitions: a later change of a tool
      # description does not change this request.
      tool_definition_list = payload.get('tools') or []

      message_list = report.ArtificialTaskReport_getMessageList()

      # WARNING: the private key `_llm_file` breaks the request. Remove it.
      # One file per request: the last file wins.
      attachment_dict = {}
      clean_message_list = []
      for message in message_list:
        if not isinstance(message, dict) or '_llm_file' not in message:
          clean_message_list.append(message)
          continue
        file_dict = message['_llm_file']
        clean_message = {}
        for message_key, message_value in message.items():
          if message_key != '_llm_file':
            clean_message[message_key] = message_value
        clean_message_list.append(clean_message)
        if isinstance(file_dict, dict) and file_dict.get('data'):
          attachment_dict = file_dict
      message_list = clean_message_list

      for attachment_key, attachment_value in (
          ('attachment_data', attachment_dict.get('data')),
          ('attachment_filename', attachment_dict.get('name')),
          ('attachment_media_type', attachment_dict.get('media_type'))):
        if attachment_value is not None and attachment_key not in keyword_dict:
          keyword_dict[attachment_key] = attachment_value

      # XXX: a stop of the node before the commit loses the identifier, and
      # a new run pays a second time.
      try:
        response = connector.createResponse(
          messages=message_list,
          model=model,
          tools=tool_definition_list,
          background=line.getIsBackgroundEnabled(),
          **keyword_dict)
      except Exception as llm_error:
        # A model that fails calls no tool, so a rule must escalate.
        if tryRuleDrivenEscalation(
            u'The call to the Large Language Model failed: %s'
            % (safeText(llm_error), )):
          return 'escalated after one provider error'
        failRun(u'The call to the Large Language Model failed: %s'
                % (safeText(llm_error), ))
        return 'error'

      # The next round reuses `file_id`. Write it before the next activity.
      # WARNING: the binary must never enter `request_parameter`.
      new_file_id = None
      try:
        new_file_id = response.get('file_id')
      except Exception:
        new_file_id = None
      if new_file_id and not keyword_dict.get('file_id'):
        keyword_dict['file_id'] = new_file_id
        try:
          stored_parameter_dict = {}
          for parameter_key, parameter_value in keyword_dict.items():
            if parameter_key in ('attachment_data', 'attachment_filename',
                                 'attachment_media_type'):
              continue
            stored_parameter_dict[parameter_key] = parameter_value
          line.setRequestParameter(
            json.dumps(stored_parameter_dict, sort_keys=True))
        except Exception:
          pass

      if response.get('id'):
        line.setDestinationReference(response['id'])

      if not response.get('is_done') and not response.get('id'):
        # The Alarm reads no line without an identifier. End the line now.
        failRun(u'The provider answered no identifier.')
        return 'error'

    try:
      total_token_count_list[0] = int(
        (response.get('usage') or {}).get('total_tokens', 0) or 0)
    except Exception:
      total_token_count_list[0] = 0

    if not response.get('is_done'):
      # The line stays `started`. The Alarm reads the provider later.
      return 'response queued'

    response_status = response.get('status') or 'completed'
    if response_status != 'completed':
      error_dict = response.get('error') or {}
      status_error_text = u'The request ended with the status %s. %s %s' % (
        safeText(response_status),
        safeText(error_dict.get('code') or u''),
        safeText(error_dict.get('message') or u''))
      if tryRuleDrivenEscalation(status_error_text):
        return 'escalated after one failed request'
      failRun(status_error_text)
      return 'error'

    tool_call_list = response.get('tool_calls') or []
    # `ArtificialTaskReport_getMessageList` sends no `model` and no `usage`.
    answer_payload = {
      'role': 'assistant',
      'content': response.get('content') or '',
      'model': response.get('model') or line.getModel(),
      'usage': response.get('usage') or {},
    }

    # Read the bound first. `tool_calls` with no answer make the next round
    # fail with the HTTP status 400.
    is_over_tool_bound = False
    if tool_call_list:
      if countTurnRole('tool_request') + len(tool_call_list) > \
         MAXIMUM_TOOL_REQUEST_COUNT:
        is_over_tool_bound = True

    if tool_call_list and not is_over_tool_bound:
      answer_payload['tool_calls'] = tool_call_list

    answer_line = newAnswerLine(answer_payload)
    writeAnswerModel(answer_line, answer_payload['model'])
    stopRequestLine()

    if not tool_call_list:
      # WARNING: an answer with a clear text and no tool call must never
      # escalate. Only an empty answer escalates.
      if not answer_payload['content']:
        if tryRuleDrivenEscalation(
            u'The model answered no tool call and no text.'):
          return 'escalated after one empty answer'
      finishRun(answer_payload['content'], answer_line)
      return 'run finished'

    if is_over_tool_bound:
      finishRun(
        'This run reached the limit of %s tool requests. The run stops here.'
        % (MAXIMUM_TOOL_REQUEST_COUNT, ),
        answer_line)
      return 'tool bound reached'

    # Fail closed: the harness must know the tools that need a validation.
    deferrable_tool_id_tuple = getDeferrableToolIdTuple()
    if deferrable_tool_id_tuple is None:
      failRun(
        u'The script %s is absent, or the script raised. The run stops.'
        % (safeText(DEFERRABLE_TOOL_SCRIPT_ID), ))
      return 'error'

    # An answer that defers a tool call must not escalate. An escalation
    # could write a second deferred line for the same document.
    has_deferred_call = False
    for tool_call in tool_call_list:
      if isDeferredToolCall(tool_call, deferrable_tool_id_tuple):
        has_deferred_call = True
        break

    started_request_count = 0
    deferred_line_count = 0
    for tool_call in tool_call_list:
      if isDeferredToolCall(tool_call, deferrable_tool_id_tuple):
        newDeferredLine(tool_call, answer_line)
        deferred_line_count = deferred_line_count + 1
      elif has_deferred_call and \
           getToolCallName(tool_call) == ESCALATION_TOOL_ID:
        # The run ends after this answer. The text is the record only.
        newAnswerLine({
          'role': 'tool',
          'tool_call_id': tool_call.get('id'),
          'name': ESCALATION_TOOL_ID,
          'content': ESCALATION_AFTER_DEFER_TEXT,
        })
      else:
        newRequestLine({'role': 'tool_request', 'tool_call': tool_call},
                       answer_line)
        started_request_count = started_request_count + 1
    if not started_request_count:
      # Every tool call was deferred. No answer arrives. End the run.
      endRunAfterDefer()
      return 'tool requests deferred'
    if deferred_line_count:
      return 'tool requests started and deferred'
    return 'tool requests started'

  elif role == 'tool_request':

    tool_call = payload.get('tool_call') or {}
    function_dict = tool_call.get('function') or {}
    tool_name = safeText(function_dict.get('name') or '')
    raw_argument_text = function_dict.get('arguments') or '{}'
    argument_dict = {}
    try:
      for key, value in (json.loads(raw_argument_text) or {}).items():
        argument_dict[str(key)] = value
    except Exception:
      argument_dict = {}

    tool_document, refusal_text = resolveTool(tool_name)
    if tool_document is None:
      # A refusal is an answer. A raise would end the run with an error.
      answer_text = refusal_text
    else:
      if tool_name == ESCALATION_TOOL_ID:
        # Write these keys after the arguments: the model must not choose them.
        task_relative_url = u''
        if artificial_task is not None:
          task_relative_url = artificial_task.getRelativeUrl()
        argument_dict['artificial_task_relative_url'] = task_relative_url
        argument_dict['report_line_relative_url'] = line_relative_url
      try:
        answer_text = normaliseText(tool_document(**argument_dict))
      except Exception as tool_error:
        answer_text = u'The tool "%s" failed: %s' % (
          tool_name, safeText(tool_error))

    tool_answer_line = newAnswerLine({
      'role': 'tool',
      'tool_call_id': tool_call.get('id'),
      'name': tool_name,
      'content': answer_text,
    })
    stopRequestLine()

    # The accepted escalation already started the next round.
    if tool_name == ESCALATION_TOOL_ID and \
       answer_text.startswith(ESCALATION_ACCEPTED_PREFIX):
      return 'the escalation started the round of the strong model'

    round_causality = line.getCausality()
    answered_causality_list = []
    for report_line in report.objectValues(portal_type=LINE_PORTAL_TYPE):
      if getRole(report_line) == 'tool':
        answered_causality_list.append(report_line.getCausality())

    for report_line in report.objectValues(portal_type=LINE_PORTAL_TYPE):
      if getRole(report_line) != 'tool_request':
        continue
      if report_line.getCausality() != round_causality:
        continue
      if report_line.getRelativeUrl() not in answered_causality_list:
        return 'this round is not complete'

    if countTurnRole('llm_request') >= MAXIMUM_LLM_REQUEST_COUNT:
      finishRun(
        'This run reached the limit of %s requests to the Large Language '
        'Model. The run stops here.' % (MAXIMUM_LLM_REQUEST_COUNT, ),
        tool_answer_line)
      return 'llm bound reached'

    newRequestLine({'role': 'llm_request'}, None)
    return 'next round started'

  else:
    stopRequestLine()
    return 'the role %s is not a request' % (safeText(role), )


try:
  return runRequest(response)
except Exception as run_error:
  # Only an answer that does not parse escalates. A defect of the code must
  # end the run.
  failure_text = u'The request failed: %s' % (safeText(run_error), )
  is_answer_failure = 0
  try:
    if getRole(line) == 'llm_request' and line.getDestinationReference():
      is_answer_failure = 1
  except Exception:
    is_answer_failure = 0
  if is_answer_failure and tryRuleDrivenEscalation(failure_text):
    return 'escalated after one answer that does not parse'
  failRun(failure_text)
  return 'error'
