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

  security.declarePublic("generateConfiguration")
  def generateConfiguration(self, test_suite_title, batch_mode=0):
    """
    generateConfiguration : this is just a proxy to an external method
    """
    test_suite_module = self._getTestSuiteModule()

    test_suite_list = test_suite_module.searchFolder(
                             title=test_suite_title,
                             validation_state="validated",
                             specialise_uid=self.getUid())
    if len(test_suite_list) == 0:
      return json.dumps({})

    generated_configuration = {}
    for unit_test in test_suite_list[0].searchFolder(
        portal_type="SlapOS Software Release Unit Test"):

      generated_configuration[unit_test.getTitle()] = {
        "title": unit_test.getTitle(),
        "url": unit_test.getUrlString(),
        "group": unit_test.getGroupReference("default")}

      if unit_test.getTextContent() is not None:
        generated_configuration[unit_test.getTitle()]['request_kw'] = unit_test.getTextContent()

      if unit_test.getSupplyComputer() is not None:
        generated_configuration[unit_test.getTitle()]['supply_computer'] = unit_test.getSupplyComputer()



    return json.dumps(generated_configuration)

















