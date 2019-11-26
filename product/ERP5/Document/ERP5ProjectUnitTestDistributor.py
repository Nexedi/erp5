##############################################################################
# Copyright (c) 2013 Nexedi SA and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Tool.TaskDistributionTool import TaskDistributionTool
from DateTime import DateTime
from datetime import datetime
import json
import sys
import itertools
from copy import deepcopy
import random
import string
from zLOG import LOG,INFO,ERROR
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery
TEST_SUITE_MAX = 4
# Depending on the test suite priority, we will affect
# more or less cores
PRIORITY_MAPPING =  {
  # int_index: (min cores, max cores)
   1: (  3,  3),
   2: (  3,  6),
   3: (  6,  9),
   4: (  6, 12),
   5: (  9, 15),
   6: (  9, 18),
   7: ( 12, 24),
   8: ( 15, 30),
   9: ( 18, 45),
  }

class ERP5ProjectUnitTestDistributor(XMLObject):

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.ManagePortal,
                            "cleanupInvalidatedTestNode")
  def cleanupInvalidatedTestNode(self, test_node):
    """
    When a test node is invalidated, the work will be distributed to
    other test nodes, so we should clean association to test suites.
    Like this, when this node will come back, we will not mess distribution
    with stuff already distributed in other places
    """
    if test_node.getAggregateList():
      test_node.setAggregateList([])

  def _cleanupTestNodeList(self,test_node_list, test_suite_list_to_remove):
    # Remove useless assigment of test suites. First remove from
    # nodes with highest number of test suites
    # test_suite_list_to_remove could be like ['foo','foo', 'bar']
    test_suite_list_to_remove.sort()
    while len(test_suite_list_to_remove):
      test_node_list.sort(key=lambda x: -len(x.getAggregateList()))
      current_test_suite = test_suite_list_to_remove[0]
      for test_node in test_node_list:
        test_suite_list = test_node.getAggregateList()
        if current_test_suite in test_suite_list:
          test_suite_list.remove(current_test_suite)
          test_node.setAggregateList(test_suite_list)
          test_suite_list_to_remove.remove(current_test_suite)
        if len(test_suite_list_to_remove):
          if test_suite_list_to_remove[0] != current_test_suite:
            break
        else:
          break

  def _checkCurrentConfiguration(self,test_node_list, test_suite_list_to_add, max_test_suite):
    """
    We look at what is already installed and then we remove from the list
    of test suite list to add what is already installed.
    We also build a list of installed test suites that should be removed
    """
    test_suite_list_to_remove = []
    for test_node in test_node_list:
      test_suite_list = test_node.getAggregateList()
      for index, test_suite in enumerate(test_suite_list, 1):
        if index > max_test_suite:
          test_suite_list_to_remove.append(test_suite)
          continue
        try:
          test_suite_list_to_add.remove(test_suite)
        except ValueError:
          test_suite_list_to_remove.append(test_suite)
    return test_suite_list_to_remove

  security.declareProtected(Permissions.ManagePortal, "optimizeConfiguration")
  def optimizeConfiguration(self):
    """
    We are going to add test suites to test nodes.
    First are completed test nodes with fewer test suites
    """
    self.serialize() # prevent parallel optimization to avoid conflict
                     # on nodes and possibly weird results
    portal = self.getPortalObject()
    test_node_module = self._getTestNodeModule()
    test_node_list = [
        x.getObject() for x in test_node_module.searchFolder(
        portal_type="Test Node", validation_state="validated",
        specialise_uid=self.getUid(), sort_on=[('title','ascending')])]

    test_node_list_len = len(test_node_list)
    max_test_suite = self.getMaxTestSuite(TEST_SUITE_MAX)
    def _optimizeConfiguration(test_suite_list_to_add, level=0,
                               test_node_list_to_optimize=None,
                               test_suite_max=max_test_suite):
      if test_node_list_to_optimize is None:
        test_node_list_to_optimize = [x for x in test_node_list]
      if test_suite_list_to_add:
        test_node_list_to_remove = []
        for test_node in test_node_list_to_optimize:
          # We can no longer add more test suite on this test node
          if test_suite_max < (level + 1):
            test_node_list_to_remove.append(test_node)
            continue
          test_suite_list = test_node.getAggregateList()
          if len(test_suite_list) == level:
            for test_suite in test_suite_list_to_add:
              if not(test_suite in test_suite_list):
                test_node.setAggregateList([test_suite] + test_suite_list)
                test_suite_list_to_add.remove(test_suite)
                break
            if len(test_suite_list_to_add) == 0:
              break
        for test_node in test_node_list_to_remove:
          test_node_list_to_optimize.remove(test_node)
      if test_suite_list_to_add and test_node_list_to_optimize:
        _optimizeConfiguration(test_suite_list_to_add, level=level+1,
                      test_node_list_to_optimize=test_node_list_to_optimize,
                      test_suite_max=test_suite_max)

    test_suite_score, test_suite_list_to_add = self._getSortedNodeTestSuiteList()
    average_quantity = float(len(test_suite_list_to_add)) / (test_node_list_len or 1)
    test_suite_list_to_remove = self._checkCurrentConfiguration(test_node_list,
      test_suite_list_to_add, max_test_suite)
    self._cleanupTestNodeList(test_node_list, test_suite_list_to_remove)
    _optimizeConfiguration(test_suite_list_to_add)
    # once we removed useless test suite and added needed ones,
    # we check if we can move some test suites to testnodes that are
    # more idle than others. We try to move first test suites using
    # more test nodes, this reduce risk of moving a test suite assigned
    # on a single test node (to avoid waiting building)
    overloaded_test_node_list = []
    lazy_test_node_list = []
    int_average_quantity = int(average_quantity)
    # Find testnode which can accept more work
    for test_node in test_node_list:
      aggregate_len = len(test_node.getAggregateList())
      if aggregate_len <= (average_quantity - 1):
        lazy_test_node_list.append(test_node)
    # check on most overloaded test nodes first if we can move some work to lazy
    # test nodes
    for aggregate_quantity in range(max_test_suite, int_average_quantity, -1):
      if len(lazy_test_node_list) == 0:
        break
      overloaded_test_node_list = [x for x in test_node_list if len(x.getAggregateList()) == aggregate_quantity]
      for test_node in overloaded_test_node_list:
        test_suite_list = test_node.getAggregateList()
        test_suite_list.sort(key=lambda x: (-test_suite_score[x][-1],
                                            portal.unrestrictedTraverse(x).getTitle()))
        for test_suite in test_suite_list:
          test_suite_list_to_move = [test_suite]
          _optimizeConfiguration(test_suite_list_to_move,
                                 test_node_list_to_optimize=lazy_test_node_list,
                                 test_suite_max=int_average_quantity)
          if len(test_suite_list_to_move) == 0:
            # This means we were able to affect the test suite to another test node
            test_suite_list.remove(test_suite)
            test_node.setAggregateList(test_suite_list)
            break
        if len(lazy_test_node_list) == 0:
          break

  def _getSortedNodeTestSuiteList(self):
    """
    We build the list of test suite instances. If a test suite
    can be installed on at most 2 test nodes, it will be twice
    in the returned list. We give a score for every wished test suites.
    The lower score, the better chance it has to be installed.

    A test_suite_score is also returned allowing to quickly identify
    which test suite migh be removed on test node with too many test suites
  """
    test_suite_module = self._getTestSuiteModule()
    portal = self.getPortalObject()
    test_suite_list = test_suite_module.searchFolder(validation_state="validated",
                                               specialise_uid=self.getUid())
    all_test_suite_list = []
    test_suite_score = {}
    for test_suite in test_suite_list:
      test_suite = test_suite.getObject()
      test_suite_url = test_suite.getRelativeUrl()
      title = test_suite.getTitle()
      # suites required
      int_index = test_suite.getIntIndex()
      # we divide per 3 because we have 3 cores per node
      node_quantity_min = PRIORITY_MAPPING[int_index][0]/3
      node_quantity_max = PRIORITY_MAPPING[int_index][1]/3
      for x in xrange(0, node_quantity_min):
        score = float(x)/(x+1)
        all_test_suite_list.append((score, test_suite_url, title))
        test_suite_score.setdefault(test_suite_url, []).append(score)
      # additional suites, lower score
      for x in xrange(0, node_quantity_max -
                   node_quantity_min ):
        score = float(1) + x/(x+1)
        all_test_suite_list.append((1 + x/(x+1), test_suite_url, title))
        test_suite_score.setdefault(test_suite_url, []).append(score)
    all_test_suite_list.sort(key=lambda x: (x[0], x[2]))
    return test_suite_score, [x[1] for x in all_test_suite_list]

  def _getTestNodeModule(self):
    return self.getPortalObject().test_node_module

  def _getTestSuiteModule(self):
    return self.getPortalObject().test_suite_module

  def getMemcachedDict(self):
    portal = self.getPortalObject()
    memcached_dict = portal.portal_memcached.getMemcachedDict(
                            "task_distribution", "default_memcached_plugin")
    return memcached_dict

  security.declarePublic("getTestType")
  def getTestType(self, batch_mode=0):
    """
    getTestType : return a string defining the test type
    """
    return 'UnitTest'

  security.declarePublic("subscribeNode")
  def subscribeNode(self,title,computer_guid,batch_mode=0):
    """
    subscribeNode doc
    """
    test_node_module = self._getTestNodeModule()
    portal = self.getPortalObject()

    config = {}
    tag = "%s_%s" % (self.getRelativeUrl(), title)
    if portal.portal_activities.countMessageWithTag(tag) == 0:
      test_node_list = test_node_module.searchFolder(
        portal_type="Test Node",
        title=SimpleQuery(comparison_operator='=', title=title),
      )
      if getattr(self, 'getProcessTimeout', None) is not None:
        config['process_timeout'] = self.getProcessTimeout()
      assert len(test_node_list) in (0, 1), "Unable to find testnode : %s" % title
      test_node = None
      if len(test_node_list) == 1:
        test_node = test_node_list[0].getObject()
        if test_node.getValidationState() != 'validated':
           try:
            test_node.validate()
           except e:
             LOG('Test Node Validate',ERROR,'%s' %e)
      if test_node is None:
        test_node = test_node_module.newContent(portal_type="Test Node", title=title, computer_guid=computer_guid,
                                      specialise=self.getRelativeUrl(),
                                      activate_kw={'tag': tag})
        self.activate(after_tag=tag).optimizeConfiguration()
      test_node.setPingDate()
    if batch_mode:
      return config
    return json.dumps(config)

  def _getSortedNodeTestSuiteToRun(self, test_node):
    """
    Returned ordered list of test suites of a test node. More the
    latest test result is old, more it will have priority. Like this
    we try to run first test suites that have no results since a long
    time
    """
    portal = self.getPortalObject()
    test_suite_list = test_node.getAggregateValueList()
    # Do not take results older than one month to avoid killing the
    # sql server
    now = DateTime()
    from_date = now - 30
    max_test_core_per_suite = max([x[1] for x in PRIORITY_MAPPING.values()])
    def getTestSuiteSortKey(test_suite):
      test_result_list = portal.portal_catalog(portal_type="Test Result",
                                          title=SimpleQuery(title=test_suite.getTitle()),
                                          creation_date=SimpleQuery(
                                            creation_date=from_date,
                                            comparison_operator='>=',
                                          ),
                                          sort_on=[("modification_date", "descending")],
                                          limit=1)
      if len(test_result_list):
        test_result = test_result_list[0].getObject()
        modification_date = test_result.getModificationDate().timeTime()
        key = (1, modification_date)
        # if a test result has all it's tests already ongoing, it is not a
        # priority at all to process it, therefore push it at the end of the list
        if test_result.getSimulationState() == "started":
          result_line_list = test_result.objectValues(portal_type="Test Result Line")
          check_priority = True
          if len(result_line_list):
            if len([x for x in result_line_list if x.getSimulationState() == "draft"]) == 0:
              key = (1000, now.timeTime())
              check_priority = False
          if check_priority:
            # calculate key[0] in such a way that more the test suite has high
            # priority and the more test result lack test node, the lower is key[0]
            # This allows to affect more test nodes to test suites with higher priority
            wanted_test_core_quantity = PRIORITY_MAPPING[test_suite.getIntIndex()][1]
            factor = float(max_test_core_per_suite) / wanted_test_core_quantity
            missing_quantity = wanted_test_core_quantity/3 - len(test_result.objectValues(portal_type="Test Result Node"))
            key = (max_test_core_per_suite - missing_quantity * 3 * factor, modification_date)
      else:
        key = (0, random.random())
      return key
    test_suite_list.sort(key=getTestSuiteSortKey)
    return test_suite_list

  security.declarePublic("startTestSuite")
  def startTestSuite(self,title, computer_guid=None, batch_mode=0):
    """
    startTestSuite doc
    """
    test_node_module = self._getTestNodeModule()
    test_suite_module =  self._getTestSuiteModule()
    portal = self.getPortalObject()
    config_list = []
    tag = "%s_%s" % (self.getRelativeUrl(), title)
    if portal.portal_activities.countMessageWithTag(tag) == 0:
      test_node_list = test_node_module.searchFolder(
        portal_type="Test Node",
        title=SimpleQuery(comparison_operator='=', title=title),
      )
      assert len(test_node_list) in (0, 1), "Unable to find testnode : %s" % title
      test_node = None
      if len(test_node_list) == 1:
        test_node = test_node_list[0].getObject()
        if test_node.getValidationState() != 'validated':
          test_node.validate()
      if test_node is None:
        test_node = test_node_module.newContent(portal_type="Test Node", title=title,
                                      specialise=self.getRelativeUrl(),
                                      activate_kw={'tag': tag})
        self.activate(after_tag=tag).optimizeConfiguration()
      test_node.setPingDate()
      choice_list = self._getSortedNodeTestSuiteToRun(test_node)
      for test_suite in choice_list:
        config = {}
        config["project_title"] = test_suite.getSourceProjectTitle()
        config["test_suite"] = test_suite.getTestSuite()
        config["test_suite_title"] = test_suite.getTitle()
        config["additional_bt5_repository_id"] = test_suite.getAdditionalBt5RepositoryId()
        config["test_suite_reference"] = test_suite.getReference()
        vcs_repository_list = []
        #In this case objectValues is faster than searchFolder
        for repository in test_suite.objectValues(portal_type="Test Suite Repository"):
          repository_dict = {}
          for property_name in ["git_url", "profile_path", "buildout_section_id", "branch"]:
            property_value = repository.getProperty(property_name)
            # the property name url returns the object's url, so it is mandatory use another name.
            if property_name == "git_url":
              property_name="url"
            if property_value is not None:
              repository_dict[property_name] = property_value
          vcs_repository_list.append(repository_dict)
        config["vcs_repository_list"] = vcs_repository_list
        to_delete_key_list = [x for x,y in config.items() if y==None]
        [config.pop(x) for x in to_delete_key_list]
        config_list.append(config)
    # LOG('ERP5ProjectUnitTestDistributor.startTestSuite, config_list',INFO,config_list)
    if batch_mode:
      return config_list
    return json.dumps(config_list)

  security.declarePublic("createTestResult")
  def createTestResult(self, name, revision, test_name_list, allow_restart,
                       test_title=None, node_title=None, project_title=None):
    """
    Here this is only a proxy to the task distribution tool
    """
    # LOG('ERP5ProjectUnitTestDistributor.createTestResult', 0, (node_title, test_title))
    portal = self.getPortalObject()
    if node_title:
      test_node = self._getTestNodeFromTitle(node_title)
      test_node.setPingDate()
    test_suite = self._getTestSuiteFromTitle(test_title)
    if test_suite is not None:
      if not allow_restart and test_suite.isEnabled():
        # in case if allow_restart is not enforced by client and test_node
        # periodicity is enabled control the restartability based on test_suite
        # periodicity
        current_date = DateTime()
        alarm_date = test_suite.getAlarmDate()
        if alarm_date is None or alarm_date <= current_date:
          allow_restart = True
          test_suite.setAlarmDate(
            test_suite.getNextPeriodicalDate(current_date, alarm_date))
      test_suite.setPingDate()
      return portal.portal_task_distribution.createTestResult(name,
           revision, test_name_list, allow_restart,
           test_title=test_title, node_title=node_title,
           project_title=project_title)

  def _getTestNodeFromTitle(self, node_title):
    test_node_list = self._getTestNodeModule().searchFolder(
      portal_type="Test Node",
      title=SimpleQuery(comparison_operator='=', title=node_title),
      limit=2
    )
    assert len(test_node_list) == 1, "We found %i test nodes for %s" % (
                                      len(test_node_list), node_title)
    test_node = test_node_list[0].getObject()
    return test_node

  def _getTestSuiteFromTitle(self, suite_title):
    test_suite_list = self._getTestSuiteModule().searchFolder(
      portal_type='Test Suite',
      title=SimpleQuery(comparison_operator='=', title=suite_title),
      validation_state='validated',
      limit=2)
    assert len(test_suite_list) <= 1, "We found %i test suite for %s" % (
                                      len(test_suite_list), suite_title)
    test_suite = None
    if len(test_suite_list):
      test_suite = test_suite_list[0].getObject()
    return test_suite

  security.declarePublic("startUnitTest")
  def startUnitTest(self, test_result_path, exclude_list=(), node_title=None):
    """
    Here this is only a proxy to the task distribution tool
    """
    # LOG('ERP5ProjectUnitTestDistributor.startUnitTest', 0, test_result_path)
    portal = self.getPortalObject()
    return portal.portal_task_distribution.startUnitTest(test_result_path,exclude_list,
                  node_title=node_title)

  security.declarePublic("stopUnitTest")
  def stopUnitTest(self,test_path,status_dict, node_title=None):
    """
    Here this is only a proxy to the task distribution tool
    """
    # LOG('ERP5ProjectUnitTestDistributor.stop_unit_test', 0, test_path)
    portal = self.getPortalObject()
    return portal.portal_task_distribution.stopUnitTest(test_path, status_dict,
                  node_title=node_title)

  security.declarePublic("generateConfiguration")
  def generateConfiguration(self, test_suite_title, batch_mode=0):
    """
    return the list of configuration to create instances, in the case of ERP5 unit tests,
    we will have only one configuration (unlike scalability tests). But for API consistency,
    always return a list.
    """
    test_suite = self._getTestSuiteFromTitle(test_suite_title)
    generated_configuration = {"configuration_list": [{}]}
    if test_suite is not None:
      cluster_configuration = test_suite.getClusterConfiguration() or '{}'
      try:
        generated_configuration = {"configuration_list": [json.loads(cluster_configuration)]}
      except ValueError:
        pass
    if batch_mode:
      return generated_configuration
    return json.dumps(generated_configuration)
