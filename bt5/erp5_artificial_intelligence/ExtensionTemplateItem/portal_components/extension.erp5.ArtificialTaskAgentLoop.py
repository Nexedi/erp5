import transaction

# Commit roughly every N streamed delta chunks, so the accumulating partial
# answer becomes visible to a separate request (the browser's status poll)
# while the LLM is still generating it - a plain RestrictedPython Skin
# script can't do this at all (no `import transaction`), its writes only
# become visible once its whole activity step finishes.
STREAM_COMMIT_INTERVAL = 20


def runStreamingLLMStep(self, report_line_relative_url, message_list, tool_definition_list):
  # self: the Artificial Task this turn belongs to.
  portal = self.getPortalObject()
  report_line = portal.restrictedTraverse(report_line_relative_url)
  conn = self.getConnectorValue()
  model = self.getModel()

  accumulated_list = []
  chunk_count = 0
  final_chunk = None

  for chunk in conn.getResponseWithUsageStream(
      messages=message_list, model=model, tools=tool_definition_list):
    if chunk.get("type") == "delta":
      accumulated_list.append(chunk.get("content") or "")
      chunk_count += 1
      if chunk_count % STREAM_COMMIT_INTERVAL == 0:
        report_line.streaming_content = "".join(accumulated_list)
        try:
          transaction.commit()
        except transaction.interfaces.TransactionError:
          transaction.abort()
    else:
      final_chunk = chunk

  report_line.streaming_content = ""
  return final_chunk
