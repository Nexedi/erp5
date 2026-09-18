import json
artificial_task = context
conn = artificial_task.getConnectorValue()
model = artificial_task.getModel()

dummy_response = artificial_task.restrictedTraverse(dummy_response_relative_url)

if tool_definition_list and isinstance(tool_definition_list, str):
  tool_definition_list = json.loads(tool_definition_list)
tool_definition_list = tool_definition_list or []

if message_list and isinstance(message_list, str):
  message_list = json.loads(message_list)
message_list = message_list or []

if compact_message_list and isinstance(compact_message_list, str):
  compact_message_list = json.loads(compact_message_list)

if is_subagent:
  response = conn.getResponseWithUsage(
    messages=message_list, model=model, tools=tool_definition_list)
  dummy_response.edit(
    description = json.dumps(response)
  )

elif compact_message_list:
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

  dummy_response.edit(
    description = json.dumps(summary_response)
  )

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
  dummy_response.edit(
    description = json.dumps(response)
  )
