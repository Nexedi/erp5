from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from zLOG import LOG,INFO,ERROR 
import json 
from Products.ERP5Type.Log import log

class TestTaskDistribution(ERP5TypeTestCase):

  def getBusinessTemplateList(self):
    return ("erp5_base",
            "erp5_test_result")

  def afterSetUp(self):
    self.portal = portal = self.getPortalObject()
    self.test_node_module = self.portal.getDefaultModule(portal_type = 'Test Node Module')
    self.test_suite_module = self.portal.getDefaultModule(portal_type = 'Test Suite Module')
    self.test_result_module = self.portal.getDefaultModule(portal_type = 'Test Result Module')
    self.test_suite = self.portal.getDefaultModule(portal_type = 'Test Suite')
    self.tool = tool = self.portal.portal_task_distribution
    if getattr(tool, "TestTaskDistribution", None) is None:
      tool.newContent(id="TestTaskDistribution",
           portal_type="ERP5 Project Unit Test Distributor")
    if getattr(tool, "TestPerformanceTaskDistribution", None) is None:
      tool.newContent(id="TestPerformanceTaskDistribution",
           portal_type="Cloud Performance Unit Test Distributor")
    if getattr(tool, "TestScalabilityTaskDistribution", None) is None:
      tool.newContent(id="TestScalabilityTaskDistribution",
           portal_type="ERP5 Scalability Distributor")
    self.distributor = tool.TestTaskDistribution
    self.performance_distributor = tool.TestPerformanceTaskDistribution
    self.scalability_distributor = tool.TestScalabilityTaskDistribution
    if getattr(portal, "test_test_node_module", None) is None:
      portal.newContent(portal_type="Test Node Module",
                        id="test_test_node_module")
    if getattr(portal, "test_test_suite_module", None) is None:
      portal.newContent(portal_type="Test Suite Module",
                        id="test_test_suite_module")
    self.test_suite_module = portal.test_test_suite_module
    self.test_node_module = portal.test_test_node_module
    self.test_suite_module.manage_delObjects(ids=[
      x for x in self.test_suite_module.objectIds()])
    self.test_node_module.manage_delObjects(ids=[
      x for x in self.test_node_module.objectIds()])

    original_class = self.distributor.__class__
    original_scalability_class = self.scalability_distributor.__class__
    original_performance_class = self.performance_distributor.__class__

    self._original_getTestNodeModule = original_class._getTestNodeModule
    def _getTestNodeModule(self):
      return self.getPortalObject().test_test_node_module
    original_class._getTestNodeModule = _getTestNodeModule
    original_scalability_class._getTestNodeModule = _getTestNodeModule
    original_performance_class._getTestNodeModule = _getTestNodeModule

    self._original_getTestSuiteModule = original_class._getTestSuiteModule
    def _getTestSuiteModule(self):
      return self.getPortalObject().test_test_suite_module
    original_class._getTestSuiteModule = _getTestSuiteModule
    original_scalability_class._getTestSuiteModule = _getTestSuiteModule
    original_performance_class._getTestSuiteModule = _getTestSuiteModule

    self._cleanupTestResult()

  def beforeTearDown(self):
    original_class = self.distributor.__class__
    original_scalability_class = self.scalability_distributor.__class__
    original_performance_class = self.performance_distributor.__class__
    
    original_class._getTestNodeModule = self._original_getTestNodeModule
    original_class._getTestSuiteModule = self._original_getTestSuiteModule
    original_scalability_class._getTestNodeModule = self._original_getTestNodeModule
    original_scalability_class._getTestSuiteModule = self._original_getTestSuiteModule
    original_performance_class._getTestNodeModule = self._original_getTestNodeModule
    original_performance_class._getTestSuiteModule = self._original_getTestSuiteModule



  def _createTestNode(self, quantity=1, reference_correction=0,
                      specialise_value=None):
    if specialise_value is None:
      specialise_value = self.distributor
    test_node_list = []
    for i in range(quantity):
      test_node = self.test_node_module.newContent(
        title = 'UnitTestNode %i' % (i + 1 + reference_correction),
        test_suite_max = 4,
        specialise_value = specialise_value,
        )
      test_node_list.append(test_node)
    return test_node_list

  def _createTestSuite(self,quantity=1,priority=1, reference_correction=0,
                       specialise_value=None, title=None, portal_type="Test Suite",
                       graph_coordinate="1", cluster_configuration='{ "test": {{ count }} }'):
    if title is None:
      title = ""
    if specialise_value is None:
      specialise_value = self.distributor
    test_suite_list = []
    for i in range(quantity):
      test_suite_title = "test suite %i" % (i + 1 + reference_correction)
      if title:
        test_suite_title += " %s" % title

      test_suite =  self.test_suite_module.newContent(
                    portal_type = portal_type,
                    title = test_suite_title,
                    test_suite_title = test_suite_title,
                    test_suite = 'B%i' % i,
                    int_index = priority,
                    specialise_value = specialise_value,
                   )
      if portal_type == "Scalability Test Suite":
        test_suite.setGraphCoordinate(graph_coordinate)
        test_suite.setClusterConfiguration(cluster_configuration)


      test_suite.newContent( portal_type= 'Test Suite Repository',
                        branch = 'master',
                        git_url = 'http://git.erp5.org/repos/erp5.git',
                        buildout_section_id  = 'erp5',
                        profile_path = 'software-release/software.cfg'
                        )
      test_suite.validate()
      test_suite_list.append(test_suite)
    return test_suite_list 

  def test_01_createTestNode(self):
    test_node = self._createTestNode()[0]
    self.assertEquals(test_node.getPortalType(), "Test Node")

  def test_02_createTestSuite(self):
    # Test Test Suite
    test_suite,  = self._createTestSuite()
    self.assertEquals(test_suite.getPortalType(), "Test Suite")
    self.assertEquals(test_suite.getSpecialise(), self.distributor.getRelativeUrl())
    # Test Scalability Test Suite
    scalability_test_suite,  = self._createTestSuite(
                                 portal_type="Scalability Test Suite",
                                 specialise_value = self.scalability_distributor
                               )
    self.assertEquals(scalability_test_suite.getPortalType(),
                       "Scalability Test Suite")
    self.assertEquals(scalability_test_suite.getSpecialise(),
                       self.scalability_distributor.getRelativeUrl())


  def _callOptimizeAlarm(self):
    self.portal.portal_alarms.task_distributor_alarm_optimize.activeSense()
    self.tic()

  def test_03_startTestSuiteWithOneTestNode(self):
    config_list = json.loads(self.distributor.startTestSuite(
                             title="COMP32-Node1"))
    self.assertEquals([], config_list)
    self._createTestSuite(quantity=3)
    self.tic()
    self._callOptimizeAlarm()
    config_list = json.loads(self.distributor.startTestSuite(
                             title="COMP32-Node1"))
    self.assertEquals(3, len(config_list))
    self.assertEquals(set(['B0','B1','B2']),
                      set([x['test_suite'] for x in config_list]))

  def test_04_startTestSuiteWithTwoTestNode(self):
    """
    When we have two test suites and we have two test nodes, we should have
    one test suite distributed per test node
    """
    config_list = json.loads(self.distributor.startTestSuite(
                             title="COMP32-Node1"))
    config_list = json.loads(self.distributor.startTestSuite(
                             title="COMP32-Node2"))
    self.assertEquals([], config_list)
    self._createTestSuite(quantity=2)
    self.tic()
    self._callOptimizeAlarm()
    def checkConfigListForTestNode(test_node_title):
      config_list = json.loads(self.distributor.startTestSuite(
                             title=test_node_title))
      self.assertEquals(1, len(config_list))
      return (test_node_title, set([x['test_suite'] for x in config_list]))
    config1 = checkConfigListForTestNode("COMP32-Node1")
    config2 = checkConfigListForTestNode("COMP32-Node2")
    self.assertTrue([config1, config2] in  [
                    [('COMP32-Node1',set([u'B0'])), ('COMP32-Node2',set([u'B1']))],
                    [('COMP32-Node1',set([u'B1'])), ('COMP32-Node2',set([u'B0']))]],
                    "%r" % ([config1, config2],))

  def _cleanupTestResult(self):
    self.tic()
    cleanup_state_list = ['started', 'stopped']
    test_list =  self.test_result_module.searchFolder(title="TEST FOO",
               simulation_state=cleanup_state_list)
    for test_result in test_list:
      if test_result.getSimulationState() in cleanup_state_list:
        test_result.cancel()
    self.tic()

  def _createTestResult(self, revision="r0=a,r1=a", node_title="Node0",
                              test_list=None, tic=1, allow_restart=False):
    result =  self.tool.createTestResult(
                               "", revision, test_list or [], allow_restart,
                               test_title="TEST FOO", node_title=node_title)
    # we commit, since usually we have a remote call only doing this
    (self.tic if tic else self.commit)()
    return result
    
  def test_05_createTestResult(self):
    """
    We will check the method createTestResult of task distribution tool
    """
    test_result_path, revision = self._createTestResult()
    self.assertEquals("r0=a,r1=a", revision)
    self.assertTrue(test_result_path.startswith("test_result_module/"))
    # If we ask again with another revision, we should get with previous
    # revision
    next_test_result_path, next_revision = self._createTestResult(
      revision="r0=a,r1=b", node_title="Node1")
    self.assertEquals(revision, next_revision)
    self.assertEquals(next_test_result_path, test_result_path)
    # Check if test result object is well created
    test_result = self.getPortalObject().unrestrictedTraverse(test_result_path)
    self.assertEquals("Test Result", test_result.getPortalType())
    self.assertEquals(0, len(test_result.objectValues(
                             portal_type="Test Result Line")))
    # now check that if we pass list of test, new lines will be created
    next_test_result_path, next_revision = self._createTestResult(
      test_list=['testFoo', 'testBar'])
    self.assertEquals(next_test_result_path, test_result_path)
    line_list = test_result.objectValues(portal_type="Test Result Line")
    self.assertEquals(2, len(line_list))
    self.assertEquals(set(['testFoo', 'testBar']), set([x.getTitle() for x
                      in line_list]))

  def test_06_startStopUnitTest(self):
    """
    We will check methods startUnitTest/stopUnitTest of task distribution tool
    """
    test_result_path, revision = self._createTestResult(
      test_list=['testFoo', 'testBar'])
    test_result = self.getPortalObject().unrestrictedTraverse(test_result_path)
    line_url, test = self.tool.startUnitTest(test_result_path)
    next_line_url, next_test = self.tool.startUnitTest(test_result_path)
    # first launch, we have no time optimisations, so tests are
    # launched in the given order
    self.assertEquals(['testFoo', 'testBar'], [test, next_test])
    status_dict = {}
    self.tool.stopUnitTest(line_url, status_dict)
    self.tool.stopUnitTest(next_line_url, status_dict)
    line = self.portal.unrestrictedTraverse(line_url)
    def checkDuration(line):
      duration = getattr(line, "duration", None)
      self.assertTrue(isinstance(duration, float))
      self.assertTrue(duration>0)
    checkDuration(line)
    next_line = self.portal.unrestrictedTraverse(next_line_url)
    checkDuration(next_line)
    # Make sure second test takes more time
    next_line.duration = line.duration + 1
    # So if we launch another unit test, it will process first the
    # one wich is the slowest
    self.assertEquals("stopped", test_result.getSimulationState())
    self.tic()
    next_test_result_path, revision = self._createTestResult(
      test_list=['testFoo', 'testBar'], revision="r0=a,r1=b")
    self.assertNotEquals(next_test_result_path, test_result_path)
    line_url, test = self.tool.startUnitTest(next_test_result_path)
    next_line_url, next_test = self.tool.startUnitTest(next_test_result_path)
    self.assertEquals(['testBar', 'testFoo'], [test, next_test])

  def test_07_reportTaskFailure(self):
    test_result_path, revision = self._createTestResult(node_title="Node0")
    test_result_path, revision = self._createTestResult(node_title="Node1")
    test_result = self.getPortalObject().unrestrictedTraverse(test_result_path)    
    self.assertEquals("started", test_result.getSimulationState())
    node_list = test_result.objectValues(portal_type="Test Result Node",
                                         sort_on=[("title", "ascending")])
    def checkNodeState(first_state, second_state):
      self.assertEquals([("Node0", first_state), ("Node1", second_state)],
              [(x.getTitle(), x.getSimulationState()) for x in node_list])
    checkNodeState("started", "started")
    self.tool.reportTaskFailure(test_result_path, {}, "Node0")
    self.assertEquals("started", test_result.getSimulationState())
    checkNodeState("failed", "started")
    self.tool.reportTaskFailure(test_result_path, {}, "Node1")
    self.assertEquals("failed", test_result.getSimulationState())
    checkNodeState("failed", "failed")

  def test_08_checkWeCanNotCreateTwoTestResultInParallel(self):
    """
    To avoid duplicates of test result when several testnodes works on the
    same suite, we create test and we immediately reindex it. So we must
    be able to find new test immediately after.
    """
    test_result_path, revision = self._createTestResult(
                                      node_title="Node0", tic=0)
    next_test_result_path, revision = self._createTestResult(
                                      node_title="Node1", tic=0)
    self.assertEquals(test_result_path, next_test_result_path)

  def _checkCreateTestResultAndAllowRestart(self, tic=False):
    test_result_path, revision = self._createTestResult(test_list=["testFoo"])
    line_url, test = self.tool.startUnitTest(test_result_path)
    status_dict = {}
    self.tool.stopUnitTest(line_url, status_dict)
    if tic:
      self.tic()
    test_result = self.getPortalObject().unrestrictedTraverse(test_result_path)
    self.assertEquals("stopped", test_result.getSimulationState())
    self.assertEquals(None, self._createTestResult(test_list=["testFoo"]))
    next_test_result_path, next_revision = self._createTestResult(
      test_list=["testFoo"], allow_restart=True)
    self.assertTrue(next_test_result_path != test_result_path)

  def test_09_checkCreateTestResultAndAllowRestartWithoutTic(self):
    """
    The option allow restart of createTestResult enable to possibility to
    always launch tests even if the given revision is already tested.

    Is this really useful and used ?
    """
    self._checkCreateTestResultAndAllowRestart()    

  def test_09b_checkCreateTestResultAndAllowRestartWithTic(self):
    """
    The option allow restart of createTestResult enable to possibility to
    always launch tests even if the given revision is already tested. We
    try here with reindex after stopUnitTest
    """
    self._checkCreateTestResultAndAllowRestart(tic=True)

  def test_10_cancelTestResult(self):
    pass

  def _checkTestSuiteAggregateList(self, *args):
    self.tic()
    self._callOptimizeAlarm()
    for test_node, aggregate_list in args:
      self.assertEquals(set(test_node.getAggregateList()),
        set(aggregate_list),
        "incorrect aggregate for %r, got %r instead of %r" % \
        (test_node.getTitle(), test_node.getAggregateList(), aggregate_list))

  def test_11_checkERP5ProjectOptimizationIsStable(self):
    """
    When we have two test suites and we have two test nodes, we should have
    one test suite distributed per test node
    """
    test_node_one, test_node_two = self._createTestNode(quantity=2)
    test_suite_one = self._createTestSuite(reference_correction=+0,
                              title='one')[0]
    test_suite_one_url = test_suite_one.getRelativeUrl()
    test_suite_two_url = self._createTestSuite(reference_correction=+1,
                              title='two')[0].getRelativeUrl()
    self.tic()
    self._callOptimizeAlarm()
    check = self._checkTestSuiteAggregateList
    check([test_node_one, [test_suite_one_url]],
          [test_node_two, [test_suite_two_url]])
    # first test suite is invalidated, so it should be removed from nodes, 
    # but this should not change assignment of second test suite
    test_suite_one.invalidate()
    check([test_node_one, []],
          [test_node_two, [test_suite_two_url]])
    # an additional test node is added, with lower title, this should
    # still not change anyting
    test_node_zero = self._createTestNode(quantity=1, reference_correction=-1)[0]
    check([test_node_zero, []],
          [test_node_one, []],
          [test_node_two, [test_suite_two_url]])
    # test suite one is validated again, it is installed on first
    # available test node
    test_suite_one.validate()
    check([test_node_zero, [test_suite_one_url]],
          [test_node_one, []],
          [test_node_two, [test_suite_two_url]])
    # for some reasons, test_node two is dead, so the work is distributed
    # to remaining test nodes
    test_node_two.invalidate()
    check([test_node_zero, [test_suite_one_url]],
          [test_node_one, [test_suite_two_url]],
          [test_node_two, []])
    # we add another test suite, since all test node already have one
    # test suite, the new test suite is given to first available one
    test_suite_three_url = self._createTestSuite(reference_correction=+2,
                                title='three')[0].getRelativeUrl()
    check([test_node_zero, [test_suite_one_url, test_suite_three_url]],
          [test_node_one, [test_suite_two_url]],
          [test_node_two, []])
    # test node two is coming back. However we do not change any assignment
    # to avoid uninstalling stuff on nodes
    test_node_two.validate()
    check([test_node_zero, [test_suite_one_url, test_suite_three_url]],
          [test_node_one, [test_suite_two_url]],
          [test_node_two, []])
    # Now let's create a test suite needing between 1 to 2 test nodes
    # We check that nodes with less suites are completed first
    test_suite_four_url = self._createTestSuite(reference_correction=+5,
                             priority=4, title='four')[0].getRelativeUrl()
    check([test_node_zero, [test_suite_one_url, test_suite_three_url]],
          [test_node_one, [test_suite_two_url, test_suite_four_url]],
          [test_node_two, [test_suite_four_url]])
    # Now let's create a 2 test suite needing between 2 to 3 test nodes
    # to make all test nodes almost satured
    test_suite_five_url = self._createTestSuite(reference_correction=+6,
                             priority=7, title='five')[0].getRelativeUrl()
    test_suite_six_url = self._createTestSuite(reference_correction=+7,
                             priority=7, title='six')[0].getRelativeUrl()
    check([test_node_zero, [test_suite_one_url, test_suite_three_url,
                            test_suite_five_url, test_suite_six_url]],
          [test_node_one, [test_suite_two_url, test_suite_four_url,
                            test_suite_five_url, test_suite_six_url]],
          [test_node_two, [test_suite_four_url,
                            test_suite_five_url, test_suite_six_url]])
    # Then, check what happens if all nodes are more than saturated
    # with a test suite needing between 3 to 5 test nodes
    test_suite_seven_url = self._createTestSuite(reference_correction=+4,
                             priority=9, title='seven')[0].getRelativeUrl()
    check([test_node_zero, [test_suite_one_url, test_suite_three_url,
                            test_suite_five_url, test_suite_six_url]],
          [test_node_one, [test_suite_two_url, test_suite_four_url,
                            test_suite_five_url, test_suite_six_url]],
          [test_node_two, [test_suite_four_url, test_suite_seven_url,
                            test_suite_five_url, test_suite_six_url]])
    # No place any more, adding more test suite has no consequence
    test_suite_height_url = self._createTestSuite(reference_correction=+8,
                             priority=9, title='height')[0].getRelativeUrl()
    check([test_node_zero, [test_suite_one_url, test_suite_three_url,
                            test_suite_five_url, test_suite_six_url]],
          [test_node_one, [test_suite_two_url, test_suite_four_url,
                            test_suite_five_url, test_suite_six_url]],
          [test_node_two, [test_suite_four_url, test_suite_seven_url,
                            test_suite_five_url, test_suite_six_url]])
    # free some place by removing a test suite
    self.portal.unrestrictedTraverse(test_suite_five_url).invalidate()
    check([test_node_zero, [test_suite_one_url, test_suite_three_url,
                            test_suite_six_url, test_suite_seven_url]],
          [test_node_one, [test_suite_two_url, test_suite_four_url,
                            test_suite_six_url, test_suite_seven_url]],
          [test_node_two, [test_suite_four_url, test_suite_six_url,
                            test_suite_seven_url, test_suite_height_url]])

  def test_12_checkCloudPerformanceOptimizationIsStable(self):
    """
    When we have two test suites and we have two test nodes, we should have
    one test suite distributed per test node
    """
    test_node_one, test_node_two = self._createTestNode(quantity=2,
                               specialise_value=self.performance_distributor)
    test_suite_list = self._createTestSuite(quantity=2,
                               specialise_value=self.performance_distributor)
    self.tic()
    self._callOptimizeAlarm()
    test_suite_one, test_suite_two = test_suite_list
    test_suite_one_url, test_suite_two_url = [x.getRelativeUrl() for x in 
                                            test_suite_list]
    check = self._checkTestSuiteAggregateList
    check([test_node_one, [test_suite_one_url, test_suite_two_url]],
          [test_node_two, [test_suite_one_url, test_suite_two_url]])
    # first test suite is invalidated, so it should be removed from nodes, 
    # but this should not change assignment of second test suite
    test_suite_one.invalidate()
    check([test_node_one, [test_suite_two_url]],
          [test_node_two, [test_suite_two_url]])
    # an additional test node is added, with lower title, it should
    # get in any case all test suite
    test_node_zero = self._createTestNode(quantity=1, reference_correction=-1,
                            specialise_value=self.performance_distributor)[0]
    check([test_node_zero, [test_suite_two_url]],
          [test_node_one, [test_suite_two_url]],
          [test_node_two, [test_suite_two_url]])
    # test suite one is validating again, it is installed on first
    # available test node
    test_suite_one.validate()
    check([test_node_zero, [test_suite_one_url, test_suite_two_url]],
          [test_node_one, [test_suite_one_url, test_suite_two_url]],
          [test_node_two, [test_suite_one_url, test_suite_two_url]])
    # for some reasons, test_node two is dead, this has no consequence
    # for others
    test_node_two.invalidate()
    check([test_node_zero, [test_suite_one_url, test_suite_two_url]],
          [test_node_one, [test_suite_one_url, test_suite_two_url]],
          [test_node_two, [test_suite_one_url, test_suite_two_url]])
    # we add another test suite, all test nodes should run it, except
    # test_node_two which is dead
    test_suite_three_url = self._createTestSuite(reference_correction=+2,
                             specialise_value=self.performance_distributor)[0]\
                             .getRelativeUrl()
    check([test_node_zero, [test_suite_one_url, test_suite_two_url,
                            test_suite_three_url]],
          [test_node_one, [test_suite_one_url, test_suite_two_url,
                            test_suite_three_url]],
          [test_node_two, [test_suite_one_url, test_suite_two_url]])
    # test node two is coming back. It should run all test suites
    test_node_two.validate()
    check([test_node_zero, [test_suite_one_url, test_suite_two_url,
                            test_suite_three_url]],
          [test_node_one, [test_suite_one_url, test_suite_two_url,
                            test_suite_three_url]],
          [test_node_two, [test_suite_one_url, test_suite_two_url,
                            test_suite_three_url]])
    # now we are going to

  def test_13_startTestSuiteWithOneTestNodeAndPerformanceDistributor(self):
    config_list = json.loads(self.performance_distributor.startTestSuite(
                             title="COMP32-Node1"))
    self.assertEquals([], config_list)
    self._createTestSuite(quantity=2, 
                          specialise_value=self.performance_distributor)
    self.tic()
    self._callOptimizeAlarm()
    config_list = json.loads(self.performance_distributor.startTestSuite(
                             title="COMP32-Node1"))
    self.assertEquals(2, len(config_list))
    self.assertEquals(set(['test suite 1-COMP32-Node1',
                           'test suite 2-COMP32-Node1']),
                      set([x['test_suite_title'] for x in config_list]))

  def test_14_subscribeNodeCheckERP5ScalabilityDistributor(self):
    """
    Check test node subscription.
    """
    test_node_module = self.test_node_module
    
    # Generate informations for nodes to subscribe
    nodes = dict([("COMP%d-Scalability-Node_test14" %i, "COMP-%d" %i) for i in range(0,5)])
    # Subscribe nodes
    for node_title in nodes.keys():
      self.scalability_distributor.subscribeNode(node_title, computer_guid=nodes[node_title])
    self.tic()
    # Get validated test nodes
    test_nodes = test_node_module.searchFolder(validation_state = 'validated')
    # Get test node title list
    test_node_titles = [x.getTitle() for x in test_nodes]
    # Check subscription
    for node_title in nodes.keys():
      self.assertTrue(node_title in test_node_titles)
    # Check ping date
    # TODO..

  def test_15_optimizeConfigurationCheckElectionERP5ScalabilityDistributor(self):
    """
    Check optimizeConfiguration method of scalability distributor.
     - Check the master election
    """
    test_node_module = self.test_node_module
    
    ## 1 (check election, classic)
    # Subscribe nodes
    self.scalability_distributor.subscribeNode("COMP1-Scalability-Node1", computer_guid="COMP-1")
    self.scalability_distributor.subscribeNode("COMP2-Scalability-Node2", computer_guid="COMP-2")
    self.scalability_distributor.subscribeNode("COMP3-Scalability-Node3", computer_guid="COMP-3")
    self.scalability_distributor.subscribeNode("COMP4-Scalability-Node4", computer_guid="COMP-4")
    self.tic()
    # Check test node election
    def getMasterAndSlaveNodeList():
      """
      Optimize the configuration and return which nodes are master/slave
      """
      self._callOptimizeAlarm()
      master_test_node_list = [x for x in test_node_module.searchFolder()\
                               if (x.getMaster() == True  and x.getValidationState() == 'validated')]
      slave_test_node_list =  [x for x in test_node_module.searchFolder()\
                               if (x.getMaster() == False and x.getValidationState() == 'validated')]
      return master_test_node_list, slave_test_node_list
    master_test_node_list, slave_test_node_list = getMasterAndSlaveNodeList()

    # -Only one master must be elected
    self.assertEquals(1, len(master_test_node_list))
    # -Others test node must not be the matser
    self.assertEquals(3, len(slave_test_node_list))
    
    # Get the current master test node 
    current_master_test_node_1 = master_test_node_list[0]
    
    ## 2 (check election, with adding new nodes)
    # Add new nodes
    self.scalability_distributor.subscribeNode("COMP5-Scalability-Node5", computer_guid="COMP-5")
    self.scalability_distributor.subscribeNode("COMP6-Scalability-Node6", computer_guid="COMP-6")
    self.tic()
    # Check test node election
    master_test_node_list, slave_test_node_list = getMasterAndSlaveNodeList()
    # -Only one master must be elected
    self.assertEquals(1, len(master_test_node_list))
    # -Others test node must not be the matser
    self.assertEquals(5, len(slave_test_node_list))

    # Get the current master test node
    current_master_test_node_2 =  master_test_node_list[0]
    # Master test node while he is alive
    self.assertEquals(current_master_test_node_1.getTitle(),
                      current_master_test_node_2.getTitle())

    ## 3 (check election, with master deletion)
    # Invalidate master
    current_master_test_node_2.invalidate()
    # Check test node election
    master_test_node_list, slave_test_node_list = getMasterAndSlaveNodeList()
    # -Only one master must be elected
    self.assertEquals(1, len(master_test_node_list))
    # -Others test node must not be the matser
    self.assertEquals(4, len(slave_test_node_list))

    # Get the current master test node 
    current_master_test_node_3 = master_test_node_list[0]
    # Master test node must be an other test node than previously
    self.assertNotEquals(current_master_test_node_2.getTitle(), 
                         current_master_test_node_3.getTitle())
    

  def test_16_startTestSuiteERP5ScalabilityDistributor(self):
    """
    Check test suite getting, for the scalability case only the master
    test node receive test suite.
    """
    test_node_module = self.test_node_module

    # Subscribe nodes
    nodes = [self.scalability_distributor.subscribeNode("COMP1-Scalability-Node1", computer_guid="COMP-1"),
             self.scalability_distributor.subscribeNode("COMP2-Scalability-Node2", computer_guid="COMP-2"),
             self.scalability_distributor.subscribeNode("COMP3-Scalability-Node3", computer_guid="COMP-3"),
             self.scalability_distributor.subscribeNode("COMP4-Scalability-Node4", computer_guid="COMP-4")]
     # Create test suite
    test_suite = self._createTestSuite(quantity=1,priority=1, reference_correction=0,
                       specialise_value=self.scalability_distributor, portal_type="Scalability Test Suite")  
    self.tic()
    self._callOptimizeAlarm()
    # Get current master test node
    master_test_nodes = [x for x in test_node_module.searchFolder()\
                         if (x.getMaster() == True and x.getValidationState() == "validated")]     
    current_master_test_node = master_test_nodes[0]
    self.tic()
    # Each node run startTestSuite
    config_nodes = {
                     'COMP1-Scalability-Node1' :
                        json.loads(self.scalability_distributor.startTestSuite(
                                   title="COMP1-Scalability-Node1")),
                     'COMP2-Scalability-Node2' :
                        json.loads(self.scalability_distributor.startTestSuite(
                                   title="COMP2-Scalability-Node2")),
                     'COMP3-Scalability-Node3' :
                        json.loads(self.scalability_distributor.startTestSuite(
                                   title="COMP3-Scalability-Node3")),
                     'COMP4-Scalability-Node4' :
                        json.loads(self.scalability_distributor.startTestSuite(
                                   title="COMP4-Scalability-Node4"))
                   }
    # Check if master has got a non empty configuration
    self.assertNotEquals(config_nodes[current_master_test_node.getTitle()], [])
    # -Delete master test node suite from dict
    del config_nodes[current_master_test_node.getTitle()]
    # Check if slave test node have got empty list
    for suite in config_nodes.values():
      self.assertEquals(suite, [])

  def test_17_isMasterTestnodeERP5ScalabilityDistributor(self):
    """
    Check the method isMasterTestnode()
    """
    test_node_module = self.test_node_module

    # Subscribe nodes
    self.scalability_distributor.subscribeNode("COMP1-Scalability-Node1", computer_guid="COMP-1")
    self.scalability_distributor.subscribeNode("COMP2-Scalability-Node2", computer_guid="COMP-2")
    self.scalability_distributor.subscribeNode("COMP3-Scalability-Node3", computer_guid="COMP-3")
    self.scalability_distributor.subscribeNode("COMP4-Scalability-Node4", computer_guid="COMP-4")
    self.tic()
    self._callOptimizeAlarm()
    # Optimize configuration
    self.scalability_distributor.optimizeConfiguration()
    self.tic()
    # Get test nodes 
    master_test_nodes = [x for x in test_node_module.searchFolder()
                         if (x.getMaster() == True and x.getValidationState() == 'validated')]
    slave_test_nodes = [x for x in test_node_module.searchFolder()
                         if (x.getMaster() == False and x.getValidationState() == 'validated')]
    # Check isMasterTestnode method
    for master in master_test_nodes:
      self.assertTrue(self.scalability_distributor.isMasterTestnode(master.getTitle()))
    for slave in slave_test_nodes:
      self.assertTrue(not self.scalability_distributor.isMasterTestnode(slave.getTitle()))

  def test_18_checkConfigurationGenerationERP5ScalabilityDistributor(self):
    """
    Check configuration generation
    """
    test_node_module = self.test_node_module

    # Subscribe nodes
    node_list = [self.scalability_distributor.subscribeNode("COMP1-Scalability-Node1", computer_guid="COMP-1"),
             self.scalability_distributor.subscribeNode("COMP2-Scalability-Node2", computer_guid="COMP-2"),
             self.scalability_distributor.subscribeNode("COMP3-Scalability-Node3", computer_guid="COMP-3"),
             self.scalability_distributor.subscribeNode("COMP4-Scalability-Node4", computer_guid="COMP-4")]
    self.tic()
    self._callOptimizeAlarm()

    #
    def generateZopePartitionDict(i):
      """
      Generate a configuration wich uses jinja2
      """
      partition_dict = ""
      for j in range(0,i):
        family_name = ['user', 'activity'][j%2]
        partition_dict += '"%s-%s":{\n' %(family_name, node_list[j].getReference())
        partition_dict += ' "instance-count": {{ count }},\n'
        partition_dict += ' "family": "%s",\n' %family_name
        partition_dict += ' "computer_guid": "%s"\n' %node_list[j].getReference()
        partition_dict += '}' 
        if j != i-1:
          partition_dict += ',\n'
        else:
          partition_dict += '\n'
      return partition_dict


    # Generate a test suite
    # -Generate a configuration adapted to the test node list length
    cluster_configuration = '{"zope-partition-dict":{\n'
    zope_partition_dict = ""
    for i in range(1, len(node_list)+1):
      zope_partition_dict += "{%% if count == %d %%}\n" %i
      zope_partition_dict += generateZopePartitionDict(i)
      zope_partition_dict += "{% endif %}\n"
    cluster_configuration += zope_partition_dict + '\n}}'
    # -Generate graph coordinate
    graph_coordinate = range(1, len(node_list)+1)
    # -Create the test suite
    test_suite = self._createTestSuite(quantity=1,priority=1, reference_correction=0,
                       specialise_value=self.scalability_distributor, portal_type="Scalability Test Suite",
                       graph_coordinate=graph_coordinate, cluster_configuration=cluster_configuration)
    self.tic()

    # Master test node launch startTestSuite
    for node in node_list:
      if node.getMaster():
        test_suite_title = self.scalability_distributor.startTestSuite(title=node.getTitle())
#        log("test_suite_title: %s" %test_suite_title)
        break
    # Get configuration list generated from test suite
#    configuration_list = self.scalability_distributor.generateConfiguration(test_suite_title)
   
    # logs
#    log(configuration_list)    

    def test_19_testMultiDistributor(self):
      pass
