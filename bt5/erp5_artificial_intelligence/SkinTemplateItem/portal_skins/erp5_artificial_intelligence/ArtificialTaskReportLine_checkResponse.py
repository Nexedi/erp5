"""Read the answer of one Artificial Task Report Line at the provider.

The Document Component `ArtificialTaskReportLine` calls this script from the
method `checkResponse` and from the method `cancelRequest`. The Alarm
`check_artificial_task_report_line_response` calls the method `checkResponse`
on every line in the state `started`.

The script performs one read at the provider. The script records the answer
only when the answer is ready. The script writes nothing when the provider
still holds the work. The script calls no network when the line already
holds one answer line.

WARNING: this script must never run inside one web request. A web request
bypasses the workflow, the permission and the serialization tag. The first
guard raises `Unauthorized` when the caller passes `REQUEST`.

WARNING: a transport error is not an answer. A transport error must never end
one run. The script answers a text and leaves the line in the state
`started`. The stuck rule ends a line that waits too long.

NOTE: one run can hold one file at the provider. The key `file_id` inside the
property `request_parameter` names that file. The script releases that file on
every path that ends the run. The script keeps that file on every path that
leaves the line in the state `started`.
"""
import json

from DateTime import DateTime
from zExceptions import Unauthorized

# The script cancels a request that stays longer at the provider.
MAXIMUM_REQUEST_DURATION_SECOND = 1800

SECOND_PER_DAY = 86400.0

# The provider ended and billed these answers. Keep them unchanged.
PROVIDER_TERMINAL_TUPLE = ('completed', 'failed', 'incomplete')

# A nested function cannot rebind a name of the script body. Use a list.
last_error_text_list = [u'']
is_file_removed_list = [False]

# Zope passes `REQUEST` to every published script. One activity passes no
# `REQUEST`. The raise therefore stops every call that comes over HTTP.
if REQUEST is not None:
  raise Unauthorized

LINE_PORTAL_TYPE = 'Artificial Task Report Line'

line = context

if line.getSimulationState() != 'started':
  return 'the line is not started'

report = line.getParentValue()

# A line with an answer needs no read, or the Alarm reads it for ever. Read
# the container: the catalog is not up to date inside this transaction.
line_relative_url = line.getRelativeUrl()
for sibling in report.objectValues(portal_type=LINE_PORTAL_TYPE):
  if sibling.getCausality() == line_relative_url:
    return line.ArtificialTaskReportLine_processRequest()

response_id = line.getDestinationReference()
if not response_id:
  # The send activity still runs. WARNING: a cancel here stops nothing.
  return 'the line holds no response identifier'

if line.hasErrorActivity():
  # One activity of this line failed. A human must read that activity first.
  return 'the line holds one activity in error'

artificial_task = report.getFollowUpValue(portal_type='Artificial Task')

connector = line.getConnectorValue()
if connector is None and artificial_task is not None:
  # TODO: acquire `connector` on the portal type, and remove this fallback.
  connector = artificial_task.getConnectorValue()
if connector is None:
  return 'the line and the Artificial Task hold no connector'


def safeText(value):
  """Return one text of one value. This function never raises.

  A message of one exception can hold a character that is not ASCII. The
  built in function `str` raises on such a message.
  """
  try:
    return u'%s' % (value, )
  except Exception:
    pass
  # A comment of a user can arrive as UTF-8 bytes. `repr` is not readable.
  try:
    return value.decode('utf-8')
  except Exception:
    pass
  try:
    return u'%s' % (repr(value), )
  except Exception:
    return u'the text of this value is not readable'


def removeProviderFile():
  """Delete the file of this run at the provider. This function never raises.

  The key `file_id` lives inside the JSON of the property
  `request_parameter`. The upload of the first round writes that key. Every
  line of the run copies the property, so this line also holds the key.

  Call this function only on one path that ends the run. A line that stays in
  the state `started` still needs the file for one later round.

  NOTE: `ArtificialTaskReportLine_processRequest` holds one function of the
  same shape. A second delete call costs one request and changes no state.
  This function answers at once after the first call.

  A failed delete leaves one paid file at the provider. A raise ends one run.
  This function therefore never raises.
  """
  if is_file_removed_list[0]:
    return
  is_file_removed_list[0] = True
  try:
    request_parameter = line.getRequestParameter()
    if not request_parameter:
      return
    parameter_dict = json.loads(request_parameter)
    if not isinstance(parameter_dict, dict):
      return
    file_id = parameter_dict.get('file_id')
    if not file_id:
      return
    connector.removeFile(file_id)
  except Exception:
    pass


def getRequestAgeInSecond():
  """Return the age of the request in seconds. Return 0 on a broken date.

  `ArtificialTaskReportLine_sendRequest` writes `start_date` before it starts
  the activity. `start_date` is therefore the clock of this rule.
  """
  start_date = line.getStartDate()
  if start_date is None:
    return 0
  try:
    return (DateTime() - start_date) * SECOND_PER_DAY
  except Exception:
    return 0


def buildCancelledAnswer(error_text):
  """Return one answer that says that the request is cancelled.

  The provider did not send this answer. This script builds this answer when
  the provider sends no answer at all.

  WARNING: the identifier of this answer must be the `destination_reference`
  of the line. `ArtificialTaskReportLine_processRequest` refuses one answer
  that names another line.
  """
  return {
    'id': response_id,
    'status': 'cancelled',
    'is_done': True,
    'content': '',
    'tool_calls': [],
    'model': line.getModel(),
    'usage': {
      'prompt_tokens': 0,
      'completion_tokens': 0,
      'total_tokens': 0,
      'cached_tokens': 0,
    },
    'error': {'code': 'cancelled', 'message': error_text},
    'file_id': None,
  }


def isResponseNotFound(error):
  """Answer true when the provider does not hold this response.

  The connector raises one `ValueError` for the HTTP status 404. The text of
  that error starts with `LLM 404 error`. No answer exists for such a
  response, so the caller must end the line.
  """
  return u'LLM 404 error' in safeText(error)


def stopRequestAtProvider(cancel_text, is_user_cancel):
  """Stop the request at the provider. Answer one response, or answer None.

  `is_user_cancel` true means that one user stopped the run. This function
  then forces the status `cancelled`. An answer of the provider must not
  restart one run that a user stopped.

  `is_user_cancel` false means that the request is too old. The provider
  bills every answer that the provider completed. This function then keeps
  one real answer, and this function reads the provider one more time after
  one failed cancel.

  The answer None means that the provider gives no state. The caller must
  then leave the line in the state `started`.

  The answer holds the `usage` of the provider, or zeros.

  WARNING: this function passes no `file_id` to `cancelResponse` and no
  `file_id` to `retrieveResponse`. Both methods delete the file on
  the first answer that is done. `retrieveResponse` therefore deletes the
  file of one run that continues. The caller of this function calls
  `removeProviderFile` on every path that ends the run.
  """
  try:
    response = connector.cancelResponse(response_id)
  except Exception as cancel_error:
    failed_cancel_text = (
      u'%s The cancel call failed: %s'
      % (safeText(cancel_text), safeText(cancel_error)))
    if is_user_cancel:
      # Record the cancel anyway. A line that stays `started` for ever is
      # worse than one wrong count.
      return buildCancelledAnswer(failed_cancel_text)
    # WARNING: a 404 on the cancel sub-path does not prove that the response
    # is absent. Read the provider again.
    try:
      response = connector.retrieveResponse(response_id)
    except Exception as retrieve_error:
      if isResponseNotFound(retrieve_error):
        return buildCancelledAnswer(failed_cancel_text)
      # The provider gives no state. `endStuckRequest` writes this text.
      last_error_text_list[0] = failed_cancel_text
      return None
    if response.get('is_done'):
      return response
    last_error_text_list[0] = failed_cancel_text
    return None
  if not is_user_cancel and response.get('status') in PROVIDER_TERMINAL_TUPLE:
    # The provider ended and billed this response before the cancel. Keep it.
    return response
  # The guard of the request script accepts this identifier only.
  response['id'] = response_id
  response['status'] = 'cancelled'
  response['is_done'] = True
  response['content'] = ''
  response['tool_calls'] = []
  response['error'] = {'code': 'cancelled',
                       'message': safeText(cancel_text)}
  return response


def endStuckRequest(stuck_text):
  """End one request that the provider held for too long.

  The line stays `started` while the provider gives no state. The line ends
  at two times `MAXIMUM_REQUEST_DURATION_SECOND`.
  """
  response = stopRequestAtProvider(stuck_text, is_user_cancel=False)
  if response is None:
    if getRequestAgeInSecond() > (2 * MAXIMUM_REQUEST_DURATION_SECOND):
      removeProviderFile()
      return line.ArtificialTaskReportLine_processRequest(
        response=buildCancelledAnswer(
          u'%s The provider gave no state. %s'
          % (stuck_text, last_error_text_list[0])))
    # The provider still holds the request. Keep the file.
    return u'the response is not known yet'
  if response.get('status') == 'cancelled':
    removeProviderFile()
  # WARNING: keep the file for another status. The answer can hold a tool
  # call, and the next round then needs the file.
  return line.ArtificialTaskReportLine_processRequest(response=response)


if is_cancel:
  # Do not read the provider first: a completed answer must not restart the
  # run that a user stopped.
  cancel_response = stopRequestAtProvider(
    comment or u'A user cancelled this request.',
    is_user_cancel=True)
  removeProviderFile()
  return line.ArtificialTaskReportLine_processRequest(
    response=cancel_response)

too_old_text = (
  u'The provider held this request for more than %s seconds.'
  % (MAXIMUM_REQUEST_DURATION_SECOND, ))

# WARNING: read before you cancel. A cancel destroys a completed, paid answer.
# Pass no `file_id`: the next round can need the file.
try:
  response = connector.retrieveResponse(response_id)
except Exception as retrieve_error:
  # A raise is not an answer. Cancel only when the request is also too old.
  if getRequestAgeInSecond() > MAXIMUM_REQUEST_DURATION_SECOND:
    return endStuckRequest(too_old_text)
  return u'the response is not known yet: %s' % (safeText(retrieve_error), )

if response.get('is_done'):
  return line.ArtificialTaskReportLine_processRequest(response=response)

if getRequestAgeInSecond() > MAXIMUM_REQUEST_DURATION_SECOND:
  return endStuckRequest(too_old_text)

return 'pending'
