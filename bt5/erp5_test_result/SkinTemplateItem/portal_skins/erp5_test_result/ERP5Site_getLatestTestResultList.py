"""
  Return list of latest test results.
"""
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery

# XXX: move comments to Test Suite description and add a relation (category) from
# Test Result -> Test Suite
# source: http://community.slapos.org/unit_test
test_suite_list= [
                  # unit tests of ERP5
                  "ERP5-Master",

                  # unit tests of Wendelin
                  "WENDELIN-MASTER-DEV",

                  # deployment tests
                  "SLAPOS-DEPLOY-erp5-standalone-stretch",
                  "SLAPOS-DEPLOY-wendelin-master-standalone-stretch",
                  "SLAPOS-DEPLOY-slapos-master-standalone-stretch",
                  "SLAPOS-DEPLOY-erp5-standalone-centos74",
                  "SLAPOS-DEPLOY-slapos-master-standalone-jessie",
                  "SLAPOS-DEPLOY-wendelin-standalone-jessie",

                  # XXX: scalability tests
                  "IVAN-WENDELIN-SCALABILITY-TEST-COMP2732-LATESTNODE-1",

                  # NEO
                  "NEO-Master",

                  # Cloudoo
                  "CLOUDOOO-MASTER",

                  # performance tests
                  "PERF-ERP5-MASTER",

                  # javascript
                  "JIO-MASTER",
                  "JIO-MASTER-NODE",
                  "RENDERJS-MASTER",
                  "P-OJS.Appstore-master",

                  # SlapOS
                  "SLAPOS-MASTER-MASTER",
                  "SLAPOS-WR-UNITTEST",
                  "SLAPOS-RESILIENCE-WR-MASTER",
                  "SLAPOS-RESILIENCE-WR-ERP5-MASTER",
                  "SLAPOS-SR-TEST",
                  "SLAPOS-SR-TEST-MASTER",
                  "SLAPOS-EGG-TEST",
                  "SLAPOS-RESILIENCE-KVM-MASTER",
                  "SLAPOS-RESILIENCE-WR-GITLAB-MASTER",
                  "SLAPOS-SR-TEST-1.0",
                  ]
test_result_list = []
for test_suite in test_suite_list:
  test_query = ComplexQuery(
                  SimpleQuery(portal_type = "Test Result"),
                  SimpleQuery(title = test_suite),
                  SimpleQuery(simulation_state = ["stopped", "failed", "public_stopped"]),
                  logical_operator='and')

  test_result = context.portal_catalog.getResultValue(
                          query = test_query,
                          #group_by_list = ('title',), # XXX: try to reduce queries from N to 1
                          sort_on=(('creation_date', 'DESC'),))
                        
  if test_result is not None:
    test_result_list.append(test_result)

return test_result_list
