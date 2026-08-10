import json
artifical_task = context
portal = artifical_task.getPortalObject()

if tool_call and isinstance(tool_call, str):
  tool_call = json.loads(tool_call)

if tool_definition_list and isinstance(tool_definition_list, str):
  tool_definition_list = json.loads(tool_definition_list)
tool_definition_list = tool_definition_list or []

if client_tool_result and isinstance(client_tool_result, str):
  client_tool_result = json.loads(client_tool_result)

if not report_path:
  artifical_task.start()
  message_list = []
  for line in artifical_task.objectValues(
    portal_type='Artificial Task Line',
    sort_on=[('creation_date', 'ascending')],
    simulation_state = ('stopped', 'delivered')
  ):
    if line.getSimulationState() == 'stopped':
      role = 'user'
    else:
      role = 'assistant'
    message_list.append({
      "role": role,
      "content": line.getTextContent()
    })
  artificial_task_report = artifical_task.getFollowUpRelatedValue(portal_type='Artificial Task Report')
  artificial_task_report_line = artificial_task_report.newContent(
    portal_type='Artificial Task Report Line',
    text_content = json.dumps(message_list, indent=2)
  )
  report_path = artificial_task_report_line.getRelativeUrl()
else:
  artificial_task_report_line = artifical_task.restrictedTraverse(report_path)
  message_list = json.loads(artificial_task_report_line.getTextContent())

if tool_call:
  function = tool_call["function"]["name"]

  if client_tool_result:
    result = client_tool_result.get("content")
    tool_call_id = client_tool_result.get("tool_call_id") or tool_call.get("id")
  else:
    raw_arguments = tool_call["function"].get("arguments") or "{}"
    try:
      arguments = json.loads(raw_arguments) or {}
    except ValueError:
      arguments = {}
    result = getattr(portal.portal_callables, function)(**arguments)
    tool_call_id = tool_call.get("id")

  message_list.append({
    "role": "tool",
    "tool_call_id": tool_call_id,
    "name": function,
    "content": result if isinstance(result, str) else json.dumps(result),
  })
  artificial_task_report_line.edit(text_content = json.dumps(message_list, indent=2))

  return json.dumps({
    "report_path": report_path,
  })

else:
  conn = artifical_task.getConnectorValue()
  model = artifical_task.getModel()

  response = conn.getResponseWithUsage(
    messages= message_list, model=model,
    tools=tool_definition_list)

  content = response["content"]
  tool_calls = response["tool_calls"]

  if not tool_calls:
    line = artifical_task.newContent(
      portal_type='Artificial Task Line',
      text_content = content
    )
    message_list = json.loads(artificial_task_report_line.getTextContent())
    message_list.append(response)
    artificial_task_report_line.edit(
      text_content = json.dumps(message_list, indent=2),
      follow_up_value = line
    )
    line.deliver()
    artifical_task.respond()

    return json.dumps({})

  else:
    message_list.append({
      "role": "assistant",
      "content": response["content"],
      "tool_calls": response["tool_calls"],
    })
    artificial_task_report_line.edit(text_content = json.dumps(message_list, indent = 2))

    return json.dumps({
      "report_path": report_path,
      "pending_tool_call_list": tool_calls,
    })
