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
TEST_SUITE_MAX = 4  
# Depending on the test suite priority, we will affect
# more or less cores
PRIORITY_MAPPING =  {
  # int_index: (min cores, max cores)
   1: ( 3,  3),
   2: ( 3,  3),
   3: ( 3,  6),
   4: ( 3,  6),
   5: ( 3,  6),
   6: ( 6,  9),
   7: ( 6,  9),
   8: ( 6,  9),
   9: ( 9, 15),
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

  def _checkCurrentConfiguration(self,test_node_list, test_suite_list_to_add):
    """
    We look at what is already installed and then we remove from the list
    of test suite list to add what is already installed.
    We also build a list of installed test suites that should be removed
    """
    test_suite_list_to_remove = []
    for test_node in test_node_list:
      test_suite_list = test_node.getAggregateList()
      for test_suite_title in test_suite_list:
        try:
          test_suite_list_to_add.remove(test_suite_title)
        except ValueError:
          test_suite_list_to_remove.append(test_suite_title)
    return test_suite_list_to_remove
  
  security.declareProtected(Permissions.ManagePortal, "optimizeConfiguration")
  def optimizeConfiguration(self):
    """
    We are going to add test suites to test nodes.
    First are completed test nodes with fewer test suites
    """
    portal = self.getPortalObject()
    test_node_module = self._getTestNodeModule()
    test_node_list = [
        x.getObject() for x in test_node_module.searchFolder(
        portal_type="Test Node", validation_state="validated",
        specialise_uid=self.getUid(), sort_on=[('title','ascending')])]
      
    test_node_list_len = len(test_node_list)
    def _optimizeConfiguration(test_suite_list_to_add, level=0):
      if test_suite_list_to_add:
        test_node_list_to_remove = []
        for test_node in test_node_list:
          # We can no longer add more test suite on this test node
          if TEST_SUITE_MAX < (level + 1):
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
          test_node_list.remove(test_node)
      if test_suite_list_to_add and test_node_list:
        _optimizeConfiguration(test_suite_list_to_add, level=level+1)

    test_suite_list_to_add = self._getSortedNodeTestSuiteList()
    test_suite_list_to_remove = self._checkCurrentConfiguration(test_node_list,
      test_suite_list_to_add)
    self._cleanupTestNodeList(test_node_list, test_suite_list_to_remove)
    _optimizeConfiguration(test_suite_list_to_add)

  def _getSortedNodeTestSuiteList(self):
    """
    We build the list of test suite instances. If a test suite
    can be installed on at most 2 test nodes, it will be twice
    in the returned list. We give a score for every wished test suites.
    The lower score, the better chance it has to be installed.
  """
    test_suite_module = self._getTestSuiteModule()
    portal = self.getPortalObject()
    test_suite_list = test_suite_module.searchFolder(validation_state="validated",
                                               specialise_uid=self.getUid())
    all_test_suite_list = []
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
        all_test_suite_list.append((x/(x+1),test_suite_url, title))
      # additional suites, lower score
      for x in xrange(0, node_quantity_max -
                   node_quantity_min ):
        all_test_suite_list.append((1 + x/(x+1), test_suite_url, title))
    all_test_suite_list.sort(key=lambda x: (x[0], x[2]))
    return [x[1] for x in all_test_suite_list]

  def _getTestNodeModule(self):
    return self.getPortalObject().test_node_module

  def _getTestSuiteModule(self):
    return self.getPortalObject().test_suite_module

  def getMemcachedDict(self):
    portal = self.getPortalObject()
    memcached_dict = portal.portal_memcached.getMemcachedDict(
                            "task_distribution", "default_memcached_plugin")
    return memcached_dict

  security.declarePublic("startTestSuite")
  def startTestSuite(self,title, batch_mode=0):
    """
    startTestSuite doc
    """
    test_node_module = self._getTestNodeModule()
    test_suite_module =  self._getTestSuiteModule()
    portal = self.getPortalObject()
    config_list = []
    tag = "%s_%s" % (self.getRelativeUrl(), title)
    if portal.portal_activities.countMessageWithTag(tag) == 0:
      test_node_list = test_node_module.searchFolder(portal_type="Test Node",title=title)
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
        test_node = test_node_module.newContent(portal_type="Test Node", title=title,
                                      specialise=self.getRelativeUrl(),
                                      activate_kw={'tag': tag})
        self.activate(after_tag=tag).optimizeConfiguration()
      test_node.setPingDate()
      test_suite_list = test_node.getAggregateList() 
      # We sort the list according to timestamp
      choice_list = []
      if len(test_suite_list):
        choice_list = [x.getObject() for x in test_suite_module.searchFolder(
                relative_url=test_suite_list,
                sort_on=[('indexation_timestamp','ascending')],
                      )] 
      # XXX we should have first test suite with no test node working on
      # them since a long time. However we do not have this information yet,
      # so random sort is better for now.
      choice_list.sort(key=lambda x: random.random())
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
    LOG('ERP5ProjectUnitTestDistributor.startTestSuite, config_list',INFO,config_list)
    if batch_mode:
      return config_list
    return json.dumps(config_list)
          
  security.declarePublic("createTestResult")
  def createTestResult(self, name, revision, test_name_list, allow_restart,
                       test_title=None, node_title=None, project_title=None):
    """
    Here this is only a proxy to the task distribution tool
    """
    LOG('ERP5ProjectUnitTestDistributor.createTestResult', 0, (node_title, test_title))
    portal = self.getPortalObject()
    test_node = self._getTestNodeFromTitle(node_title)
    test_node.setPingDate()
    test_suite = self._getTestSuiteFromTitle(name)
    test_suite.setPingDate()
    return portal.portal_task_distribution_tool.createTestResult(name,
           revision, test_name_list, allow_restart,
           test_title=title_title, node_title=node_title, 
           project_title=project_title)

  def _getTestNodeFromTitle(self, node_title):
    test_node_list = self._getTestNodeModule().searchFolder(
                       portal_type='Test Node', title="='%s'" % node_title)
    assert len(test_node_list) == 1, "We found %i test nodes for %s" % (
                                      len(test_node_list), node_title)
    test_node = test_node_list[0].getObject()
    return test_node

  def _getTestSuiteFromTitle(self, suite_title):
    test_suite_list = self._getTestSuiteModule().searchFolder(
                       portal_type='Test Suite', title="='%s'" % suit_tile, validation_state="validated")
    assert len(test_suite_list) == 1, "We found %i test suite for %s" % (
                                      len(test_suite_list), name)
    test_suite = test_suite_list[0].getObject()

  security.declarePublic("startUnitTest")
  def startUnitTest(self,test_result_path,exclude_list=()):
    """
    Here this is only a proxy to the task distribution tool
    """
    LOG('ERP5ProjectUnitTestDistributor.startUnitTest', 0, test_result_path)
    portal = self.getPortalObject()
    return portal.portal_task_distribution_tool.startUnitTest(test_result_path,exclude_list)

  security.declarePublic("stopUnitTest")
  def stopUnitTest(self,test_path,status_dict):
    """
    Here this is only a proxy to the task distribution tool
    """
    LOG('ERP5ProjectUnitTestDistributor.stop_unit_test', 0, test_path)
    portal = self.getPortalObject()
    test_result = portal.unrestrictedTraverse(test_path)
    test_suite_title = test_result.getTitle()
    return portal.portal_task_distribution_tool.stopUnitTest(self,test_path,status_dict)