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
- content "repeated http_request tool
  test"                                  -> calls http_request with a marked
                                             ("repeat_test") argument set; once
                                             that result comes back, this
                                             script re-issues the exact same
                                             call a second time rather than
                                             giving a final answer - the
                                             client-side guard in
                                             runClientToolCallList
                                             (gadget_officejs_harness_ai_tool_common_js.js)
                                             short-circuits that second,
                                             identical call itself (never
                                             reaching ERP5Site_fakeHttpEndpoint
                                             again) and returns its own
                                             canned "you already called this"
                                             notice as the tool result
                                             instead - this script then sees
                                             two prior matching assistant
                                             tool_calls and stops re-issuing,
                                             falling through to the generic
                                             role-"tool" branch below, which
                                             echoes that notice back as the
                                             final answer
                                             (testOfficeJSHarnessAIRepeatedToolCallGuard.zpt)
- content "check for skill injection"    -> reports back (as plain text) whether any role-"system"
                                             message in the request already carries the
                                             create_html_report skill's instructions - this skill is
                                             unconditionally prepended to every task's message_list by
                                             gadget_officejs_harness_ai_agent_js.js (window.ChatSkills.
                                             SKILL_LIST), regardless of what the user asked, so this
                                             must be true even though nothing in the user's message
                                             mentions HTML, CSS or reports
                                             (testOfficeJSHarnessAISkillInjection.zpt)
- otherwise                              -> a fixed, plain-text reply

Setting's "Model" field (gadget_officejs_harness_ai_setting_js.js's
updateModelListField) does a plain GET to "<base_url>/models" to populate its
<select> - since Base URL is pointed at this very script, that lands here as
a subpath, bound as traverse_subpath (name_subpath in this script's
Script (Python) parameters). Answer that one with a single fixed model so
Zelenium tests can select a real option instead of hacking the <select>.
"""
import json
import time

request = context.REQUEST

if traverse_subpath and traverse_subpath[0] == 'models':
  request.RESPONSE.setHeader('Content-Type', 'application/json')
  return json.dumps({'data': [{'id': 'test-model'}]})

body = json.loads(request.get('BODY', '') or '{}')
message_list = body.get('messages') or []
last_message = message_list[-1] if message_list else {}
last_content = last_message.get('content') or ''
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

if last_message.get('role') == 'tool' and last_message.get('name') == 'execution_plan':
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
          message_list, 'http_request', json.dumps(repeat_test_args())) < 2):
  # Re-issue the exact same call once - see the "repeated http_request tool
  # test" docstring entry above for why this stops after one re-issue.
  chunk = tool_call_chunk('http_request', repeat_test_args())
elif last_message.get('role') == 'tool':
  chunk = {'choices': [{'delta': {
      'content': 'Tool result: %s' % last_content,
  }}]}
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
elif 'repeated http_request tool test' in last_content_lower:
  chunk = tool_call_chunk('http_request', repeat_test_args())
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
  skill_system_message_found = any(
      m.get('role') == 'system' and 'Do not add CSS' in (m.get('content') or '')
      for m in message_list
  )
  chunk = {'choices': [{'delta': {
      'content': 'Skill detected: %s' % skill_system_message_found,
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
chunk_list = chunk_list + [{'choices': [], 'usage': {
    'prompt_tokens': 500,
    'completion_tokens': 50,
    'total_tokens': 550,
}}]

body_text = ''.join('data: %s\n\n' % json.dumps(c) for c in chunk_list) + 'data: [DONE]\n\n'

response = request.RESPONSE
response.setHeader('Content-Type', 'text/event-stream')
return body_text
