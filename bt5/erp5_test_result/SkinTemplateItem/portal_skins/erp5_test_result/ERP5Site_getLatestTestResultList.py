"""
  Return list of latest test results.
"""
from Products.ERP5Type.Document import newTempBase

test_suite_list= [
                  # unit tests of ERP5
                  {"title": "ERP5-Master",
                   "description": "Test ERP5's master branch code.",
                   "repository-url": "https://lab.nexedi.com/nexedi/erp5"},

                  # unit tests of Wendelin
                  {"title":"WENDELIN-MASTER-DEV",
                   "description": "Test Wendelin's master branch code.",
                   "repository-url": "https://lab.nexedi.com/nexedi/wendelin"},                  

                  # deployment tests
                  {"title": "SLAPOS-DEPLOY-erp5-standalone-stretch",
                   "description": "Test deploying Wendelin inside Debian stretch release OS.",
                   "repository-url": "https://lab.nexedi.com/nexedi/erp5"}, 

                  {"title": "SLAPOS-DEPLOY-wendelin-master-standalone-stretch",
                   "description": "Test deploying Wendelin inside Debian stretch release OS.",
                   "repository-url": "https://lab.nexedi.com/nexedi/wendelin"},                  

                  # XXX: scalability tests
                  {"title": "IVAN-WENDELIN-SCALABILITY-TEST-COMP2732-LATESTNODE-1",
                   "description": "Test Wendelin's scalability.",
                   "repository-url": "https://lab.nexedi.com/nexedi/wendelin"},
               								
                  # XXX: webrunner tests
                  # XXX: slapos master tests
                  ]

for test_suite in test_suite_list:
  test_title = test_suite["title"]
  test_result = context.portal_catalog.getResultValue(
                  portal_type = "Test Result",
                  simulation_state = ["stopped", "failed"],
                  sort_on=(('creation_date', 'ascending'))
                 )
  if test_result is not None:
    context.log(test_result)
    test_suite["result"] = test_result.getTranslatedSimulationStateTitle()
    test_suite["start_date"] = test_result.getStartDate()
    test_suite["stop_date"] = test_result.getStopDate()
    test_suite["reference"] = test_result.getReference()
    test_suite["test_result"] = test_result.getStringIndex()
    for key in ("all_tests", "failures", "errors", "skips"):
      test_suite[key] = getattr(test_result, key, None)

portal = context.getPortalObject()
return [newTempBase(portal, 
                    x['title'], 
                    **x) for x in test_suite_list]
