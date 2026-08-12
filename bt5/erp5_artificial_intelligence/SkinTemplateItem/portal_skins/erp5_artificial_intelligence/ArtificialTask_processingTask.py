import json
artifical_task = context
portal = artifical_task.getPortalObject()

RESPONSE = context.REQUEST.RESPONSE

if tool_call and isinstance(tool_call, str):
  tool_call = json.loads(tool_call)

if tool_definition_list and isinstance(tool_definition_list, str):
  tool_definition_list = json.loads(tool_definition_list)
tool_definition_list = tool_definition_list or []

if message_list and isinstance(message_list, str):
  message_list = json.loads(message_list)
message_list = message_list or []

if compact_message_list and isinstance(compact_message_list, str):
  compact_message_list = json.loads(compact_message_list)

if finalize_result and isinstance(finalize_result, str):
  finalize_result = json.loads(finalize_result)

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

elif compact_message_list:

  conn = artifical_task.getConnectorValue()
  model = artifical_task.getModel()

  conversation_text = "\n".join([
    "%s: %s" % (
      m.get("role"),
      m.get("content") if isinstance(m.get("content"), str) else json.dumps(m.get("content"))
    )
    for m in compact_message_list
  ])

  summary_response = conn.getResponseWithUsage(
    messages=[
      {
        "role": "system",
        "content": "Summarize the following conversation into a concise context "
                   "summary. Preserve key decisions, work already done, and open tasks.",
      },
      {"role": "user", "content": conversation_text},
    ],
    model=model,
    tools=[])

  return json.dumps({
    "content": summary_response["content"],
  })

elif finalize_result:
  response = finalize_result
  content = response["content"]
  tool_calls = response.get("tool_calls") or []

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

else:
  conn = artifical_task.getConnectorValue()
  model = artifical_task.getModel()
  RESPONSE.setHeader('Content-Type', 'text/plain; charset=utf-8')
  RESPONSE.setBody(conn.getResponseStreamIterator(
    messages=message_list, model=model, tools=tool_definition_list))
  return ''
