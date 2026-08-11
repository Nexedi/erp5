import json
artifical_task = context
portal = artifical_task.getPortalObject()

if tool_call and isinstance(tool_call, str):
  tool_call = json.loads(tool_call)

if tool_definition_list and isinstance(tool_definition_list, str):
  tool_definition_list = json.loads(tool_definition_list)
tool_definition_list = tool_definition_list or []

if message_list and isinstance(message_list, str):
  message_list = json.loads(message_list)
message_list = message_list or []

if tool_call:
  function = tool_call["function"]["name"]
  raw_arguments = tool_call["function"].get("arguments") or "{}"
  try:
    arguments = json.loads(raw_arguments) or {}
  except ValueError:
    arguments = {}
  context.log('call ********* %s' % function)
  context.log('argument ******* %s' % arguments)
  result = getattr(portal.portal_callables, function)(**arguments)

  return json.dumps({
    "content": result if isinstance(result, str) else json.dumps(result),
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
    artificial_task_report = artifical_task.getFollowUpRelatedValue(portal_type='Artificial Task Report')
    artificial_task_report.newContent(
      portal_type='Artificial Task Report Line',
      text_content = json.dumps(message_list + [response], indent=2),
      follow_up_value = line
    )
    line.deliver()
    if artifical_task.getSimulationState() != 'processing':
      artifical_task.start()
    artifical_task.respond()

    return json.dumps({
      "post": {
        "date": line.getCreationDate().ISO8601(),
        "text": content,
        "response": True
      }
    })

  else:
    if artifical_task.getSimulationState() != 'processing':
      artifical_task.start()
    return json.dumps({
      "content": content,
      "tool_calls": tool_calls,
    })
