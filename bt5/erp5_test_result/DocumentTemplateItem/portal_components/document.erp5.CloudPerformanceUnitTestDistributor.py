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
from erp5.component.document.ERP5ProjectUnitTestDistributor import ERP5ProjectUnitTestDistributor
import json
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions

class CloudPerformanceUnitTestDistributor(ERP5ProjectUnitTestDistributor):

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.ManagePortal,
                            "cleanupInvalidatedTestNode")
  def cleanupInvalidatedTestNode(self, test_node):
    """
    When a test node is invalidated, we keep current configuration. Since
    all test nodes runs all test suites, this is not a problem to keep
    configuration
    """

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

  security.declarePublic("startTestSuite")
  def startTestSuite(self,title, computer_guid=None, **kw):
    """
    give the list of test suite to start. We will take all test suites
    associated to the testnode. Then we add the test node title to the
    test_suite_title to make sure that every test node will have it's
    own test result without the possibility that another one participate
    to the same test.
    """
    config_list = super(CloudPerformanceUnitTestDistributor,
                        self).startTestSuite(title, batch_mode=1)
    for config in config_list:
      config["test_suite_title"] = config["test_suite_title"] + "|%s" % title
    return json.dumps(config_list)

  security.declarePublic("generateConfiguration")
  def generateConfiguration(self, test_suite_title, batch_mode=0):
    """
    return the list of configuration to create instances, in the case of ERP5 unit tests,
    we will have only one configuration (unlike scalability tests). But for API consistency,
    always return a list.
    """
    # The test_suite_title parameter does not correspond exactly to the test
    # suite title present in ERP5, as this test is not supposed to share the
    # effort to run tests.
    return super(CloudPerformanceUnitTestDistributor, self) \
      .generateConfiguration("ERP5-Cloud-Reliability", batch_mode)

  def _getTestSuiteFromTitle(self, suite_title):
    return super(CloudPerformanceUnitTestDistributor,
                 self)._getTestSuiteFromTitle(suite_title.split("|")[0])
