"""Return the message list of this Artificial Task Report.

The message list has the shape that the OpenAI interface needs. The script
reads every Artificial Task Report Line of the report. The script keeps only
the lines whose role is `user`, `assistant` or `tool`. The script sorts the
lines by the property `int_index`.

The script puts the text of every skill page in front of the message list as
a `system` message.

The script keeps one line only when the `simulation_state` of that line is
`stopped`. A line in the state `draft` is one line that no run finished. A
line in the state `started` is one request in flight. A line in the state
`cancelled` is one line that one user stopped. None of those three lines is
one message of the conversation. The provider must not read those lines.

The base category `aggregate` names one document of the run. The Artificial
Task holds the document of the whole run. One Artificial Task Report Line
holds the document of one round. The script adds one `user` message for each
such document. The script builds that message with the type based method
`asLLMMessage`.

A message that holds one file also holds the private key `_llm_file`.
`ArtificialTaskReportLine_processRequest` removes that key before the send.
WARNING: the key `_llm_file` must never reach the provider.

WARNING: this script must never raise. A raise ends the whole run with one
`error` line. A line that
holds no JSON is skipped. A skill page that is absent is skipped. An aggregate
that gives no representation is skipped.
"""
import json

LINE_PORTAL_TYPE = 'Artificial Task Report Line'

report = context
portal = report.getPortalObject()
artificial_task = report.getFollowUpValue(portal_type='Artificial Task')

message_list = []


def decodeText(value):
  """Return one unicode text of one value. This function never raises.

  WARNING: an ERP5 accessor answers UTF-8 bytes on Python 2. A byte string
  inside one unicode format makes Python 2 decode with the ASCII codec. A
  German title then raises `UnicodeDecodeError`.

  The function answers one `unicode` value without one change. The function
  decodes one byte string with the codec `utf-8` and the error handler
  `replace`. The function answers `u''` on any defect.
  """
  if value is None:
    return u''
  try:
    if isinstance(value, unicode):
      return value
  except Exception:
    return u''
  try:
    if isinstance(value, str):
      return value.decode('utf-8', 'replace')
  except Exception:
    return u''
  try:
    return u'%s' % (value, )
  except Exception:
    return u''


def buildAggregateMessage(document):
  """Return one `user` message for one aggregate document, or None.

  The function reads the type based method `asLLMMessage`.
  `product/ERP5Type/Base.py` line 3111
  answers None and raises nothing when no script exists. The caller passes no
  `fallback_script_id`, because `getattr` on one absent identifier raises.

  The function never raises. A defect gives the fallback. The fallback is the
  title and the description of the document.
  """
  representation = None
  try:
    method = document.getTypeBasedMethod('asLLMMessage')
  except Exception:
    method = None
  if method is not None:
    try:
      representation = method()
    except Exception:
      representation = None
  if not isinstance(representation, dict):
    # The fallback holds no file and never raises.
    try:
      representation = {
        'role': 'user',
        'text': u'%s\n%s' % (decodeText(document.getTitle()),
                             decodeText(document.getDescription())),
        'is_file': 0,
      }
    except Exception:
      return None
  # WARNING: the key `content` must hold unicode. One consumer compares the
  # content with one unicode literal. That comparison raises on UTF-8 bytes.
  message = {
    'role': representation.get('role') or 'user',
    'content': decodeText(representation.get('text')),
  }
  if representation.get('is_file') and representation.get('file_data'):
    # `ArtificialTaskReportLine_processRequest` removes this private key.
    message['_llm_file'] = {
      'data': representation.get('file_data'),
      'name': decodeText(representation.get('file_name')) or u'attachment.pdf',
      'media_type': representation.get('file_media_type')
                    or 'application/octet-stream',
    }
  return message


def appendAggregateMessage(document_holder):
  """Append the message of the aggregate of one document. Never raise.

  `document_holder` is the Artificial Task, or one Artificial Task Report
  Line. A holder with no aggregate appends nothing. The message list of one
  run with no aggregate is therefore the message list of today.

  The user must hold the permission
  `View` on the aggregate. This script must carry no `Manager` proxy role.
  """
  try:
    document = document_holder.getAggregateValue()
  except Exception:
    return
  if document is None:
    return
  try:
    if not portal.portal_membership.checkPermission('View', document):
      # The user may not read the aggregate. Do not stop the run.
      return
  except Exception:
    return
  try:
    message = buildAggregateMessage(document)
  except Exception:
    return
  if message is not None:
    message_list.append(message)


if artificial_task is not None:
  for skill_reference in (artificial_task.getSkillList() or []):
    skill_page = portal.web_page_module.get(skill_reference, None)
    if skill_page is None:
      # Skip an absent skill page. Do not stop the run.
      continue
    # WARNING: a Web Page accessor answers UTF-8 bytes on Python 2. Decode
    # here, or a later unicode operation raises `UnicodeDecodeError`.
    message_list.append({
      'role': 'system',
      'content': decodeText(skill_page.getTextContent()),
    })

# The document of the whole run comes after the `system` messages, so the
# prompt prefix stays stable for the cache of the provider.
if artificial_task is not None:
  appendAggregateMessage(artificial_task)

sort_key_list = []
for line in report.objectValues(portal_type=LINE_PORTAL_TYPE):
  sort_key_list.append((line.getIntIndex() or 0, line.getId(), line))
sort_key_list.sort()

MESSAGE_SIMULATION_STATE = 'stopped'

for int_index, line_id, line in sort_key_list:
  if line.getSimulationState() != MESSAGE_SIMULATION_STATE:
    # A line that is not `stopped` is not one finished message.
    continue
  text_content = line.getTextContent()
  if not text_content:
    continue
  try:
    payload = json.loads(text_content)
  except Exception:
    # The line holds no JSON. Skip the line.
    continue
  if not isinstance(payload, dict):
    continue
  role = payload.get('role')
  if role == 'user':
    # The document of one round comes before the message of that line.
    appendAggregateMessage(line)
    message_list.append({
      'role': 'user',
      'content': payload.get('content') or '',
    })
  elif role == 'assistant':
    message = {
      'role': 'assistant',
      'content': payload.get('content') or '',
    }
    if payload.get('tool_calls'):
      message['tool_calls'] = payload['tool_calls']
    message_list.append(message)
  elif role == 'tool':
    message_list.append({
      'role': 'tool',
      'tool_call_id': payload.get('tool_call_id'),
      'name': payload.get('name'),
      'content': payload.get('content') or '',
    })

return message_list
