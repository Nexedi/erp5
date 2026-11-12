"""
Fake OpenAI-compatible chat/completions endpoint, used only by the Zelenium
tests of officejs_harness_ai (portal_tests/officejs_harness_ai_ui_zuite).
Point the harness's Setting "Base URL" at this script to drive the browser
agent loop deterministically, without any real LLM provider.

Request:  {model, stream: true, messages, tools, ...} (requestProcessTask in
          gadget_officejs_harness_ai_artificial_task_view_js.js).
Response: an OpenAI-style SSE stream - one "data: {...}\\n\\n" frame per chunk,
          a last frame carrying only "usage" (like stream_options.include_usage),
          then "data: [DONE]\\n\\n".

The reply is chosen statelessly, from the conversation in the request:
1. some phrases make the request itself fail (HTTP 500 / 400);
2. a compaction summary request (recognized by its first system message)
   gets a canned summary;
3. a tool result (last message has role "tool") gets a follow-up, chosen
   from the tool call that produced it (the previous assistant message);
4. otherwise the last user message is matched against test phrases, first
   match wins (so the order of reply_to_user_message matters).
Each branch has a comment naming the test that uses it.

"<base_url>/models" (a GET from the Setting's Model field) lands here as
traverse_subpath and returns two models: "test-model", selected by every test,
and SMALL_CONTEXT_MODEL, whose tiny max_model_len makes the client compact
history after a few tool calls. For that model only, usage.prompt_tokens
follows the request size; other models report fixed numbers, which
testOfficeJSHarnessAIChat.zpt checks.
"""
import json
import re
import time

request = context.REQUEST
response = request.RESPONSE

SMALL_CONTEXT_MODEL = 'test-model-small-context'

if traverse_subpath and traverse_subpath[0] == 'models':
  response.setHeader('Content-Type', 'application/json')
  return json.dumps({'data': [
      {'id': 'test-model'},
      {'id': SMALL_CONTEXT_MODEL, 'max_model_len': 4000},
  ]})

body = json.loads(request.get('BODY', '') or '{}')
tool_list = body.get('tools') or []
message_list = body.get('messages') or []
last_message = message_list[-1] if message_list else {}
previous_message = message_list[-2] if len(message_list) >= 2 else {}
whole_request_text = json.dumps(message_list)
portal_url = context.getPortalObject().absolute_url()
ENDPOINT_URL = portal_url + '/ERP5Site_fakeHttpEndpoint'


def message_text(message):
  # "content" is a string, or a list of {type: "text" | "image_url"} parts
  # when the message carries an image attachment: keep only the text.
  content = message.get('content')
  if isinstance(content, list):
    return ' '.join(part.get('text', '') for part in content if part.get('type') == 'text')
  return content or ''


def message_has_image(message):
  content = message.get('content')
  return isinstance(content, list) and any(
      part.get('type') == 'image_url' for part in content)


last_content = message_text(last_message)
last_content_lower = last_content.lower()


# --- 1. Requests that fail -------------------------------------------------

# testOfficeJSHarnessAIErrorHandling.zpt: the client retries, then shows the error.
if 'please return an llm error' in last_content_lower:
  response.setStatus(500)
  response.setHeader('Content-Type', 'text/plain')
  return 'Simulated LLM failure'

# testOfficeJSHarnessAIContextOverflow.zpt: fails until the client compacted
# the history, then "context overflow test" below answers.
if ('context overflow test' in last_content_lower
    and '[context summary]' not in whole_request_text):
  response.setStatus(400)
  response.setHeader('Content-Type', 'application/json')
  return json.dumps({'error': {
      'message': "This model's maximum context length is 4096 tokens. However, your "
                 "messages resulted in 9000 tokens. Please reduce the length of the messages.",
      'type': 'invalid_request_error',
      'code': 'context_length_exceeded',
  }})


# --- Chunk builders and tool call helpers ----------------------------------

def text_chunk(text):
  return {'choices': [{'delta': {'content': text}}]}


def reasoning_chunk(text):
  return {'choices': [{'delta': {'reasoning_content': text}}]}


def raw_tool_call_chunk(name, arguments_text, finish_reason=None):
  # The arguments text is sent as is, so it can be invalid JSON.
  choice = {'delta': {'tool_calls': [{
      'index': 0,
      'id': 'call_1',
      'type': 'function',
      'function': {'name': name, 'arguments': arguments_text},
  }]}}
  if finish_reason:
    choice['finish_reason'] = finish_reason
  return {'choices': [choice]}


def tool_call_chunk(name, arguments, finish_reason=None):
  return raw_tool_call_chunk(name, json.dumps(arguments), finish_reason)


def first_tool_call(message):
  # (name, arguments text) of the first tool call of an assistant message.
  tool_call_list = message.get('tool_calls') or []
  if not tool_call_list:
    return None, ''
  function = tool_call_list[0].get('function') or {}
  return function.get('name'), function.get('arguments') or ''


def is_call(message, name=None, marker=''):
  # Whether the message's first tool call is to `name` (any tool if None)
  # with `marker` in its arguments text. Test calls carry a marker argument
  # (e.g. "repeat_test": true) so that their result can be recognized here.
  call_name, arguments_text = first_tool_call(message)
  return (call_name is not None
          and (name is None or call_name == name)
          and marker in arguments_text)


def count_calls(name, arguments):
  # How many times an assistant message called `name` with exactly `arguments`.
  arguments_text = json.dumps(arguments)
  count = 0
  for message in message_list:
    if message.get('role') != 'assistant':
      continue
    for tool_call in message.get('tool_calls') or []:
      function = tool_call.get('function') or {}
      if function.get('name') == name and function.get('arguments') == arguments_text:
        count += 1
  return count


def find_tool_name(description_marker):
  # The public name of an MCP tool is built from the server URL
  # (uniqueNamespacedName in gadget_officejs_harness_ai_mcp_client_js.js):
  # find it by the description from ERP5Site_fakeMcpServer instead.
  for tool in tool_list:
    function = tool.get('function') or {}
    if description_marker in (function.get('description') or ''):
      return function.get('name')
  return None


REPEAT_TEST_ARGUMENTS = {'url': ENDPOINT_URL, 'repeat_test': True}
STUCK_TEST_ARGUMENTS = {'url': ENDPOINT_URL, 'stuck_test': True}
DEFINE_TOOL_LIST_REPEAT_ARGUMENTS = {'command': 'list', 'repeat_test': True}
REASONING_TEST_TEXT = 'REASONING-MARKER: fetch the fake endpoint first.'
READ_OUTPUT_NEEDLE = 'READ-OUTPUT-NEEDLE'
# Runs about 8 seconds, so the test can cancel the task while it runs.
TOOL_HISTORY_SLOW_CODE = ('/* tool-history-slow */ var start = Date.now(); '
                          'while (Date.now() - start < 8000) {} return "slow done";')


def tool_result_of(name, marker):
  # The content of the tool message answering the first call to `name` with
  # `marker` in its arguments, or '' (the history replays the tool calls of
  # the earlier answers with their results).
  for index, message in enumerate(message_list):
    for tool_call in message.get('tool_calls') or []:
      function = tool_call.get('function') or {}
      if function.get('name') == name and marker in (function.get('arguments') or ''):
        for result in message_list[index + 1:]:
          if result.get('role') == 'tool' and result.get('tool_call_id') == tool_call.get('id'):
            return message_text(result)
        return ''
  return ''


def endless_test_arguments(step):
  return {'wat': '(module (func (export "endless_test") (result i32) (i32.const %d)))' % step,
          'calls': [{'name': 'endless_test'}]}


def compaction_test_arguments(step):
  return {'code': 'return "compaction-step-%d " + "x".repeat(5000);' % step}


# --- 3. Follow-ups to a tool result -----------------------------------------

def reply_to_tool_result():
  previous = previous_message

  # testOfficeJSHarnessAICompaction.zpt: keep calling run_javascript with big
  # results until the history carries SUMMARY-TWO. Summarized steps leave the
  # history, so the next step number also counts the summary received.
  if is_call(previous, 'run_javascript', 'compaction-step-'):
    if 'SUMMARY-TWO' in whole_request_text:
      return [text_chunk('Compaction test finished with a merged summary.')]
    next_step = (len([m for m in message_list if is_call(m, 'run_javascript', 'compaction-step-')])
                 + 1 + (1 if 'SUMMARY-ONE' in whole_request_text else 0))
    if next_step > 6:
      # Never loop forever if the client stopped compacting.
      return [text_chunk('Compaction test failed: history was not compacted.')]
    return [tool_call_chunk('run_javascript', compaction_test_arguments(next_step))]

  # testOfficeJSHarnessAIExecutionPlanTool.zpt: follow a "set" with one
  # "update_step" (step 0 done); after that, a final answer ends the chain.
  if last_message.get('name') == 'execution_plan':
    if json.loads(first_tool_call(previous)[1] or '{}').get('command') == 'set':
      return [tool_call_chunk('execution_plan', {
          'command': 'update_step',
          'index': 0,
          'status': 'done',
          'note': 'Dry run: step looks safe, marking done.',
      })]
    return [text_chunk('Tool result: %s' % last_content)]

  # testOfficeJSHarnessAIRepeatedToolCall.zpt: re-issue the same call until it
  # was made 3 times; the client's guard answers the 3rd itself, and that
  # notice is echoed by the generic answer at the end.
  if (is_call(previous, 'http_request', '"repeat_test"')
      and count_calls('http_request', REPEAT_TEST_ARGUMENTS) < 3):
    return [tool_call_chunk('http_request', REPEAT_TEST_ARGUMENTS)]

  # testOfficeJSHarnessAIChat.zpt: the report was written with the tool call.
  if is_call(previous, marker='"report_test"'):
    return [text_chunk('The full report is above.')]

  # testOfficeJSHarnessAIThinking.zpt: the client must send the reasoning back.
  if is_call(previous, marker='"reasoning_test"'):
    if previous.get('reasoning_content') == REASONING_TEST_TEXT:
      return [text_chunk('The reasoning was sent back.')]
    return [text_chunk('The reasoning was lost.')]

  # "endless run_wasm loop": never gives a final answer.
  if is_call(previous, 'run_wasm', '"endless_test"'):
    return [tool_call_chunk('run_wasm', endless_test_arguments(
        len([m for m in message_list if is_call(m, 'run_wasm', '"endless_test"')]) + 1))]

  # testOfficeJSHarnessAIRepeatedToolCall.zpt: a model that ignores the guard
  # notice and never gives up - the client must stop the task itself.
  if is_call(previous, 'http_request', '"stuck_test"'):
    return [tool_call_chunk('http_request', STUCK_TEST_ARGUMENTS)]

  # testOfficeJSHarnessAIRepeatedToolCall.zpt: define_tool is allow_repeat, so
  # all 4 identical calls must reach the real tool.
  if (is_call(previous, 'define_tool', '"repeat_test"')
      and count_calls('define_tool', DEFINE_TOOL_LIST_REPEAT_ARGUMENTS) < 4):
    return [tool_call_chunk('define_tool', DEFINE_TOOL_LIST_REPEAT_ARGUMENTS)]

  # testOfficeJSHarnessAICancelRequest.zpt: stall so the user can cancel after
  # some text was already written.
  if is_call(previous, marker='"cancel_test"'):
    time.sleep(5)
    return [text_chunk('Finished stalling.')]

  # testOfficeJSHarnessAIReadToolOutputTool.zpt: the big result must come back
  # cut, without the needle, with an output_id to read the rest.
  if is_call(previous, 'run_javascript', 'READ-OUTPUT-START'):
    output_id_match = re.search(r'output_id "(output_[0-9]+)"', last_content)
    if (last_content.startswith('[Output too large') and output_id_match
        and READ_OUTPUT_NEEDLE not in last_content):
      return [tool_call_chunk('read_tool_output', {
          'output_id': output_id_match.group(1),
          'pattern': READ_OUTPUT_NEEDLE,
      })]
    return [text_chunk('read_tool_output test failed: the tool output was not cut.')]
  if last_message.get('name') == 'read_tool_output':
    return [text_chunk('read_tool_output found: %s' % last_content)]

  # Any other tool: echo its result as the final answer.
  return [text_chunk('Tool result: %s' % last_content)]


# --- 4. Replies to a user message -------------------------------------------

def reply_to_user_message():
  text = last_content_lower

  # testOfficeJSHarnessAIToolCallHistory.zpt: a tool call that returns, then
  # a slow one cancelled while it runs, then a check of the history sent.
  if 'please start the tool history test' in text:
    return [tool_call_chunk('http_request', {'url': ENDPOINT_URL, 'tool_history_test': True})]
  if 'please run the slow tool history step' in text:
    return [tool_call_chunk('run_javascript', {'code': TOOL_HISTORY_SLOW_CODE})]
  if 'please check the tool history' in text:
    return [text_chunk('Tool history: replayed=%s, missing result filled=%s.' % (
        'Hello from the fake HTTP endpoint!' in tool_result_of('http_request', '"tool_history_test"'),
        tool_result_of('run_javascript', 'tool-history-slow').startswith(
            'Not run: the task stopped')))]

  # testOfficeJSHarnessAIStoredCompaction.zpt: two long answers, then checks
  # of the history once the first one is summarized.
  if 'please write the first long answer for the stored compaction test' in text:
    return [text_chunk('STORED-COMPACTION-ONE ' + 'filler ' * 714)]
  if 'please write the second long answer for the stored compaction test' in text:
    return [text_chunk('STORED-COMPACTION-TWO ' + 'filler ' * 714)]
  if 'please check the stored compaction test' in text:
    return [text_chunk('Stored compaction: summary=%s, first answer summarized=%s, '
                       'second answer kept=%s.' % (
        any(m.get('role') == 'user' and message_text(m).startswith('[context summary]\nSTORED-SUMMARY')
            for m in message_list),
        'STORED-COMPACTION-ONE' not in whole_request_text,
        'STORED-COMPACTION-TWO' in whole_request_text))]

  # testOfficeJSHarnessAISteering.zpt: the user posts while the agent runs.
  if 'please stall then call a tool for the steering test' in text:
    time.sleep(5)
    return [tool_call_chunk('http_request', {'url': ENDPOINT_URL})]
  if text == 'steering message':
    if previous_message.get('role') == 'tool':
      return [text_chunk('STEERING-RECEIVED after tool.')]
    return [text_chunk('STEERING-RECEIVED without tool.')]
  if text == 'follow up message':
    # Answers only: the history also replays the tool calls of the answers.
    return [text_chunk('FOLLOW-UP-RECEIVED after %d answer(s).' % len(
        [m for m in message_list if m.get('role') == 'assistant' and not m.get('tool_calls')]))]

  # testOfficeJSHarnessAICancelRequest.zpt: write some text, then stall on
  # the next request (see "cancel_test" above).
  if 'please work then stall for the cancel test' in text:
    return [
        text_chunk('WORK-DONE-BEFORE-CANCEL.'),
        tool_call_chunk('http_request', {'url': ENDPOINT_URL, 'cancel_test': True}),
    ]
  # Real providers are never instant: give the test time to click Cancel.
  if 'please stall for the cancel test' in text:
    time.sleep(5)
    return [text_chunk('Finished stalling.')]

  # Several incremental delta.content frames, to exercise streaming display.
  if 'please stream a reply in parts' in text:
    return [text_chunk('Hello'), text_chunk(' from'), text_chunk(' streaming!')]

  # testOfficeJSHarnessAIToolArguments.zpt: cut JSON (must not run), JSON with
  # a raw newline (repaired by the client), a call cut by finish_reason "length".
  if 'invalid tool arguments test' in text:
    return [raw_tool_call_chunk('http_request', '{"url": "' + portal_url)]
  if 'repairable tool arguments test' in text:
    return [raw_tool_call_chunk('run_javascript', '{"code": "return \'repaired-json-ok\';\n"}')]
  if 'truncated tool call test' in text:
    return [tool_call_chunk('http_request', {'url': ENDPOINT_URL, 'truncated_test': True},
                            finish_reason='length')]

  # testOfficeJSHarnessAIChat.zpt: frames separated by "\r\n\r\n" (see the end).
  if 'crlf stream test' in text:
    return [text_chunk('CRLF stream '), text_chunk('is ok.')]

  # testOfficeJSHarnessAIContextOverflow.zpt: reached once the history is compacted.
  if 'context overflow test' in text:
    return [text_chunk('Context overflow recovered.')]

  # testOfficeJSHarnessAIErrorHandling.zpt: the error of a failed turn must
  # never be sent back to the model.
  if 'check the history for errors' in text:
    return [text_chunk('Error in history: %s' % any(
        m.get('role') == 'assistant' and 'Simulated LLM failure' in message_text(m)
        for m in message_list))]

  # testOfficeJSHarnessAIHttpRequestTool.zpt: the request must carry no cookie.
  if 'http_request cookie test' in text:
    return [tool_call_chunk('http_request', {'url': ENDPOINT_URL + '?report_cookie=1'})]

  # testOfficeJSHarnessAIChat.zpt: only the https:// link may become a link.
  if 'unsafe link test' in text:
    return [text_chunk(
        'Links: [UNSAFE-LINK](javascript:alert(1)) and [SAFE-LINK](https://www.nexedi.com/).')]

  # testOfficeJSHarnessAIThinking.zpt: reasoning before a final answer is
  # kept in the answer's tool call trace.
  if 'final reasoning test' in text:
    return [
        reasoning_chunk('FINAL-REASONING-'),
        reasoning_chunk('MARKER: answer directly.'),
        text_chunk('Final answer after reasoning.'),
    ]

  # testOfficeJSHarnessAIPdfToTextTool.zpt (no file_name: the last PDF attached).
  if 'pdf_to_text missing file test' in text:
    return [tool_call_chunk('pdf_to_text', {'file_name': 'missing.pdf'})]
  if 'pdf_to_text tool test' in text:
    return [tool_call_chunk('pdf_to_text', {})]

  # testOfficeJSHarnessAILoadSkillTool.zpt
  if 'load_skill unknown skill test' in text:
    return [tool_call_chunk('load_skill', {'name': 'no_such_skill'})]
  if 'load_skill tool test' in text:
    return [tool_call_chunk('load_skill', {'name': 'create_html_report'})]

  # testOfficeJSHarnessAIMcpServer.zpt: list the tools of ERP5Site_fakeMcpServer
  # sent to the model, then call them (found by their description).
  if 'mcp tool list test' in text:
    mcp_description_list = [
        (tool.get('function') or {}).get('description') or '' for tool in tool_list]
    mcp_description_list = [d for d in mcp_description_list if 'FAKE-MCP-' in d]
    mcp_description_list.sort()
    return [text_chunk('MCP tools: %d. %s' % (
        len(mcp_description_list), ' | '.join(mcp_description_list)))]
  if 'mcp echo tool test' in text or 'mcp fail tool test' in text:
    is_echo = 'mcp echo tool test' in text
    mcp_tool_name = find_tool_name('FAKE-MCP-ECHO' if is_echo else 'FAKE-MCP-FAIL')
    if not mcp_tool_name:
      return [text_chunk('The MCP tool was not sent to the model.')]
    return [tool_call_chunk(mcp_tool_name, {'text': 'hello mcp'} if is_echo else {})]

  # testOfficeJSHarnessAIReadToolOutputTool.zpt: ~60000 chars, more than the
  # client's tool output limit, with the needle in the middle.
  if 'read_tool_output tool test' in text:
    return [tool_call_chunk('run_javascript', {
        'code': 'return "READ-OUTPUT-START " + "a".repeat(30000) + " %s " + '
                '"b".repeat(30000) + " READ-OUTPUT-END";' % READ_OUTPUT_NEEDLE})]
  if 'run_javascript tool test' in text:
    return [tool_call_chunk('run_javascript', {'code': 'return "javascript-tool-test-ok";'})]
  if 'run_wasm tool test' in text:
    return [tool_call_chunk('run_wasm', {
        'wat': '(module (func $add (export "add") (param i32 i32) (result i32) '
               'local.get 0 local.get 1 i32.add))',
        'calls': [{'name': 'add', 'args': [2, 3]}],
    })]
  # Checks the API of a library with run_javascript, as its description tells.
  if 'run_javascript library test' in text:
    library_url = portal_url + '/ERP5Site_fakeLibrary'
    return [tool_call_chunk('run_javascript', {
        'code': 'return Object.keys(lib[%s]).join(", ");' % json.dumps(library_url),
        'libraries': [library_url],
    })]

  # testOfficeJSHarnessAISpawnSubagentTool.zpt: a sub-agent on an endless task
  # gets one last request without tools at its turn limit.
  if 'spawn_subagent turn limit test' in text:
    return [tool_call_chunk('spawn_subagent', {
        'task': 'Please run the endless run_wasm loop',
        'max_turns': 4,
    })]
  if text.startswith('turn limit reached: you can not call tools anymore'):
    return [text_chunk('Partial answer after the turn limit.')]

  # testOfficeJSHarnessAIThinking.zpt: the Thinking setting adds chat_template_kwargs.
  if 'check thinking parameter' in text:
    chat_template_kwargs = body.get('chat_template_kwargs') or {}
    if chat_template_kwargs.get('enable_thinking') and chat_template_kwargs.get('preserve_thinking'):
      return [text_chunk('Thinking parameter: enabled.')]
    return [text_chunk('Thinking parameter: absent.')]

  # testOfficeJSHarnessAIProxyServer.zpt: through ERP5Site_fakeProxy.
  if 'proxy http_request test' in text:
    return [tool_call_chunk('http_request', {'url': ENDPOINT_URL + '?fake_proxy_redirect=1'})]
  if 'proxy dns test' in text:
    return [tool_call_chunk('http_request', {'url': 'https://does-not-exist.invalid/'})]

  # testOfficeJSHarnessAIChat.zpt: the report is written in the same response
  # as a tool call, and must stay in the task's answer ("report_test" above).
  if 'report in tool turn test' in text:
    return [
        text_chunk('REPORT-BODY: the whole report.'),
        tool_call_chunk('http_request', {'url': ENDPOINT_URL, 'report_test': True}),
    ]

  # testOfficeJSHarnessAIThinking.zpt: reasoning streamed before a tool call,
  # like llama.cpp/vLLM ("reasoning_test" above).
  if 'reasoning tool test' in text:
    return [
        reasoning_chunk(REASONING_TEST_TEXT[:20]),
        reasoning_chunk(REASONING_TEST_TEXT[20:]),
        tool_call_chunk('http_request', {'url': ENDPOINT_URL, 'reasoning_test': True}),
    ]

  # testOfficeJSHarnessAIHttpRequestTool.zpt: the result lists the match.
  if 'http_request pattern tool test' in text:
    return [tool_call_chunk('http_request', {'url': ENDPOINT_URL, 'pattern': 'fake http'})]

  # Loops continued in reply_to_tool_result.
  if 'repeated http_request tool test' in text:
    return [tool_call_chunk('http_request', REPEAT_TEST_ARGUMENTS)]
  if 'endless run_wasm loop' in text:
    return [tool_call_chunk('run_wasm', endless_test_arguments(1))]
  if 'stuck http_request tool test' in text:
    return [tool_call_chunk('http_request', STUCK_TEST_ARGUMENTS)]
  if 'repeated define_tool list test' in text:
    return [tool_call_chunk('define_tool', DEFINE_TOOL_LIST_REPEAT_ARGUMENTS)]
  # Only meaningful with SMALL_CONTEXT_MODEL selected.
  if 'compaction context test' in text:
    return [tool_call_chunk('run_javascript', compaction_test_arguments(1))]

  # testOfficeJSHarnessAISpawnSubagentTool.zpt: the sub-agent runs the
  # "http_request tool test" below, so the final reply starts with
  # "Tool result: Tool result:" only if it really went through the sub-agent.
  if 'spawn_subagent tool test' in text:
    return [tool_call_chunk('spawn_subagent', {'task': 'Please run the http_request tool test'})]
  if 'http_request tool test' in text:
    return [tool_call_chunk('http_request', {'url': ENDPOINT_URL})]

  # testOfficeJSHarnessAIDefineTool.zpt: the define/list/remove lifecycle,
  # always on the "double" tool.
  if 'define_tool list test' in text:
    return [tool_call_chunk('define_tool', {'command': 'list'})]
  if 'remove the double tool' in text:
    return [tool_call_chunk('define_tool', {'command': 'remove', 'name': 'double'})]

  # testOfficeJSHarnessAIExecutionPlanTool.zpt: "set" a plan, chained with an
  # "update_step" in reply_to_tool_result. A second plan in a later message
  # must not change the first one; the long plan is for visual checks.
  if 'long execution plan tool test' in text:
    return [tool_call_chunk('execution_plan', {
        'command': 'set',
        'goal': 'Ship a small feature end-to-end, from requirements to a summary report.',
        'step_list': [
            {'title': 'Gather requirements'},
            {'title': 'Design the approach'},
            {'title': 'Implement the core logic'},
            {'title': 'Test the implementation'},
            {'title': 'Write the summary report'},
        ],
    })]
  if 'execution plan tool test' in text:
    return [tool_call_chunk('execution_plan', {
        'command': 'set',
        'goal': 'Prove the execution-plan checklist works end-to-end.',
        'step_list': [{'title': 'Check something'}, {'title': 'Do the thing'}],
    })]
  if 'archive plan tool test' in text:
    return [tool_call_chunk('execution_plan', {
        'command': 'set',
        'goal': 'Second goal: prove the old plan is not erased by a new one.',
        'step_list': [{'title': 'Second plan step'}],
    })]

  # testOfficeJSHarnessAIDefineTool.zpt: any other message mentioning "define".
  if 'define' in text:
    return [tool_call_chunk('define_tool', {
        'command': 'define',
        'name': 'double',
        'description': 'Test tool "double" for Zelenium coverage.',
        'parameters': {
            'type': 'object',
            'properties': {'n': {'type': 'number'}},
            'required': ['n'],
        },
        'code': 'return args.n * 2;',
    })]

  # testOfficeJSHarnessAISkillInjection.zpt: the short <available_skills>
  # listing is always in a system message, the full instructions never
  # (they are only loaded by the load_skill tool).
  if 'check for skill injection' in text:
    system_text_list = [message_text(m) for m in message_list if m.get('role') == 'system']
    skill_listing_found = any(
        '<available_skills>' in t and 'create_html_report' in t for t in system_text_list)
    full_instructions_leaked = any('Do not add CSS' in t for t in system_text_list)
    return [text_chunk('Skill listing detected: %s, full instructions leaked: %s' % (
        skill_listing_found, full_instructions_leaked))]

  # testOfficeJSHarnessAIAttachmentUpload.zpt: a text attachment is inlined,
  # an image becomes an image_url part, a PDF becomes a "call pdf_to_text" hint.
  if 'please confirm text attachment' in text and 'hello attachment world' in text:
    return [text_chunk('I can see the attachment text: Hello attachment world')]
  if 'please confirm image attachment' in text and message_has_image(last_message):
    return [text_chunk('I can see an image attachment.')]
  if 'please confirm pdf attachment' in text and 'pdf_to_text' in text:
    return [text_chunk('I see a PDF attachment - I should call pdf_to_text to read it.')]

  return [text_chunk('Hello from the fake LLM!')]


# --- Choose the reply --------------------------------------------------------

first_message = message_list[0] if message_list else {}
first_system_content = (first_message.get('content') or '') if first_message.get('role') == 'system' else ''
crlf_stream = False

# 2. Compaction summary requests (compactMessageList): SUMMARY-ONE only when
# the long tool results were truncated, SUMMARY-TWO only when SUMMARY-ONE was
# passed as <previous-summary>.
if first_system_content.startswith('Summarize the conversation given'):
  # testOfficeJSHarnessAIStoredCompaction.zpt
  if 'STORED-COMPACTION-ONE' in last_content:
    chunk_list = [text_chunk('STORED-SUMMARY: the first long answer was summarized.')]
  elif 'more characters truncated' in last_content:
    chunk_list = [text_chunk('SUMMARY-ONE: compaction context test in progress.')]
  else:
    chunk_list = [text_chunk('SUMMARY-UNTRUNCATED')]
elif first_system_content.startswith('Update the summary given'):
  if '<previous-summary>\nSUMMARY-ONE' in last_content:
    chunk_list = [text_chunk('SUMMARY-TWO: merged with the previous summary.')]
  else:
    chunk_list = [text_chunk('SUMMARY-BAD')]
elif last_message.get('role') == 'tool':
  chunk_list = reply_to_tool_result()
else:
  chunk_list = reply_to_user_message()
  crlf_stream = 'crlf stream test' in last_content_lower


# --- Write the SSE stream ----------------------------------------------------

# Last frame: only "usage", like a real backend with include_usage.
if body.get('model') == SMALL_CONTEXT_MODEL:
  # Same 3.5 characters per token as the client's own estimate.
  prompt_tokens = int(len(json.dumps(message_list, separators=(',', ':'))) / 3.5)
else:
  prompt_tokens = 500
chunk_list = chunk_list + [{'choices': [], 'usage': {
    'prompt_tokens': prompt_tokens,
    'completion_tokens': 50,
    'total_tokens': prompt_tokens + 50,
}}]

if crlf_stream:
  # Frames separated by "\r\n\r\n", each JSON split over two "data:" lines
  # right after its first ": " (between two tokens, so it joins back with "\n").
  body_text = ''
  for chunk in chunk_list:
    frame = json.dumps(chunk)
    split_index = frame.index(': ') + 2
    body_text += 'data: %s\r\ndata: %s\r\n\r\n' % (frame[:split_index], frame[split_index:])
  body_text += 'data: [DONE]\r\n\r\n'
else:
  body_text = ''.join('data: %s\n\n' % json.dumps(chunk) for chunk in chunk_list) + 'data: [DONE]\n\n'

response.setHeader('Content-Type', 'text/event-stream')
return body_text
