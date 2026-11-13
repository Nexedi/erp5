import json

MAX_LOOP_COUNT = 50

artificial_task = context
portal = artificial_task.getPortalObject()
processing_tag = 'process_%s' % artificial_task.getRelativeUrl()
if portal.portal_activities.countMessageWithTag(processing_tag) > 1:
  return

if not request_object_relative_url:
  request_object = artificial_task
  for x in artificial_task.objectValues(portal_type='Artificial Task Line'):
    if x.getSimulationState() == 'stopped':
      request_object = x
      break
  request_object_relative_url = request_object.getRelativeUrl()
else:
  request_object = artificial_task.restrictedTraverse(request_object_relative_url)

artificial_agent = request_object.getDestinationValue(portal_type='Artificial Agent')
connector = artificial_agent.getConnectorValue()
llm_node = portal.portal_preferences.getPreferredLlmActivityFamily()

def finalize(report_line, message_list):
  content = '\n'.join([x.get("content") for x in message_list if x.get('role', '') != 'tool' and x.get("content", '')])
  line = artificial_task.newContent(
    portal_type='Artificial Task Line',
    text_content=content,
    source_value = artificial_agent,
  )
  report_line.edit(
    text_content=json.dumps({
      "response_id": None,
      "response_id_list": response_id_list,
      "message_list": message_list,
    }, indent=2),
    follow_up_value=line
  )
  line.deliver()
  report_line.deliver()
  artificial_task.stop()
  if request_object.getPortalType() == 'Artificial Task Line':
    request_object.deliver()
    line.edit(follow_up_value = request_object)


def finalizeWithApology(error_text):
  message_list.append({
    "content": "Sorry, something went wrong while processing this request: %s" % error_text
  })
  finalize(artificial_task_report_line, message_list)


def activateNextStep(loop_count, pending_tool_call_list=None):
  getattr(
    artificial_task.activate(
      activity="SQLDict", tag=processing_tag, node=llm_node,
      after_path_and_method_id=(artificial_task_report_line.getPath(), ('immediateReindexObject',))),
    script.id
  )(
    request_object_relative_url=request_object_relative_url,
    artificial_task_report_line_relative_url=artificial_task_report_line_relative_url,
    pending_tool_call_list=pending_tool_call_list,
    loop_count=loop_count,
  )


def handleCompletedResponse(response):
  error = response.get("error")
  if error:
    finalizeWithApology(error.get("message") or error.get("code") or "unknown error")
    return

  tool_calls = response.get("tool_calls") or []
  if not tool_calls:
    message_list.append(response)
    finalize(artificial_task_report_line, message_list)
  else:
    message_list.append({
      "role": "assistant",
      "content": response.get("content"),
      "tool_calls": tool_calls,
    })
    artificial_task_report_line.edit(
      text_content=json.dumps({
        "response_id": None,
        "response_id_list": response_id_list,
        "message_list": message_list,
      }, indent=2))
    activateNextStep(pending_tool_call_list=tool_calls, loop_count=loop_count + 1)


default_message_list = artificial_task.ArtificialTask_getMessageListForArtificialAgent(artificial_agent.getRelativeUrl())

is_new_report_line = False

if artificial_task_report_line_relative_url:
  artificial_task_report_line = artificial_task.restrictedTraverse(artificial_task_report_line_relative_url)
else:
  artificial_task_report = artificial_task.getFollowUpRelatedValue(portal_type='Artificial Task Report')
  artificial_task_report_line = None
  if artificial_task_report is not None:
    for line in artificial_task_report.objectValues(portal_type='Artificial Task Report Line'):
      if line.getSimulationState() != 'delivered':
        artificial_task_report_line = line
        break
  if artificial_task_report_line is None:
    if artificial_task_report is None:
      artificial_task_report = portal.artificial_task_report_module.newContent(portal_type='Artificial Task Report')
      artificial_task_report.edit(
        follow_up_value = artificial_task
      )
    artificial_task_report_line = artificial_task_report.newContent(
      portal_type='Artificial Task Report Line'
    )
    is_new_report_line = True
  artificial_task_report_line_relative_url = artificial_task_report_line.getRelativeUrl()

if is_new_report_line:
  message_list = []
  response_id_list = []
  pending_response_id = None
else:
  state = json.loads(artificial_task_report_line.getTextContent())
  message_list = state.get("message_list", [])
  response_id_list = state.get("response_id_list", [])
  pending_response_id = state.get("response_id")


if loop_count >= MAX_LOOP_COUNT:
  message_list.append({
    "content": "Sorry, I could not finish this task within the allowed number of steps."
  })
  finalize(artificial_task_report_line, message_list)

elif pending_response_id:
  # A background LLM call is in progress: ask the provider for its current
  # state instead of starting a new one.
  try:
    response = connector.retrieveResponse(pending_response_id)
  except Exception as llm_error:
    finalizeWithApology(str(llm_error))
  else:
    if response["is_done"]:
      handleCompletedResponse(response)
    else:
      artificial_task.Base_reindexAndSenseAlarm(['run_artificial_task_alarm'])

elif pending_tool_call_list:
  for tool_call in pending_tool_call_list:
    function = tool_call["function"]["name"]
    raw_arguments = tool_call["function"].get("arguments") or "{}"
    try:
      arguments = json.loads(raw_arguments) or {}
    except ValueError:
      arguments = {}

    try:
      result = getattr(portal.portal_callables, function)(**arguments)
      result_content = result if isinstance(result, str) else json.dumps(result)
    except Exception as tool_error:
      result_content = "Error running tool \"%s\": %s" % (function, str(tool_error))

    message_list.append({
      "role": "tool",
      "tool_call_id": tool_call.get("id"),
      "name": function,
      "content": result_content,
    })
  artificial_task_report_line.edit(
    text_content=json.dumps({
      "response_id": None,
      "response_id_list": response_id_list,
      "message_list": message_list,
    }, indent=2))
  activateNextStep(loop_count=loop_count + 1)

else:
  tool_list = artificial_agent.getToolList()
  skill_list = artificial_agent.getSkillList()
  tool_definition_list = [
    json.loads(getattr(portal.portal_callables, x).getDescription()) for x in tool_list
  ]
  system_level_message_list = [
    {
      'role': "system",
      'content': portal.web_page_module[skill].getTextContent()
    } for skill in skill_list]

  try:
    response = connector.createResponse(
      messages=system_level_message_list + default_message_list + message_list,
      model=artificial_agent.getModel(),
      tools=tool_definition_list,
      background=True)
  except Exception as llm_error:
    finalizeWithApology(str(llm_error))
  else:
    if response.get("id"):
      response_id_list.append(response["id"])
    if response["is_done"]:
      handleCompletedResponse(response)
    else:
      artificial_task_report_line.edit(
        text_content=json.dumps({
          "response_id": response["id"],
          "response_id_list": response_id_list,
          "message_list": message_list,
        }, indent=2))
      artificial_task.Base_reindexAndSenseAlarm(['run_artificial_task_alarm'])
