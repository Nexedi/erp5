##############################################################################
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
#          Rafael Monnerat <rafael@nexedi.com>
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

from erp5.component.document.ERP5ProjectUnitTestDistributor import ERP5ProjectUnitTestDistributor
from DateTime import DateTime
from zLOG import LOG,DEBUG,ERROR,INFO
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
import json

class SlapOSAgentDistributor(ERP5ProjectUnitTestDistributor):
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declarePublic("optimizeConfiguration")
  def optimizeConfiguration(self):
    """
    We are going to add test suites to test nodes.
    In the case of cloud performance, we associate all test suites to
    every test node. Like this, every test suite will be executed by
    every test node
    """
    test_node_module = self._getTestNodeModule()
    test_suite_module = self._getTestSuiteModule()
    test_node_list = [
        x.getObject() for x in test_node_module.searchFolder(
        portal_type="Test Node", validation_state="validated",
        specialise_uid=self.getUid())]

    test_suite_list = [x.getRelativeUrl()
                             for x in test_suite_module.searchFolder(
                             validation_state="validated",
                             specialise_uid=self.getUid())]
    for test_node in test_node_list:
      test_node.setAggregateList(test_suite_list)


  security.declarePublic("getTestType")
  def getTestType(self, batch_mode=0):
    """
    getTestType : return a string defining the type of tests
    """
    return 'SlapOSAgentTest'

  security.declarePublic("createTestResult")
  def createTestResult(self, name, revision, test_name_list, allow_restart,
                       test_title=None, node_title=None, project_title=None):
    """
    Here this is only a proxy to the task distribution tool
    """
    LOG('SlapOSAgentDistributor.createTestResult', INFO, (node_title, test_title, revision))
    portal = self.getPortalObject()
    if node_title:
      test_node = self._getTestNodeFromTitle(node_title)
      test_node.setPingDate()
    test_suite = self._getTestSuiteFromTitle(test_title)
    LOG('SlapOSAgentDistributor.createTestResult 2', INFO, (test_suite))
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
      #test_suite.setPingDate()
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
    LOG('SlapOSAgentDistributor._getTestSuiteFromTitle', INFO, (suite_title, self._getTestSuiteModule()))
    test_suite_list = self._getTestSuiteModule().searchFolder(
      portal_type='SlapOS Agent Test Suite',
      title=SimpleQuery(comparison_operator='=', title=suite_title),
      validation_state='validated',
      limit=2)
    assert len(test_suite_list) <= 1, "We found %i test suite for %s" % (
                                      len(test_suite_list), suite_title)
    test_suite = None
    if len(test_suite_list):
      test_suite = test_suite_list[0].getObject()
    return test_suite


  security.declarePublic("generateConfiguration")
  def generateConfiguration(self, test_suite_title, batch_mode=0):
    """
    generateConfiguration : not used for slapos agent
    """
    return json.dumps({"configuration_list": [{}]})

  security.declarePublic("getServiceList")
  def getServiceList(self, test_suite_title):
    """
    getServiceList : return a dict containing the list of services to request to slapos master before running the test
    """
    LOG('[SlapOSAgentDistributor] getServiceList', INFO, test_suite_title)
    test_suite_module = self._getTestSuiteModule()
    test_suite_list = test_suite_module.searchFolder(
                             title=test_suite_title,
                             validation_state="validated",
                             specialise_uid=self.getUid())
    service_list = {}
    if len(test_suite_list) == 0:
      error_message = 'Error getting test suite information. Bad test suite title? '
      LOG('[SlapOSAgentDistributor] getServiceList', ERROR, error_message)
      return json.dumps({'error_message': error_message})

    
    for unit_test in test_suite_list[0].searchFolder(
        portal_type="SlapOS Software Release Unit Test"):

      LOG('[SlapOSAgentDistributor] getServiceList, unit_test: ', INFO, unit_test.getTitle())
      service_list[unit_test.getTitle()] = {
        "title": unit_test.getTitle(),
        "url": unit_test.getUrlString(),
        "group": unit_test.getGroupReference("default"),
        "shared" : unit_test.getShared(),
        "software_type" : unit_test.getSoftwareType(),
        "partition_parameter_kw" : unit_test.getTextContent(),
        "filter_kw" : unit_test.getFilterKw()
        }

      if unit_test.getSupplyComputer() is not None:
        service_list[unit_test.getTitle()]['supply_computer'] = unit_test.getSupplyComputer()

    LOG('[SlapOSAgentDistributor] getServiceList, final service_list: ', INFO, service_list)
    return json.dumps(service_list)

  def _getSortedNodeTestSuiteToRun(self, test_node):
    """
    Returned ordered list of test suites of a test node.

    For now do nothing
    """
    test_suite_list = test_node.getAggregateValueList()
    return test_suite_list














