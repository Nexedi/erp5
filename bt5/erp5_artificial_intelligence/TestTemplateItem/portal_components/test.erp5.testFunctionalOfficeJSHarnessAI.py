import unittest

from Products.ERP5Type.tests.ERP5TypeFunctionalTestCase import ERP5TypeFunctionalTestCase


class TestFunctionalOfficeJSHarnessAI(ERP5TypeFunctionalTestCase):
  foreground = 0
  run_only = "officejs_harness_ai_ui_zuite"

  def getBusinessTemplateList(self):
    return (
        'erp5_artificial_intelligence',
        'erp5_officejs',
        'erp5_web_renderjs_ui_test',
        'erp5_ui_test_core',
    )


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(
      unittest.defaultTestLoader.loadTestsFromTestCase(TestFunctionalOfficeJSHarnessAI))
  return suite
