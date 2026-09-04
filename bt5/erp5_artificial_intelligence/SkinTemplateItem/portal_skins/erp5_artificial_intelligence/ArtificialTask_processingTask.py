import json
artificial_task = context
portal = artificial_task.getPortalObject()

conn = artificial_task.getConnectorValue()
model = artificial_task.getModel()

if tool_definition_list and isinstance(tool_definition_list, str):
  tool_definition_list = json.loads(tool_definition_list)
tool_definition_list = tool_definition_list or []

if message_list and isinstance(message_list, str):
  message_list = json.loads(message_list)
message_list = message_list or []

if compact_message_list and isinstance(compact_message_list, str):
  compact_message_list = json.loads(compact_message_list)

simulation_state = artificial_task.getSimulationState()

if simulation_state == 'draft':
  artificial_task.plan()

if compact_message_list:
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

else:
  if not artificial_task.getDescription():
    title_response = conn.getResponseWithUsage(
      messages=[
        {
          "role": "system",
          "content": "Reply with only a short chat title (3 to 6 words, no quotes, "
          "no trailing punctuation) summarizing the user's request below."
        }
      ] + message_list,
      model=model,
      tools=[])
    title = (title_response.get("content") or "").strip().strip('"').strip("'").strip()
    if title:
      artificial_task.edit(
        title = title[:80],
        description = title)

  response = conn.getResponseWithUsage(
    messages=message_list, model=model, tools=tool_definition_list)
  content = response["content"]
  tool_calls = response.get("tool_calls") or []

  if not tool_calls:
    line = artificial_task.newContent(
      portal_type='Artificial Task Line',
      text_content = content
    )
    artificial_task_report = artificial_task.getFollowUpRelatedValue(portal_type='Artificial Task Report')
    if not artificial_task_report:
      artificial_task_report = portal.artificial_task_report_module.newContent(portal_type='Artificial Task Report')
      artificial_task_report.edit(
        follow_up_value = artificial_task
      )

    artificial_task_report.newContent(
      portal_type='Artificial Task Report Line',
      text_content = json.dumps(message_list[int(initial_message_length):] + [response], indent=2),
      follow_up_value = line
    )
    line.deliver()
    if simulation_state != 'processing':
      artificial_task.start()
    artificial_task.respond()

    return json.dumps({
      "content": content
    })

  else:
    if simulation_state != 'processing':
      artificial_task.start()
    return json.dumps({
      "content": content,
      "tool_calls": tool_calls,
    })
