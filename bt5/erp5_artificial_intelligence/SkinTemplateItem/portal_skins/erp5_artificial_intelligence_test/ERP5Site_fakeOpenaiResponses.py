"""
Fake OpenAI Responses API endpoint, used only by the Zelenium tests for
erp5_harness_ai (testERP5HarnessAI*.zpt). Point the test fixture's "Openai
Connector" Url String field at this script's URL to drive
ArtificialTask_runHarnessAgent.py deterministically, with no real LLM provider
involved.

connector.createResponse() in erp5_interface_openai's OpenaiConnector.py is
always called with background=True by ArtificialTask_runHarnessAgent.py, so
it always POSTs to "<Url String>/responses" with a Responses-API payload
({model, input, tools, background: true, store: true}) and parses the answer
with _parseResponsesAnswer() - this script emits exactly the JSON shape that
expects: {id, status, output: [...], usage: {input_tokens, output_tokens,
total_tokens}}. status "completed" is a terminal status, so is_done is True
and the harness never needs to poll retrieveResponse - one call finishes the
whole turn, no streaming or background polling to simulate.

The reply is chosen statelessly from the "input" list already present in the
request body (built by OpenaiConnector._buildResponsesInput from the chat
message list), so no server-side counter/session state is needed. The LAST
input item's shape picks the branch:
- {"type": "function_call_output", ...}       -> a final answer echoing that
                                                  tool's result
- {"type": "message", ...} whose content
  contains "fake_tool test"                   -> a function_call output item
                                                  invoking fake_tool with a
                                                  canned "quantity" argument
                                                  (testERP5HarnessAIToolCall.zpt)
- {"type": "message", ...} whose content
  contains "hello again"                      -> a different fixed plain-text
                                                  final answer, so a restart's
                                                  second turn is distinguishable
                                                  from its first in the page
                                                  (testERP5HarnessAIRestart.zpt)
- anything else                                -> a fixed plain-text final
                                                  answer (testERP5HarnessAIBasicChat.zpt,
                                                  testERP5HarnessAIRestart.zpt's first
                                                  turn)
"""
import json

request = context.REQUEST

body = json.loads(request.get('BODY', '') or '{}')
input_list = body.get('input') or []
last_input = input_list[-1] if input_list else {}
last_input_type = last_input.get('type')


def responses_chunk(output_list):
  return {
      'id': 'resp_fake_1',
      'status': 'completed',
      'output': output_list,
      'usage': {
          'input_tokens': 500,
          'output_tokens': 50,
          'total_tokens': 550,
      },
  }


def text_output(text):
  return responses_chunk([{
      'type': 'message',
      'role': 'assistant',
      'content': [{'type': 'output_text', 'text': text}],
  }])


def function_call_output(name, arguments):
  return responses_chunk([{
      'type': 'function_call',
      'call_id': 'call_1',
      'name': name,
      'arguments': json.dumps(arguments),
  }])


if last_input_type == 'function_call_output':
  response_dict = text_output('Tool result: %s' % last_input.get('output', ''))
elif (last_input_type == 'message' and
      'fake_tool test' in (last_input.get('content') or '').lower()):
  response_dict = function_call_output('fake_tool', {'quantity': 10})
elif (last_input_type == 'message' and
      'hello again' in (last_input.get('content') or '').lower()):
  response_dict = text_output('Hello again from the fake LLM!')
else:
  response_dict = text_output('Hello from the fake LLM!')

request.RESPONSE.setHeader('Content-Type', 'application/json')
return json.dumps(response_dict)
