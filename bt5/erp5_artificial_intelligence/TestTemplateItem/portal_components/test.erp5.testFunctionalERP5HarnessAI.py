import unittest

from Products.ERP5Type.tests.ERP5TypeFunctionalTestCase import ERP5TypeFunctionalTestCase

# Same title as in ERP5Site_setupHarnessAITestFixture, which reuses the
# connector found with it.
FIXTURE_CONNECTOR_TITLE = 'Zelenium Fixture Harness AI Connector'


class TestFunctionalERP5HarnessAI(ERP5TypeFunctionalTestCase):
  foreground = 0
  run_only = "erp5_harness_ai_ui_zuite"

  def getBusinessTemplateList(self):
    return (
        'erp5_artificial_intelligence',
        'erp5_interface_openai',
        'erp5_web_renderjs_ui_test',
        'erp5_ui_test_core',
    )

  def afterSetUp(self):
    super(TestFunctionalERP5HarnessAI, self).afterSetUp()
    # On the test nodes, the browser reaches the portal through an https
    # frontend whose certificate python requests does not trust: the
    # connector of the fixture, called by the agent on the server side, uses
    # the URL of the portal in this test instead, the http server of the test.
    url_string = self.portal.absolute_url() + '/ERP5Site_fakeOpenaiResponses'
    connector = self.portal.portal_catalog.getResultValue(
        portal_type='Openai Connector', title=FIXTURE_CONNECTOR_TITLE)
    if connector is None:
      self.portal.portal_web_services.newContent(
          portal_type='Openai Connector',
          title=FIXTURE_CONNECTOR_TITLE,
          url_string=url_string,
          password='test-api-key',
      )
    else:
      connector.setUrlString(url_string)
    self.tic()


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(
      unittest.defaultTestLoader.loadTestsFromTestCase(TestFunctionalERP5HarnessAI))
  return suite
