"""
Idempotent test fixture provisioning for the erp5_harness_ai (native ERP5 UI)
Zelenium suite (testERP5HarnessAI*.zpt). Called via a plain `open`/`openAndWait`
from a test's Zuite_CommonTemplateForErp5HarnessAI/macros/open_fixture_task
macro - same idiom as Zuite_waitForActivities/Alarm_launchRecordAlarm.

Find-or-creates (by a fixed title, so repeated calls across test files in the
same suite run reuse the same fixture documents instead of piling up new
ones) an Openai Connector pointed at ERP5Site_fakeOpenaiResponses and an
Artificial Agent using it, mirroring _makeArtificialAgent/afterSetUp in
test.erp5.TestArtificialIntelligence.py - but as real, committed business
documents instead of a monkey-patched Python object, since Zelenium drives a
real, separately-running instance over HTTP rather than a single
ERP5TypeTestCase process.

Always creates a brand-new Artificial Task against that fixture agent (one
fresh document per Zelenium `open` of this script, same "fresh document per
test" choice TestArtificialIntelligence.py makes per test method), confirms
it (draft -> confirmed, matching _makeConfirmedArtificialTask) and returns
its relative URL as the plain-text response body, so the calling Selenese
can storeEval it and `open` the task's native view page directly.

The task is left in "confirmed", not "started": the Zelenium test's own
first postComment through the browser is what should exercise the real
confirmed -> start() transition in ArtificialTask_createCommentLine.py,
rather than pre-starting it here.
"""
import json
import time

FIXTURE_CONNECTOR_TITLE = 'Zelenium Fixture Harness AI Connector'
FIXTURE_AGENT_TITLE = 'Zelenium Fixture Harness AI Agent'
FIXTURE_TOOL_ID = 'fake_tool'
FIXTURE_TOOL_DESCRIPTION = json.dumps({
    'type': 'function',
    'name': FIXTURE_TOOL_ID,
    'description': 'Create an iPhone invoice for a given quantity.',
    'parameters': {
        'type': 'object',
        'properties': {'quantity': {'type': 'number'}},
        'required': ['quantity'],
    },
})

portal = context.getPortalObject()
portal_url = portal.absolute_url()

connector = portal.portal_catalog.getResultValue(
    portal_type='Openai Connector', title=FIXTURE_CONNECTOR_TITLE)
if connector is None:
  connector = portal.portal_web_services.newContent(
      portal_type='Openai Connector',
      title=FIXTURE_CONNECTOR_TITLE,
      url_string=portal_url + '/ERP5Site_fakeOpenaiResponses',
      password='test-api-key',
  )

if FIXTURE_TOOL_ID not in portal.portal_callables.objectIds():
  portal.portal_callables.newContent(
      portal_type='Python Script', id=FIXTURE_TOOL_ID)
  portal.portal_callables.fake_tool.ZPythonScript_edit(
      'quantity', "return 'iPhone invoice created: quantity=%s' % quantity")
  portal.portal_callables.fake_tool.setDescription(FIXTURE_TOOL_DESCRIPTION)

agent = portal.portal_catalog.getResultValue(
    portal_type='Artificial Agent', title=FIXTURE_AGENT_TITLE)
if agent is None:
  agent = portal.artificial_agent_module.newContent(
      portal_type='Artificial Agent',
      title=FIXTURE_AGENT_TITLE,
  )
  agent.setModel('test-model')
  agent.setToolList([FIXTURE_TOOL_ID])
  agent.setSkillList([])
  agent.setConnectorValue(connector)

task = portal.artificial_task_module.newContent(
    portal_type='Artificial Task',
    title='Zelenium Harness AI Task %s' % time.time(),
)
task.setDestinationValue(agent)
task.confirm()

request = context.REQUEST
request.RESPONSE.setHeader('Content-Type', 'text/plain')
return task.getRelativeUrl()
