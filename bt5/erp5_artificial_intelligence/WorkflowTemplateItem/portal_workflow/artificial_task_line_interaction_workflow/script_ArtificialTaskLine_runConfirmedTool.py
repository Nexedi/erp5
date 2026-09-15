# Only the Confirm click of one user runs the deferred tool. The tool must be
# in `ArtificialTask_getDeferrableToolIdList`. This script must never raise.

DEFERRABLE_TOOL_SCRIPT_ID = 'ArtificialTask_getDeferrableToolIdList'

line = state_change.object

try:
  from Products.ERP5Type.Log import log
  log('artificial_task_line_confirm', 'ENTER line=%s' % line.getRelativeUrl())
except Exception:
  pass

tool = None
tool_id = None
answer_text = None
error_text = None
state_text = None

try:
  tool = line.getSpecialiseValue()
except Exception as error:
  tool = None
  error_text = repr(error)

if tool is None:
  # No tool is linked. This is one ordinary Artificial Task Line.
  return

portal_type_text = None
try:
  portal_type_text = tool.getPortalType()
except Exception as error:
  portal_type_text = None
  error_text = repr(error)

if portal_type_text != 'Python Script':
  return

try:
  tool_id = tool.getId()
except Exception as error:
  tool_id = None
  error_text = repr(error)

# Fail closed. An absent script, and a script that raises, both give None.
deferrable_tool_id_tuple = None
try:
  allow_list_method = getattr(line, DEFERRABLE_TOOL_SCRIPT_ID, None)
  if allow_list_method is not None:
    answer = allow_list_method()
    deferrable_tool_id_tuple = () if answer is None else tuple(answer)
except Exception as error:
  deferrable_tool_id_tuple = None
  error_text = repr(error)

if deferrable_tool_id_tuple is None:
  try:
    line.setDescription(
      'Tool refused: the allow list is not available.')
  except Exception:
    pass
  return

if tool_id not in deferrable_tool_id_tuple:
  refusal_text = 'Tool refused: %s is not in the allow list.' % tool_id
  try:
    line.setDescription(refusal_text)
  except Exception:
    pass
  try:
    from Products.ERP5Type.Log import log
    log('artificial_task_line_confirm',
        'REFUSED line=%s tool=%r allow_list=%r' % (
          line.getRelativeUrl(), tool_id, deferrable_tool_id_tuple))
  except Exception:
    pass
  return

try:
  answer_text = str(tool(line.getTextContent() or ''))
except Exception as error:
  answer_text = None
  error_text = repr(error)

try:
  if answer_text is not None:
    line.setDescription('Tool answer: %s' % answer_text)
  else:
    line.setDescription('Tool failed: %s' % error_text)
except Exception as error:
  if error_text is None:
    error_text = repr(error)

try:
  line.stop()
except Exception:
  try:
    line.start()
    line.stop()
  except Exception:
    pass

try:
  state_text = line.getSimulationState()
except Exception:
  state_text = None

try:
  from Products.ERP5Type.Log import log
  log('artificial_task_line_confirm',
      'line=%s tool=%s answer=%r error=%r state=%r' % (
        line.getRelativeUrl(), tool_id, answer_text, error_text,
        state_text))
except Exception:
  pass
