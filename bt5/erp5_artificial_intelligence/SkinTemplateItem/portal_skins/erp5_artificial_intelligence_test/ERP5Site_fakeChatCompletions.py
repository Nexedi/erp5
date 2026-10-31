"""
Fake OpenAI-compatible chat/completions endpoint, used only by the Zelenium
tests for officejs_harness_ai (testOfficeJSHarnessAI*.zpt). Point the
harness's Setting "Base URL" at this script's URL to drive the browser-side
agent loop deterministically, with no real LLM provider involved.

requestProcessTask() in gadget_officejs_harness_ai_artificial_task_view_js.js
always sends {model, stream: true, messages, tools} and parses the response
as an OpenAI-style SSE stream via consumeOpenAIStream() - this script emits
exactly that wire format (one or more "data: {...}\n\n" frames, then
"data: [DONE]\n\n"). consumeOpenAIStream() just buffers and splits on "\n\n",
accumulating each frame's delta.content onto the running total (standard
OpenAI incremental-delta semantics - see applyStreamChunk), so a multi-frame
reply genuinely exercises showStreamingDelta's incremental showMessage path,
not just a single complete-content call.

The reply is chosen statelessly, from the conversation already present in the
request body, so no server-side counter/session state is needed. The last
message's role/content picks the branch:
- role "tool"                            -> final answer echoing the tool result
- content "please stall for the cancel
  test"                                  -> sleeps 5s first (see below), then a
                                             plain reply - gives a Zelenium test
                                             a window to click Cancel
- content "please stream a reply in
  parts"                                 -> three separate SSE frames, each
                                             with a small delta.content chunk,
                                             instead of the usual single frame
- content "please return an llm error"   -> responds with HTTP 500 instead of
                                             the usual 200, so requestProcessTask's
                                             "!response.ok" branch throws and the
                                             agent loop's error path runs
- content "<tool> tool test"             -> a tool_calls chunk invoking that
                                             built-in tool with canned arguments
                                             (one per gadget_officejs_harness_ai_tool_*.html
                                             gadget, including
                                             list_defined_tools - no arguments
                                             needed, it just lists whatever is
                                             already defined)
- content "remove the double tool"       -> a tool_calls chunk invoking
                                             undefine_tool for "double"
- content "execution plan tool test"     -> a tool_calls chunk invoking the
                                             single execution_plan tool with
                                             command "set" and two canned
                                             steps; once the client's tool
                                             result comes back (role "tool",
                                             name "execution_plan"), the
                                             role-"tool" branch below looks at
                                             what command the preceding
                                             assistant message actually ran -
                                             a "set" gets chained with a
                                             second tool_calls chunk invoking
                                             command "update_step" (marks step
                                             0 "done"), so a single test
                                             message exercises both commands
                                             in one processTask loop, same as
                                             any other "<tool> tool test"
                                             branch; an "update_step" (i.e.
                                             the second round-trip) falls
                                             through to a plain final answer
                                             instead, so the chain stops there
- content "archive plan tool test"       -> same as above, but with a
                                             different goal/step - used to
                                             prove that calling command "set"
                                             again (for a second, unrelated goal,
                                             in a later message) never touches the
                                             first message's own, already-persisted
                                             plan snapshot - each turn's plan is
                                             permanent once stored, see
                                             storeTaskResult in
                                             gadget_officejs_harness_ai_artificial_task_view_js.js
                                             (testOfficeJSHarnessAIExecutionPlanTool.zpt's
                                             second round)
- content "long execution plan tool
  test"                                  -> execution_plan with command "set"
                                             and a longer, 5-step plan; the same
                                             generic role-"tool"/name-"execution_plan"
                                             chain above still applies, so step 0
                                             ends up "done" and steps 1-4 stay
                                             "pending" - a general-purpose fixture
                                             for exercising/visually checking a
                                             longer checklist, kept independent of
                                             the 2-step/1-step rounds above
- content mentions "define"              -> define_tool, hard-coded as "double"
                                             (testOfficeJSHarnessAIDefineTool.zpt
                                             exercises the whole
                                             define_tool/list_defined_tools/undefine_tool
                                             lifecycle on this one tool name,
                                             reusing it throughout rather than
                                             defining a separate tool per test)
- content "spawn_subagent turn limit
  test"                                  -> calls spawn_subagent with max_turns 4 on the "endless
                                             run_wasm tool test" task, which never ends. At the
                                             limit the sub-agent sends one last request without
                                             tools, ending with its turn limit prompt, answered
                                             with "Partial answer after the turn limit."
                                             (testOfficeJSHarnessAISpawnSubagentTool.zpt)
- content "check thinking parameter"    -> reports whether the request carries
                                             chat_template_kwargs {enable_thinking: true,
                                             preserve_thinking: true}, which the Thinking
                                             setting adds: "Thinking parameter: enabled." or
                                             "Thinking parameter: absent."
                                             (testOfficeJSHarnessAIThinking.zpt)
- content "please work then stall for
  the cancel test"                       -> writes "WORK-DONE-BEFORE-CANCEL." with an
                                             http_request call, then stalls 5 seconds on the
                                             next request, so the user cancels after some text
                                             was written (testOfficeJSHarnessAICancelRequest.zpt)
- content "report in tool turn test"    -> writes "REPORT-BODY: the whole report." in the same
                                             response as an http_request call, then ends with a
                                             short "The full report is above." - the client must
                                             keep the report in the answer of the task
                                             (testOfficeJSHarnessAIChat.zpt)
- content "reasoning tool test"         -> streams a delta.reasoning_content chunk before an
                                             http_request call, like llama.cpp/vLLM reasoning
                                             models. On the next request it checks that the
                                             previous assistant message carries that reasoning
                                             in reasoning_content, and answers "The reasoning
                                             was sent back." or "The reasoning was lost."
                                             (testOfficeJSHarnessAIThinking.zpt)
- content "http_request pattern tool test"
                                         -> calls http_request on ERP5Site_fakeHttpEndpoint with
                                             pattern "fake http": the result lists the match
                                             instead of the page text
                                             (testOfficeJSHarnessAIHttpRequestTool.zpt)
- content "repeated http_request tool
  test"                                  -> calls http_request with a marked
                                             ("repeat_test") argument set; once
                                             that result comes back, this
                                             script re-issues the exact same
                                             call until it was made three
                                             times (TOOL_CALL_REPEAT_LIMIT)
                                             rather than giving a final
                                             answer - the client-side guard in
                                             runClientToolCallList
                                             (gadget_officejs_harness_ai_tool_manager_js.js)
                                             short-circuits that third,
                                             identical call itself (never
                                             reaching ERP5Site_fakeHttpEndpoint
                                             again) and returns its own
                                             canned "you already called this"
                                             notice as the tool result
                                             instead - this script then sees
                                             three prior matching assistant
                                             tool_calls and stops re-issuing,
                                             falling through to the generic
                                             role-"tool" branch below, which
                                             echoes that notice back as the
                                             final answer
                                             (testOfficeJSHarnessAIRepeatedToolCall.zpt)
- content "repeated list_defined_tools
  tool test"                              -> calls list_defined_tools (marked with a
                                             "repeat_test" argument, silently ignored by the
                                             real tool) four times in a row - one more than
                                             TOOL_CALL_REPEAT_LIMIT - proving its allow_repeat
                                             flag (gadget_officejs_harness_ai_tool_list_defined_tools_js.js)
                                             exempts it from the client-side guard entirely:
                                             unlike the http_request case above, every one of
                                             the four calls reaches the real tool and returns
                                             its genuine result, so the guard's canned "you
                                             already called this" notice must never appear
                                             (testOfficeJSHarnessAIRepeatedToolCall.zpt)
- content "stuck http_request tool test" -> calls http_request with a marked ("stuck_test")
                                             argument set, then keeps re-issuing that exact
                                             call after every result, even once http_request
                                             has been dropped from the request's tools - a
                                             model that ignores the guard notice. The client
                                             must stop on its own: it hides the tool after the
                                             4th call and ends the task with an error before
                                             the 6th LLM request
                                             (testOfficeJSHarnessAIRepeatedToolCall.zpt)
- content "endless run_wasm loop" -> calls run_wasm with a new constant on every turn,
                                             forever - a task that never gives a final answer
                                             (used through "spawn_subagent turn limit test")
- content "check for skill injection"    -> reports back (as plain text) whether any role-"system"
                                             message in the request already carries the lightweight
                                             <available_skills> name+description listing for the
                                             create_html_report skill - gadget_officejs_harness_ai_
                                             agent_js.js unconditionally prepends this short listing
                                             (built by skill_manager's formatSkillListForPrompt()) to
                                             every task's message_list regardless of what the user
                                             asked, so this must be true even though nothing in the
                                             user's message mentions HTML, CSS or reports - but the
                                             skill's full instructions must NOT also be there: those
                                             are only loaded on demand, via the load_skill tool
                                             (gadget_officejs_harness_ai_tool_load_skill_js.js)
                                             (testOfficeJSHarnessAISkillInjection.zpt)
- content "please confirm text
  attachment" + the message also
  contains the known fixture text        -> confirms a text/* attachment's DECODED content really
                                             reached this script (getAttachmentContentPart in
                                             gadget_chat_ui_js.js inlines it as plain text onto the
                                             message's string content) - the branch only matches if
                                             the fixture text is actually present, so this is a real
                                             end-to-end check, not just a trigger-phrase match
                                             (testOfficeJSHarnessAIAttachmentUpload.zpt)
- content "please confirm image
  attachment" + the message's content
  is a list with an image_url part       -> confirms an image/* attachment became a real structured
                                             multimodal content part (not flattened text) - message_text()/
                                             message_has_image() below handle the "content" field being
                                             a list of parts (see note above their definitions)
                                             (testOfficeJSHarnessAIAttachmentUpload.zpt)
- content "please confirm pdf
  attachment" + the message also
  mentions "pdf_to_text"                 -> confirms a PDF attachment produced the "call pdf_to_text"
                                             skip-placeholder text (PDF content itself is never inlined -
                                             see getAttachmentContentPart) - this does NOT exercise the
                                             real pdf_to_text tool/pdf.js/CDN, only the placeholder text
                                             (testOfficeJSHarnessAIAttachmentUpload.zpt)
- content "spawn_subagent tool test"     -> calls spawn_subagent with a task that is itself the
                                             "http_request tool test" phrase, so the sub-agent's own
                                             loop (driven by this same script) runs http_request and
                                             echoes its result back; the parent then echoes the
                                             sub-agent's answer, giving a final reply that starts with
                                             "Tool result: Tool result:" only when the result really
                                             went through the sub-agent
                                             (testOfficeJSHarnessAISpawnSubagentTool.zpt)
- content "compaction context test"      -> only meaningful with SMALL_CONTEXT_MODEL selected (its
                                             tiny context window makes the client compact after two
                                             tool rounds): keeps calling execute_javascript, each
                                             call returning ~5000 characters, until the history
                                             carries SUMMARY-TWO, then gives a final answer
                                             (testOfficeJSHarnessAICompaction.zpt)
- first message is the compaction
  SUMMARIZATION_PROMPT                   -> a summary request from compactMessageList: answers
                                             SUMMARY-ONE, but only when the long tool results were
                                             truncated in the request (else SUMMARY-UNTRUNCATED)
- first message is the compaction
  UPDATE_SUMMARIZATION_PROMPT            -> answers SUMMARY-TWO, but only when SUMMARY-ONE was passed
                                             in <previous-summary> tags (else SUMMARY-BAD)
- otherwise                              -> a fixed, plain-text reply

Setting's "Model" field (gadget_officejs_harness_ai_setting_js.js's
updateModelListField) does a plain GET to "<base_url>/models" to populate its
<select> - since Base URL is pointed at this very script, that lands here as
a subpath, bound as traverse_subpath (name_subpath in this script's
Script (Python) parameters). Answer that one with fixed models so Zelenium
tests can select a real option instead of hacking the <select>: "test-model"
first (selected by every test through the shared macro) without any context
window size, and SMALL_CONTEXT_MODEL reporting a tiny max_model_len (the vLLM
field), so the client compacts history after a few tool calls. For that model
only, usage.prompt_tokens follows the request size, since the client uses it
to estimate the context size - every other model keeps the fixed numbers
testOfficeJSHarnessAIChat.zpt checks.
"""
import json
import time

request = context.REQUEST

SMALL_CONTEXT_MODEL = 'test-model-small-context'

if traverse_subpath and traverse_subpath[0] == 'models':
  request.RESPONSE.setHeader('Content-Type', 'application/json')
  return json.dumps({'data': [
      {'id': 'test-model'},
      {'id': SMALL_CONTEXT_MODEL, 'max_model_len': 4000},
  ]})

body = json.loads(request.get('BODY', '') or '{}')
message_list = body.get('messages') or []
last_message = message_list[-1] if message_list else {}


def message_text(message):
  # A user message's "content" is a plain string, UNLESS it carries an image
  # attachment (getMessageList in gadget_chat_ui_js.js then builds an array
  # of {type:"text"|"image_url", ...} parts instead) - extract just the text
  # parts here so every existing phrase-matching branch below keeps working
  # unchanged for both shapes.
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

portal_url = context.getPortalObject().absolute_url()

if 'please return an llm error' in last_content_lower:
  request.RESPONSE.setStatus(500)
  request.RESPONSE.setHeader('Content-Type', 'text/plain')
  return 'Simulated LLM failure'


def tool_call_chunk(name, arguments):
  return {'choices': [{'delta': {
      'tool_calls': [{
          'index': 0,
          'id': 'call_1',
          'type': 'function',
          'function': {
              'name': name,
              'arguments': json.dumps(arguments),
          },
      }],
  }}]}


def define_tool_chunk(name):
  return tool_call_chunk('define_tool', {
      'name': name,
      'description': 'Test tool "%s" for Zelenium coverage.' % name,
      'parameters': {
          'type': 'object',
          'properties': {'n': {'type': 'number'}},
          'required': ['n'],
      },
      'code': 'return args.n * 2;',
  })


def repeat_test_args():
  return {'url': portal_url + '/ERP5Site_fakeHttpEndpoint', 'repeat_test': True}


def is_repeat_test_tool_call(assistant_message):
  tool_call_list = assistant_message.get('tool_calls') or []
  if not tool_call_list:
    return False
  function = tool_call_list[0].get('function') or {}
  if function.get('name') != 'http_request':
    return False
  try:
    arguments = json.loads(function.get('arguments') or '{}')
  except ValueError:
    return False
  return bool(arguments.get('repeat_test'))


def stuck_test_args():
  return {'url': portal_url + '/ERP5Site_fakeHttpEndpoint', 'stuck_test': True}


def is_stuck_test_tool_call(assistant_message):
  tool_call_list = assistant_message.get('tool_calls') or []
  if not tool_call_list:
    return False
  function = tool_call_list[0].get('function') or {}
  if function.get('name') != 'http_request':
    return False
  try:
    arguments = json.loads(function.get('arguments') or '{}')
  except ValueError:
    return False
  return bool(arguments.get('stuck_test'))


def endless_test_args(step):
  return {'wat': '(module (func (export "endless_test") (result i32) (i32.const %d)))' % step,
          'calls': [{'name': 'endless_test'}]}


def is_endless_test_call(message):
  tool_call_list = message.get('tool_calls') or []
  if not tool_call_list:
    return False
  function = tool_call_list[0].get('function') or {}
  return (function.get('name') == 'run_wasm'
          and '"endless_test"' in (function.get('arguments') or ''))


REASONING_TEST_TEXT = 'REASONING-MARKER: fetch the fake endpoint first.'


def is_cancel_test_call(message):
  tool_call_list = message.get('tool_calls') or []
  if not tool_call_list:
    return False
  function = tool_call_list[0].get('function') or {}
  return '"cancel_test"' in (function.get('arguments') or '')


def is_report_test_call(message):
  tool_call_list = message.get('tool_calls') or []
  if not tool_call_list:
    return False
  function = tool_call_list[0].get('function') or {}
  return '"report_test"' in (function.get('arguments') or '')


def is_reasoning_test_call(message):
  tool_call_list = message.get('tool_calls') or []
  if not tool_call_list:
    return False
  function = tool_call_list[0].get('function') or {}
  return '"reasoning_test"' in (function.get('arguments') or '')


def compaction_test_args(step):
  return {'code': 'return "compaction-step-%d " + "x".repeat(5000);' % step}


def is_compaction_test_call(message):
  tool_call_list = message.get('tool_calls') or []
  if not tool_call_list:
    return False
  function = tool_call_list[0].get('function') or {}
  return (function.get('name') == 'execute_javascript'
          and 'compaction-step-' in (function.get('arguments') or ''))


def list_defined_tools_repeat_args():
  return {'repeat_test': True}


def is_list_defined_tools_repeat_test_call(assistant_message):
  tool_call_list = assistant_message.get('tool_calls') or []
  if not tool_call_list:
    return False
  function = tool_call_list[0].get('function') or {}
  if function.get('name') != 'list_defined_tools':
    return False
  try:
    arguments = json.loads(function.get('arguments') or '{}')
  except ValueError:
    return False
  return bool(arguments.get('repeat_test'))


def count_matching_assistant_tool_calls(msgs, name, arguments_json):
  count = 0
  for m in msgs:
    if m.get('role') != 'assistant':
      continue
    for tc in (m.get('tool_calls') or []):
      function = tc.get('function') or {}
      if function.get('name') == name and function.get('arguments') == arguments_json:
        count += 1
  return count


chunk_list = None
first_message = message_list[0] if message_list else {}
first_system_content = (first_message.get('content') or '') if first_message.get('role') == 'system' else ''
whole_request_text = json.dumps(message_list)

if first_system_content.startswith('The text above is a conversation to summarize'):
  if 'more characters truncated' in last_content:
    chunk = {'choices': [{'delta': {'content': 'SUMMARY-ONE: compaction context test in progress.'}}]}
  else:
    chunk = {'choices': [{'delta': {'content': 'SUMMARY-UNTRUNCATED'}}]}
elif first_system_content.startswith('The text above contains NEW conversation messages'):
  if '<previous-summary>\nSUMMARY-ONE' in last_content:
    chunk = {'choices': [{'delta': {'content': 'SUMMARY-TWO: merged with the previous summary.'}}]}
  else:
    chunk = {'choices': [{'delta': {'content': 'SUMMARY-BAD'}}]}
elif (last_message.get('role') == 'tool' and len(message_list) >= 2
      and is_compaction_test_call(message_list[-2])):
  # Older steps disappear from the history once summarized, so the next step
  # number comes from the visible calls plus the summary already received.
  visible_step_count = len([m for m in message_list if is_compaction_test_call(m)])
  next_step = visible_step_count + 1 + (1 if 'SUMMARY-ONE' in whole_request_text else 0)
  if 'SUMMARY-TWO' in whole_request_text:
    chunk = {'choices': [{'delta': {
        'content': 'Compaction test finished with a merged summary.',
    }}]}
  elif next_step > 6:
    # Never loop forever if the client stopped compacting.
    chunk = {'choices': [{'delta': {
        'content': 'Compaction test failed: history was not compacted.',
    }}]}
  else:
    chunk = tool_call_chunk('execute_javascript', compaction_test_args(next_step))
elif last_message.get('role') == 'tool' and last_message.get('name') == 'execution_plan':
  # Chains straight off the "execution plan tool test" branch below, without
  # needing a second user message - same one-phrase-per-tool-test convention
  # as every other "<tool> tool test" branch here. Only chain once: look at
  # what command the client just ran (the preceding assistant message's
  # tool_calls arguments) and follow a "set" with one "update_step" - chaining
  # off an "update_step" result instead would loop forever.
  previous_tool_call_list = message_list[-2].get('tool_calls') or [] if len(message_list) >= 2 else []
  previous_arguments = json.loads(previous_tool_call_list[0]['function']['arguments']) if previous_tool_call_list else {}
  if previous_arguments.get('command') == 'set':
    chunk = tool_call_chunk('execution_plan', {
        'command': 'update_step',
        'index': 0,
        'status': 'done',
        'note': 'Dry run: step looks safe, marking done.',
    })
  else:
    chunk = {'choices': [{'delta': {
        'content': 'Tool result: %s' % last_content,
    }}]}
elif (last_message.get('role') == 'tool' and len(message_list) >= 2
      and is_repeat_test_tool_call(message_list[-2])
      and count_matching_assistant_tool_calls(
          message_list, 'http_request', json.dumps(repeat_test_args())) < 3):
  # Re-issue the exact same call up to 3 calls in total - see the "repeated
  # http_request tool test" docstring entry above.
  chunk = tool_call_chunk('http_request', repeat_test_args())
elif (last_message.get('role') == 'tool' and len(message_list) >= 2
      and is_report_test_call(message_list[-2])):
  chunk = {'choices': [{'delta': {'content': 'The full report is above.'}}]}
elif (last_message.get('role') == 'tool' and len(message_list) >= 2
      and is_reasoning_test_call(message_list[-2])):
  if message_list[-2].get('reasoning_content') == REASONING_TEST_TEXT:
    chunk = {'choices': [{'delta': {'content': 'The reasoning was sent back.'}}]}
  else:
    chunk = {'choices': [{'delta': {'content': 'The reasoning was lost.'}}]}
elif (last_message.get('role') == 'tool' and len(message_list) >= 2
      and is_endless_test_call(message_list[-2])):
  # Never gives up - see the "endless run_wasm loop" docstring entry.
  chunk = tool_call_chunk('run_wasm', endless_test_args(
      len([m for m in message_list if is_endless_test_call(m)]) + 1))
elif (last_message.get('role') == 'tool' and len(message_list) >= 2
      and is_stuck_test_tool_call(message_list[-2])):
  # Never gives up - see the "stuck http_request tool test" docstring entry.
  chunk = tool_call_chunk('http_request', stuck_test_args())
elif (last_message.get('role') == 'tool' and len(message_list) >= 2
      and is_list_defined_tools_repeat_test_call(message_list[-2])
      and count_matching_assistant_tool_calls(
          message_list, 'list_defined_tools', json.dumps(list_defined_tools_repeat_args())) < 4):
  # Re-issue three times more (4 calls total) - see the "repeated list_defined_tools
  # tool test" docstring entry above: allow_repeat means none of these ever
  # get intercepted by the guard, unlike the http_request case.
  chunk = tool_call_chunk('list_defined_tools', list_defined_tools_repeat_args())
elif (last_message.get('role') == 'tool' and len(message_list) >= 2
      and is_cancel_test_call(message_list[-2])):
  # Second turn of "please work then stall for the cancel test": stalls so
  # the user can cancel after some text was already written.
  time.sleep(5)
  chunk = {'choices': [{'delta': {'content': 'Finished stalling.'}}]}
elif last_message.get('role') == 'tool':
  chunk = {'choices': [{'delta': {
      'content': 'Tool result: %s' % last_content,
  }}]}
elif 'please work then stall for the cancel test' in last_content_lower:
  chunk_list = [
      {'choices': [{'delta': {'content': 'WORK-DONE-BEFORE-CANCEL.'}}]},
      tool_call_chunk('http_request', {
          'url': portal_url + '/ERP5Site_fakeHttpEndpoint',
          'cancel_test': True,
      }),
  ]
elif 'please stall for the cancel test' in last_content_lower:
  # Real LLM providers are never instant - without this, a Zelenium test has
  # no reliable window to click Cancel before the (otherwise synchronous)
  # response below would already have arrived.
  time.sleep(5)
  chunk = {'choices': [{'delta': {'content': 'Finished stalling.'}}]}
elif 'please stream a reply in parts' in last_content_lower:
  # Each delta.content is incremental (applyStreamChunk does
  # state.content += delta.content), so this genuinely exercises
  # showStreamingDelta -> showMessage's incremental-append path with more
  # than one call, unlike every other branch here (a single frame).
  chunk_list = [
      {'choices': [{'delta': {'content': 'Hello'}}]},
      {'choices': [{'delta': {'content': ' from'}}]},
      {'choices': [{'delta': {'content': ' streaming!'}}]},
  ]
elif 'execute_javascript tool test' in last_content_lower:
  chunk = tool_call_chunk('execute_javascript', {'code': 'return "javascript-tool-test-ok";'})
elif 'run_wasm tool test' in last_content_lower:
  chunk = tool_call_chunk('run_wasm', {
      'wat': '(module (func $add (export "add") (param i32 i32) (result i32) '
             'local.get 0 local.get 1 i32.add))',
      'calls': [{'name': 'add', 'args': [2, 3]}],
  })
elif 'library_inspect tool test' in last_content_lower:
  chunk = tool_call_chunk('library_inspect', {
      'libraries': [portal_url + '/ERP5Site_fakeLibrary'],
  })
elif 'spawn_subagent turn limit test' in last_content_lower:
  chunk = tool_call_chunk('spawn_subagent', {
      'task': 'Please run the endless run_wasm loop',
      'max_turns': 4,
  })
elif last_content_lower.startswith('turn limit reached: you can not call tools anymore'):
  chunk = {'choices': [{'delta': {'content': 'Partial answer after the turn limit.'}}]}
elif 'check thinking parameter' in last_content_lower:
  chat_template_kwargs = body.get('chat_template_kwargs') or {}
  if chat_template_kwargs.get('enable_thinking') and chat_template_kwargs.get('preserve_thinking'):
    chunk = {'choices': [{'delta': {'content': 'Thinking parameter: enabled.'}}]}
  else:
    chunk = {'choices': [{'delta': {'content': 'Thinking parameter: absent.'}}]}
elif 'report in tool turn test' in last_content_lower:
  chunk_list = [
      {'choices': [{'delta': {'content': 'REPORT-BODY: the whole report.'}}]},
      tool_call_chunk('http_request', {
          'url': portal_url + '/ERP5Site_fakeHttpEndpoint',
          'report_test': True,
      }),
  ]
elif 'reasoning tool test' in last_content_lower:
  chunk_list = [
      {'choices': [{'delta': {'reasoning_content': REASONING_TEST_TEXT[:20]}}]},
      {'choices': [{'delta': {'reasoning_content': REASONING_TEST_TEXT[20:]}}]},
      tool_call_chunk('http_request', {
          'url': portal_url + '/ERP5Site_fakeHttpEndpoint',
          'reasoning_test': True,
      }),
  ]
elif 'http_request pattern tool test' in last_content_lower:
  chunk = tool_call_chunk('http_request', {
      'url': portal_url + '/ERP5Site_fakeHttpEndpoint',
      'pattern': 'fake http',
  })
elif 'repeated http_request tool test' in last_content_lower:
  chunk = tool_call_chunk('http_request', repeat_test_args())
elif 'endless run_wasm loop' in last_content_lower:
  chunk = tool_call_chunk('run_wasm', endless_test_args(1))
elif 'stuck http_request tool test' in last_content_lower:
  chunk = tool_call_chunk('http_request', stuck_test_args())
elif 'repeated list_defined_tools tool test' in last_content_lower:
  chunk = tool_call_chunk('list_defined_tools', list_defined_tools_repeat_args())
elif 'compaction context test' in last_content_lower:
  chunk = tool_call_chunk('execute_javascript', compaction_test_args(1))
elif 'spawn_subagent tool test' in last_content_lower:
  chunk = tool_call_chunk('spawn_subagent', {'task': 'Please run the http_request tool test'})
elif 'http_request tool test' in last_content_lower:
  chunk = tool_call_chunk('http_request', {
      'url': portal_url + '/ERP5Site_fakeHttpEndpoint',
  })
elif 'list_defined_tools tool test' in last_content_lower:
  chunk = tool_call_chunk('list_defined_tools', {})
elif 'remove the double tool' in last_content_lower:
  chunk = tool_call_chunk('undefine_tool', {'name': 'double'})
elif 'long execution plan tool test' in last_content_lower:
  # More realistic, longer plan - 5 steps instead of the 1-2 used by the
  # other execution-plan branches above/below, e.g. for visually checking
  # the checklist with a longer step_list.
  chunk = tool_call_chunk('execution_plan', {
      'command': 'set',
      'goal': 'Ship a small feature end-to-end, from requirements to a summary report.',
      'step_list': [
          {'title': 'Gather requirements'},
          {'title': 'Design the approach'},
          {'title': 'Implement the core logic'},
          {'title': 'Test the implementation'},
          {'title': 'Write the summary report'},
      ],
  })
elif 'execution plan tool test' in last_content_lower:
  chunk = tool_call_chunk('execution_plan', {
      'command': 'set',
      'goal': 'Prove the execution-plan checklist works end-to-end.',
      'step_list': [
          {'title': 'Check something'},
          {'title': 'Do the thing'},
      ],
  })
elif 'archive plan tool test' in last_content_lower:
  chunk = tool_call_chunk('execution_plan', {
      'command': 'set',
      'goal': 'Second goal: prove the old plan is not erased by a new one.',
      'step_list': [
          {'title': 'Second plan step'},
      ],
  })
elif 'define' in last_content_lower:
  chunk = define_tool_chunk('double')
elif 'check for skill injection' in last_content_lower:
  skill_listing_found = any(
      m.get('role') == 'system' and '<available_skills>' in (m.get('content') or '')
      and 'create_html_report' in (m.get('content') or '')
      for m in message_list
  )
  full_instructions_leaked = any(
      m.get('role') == 'system' and 'Do not add CSS' in (m.get('content') or '')
      for m in message_list
  )
  chunk = {'choices': [{'delta': {
      'content': 'Skill listing detected: %s, full instructions leaked: %s' % (
          skill_listing_found, full_instructions_leaked),
  }}]}
elif ('please confirm text attachment' in last_content_lower
      and 'hello attachment world' in last_content_lower):
  chunk = {'choices': [{'delta': {
      'content': 'I can see the attachment text: Hello attachment world',
  }}]}
elif ('please confirm image attachment' in last_content_lower
      and message_has_image(last_message)):
  chunk = {'choices': [{'delta': {
      'content': 'I can see an image attachment.',
  }}]}
elif ('please confirm pdf attachment' in last_content_lower
      and 'pdf_to_text' in last_content_lower):
  chunk = {'choices': [{'delta': {
      'content': 'I see a PDF attachment - I should call pdf_to_text to read it.',
  }}]}
else:
  chunk = {'choices': [{'delta': {'content': 'Hello from the fake LLM!'}}]}

if chunk_list is None:
  chunk_list = [chunk]

# Real OpenAI-compatible streaming (with stream_options.include_usage, which
# requestProcessTask always sets) ends with one extra frame carrying only
# "usage" and an empty/absent "choices" - added here so every response this
# script returns exercises gadget_officejs_harness_ai_agent_js.js's usage
# accumulation (gadget.usage_totals) the same way a real backend would.
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

body_text = ''.join('data: %s\n\n' % json.dumps(c) for c in chunk_list) + 'data: [DONE]\n\n'

response = request.RESPONSE
response.setHeader('Content-Type', 'text/event-stream')
return body_text
