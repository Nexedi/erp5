##############################################################################
#
# Copyright (c) 2026 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import json

import transaction
from functools import wraps
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript


def simulate(script_id, params_string, code_string):
  """Temporarily override a skin script by creating one of the same id in
  portal_skins/custom, for the duration of the decorated test method.
  """
  def upperWrap(f):
    @wraps(f)
    def decorated(self, *args, **kw):
      if script_id in self.portal.portal_skins.custom.objectIds():
        raise ValueError('Precondition failed: %s exists in custom' % script_id)
      createZODBPythonScript(self.portal.portal_skins.custom,
                          script_id, params_string, code_string)
      transaction.commit()
      try:
        result = f(self, *args, **kw)
      finally:
        transaction.abort()
        if script_id in self.portal.portal_skins.custom.objectIds():
          self.portal.portal_skins.custom.manage_delObjects(script_id)
        transaction.commit()
      return result
    return decorated
  return upperWrap


class FakeOpenaiConnector(object):
  """
  Stands in for the Openai Connector, so these tests exercise
  ArtificialTask_runHarnessAgent's own control flow - the tool-call loop,
  the finalize step, the loop-count guard - without any real network or LLM
  dependency. Responses are returned in call order.
  """

  def __init__(self, response_list):
    self._response_list = list(response_list)
    self.call_list = []

  def createResponse(self, **kw):
    self.call_list.append(kw)
    return self._response_list.pop(0)


class TestArtificialIntelligence(ERP5TypeTestCase):

  def getTitle(self):
    return "Artificial Task Harness Agent"

  def afterSetUp(self):
    if 'fake_tool' not in self.portal.portal_callables.objectIds():
      self.portal.portal_callables.newContent(
          portal_type='Python Script', id='fake_tool')
      self.portal.portal_callables.fake_tool.ZPythonScript_edit(
          'quantity', "return 'iPhone invoice created: quantity=%s' % quantity")

  def _makeArtificialAgent(self, response_list=()):
    agent = self.portal.artificial_agent_module.newContent(
        portal_type='Artificial Agent',
        title='Test Agent %s' % self.id(),
    )
    agent.setModel('test-model')
    agent.setToolList([])
    agent.setSkillList([])
    fake_connector = FakeOpenaiConnector(response_list)
    connector = self.portal.portal_web_services.newContent(
        portal_type='Openai Connector',
        title='Test Connector %s' % self.id(),
    )
    connector.createResponse = fake_connector.createResponse
    connector.call_list = fake_connector.call_list
    agent.setConnectorValue(connector)
    return agent

  def _makeStartedArtificialTask(self, agent):
    task = self.portal.artificial_task_module.newContent(
        portal_type='Artificial Task',
        title='Test Task %s' % self.id(),
    )
    task.setDestinationValue(agent)
    task.confirm()
    task.start()
    return task

  def _makeConfirmedArtificialTask(self, agent):
    task = self.portal.artificial_task_module.newContent(
        portal_type='Artificial Task',
        title='Test Task %s' % self.id(),
    )
    task.setDestinationValue(agent)
    task.confirm()
    return task

  def _makePerson(self):
    person = self.portal.person_module.newContent(
        portal_type='Person',
        title='Test Person %s' % self.id(),
    )
    assignment = person.newContent(portal_type='Assignment')
    assignment.open()
    reference = 'test_person_%s' % self.id().replace('.', '_')
    person.newContent(portal_type='ERP5 Login', reference=reference).validate()
    self.tic()
    self.portal.acl_users.zodb_roles.assignRoleToPrincipal(
        'Manager', person.getUserId())
    self.login(person.getUserId())
    return person

  def test_01_LoopLimitFinalizesWithApologyWithoutCallingTheLLM(self):
    agent = self._makeArtificialAgent(response_list=[])
    task = self._makeStartedArtificialTask(agent)

    task.ArtificialTask_runHarnessAgent(
        request_object_relative_url=task.getRelativeUrl(),
        loop_count=50,
    )
    self.tic()

    self.assertEqual([], agent.getConnectorValue().call_list)
    self.assertEqual('stopped', task.getSimulationState())

    line_list = task.objectValues(portal_type='Artificial Task Line')
    self.assertEqual(1, len(line_list))
    self.assertIn('could not finish', line_list[0].getTextContent())

  def test_02_NoToolCallsFinalizesImmediately(self):
    agent = self._makeArtificialAgent(response_list=[
        {'content': 'Hello, how can I help you today?', 'tool_calls': []},
    ])
    task = self._makeStartedArtificialTask(agent)
    self.tic()
    self.assertEqual(1, len(agent.getConnectorValue().call_list))
    self.assertEqual('stopped', task.getSimulationState())

    line_list = task.objectValues(portal_type='Artificial Task Line')
    self.assertEqual(1, len(line_list))
    self.assertEqual(
        'Hello, how can I help you today?',
        line_list[0].getTextContent())
    self.assertEqual('delivered', line_list[0].getSimulationState())

  def test_03_ToolCallRoundTripFinalizesWithFinalAnswer(self):
    agent = self._makeArtificialAgent(response_list=[
        {
            'content': None,
            'tool_calls': [{
                'id': 'call_1',
                'function': {
                    'name': 'fake_tool',
                    'arguments': '{"quantity": 10}',
                },
            }],
        },
        {
            'content': 'Done! Created the invoice for 10 iPhones.',
            'tool_calls': [],
        },
    ])
    task = self._makeStartedArtificialTask(agent)
    self.tic()

    connector = agent.getConnectorValue()
    self.assertEqual(2, len(connector.call_list))
    self.assertEqual('stopped', task.getSimulationState())

    line_list = task.objectValues(portal_type='Artificial Task Line')
    self.assertEqual(1, len(line_list))
    self.assertEqual(
        'Done! Created the invoice for 10 iPhones.',
        line_list[0].getTextContent())

    report = task.getFollowUpRelatedValue(portal_type='Artificial Task Report')
    self.assertIsNotNone(report)
    report_line, = report.objectValues(portal_type='Artificial Task Report Line')
    message_list = json.loads(report_line.getTextContent())
    tool_message_list = [m for m in message_list if m.get('role') == 'tool']
    self.assertEqual(1, len(tool_message_list))
    self.assertEqual('call_1', tool_message_list[0]['tool_call_id'])
    self.assertEqual('fake_tool', tool_message_list[0]['name'])
    self.assertIn('iPhone invoice created', tool_message_list[0]['content'])

  def test_04_ConfirmingDoesNotRunButStartingRunsTheHarnessAgentThroughTheAlarm(self):
    agent = self._makeArtificialAgent(response_list=[
        {'content': 'Hi there!', 'tool_calls': []},
    ])
    task = self._makeConfirmedArtificialTask(agent)
    self.tic()

    self.assertEqual([], agent.getConnectorValue().call_list)
    self.assertEqual('confirmed', task.getSimulationState())

    task.start()
    self.tic()

    self.assertEqual(1, len(agent.getConnectorValue().call_list))
    self.assertEqual('stopped', task.getSimulationState())
    line_list = task.objectValues(portal_type='Artificial Task Line')
    self.assertEqual(1, len(line_list))
    self.assertEqual('Hi there!', line_list[0].getTextContent())

  def test_05_RestartingStoppedTaskRunsHarnessAgentAgainThroughTheAlarm(self):
    agent = self._makeArtificialAgent(response_list=[
        {'content': 'First answer', 'tool_calls': []},
        {'content': 'Second answer', 'tool_calls': []},
    ])
    task = self._makeConfirmedArtificialTask(agent)
    task.start()
    self.tic()

    task.restart()
    self.tic()

    self.assertEqual(2, len(agent.getConnectorValue().call_list))
    self.assertEqual('stopped', task.getSimulationState())
    line_list = task.objectValues(portal_type='Artificial Task Line')
    self.assertEqual(2, len(line_list))

  def test_06_CreatingArtificialTaskAddsAuthenticatedPersonAsContributor(self):
    person = self._makePerson()

    task = self.portal.artificial_task_module.newContent(
        portal_type='Artificial Task',
        title='Test Task %s' % self.id(),
    )

    self.assertIn(person, task.getContributorValueList())

  def test_07_EditingArtificialTaskDoesNotDuplicateExistingContributor(self):
    person = self._makePerson()
    task = self.portal.artificial_task_module.newContent(
        portal_type='Artificial Task',
        title='Test Task %s' % self.id(),
    )

    task.setDescription('edited once more')

    self.assertEqual([person], task.getContributorValueList())

  def test_08_CreatingArtificialTaskLineAddsAuthenticatedPersonAsSource(self):
    task = self.portal.artificial_task_module.newContent(
        portal_type='Artificial Task',
        title='Test Task %s' % self.id(),
    )
    person = self._makePerson()

    line = task.newContent(portal_type='Artificial Task Line', text_content='Hello')

    self.assertIn(person, line.getSourceValueList())

  def test_09_StartNewArtificialTaskWithoutDefaultAgentStaysDraft(self):
    artificial_task_module = self.portal.artificial_task_module

    artificial_task_module.ArtificialTaskModule_startNewArtificialTask(
        data='Please help me with something', file=None)
    self.tic()

    task = self.portal.portal_catalog.getResultValue(
        portal_type='Artificial Task', sort_on=(('creation_date', 'DESC'),))

    self.assertIsNone(task.getDestinationValue(portal_type='Artificial Agent'))
    self.assertEqual('draft', task.getSimulationState())
    line_list = task.objectValues(portal_type='Artificial Task Line')
    self.assertEqual(1, len(line_list))
    self.assertEqual('Please help me with something', line_list[0].getTextContent())

  @simulate(
      'ERP5Site_getDefaultArtificialAgent', '*args, **kwargs',
      "return context.getPortalObject().portal_catalog.getResultValue("
      "portal_type='Artificial Agent', sort_on=(('creation_date', 'DESC'),))")
  def test_10_StartNewArtificialTaskWithDefaultAgentRunsHarnessAgentThroughTheAlarm(self):
    agent = self._makeArtificialAgent(response_list=[
        {'content': 'Hi, how can I help?', 'tool_calls': []},
    ])
    self.tic()

    self.portal.artificial_task_module.ArtificialTaskModule_startNewArtificialTask(
        data='Please help me with something', file=None)
    self.tic()

    task = self.portal.portal_catalog.getResultValue(
        portal_type='Artificial Task', sort_on=(('creation_date', 'DESC'),))

    self.assertEqual(
        agent.getRelativeUrl(),
        task.getDestinationValue(portal_type='Artificial Agent').getRelativeUrl())
    self.assertEqual('stopped', task.getSimulationState())
    self.assertEqual(1, len(agent.getConnectorValue().call_list))

    line_list = task.objectValues(
        portal_type='Artificial Task Line', sort_on=[('creation_date', 'ascending')])
    self.assertEqual(2, len(line_list))
    self.assertEqual('Please help me with something', line_list[0].getTextContent())
    self.assertEqual('Hi, how can I help?', line_list[1].getTextContent())
