import json

MAX_LOOP_COUNT = 50

artificial_task = context
portal = artificial_task.getPortalObject()
processing_tag = 'process_%s' % artificial_task.getRelativeUrl()


def finalize(report_line, message_list, response):
  content = response.get("content") or ""
  line = artificial_task.newContent(
    portal_type='Artificial Task Line',
    text_content=content
  )
  report_line.edit(
    text_content=json.dumps(message_list + [response], indent=2),
    follow_up_value=line
  )
  line.deliver()
  report_line.deliver()
  artificial_task.respond()


if not artificial_task_report_line_relative_url:
  simulation_state = artificial_task.getSimulationState()
  if simulation_state == 'draft':
    artificial_task.plan()
  if simulation_state != 'processing':
    artificial_task.start()

  message_list = artificial_task.ArtificialTask_getMessageList()

  if not artificial_task.getDescription():
    try:
      title_response = artificial_task.getConnectorValue().getResponseWithUsage(
        messages=[{
          "role": "system",
          "content": "Reply with only a short chat title (3 to 6 words, no quotes, "
                     "no trailing punctuation) summarizing the user's request below."
        }] + message_list,
        model=artificial_task.getModel(),
        tools=[])
      title = (title_response.get("content") or "").strip().strip('"').strip("'").strip()
      if title:
        artificial_task.edit(title=title[:80], description=title)
    except Exception:
      pass

  artificial_task_report = artificial_task.getFollowUpRelatedValue(portal_type='Artificial Task Report')
  if not artificial_task_report:
    artificial_task_report = portal.artificial_task_report_module.newContent(portal_type='Artificial Task Report')
    artificial_task_report.edit(
      follow_up_value = artificial_task
    )
  artificial_task_report_line = artificial_task_report.newContent(
    portal_type='Artificial Task Report Line',
    text_content=json.dumps(message_list, indent=2)
  )
  artificial_task_report_line_relative_url = artificial_task_report_line.getRelativeUrl()
else:
  artificial_task_report_line = artificial_task.restrictedTraverse(artificial_task_report_line_relative_url)
  message_list = json.loads(artificial_task_report_line.getTextContent())


if loop_count >= MAX_LOOP_COUNT:
  finalize(artificial_task_report_line, message_list, {
    "content": "Sorry, I could not finish this task within the allowed number of steps."
  })

elif pending_tool_call_list:
  tool_call = pending_tool_call_list[0]
  remaining_tool_call_list = pending_tool_call_list[1:]
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
    artificial_task.activate(activity="SQLDict", tag=processing_tag),
    script.id
  )(
    artificial_task_report_line_relative_url=artificial_task_report_line_relative_url,
    pending_tool_call_list=remaining_tool_call_list,
    loop_count=loop_count + 1,
  )

else:
  # The beginning to call llm
  tool_list = artificial_task.getToolList()
  skill_list = artificial_task.getSkillList()
  tool_definition_list = [
    json.loads(getattr(portal.portal_callables, x).getDescription()) for x in tool_list
  ]
  system_level_message_list = [
    {
      'role': "system",
      'content': portal.web_page_module[skill].getTextContent()
    } for skill in skill_list]

  try:
    response = artificial_task.ArtificialTask_runStreamingLLMStep(
      artificial_task_report_line_relative_url, system_level_message_list + message_list, tool_definition_list)
  except Exception as llm_error:
    finalize(artificial_task_report_line, message_list, {
      "content": "Sorry, something went wrong while processing this request: %s" % str(llm_error)
    })
    return

  tool_calls = response.get("tool_calls") or []

  if not tool_calls:
    finalize(artificial_task_report_line, message_list, response)
  else:
    message_list.append({
      "role": "assistant",
      "content": response.get("content"),
      "tool_calls": tool_calls,
    })
    artificial_task_report_line.edit(text_content=json.dumps(message_list, indent=2))
    getattr(
      artificial_task.activate(activity="SQLDict", tag=processing_tag),
      script.id
    )(
      artificial_task_report_line_relative_url=artificial_task_report_line_relative_url,
      pending_tool_call_list=tool_calls,
      loop_count=loop_count + 1,
    )
