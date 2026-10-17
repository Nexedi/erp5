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
                                             (one per gadget_officejs_harness_ai_tools_js.js
                                             local tool, including
                                             list_defined_tools - no arguments
                                             needed, it just lists whatever is
                                             already defined)
- content "remove the double tool"       -> a tool_calls chunk invoking
                                             undefine_tool for "double"
- content "execution plan tool test"     -> a tool_calls chunk invoking
                                             set_execution_plan with two canned
                                             steps; once the client's tool
                                             result comes back (role "tool",
                                             name "set_execution_plan"), the
                                             role-"tool" branch below replies
                                             with a second tool_calls chunk
                                             invoking update_execution_plan_step
                                             (marks step 0 "done") - so a
                                             single test message exercises both
                                             execution-plan tools in one
                                             processTask loop, same as any
                                             other "<tool> tool test" branch
- content "archive plan tool test"       -> same as above, but with a
                                             different goal/step - used to
                                             prove that calling set_execution_plan
                                             again (for a second, unrelated goal,
                                             in a later message) never touches the
                                             first message's own, already-persisted
                                             plan snapshot - each turn's plan is
                                             permanent once stored, see
                                             storeTaskResult in
                                             gadget_officejs_harness_ai_artificial_task_view_js.js
                                             (testOfficeJSHarnessAIExecutionPlanTool.zpt's
                                             second round)
- content mentions "define"              -> define_tool, hard-coded as "double"
                                             (testOfficeJSHarnessAIDefineTool.zpt
                                             exercises the whole
                                             define_tool/list_defined_tools/undefine_tool
                                             lifecycle on this one tool name,
                                             reusing it throughout rather than
                                             defining a separate tool per test)
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


chunk_list = None

if last_message.get('role') == 'tool' and last_message.get('name') == 'set_execution_plan':
  # Chains straight off the "execution plan tool test" branch below, without
  # needing a second user message - same one-phrase-per-tool-test convention
  # as every other "<tool> tool test" branch here.
  chunk = tool_call_chunk('update_execution_plan_step', {
      'index': 0,
      'status': 'done',
      'note': 'Dry run: step looks safe, marking done.',
  })
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
elif 'http_request tool test' in last_content_lower:
  chunk = tool_call_chunk('http_request', {
      'url': portal_url + '/ERP5Site_fakeHttpEndpoint',
  })
elif 'list_defined_tools tool test' in last_content_lower:
  chunk = tool_call_chunk('list_defined_tools', {})
elif 'remove the double tool' in last_content_lower:
  chunk = tool_call_chunk('undefine_tool', {'name': 'double'})
elif 'execution plan tool test' in last_content_lower:
  chunk = tool_call_chunk('set_execution_plan', {
      'goal': 'Prove the execution-plan checklist works end-to-end.',
      'step_list': [
          {'title': 'Check something'},
          {'title': 'Do the thing'},
      ],
  })
elif 'archive plan tool test' in last_content_lower:
  chunk = tool_call_chunk('set_execution_plan', {
      'goal': 'Second goal: prove the old plan is not erased by a new one.',
      'step_list': [
          {'title': 'Second plan step'},
      ],
  })
elif 'define' in last_content_lower:
  chunk = define_tool_chunk('double')
else:
  chunk = {'choices': [{'delta': {'content': 'Hello from the fake LLM!'}}]}

if chunk_list is None:
  chunk_list = [chunk]

body_text = ''.join('data: %s\n\n' % json.dumps(c) for c in chunk_list) + 'data: [DONE]\n\n'

response = request.RESPONSE
response.setHeader('Content-Type', 'text/event-stream')
return body_text
