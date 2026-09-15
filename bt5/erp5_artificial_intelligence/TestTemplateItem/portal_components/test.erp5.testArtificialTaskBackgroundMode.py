# -*- coding: utf-8 -*-
"""Verify the workflow driven request mechanism of the Artificial Task Report.

The subject is the portal type `Artificial Task Report Line`. One line is one
request. The transition `start` calls the method `send`. The method `send`
starts one activity. The activity writes one answer line.

WARNING: this test must not call a Large Language Model by default. Every
method either avoids the connector, or replaces the three methods
`createResponse`, `retrieveResponse` and `cancelResponse` of the connector
class. Three methods call the real service:
`test_41_realBackgroundRoundTrip`, `test_42_realCancel` and
`test_43_realCancelOfOneCompletedResponse`. The three methods run only when
the module constant REAL_LLM holds the value 1.

The test writes fixtures in the modules `artificial_task_report_module` and
`artificial_task_module` only. The test never deletes a document from a
module. The test deletes the Artificial Task Report Line objects inside the
reports that the test owns. Those lines are sub-objects of a fixture, not
module documents.

This test uses no fixed identifier. `afterSetUp` builds one suffix for every
test method, from one timestamp and one random number. Every report
identifier, every provider identifier and every activity tag holds that
suffix. The test asserts on the built value, never on one literal.
"""
import json
import logging
import random
import six
import sys
import time

from zExceptions import Unauthorized

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


ACCESS_CONTENTS_INFORMATION = 'Access contents information'

PORTAL_TYPE = 'Artificial Task Report Line'
REPORT_PORTAL_TYPE = 'Artificial Task Report'

# Prefixes only. A live test must never use one fixed identifier: an object
# of an earlier run stays on this shared instance.
PROVIDER_ID_PREFIX = 'resp_bg'
ALARM_TAG_PREFIX = 'test_ai_workflow_send_alarm'

# The prefix of the reference argument of the tool calls of this test.
REFERENCE_PREFIX = 'test_reference_'

# A read only tool of this business template. It accepts every argument.
READ_ONLY_TOOL_ID = 'ERP5Site_getCurrentTime'

# One callable of portal_callables that writes. The test never lets the agent
# reach this callable. The test proves the refusal instead.
WRITE_TOOL_ID = 'ERP5Site_createOrganisation'

# Not an own object of portal_callables: `getattr` acquires it. The allow
# list must refuse it.
ACQUIRED_ONLY_TOOL_ID = 'ArtificialTaskReport_getMessageList'

SEND_METHOD_ID = 'ArtificialTaskReportLine_sendRequest'

NON_ASCII_TEXT = u'M\xfcller \u2014 pr\xfcfung \u03a9'

PROCESS_METHOD_ID = 'ArtificialTaskReportLine_processRequest'
CHECK_METHOD_ID = 'ArtificialTaskReportLine_checkResponse'
ALARM_METHOD_ID = 'Alarm_checkArtificialTaskReportLineResponse'
ALARM_ID = 'check_artificial_task_report_line_response'

# The four status values that end one response. The connector answers
# `is_done` true for these four values only.
TERMINAL_STATUS_TUPLE = ('completed', 'failed', 'incomplete', 'cancelled')

# The stuck rule of ArtificialTaskReportLine_checkResponse. The script cancels
# one request that stays at the provider for more than this time.
MAXIMUM_REQUEST_DURATION_SECOND = 1800

# Set this constant to 0 to skip the real service.
REAL_LLM = 1

# WARNING: `test_41` to `test_43` read the model of production at run time.
# The route of background mode follows the model.
REAL_PROMPT = 'Answer with the single word ready.'
REAL_LONG_PROMPT = ('Count from 1 to 400. Write one number on every line. '
                    'Write no other text.')

# `createResponse` with background true must answer inside this time. A
# longer answer means that the provider ignored the background mode.
REAL_CREATE_BOUND_SECOND = 15

# The read loop of the real methods. The loop waits at most 240 seconds.
REAL_READ_COUNT = 120
REAL_READ_PAUSE_SECOND = 2

# The logger that holds the recorded facts of the provider. The Zope event
# log holds every line of this logger.
PROVIDER_FACT_LOGGER = logging.getLogger('testAITaskWorkflowSend')

MAXIMUM_TOOL_REQUEST_COUNT = 8
MAXIMUM_LLM_REQUEST_COUNT = 20

# These scripts must stay absent. A custom script with the proxy role
# Manager is reachable by an anonymous caller.
ADMIN_SCRIPT_ID_LIST = [
  'Admin_callCallable',
  'Admin_describeObject',
  'Admin_dumpReport',
  'Admin_listActivity',
  'Admin_newArtificialTaskForTest',
  'Admin_newReportLine',
  'Admin_probeAccessor',
  'Admin_probeConfiguration',
  'Admin_probeId',
  'Admin_probePermission',
  'Admin_runTransition',
  'Admin_setupArtificialTaskReportLine',
  'Admin_tic',
]


class ArtificialTaskTestMixin(ERP5TypeTestCase):
  """Hold the shared harness of the Artificial Task tests.

  This class holds no test method. The class
  `TestArtificialTaskBackgroundMode` holds the generic tests.
  """

  MAIL_MESSAGE_PORTAL_TYPE = 'Mail Message'
  ARTIFICIAL_TASK_PORTAL_TYPE = 'Artificial Task'
  ARTIFICIAL_TASK_LINE_PORTAL_TYPE = 'Artificial Task Line'
  PDF_SKIN_FOLDER_ID = 'erp5_artificial_intelligence'
  EVENT_REPRESENTATION_SCRIPT_ID = 'Event_asLLMMessage'
  TYPE_BASED_METHOD_ID = 'asLLMMessage'
  # `ArtificialTaskReport_getMessageList` puts the binary under this key.
  PRIVATE_FILE_KEY = '_llm_file'
  MAXIMUM_REPRESENTATION_TEXT_LENGTH = 20000
  CONNECTOR_FILE_METHOD_ID_LIST = [
    '_uploadFile', '_addFilePartToMessageList', 'removeFile']
  # One token covers about four characters. Two is a safe floor.
  MINIMUM_CHARACTER_PER_TOKEN = 2
  # The transition names that cancel one Mail Message. The cleanup tries
  # every name of this list.
  MAIL_CANCEL_TRANSITION_ID_LIST = ['cancel', 'cancel_action']

  def getTitle(self):
    return "AI Task workflow send"

  def afterSetUp(self):
    self.portal = self.getPortal()
    # The suffix of this run. Every identifier that this test writes on the
    # shared instance holds this suffix. Read `_buildUniqueSuffix`.
    self._run_identifier = self._buildUniqueSuffix()
    self._report_by_suffix = {}
    self._patched_class = None
    self._original_method = None
    self._create_call_log = []
    self._retrieve_call_log = []
    self._cancel_call_log = []
    # `beforeTearDown` closes every line of this list, also after a failure.
    self._started_line_list = []
    # The recorded facts of the provider. Only the three methods that call
    # the real service write in this list.
    self._provider_fact_list = []
    self._clearFailedActivities()
    # WARNING: `tic()` also runs the Alarm, which reads every started line of
    # the instance. Refuse to run when a line of another run waits.
    self._assertNoForeignStartedLine()
    self.tool_reference = REFERENCE_PREFIX + self._run_identifier

  def beforeTearDown(self):
    # WARNING: a patch on one class reaches every user of this Zope process.
    self._unpatchConnector()
    for line in self._started_line_list:
      try:
        self._closeStartedLine(line)
      except Exception:
        # The cleanup must never hide the error of the test.
        pass

  def _clearFailedActivities(self):
    """Drop the activities that failed for good.

    A message with processing_node -2 never runs again. tic() then loops
    forever.

    WARNING: `getMessageList` reads every row of the activity table, and
    unpickles every message. The call waits when another transaction holds
    the lock on that table. `afterSetUp` calls this method before every test
    method, so one wait stops the whole suite.

    The method therefore counts first. `countMessage` runs one SQL COUNT on
    one index. The method reads the message list only when the count is
    above zero. A healthy run gives the count zero, so the method reads no
    message list at all.

    The method also catches every error of the activity table. A locked
    activity table must not stop the suite. The test methods carry their own
    assertion on the failed messages, through
    `_getPermanentlyFailedMessageList`.
    """
    activity_tool = self.portal.portal_activities
    try:
      failed_count = activity_tool.countMessage(processing_node=-2)
    except Exception as error:
      PROVIDER_FACT_LOGGER.warning(
        'the activity table did not answer countMessage: %r', error)
      return
    if not failed_count:
      return
    PROVIDER_FACT_LOGGER.warning(
      'the activity table holds %s message(s) with processing_node -2. '
      'The suite drops them now.', failed_count)
    seen = set()
    for message in list(activity_tool.getMessageList()):
      if message.processing_node != -2:
        continue
      key = (tuple(message.object_path), message.method_id)
      if key in seen:
        continue
      seen.add(key)
      PROVIDER_FACT_LOGGER.warning(
        'the suite drops one failed activity. method_id %r. object_path %r.',
        message.method_id, message.object_path)
      try:
        activity_tool.flush(
          message.object_path, invoke=False, method_id=message.method_id,
          only_safe=False,
        )
      except Exception:
        pass
    self.commit()

  def _buildUniqueSuffix(self):
    """Return one suffix that no other run holds.

    The value holds one timestamp and one random number. The value holds
    digits only.

    WARNING: a live test must never use one fixed identifier. Read the
    comment of PROVIDER_ID_PREFIX.
    """
    return '%d%06d' % (int(time.time()), random.randint(0, 999999))

  def _buildProviderIdentifier(self, name, prefix=PROVIDER_ID_PREFIX):
    """Return one provider identifier of this run.

    The identifier reaches `destination_reference` of one real Artificial
    Task Report Line of this shared instance. The catalog holds that value.
    One fixed value therefore names the line of one earlier run too, and the
    stub of this run answers for that old line.

    `name` keeps the role of the identifier in the text.
    """
    return '%s_%s_%s' % (prefix, name, self._run_identifier)

  def _buildAlarmTag(self, name):
    """Return one activity tag of this run.

    Two runs that hold the same tag share one activity. The second call then
    starts no activity, and the test proves nothing.
    """
    return '%s_%s_%s' % (ALARM_TAG_PREFIX, name, self._run_identifier)

  def _findInheritedMethod(self, klass, method_id):
    """Return the function that `klass` holds or inherits under `method_id`.

    The method reads the class dictionary of every class of the order of
    resolution. The method answers None when no class holds the name.
    """
    class_list = list(getattr(klass, '__mro__', None) or ())
    if not class_list:
      class_list = [klass]
      index = 0
      while index < len(class_list):
        for base in getattr(class_list[index], '__bases__', ()):
          if base not in class_list:
            class_list.append(base)
        index += 1
    for one_class in class_list:
      method = one_class.__dict__.get(method_id)
      if method is not None:
        return method
    return None

  def _getReport(self, suffix):
    """Return the Artificial Task Report of `suffix` for this run.

    The first call for one suffix creates one new report. The module
    generates the identifier. The next calls answer the same report.
    """
    report = self._report_by_suffix.get(suffix)
    if report is None:
      report = self.portal.artificial_task_report_module.newContent(
        portal_type=REPORT_PORTAL_TYPE,
        title='Workflow send test %s' % (suffix, ))
      self._report_by_suffix[suffix] = report
    report.edit(follow_up_value=None)
    self.commit()
    self.tic()
    return report

  def _newLine(self, report, int_index, payload):
    """Create one Artificial Task Report Line that holds one payload.

    The send path reads the line only. A request line must therefore hold
    the connector, the model and the other send parameters before the
    transition `start`. The production script `ArtificialTask_startAgent`
    writes the same values at the creation of the line.

    The method also writes the quantity 0. ERP5 gives every new Movement
    the default `quantity=1.0`, and 1.0 is one false token count.
    """
    line = report.newContent(
      portal_type=PORTAL_TYPE,
      int_index=int_index,
      text_content=json.dumps(payload),
    )
    self._writeLineParameterList(report, line, payload)
    return line

  def _writeLineParameterList(self, report, line, payload):
    """Call the production writer of the send parameters.

    WARNING: this method must add nothing. The skin script
    `ArtificialTaskReportLine_writeRequestParameterList` is the one writer of
    the send parameters. A fixture that writes its own values proves nothing
    about the production path.

    The script writes nothing but the quantity when the report holds no
    Artificial Task. A test that proves the error path therefore keeps one
    line with no connector.
    """
    line.ArtificialTaskReportLine_writeRequestParameterList(
      artificial_task=report.getFollowUpValue(
        portal_type='Artificial Task'))

  def _getLineList(self, report):
    """Return the lines of one report in the order of int_index."""
    sort_key_list = []
    for line in report.objectValues(portal_type=PORTAL_TYPE):
      sort_key_list.append((line.getIntIndex() or 0, line.getId(), line))
    sort_key_list.sort()
    return [x[2] for x in sort_key_list]

  def _getRole(self, line):
    """Return the role of one line. Return an empty text on a broken line."""
    text_content = line.getTextContent()
    if not text_content:
      return ''
    try:
      payload = json.loads(text_content)
    except ValueError:
      return ''
    if not isinstance(payload, dict):
      return ''
    return payload.get('role') or ''

  def _countRole(self, report, role):
    count = 0
    for line in self._getLineList(report):
      if self._getRole(line) == role:
        count += 1
    return count

  def _getAnswerLineList(self, request_line):
    """Return the lines whose causality points at this request line."""
    report = request_line.getParentValue()
    relative_url = request_line.getRelativeUrl()
    return [x for x in self._getLineList(report)
            if x.getCausality() == relative_url]

  def _countActivity(self, document, method_id=PROCESS_METHOD_ID):
    """Return how many messages wait for this document and this method."""
    path = document.getPath()
    count = 0
    for message in self.portal.portal_activities.getMessageList():
      if '/'.join(message.object_path) != path:
        continue
      if method_id is not None and message.method_id != method_id:
        continue
      count += 1
    return count

  def _getPermanentlyFailedMessageList(self):
    """Return the messages that failed for good.

    39 test methods assert that this list is empty. `getMessageList` reads
    and unpickles every row of the activity table, so 39 reads are
    expensive. The method therefore counts first. `countMessage` runs one
    SQL COUNT. A count of zero gives the empty list, and the method reads no
    message.
    """
    activity_tool = self.portal.portal_activities
    if not activity_tool.countMessage(processing_node=-2):
      return []
    return [x for x in activity_tool.getMessageList()
            if x.processing_node == -2]

  def _getPortalTypeClass(self):
    return self.portal.portal_types.getPortalTypeClass(PORTAL_TYPE)

  def _newArtificialTask(self, title):
    """Create one fresh Artificial Task.

    The Artificial Task carries a workflow state. A new run needs a fresh
    state. The method therefore creates a new document on every run.
    """
    return self.portal.artificial_task_module.newContent(
      portal_type='Artificial Task', title=title)

  def _buildResponse(self, **kw):
    """Return one answer of the connector, in the shape of background mode.

    The three methods `createResponse`, `retrieveResponse` and
    `cancelResponse` all answer this shape. A caller names only the keys
    that the test needs. `is_done` follows the status when the caller names
    no value for `is_done`.
    """
    response = {
      'id': self._buildProviderIdentifier('stub'),
      'status': 'completed',
      'content': '',
      'tool_calls': [],
      'model': 'gpt-4.1',
      'usage': {},
      'error': None,
      'file_id': None,
    }
    response.update(kw)
    if 'is_done' not in kw:
      response['is_done'] = response['status'] in TERMINAL_STATUS_TUPLE
    return response

  def _patchConnectorResponses(self, response_list,
                               retrieve_response_dict=None,
                               cancel_response_dict=None):
    """Replace the three request methods of the connector class with stubs.

    An instance level patch does not survive a commit. The patch is therefore
    on the class.

    WARNING: a write of a Document Component resets the dynamic classes. This
    method reads the class of the connector again on every call. Do not keep
    the class between two calls.

    `response_list` holds the answers of `createResponse`, in order. The stub
    of `createResponse` raises when the list is empty. A second call of
    `createResponse` pays the service a second time, so the test must see
    that call.

    `retrieve_response_dict` and `cancel_response_dict` map one response
    identifier to one answer. The two stubs answer a pending response, and a
    cancelled response, for an identifier that the map does not hold. The map
    is necessary because the Alarm reads every line of the instance that
    waits, not the line of this test alone.

    The method answers the connector and the call log of `createResponse`.
    The call log of `retrieveResponse` is `self._retrieve_call_log`. The call
    log of `cancelResponse` is `self._cancel_call_log`.
    """
    connector = self.portal.ArtificialTask_getDefaultConnector()
    connector_class = connector.__class__
    self._patched_class = connector_class
    self._original_method = {}
    for method_id in ('createResponse', 'retrieveResponse',
                      'cancelResponse'):
      self._original_method[method_id] = connector_class.__dict__.get(
        method_id)
    remaining_list = [self._buildResponse(**x) for x in response_list]
    retrieve_response_dict = retrieve_response_dict or {}
    cancel_response_dict = cancel_response_dict or {}
    call_log = []
    retrieve_call_log = []
    cancel_call_log = []
    self._create_call_log = call_log
    self._retrieve_call_log = retrieve_call_log
    self._cancel_call_log = cancel_call_log
    build_response = self._buildResponse

    def create_stub(self, **kw):
      call_log.append(kw)
      if not remaining_list:
        raise AssertionError('the stub has no answer left')
      return remaining_list.pop(0)

    def retrieve_stub(self, response_id, **kw):
      retrieve_call_log.append((response_id, kw))
      if response_id in retrieve_response_dict:
        return retrieve_response_dict[response_id]
      return build_response(id=response_id, status='in_progress')

    def cancel_stub(self, response_id, **kw):
      cancel_call_log.append((response_id, kw))
      if response_id in cancel_response_dict:
        return cancel_response_dict[response_id]
      # WARNING: never answer a cancel for an unknown identifier. The Alarm
      # reads the lines of other runs. The raise shows the defect in the log.
      raise AssertionError(
        'the cancel stub does not know the identifier %s' % (response_id, ))

    connector_class.createResponse = create_stub
    connector_class.retrieveResponse = retrieve_stub
    connector_class.cancelResponse = cancel_stub
    return connector, call_log

  def _patchConnectorRaise(self, exception):
    """Make every request method of the connector class raise.

    The method answers the connector. A test that needs the call log must
    use `_patchConnectorResponses` instead.
    """
    connector = self.portal.ArtificialTask_getDefaultConnector()
    connector_class = connector.__class__
    self._patched_class = connector_class
    self._original_method = {}
    for method_id in ('createResponse', 'retrieveResponse',
                      'cancelResponse'):
      self._original_method[method_id] = connector_class.__dict__.get(
        method_id)

    def raising_stub(self, *args, **kw):
      raise exception

    connector_class.createResponse = raising_stub
    connector_class.retrieveResponse = raising_stub
    connector_class.cancelResponse = raising_stub
    return connector

  def _unpatchConnector(self):
    connector_class = self._patched_class
    if connector_class is None:
      return
    for method_id, original_method in (self._original_method or {}).items():
      if original_method is None:
        try:
          delattr(connector_class, method_id)
        except AttributeError:
          pass
      else:
        setattr(connector_class, method_id, original_method)
    self._patched_class = None
    self._original_method = None

  def _buildToolCall(self, call_id, reference, tool_name=READ_ONLY_TOOL_ID,
                     argument_dict=None):
    if argument_dict is None:
      argument_dict = {'reference': reference}
    return {
      'id': call_id,
      'type': 'function',
      'function': {
        'name': tool_name,
        'arguments': json.dumps(argument_dict),
      },
    }

  def _newArtificialTaskForReport(self, report, title, tool_list=None,
                                  with_connector=False):
    """Create one Artificial Task and link the report to that task.

    The allow list of the tool refuses every tool when the report holds no
    Artificial Task. A test that calls one tool therefore needs one task.
    """
    artificial_task = self._newArtificialTask(title)
    # WARNING: a new Artificial Task holds the real connector. Clear it, or
    # the test pays the service.
    edit_kw = {'tool_list': tool_list or [], 'connector_value': None}
    if with_connector:
      edit_kw['connector_value'] = (
        self.portal.ArtificialTask_getDefaultConnector())
      edit_kw['model'] = 'gpt-4.1'
    artificial_task.edit(**edit_kw)
    artificial_task.plan()
    artificial_task.start()
    report.edit(follow_up_value=artificial_task)
    return artificial_task

  def _getOrganisationIdList(self):
    return sorted([x for x in self.portal.organisation_module.objectIds()])

  def _getToolAnswerContent(self, request_line):
    """Return the content of the single tool answer of one request line."""
    answer_line_list = self._getAnswerLineList(request_line)
    self.assertEqual(
      1, len(answer_line_list),
      'the request produced %s answer lines' % (len(answer_line_list), ))
    payload = json.loads(answer_line_list[0].getTextContent())
    self.assertEqual('tool', payload['role'])
    return payload['content']

  def _assertOnlyConnectorError(self, report):
    """Assert that every error line of one report names the connector.

    A test that holds no connector reaches one error line at the end of the
    round. That error line must be the error about the connector. Any other
    error line is one defect.
    """
    for line in self._getLineList(report):
      if self._getRole(line) != 'error':
        continue
      content = json.loads(line.getTextContent())['content']
      self.assertIn(
        'connector', content,
        'the report holds one error that is not about the connector: %s'
        % (content[:400], ))

  def _buildLlmRequestFixture(self, suffix, question='a question',
                              tool_list=None, model=None):
    """Build one report that holds one user line and one llm_request line.

    The report holds one Artificial Task. The Artificial Task holds the
    connector and the model. Every test of background mode needs this shape.

    The fixture builds the shape of production. The Artificial Task holds one
    Artificial Task Line with the question. The production script
    `ArtificialTask_buildRequestLine` then writes the `user` line, the link
    `causality` and the `llm_request` line. The request line stays in the
    state `draft`.
    """
    if tool_list is None:
      tool_list = [READ_ONLY_TOOL_ID]
    report = self._getReport(suffix)
    artificial_task = self._newArtificialTaskForReport(
      report, 'Workflow send %s test' % (suffix, ),
      tool_list=tool_list, with_connector=True)
    # The writer of the send parameters copies these values to the line.
    if model is not None:
      artificial_task.edit(model=model)
    # The same two calls as `ArtificialTask_createCommentLine`.
    artificial_task.newContent(
      portal_type='Artificial Task Line', text_content=question).stop()
    self.commit()
    self.tic()
    # The build path of production. This fixture starts no line.
    result = artificial_task.ArtificialTask_buildRequestLine(report=report)
    request_line = result[1]
    self.commit()
    self.tic()
    # `beforeTearDown` closes this line whatever the test does. See
    # `afterSetUp`.
    self._started_line_list.append(request_line)
    return report, artificial_task, request_line

  def _assertRunDidNotFail(self, status):
    """Fail the current method when the status names one failed run.

    Call this helper BEFORE the assertion on `status['done']`. One failed
    run also ends, so `done` is true for one failed run.
    """
    if status.get('failed'):
      self.fail(
        'the run failed: %s'
        % (status.get('failure_text') or status.get('content') or '', ))

  def _assertNoForeignStartedLine(self):
    """Fail when one started line of another run waits at the provider.

    `afterSetUp` calls this method before every test. The Alarm reads every
    Artificial Task Report Line of the instance that is in the state
    `started`. A line of another run that is older than
    MAXIMUM_REQUEST_DURATION_SECOND then reaches the cancel path of the check
    script, and that run ends with one error line. The real request at the
    provider is lost, and the provider billed that request.

    One line that holds no `destination_reference` is safe. The Alarm skips
    that line.
    """
    own_path_list = [x.getPath() for x in self._started_line_list]
    foreign_path_list = []
    for brain in self.portal.portal_catalog(
        portal_type=PORTAL_TYPE, simulation_state='started'):
      if brain.getPath() in own_path_list:
        continue
      if brain.getObject().getDestinationReference():
        foreign_path_list.append(brain.getPath())
    self.assertEqual(
      [], foreign_path_list,
      'One started line of another run waits at the provider. This test '
      'calls the Alarm, and the Alarm can end that run. Wait for that run, '
      'or close the line by hand. The lines are: %s'
      % (foreign_path_list, ))

  def _countRetrieveCall(self, response_id):
    """Return the count of reads of one response identifier.

    The stub of `retrieveResponse` logs every read. The Alarm of the
    instance can read one line of another run inside the same `tic()`. A
    test must therefore count the reads of its own identifier, not the
    length of the whole log.
    """
    return len([x for x in self._retrieve_call_log if x[0] == response_id])

  def _countCancelCall(self, response_id):
    """Return the count of cancel calls of one response identifier."""
    return len([x for x in self._cancel_call_log if x[0] == response_id])

  def _assertRetrieveCallLogNames(self, response_id):
    """Fail when the stub read one identifier that is not this one.

    `_countRetrieveCall` counts the reads of one identifier. That count
    alone hides one read of one wrong identifier, for example one empty
    identifier. `afterSetUp` proves that no started line of another run
    holds one identifier, so every read of one test must name the line of
    that test.
    """
    self.assertTrue(
      len(self._retrieve_call_log) >= 1,
      'the script read the provider no time')
    self.assertEqual(
      response_id, self._retrieve_call_log[0][0],
      'the first read named the identifier %r'
      % (self._retrieve_call_log[0][0], ))
    other_list = sorted(set(
      [x[0] for x in self._retrieve_call_log if x[0] != response_id]))
    self.assertEqual(
      [], other_list,
      'the script read these other identifiers: %s' % (other_list, ))

  def _closeStartedLine(self, line):
    """Stop one line that still waits, and clear the identifier.

    WARNING: one line in the state `started` that holds one
    `destination_reference` is one line that the Alarm reads on every
    period. A test must leave no such line on the instance.
    """
    if line.getSimulationState() == 'started':
      line.stop()
    line.setDestinationReference('')
    self.commit()

  def _setRequestPath(self, path):
    """Set PATH_INFO of the running request. Return the former value."""
    request = self.portal.REQUEST
    former_path = request.get('PATH_INFO', '')
    request.set('PATH_INFO', path)
    return former_path

  def _registerStartedLineList(self, report):
    """Add every started line of one report to the cleanup list.

    `beforeTearDown` closes every line of `_started_line_list`. One round of
    the agent starts one new line. The test must therefore register the new
    line after every round. A started line that keeps one
    `destination_reference` poisons every later test of the instance.
    """
    known_path_list = [x.getPath() for x in self._started_line_list]
    for line in self._getLineList(report):
      if line.getSimulationState() != 'started':
        continue
      if line.getPath() in known_path_list:
        continue
      self._started_line_list.append(line)

  def _getStartedLineList(self, report):
    """Return every line of one report that is in the state `started`."""
    return [x for x in self._getLineList(report)
            if x.getSimulationState() == 'started']

  def _runAgentRoundListWithTheAlarm(self, artificial_task, report):
    """Call the Alarm by hand until the Artificial Task answers.

    WARNING: no Alarm fires by itself on this instance. A real background
    request therefore stays in the state `started` for ever. The method
    calls the Alarm script by hand, so the test closes its own line.

    The method calls the script on the Alarm object. `Alarm.activeSense`
    calls the method on the Alarm, so `context` is the Alarm. The script
    ends with `context.activate(...)`, and the portal holds no `activate`.

    One round of the agent holds one request and one answer. One tool call
    starts one new request. The method therefore calls the Alarm many times.

    The method registers every new started line before every Alarm call.
    The method returns the status of the Artificial Task.
    """
    alarm = self.portal.portal_alarms[ALARM_ID]
    status = json.loads(artificial_task.ArtificialTask_getAgentStatus())
    for round_index in range(REAL_READ_COUNT):
      if status['done']:
        return status
      self._registerStartedLineList(report)
      alarm.Alarm_checkArtificialTaskReportLineResponse(
        tag=self._buildAlarmTag('real_%s' % (round_index, )),
        fixit=0, params=None)
      self.commit()
      self.tic()
      status = json.loads(artificial_task.ArtificialTask_getAgentStatus())
      if status['done']:
        return status
      time.sleep(REAL_READ_PAUSE_SECOND)
    return status

  def _skipWithoutRealLargeLanguageModel(self):
    """Skip the current method when the real service must not run.

    WARNING: the three methods `test_41` to `test_43` cost money. The three
    methods run only when the module constant REAL_LLM holds the
    value 1.
    """
    if REAL_LLM != 1:
      self.skipTest('set REAL_LLM to 1 to call the real service')
    self._provider_fact_list = []

  def _getRealModel(self):
    """Return the model of production. Fail when no model is known.

    WARNING: background mode lives on the route `/v1/responses` only. One
    reasoning model refuses one function tool on `/v1/chat/completions`, so
    the connector sends that model to `/v1/responses`. A run on another
    model proves the shape of the answer, and proves no route.

    The model does not live on the connector. The connector holds no
    property `model` and no method `getModel`. The connector holds
    `getModelList` only, and that method is one HTTP GET. The model lives on
    the Artificial Task. `ArtificialTaskReportLine_processRequest` reads
    `artificial_task.getModel()`, and the default of that property comes
    from `ArtificialTask_getDefaultModel`.

    WARNING: this method must never answer one literal. A silent fallback
    records one fact of the wrong model.
    """
    model = None
    try:
      model = self.portal.ArtificialTask_getDefaultModel()
    except Exception as model_error:
      self.fail('ArtificialTask_getDefaultModel raised %s. The test cannot '
                'name the model of production.' % (repr(model_error), ))
    if not model:
      self.fail('ArtificialTask_getDefaultModel answered %r. The test must '
                'not guess the model of production.' % (model, ))
    return model

  def _recordProviderFact(self, model, text):
    """Record one fact of the provider. Return the whole recorded text.

    A stub proves the shape of one answer. A stub does not prove the
    behaviour of the provider. The operator records these facts.

    WARNING: every fact names the model. One fact of one model is not one
    fact of another model. The route of the provider follows the model.

    The method writes the fact three times. The error output holds the fact.
    The Zope event log holds the fact, because `runLiveTest` does not send
    the error output to the body of the result. The list
    `_provider_fact_list` holds the fact, and every later assertion of the
    method names that list in its message.
    """
    fact_text = 'PROVIDER FACT [model=%s]: %s' % (model, text)
    self._provider_fact_list.append(fact_text)
    sys.stderr.write('\n%s\n' % (fact_text, ))
    PROVIDER_FACT_LOGGER.info(fact_text)
    return self._getProviderFactText()

  def _getProviderFactText(self):
    """Return every recorded fact of the provider as one text."""
    return ' || '.join(self._provider_fact_list)

  def _waitForRealResponse(self, connector, response_id):
    """Read one real response until the response is done. Return the answer.

    The method reads at most REAL_READ_COUNT times. The method waits
    REAL_READ_PAUSE_SECOND seconds between two reads.
    """
    response = None
    for _ in range(REAL_READ_COUNT):
      response = connector.retrieveResponse(response_id)
      if response['is_done']:
        return response
      time.sleep(REAL_READ_PAUSE_SECOND)
    return response

  def _cancelRealResponseThatRuns(self, connector, response_id):
    """Stop one real response that still runs. Never raise.

    WARNING: the provider bills one background request that nobody stops.
    Call this method in one `finally` block of every method that creates one
    real background request.
    """
    try:
      response = connector.retrieveResponse(response_id)
      if response['is_done']:
        return
      connector.cancelResponse(response_id)
    except Exception:
      # The cleanup must never hide the error of the test.
      pass

  def _getArtificialTaskIdSet(self):
    """Return the identifiers of every document of artificial_task_module.

    A method that proves one delta reads this set before the call and after
    the call. A method must never assert one absolute total.
    """
    return set([x for x in self.portal.artificial_task_module.objectIds()])

  def _getRepresentationScript(self, script_id):
    """Return one skin script by acquisition from the portal.

    The method resolves the script through the skin selection of the
    portal. The script can live in any skin folder of the selection. The
    method skips the current method when no skin folder holds the script.
    This suite installs no skin script. Deploy the script first, then run
    this suite again.

    NOTE: the method does not name one skin folder. One customer Business
    Template can hold the script in its own skin folder.

    WARNING: `getattr` on one skin folder acquires, and `getattr` on one
    skin folder therefore answers one script of another folder. The portal
    root has no such trap. The portal root is the correct route for one
    skin script.
    """
    script = getattr(self.portal, script_id, None)
    if script is None:
      self.fail(
        'the skin script %s is absent from every skin folder of the '
        'portal. Deploy the script, then run this method again. This '
        'suite installs no skin script.' % (script_id, ))
    return script

  def _getConnectorClass(self):
    """Return the class of the connector.

    WARNING: a write of one Document Component resets the dynamic classes.
    Read the class again on every call. Do not keep the class between two
    calls.
    """
    return self.portal.ArtificialTask_getDefaultConnector().__class__

  def _skipWithoutConnectorFileMethodList(self):
    """Skip the current method when the connector holds no file method.

    The new source of the connector adds the file methods.
    """
    connector_class = self._getConnectorClass()
    for method_id in self.CONNECTOR_FILE_METHOD_ID_LIST:
      if self._findInheritedMethod(connector_class, method_id) is None:
        self.fail(
          'the connector holds no method %s. Deploy the new source of '
          'the connector, then run this method again.' % (method_id, ))

  def _patchClassMethodList(self, klass, method_dict):
    """Replace the methods of one class with the given functions.

    WARNING: a patch on one class reaches every user of this Zope process.
    The caller must call `_unpatchClassMethodList` inside one `finally`.
    `beforeTearDown` does not call that method, because this suite must not
    change the methods that the earlier tests wrote.
    """
    if getattr(self, '_extra_patch_list', None) is None:
      self._extra_patch_list = []
    for method_id, function in method_dict.items():
      self._extra_patch_list.append(
        (klass, method_id, klass.__dict__.get(method_id)))
      setattr(klass, method_id, function)

  def _unpatchClassMethodList(self):
    """Write back every method that `_patchClassMethodList` replaced."""
    patch_list = getattr(self, '_extra_patch_list', None) or []
    patch_list.reverse()
    for klass, method_id, original_method in patch_list:
      if original_method is None:
        try:
          delattr(klass, method_id)
        except AttributeError:
          pass
      else:
        setattr(klass, method_id, original_method)
    self._extra_patch_list = []

  def _toUnicodeText(self, value):
    """Return one unicode text for one value of any type.

    WARNING: Python 2 compares one `str` with one `unicode` through the
    codec `ascii`. One byte above 127 then raises UnicodeDecodeError. One
    ERP5 accessor answers UTF-8 bytes, so one message content can hold
    bytes. Every text comparison of the methods below calls this method
    first.
    """
    if value is None:
      return u''
    if isinstance(value, six.text_type):
      return value
    if isinstance(value, str):
      return value.decode('utf-8', 'replace')
    return six.text_type(value)

  def _buildFileIdentifier(self, name):
    """Return one file identifier of this run.

    WARNING: a live test must never use one fixed identifier. The stub of
    the upload answers this value. Every assertion reads this value back.
    """
    return 'file_%s_%s' % (name, self._run_identifier)

  def _setAggregateOrSkip(self, document, value):
    """Write the base category `aggregate` of one document.

    The method skips the current method when the portal type of the
    document holds no base category `aggregate`. A deployment step adds
    that base category.
    """
    absent_text = (
      'the portal type %s holds no base category aggregate. Add that '
      'base category, then run this method again.'
      % (document.getPortalType(), ))
    try:
      document.setAggregateValue(value)
      self.commit()
      written_value = document.getAggregateValue()
    except Exception:
      self.skipTest(absent_text)
    if written_value is None:
      self.skipTest(absent_text)
    self.assertEqual(
      value.getRelativeUrl(), written_value.getRelativeUrl(),
      'the aggregate of %s holds another document'
      % (document.getRelativeUrl(), ))

  def _assertNoPrivateMessageKey(self, message_list, place_text):
    """Fail when one message holds one key that starts with the low line.

    WARNING: a key outside the shape of the provider breaks the request.
    The key `_llm_file` carries the binary, and
    `ArtificialTaskReportLine_processRequest` must remove that key before
    the send.
    """
    private_key_list = []
    for message in (message_list or []):
      if not isinstance(message, dict):
        continue
      for key in message.keys():
        if str(key).startswith('_'):
          private_key_list.append(str(key))
    self.assertEqual(
      [], sorted(set(private_key_list)),
      'the message list of %s holds these private keys: %s'
      % (place_text, sorted(set(private_key_list))))

  def _getOtherRequestLine(self, report, request_line):
    """Return the one `llm_request` line that is not `request_line`."""
    other_list = [
      x for x in self._getLineList(report)
      if self._getRole(x) == 'llm_request' and
      x.getRelativeUrl() != request_line.getRelativeUrl()]
    self.assertEqual(
      1, len(other_list),
      'the round created %s other request lines' % (len(other_list), ))
    return other_list[0]

  def _snapshotTextContent(self, document):
    """Return the present `text_content` of one document, or None."""
    try:
      return document.getTextContent()
    except Exception:
      return None

  def _restoreTextContent(self, document, former_text):
    """Write back the text that `_snapshotTextContent` answered.

    The method never raises. A failure of the restore must not hide the
    error of the test method.
    """
    try:
      document.setTextContent(former_text)
      self.commit()
    except Exception:
      pass

  def _cancelDocumentOfThisRun(self, document):
    """Cancel one document that this method created. Never raise.

    WARNING: this suite must never delete one document of one module. The
    method cancels the document, or the method leaves the document.
    """
    workflow_tool = self.portal.portal_workflow
    for transition_id in self.MAIL_CANCEL_TRANSITION_ID_LIST:
      try:
        workflow_tool.doActionFor(document, transition_id)
        self.commit()
        return
      except Exception:
        continue

  def _getFirstRequestLine(self, report):
    """Return the first line of one report that holds one provider value.

    One request line holds `destination_reference`. That value is the
    identifier of the response at the provider.
    """
    for line in self._getLineList(report):
      if line.getDestinationReference():
        return line
    return None

  def _measureTextCharacterCount(self, report, last_line):
    """Return the character count of every line up to one line.

    The count holds the text of the request line. That text holds the tool
    definitions and the system block. The count holds no binary.
    """
    total = 0
    for line in self._getLineList(report):
      total += len(self._toUnicodeText(line.getTextContent()))
      if line.getPath() == last_line.getPath():
        break
    return total


class TestArtificialTaskBackgroundMode(ArtificialTaskTestMixin):
  """Prove the workflow driven request mechanism."""

  def test_01_theComponentIsLoadedAndTheClassIsRight(self):
    """The portal type uses the class ArtificialTaskReportLine.

    The class must inherit from Event. Before this change the portal type
    used the class TextDocument.
    """
    portal = self.portal
    base_type = portal.portal_types[PORTAL_TYPE]
    self.assertEqual('ArtificialTaskReportLine', base_type.getTypeClass())
    # Strict: one other base category fails this method.
    self.assertEqual(['aggregate', 'connector'],
                     list(base_type.getTypeBaseCategoryList()))
    property_sheet_list = list(base_type.getTypePropertySheetList())
    self.assertIn('ArtificialTask', property_sheet_list)
    self.assertIn('SortIndex', property_sheet_list)

    document_class = self._getPortalTypeClass()
    # NOTE: ERP5 names the generated class after the portal type. The name of
    # the Document Component is one name of the base classes.
    self.assertEqual(PORTAL_TYPE, document_class.__name__)

    base_name_list = [x.__name__ for x in document_class.__mro__]
    self.assertIn('Event', base_name_list)
    self.assertIn('ArtificialTaskReportLine', base_name_list)

    # NOTE: a reload gives another class object. Compare the module name.
    component_class_list = [
      x for x in document_class.__mro__
      if x.__name__ == 'ArtificialTaskReportLine']
    self.assertEqual(1, len(component_class_list))
    component_class = component_class_list[0]
    # The module name holds the version folder, for example
    # `erp5.component.document.erp5_version.ArtificialTaskReportLine`.
    self.assertTrue(
      component_class.__module__.startswith('erp5.component.document.')
      and component_class.__module__.endswith('.ArtificialTaskReportLine'),
      'the base class comes from the module %s'
      % (component_class.__module__, ))

    report = self._getReport('class')
    line = self._newLine(report, 1, {'role': 'user', 'content': 'hello'})
    # NOTE: ERP5 may generate a new portal type class after a commit. Read
    # the base classes of the real instance instead of an isinstance test.
    line_base_name_list = [x.__name__ for x in line.__class__.__mro__]
    self.assertIn('ArtificialTaskReportLine', line_base_name_list)
    self.assertIn('Event', line_base_name_list)
    # NOTE: Movement writes stop_date with start_date. test_13 covers it.
    self.assertIn('Movement', line_base_name_list)
    # The name ArtificialTaskReportLine must come before the name Event.
    self.assertTrue(
      line_base_name_list.index('ArtificialTaskReportLine')
      < line_base_name_list.index('Event'))
    self.assertEqual(PORTAL_TYPE, line.getPortalType())

    # The property sheet ArtificialTask holds request_parameter.
    property_sheet = portal.portal_property_sheets.ArtificialTask
    reference_list = []
    for standard_property in property_sheet.objectValues():
      reference_list.append(standard_property.getReference())
    self.assertIn('request_parameter', reference_list)
    self.assertTrue(hasattr(line, 'getRequestParameter'))
    self.assertTrue(hasattr(line, 'setRequestParameter'))
    self.assertTrue(hasattr(line, 'getIntIndex'))
    self.assertTrue(hasattr(line, 'getConnectorValue'))

    self.abort()

  def test_03_sendIsNotPublishableOverHttp(self):
    """The method send holds no docstring. Zope publishes no such method.

    This version of ERP5 holds no decorator `non_publishable`. The missing
    docstring is the only guard.
    """
    from erp5.component.document.ArtificialTaskReportLine import \
      ArtificialTaskReportLine
    self.assertEqual(None, ArtificialTaskReportLine.send.__doc__)

    document_class = self._getPortalTypeClass()
    self.assertEqual(None, document_class.send.__doc__)

    # The two scripts hold their own guard. test_17 proves the guard.
    self.assertNotEqual(
      None,
      self.portal.portal_skins.erp5_artificial_intelligence
      .ArtificialTaskReportLine_sendRequest.__doc__)

  def test_04_startAndStopReachTheRightState(self):
    """start() must reach `started`. stop() must reach `stopped`.

    Before this change start() raised AttributeError on the name send. The
    portal type used the class TextDocument. TextDocument holds no send.
    """
    report = self._getReport('transition')
    line = report.newContent(portal_type=PORTAL_TYPE, int_index=1)
    self.assertEqual('draft', line.getSimulationState())

    # The line holds no payload. sendRequest returns early and starts no
    # activity. The transition alone is under test here.
    line.start()
    self.assertEqual('started', line.getSimulationState())
    self.assertEqual(0, self._countActivity(line))

    line.stop()
    self.assertEqual('stopped', line.getSimulationState())
    self.abort()

  def test_05_startEnqueuesAndDoesNotCallOut(self):
    """The transition start must only create one activity.

    The transition runs inside the transaction of the caller. A network call
    inside that transaction blocks one Zope thread.
    """
    report = self._getReport('enqueue')
    # The role `note` is not a request role. The activity is therefore cheap.
    line = self._newLine(report, 1, {'role': 'note', 'content': 'x'})
    self.commit()
    self.tic()

    self.assertEqual(0, self._countActivity(line))

    start_time = time.time()
    line.start()
    elapsed = time.time() - start_time

    self.assertEqual('started', line.getSimulationState())
    self.assertTrue(
      elapsed < 5.0,
      'the transition needed %s seconds. A network call is likely.' % (
        elapsed, ))
    # NOTE: the activity tool writes the message on the commit. Commit first,
    # then count. The commit does not run the activity.
    self.commit()
    self.assertEqual(1, self._countActivity(line))
    self.assertEqual([], self._getAnswerLineList(line))
    self.assertEqual(1, len(self._getLineList(report)))

    # The report holds no Artificial Task and the line holds no connector.
    # A synchronous call would therefore have raised already.
    self.assertEqual(None, line.getConnectorValue())

    self.commit()
    self.tic()
    # The role is not a request role. The activity writes no answer.
    self.assertEqual([], self._getAnswerLineList(line))
    self.assertEqual('stopped', line.getSimulationState())

  def test_06_sendRequestIsIdempotent(self):
    """A second call must not start a second activity.

    A second activity pays the Large Language Model a second time.
    """
    report = self._getReport('idempotence')
    request_line = self._newLine(report, 1, {'role': 'llm_request'})
    answer_line = self._newLine(
      report, 2, {'role': 'assistant', 'content': 'the answer'})
    answer_line.setCausalityValue(request_line)
    answer_line.stop()
    self.commit()
    self.tic()

    # The scripts refuse a line that is not started. The transition starts
    # no activity, because the answer already exists.
    request_line.start()
    self.commit()
    self.assertEqual('started', request_line.getSimulationState())
    self.assertEqual(0, self._countActivity(request_line))

    first_result = request_line.ArtificialTaskReportLine_sendRequest()
    self.assertEqual('answer already exists', first_result)
    self.assertEqual(0, self._countActivity(request_line))

    second_result = request_line.ArtificialTaskReportLine_sendRequest()
    self.assertEqual('answer already exists', second_result)
    self.assertEqual(0, self._countActivity(request_line))

    # The activity itself holds the same guard.
    process_result = request_line.ArtificialTaskReportLine_processRequest()
    self.assertEqual('answer already exists', process_result)
    self.assertEqual(2, len(self._getLineList(report)))

    # A `started` line with an answer waits for ever. The script stops it.
    self.commit()
    self.assertEqual('stopped', request_line.getSimulationState())

  def test_08_theMessageListKeepsTheOrderAndDropsTheRequestLines(self):
    """The message list must hold `user`, `assistant` and `tool` only."""
    report = self._getReport('message')
    # Out of order: the script must sort on int_index. Every line is
    # `stopped`, because the script skips an unfinished message.
    self._newLine(report, 3, {'role': 'assistant', 'content': 'answer one',
                              'tool_calls': [
                                self._buildToolCall(
                                  'c1', self.tool_reference)]}).stop()
    self._newLine(report, 1,
                  {'role': 'user', 'content': 'question one'}).stop()
    self._newLine(report, 2, {'role': 'llm_request'})
    self._newLine(report, 5, {'role': 'tool', 'tool_call_id': 'c1',
                              'name': READ_ONLY_TOOL_ID,
                              'content': 'the tool answer'}).stop()
    self._newLine(report, 4, {'role': 'tool_request',
                              'tool_call': self._buildToolCall(
                                'c1', self.tool_reference)})
    self._newLine(report, 6, {'role': 'error', 'content': 'something broke'})
    self._newLine(report, 7,
                  {'role': 'user', 'content': 'question two'}).stop()
    self.commit()
    self.tic()

    message_list = report.ArtificialTaskReport_getMessageList()
    role_list = [x['role'] for x in message_list]
    self.assertEqual(['user', 'assistant', 'tool', 'user'], role_list)

    self.assertEqual('question one', message_list[0]['content'])
    self.assertEqual('answer one', message_list[1]['content'])
    self.assertEqual('c1', message_list[1]['tool_calls'][0]['id'])
    self.assertEqual('c1', message_list[2]['tool_call_id'])
    self.assertEqual(READ_ONLY_TOOL_ID, message_list[2]['name'])
    self.assertEqual('question two', message_list[3]['content'])

  def test_09_aBrokenRequestWritesAnErrorLineAndDoesNotRetry(self):
    """A request without a connector must write one error line.

    The activity must not raise. A raise fails the activity for good
    (`max_retry=0`), and the request line stays `started`.
    """
    report = self._getReport('failure')
    request_line = self._newLine(report, 1, {'role': 'llm_request'})
    self.commit()
    self.tic()
    self.assertEqual(None, request_line.getConnectorValue())

    request_line.start()
    self.commit()
    self.tic()

    answer_line_list = self._getAnswerLineList(request_line)
    self.assertEqual(1, len(answer_line_list))
    error_line = answer_line_list[0]
    self.assertEqual('error', self._getRole(error_line))
    self.assertEqual('stopped', error_line.getSimulationState())
    self.assertIn(
      'connector', json.loads(error_line.getTextContent())['content'])

    self.assertEqual('stopped', request_line.getSimulationState())
    self.assertEqual(0, self._countActivity(request_line))
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_10_aReportPastTheBoundStartsNoRound(self):
    """A report with 20 requests to the model must not send one more.

    The test gives the report 20 finished requests to the Large Language
    Model and one tool request. The test runs the tool request and checks
    that no new request to the model starts. No real model is called.
    """
    report = self._getReport('llm_bound')
    self._newArtificialTaskForReport(
      report, 'Workflow send llm bound test', tool_list=[READ_ONLY_TOOL_ID])
    for int_index in range(1, MAXIMUM_LLM_REQUEST_COUNT + 1):
      line = self._newLine(report, int_index, {'role': 'llm_request'})
      line.stop()
    tool_call = self._buildToolCall('call_test_10', self.tool_reference)
    request_line = self._newLine(
      report, MAXIMUM_LLM_REQUEST_COUNT + 1,
      {'role': 'tool_request', 'tool_call': tool_call})
    self.commit()
    self.tic()

    self.assertEqual(MAXIMUM_LLM_REQUEST_COUNT,
                     self._countRole(report, 'llm_request'))

    request_line.start()
    self.commit()
    self.tic()

    self.assertEqual(1, len(self._getAnswerLineList(request_line)))
    self.assertEqual('tool',
                     self._getRole(self._getAnswerLineList(request_line)[0]))
    self.assertEqual(
      MAXIMUM_LLM_REQUEST_COUNT, self._countRole(report, 'llm_request'),
      'the script started one more round after the bound')
    self.assertEqual(MAXIMUM_LLM_REQUEST_COUNT + 2,
                     len(self._getLineList(report)))
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_11_aReportAtTheToolBoundStartsNoToolRequest(self):
    """A report with 8 tool requests must not start a ninth one.

    The test gives the report one user message, 8 finished tool requests
    and one request to the model. A fake answer of the model asks for one
    more tool. The test checks that no new tool request starts and that the
    task ends with the message about the limit of 8 tool requests.
    """
    report = self._getReport('tool_turn_bound')
    artificial_task = self._newArtificialTaskForReport(
      report, 'Workflow send tool turn bound test',
      tool_list=[READ_ONLY_TOOL_ID], with_connector=True)
    self._newLine(report, 1,
                  {'role': 'user', 'content': 'find everything'}).stop()
    for int_index in range(2, MAXIMUM_TOOL_REQUEST_COUNT + 2):
      tool_call = self._buildToolCall(
        'call_turn_%s' % (int_index, ), self.tool_reference)
      self._newLine(report, int_index,
                    {'role': 'tool_request', 'tool_call': tool_call}).stop()
    request_line = self._newLine(
      report, MAXIMUM_TOOL_REQUEST_COUNT + 2, {'role': 'llm_request'})
    self.commit()
    self.tic()

    _, call_log = self._patchConnectorResponses([
      {'content': '',
       'tool_calls': [self._buildToolCall('call_turn_over',
                                          self.tool_reference)],
       'usage': {}},
    ])
    try:
      request_line.start()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual(1, len(call_log))
    self.assertEqual(
      MAXIMUM_TOOL_REQUEST_COUNT, self._countRole(report, 'tool_request'),
      'the script started one tool request above the bound')
    self.assertEqual(0, self._countRole(report, 'tool'))
    assistant_line_list = [x for x in self._getLineList(report)
                           if self._getRole(x) == 'assistant']
    self.assertEqual(1, len(assistant_line_list))
    self.assertNotIn(
      'tool_calls', json.loads(assistant_line_list[0].getTextContent()))
    self.assertEqual('stopped', request_line.getSimulationState())

    artificial_task_line_list = list(artificial_task.objectValues(
      portal_type='Artificial Task Line'))
    self.assertEqual(1, len(artificial_task_line_list))
    self.assertIn('%s tool requests' % (MAXIMUM_TOOL_REQUEST_COUNT, ),
                  artificial_task_line_list[0].getTextContent())
    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_12_theToolRequestBoundStopsTheRun(self):
    """A round that asks for more tool calls than the bound must stop.

    The stub of the connector answers nine tool calls. The bound is eight.
    """
    portal = self.portal
    report = self._getReport('tool_bound')
    artificial_task = self._newArtificialTask('Workflow send tool bound test')
    artificial_task.edit(
      connector_value=portal.ArtificialTask_getDefaultConnector(),
      model='gpt-4.1')
    artificial_task.plan()
    artificial_task.start()
    report.edit(follow_up_value=artificial_task)

    self._newLine(report, 1,
                  {'role': 'user', 'content': 'find everything'}).stop()
    request_line = self._newLine(report, 2, {'role': 'llm_request'})
    self.commit()
    self.tic()

    tool_call_list = [
      self._buildToolCall('call_bound_%s' % (x, ), self.tool_reference)
      for x in range(MAXIMUM_TOOL_REQUEST_COUNT + 1)]
    _, call_log = self._patchConnectorResponses([
      {'content': '', 'tool_calls': tool_call_list, 'usage': {}},
    ])
    try:
      request_line.start()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual(1, len(call_log))
    self.assertEqual(
      0, self._countRole(report, 'tool_request'),
      'the script started tool requests above the bound')
    self.assertEqual(1, self._countRole(report, 'assistant'))
    self.assertEqual('stopped', request_line.getSimulationState())

    # The assistant line must hold no key `tool_calls`. A `tool_calls` key
    # with no answer makes the next round fail with the HTTP status 400.
    assistant_line_list = [x for x in self._getLineList(report)
                           if self._getRole(x) == 'assistant']
    assistant_payload = json.loads(assistant_line_list[0].getTextContent())
    self.assertNotIn(
      'tool_calls', assistant_payload,
      'the assistant line holds tool_calls with no answer')

    artificial_task_line_list = list(artificial_task.objectValues(
      portal_type='Artificial Task Line'))
    self.assertEqual(1, len(artificial_task_line_list))
    self.assertIn('%s tool requests' % (MAXIMUM_TOOL_REQUEST_COUNT, ),
                  artificial_task_line_list[0].getTextContent())
    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_13_settingTheStartDateAlsoSetsTheStopDate(self):
    """Check the claim of the implementer about the two dates.

    The class Event inherits from Movement. Movement writes stop_date when
    the caller writes start_date and stop_date is empty.
    """
    report = self._getReport('date')
    line = report.newContent(portal_type=PORTAL_TYPE, int_index=1)
    self.assertEqual(None, line.getStartDate())
    self.assertEqual(None, line.getStopDate())

    from DateTime import DateTime
    reference_date = DateTime('2026/01/02 03:04:05 UTC')
    line.edit(start_date=reference_date)

    self.assertEqual(reference_date, line.getStartDate())
    # Movement also writes stop_date.
    self.claim_stop_date_is_written = line.getStopDate() is not None
    self.assertNotEqual(
      None, line.getStopDate(),
      'the claim of the implementer is wrong: stop_date stayed empty')
    self.assertEqual(reference_date, line.getStopDate())
    self.abort()

  def test_14_theAnswerOfTheTaskIsMirroredBackAsAUserMessage(self):
    """Check the claim of the implementer about ArtificialTask_getCommentPostList.

    That script marks a post as an answer only when the Artificial Task Line
    is in the state `delivered`. The workflow of the Artificial Task Line is
    `event_simulation_workflow`. Check whether that workflow holds a state
    `delivered`.
    """
    portal = self.portal
    workflow = portal.portal_workflow.event_simulation_workflow
    state_id_list = [str(x) for x in workflow.objectIds()
                     if str(x).startswith('state_')]
    self.assertNotIn(
      'state_delivered', state_id_list,
      'the workflow holds a state delivered. The claim is wrong.')

    artificial_task = self._newArtificialTask('Workflow send mirror test')
    # WARNING: the task holds the real connector. The stub replaces it before
    # the last tic().
    question_line = artificial_task.newContent(
      portal_type='Artificial Task Line', text_content='Question one')
    question_line.stop()
    self.commit()
    self.tic()

    # The script ArtificialTaskReportLine_processRequest writes the answer of
    # one run in this shape. Build the same shape here.
    answer_line = artificial_task.newContent(
      portal_type='Artificial Task Line', text_content='Answer one')
    answer_line.stop()
    self.commit()
    self.tic()

    post_list = artificial_task.ArtificialTask_getCommentPostList()
    self.assertEqual(2, len(post_list))
    self.assertEqual('Question one', post_list[0]['text'])
    self.assertEqual('Answer one', post_list[1]['text'])
    # The defect: the answer of the agent is not marked as an answer.
    self.assertEqual(
      False, post_list[1]['response'],
      'the claim is wrong: the script already marks the answer')

    message_list = artificial_task.ArtificialTask_getMessageList()
    self.assertEqual(['user', 'user'], [x['role'] for x in message_list],
                     'the claim is wrong: the answer carries the role '
                     'assistant')

    # WARNING: arm the stub before `ArtificialTask_startAgent`. Another
    # activity node can take the send message and pay the provider.
    _, call_log = self._patchConnectorResponses([
      {'content': 'stub answer', 'tool_calls': [], 'usage': {}},
    ])
    try:
      artificial_task.plan()
      artificial_task.start()
      self.assertEqual('processing', artificial_task.getSimulationState())
      report_relative_url = artificial_task.ArtificialTask_startAgent()
      report = portal.restrictedTraverse(report_relative_url)

      user_content_list = [
        json.loads(x.getTextContent())['content']
        for x in self._getLineList(report) if self._getRole(x) == 'user']
      self.assertIn(
        'Answer one', user_content_list,
        'the claim is wrong: the answer of the agent did not come back as a '
        'user message')
      self.assertEqual(
        0, self._countRole(report, 'assistant'),
        'the report holds an assistant line. The claim is wrong.')

      # Drain the activity of the started llm_request line. The stub
      # answers. No real service runs here.
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()
    self.assertEqual(1, len(call_log))
    self.assertEqual(0, self._countRole(report, 'error'))
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_15_theAdminHelperScriptsAreAbsent(self):
    """No helper script of the implementer must stay in portal_skins/custom.

    A script in the folder portal_skins/custom is reachable over HTTP. A
    proxy role Manager on such a script raises the rights of an anonymous
    caller. The 13 scripts of ADMIN_SCRIPT_ID_LIST carried that proxy role.
    This method guards against a new deploy of the same scripts.
    """
    custom_folder = self.portal.portal_skins.custom
    present_script_id_list = []
    manager_script_id_list = []
    for script_id in ADMIN_SCRIPT_ID_LIST:
      script = custom_folder.get(script_id, None)
      if script is None:
        continue
      present_script_id_list.append(script_id)
      if 'Manager' in list(getattr(script, '_proxy_roles', ()) or ()):
        manager_script_id_list.append(script_id)
    self.assertEqual(
      [], present_script_id_list,
      'these helper scripts came back into portal_skins/custom: %s'
      % (present_script_id_list, ))
    self.assertEqual([], manager_script_id_list)

  def test_17_theRequestScriptsRefuseAWebRequest(self):
    """A GET on either script must not run the body of that script.

    WARNING: a GET on <line>/ArtificialTaskReportLine_processRequest answered
    the HTTP status 200 and ran the body. A GET on
    <line>/ArtificialTaskReportLine_sendRequest answered the HTTP status 200
    and started one activity. Both calls bypassed the workflow, the permission
    `AccessContentsInformation` and the serialization tag.

    Each script holds two guards. The second guard reads the simulation
    state of the line, and is the same in both scripts.

    The first guard is not the same in the two scripts.
    `ArtificialTaskReportLine_sendRequest` reads PATH_INFO of the request.
    `ArtificialTaskReportLine_processRequest` raises `Unauthorized` when the
    caller passes `REQUEST`. Zope passes `REQUEST` to every published
    script. One activity passes no `REQUEST`. The method test_38 proves the
    same guard on `ArtificialTaskReportLine_checkResponse`.
    """
    report = self._getReport('web_request')
    self._newArtificialTaskForReport(
      report, 'Workflow send web request test',
      tool_list=[READ_ONLY_TOOL_ID])
    tool_call = self._buildToolCall('call_test_17', self.tool_reference)
    request_line = self._newLine(
      report, 1, {'role': 'tool_request', 'tool_call': tool_call})
    self.commit()
    self.tic()

    # Guard 2 alone: the line is in the state draft.
    self.assertEqual('draft', request_line.getSimulationState())
    self.assertEqual(
      'refused: the line is not started',
      request_line.ArtificialTaskReportLine_processRequest())
    self.assertEqual(
      'refused: the line is not started',
      request_line.ArtificialTaskReportLine_sendRequest())
    self.assertEqual(1, len(self._getLineList(report)))
    self.assertEqual(0, self._countActivity(request_line))

    # Guard 1 alone: the line is started and the path of the request names
    # the script. This is the shape of a GET over HTTP.
    request_line.start()
    self.commit()
    self.assertEqual('started', request_line.getSimulationState())

    # Guard 1 of the request script: the caller passes REQUEST. Zope passes
    # REQUEST to every published script. The script raises Unauthorized.
    self.assertRaises(
      Unauthorized, request_line.ArtificialTaskReportLine_processRequest,
      REQUEST=self.portal.REQUEST)

    former_path = self._setRequestPath(
      '/%s/%s/%s' % (self.portal.getId(), request_line.getRelativeUrl(),
                     SEND_METHOD_ID))
    try:
      self.assertEqual(
        'refused: this script is not a web page',
        request_line.ArtificialTaskReportLine_sendRequest())
    finally:
      self._setRequestPath(former_path)

    # WARNING: one trailing solidus defeats a guard that compares the end of
    # the path. The guard compares every segment of the path instead.
    for path_suffix in ('/', '//'):
      former_path = self._setRequestPath(
        '/%s/%s/%s%s' % (self.portal.getId(),
                         request_line.getRelativeUrl(),
                         SEND_METHOD_ID, path_suffix))
      try:
        self.assertEqual(
          'refused: this script is not a web page',
          request_line.ArtificialTaskReportLine_sendRequest(),
          'the path %s defeated the guard' % (path_suffix, ))
      finally:
        self._setRequestPath(former_path)

    # No guard wrote a line.
    self.assertEqual(1, len(self._getLineList(report)))

    # Drain the activity that the transition start created.
    self.commit()
    self.tic()
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_18_aToolOutsideTheToolListDoesNotRun(self):
    """A tool name that is not in tool_list must not run.

    WARNING: the earlier script called
    getattr(portal.portal_callables, tool_name)(**argument_dict). The name
    came from the model. No allow list existed. The callable
    ERP5Site_createOrganisation writes one Organisation.
    """
    report = self._getReport('allow_list')
    self._newArtificialTaskForReport(
      report, 'Workflow send allow list test',
      tool_list=[READ_ONLY_TOOL_ID])

    organisation_id_list_before = self._getOrganisationIdList()

    tool_call = self._buildToolCall(
      'call_test_18', None, tool_name=WRITE_TOOL_ID,
      argument_dict={
        'title': 'Zzzworkflowsend Forbidden Organisation %s'
                 % (self._run_identifier, ),
        'reference': 'ZZZWORKFLOWSENDFORBIDDEN%s' % (self._run_identifier, ),
        'dry_run': False})
    request_line = self._newLine(
      report, 1, {'role': 'tool_request', 'tool_call': tool_call})
    self.commit()
    self.tic()

    request_line.start()
    self.commit()
    self.tic()

    content = self._getToolAnswerContent(request_line)
    self.assertIn('is not in the tool list', content)
    self.assertEqual(
      organisation_id_list_before, self._getOrganisationIdList(),
      'the refused tool created one Organisation')
    # The refusal completes the round, and the next round fails on the
    # missing connector. That error is not a defect of the allow list.
    self._assertOnlyConnectorError(report)
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_19_aToolThatOnlyAcquisitionResolvesDoesNotRun(self):
    """A name that getattr resolves through acquisition must be refused.

    WARNING: portal_callables is one folder in one acquisition wrapper.
    getattr(portal.portal_callables, 'Base_edit') returns one skin script. The
    allow list therefore compares the name with the own identifiers of
    portal_callables. The allow list must refuse the name even when tool_list
    holds that name.
    """
    report = self._getReport('acquisition')
    # The tool list holds the name. Only the check on the own identifiers
    # of portal_callables can refuse the name now.
    self._newArtificialTaskForReport(
      report, 'Workflow send acquisition test',
      tool_list=[ACQUIRED_ONLY_TOOL_ID])

    # Prove the premise: getattr resolves the name, and the name is not one
    # own identifier of portal_callables.
    callable_tool = self.portal.portal_callables
    self.assertNotIn(ACQUIRED_ONLY_TOOL_ID, list(callable_tool.objectIds()))
    self.assertNotEqual(
      None, getattr(callable_tool, ACQUIRED_ONLY_TOOL_ID, None),
      'the premise is wrong: getattr does not acquire')

    tool_call = self._buildToolCall(
      'call_test_19', None, tool_name=ACQUIRED_ONLY_TOOL_ID,
      argument_dict={})
    request_line = self._newLine(
      report, 1, {'role': 'tool_request', 'tool_call': tool_call})
    self.commit()
    self.tic()

    request_line.start()
    self.commit()
    self.tic()

    content = self._getToolAnswerContent(request_line)
    self.assertIn('is not one own object of portal_callables', content)
    self._assertOnlyConnectorError(report)
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_20_aToolNameWithABadCharacterDoesNotRun(self):
    """A tool name outside [A-Za-z0-9_] must be refused."""
    report = self._getReport('bad_name')
    self._newArtificialTaskForReport(
      report, 'Workflow send bad name test',
      tool_list=[READ_ONLY_TOOL_ID])

    request_line = self._newLine(report, 1, {
      'role': 'tool_request',
      'tool_call': self._buildToolCall(
        'call_test_20', None, tool_name='portal_skins/custom/Base_edit',
        argument_dict={})})
    self.commit()
    self.tic()

    request_line.start()
    self.commit()
    self.tic()

    content = self._getToolAnswerContent(request_line)
    self.assertIn('holds one character that is not allowed', content)
    self._assertOnlyConnectorError(report)
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_21_aToolRequestWithNoArtificialTaskDoesNotRun(self):
    """A report with no Artificial Task must run no tool.

    The property tool_list lives on the Artificial Task. With no Artificial
    Task there is no allow list. The script must therefore refuse.
    """
    report = self._getReport('no_task')
    self.assertEqual(
      None, report.getFollowUpValue(portal_type='Artificial Task'))

    organisation_id_list_before = self._getOrganisationIdList()
    request_line = self._newLine(report, 1, {
      'role': 'tool_request',
      'tool_call': self._buildToolCall(
        'call_test_21', None, tool_name=WRITE_TOOL_ID,
        argument_dict={
          'title': 'Zzzworkflowsend No Task Organisation %s'
                   % (self._run_identifier, ),
          'reference': 'ZZZWORKFLOWSENDNOTASK%s' % (self._run_identifier, ),
          'dry_run': False})})
    self.commit()
    self.tic()

    request_line.start()
    self.commit()
    self.tic()

    content = self._getToolAnswerContent(request_line)
    self.assertIn('has no Artificial Task', content)
    self.assertEqual(
      organisation_id_list_before, self._getOrganisationIdList(),
      'the refused tool created one Organisation')
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_22_twoToolCallsInOneRoundBothRunAndStartOneNextRound(self):
    """One round with two tool calls must start exactly one next round."""
    report = self._getReport('two_tools')
    artificial_task = self._newArtificialTaskForReport(
      report, 'Workflow send two tool test', tool_list=[READ_ONLY_TOOL_ID],
      with_connector=True)

    self._newLine(report, 1,
                  {'role': 'user', 'content': 'find two things'}).stop()
    request_line = self._newLine(report, 2, {'role': 'llm_request'})
    self.commit()
    self.tic()

    _, call_log = self._patchConnectorResponses([
      {'content': '',
       'tool_calls': [self._buildToolCall('call_two_a', self.tool_reference),
                      self._buildToolCall('call_two_b', self.tool_reference)],
       'usage': {}},
      {'content': 'Both tools answered.', 'tool_calls': [], 'usage': {}},
    ])
    try:
      request_line.start()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual(2, len(call_log),
                     'the stub answered %s calls' % (len(call_log), ))
    self.assertEqual(2, self._countRole(report, 'tool_request'))
    self.assertEqual(2, self._countRole(report, 'tool'))
    # Exactly one next round. Two rounds would pay the service twice.
    self.assertEqual(2, self._countRole(report, 'llm_request'))
    self.assertEqual(2, self._countRole(report, 'assistant'))
    self.assertEqual(0, self._countRole(report, 'error'))

    # The second call must carry both tool answers.
    second_role_list = [x['role'] for x in call_log[1]['messages']
                        if x['role'] != 'system']
    self.assertEqual(['user', 'assistant', 'tool', 'tool'], second_role_list)

    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_23_textThatIsNotAsciiDoesNotRaise(self):
    """A character outside ASCII must not make the activity raise.

    WARNING: str(exception) raises UnicodeEncodeError when the message of
    the exception holds a character outside ASCII. The script uses the
    helper safeText instead.

    The method covers three places: the name of one tool, the argument of
    one tool, and the message of one error.
    """
    report = self._getReport('non_ascii')
    self._newArtificialTaskForReport(
      report, 'Workflow send non ascii test', tool_list=[READ_ONLY_TOOL_ID])

    # 1. The name of the tool holds characters outside ASCII. The refusal
    #    text embeds that name.
    bad_name_line = self._newLine(report, 1, {
      'role': 'tool_request',
      'tool_call': self._buildToolCall(
        'call_ascii_1', None, tool_name=NON_ASCII_TEXT, argument_dict={})})
    self.commit()
    self.tic()
    bad_name_line.start()
    self.commit()
    self.tic()
    content = self._getToolAnswerContent(bad_name_line)
    self.assertIn('not allowed', content)
    self._assertOnlyConnectorError(report)
    self.assertEqual([], self._getPermanentlyFailedMessageList())

    # 2. The argument of the tool holds characters outside ASCII. The tool
    #    is read only.
    report_two = self._getReport('non_ascii_argument')
    self._newArtificialTaskForReport(
      report_two, 'Workflow send non ascii argument test',
      tool_list=[READ_ONLY_TOOL_ID])
    argument_line = self._newLine(report_two, 1, {
      'role': 'tool_request',
      'tool_call': self._buildToolCall(
        'call_ascii_2', NON_ASCII_TEXT)})
    self.commit()
    self.tic()
    argument_line.start()
    self.commit()
    self.tic()
    self.assertEqual(1, len(self._getAnswerLineList(argument_line)))
    self.assertEqual('stopped', argument_line.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

    # 3. The message of the error holds characters outside ASCII.
    report_three = self._getReport('non_ascii_error')
    artificial_task = self._newArtificialTaskForReport(
      report_three, 'Workflow send non ascii error test',
      tool_list=[READ_ONLY_TOOL_ID], with_connector=True)
    self._newLine(report_three, 1,
                  {'role': 'user', 'content': 'question'}).stop()
    error_request_line = self._newLine(report_three, 2, {'role': 'llm_request'})
    self.commit()
    self.tic()

    self._patchConnectorRaise(ValueError(NON_ASCII_TEXT))
    try:
      error_request_line.start()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual(1, self._countRole(report_three, 'error'))
    self.assertEqual('stopped', error_request_line.getSimulationState())
    error_line_list = [x for x in self._getLineList(report_three)
                       if self._getRole(x) == 'error']
    error_content = json.loads(
      error_line_list[0].getTextContent())['content']
    self.assertIn(u'M\xfcller', error_content)

    # WARNING: artificial_task_workflow holds no `cancel` from `processing`.
    # The script ends the run with `respond`.
    workflow = self.portal.portal_workflow.artificial_task_workflow
    self.assertEqual(
      ['transition_respond', 'transition_respond_action'],
      sorted(['%s' % (x, ) for x in
              workflow.state_processing.getDestinationIdList()]),
      'the workflow changed. Read the fallback of failRun again.')
    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_24_aLineThatHoldsNoJsonDoesNotWedgeTheReport(self):
    """One broken sibling line must not stop the run.

    The script ArtificialTaskReport_getMessageList reads every line. A line
    that holds no JSON must be skipped, not raise.
    """
    report = self._getReport('broken_json')
    artificial_task = self._newArtificialTaskForReport(
      report, 'Workflow send broken json test',
      tool_list=[READ_ONLY_TOOL_ID], with_connector=True)

    self._newLine(report, 1,
                  {'role': 'user', 'content': 'question'}).stop()
    broken_line = report.newContent(
      portal_type=PORTAL_TYPE, int_index=2,
      text_content='this line holds no JSON at all')
    broken_line.stop()
    request_line = self._newLine(report, 3, {'role': 'llm_request'})
    self.commit()
    self.tic()

    # The message list must skip the broken line and must not raise.
    message_list = report.ArtificialTaskReport_getMessageList()
    self.assertEqual(['user'],
                     [x['role'] for x in message_list if x['role'] != 'system'])

    _, call_log = self._patchConnectorResponses([
      {'content': 'the answer', 'tool_calls': [], 'usage': {}},
    ])
    try:
      request_line.start()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual(1, len(call_log))
    self.assertEqual(0, self._countRole(report, 'error'))
    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

    # The status script must not raise on the broken line either.
    status = json.loads(artificial_task.ArtificialTask_getAgentStatus())
    self.assertEqual(True, status['done'])

  def test_25_exactlyEightToolCallsAreAccepted(self):
    """Eight tool calls in one round must run. Nine must not.

    The method test_12 proves the refusal of nine tool calls. This method
    proves that eight tool calls run.
    """
    report = self._getReport('eight_tools')
    artificial_task = self._newArtificialTaskForReport(
      report, 'Workflow send eight tool test', tool_list=[READ_ONLY_TOOL_ID],
      with_connector=True)

    self._newLine(report, 1,
                  {'role': 'user', 'content': 'find eight things'}).stop()
    request_line = self._newLine(report, 2, {'role': 'llm_request'})
    self.commit()
    self.tic()

    tool_call_list = [
      self._buildToolCall('call_eight_%s' % (x, ), self.tool_reference)
      for x in range(MAXIMUM_TOOL_REQUEST_COUNT)]
    _, call_log = self._patchConnectorResponses([
      {'content': '', 'tool_calls': tool_call_list, 'usage': {}},
      {'content': 'Eight tools answered.', 'tool_calls': [], 'usage': {}},
    ])
    try:
      request_line.start()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual(
      MAXIMUM_TOOL_REQUEST_COUNT, self._countRole(report, 'tool_request'),
      'the script refused eight tool calls')
    self.assertEqual(MAXIMUM_TOOL_REQUEST_COUNT,
                     self._countRole(report, 'tool'))
    self.assertEqual(2, len(call_log))
    self.assertEqual(0, self._countRole(report, 'error'))

    # The assistant line must keep its tool_calls, because the bound holds.
    assistant_line_list = [x for x in self._getLineList(report)
                           if self._getRole(x) == 'assistant']
    first_payload = json.loads(assistant_line_list[0].getTextContent())
    self.assertEqual(MAXIMUM_TOOL_REQUEST_COUNT,
                     len(first_payload['tool_calls']))
    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_26_exactlyTwentyRoundsAreAccepted(self):
    """Nineteen earlier rounds must allow one more round.

    The method test_10 proves the refusal of round 21. This method proves
    that round 20 runs.
    """
    report = self._getReport('twenty_rounds')
    self._newArtificialTaskForReport(
      report, 'Workflow send twenty round test',
      tool_list=[READ_ONLY_TOOL_ID])

    for int_index in range(1, MAXIMUM_LLM_REQUEST_COUNT):
      line = self._newLine(report, int_index, {'role': 'llm_request'})
      line.stop()
    self.assertEqual(MAXIMUM_LLM_REQUEST_COUNT - 1,
                     self._countRole(report, 'llm_request'))

    tool_call = self._buildToolCall('call_test_26', self.tool_reference)
    request_line = self._newLine(
      report, MAXIMUM_LLM_REQUEST_COUNT,
      {'role': 'tool_request', 'tool_call': tool_call})
    self.commit()
    self.tic()

    request_line.start()
    self.commit()
    self.tic()

    self.assertEqual(
      MAXIMUM_LLM_REQUEST_COUNT, self._countRole(report, 'llm_request'),
      'the script refused round %s' % (MAXIMUM_LLM_REQUEST_COUNT, ))
    self._assertOnlyConnectorError(report)
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_27_theBoundCountsTheCurrentTurnOnly(self):
    """A bound must count the lines of the current turn only.

    WARNING: the earlier script counted every line of the report. Turn two
    therefore inherited the budget of turn one. One turn starts after the
    newest line whose role is `user`.
    """
    report = self._getReport('per_turn')
    self._newArtificialTaskForReport(
      report, 'Workflow send per turn test', tool_list=[READ_ONLY_TOOL_ID])

    # Turn one holds the whole budget of the requests to the service.
    int_index = 0
    for _ in range(MAXIMUM_LLM_REQUEST_COUNT):
      int_index += 1
      line = self._newLine(report, int_index, {'role': 'llm_request'})
      line.stop()
    # Turn two starts here.
    int_index += 1
    self._newLine(report, int_index, {'role': 'user',
                                      'content': 'a new question'}).stop()
    int_index += 1
    tool_call = self._buildToolCall('call_test_27', self.tool_reference)
    request_line = self._newLine(
      report, int_index, {'role': 'tool_request', 'tool_call': tool_call})
    self.commit()
    self.tic()

    request_line.start()
    self.commit()
    self.tic()

    self.assertEqual(
      MAXIMUM_LLM_REQUEST_COUNT + 1, self._countRole(report, 'llm_request'),
      'the bound counted the lines of turn one')
    self._assertOnlyConnectorError(report)
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_28_aSecondStartAgentDoesNotForkTheConversation(self):
    """A second call of ArtificialTask_startAgent must create no line.

    Two open requests fork the conversation and pay the service twice.
    """
    portal = self.portal
    report = self._getReport('second_start')
    artificial_task = self._newArtificialTask('Workflow send second start')
    artificial_task.edit(
      connector_value=portal.ArtificialTask_getDefaultConnector(),
      model='gpt-4.1')
    # WARNING: `ArtificialTask_startAgent` reads the catalog. Index the link
    # first, or the second call creates a second report.
    report.edit(follow_up_value=artificial_task)
    question_line = artificial_task.newContent(
      portal_type='Artificial Task Line', text_content='Question one')
    question_line.stop()
    self.commit()
    self.tic()
    self.assertEqual(
      report.getRelativeUrl(),
      artificial_task.getFollowUpRelatedValue(
        portal_type='Artificial Task Report').getRelativeUrl())

    # WARNING: arm the stub before the first `ArtificialTask_startAgent`.
    # Another activity node can take the send message and pay the provider.
    _, call_log = self._patchConnectorResponses([
      {'content': 'stub answer', 'tool_calls': [], 'usage': {}},
    ])
    try:
      report_relative_url = artificial_task.ArtificialTask_startAgent()
      self.assertEqual(report.getRelativeUrl(), report_relative_url)
      line_count_after_first = len(self._getLineList(report))
      self.assertEqual(1, self._countRole(report, 'llm_request'))

      # The llm_request line is open. A second start must change nothing.
      second_relative_url = artificial_task.ArtificialTask_startAgent()
      self.assertEqual(report_relative_url, second_relative_url)
      self.assertEqual(
        line_count_after_first, len(self._getLineList(report)),
        'the second start created one more line')
      self.assertEqual(
        1, self._countRole(report, 'llm_request'),
        'the second start forked the conversation')

      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()
    self.assertEqual(1, len(call_log),
                     'the service was called %s times' % (len(call_log), ))
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_29_aBackgroundStartAnswersQueuedAndHoldsTheIdentifier(self):
    """A background start must write the identifier and hold the state.

    Background mode is the default. `createResponse` answers at once with
    the status `queued`. The line then holds the identifier of the response
    in `destination_reference`. The line stays in the state `started`. No
    answer line exists yet.
    """
    response_identifier = self._buildProviderIdentifier('29')
    report, artificial_task, request_line = self._buildLlmRequestFixture(
      'background_start')

    _, call_log = self._patchConnectorResponses([
      {'id': response_identifier, 'status': 'queued'},
    ])
    try:
      request_line.start()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual(
      1, len(call_log),
      'createResponse ran %s times' % (len(call_log), ))
    # The line holds no value for is_background_enabled. The default of the
    # property is true.
    self.assertEqual(True, call_log[0]['background'])
    self.assertEqual(
      response_identifier, request_line.getDestinationReference())
    self.assertEqual('started', request_line.getSimulationState())
    self.assertEqual([], self._getAnswerLineList(request_line))
    self.assertEqual(2, len(self._getLineList(report)))
    self.assertEqual(0, self._countRole(report, 'error'))
    # The run is not finished. The Artificial Task must not answer yet.
    self.assertEqual('processing', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

    self._closeStartedLine(request_line)

  def test_30_checkResponseAnswersPendingAndWritesNothing(self):
    """checkResponse must write nothing while the provider still runs.

    The provider answers the status `in_progress`. The script reads that
    status and answers the text `pending`. The script must create no line,
    must not stop the request line, and must not call `createResponse` a
    second time.
    """
    response_identifier = self._buildProviderIdentifier('30')
    report, artificial_task, request_line = self._buildLlmRequestFixture(
      'background_pending')

    _, call_log = self._patchConnectorResponses(
      [{'id': response_identifier, 'status': 'queued'}],
      retrieve_response_dict={
        response_identifier: self._buildResponse(
          id=response_identifier, status='in_progress'),
      })
    try:
      request_line.start()
      self.commit()
      self.tic()
      self.assertEqual(
        response_identifier, request_line.getDestinationReference())
      line_count_before = len(self._getLineList(report))

      result = request_line.ArtificialTaskReportLine_checkResponse()
      self.commit()
    finally:
      self._unpatchConnector()

    self.assertEqual('pending', result)
    # The Alarm of the instance can read one line of another run inside the
    # same `tic()`. Count the reads of this line only.
    self.assertEqual(1, self._countRetrieveCall(response_identifier))
    self._assertRetrieveCallLogNames(response_identifier)
    self.assertEqual(
      1, len(call_log),
      'createResponse ran %s times' % (len(call_log), ))
    self.assertEqual(line_count_before, len(self._getLineList(report)))
    self.assertEqual([], self._getAnswerLineList(request_line))
    self.assertEqual('started', request_line.getSimulationState())
    self.assertEqual('processing', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

    self._closeStartedLine(request_line)

  def test_31_checkResponseRecordsTheAnswerWhenTheProviderIsDone(self):
    """checkResponse must record the answer of one completed response.

    The method calls `checkResponse` of the Document Component, not the
    skin script. The two must reach the same result.
    """
    response_identifier = self._buildProviderIdentifier('31')
    report, artificial_task, request_line = self._buildLlmRequestFixture(
      'background_done')

    _, call_log = self._patchConnectorResponses(
      [{'id': response_identifier, 'status': 'queued'}],
      retrieve_response_dict={
        response_identifier: self._buildResponse(
          id=response_identifier, status='completed',
          content='The provider answered.',
          usage={'prompt_tokens': 11, 'completion_tokens': 4,
                 'total_tokens': 15, 'cached_tokens': 0}),
      })
    try:
      request_line.start()
      self.commit()
      self.tic()
      result = request_line.checkResponse()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual('run finished', result)
    self.assertEqual(
      1, len(call_log),
      'createResponse ran %s times' % (len(call_log), ))
    self.assertEqual(1, self._countRetrieveCall(response_identifier))
    self._assertRetrieveCallLogNames(response_identifier)

    answer_line_list = self._getAnswerLineList(request_line)
    self.assertEqual(
      1, len(answer_line_list),
      'the request produced %s answer lines' % (len(answer_line_list), ))
    answer_line = answer_line_list[0]
    self.assertEqual('assistant', self._getRole(answer_line))
    self.assertEqual(request_line.getRelativeUrl(), answer_line.getCausality())
    self.assertEqual(
      'The provider answered.',
      json.loads(answer_line.getTextContent())['content'])
    # The Artificial Task Report Line is one Movement. The token count of
    # the response lives in `quantity`.
    self.assertEqual(15, answer_line.getQuantity())
    # The unit of that count is one token. The value names the category
    # `quantity_unit/unit/token`.
    self.assertEqual(
      'unit/token', answer_line.getQuantityUnit(),
      'the answer line holds the quantity unit %s'
      % (answer_line.getQuantityUnit(), ))

    self.assertEqual('stopped', request_line.getSimulationState())
    self.assertEqual('stopped', answer_line.getSimulationState())
    self.assertEqual(0, self._countRole(report, 'error'))
    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_32_processRequestNeverCreatesASecondResponse(self):
    """A second run of the request script must create no second response.

    A second response pays the service a second time. The script reads
    `destination_reference` first. A line that holds one identifier reaches
    `retrieveResponse`, never `createResponse`.

    The transition `start` is the first call of the request script. The
    direct call below is the second call.
    """
    response_identifier = self._buildProviderIdentifier('32')
    report, _, request_line = self._buildLlmRequestFixture(
      'background_idempotence')

    _, call_log = self._patchConnectorResponses(
      [{'id': response_identifier, 'status': 'queued'}],
      retrieve_response_dict={
        response_identifier: self._buildResponse(
          id=response_identifier, status='in_progress'),
      })
    try:
      request_line.start()
      self.commit()
      self.tic()
      self.assertEqual(
        response_identifier, request_line.getDestinationReference())

      second_result = request_line.ArtificialTaskReportLine_processRequest()
      self.commit()
    finally:
      self._unpatchConnector()

    self.assertEqual('response queued', second_result)
    self.assertEqual(
      1, len(call_log),
      'createResponse ran %s times. The run paid the service twice.'
      % (len(call_log), ))
    self.assertEqual(
      1, self._countRetrieveCall(response_identifier),
      'retrieveResponse ran %s times on this line'
      % (self._countRetrieveCall(response_identifier), ))
    self._assertRetrieveCallLogNames(response_identifier)
    self.assertEqual(
      response_identifier, request_line.getDestinationReference())
    self.assertEqual('started', request_line.getSimulationState())
    self.assertEqual(2, len(self._getLineList(report)))
    self.assertEqual([], self._getPermanentlyFailedMessageList())

    self._closeStartedLine(request_line)

  def test_33_theAlarmFindsAStartedLineAndRecordsTheAnswer(self):
    """The Alarm must find one waiting line and must end the run.

    WARNING: `Alarm_checkArtificialTaskReportLineResponse` reads every
    Artificial Task Report Line of the instance that is in the state
    `started`. The method therefore starts one `checkResponse` activity for
    every such line, not for the line of this test alone. A line that holds
    no `destination_reference` answers at once and calls no network. A line
    that holds one identifier reaches the stub of this method, because the
    stub sits on the connector class.
    """
    response_identifier = self._buildProviderIdentifier('33')
    portal = self.portal
    alarm = portal.portal_alarms.get(ALARM_ID, None)
    self.assertNotEqual(
      None, alarm, 'the Alarm %s does not exist' % (ALARM_ID, ))
    self.assertEqual(ALARM_METHOD_ID, alarm.getActiveSenseMethodId())
    self.assertEqual(1, alarm.getPeriodicityMinuteFrequency())
    self.assertNotEqual(
      None, alarm.getPeriodicityStartDate(),
      'an Alarm with no periodicity_start_date computes no alarm date')
    # An Alarm that is not enabled never runs.
    self.assertTrue(
      alarm.getEnabled(),
      'the Alarm %s is not enabled. No line is ever read.' % (ALARM_ID, ))

    # The Alarm reads every started line. `afterSetUp` proved that no line of
    # another run waits.

    report, artificial_task, request_line = self._buildLlmRequestFixture(
      'background_alarm')

    _, call_log = self._patchConnectorResponses(
      [{'id': response_identifier, 'status': 'queued'}],
      retrieve_response_dict={
        response_identifier: self._buildResponse(
          id=response_identifier, status='completed',
          content='The Alarm recorded this answer.',
          usage={'total_tokens': 21}),
      })
    try:
      request_line.start()
      self.commit()
      self.tic()
      self.assertEqual('started', request_line.getSimulationState())
      self.assertEqual(
        response_identifier, request_line.getDestinationReference())

      # The catalog must hold the line. The Alarm reads the catalog.
      brain_list = portal.portal_catalog(
        portal_type=PORTAL_TYPE, simulation_state='started',
        path=request_line.getPath())
      self.assertEqual(
        1, len(brain_list),
        'the catalog does not hold the waiting line')

      # SQLQueue merges no activity: two Alarm periods give two checks. Call
      # the script on the Alarm, because the script calls `context.activate`.
      alarm.Alarm_checkArtificialTaskReportLineResponse(
        tag=self._buildAlarmTag('first'), fixit=0, params=None)
      alarm.Alarm_checkArtificialTaskReportLineResponse(
        tag=self._buildAlarmTag('second'), fixit=0, params=None)
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual(1, len(call_log))
    answer_line_list = self._getAnswerLineList(request_line)
    self.assertEqual(
      1, len(answer_line_list),
      'the Alarm produced %s answer lines. Two Alarm periods must give one '
      'answer line only.' % (len(answer_line_list), ))
    self.assertEqual('assistant', self._getRole(answer_line_list[0]))
    self.assertEqual(
      'The Alarm recorded this answer.',
      json.loads(answer_line_list[0].getTextContent())['content'])
    self.assertEqual(21, answer_line_list[0].getQuantity())
    self.assertEqual('stopped', request_line.getSimulationState())
    self.assertEqual(0, self._countRole(report, 'error'))
    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_34_aRequestThatWaitsTooLongEndsWithOneCancel(self):
    """One request older than the bound must end with one cancel.

    The provider still answers `in_progress`. The clock is `start_date`.
    `ArtificialTaskReportLine_sendRequest` writes that date.

    The script reads the provider first, then cancels. The read proves that
    the provider holds no answer. A cancel before the read destroys one
    answer that the provider completed and billed. `test_39` proves the
    other side of this rule.
    """
    response_identifier = self._buildProviderIdentifier('34')
    from DateTime import DateTime
    _, artificial_task, request_line = self._buildLlmRequestFixture(
      'background_stuck')

    self._patchConnectorResponses(
      [{'id': response_identifier, 'status': 'queued'}],
      retrieve_response_dict={
        response_identifier: self._buildResponse(
          id=response_identifier, status='in_progress'),
      },
      cancel_response_dict={
        response_identifier: self._buildResponse(
          id=response_identifier, status='cancelled',
          usage={'total_tokens': 8}),
      })
    try:
      request_line.start()
      self.commit()
      self.tic()
      self.assertEqual(
        response_identifier, request_line.getDestinationReference())

      # Move the clock of the line into the past. The age is then above the
      # bound of the stuck rule.
      old_date = DateTime() - (
        (MAXIMUM_REQUEST_DURATION_SECOND + 600) / 86400.0)
      request_line.edit(start_date=old_date)
      self.commit()

      result = request_line.ArtificialTaskReportLine_checkResponse()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual('error', result)
    self.assertEqual(
      1, self._countCancelCall(response_identifier),
      'cancelResponse ran %s times on this line'
      % (self._countCancelCall(response_identifier), ))
    # The script must read the provider before the script cancels. The cancel
    # answers the status `cancelled`, so the script performs no second read.
    self.assertEqual(
      1, self._countRetrieveCall(response_identifier),
      'retrieveResponse ran %s times. The stuck rule must read the provider '
      'one time before the cancel.'
      % (self._countRetrieveCall(response_identifier), ))
    self._assertRetrieveCallLogNames(response_identifier)

    answer_line_list = self._getAnswerLineList(request_line)
    self.assertEqual(1, len(answer_line_list))
    error_line = answer_line_list[0]
    self.assertEqual('error', self._getRole(error_line))
    error_content = json.loads(error_line.getTextContent())['content']
    self.assertIn('cancelled', error_content)
    self.assertIn('%s' % (MAXIMUM_REQUEST_DURATION_SECOND, ), error_content)
    # The provider bills the tokens that it generated before the stop.
    self.assertEqual(8, error_line.getQuantity())

    self.assertEqual('stopped', request_line.getSimulationState())
    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_35_cancelRequestWritesTheTokenCountIntoQuantity(self):
    """cancelRequest must stop the request and must write the token count.

    The Artificial Task Report Line is one Movement. `quantity` is
    therefore the place of the token count. The provider bills the tokens
    of one cancelled request too.
    """
    response_identifier = self._buildProviderIdentifier('35')
    _, artificial_task, request_line = self._buildLlmRequestFixture(
      'background_cancel')

    self._patchConnectorResponses(
      [{'id': response_identifier, 'status': 'queued'}],
      cancel_response_dict={
        response_identifier: self._buildResponse(
          id=response_identifier, status='cancelled',
          usage={'prompt_tokens': 30, 'completion_tokens': 12,
                 'total_tokens': 42, 'cached_tokens': 0}),
      })
    try:
      request_line.start()
      self.commit()
      self.tic()
      self.assertEqual(
        response_identifier, request_line.getDestinationReference())

      result = request_line.cancelRequest(
        comment=u'The user stopped this run.')
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual('error', result)
    self.assertEqual(1, len(self._cancel_call_log))
    self.assertEqual(response_identifier, self._cancel_call_log[0][0])
    # One user cancel reads the provider no time. Count the reads of this
    # line only. The Alarm of the instance can read one other line.
    self.assertEqual(0, self._countRetrieveCall(response_identifier))

    answer_line_list = self._getAnswerLineList(request_line)
    self.assertEqual(1, len(answer_line_list))
    error_line = answer_line_list[0]
    self.assertEqual('error', self._getRole(error_line))
    error_content = json.loads(error_line.getTextContent())['content']
    self.assertIn('The user stopped this run.', error_content)
    self.assertEqual(
      42, error_line.getQuantity(),
      'the cancelled line holds the quantity %s' % (
        error_line.getQuantity(), ))

    self.assertEqual('stopped', request_line.getSimulationState())
    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_36_theOptOutCallsTheConnectorWithBackgroundFalse(self):
    """A line with is_background_enabled false must block for the answer.

    The connector then holds the Zope node for the whole generation. The
    answer arrives inside the same activity, so no Alarm period is
    necessary.
    """
    response_identifier = self._buildProviderIdentifier(
      '36', prefix='chatcmpl')
    _, artificial_task, request_line = self._buildLlmRequestFixture(
      'background_opt_out')

    # The property comes from the property sheet ArtificialTask.
    request_line.edit(is_background_enabled=False)
    self.commit()
    self.assertEqual(False, request_line.getIsBackgroundEnabled())

    _, call_log = self._patchConnectorResponses([
      {'id': response_identifier, 'status': 'completed',
       'content': 'The blocking call answered.',
       'usage': {'total_tokens': 7}},
    ])
    try:
      request_line.start()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual(1, len(call_log))
    self.assertEqual(False, call_log[0]['background'])
    # The blocking call needs no read at the provider. Count the reads of
    # this line only. The Alarm of the instance can read one other line.
    self.assertEqual(0, self._countRetrieveCall(response_identifier))

    answer_line_list = self._getAnswerLineList(request_line)
    self.assertEqual(
      1, len(answer_line_list),
      'the blocking call produced %s answer lines'
      % (len(answer_line_list), ))
    self.assertEqual('assistant', self._getRole(answer_line_list[0]))
    self.assertEqual(
      'The blocking call answered.',
      json.loads(answer_line_list[0].getTextContent())['content'])
    self.assertEqual(7, answer_line_list[0].getQuantity())
    # The identifier of the blocking answer reaches the line too.
    self.assertEqual(
      response_identifier, request_line.getDestinationReference())
    self.assertEqual('stopped', request_line.getSimulationState())
    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_37_checkResponseMakesNoNetworkCallWhenAnAnswerExists(self):
    """checkResponse must read no provider when one answer line exists.

    The Alarm reads every line in the state `started`. A line that holds one
    answer needs no read. Without this guard the Alarm reads the provider on
    every period, for ever.
    """
    response_identifier = self._buildProviderIdentifier('37')
    report = self._getReport('background_answered')
    self._newArtificialTaskForReport(
      report, 'Workflow send background answered test',
      tool_list=[READ_ONLY_TOOL_ID], with_connector=True)
    request_line = self._newLine(report, 1, {'role': 'llm_request'})
    # A line built by hand. `beforeTearDown` closes it after a failure.
    self._started_line_list.append(request_line)
    answer_line = self._newLine(
      report, 2, {'role': 'assistant', 'content': 'the answer'})
    answer_line.setCausalityValue(request_line)
    answer_line.stop()
    request_line.setDestinationReference(response_identifier)
    self.commit()
    self.tic()

    # The transition starts no activity, because the answer already exists.
    request_line.start()
    self.commit()
    self.assertEqual('started', request_line.getSimulationState())
    self.assertEqual(0, self._countActivity(request_line))

    _, call_log = self._patchConnectorResponses([])
    try:
      result = request_line.ArtificialTaskReportLine_checkResponse()
      self.commit()
    finally:
      self._unpatchConnector()

    self.assertEqual('answer already exists', result)
    self.assertEqual(
      [], self._retrieve_call_log,
      'the script read the provider for one line that holds one answer')
    self.assertEqual([], call_log)
    self.assertEqual([], self._cancel_call_log)
    self.assertEqual(2, len(self._getLineList(report)))
    # The request script stops the line, or the Alarm reads it for ever.
    self.assertEqual(
      'stopped', request_line.getSimulationState(),
      'the line holds one answer and stays in the state %s'
      % (request_line.getSimulationState(), ))
    self.assertEqual([], self._getPermanentlyFailedMessageList())

    self._closeStartedLine(request_line)

  def test_38_theNewMethodsAreNotPublishableOverHttp(self):
    """checkResponse and cancelRequest must hold no docstring.

    This version of ERP5 holds no decorator `non_publishable`. Zope does not
    publish a method that has no docstring. The missing docstring is the
    only guard. A GET on `<line>/checkResponse` costs money, because
    recording one answer can start the next paid request.

    The skin script `ArtificialTaskReportLine_checkResponse` holds its own
    guard. Zope passes `REQUEST` to every published script. The script
    raises `Unauthorized` for such a caller.
    """
    from erp5.component.document.ArtificialTaskReportLine import \
      ArtificialTaskReportLine
    self.assertEqual(None, ArtificialTaskReportLine.checkResponse.__doc__)
    self.assertEqual(None, ArtificialTaskReportLine.cancelRequest.__doc__)

    document_class = self._getPortalTypeClass()
    self.assertEqual(None, document_class.checkResponse.__doc__)
    self.assertEqual(None, document_class.cancelRequest.__doc__)

    # The two methods carry the right permission.
    from AccessControl.Permission import pname
    security_info = getattr(ArtificialTaskReportLine, 'security', None)
    name_dict = getattr(security_info, 'names', None) or {}
    permission_of_check = name_dict.get('checkResponse')
    if permission_of_check is None:
      # NOTE: ClassSecurityInfo keeps the mangled name of the permission.
      role_holder = ArtificialTaskReportLine.__dict__.get(
        'checkResponse__roles__')
      permission_of_check = getattr(role_holder, '_p', None)
    self.assertIn(
      permission_of_check,
      (ACCESS_CONTENTS_INFORMATION,
       pname(ACCESS_CONTENTS_INFORMATION)),
      'checkResponse carries the permission %r' % (permission_of_check, ))

    report = self._getReport('not_publishable')
    line = self._newLine(report, 1, {'role': 'llm_request'})
    self.commit()

    # The guard runs before every other rule of the script. The state of the
    # line does not matter here.
    self.assertRaises(
      Unauthorized, line.ArtificialTaskReportLine_checkResponse,
      REQUEST=self.portal.REQUEST)
    self.assertRaises(
      Unauthorized, line.ArtificialTaskReportLine_checkResponse,
      is_cancel=1, REQUEST=self.portal.REQUEST)
    self.assertEqual(1, len(self._getLineList(report)))
    self.abort()

  def test_39_anOldRequestThatIsCompleteIsRecordedAndNotCancelled(self):
    """One old request that the provider completed must give its answer.

    WARNING: the first version of the script tested the age before the read.
    One answer that the provider completed, and that nobody read for
    MAXIMUM_REQUEST_DURATION_SECOND, was then cancelled. The answer was lost,
    and the provider billed that answer. Three events make this case: one long
    stop of the Alarm, one maintenance of the instance, and one read that fails
    for a long time.

    The script must read the provider first. The answer is done, so the
    script must record the answer. The script must call no cancel.
    """
    response_identifier = self._buildProviderIdentifier('39')
    from DateTime import DateTime
    report, artificial_task, request_line = self._buildLlmRequestFixture(
      'background_old_but_complete')

    self._patchConnectorResponses(
      [{'id': response_identifier, 'status': 'queued'}],
      retrieve_response_dict={
        response_identifier: self._buildResponse(
          id=response_identifier, status='completed',
          content='The provider finished this answer long ago.',
          usage={'total_tokens': 34}),
      })
    try:
      request_line.start()
      self.commit()
      self.tic()
      self.assertEqual(
        response_identifier, request_line.getDestinationReference())

      # Move the clock of the line into the past. The age is then above the
      # bound of the stuck rule.
      old_date = DateTime() - (
        (MAXIMUM_REQUEST_DURATION_SECOND + 600) / 86400.0)
      request_line.edit(start_date=old_date)
      self.commit()

      request_line.ArtificialTaskReportLine_checkResponse()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual(
      1, self._countRetrieveCall(response_identifier),
      'retrieveResponse ran %s times on this line'
      % (self._countRetrieveCall(response_identifier), ))
    self._assertRetrieveCallLogNames(response_identifier)
    self.assertEqual(
      0, self._countCancelCall(response_identifier),
      'the script cancelled one answer that the provider had completed')

    answer_line_list = self._getAnswerLineList(request_line)
    self.assertEqual(
      1, len(answer_line_list),
      'the script wrote %s answer lines' % (len(answer_line_list), ))
    self.assertEqual('assistant', self._getRole(answer_line_list[0]))
    self.assertEqual(
      'The provider finished this answer long ago.',
      json.loads(answer_line_list[0].getTextContent())['content'])
    self.assertEqual(34, answer_line_list[0].getQuantity())
    self.assertEqual(0, self._countRole(report, 'error'))
    self.assertEqual('stopped', request_line.getSimulationState())
    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_40_aCancelThatAnswersCompletedStillEndsTheRun(self):
    """One cancel must end the run, whatever status the provider answers.

    OpenAI answers the HTTP status 400 to the cancel of one response that it
    already completed. The local server `yusei-ai`, and every other server
    that speaks the same protocol, can answer the complete object instead.
    The script must not record that object as one normal answer. A user who
    pressed cancel must not see the run continue, and must not pay the next
    round of tool calls.
    """
    response_identifier = self._buildProviderIdentifier('40')
    report, artificial_task, request_line = self._buildLlmRequestFixture(
      'background_cancel_completed')

    _, call_log = self._patchConnectorResponses(
      [{'id': response_identifier, 'status': 'queued'}],
      cancel_response_dict={
        response_identifier: self._buildResponse(
          id=response_identifier, status='completed',
          content='The provider answered this text to the cancel call.',
          tool_calls=[{
            'id': 'call_bg_40',
            'type': 'function',
            'function': {'name': READ_ONLY_TOOL_ID, 'arguments': '{}'},
          }],
          usage={'total_tokens': 11}),
      })
    try:
      request_line.start()
      self.commit()
      self.tic()
      self.assertEqual(
        response_identifier, request_line.getDestinationReference())

      request_line.cancelRequest(comment=u'The user stopped this run.')
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    # No read first: a complete answer must not restart a stopped run.
    self.assertEqual(
      1, len(self._cancel_call_log),
      'cancelResponse ran %s times' % (len(self._cancel_call_log), ))
    self.assertEqual(
      1, len(call_log),
      'createResponse ran %s times. The run continued after the cancel.'
      % (len(call_log), ))

    answer_line_list = self._getAnswerLineList(request_line)
    self.assertEqual(1, len(answer_line_list))
    error_line = answer_line_list[0]
    self.assertEqual(
      'error', self._getRole(error_line),
      'the script recorded the cancel as one normal answer')
    error_content = json.loads(error_line.getTextContent())['content']
    self.assertIn('cancelled', error_content)
    self.assertIn('The user stopped this run.', error_content)
    # The provider bills the tokens that it generated before the stop.
    self.assertEqual(11, error_line.getQuantity())

    self.assertEqual(0, self._countRole(report, 'tool'))
    self.assertEqual('stopped', request_line.getSimulationState())
    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_44_aReadThatRaisesOnAYoungLineWritesNothing(self):
    """One read that raises must not end one young run.

    A transport error is not an answer. `retrieveResponse` raises on one
    HTTP 429 and on one HTTP 502 of the proxy. The line is younger than
    MAXIMUM_REQUEST_DURATION_SECOND. The script must write no line, must
    call no cancel, and must leave the line in the state `started`.

    The text of the error holds characters that are not ASCII. On Python 2
    the built in function `str` raises on such a text. The helper `safeText`
    of the script must catch that raise.
    """
    response_identifier = self._buildProviderIdentifier('44')
    report, artificial_task, request_line = self._buildLlmRequestFixture(
      'background_read_raises_young')

    self._patchConnectorResponses(
      [{'id': response_identifier, 'status': 'queued'}])
    connector_class = self._patched_class
    retrieve_log = []

    def raising_retrieve(self, response_id, **kw):
      retrieve_log.append(response_id)
      raise ValueError(NON_ASCII_TEXT)

    try:
      request_line.start()
      self.commit()
      self.tic()
      self.assertEqual(
        response_identifier, request_line.getDestinationReference())
      line_count_before = len(self._getLineList(report))

      # Replace the read only. The stub of the cancel stays, so the call log
      # of the cancel still proves that no cancel ran.
      connector_class.retrieveResponse = raising_retrieve
      result = request_line.ArtificialTaskReportLine_checkResponse()
      self.commit()
    finally:
      self._unpatchConnector()

    self.assertTrue(
      result.startswith('the response is not known yet'),
      'the script answered %r' % (result, ))
    self.assertEqual([response_identifier], retrieve_log)
    self.assertEqual(
      [], self._cancel_call_log,
      'the script cancelled one request that is not too old')
    self.assertEqual(line_count_before, len(self._getLineList(report)))
    self.assertEqual([], self._getAnswerLineList(request_line))
    self.assertEqual(0, self._countRole(report, 'error'))
    self.assertEqual('started', request_line.getSimulationState())
    self.assertEqual('processing', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

    self._closeStartedLine(request_line)

  def test_45_aFailedCancelOnAnOldLineKeepsTheRealAnswer(self):
    """One failed cancel must not destroy one answer that the provider holds.

    The line is older than MAXIMUM_REQUEST_DURATION_SECOND. The first read
    raises. The script therefore goes to the stuck path. The cancel raises
    too. The script tests no HTTP status on the error of the cancel. The
    cancel writes to one sub-path, and one HTTP status 404 on that sub-path
    says nothing about the response.

    The script must then read the provider one more time. The provider holds
    one completed answer. The provider billed that answer. The script must
    record that answer as one assistant line, and must write no error line.
    """
    response_identifier = self._buildProviderIdentifier('45')
    from DateTime import DateTime
    report, artificial_task, request_line = self._buildLlmRequestFixture(
      'background_failed_cancel')

    self._patchConnectorResponses(
      [{'id': response_identifier, 'status': 'queued'}])
    connector_class = self._patched_class
    retrieve_log = []
    cancel_log = []
    build_response = self._buildResponse

    def raising_then_answering_retrieve(self, response_id, **kw):
      retrieve_log.append(response_id)
      if response_id != response_identifier:
        return build_response(id=response_id, status='in_progress')
      if len([x for x in retrieve_log if x == response_identifier]) == 1:
        # The first read fails. A transport error is not an answer.
        raise ValueError(NON_ASCII_TEXT)
      return build_response(
        id=response_identifier, status='completed',
        content='The provider completed this answer long ago.',
        usage={'total_tokens': 27})

    def raising_cancel(self, response_id, **kw):
      cancel_log.append(response_id)
      raise ValueError(NON_ASCII_TEXT)

    try:
      request_line.start()
      self.commit()
      self.tic()
      self.assertEqual(
        response_identifier, request_line.getDestinationReference())

      # Move the clock of the line into the past. The age is then above the
      # bound of the stuck rule.
      old_date = DateTime() - (
        (MAXIMUM_REQUEST_DURATION_SECOND + 600) / 86400.0)
      request_line.edit(start_date=old_date)
      self.commit()

      connector_class.retrieveResponse = raising_then_answering_retrieve
      connector_class.cancelResponse = raising_cancel
      result = request_line.ArtificialTaskReportLine_checkResponse()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual('run finished', result)
    self.assertEqual(
      1, len([x for x in cancel_log if x == response_identifier]),
      'cancelResponse ran %s times on this line' % (len(cancel_log), ))
    self.assertEqual(
      2, len([x for x in retrieve_log if x == response_identifier]),
      'retrieveResponse ran %s times on this line. The script must read the '
      'provider one more time after one failed cancel.'
      % (len([x for x in retrieve_log if x == response_identifier]), ))

    answer_line_list = self._getAnswerLineList(request_line)
    self.assertEqual(
      1, len(answer_line_list),
      'the script wrote %s answer lines' % (len(answer_line_list), ))
    answer_line = answer_line_list[0]
    self.assertEqual(
      'assistant', self._getRole(answer_line),
      'the script destroyed one answer that the provider billed')
    self.assertEqual(
      'The provider completed this answer long ago.',
      json.loads(answer_line.getTextContent())['content'])
    self.assertEqual(27, answer_line.getQuantity())
    self.assertEqual(
      0, self._countRole(report, 'error'),
      'the script wrote one error line for one answer that exists')
    self.assertEqual('stopped', request_line.getSimulationState())
    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_46_aStuckCancelThatAnswersCompletedKeepsTheAnswer(self):
    """The stuck path must keep one completed answer of the cancel call.

    WARNING: no user pressed cancel here. `is_cancel` is 0. The stuck rule
    alone reached the cancel. The provider completed the response before the
    cancel arrived, and the provider billed that response. The first version of
    the script overwrote `status`, `content` and `tool_calls` of that answer.
    The paid answer was lost, and the run ended with one error line.

    `test_40` proves the other side of this rule. A user cancel must force
    the status `cancelled`, whatever the provider answers.
    """
    response_identifier = self._buildProviderIdentifier('46')
    from DateTime import DateTime
    report, artificial_task, request_line = self._buildLlmRequestFixture(
      'background_stuck_completed')

    self._patchConnectorResponses(
      [{'id': response_identifier, 'status': 'queued'}],
      retrieve_response_dict={
        response_identifier: self._buildResponse(
          id=response_identifier, status='in_progress'),
      },
      cancel_response_dict={
        response_identifier: self._buildResponse(
          id=response_identifier, status='completed',
          content='The provider completed this answer before the cancel.',
          usage={'total_tokens': 19}),
      })
    try:
      request_line.start()
      self.commit()
      self.tic()
      self.assertEqual(
        response_identifier, request_line.getDestinationReference())

      # Move the clock of the line into the past. The age is then above the
      # bound of the stuck rule.
      old_date = DateTime() - (
        (MAXIMUM_REQUEST_DURATION_SECOND + 600) / 86400.0)
      request_line.edit(start_date=old_date)
      self.commit()

      # `is_cancel` holds the default value 0. No user pressed cancel.
      result = request_line.ArtificialTaskReportLine_checkResponse()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual('run finished', result)
    self.assertEqual(
      1, self._countRetrieveCall(response_identifier),
      'retrieveResponse ran %s times on this line'
      % (self._countRetrieveCall(response_identifier), ))
    self.assertEqual(
      1, self._countCancelCall(response_identifier),
      'cancelResponse ran %s times on this line'
      % (self._countCancelCall(response_identifier), ))
    self._assertRetrieveCallLogNames(response_identifier)

    answer_line_list = self._getAnswerLineList(request_line)
    self.assertEqual(
      1, len(answer_line_list),
      'the script wrote %s answer lines' % (len(answer_line_list), ))
    answer_line = answer_line_list[0]
    self.assertEqual(
      'assistant', self._getRole(answer_line),
      'the script recorded one paid answer as one error')
    self.assertEqual(
      'The provider completed this answer before the cancel.',
      json.loads(answer_line.getTextContent())['content'])
    self.assertEqual(19, answer_line.getQuantity())
    self.assertEqual(
      0, self._countRole(report, 'error'),
      'the script wrote one error line and lost one paid answer')
    self.assertEqual('stopped', request_line.getSimulationState())
    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_47_aCreateThatAnswersNoIdentifierEndsTheRun(self):
    """One create with no identifier must end the run at once.

    WARNING: this method holds the correction A3. The provider holds the
    request and answers no `id`. `is_done` is false, so no answer exists
    either. `Alarm_checkArtificialTaskReportLineResponse` skips every line
    that holds no `destination_reference`. Such one line therefore stays in
    the state `started` for ever, and no human sees the failure.

    The request script must fail the run at once.
    """
    _, artificial_task, request_line = self._buildLlmRequestFixture(
      'background_no_identifier')

    _, call_log = self._patchConnectorResponses([
      {'id': None, 'status': 'queued'},
    ])
    try:
      request_line.start()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual(
      1, len(call_log),
      'createResponse ran %s times' % (len(call_log), ))
    self.assertEqual(
      '', request_line.getDestinationReference() or '',
      'the line holds the identifier %r'
      % (request_line.getDestinationReference(), ))

    answer_line_list = self._getAnswerLineList(request_line)
    self.assertEqual(
      1, len(answer_line_list),
      'the script wrote %s answer lines' % (len(answer_line_list), ))
    error_line = answer_line_list[0]
    self.assertEqual(
      'error', self._getRole(error_line),
      'the script wrote one line with the role %s'
      % (self._getRole(error_line), ))
    error_content = json.loads(error_line.getTextContent())['content']
    self.assertIn(
      'no identifier', error_content,
      'the error line holds the text %r' % (error_content[:400], ))

    self.assertEqual(
      'stopped', request_line.getSimulationState(),
      'the line stays in the state %s. The Alarm never reads that line, '
      'because the line holds no identifier.'
      % (request_line.getSimulationState(), ))
    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_48_aCancelCommentThatIsNotUnicodeDoesNotRaise(self):
    """One byte comment that is not ASCII must record one error line.

    WARNING: this method holds the correction A4. The comment of the user
    arrives as one byte string when the caller is one ERP5 Form. On Python 2
    the operation `u'%s' % (byte_string, )` raises `UnicodeDecodeError` when
    the byte string holds one character that is not ASCII. That raise
    happens inside the `except` block of `stopRequestAtProvider`, so nothing
    is recorded, and the line stays `started` for ever.

    The helper `safeText` of the script must catch that raise. The script
    must then record one error line.

    NOTE: `safeText` answers the `repr` of the byte string in that case.
    The ASCII part of the comment reaches the error line. The escape form
    holds the other characters. The method therefore tests the ASCII part.
    """
    response_identifier = self._buildProviderIdentifier('48')
    _, artificial_task, request_line = self._buildLlmRequestFixture(
      'background_byte_comment')

    # One byte string in the encoding utf-8. The text holds two characters
    # that are not ASCII. The first sentence holds ASCII characters only.
    byte_comment = (
      u'Der Benutzer stoppte diesen Lauf. Pr\xfcfung \xd6').encode('utf-8')

    self._patchConnectorResponses(
      [{'id': response_identifier, 'status': 'queued'}])
    connector_class = self._patched_class
    cancel_log = []

    def raising_cancel(self, response_id, **kw):
      cancel_log.append(response_id)
      raise ValueError(NON_ASCII_TEXT)

    try:
      request_line.start()
      self.commit()
      self.tic()
      self.assertEqual(
        response_identifier, request_line.getDestinationReference())

      connector_class.cancelResponse = raising_cancel
      result = request_line.cancelRequest(comment=byte_comment)
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual('error', result)
    self.assertEqual([response_identifier], cancel_log)
    # One user cancel reads the provider no time.
    self.assertEqual(0, self._countRetrieveCall(response_identifier))

    answer_line_list = self._getAnswerLineList(request_line)
    self.assertEqual(
      1, len(answer_line_list),
      'the script wrote %s answer lines. The byte comment stopped the '
      'record.' % (len(answer_line_list), ))
    error_line = answer_line_list[0]
    self.assertEqual('error', self._getRole(error_line))
    error_content = json.loads(error_line.getTextContent())['content']
    self.assertIn(
      'Der Benutzer stoppte diesen Lauf.', error_content,
      'the error line holds the text %r' % (error_content[:400], ))
    self.assertIn('cancelled', error_content)

    self.assertEqual('stopped', request_line.getSimulationState())
    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_49_aCancelAndAReadThatBothFailKeepTheLineStarted(self):
    """The script must wait when the cancel and the second read both fail.

    The line is older than MAXIMUM_REQUEST_DURATION_SECOND and younger than
    two times that bound. The first read raises. The cancel raises. The
    second read raises too, and no error is one HTTP 404.

    The provider gives no state. The script must write nothing, and must
    leave the line in the state `started`. A synthetic cancelled answer here
    would destroy one answer that the provider can still hold.
    """
    response_identifier = self._buildProviderIdentifier('49')
    from DateTime import DateTime
    report, artificial_task, request_line = self._buildLlmRequestFixture(
      'background_no_state_young')

    self._patchConnectorResponses(
      [{'id': response_identifier, 'status': 'queued'}])
    connector_class = self._patched_class
    retrieve_log = []
    cancel_log = []

    def raising_retrieve(self, response_id, **kw):
      retrieve_log.append(response_id)
      raise ValueError(NON_ASCII_TEXT)

    def raising_cancel(self, response_id, **kw):
      cancel_log.append(response_id)
      raise ValueError(NON_ASCII_TEXT)

    try:
      request_line.start()
      self.commit()
      self.tic()
      self.assertEqual(
        response_identifier, request_line.getDestinationReference())
      line_count_before = len(self._getLineList(report))

      # The age is above one bound and below two bounds.
      old_date = DateTime() - (
        (MAXIMUM_REQUEST_DURATION_SECOND + 600) / 86400.0)
      request_line.edit(start_date=old_date)
      self.commit()

      connector_class.retrieveResponse = raising_retrieve
      connector_class.cancelResponse = raising_cancel
      result = request_line.ArtificialTaskReportLine_checkResponse()
      self.commit()
    finally:
      self._unpatchConnector()

    self.assertEqual('the response is not known yet', result)
    self.assertEqual(
      2, len([x for x in retrieve_log if x == response_identifier]),
      'retrieveResponse ran %s times on this line. The script must read the '
      'provider one more time after one failed cancel.'
      % (len([x for x in retrieve_log if x == response_identifier]), ))
    self.assertEqual([response_identifier], cancel_log)
    self.assertEqual(line_count_before, len(self._getLineList(report)))
    self.assertEqual([], self._getAnswerLineList(request_line))
    self.assertEqual(0, self._countRole(report, 'error'))
    self.assertEqual(
      'started', request_line.getSimulationState(),
      'the script ended one line that the provider can still answer')
    self.assertEqual('processing', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

    self._closeStartedLine(request_line)

  def test_50_aCancelAndAReadThatBothFailEndTheLineAtTwoBounds(self):
    """The script must end the line at two times the bound.

    The line is older than two times MAXIMUM_REQUEST_DURATION_SECOND. The
    first read raises. The cancel raises. The second read raises too. The
    provider gives no state, and the line waited long enough.

    The script must write one error line. That line must hold the text
    `The provider gave no state`. The line must also hold the recorded
    cause, so a human reads why the provider gave no state.
    """
    response_identifier = self._buildProviderIdentifier('50')
    from DateTime import DateTime
    _, artificial_task, request_line = self._buildLlmRequestFixture(
      'background_no_state_old')

    self._patchConnectorResponses(
      [{'id': response_identifier, 'status': 'queued'}])
    connector_class = self._patched_class
    retrieve_log = []
    cancel_log = []

    def raising_retrieve(self, response_id, **kw):
      retrieve_log.append(response_id)
      raise ValueError(NON_ASCII_TEXT)

    def raising_cancel(self, response_id, **kw):
      cancel_log.append(response_id)
      raise ValueError(NON_ASCII_TEXT)

    try:
      request_line.start()
      self.commit()
      self.tic()
      self.assertEqual(
        response_identifier, request_line.getDestinationReference())

      # The age is above two bounds.
      old_date = DateTime() - (
        (2 * MAXIMUM_REQUEST_DURATION_SECOND + 600) / 86400.0)
      request_line.edit(start_date=old_date)
      self.commit()

      connector_class.retrieveResponse = raising_retrieve
      connector_class.cancelResponse = raising_cancel
      result = request_line.ArtificialTaskReportLine_checkResponse()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual('error', result)
    self.assertEqual(
      2, len([x for x in retrieve_log if x == response_identifier]),
      'retrieveResponse ran %s times on this line'
      % (len([x for x in retrieve_log if x == response_identifier]), ))
    self.assertEqual([response_identifier], cancel_log)

    answer_line_list = self._getAnswerLineList(request_line)
    self.assertEqual(
      1, len(answer_line_list),
      'the script wrote %s answer lines' % (len(answer_line_list), ))
    error_line = answer_line_list[0]
    self.assertEqual('error', self._getRole(error_line))
    error_content = json.loads(error_line.getTextContent())['content']
    self.assertIn(
      'The provider gave no state', error_content,
      'the error line holds the text %r' % (error_content[:400], ))
    self.assertIn(
      'The cancel call failed', error_content,
      'the error line holds no cause. A human cannot read why the provider '
      'gave no state. The text is %r' % (error_content[:400], ))
    self.assertIn(
      '%s' % (MAXIMUM_REQUEST_DURATION_SECOND, ), error_content)

    self.assertEqual('stopped', request_line.getSimulationState())
    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_51_aCancelWithAUsageOfZeroWritesTheQuantityZero(self):
    """A cancelled line and every request line must hold the quantity 0.

    The measurement shows the answer of the provider to one cancel of one
    running response. The status is `cancelled`. Every value of `usage` is 0.
    The cancel stub answers that shape.

    The Artificial Task Report Line is one Movement. ERP5 gives every new
    Movement the default `quantity=1.0`. A line that keeps 1.0 reports one
    token that the provider never reported. The error line must hold the
    quantity 0 and the unit `unit/token`.

    The fixture creates the `user` line and the first `llm_request` line
    with `_newLine`, not with one production script. The test therefore
    drives one tool round first. The first answer of the provider holds one
    tool call with a name outside the tool list. The request script then
    creates one `tool_request` line and one second `llm_request` line with
    `newRequestLine`. Both lines must hold the quantity 0 and the unit. The
    second `llm_request` line waits at the provider, and the test cancels
    that line.

    `test_35` proves the cancel path with a count above 0. This method proves
    the count 0.
    """
    response_identifier = self._buildProviderIdentifier('51')
    first_response_identifier = self._buildProviderIdentifier('51_first')
    report, artificial_task, request_line = self._buildLlmRequestFixture(
      'background_cancel_zero')

    # The tool name is outside the tool list. The allow list refuses the
    # tool, and no tool runs. The refusal is one normal tool answer.
    tool_call = self._buildToolCall(
      'call_51_%s' % (self._run_identifier, ), None,
      tool_name=WRITE_TOOL_ID, argument_dict={})
    _, call_log = self._patchConnectorResponses(
      [{'id': first_response_identifier, 'status': 'completed',
        'tool_calls': [tool_call],
        'usage': {'prompt_tokens': 9, 'completion_tokens': 4,
                  'total_tokens': 13, 'cached_tokens': 0}},
       {'id': response_identifier, 'status': 'queued'}],
      cancel_response_dict={
        response_identifier: self._buildResponse(
          id=response_identifier, status='cancelled',
          usage={'prompt_tokens': 0, 'completion_tokens': 0,
                 'total_tokens': 0, 'cached_tokens': 0}),
      })
    try:
      request_line.start()
      self.commit()
      self.tic()
      self.assertEqual(
        2, len(call_log), 'createResponse ran %s times' % (len(call_log), ))

      # The lines that the request script created in the tool round.
      tool_request_line_list = [
        x for x in self._getLineList(report)
        if self._getRole(x) == 'tool_request']
      second_request_line_list = [
        x for x in self._getLineList(report)
        if self._getRole(x) == 'llm_request' and
        x.getRelativeUrl() != request_line.getRelativeUrl()]
      self.assertEqual(1, len(tool_request_line_list))
      self.assertEqual(1, len(second_request_line_list))
      tool_request_line = tool_request_line_list[0]
      second_request_line = second_request_line_list[0]
      # `beforeTearDown` closes this line whatever the test does.
      self._started_line_list.append(second_request_line)
      self.assertEqual(
        response_identifier, second_request_line.getDestinationReference())

      result = second_request_line.cancelRequest(
        comment=u'The user stopped this run.')
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual('error', result)
    self.assertEqual(1, self._countCancelCall(response_identifier))
    self.assertEqual(0, self._countRetrieveCall(response_identifier))

    # A request line reads no provider. `newRequestLine` must write 0. The
    # default of one Movement is 1.0, and 1.0 is one false count.
    for created_line in (tool_request_line, second_request_line):
      self.assertEqual(
        0, created_line.getQuantity(),
        'the request line %s holds the quantity %s'
        % (self._getRole(created_line), created_line.getQuantity()))
      self.assertEqual(
        'unit/token', created_line.getQuantityUnit(),
        'the request line %s holds the quantity unit %s'
        % (self._getRole(created_line), created_line.getQuantityUnit()))

    answer_line_list = self._getAnswerLineList(second_request_line)
    self.assertEqual(
      1, len(answer_line_list),
      'the request produced %s answer lines' % (len(answer_line_list), ))
    error_line = answer_line_list[0]
    self.assertEqual('error', self._getRole(error_line))
    error_content = json.loads(error_line.getTextContent())['content']
    self.assertIn('The user stopped this run.', error_content)
    # The provider reported 0 tokens. The line must hold 0.
    self.assertEqual(
      0, error_line.getQuantity(),
      'the cancelled line holds the quantity %s. The provider reported 0 '
      'tokens.' % (error_line.getQuantity(), ))
    self.assertEqual(
      'unit/token', error_line.getQuantityUnit(),
      'the cancelled line holds the quantity unit %s'
      % (error_line.getQuantityUnit(), ))

    self.assertEqual('stopped', request_line.getSimulationState())
    self.assertEqual('stopped', second_request_line.getSimulationState())
    self.assertEqual('stopped', error_line.getSimulationState())
    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_52_theRequestLineHoldsEverySendParameter(self):
    """`ArtificialTask_startAgent` writes every send parameter on the line.

    The send path reads the line only. The line must therefore hold the
    connector, the model, the tool definitions and the record of the system
    pages.
    """
    response_identifier = self._buildProviderIdentifier('52')
    report = self._getReport('parameter_on_line')
    artificial_task = self._newArtificialTaskForReport(
      report, 'Workflow send parameter test',
      tool_list=[READ_ONLY_TOOL_ID], with_connector=True)
    self.commit()
    self.tic()

    _, call_log = self._patchConnectorResponses([
      {'id': response_identifier, 'status': 'completed',
       'content': 'the answer of the stub', 'usage': {'total_tokens': 5}},
    ])
    try:
      artificial_task.ArtificialTask_startAgent()
      self.commit()
      # WARNING: register the started lines first. A queued send activity
      # makes the next `tic()` call the real provider.
      self._registerStartedLineList(report)
      request_line_list = [
        x for x in self._getLineList(report)
        if self._getRole(x) == 'llm_request']
      self.assertEqual(1, len(request_line_list))
      request_line = request_line_list[0]

      self.assertTrue(
        request_line.getConnectorValue() is not None,
        'the request line holds no connector')
      self.assertEqual(
        artificial_task.getConnectorValue().getRelativeUrl(),
        request_line.getConnectorValue().getRelativeUrl())
      self.assertEqual(
        artificial_task.getModel(), request_line.getModel(),
        'the request line holds the model %r' % (request_line.getModel(), ))
      self.assertEqual(
        artificial_task.getIsBackgroundEnabled(),
        request_line.getIsBackgroundEnabled())

      payload = json.loads(request_line.getTextContent())
      self.assertEqual(artificial_task.getModel(), payload.get('model'))
      self.assertTrue(
        isinstance(payload.get('tools'), list),
        'the payload holds no list of tools: %r' % (payload.get('tools'), ))
      self.assertTrue(
        isinstance(payload.get('system'), list),
        'the payload holds no record of the system pages: %r'
        % (payload.get('system'), ))
      self.assertEqual(
        [READ_ONLY_TOOL_ID],
        [x.get('function', {}).get('name') or x.get('name')
         for x in payload['tools']],
        'the payload holds the tool definitions %r' % (payload['tools'], ))
      self.assertEqual(
        artificial_task.getRequestParameter(),
        request_line.getRequestParameter())

      # The base category `resource` names one validated Service. No test
      # creates one Service, so the assertion reads the catalog first.
      service_list = list(self.portal.portal_catalog(
        portal_type='Service', reference=artificial_task.getModel(),
        validation_state='validated', limit=2))
      if service_list:
        self.assertEqual(
          'Service', request_line.getResourceValue().getPortalType())
      else:
        self.assertEqual(
          None, request_line.getResourceValue(),
          'no validated Service names the model, so the line must hold no '
          'resource')
      self.assertEqual(artificial_task.getModel(), payload.get('model'))

      self.tic()
    finally:
      self._unpatchConnector()

    # The send path read the tool definitions of the line. The provider
    # therefore received the tool schema list of this run.
    self.assertEqual(1, len(call_log))
    self.assertEqual(
      [READ_ONLY_TOOL_ID],
      [x.get('function', {}).get('name') or x.get('name')
       for x in (call_log[0].get('tools') or [])],
      'the connector received the tools %r' % (call_log[0].get('tools'), ))
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_53_theSendPathDoesNotReadTheTaskForTheModel(self):
    """One line with no parameter gives one error line and calls nobody.

    The Artificial Task of this report holds one connector and one model.
    The line holds no connector and no model. The send path must read the
    line only, so the run must end with one error line.
    """
    response_identifier = self._buildProviderIdentifier('53')
    report = self._getReport('no_parameter_on_line')
    self._newArtificialTaskForReport(
      report, 'Workflow send no parameter test',
      tool_list=[READ_ONLY_TOOL_ID], with_connector=True)
    # BBB: a line with no send parameter.
    request_line = report.newContent(
      portal_type=PORTAL_TYPE,
      int_index=1,
      text_content=json.dumps({'role': 'llm_request'}),
    )
    self.commit()
    self.tic()
    self._started_line_list.append(request_line)

    _, call_log = self._patchConnectorResponses([
      {'id': response_identifier, 'status': 'completed',
       'content': 'this answer must never arrive'},
    ])
    try:
      request_line.start()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual(
      0, len(call_log),
      'the send path called the provider %s times' % (len(call_log), ))
    error_line_list = [
      x for x in self._getLineList(report) if self._getRole(x) == 'error']
    self.assertEqual(
      1, len(error_line_list),
      'the run wrote %s error lines' % (len(error_line_list), ))
    self._assertOnlyConnectorError(report)
    self.assertEqual('stopped', request_line.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_54_theAnswerLineHoldsTheModelAndTheUsage(self):
    """The answer line holds the model, the connector and the usage map."""
    response_identifier = self._buildProviderIdentifier('54')
    answer_model = 'gpt-4.1-%s' % (self._run_identifier, )
    _, _, request_line = self._buildLlmRequestFixture(
      'answer_model_and_usage')

    self._patchConnectorResponses([
      {'id': response_identifier, 'status': 'completed',
       'content': 'the answer of the stub',
       'model': answer_model,
       'usage': {'total_tokens': 9, 'prompt_tokens': 4,
                 'completion_tokens': 5}},
    ])
    try:
      request_line.start()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    answer_line_list = self._getAnswerLineList(request_line)
    self.assertEqual(1, len(answer_line_list))
    answer_line = answer_line_list[0]
    payload = json.loads(answer_line.getTextContent())
    self.assertEqual('assistant', payload.get('role'))
    self.assertEqual(
      answer_model, payload.get('model'),
      'the answer line holds the model %r' % (payload.get('model'), ))
    self.assertEqual(
      4, (payload.get('usage') or {}).get('prompt_tokens'),
      'the answer line holds the usage %r' % (payload.get('usage'), ))
    self.assertEqual(9, answer_line.getQuantity())
    self.assertEqual(answer_model, answer_line.getModel())
    self.assertTrue(
      answer_line.getConnectorValue() is not None,
      'the answer line holds no connector')
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_55_theTaskLineLinksToTheReportLineBothWays(self):
    """`finishRun` writes `causality` from the task line to the answer."""
    response_identifier = self._buildProviderIdentifier('55')
    _, artificial_task, request_line = self._buildLlmRequestFixture(
      'causality_both_ways')

    self._patchConnectorResponses([
      {'id': response_identifier, 'status': 'completed',
       'content': 'the answer of the stub', 'usage': {'total_tokens': 3}},
    ])
    try:
      request_line.start()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    answer_line_list = self._getAnswerLineList(request_line)
    self.assertEqual(1, len(answer_line_list))
    answer_line = answer_line_list[0]
    # The comment of the user, then the answer that `finishRun` wrote.
    task_line_list = list(artificial_task.objectValues(
      portal_type='Artificial Task Line'))
    self.assertEqual(
      2, len(task_line_list),
      'the task holds %s Artificial Task Lines' % (len(task_line_list), ))
    answer_task_line_list = [
      x for x in task_line_list
      if x.getCausality() == answer_line.getRelativeUrl()]
    self.assertEqual(
      1, len(answer_task_line_list),
      'the run wrote %s answer Artificial Task Lines'
      % (len(answer_task_line_list), ))
    task_line = answer_task_line_list[0]

    self.assertEqual(
      answer_line.getRelativeUrl(), task_line.getCausality(),
      'the Artificial Task Line points at %r' % (task_line.getCausality(), ))
    related_value = answer_line.getCausalityRelatedValue(
      portal_type='Artificial Task Line')
    self.assertTrue(
      related_value is not None,
      'the answer line answers no related Artificial Task Line')
    self.assertEqual(
      task_line.getRelativeUrl(), related_value.getRelativeUrl())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_56_theUserLineLinksToTheCommentTaskLine(self):
    """`ArtificialTask_startAgent` links the `user` line to the comment.

    The comment of the user is one Artificial Task Line. The `user`
    Artificial Task Report Line points at that Artificial Task Line with the
    category `causality`.
    """
    response_identifier = self._buildProviderIdentifier('56')
    question = 'the question of the run %s' % (self._run_identifier, )
    report = self._getReport('user_line_causality')
    artificial_task = self._newArtificialTaskForReport(
      report, 'Workflow send user link test',
      tool_list=[READ_ONLY_TOOL_ID], with_connector=True)
    comment_line = artificial_task.newContent(
      portal_type='Artificial Task Line', text_content=question)
    comment_line.stop()
    self.commit()
    self.tic()

    self._patchConnectorResponses([
      {'id': response_identifier, 'status': 'completed',
       'content': 'the answer of the stub', 'usage': {'total_tokens': 2}},
    ])
    try:
      artificial_task.ArtificialTask_startAgent()
      self.commit()
      self._registerStartedLineList(report)
      self.tic()
    finally:
      self._unpatchConnector()

    user_line_list = [
      x for x in self._getLineList(report) if self._getRole(x) == 'user']
    self.assertEqual(
      1, len(user_line_list),
      'the run wrote %s user lines' % (len(user_line_list), ))
    user_line = user_line_list[0]
    self.assertEqual(
      question, json.loads(user_line.getTextContent()).get('content'))
    self.assertEqual(
      comment_line.getRelativeUrl(), user_line.getCausality(),
      'the user line points at %r' % (user_line.getCausality(), ))
    related_value = comment_line.getCausalityRelatedValue(
      portal_type=PORTAL_TYPE)
    self.assertTrue(
      related_value is not None,
      'the comment line answers no related Artificial Task Report Line')
    self.assertEqual(
      user_line.getRelativeUrl(), related_value.getRelativeUrl())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_57_aDraftLineOfTheReportIsNotSentToTheProvider(self):
    """One line in the state `draft` must not reach the provider.

    The script `ArtificialTaskReport_getMessageList` reads one Artificial
    Task Report Line in the state `stopped` only. A line in the state
    `draft` is one line that no run finished. A line in the state `started`
    is one request in flight. Neither line is one finished message.

    The test adds one extra line with the role `user`. The test leaves that
    line in the state `draft`. The test then runs one round with the stub of
    the connector. No message of the request holds the text of that line.
    """
    response_identifier = self._buildProviderIdentifier('57')
    stopped_text = 'the stopped question of the run %s' % (
      self._run_identifier, )
    report, _, request_line = self._buildLlmRequestFixture(
      'draft_line', question=stopped_text)
    draft_text = 'the draft question of the run %s' % (self._run_identifier, )
    # This line stays in the state `draft`. The test calls no transition.
    draft_line = self._newLine(
      report, 3, {'role': 'user', 'content': draft_text})
    self.commit()
    self.tic()
    self.assertEqual('draft', draft_line.getSimulationState())

    # The message list must already skip the line, before any round runs.
    message_list = report.ArtificialTaskReport_getMessageList()
    content_list = [x.get('content') or '' for x in message_list]
    self.assertNotIn(
      draft_text, content_list,
      'the message list holds the draft line: %s' % (content_list, ))

    _, call_log = self._patchConnectorResponses([
      {'id': response_identifier, 'status': 'completed',
       'content': 'the answer of the stub', 'usage': {'total_tokens': 2}},
    ])
    try:
      request_line.start()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual(
      1, len(call_log),
      'the stub answered %s calls' % (len(call_log), ))
    sent_message_list = call_log[0].get('messages') or []
    sent_content_list = [
      x.get('content') or '' for x in sent_message_list]
    self.assertNotIn(
      draft_text, sent_content_list,
      'the request holds the draft line: %s' % (sent_content_list, ))
    # The `user` line of the fixture is `stopped`, so that line still
    # reaches the provider. This assertion proves that the skip is narrow.
    self.assertIn(
      stopped_text, sent_content_list,
      'the request lost the stopped user line: %s' % (sent_content_list, ))
    self.assertEqual('draft', draft_line.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_58_theHarnessScriptRefusesAndCreatesNoLine(self):
    """`ArtificialTask_runHarnessAgent` must refuse every call.

    The script must raise one clear error text. The script must create no
    Artificial Task Report, no Artificial Task Report Line and no Artificial
    Task Line.
    """
    report, artificial_task, request_line = self._buildLlmRequestFixture(
      'harness_retired')
    # Close the request line at once. This test runs no round.
    self._closeStartedLine(request_line)
    self.commit()
    self.tic()

    module = self.portal.artificial_task_report_module
    report_id_list_before = sorted([x for x in module.objectIds()])
    line_id_list_before = sorted([x for x in report.objectIds()])
    task_line_id_list_before = sorted(
      [x for x in artificial_task.objectIds()])

    # The connector must never answer. A call of the provider is one defect.
    _, call_log = self._patchConnectorResponses([])
    try:
      error = None
      try:
        artificial_task.ArtificialTask_runHarnessAgent()
      except Exception as raised_error:
        error = raised_error
    finally:
      self._unpatchConnector()

    self.assertTrue(
      error is not None,
      'the harness script answered and raised no error')
    self.assertIn('retired', str(error))
    self.assertIn('ArtificialTask_startAgent', str(error))
    self.assertEqual(
      0, len(call_log),
      'the harness script called the provider %s times' % (len(call_log), ))

    self.commit()
    self.tic()
    self.assertEqual(
      report_id_list_before, sorted([x for x in module.objectIds()]),
      'the harness script created one Artificial Task Report')
    self.assertEqual(
      line_id_list_before, sorted([x for x in report.objectIds()]),
      'the harness script created one Artificial Task Report Line')
    self.assertEqual(
      task_line_id_list_before,
      sorted([x for x in artificial_task.objectIds()]),
      'the harness script created one Artificial Task Line')
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_41_realBackgroundRoundTrip(self):
    """One real background request must answer one identifier, then one text.

    WARNING: this method costs money. This method is skipped by default.

    The method proves three facts at the provider. The provider answers one
    identifier at once. The provider answers the status `queued` or
    `in_progress`. One read later answers the content and the four integer
    keys of `usage`.

    The model is the model of production. `_getRealModel` reads that model
    from `ArtificialTask_getDefaultModel` at run time. The method fails when
    that script names no model. The method never guesses one model.

    The `finally` block cancels the response when the read loop ends before
    the response ends. The provider bills one request that nobody stops.
    """
    self._skipWithoutRealLargeLanguageModel()

    connector = self.portal.ArtificialTask_getDefaultConnector()
    model = self._getRealModel()
    start_time = time.time()
    response = connector.createResponse(
      messages=[{'role': 'user', 'content': REAL_PROMPT}],
      model=model,
      background=True)
    create_second = time.time() - start_time
    fact_text = self._recordProviderFact(
      model,
      'createResponse answered the status %r in %.1f seconds'
      % (response.get('status'), create_second))

    self.assertTrue(
      response.get('id'),
      'the provider answered no identifier: %r. %s'
      % (response, fact_text))
    response_id = response['id']
    try:
      self.assertIn(
        response['status'], ('queued', 'in_progress'),
        'the provider answered the status %r. The provider ignored the '
        'background mode. %s' % (response['status'], fact_text))
      self.assertEqual(
        False, response['is_done'],
        'the provider answered one response that is already done. %s'
        % (fact_text, ))
      self.assertTrue(
        create_second < REAL_CREATE_BOUND_SECOND,
        'createResponse took %.1f seconds. The provider ignored the '
        'background mode. %s' % (create_second, fact_text))

      final_response = self._waitForRealResponse(connector, response_id)
      fact_text = self._recordProviderFact(
        model,
        'retrieveResponse ended with the status %r'
        % (final_response['status'], ))
      self.assertTrue(
        final_response['is_done'],
        'the response did not end inside %s reads. %s'
        % (REAL_READ_COUNT, fact_text))
      self.assertEqual(
        'completed', final_response['status'],
        'the provider ended with one other status. %s' % (fact_text, ))
      self.assertEqual(
        response_id, final_response['id'],
        'the read answered one other identifier. %s' % (fact_text, ))
      self.assertTrue(
        final_response['content'],
        'the provider answered one empty content. %s' % (fact_text, ))

      usage = final_response['usage']
      for usage_key in ('prompt_tokens', 'completion_tokens',
                        'total_tokens', 'cached_tokens'):
        self.assertTrue(
          isinstance(usage.get(usage_key), int),
          'the key %s of usage holds %r, and that value is not one integer. '
          '%s' % (usage_key, usage.get(usage_key), fact_text))
      self.assertTrue(
        usage['total_tokens'] > 0,
        'the provider answered the token count %r. %s'
        % (usage['total_tokens'], fact_text))
    finally:
      self._cancelRealResponseThatRuns(connector, response_id)

  def test_42_realCancel(self):
    """One cancel of one running response must answer one known shape.

    WARNING: this method costs money. This method is skipped by default.

    The method records the status and the `usage` that the provider answers.
    `ArtificialTaskReportLine_checkResponse` writes that token count on the
    error line.

    CAUTION: one fast model can end the response before the cancel arrives.
    The provider then answers the HTTP status 400, and the connector raises.
    That raise is one valid answer of the provider, not one failure of the
    method. `stopRequestAtProvider` reads the provider one more time after
    one failed cancel.

    The model is the model of production. `_getRealModel` reads that model
    from `ArtificialTask_getDefaultModel` at run time.

    The `finally` block cancels the response when the cancel of the method
    did not stop the response. The provider bills the whole job otherwise.
    """
    self._skipWithoutRealLargeLanguageModel()

    connector = self.portal.ArtificialTask_getDefaultConnector()
    model = self._getRealModel()
    response = connector.createResponse(
      messages=[{'role': 'user', 'content': REAL_LONG_PROMPT}],
      model=model,
      background=True)
    self.assertTrue(
      response.get('id'),
      'the provider answered no identifier: %r' % (response, ))
    response_id = response['id']
    try:
      cancel_response = None
      cancel_error_text = ''
      try:
        cancel_response = connector.cancelResponse(response_id)
      except Exception as cancel_error:
        cancel_error_text = repr(cancel_error)
      fact_text = self._recordProviderFact(
        model,
        'cancelResponse on one running response answered %r and raised %r'
        % (cancel_response and cancel_response.get('status'),
           cancel_error_text))

      if cancel_error_text:
        # The provider refused the cancel. The response ended first.
        self.assertIn(
          'LLM ', cancel_error_text,
          'the connector raised one error that the check script does not '
          'know: %s. %s' % (cancel_error_text, fact_text))
        return
      self.assertEqual(
        response_id, cancel_response['id'],
        'the cancel answered one other identifier. %s' % (fact_text, ))
      self.assertIn(
        cancel_response['status'],
        ('cancelled', 'completed', 'failed', 'incomplete', 'queued',
         'in_progress'),
        'the provider answered the unknown status %r. %s'
        % (cancel_response['status'], fact_text))
      self.assertTrue(
        isinstance(cancel_response.get('usage'), dict),
        'the cancel answered no usage: %r. %s'
        % (cancel_response.get('usage'), fact_text))
    finally:
      self._cancelRealResponseThatRuns(connector, response_id)

  def test_43_realCancelOfOneCompletedResponse(self):
    """Record what the provider answers to one cancel of one done response.

    WARNING: this method costs money. This method is skipped by default.

    This method is the reason of the correction A1. The provider can raise
    with the HTTP status 400. The provider can answer one object with one
    status of PROVIDER_TERMINAL_TUPLE, which holds `completed`, `failed` and
    `incomplete`. The provider can answer one object with the status
    `cancelled`. `stopRequestAtProvider` is safe for the three answers.

    The model is the model of production. `_getRealModel` reads that model
    from `ArtificialTask_getDefaultModel` at run time. The answer of the
    provider to one cancel can differ from one model to another model,
    because the route differs. The method must therefore measure the model
    of production. The method never guesses one model.

    The method records the real answer with the name of the model. The
    operator records that fact.
    """
    self._skipWithoutRealLargeLanguageModel()

    connector = self.portal.ArtificialTask_getDefaultConnector()
    model = self._getRealModel()
    response = connector.createResponse(
      messages=[{'role': 'user', 'content': REAL_PROMPT}],
      model=model,
      background=True)
    self.assertTrue(
      response.get('id'),
      'the provider answered no identifier: %r' % (response, ))
    response_id = response['id']
    try:
      final_response = self._waitForRealResponse(connector, response_id)
      fact_text = self._recordProviderFact(
        model,
        'retrieveResponse ended with the status %r before the cancel'
        % (final_response['status'], ))
      self.assertTrue(
        final_response['is_done'],
        'the response did not end inside %s reads. %s'
        % (REAL_READ_COUNT, fact_text))
      self.assertEqual(
        'completed', final_response['status'],
        'the response ended with the status %r. %s'
        % (final_response['status'], fact_text))

      cancel_response = None
      cancel_error_text = ''
      try:
        cancel_response = connector.cancelResponse(response_id)
      except Exception as cancel_error:
        cancel_error_text = repr(cancel_error)
      fact_text = self._recordProviderFact(
        model,
        'cancelResponse on one completed response answered %r and raised %r'
        % (cancel_response and cancel_response.get('status'),
           cancel_error_text))

      if cancel_error_text:
        # The provider refused the cancel. `stopRequestAtProvider` then
        # reads the provider one more time and keeps the completed answer.
        self.assertIn(
          'LLM ', cancel_error_text,
          'the connector raised one error that the check script does not '
          'know: %s. %s' % (cancel_error_text, fact_text))
      else:
        self.assertIn(
          cancel_response['status'],
          ('completed', 'failed', 'incomplete', 'cancelled'),
          'the provider answered the unknown status %r. The correction A1 '
          'knows PROVIDER_TERMINAL_TUPLE and the status cancelled only. %s'
          % (cancel_response['status'], fact_text))
      # Name the fact in the message, so a failed result holds the fact.
      self.assertEqual(
        2, len(self._provider_fact_list),
        'the method recorded %s facts. The facts are: %s'
        % (len(self._provider_fact_list), fact_text))
    finally:
      self._cancelRealResponseThatRuns(connector, response_id)

  def test_59_theReportTotalEqualsTheSumOfTheStoppedTokenLines(self):
    """The total of one report equals the sum of its stopped token lines.

    The script `ArtificialTaskReport_getTotalQuantity` adds one line when
    two conditions are true. The quantity unit is `unit/token`. The
    simulation state is `stopped`. The test builds four lines. Two lines
    match. Two lines do not match.

    PREDICTION before Step 7: the call raises AttributeError, because the
    skin script does not exist.
    """
    report, artificial_task, _ = self._buildLlmRequestFixture(
      'total_quantity')

    # Two lines that match. The sum of the two quantities is 300.0.
    first_line = self._newLine(report, 3, {'role': 'assistant'})
    first_line.edit(quantity=120.0, quantity_unit='unit/token')
    first_line.stop()
    second_line = self._newLine(report, 4, {'role': 'assistant'})
    second_line.edit(quantity=180.0, quantity_unit='unit/token')
    second_line.stop()

    # One line with the right unit that stays outside the state
    # `stopped`. The script must skip this line.
    draft_line = self._newLine(report, 5, {'role': 'assistant'})
    draft_line.edit(quantity=999.0, quantity_unit='unit/token')

    # One stopped line with another quantity unit. The script must skip
    # this line too.
    other_unit_line = self._newLine(report, 6, {'role': 'assistant'})
    other_unit_line.edit(quantity=500.0, quantity_unit='unit/piece')
    other_unit_line.stop()

    self.commit()
    self.tic()

    total = report.ArtificialTaskReport_getTotalQuantity()
    self.assertEqual(
      300.0, total,
      'the report answered the total %r. The test wrote 120.0 plus 180.0 '
      'in the state stopped with the unit unit/token, plus 999.0 in one '
      'draft line, plus 500.0 with another unit.' % (total, ))

    # The total of the Artificial Task adds the total of every related
    # report. This task holds one report only.
    task_total = artificial_task.ArtificialTask_getTotalQuantity()
    self.assertEqual(
      300.0, task_total,
      'the Artificial Task answered the total %r' % (task_total, ))

  def test_60_theTwoJumpActionsExistOnTheTwoPortalTypes(self):
    """The two jump actions exist with the expected reference and category.

    Step 8 adds one Action Information on `Artificial Task` and one
    Action Information on `Artificial Task Report`. The test reads the
    portal type objects. The test reads no document, so the test creates
    no document.

    PREDICTION before Step 8: both assertions fail. The two portal types
    hold the action `jump_query` only.
    """
    expected_list = [
      ('Artificial Task', 'jump_to_related_artificial_task_report',
       'Base_jumpToRelatedObject', 'Artificial+Task+Report'),
      ('Artificial Task Report', 'jump_to_artificial_task',
       'Base_jumpToRelationObject', 'Artificial+Task'),
    ]
    for row in expected_list:
      portal_type_id = row[0]
      action_id = row[1]
      script_id = row[2]
      target_portal_type = row[3]
      portal_type = self.portal.portal_types[portal_type_id]
      action = portal_type.get(action_id, None)
      self.assertNotEqual(
        None, action,
        'the portal type %s holds no action %s. The actions are: %s'
        % (portal_type_id, action_id, sorted(portal_type.objectIds())))
      self.assertEqual(
        action_id, action.getReference(),
        'the action %s of %s answers the reference %r'
        % (action_id, portal_type_id, action.getReference()))
      self.assertEqual(
        'object_jio_jump', action.getActionType(),
        'the action %s of %s answers the category %r. The expected '
        'category is object_jio_jump.'
        % (action_id, portal_type_id, action.getActionType()))
      action_text = str(action.getActionText())
      self.assertIn(
        script_id, action_text,
        'the action %s of %s does not call %s. The text is %r'
        % (action_id, portal_type_id, script_id, action_text))
      self.assertIn(
        'base_category=follow_up', action_text,
        'the action %s of %s does not name the base category follow_up. '
        'The text is %r' % (action_id, portal_type_id, action_text))
      self.assertIn(
        target_portal_type, action_text,
        'the action %s of %s does not name the portal type %s. The text '
        'is %r' % (action_id, portal_type_id, target_portal_type,
                   action_text))

  def test_61_theLineViewHoldsTheNewFieldsAndTheListboxSortsOnIntIndex(self):
    """The line view holds the new fields. The listbox sorts on int_index.

    Step 6 adds the fields to `ArtificialTaskReportLine_view`. Step 7
    changes the columns and the sort of the listbox of
    `ArtificialTaskReport_view`.

    The test also renders two new fields against one real line. That
    render proves that the TALES default holds one TALESMethod object,
    not one plain text. A plain text raises AttributeError there.

    PREDICTION before Step 6 and Step 7: the form holds `my_title` and
    `my_text_content` only, and the listbox sorts on `creation_date`.
    """
    skin_folder = self.portal.portal_skins['erp5_artificial_intelligence']

    line_form = skin_folder['ArtificialTaskReportLine_view']
    field_id_list = sorted(line_form.objectIds())
    expected_field_id_list = [
      'my_translated_simulation_state_title',
      'my_role',
      'my_causality_title',
      'my_resource_title',
      'my_connector_title',
      'my_quantity',
      'my_quantity_unit_title',
      'my_destination_reference',
    ]
    missing_field_id_list = [
      x for x in expected_field_id_list if x not in field_id_list]
    self.assertEqual(
      [], missing_field_id_list,
      'the form ArtificialTaskReportLine_view holds no %s. The form '
      'holds %s' % (missing_field_id_list, field_id_list))

    report_form = skin_folder['ArtificialTaskReport_view']
    self.assertIn(
      'my_total_quantity', sorted(report_form.objectIds()),
      'the form ArtificialTaskReport_view holds no my_total_quantity. '
      'The form holds %s' % (sorted(report_form.objectIds()), ))

    listbox = report_form['listbox']
    sort_list = [tuple(x) for x in listbox.get_value('sort')]
    self.assertEqual(
      [('int_index', 'ascending')], sort_list,
      'the listbox sorts on %r. Decision 7 asks for int_index ascending.'
      % (sort_list, ))

    column_id_list = [x[0] for x in listbox.get_value('columns')]
    expected_column_id_list = [
      'id', 'int_index', 'ArtificialTaskReportLine_getRole',
      'resource_title', 'connector_title', 'quantity',
      'quantity_unit_title', 'translated_simulation_state_title',
      'destination_reference',
    ]
    self.assertEqual(
      expected_column_id_list, column_id_list,
      'the listbox holds the columns %r' % (column_id_list, ))

    # `get_value('default')` evaluates the TALES of the field, as the render
    # does. Read the form through the line: `here` must be the line.
    report, _, _ = self._buildLlmRequestFixture(
      'field_render')
    line = self._newLine(report, 3, {'role': 'assistant'})
    line.edit(quantity=42.0, quantity_unit='unit/token')
    line.stop()
    self.commit()
    self.tic()

    rendered_form = getattr(line, 'ArtificialTaskReportLine_view')
    role_value = rendered_form['my_role'].get_value('default')
    self.assertEqual(
      'assistant', role_value,
      'the field my_role rendered %r. The line holds the role assistant.'
      % (role_value, ))

    quantity_value = rendered_form['my_quantity'].get_value('default')
    self.assertEqual(
      42.0, float(quantity_value),
      'the field my_quantity rendered %r' % (quantity_value, ))

    # The skin script that the listbox column calls must answer the role
    # too. The listbox calls the column name as one method of the row.
    self.assertEqual(
      'assistant', line.ArtificialTaskReportLine_getRole(),
      'the script ArtificialTaskReportLine_getRole answered %r'
      % (line.ArtificialTaskReportLine_getRole(), ))

  def test_62_theNextRequestLineCopiesTheLineNotTheTask(self):
    """The second request line of one round copies the first request line.

    `newRequestLine` calls
    `ArtificialTaskReportLine_writeRequestParameterList` with the parameter
    `source_line`. The script therefore reads the line that runs now. The
    script reads no value of the Artificial Task.

    The test proves the rule. The test writes one other model on the
    Artificial Task before the round. The second request line must still
    hold the model of the first request line.
    """
    first_response_identifier = self._buildProviderIdentifier('62_first')
    second_response_identifier = self._buildProviderIdentifier('62_second')
    report, artificial_task, request_line = self._buildLlmRequestFixture(
      'source_line_copy')

    first_model = request_line.getModel()
    self.assertTrue(
      first_model, 'the fixture wrote no model on the first request line')
    first_payload = json.loads(request_line.getTextContent())
    first_connector_value = request_line.getConnectorValue()
    first_resource_value = request_line.getResourceValue()

    # The Artificial Task now holds one other model. A read of the
    # Artificial Task therefore gives one value that the run never used.
    task_model = 'zzz-model-%s' % (self._run_identifier, )
    artificial_task.edit(model=task_model)
    self.commit()
    self.tic()
    self.assertEqual(task_model, artificial_task.getModel())
    self.assertEqual(first_model, request_line.getModel())

    # The allow list refuses the tool. The refusal is a tool answer, and the
    # round starts a second request line.
    tool_call = self._buildToolCall(
      'call_62_%s' % (self._run_identifier, ), None,
      tool_name=WRITE_TOOL_ID, argument_dict={})
    _, call_log = self._patchConnectorResponses([
      {'id': first_response_identifier, 'status': 'completed',
       'tool_calls': [tool_call],
       'usage': {'total_tokens': 11}},
      {'id': second_response_identifier, 'status': 'queued'},
    ])
    try:
      request_line.start()
      self.commit()
      self.tic()
      self._registerStartedLineList(report)
      self.assertEqual(
        2, len(call_log), 'createResponse ran %s times' % (len(call_log), ))
    finally:
      self._unpatchConnector()

    second_request_line_list = [
      x for x in self._getLineList(report)
      if self._getRole(x) == 'llm_request' and
      x.getRelativeUrl() != request_line.getRelativeUrl()]
    self.assertEqual(
      1, len(second_request_line_list),
      'the round created %s second request lines'
      % (len(second_request_line_list), ))
    second_request_line = second_request_line_list[0]
    second_payload = json.loads(second_request_line.getTextContent())

    # The connector of the second line is the connector of the first line.
    self.assertTrue(
      second_request_line.getConnectorValue() is not None,
      'the second request line holds no connector')
    self.assertEqual(
      first_connector_value.getRelativeUrl(),
      second_request_line.getConnectorValue().getRelativeUrl())

    # The model of the second line is the model of the first line. The
    # model of the Artificial Task never reaches the line.
    self.assertEqual(
      first_model, second_request_line.getModel(),
      'the second request line holds the model %r'
      % (second_request_line.getModel(), ))
    self.assertEqual(
      first_model, second_payload.get('model'),
      'the payload of the second request line holds the model %r'
      % (second_payload.get('model'), ))
    self.assertNotEqual(
      task_model, second_request_line.getModel(),
      'the second request line read the model of the Artificial Task')
    self.assertNotEqual(task_model, second_payload.get('model'))

    # The tool definitions of the second line are the tool definitions of
    # the first line.
    self.assertEqual(
      first_payload.get('tools'), second_payload.get('tools'),
      'the payload of the second request line holds the tools %r'
      % (second_payload.get('tools'), ))

    # The resource of the two lines is the same value. The test creates no
    # Service, so the test compares the two values.
    second_resource_value = second_request_line.getResourceValue()
    if first_resource_value is None:
      self.assertEqual(
        None, second_resource_value,
        'the first line holds no resource and the second line holds %r'
        % (second_resource_value, ))
    else:
      self.assertTrue(
        second_resource_value is not None,
        'the second request line holds no resource')
      self.assertEqual(
        first_resource_value.getRelativeUrl(),
        second_resource_value.getRelativeUrl())

    # A request line reads no provider. The line therefore holds the
    # quantity 0.
    self.assertEqual(
      0, second_request_line.getQuantity(),
      'the second request line holds the quantity %s'
      % (second_request_line.getQuantity(), ))
    self.assertEqual(
      'unit/token', second_request_line.getQuantityUnit(),
      'the second request line holds the quantity unit %s'
      % (second_request_line.getQuantityUnit(), ))

    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_75_theEventRepresentationHoldsNoFileAndBoundsTheText(self):
    """`Event_asLLMMessage` answers no file and cuts one long text.

    One Artificial Task Line holds the type class `Event`. The script
    therefore serves that portal type.

    The method writes one text that is longer than the bound. The answer
    must hold the head of that text, and the answer must not hold the tail.
    """
    self._getRepresentationScript(self.EVENT_REPRESENTATION_SCRIPT_ID)
    artificial_task = self._newArtificialTask(
      'Workflow send representation test %s' % (self._run_identifier, ))
    head_text = u'head %s' % (self._run_identifier, )
    tail_text = u'tail %s' % (self._run_identifier, )
    line_title = u'Title %s' % (self._run_identifier, )
    long_text = u'%s %s %s' % (
      head_text,
      u'a' * (self.MAXIMUM_REPRESENTATION_TEXT_LENGTH + 5000),
      tail_text)
    artificial_task_line = artificial_task.newContent(
      portal_type=self.ARTIFICIAL_TASK_LINE_PORTAL_TYPE,
      title=line_title,
      text_content=long_text)
    self.commit()
    self.tic()

    answer = artificial_task_line.Event_asLLMMessage()

    self.assertTrue(
      isinstance(answer, dict),
      'the script answered %r' % (str(answer)[:200], ))
    self.assertEqual('user', answer.get('role'))
    self.assertEqual(
      0, answer.get('is_file'),
      'the script answered is_file %r for one Artificial Task Line'
      % (answer.get('is_file'), ))
    self.assertEqual(None, answer.get('file_data'))
    text = self._toUnicodeText(answer.get('text'))
    self.assertIn(line_title, text)
    self.assertIn(head_text, text)
    self.assertNotIn(
      tail_text, text,
      'the script sent the whole text of the Artificial Task Line')
    self.assertIn(u'[the text is cut here]', text)
    self.assertTrue(
      len(text) < len(long_text),
      'the answer holds %s characters and the text holds %s characters'
      % (len(text), len(long_text)))
    self.assertTrue(
      len(text) <= self.MAXIMUM_REPRESENTATION_TEXT_LENGTH
      + len(line_title) + 200,
      'the answer holds %s characters. The bound is %s characters.'
      % (len(text), self.MAXIMUM_REPRESENTATION_TEXT_LENGTH))

  def test_77_aReportWithNoAggregateBuildsTheMessageListOfToday(self):
    """A report with no aggregate answers the unchanged message list.

    THIS IS THE REGRESSION TEST. The change of the Portable Document Format
    route must change no run that holds no aggregate.

    The method asserts the WHOLE message list, with one `assertEqual` on
    one list. A new message, one new key, or one other order therefore
    fails this method.
    """
    report = self._getReport('no_aggregate_regression')
    self.assertEqual(
      None, report.getFollowUpValue(portal_type='Artificial Task'),
      'the report holds one Artificial Task')

    first_question = 'question one %s' % (self._run_identifier, )
    second_question = 'question two %s' % (self._run_identifier, )
    answer_text = 'answer one %s' % (self._run_identifier, )
    tool_answer_text = 'the tool answer %s' % (self._run_identifier, )
    tool_call = self._buildToolCall(
      'call_77_%s' % (self._run_identifier, ), self.tool_reference)

    self._newLine(report, 1,
                  {'role': 'user', 'content': first_question}).stop()
    self._newLine(report, 2, {'role': 'assistant', 'content': answer_text,
                              'tool_calls': [tool_call]}).stop()
    self._newLine(report, 3, {'role': 'tool',
                              'tool_call_id': tool_call['id'],
                              'name': READ_ONLY_TOOL_ID,
                              'content': tool_answer_text}).stop()
    self._newLine(report, 4, {'role': 'llm_request'})
    self._newLine(report, 5,
                  {'role': 'user', 'content': second_question}).stop()
    self.commit()
    self.tic()

    message_list = report.ArtificialTaskReport_getMessageList()

    expected_list = [
      {'role': 'user', 'content': first_question},
      {'role': 'assistant', 'content': answer_text,
       'tool_calls': [tool_call]},
      {'role': 'tool', 'tool_call_id': tool_call['id'],
       'name': READ_ONLY_TOOL_ID, 'content': tool_answer_text},
      {'role': 'user', 'content': second_question},
    ]
    self.assertEqual(
      expected_list, message_list,
      'the message list of one report with no aggregate changed')
    self._assertNoPrivateMessageKey(
      message_list, 'one report with no aggregate')

  def test_80_createResponseUploadsOneTimeAndAddsTheFilePart(self):
    """`createResponse` uploads one file and writes the file part.

    The file part goes into the LAST `user` message. The `system` message
    receives no file part.

    The method stubs `_uploadFile`, `_deleteFile` and `_callResponsesApi`.
    The method therefore makes no network call.
    """
    self._skipWithoutConnectorFileMethodList()
    connector = self.portal.ArtificialTask_getDefaultConnector()
    connector_class = self._getConnectorClass()
    file_identifier = self._buildFileIdentifier('80')
    # WARNING: the name `self` inside the stubs below names the connector,
    # not the test. Read the run identifier here.
    run_identifier = self._run_identifier
    attachment_data = 'the binary of the run %s' % (self._run_identifier, )
    attachment_filename = 'scan_%s.pdf' % (self._run_identifier, )
    skill_text = 'the skill %s' % (self._run_identifier, )
    question_text = 'the question %s' % (self._run_identifier, )
    upload_log = []
    delete_log = []
    api_log = []

    def upload_stub(self, data, file_name, media_type, base_url, headers,
                    request_kw):
      upload_log.append((data, file_name, media_type))
      return file_identifier

    def delete_stub(self, one_file_id, headers, request_kw):
      delete_log.append(one_file_id)

    def responses_stub(self, chat_message_list, model, tools, tool_choice,
                       response_format, reasoning_effort, headers, timeout,
                       request_kw, prompt_cache_key=None, background=True,
                       file_id=None):
      api_log.append({'messages': chat_message_list, 'file_id': file_id})
      return {'id': 'stub_%s' % (run_identifier, ),
              'status': 'completed', 'is_done': True, 'content': '',
              'tool_calls': [], 'model': model, 'usage': {}, 'error': None,
              'file_id': file_id}

    system_message = {'role': 'system', 'content': skill_text}
    user_message = {'role': 'user', 'content': question_text}
    message_list = [system_message, user_message]

    self._patchClassMethodList(connector_class, {
      '_uploadFile': upload_stub,
      '_deleteFile': delete_stub,
      '_callResponsesApi': responses_stub,
    })
    try:
      answer = connector.createResponse(
        messages=message_list, model='gpt-4.1',
        attachment_data=attachment_data,
        attachment_filename=attachment_filename,
        attachment_media_type='application/pdf')
    finally:
      self._unpatchClassMethodList()

    self.assertEqual(
      1, len(upload_log),
      'the connector uploaded the file %s times' % (len(upload_log), ))
    self.assertEqual(attachment_data, upload_log[0][0])
    self.assertEqual(attachment_filename, upload_log[0][1])
    self.assertEqual('application/pdf', upload_log[0][2])
    self.assertEqual(file_identifier, answer.get('file_id'))

    self.assertEqual(1, len(api_log))
    self.assertEqual(file_identifier, api_log[0]['file_id'])
    sent_list = api_log[0]['messages']
    self.assertEqual(2, len(sent_list))
    # The `system` message receives no file part.
    self.assertEqual('system', sent_list[0]['role'])
    self.assertEqual(skill_text, sent_list[0]['content'])
    # The last `user` message holds the text part and the file part.
    self.assertEqual('user', sent_list[1]['role'])
    part_list = sent_list[1]['content']
    self.assertTrue(
      isinstance(part_list, list),
      'the content of the user message is %r' % (str(part_list)[:200], ))
    self.assertEqual({'type': 'text', 'text': question_text}, part_list[0])
    self.assertEqual(
      {'type': 'file', 'file': {'file_id': file_identifier}}, part_list[1])

    # The connector changed no message of the caller.
    self.assertEqual(question_text, user_message['content'])
    self.assertEqual([system_message, user_message], message_list)
    # The caller owns the file. The connector deletes no file here.
    self.assertEqual(
      [], delete_log,
      'the connector deleted the file inside createResponse')

  def test_81_createResponseWithOneFileIdentifierUploadsNoFile(self):
    """A call with `file_id` performs NO upload.

    This method protects the cost of the run. Round 2 to round 20 of one
    run must pay no second upload. The method counts the uploads, and the
    count must be 0.
    """
    self._skipWithoutConnectorFileMethodList()
    connector = self.portal.ArtificialTask_getDefaultConnector()
    connector_class = self._getConnectorClass()
    file_identifier = self._buildFileIdentifier('81')
    # WARNING: the name `self` inside the stubs below names the connector,
    # not the test. Read the run identifier here.
    run_identifier = self._run_identifier
    question_text = 'the question %s' % (self._run_identifier, )
    upload_log = []
    delete_log = []
    api_log = []

    def upload_stub(self, data, file_name, media_type, base_url, headers,
                    request_kw):
      upload_log.append((data, file_name, media_type))
      return 'file_that_no_call_must_build_%s' % (run_identifier, )

    def delete_stub(self, one_file_id, headers, request_kw):
      delete_log.append(one_file_id)

    def responses_stub(self, chat_message_list, model, tools, tool_choice,
                       response_format, reasoning_effort, headers, timeout,
                       request_kw, prompt_cache_key=None, background=True,
                       file_id=None):
      api_log.append({'messages': chat_message_list, 'file_id': file_id})
      return {'id': 'stub_%s' % (run_identifier, ),
              'status': 'completed', 'is_done': True, 'content': '',
              'tool_calls': [], 'model': model, 'usage': {}, 'error': None,
              'file_id': file_id}

    message_list = [{'role': 'user', 'content': question_text}]

    self._patchClassMethodList(connector_class, {
      '_uploadFile': upload_stub,
      '_deleteFile': delete_stub,
      '_callResponsesApi': responses_stub,
    })
    try:
      answer = connector.createResponse(
        messages=message_list, model='gpt-4.1',
        file_id=file_identifier)
    finally:
      self._unpatchClassMethodList()

    self.assertEqual(
      [], upload_log,
      'the connector uploaded %s files for one call that holds one file '
      'identifier' % (len(upload_log), ))
    self.assertEqual(file_identifier, answer.get('file_id'))
    self.assertEqual(1, len(api_log))
    self.assertEqual(file_identifier, api_log[0]['file_id'])
    part_list = api_log[0]['messages'][0]['content']
    self.assertEqual(
      {'type': 'file', 'file': {'file_id': file_identifier}}, part_list[1])
    # WARNING: the caller owns this file. The connector must delete no file
    # of the caller.
    self.assertEqual(
      [], delete_log,
      'the connector deleted the file of the caller')

  def test_83_theFileIsRemovedAtTheEndOfTheRunOnly(self):
    """`removeFile` runs one time, and runs at the terminal line.

    Phase A drives one run that stays open. `removeFile` must run no time.
    A file that goes away in the middle of one run breaks round 2.

    Phase B drives one run to the end. `removeFile` must run one time, with
    the file identifier of that run.
    """
    self._skipWithoutConnectorFileMethodList()
    connector_class = self._getConnectorClass()
    open_file_identifier = self._buildFileIdentifier('83_open')
    end_file_identifier = self._buildFileIdentifier('83_end')
    remove_log = []

    def remove_stub(self, file_id, cert=None, verify=None):
      remove_log.append(file_id)
      return True

    self._patchClassMethodList(connector_class, {'removeFile': remove_stub})
    try:
      # Phase A. The run stays open.
      open_report, _, open_line = self._buildLlmRequestFixture(
        'file_open_run')
      open_tool_call = self._buildToolCall(
        'call_83_%s' % (self._run_identifier, ), None,
        tool_name=WRITE_TOOL_ID, argument_dict={})
      _, open_call_log = self._patchConnectorResponses([
        {'id': self._buildProviderIdentifier('83_open_first'),
         'status': 'completed', 'tool_calls': [open_tool_call],
         'file_id': open_file_identifier, 'usage': {'total_tokens': 5}},
        {'id': self._buildProviderIdentifier('83_open_second'),
         'status': 'queued'},
      ])
      try:
        open_line.start()
        self.commit()
        self.tic()
        self._registerStartedLineList(open_report)
      finally:
        self._unpatchConnector()

      self.assertEqual(
        2, len(open_call_log),
        'createResponse ran %s times in phase A' % (len(open_call_log), ))
      self.assertEqual(
        [], remove_log,
        'the script removed the file while the run was open')

      # Phase B. The run ends with the last answer.
      _, end_task, end_line = self._buildLlmRequestFixture(
        'file_end_run')
      _, end_call_log = self._patchConnectorResponses([
        {'id': self._buildProviderIdentifier('83_end'),
         'status': 'completed', 'tool_calls': [],
         'content': 'the final answer %s' % (self._run_identifier, ),
         'file_id': end_file_identifier},
      ])
      try:
        end_line.start()
        self.commit()
        self.tic()
      finally:
        self._unpatchConnector()
    finally:
      self._unpatchClassMethodList()

    self.assertEqual(
      1, len(end_call_log),
      'createResponse ran %s times in phase B' % (len(end_call_log), ))
    self.assertEqual(
      'responded', end_task.getSimulationState(),
      'the run of phase B did not end')
    self.assertEqual(
      [end_file_identifier], remove_log,
      'the script called removeFile with %s' % (remove_log, ))
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_84_aRunWithNoAggregateCallsTheConnectorWithNoAttachment(self):
    """A run with no aggregate calls `createResponse` with no attachment.

    The call holds no `attachment_data`, no `attachment_filename`, no
    `attachment_media_type` and no `file_id`.
    """
    response_identifier = self._buildProviderIdentifier('84')
    _, artificial_task, request_line = self._buildLlmRequestFixture(
      'no_attachment')
    aggregate_value = None
    try:
      aggregate_value = artificial_task.getAggregateValue()
    except Exception:
      # The portal type holds no base category `aggregate` yet. The run
      # then holds no aggregate too.
      aggregate_value = None
    self.assertEqual(
      None, aggregate_value,
      'the Artificial Task of the fixture holds one aggregate')

    _, call_log = self._patchConnectorResponses([
      {'id': response_identifier, 'status': 'completed',
       'content': 'the final answer %s' % (self._run_identifier, ),
       'tool_calls': []},
    ])
    try:
      request_line.start()
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    self.assertEqual(
      1, len(call_log), 'createResponse ran %s times' % (len(call_log), ))
    for absent_key in ('attachment_data', 'attachment_filename',
                       'attachment_media_type', 'file_id'):
      self.assertTrue(
        absent_key not in call_log[0],
        'the call of one run with no aggregate holds the key %s'
        % (absent_key, ))
    self._assertNoPrivateMessageKey(
      call_log[0].get('messages') or [], 'one run with no aggregate')
    self.assertEqual('responded', artificial_task.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())

  def test_85_theCancelPathPassesTheFileIdentifierToTheProvider(self):
    """One user cancel gives `file_id` to `cancelResponse`.

    One cancel is terminal, so the connector deletes the file of that run.

    WARNING: the method skips itself when
    `ArtificialTaskReportLine_checkResponse` passes no `file_id`.
    """
    script = self._getRepresentationScript(CHECK_METHOD_ID)
    compact_source = ''.join(script.body().split())
    if 'cancelResponse(response_id,file_id' not in compact_source:
      self.skipTest(
        'the script %s passes no file_id to cancelResponse. That change '
        'is not deployed. Deploy that change, then run this method again.'
        % (CHECK_METHOD_ID, ))

    file_identifier = self._buildFileIdentifier('85')
    response_identifier = self._buildProviderIdentifier('85')
    _, _, request_line = self._buildLlmRequestFixture(
      'cancel_file')

    self._patchConnectorResponses(
      [{'id': response_identifier, 'status': 'queued',
        'file_id': file_identifier}],
      cancel_response_dict={
        response_identifier: self._buildResponse(
          id=response_identifier, status='cancelled',
          usage={'prompt_tokens': 0, 'completion_tokens': 0,
                 'total_tokens': 0, 'cached_tokens': 0}),
      })
    try:
      request_line.start()
      self.commit()
      self.tic()
      self.assertEqual(
        response_identifier, request_line.getDestinationReference())
      parameter_dict = json.loads(request_line.getRequestParameter() or '{}')
      self.assertEqual(
        file_identifier, parameter_dict.get('file_id'),
        'the line holds the file identifier %r'
        % (parameter_dict.get('file_id'), ))

      request_line.cancelRequest(
        comment=u'The user stopped this run %s.' % (self._run_identifier, ))
      self.commit()
      self.tic()
    finally:
      self._unpatchConnector()

    own_cancel_list = [
      x for x in self._cancel_call_log if x[0] == response_identifier]
    self.assertEqual(
      1, len(own_cancel_list),
      'the script cancelled this identifier %s times'
      % (len(own_cancel_list), ))
    self.assertEqual(
      file_identifier, own_cancel_list[0][1].get('file_id'),
      'the cancel carried the file identifier %r'
      % (own_cancel_list[0][1].get('file_id'), ))
    self.assertEqual('stopped', request_line.getSimulationState())
    self.assertEqual([], self._getPermanentlyFailedMessageList())