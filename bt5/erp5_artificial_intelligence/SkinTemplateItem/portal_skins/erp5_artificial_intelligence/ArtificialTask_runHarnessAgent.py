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

def finalize(report_line, message_list):
  content = '\n'.join([x.get("content") for x in message_list if x.get('role', '') != 'tool' and x.get("content", '')])
  line = artificial_task.newContent(
    portal_type='Artificial Task Line',
    text_content=content,
    source_value = artificial_agent,
  )
  report_line.edit(
    text_content=json.dumps(message_list, indent=2),
    follow_up_value=line
  )
  line.deliver()
  report_line.deliver()
  artificial_task.stop()
  if request_object.getPortalType() == 'Artificial Task Line':
    request_object.deliver()
    line.edit(follow_up_value = request_object)



default_message_list = artificial_task.ArtificialTask_getMessageListForArtificialAgent(artificial_agent.getRelativeUrl())

if not artificial_task_report_line_relative_url:
  artificial_task_report = artificial_task.getFollowUpRelatedValue(portal_type='Artificial Task Report')
  if not artificial_task_report:
    artificial_task_report = portal.artificial_task_report_module.newContent(portal_type='Artificial Task Report')
    artificial_task_report.edit(
      follow_up_value = artificial_task
    )
  artificial_task_report_line = artificial_task_report.newContent(
    portal_type='Artificial Task Report Line'
  )
  artificial_task_report_line_relative_url = artificial_task_report_line.getRelativeUrl()
  message_list = []
else:
  artificial_task_report_line = artificial_task.restrictedTraverse(artificial_task_report_line_relative_url)
  message_list = json.loads(artificial_task_report_line.getTextContent())


if loop_count >= MAX_LOOP_COUNT:
  message_list.append({
    "content": "Sorry, I could not finish this task within the allowed number of steps."
  })
  finalize(artificial_task_report_line, message_list)

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
  artificial_task_report_line.edit(text_content=json.dumps(message_list, indent=2))

  getattr(
    artificial_task.activate(
      activity="SQLDict", tag=processing_tag,
      after_path_and_method_id=(artificial_task_report_line.getPath(), ('immediateReindexObject',))),
    script.id
  )(
    request_object_relative_url = request_object_relative_url,
    artificial_task_report_line_relative_url=artificial_task_report_line_relative_url,
    pending_tool_call_list=None,
    loop_count=loop_count + 1,
  )

else:
  # The beginning to call llm
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
    response = connector.getResponseWithUsage(
      messages=system_level_message_list + default_message_list + message_list, model=artificial_agent.getModel(),
      tools=tool_definition_list)
  except Exception as llm_error:
    message_list.append({
      "content": "Sorry, something went wrong while processing this request: %s" % str(llm_error)
    })
    finalize(artificial_task_report_line, message_list)
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
    artificial_task_report_line.edit(text_content=json.dumps(message_list, indent=2))
    getattr(
      artificial_task.activate(
        activity="SQLDict", tag=processing_tag,
        after_path_and_method_id=(artificial_task_report_line.getPath(), ('immediateReindexObject',))),
      script.id
    )(
      request_object_relative_url = request_object_relative_url,
      artificial_task_report_line_relative_url=artificial_task_report_line_relative_url,
      pending_tool_call_list=tool_calls,
      loop_count=loop_count + 1,
    )
