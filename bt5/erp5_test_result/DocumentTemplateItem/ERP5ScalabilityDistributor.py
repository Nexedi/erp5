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

from Products.ERP5.Document.ERP5ProjectUnitTestDistributor import ERP5ProjectUnitTestDistributor
import string
import erp5.util.taskdistribution
from Products.ERP5Type.Log import log


from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
import json
import random 

from Products.ERP5.Tool.TaskDistributionTool import TaskDistributionTool


class ERP5ScalabilityDistributor(ERP5ProjectUnitTestDistributor):
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.ManagePortal, "optimizeConfiguration")
  def optimizeConfiguration(self):
    """
    Do master testnode selection and associate testsuites.
    """

    # Get modules
    portal = self.getPortalObject()
    test_node_module = self._getTestNodeModule()
    test_suite_module = self._getTestSuiteModule()

    # Get lists of test node wich belong to the current distributor
    all_test_node_list = test_node_module.searchFolder(
        portal_type="Test Node", specialise_uid=self.getUid())
    test_node_list = [ x.getObject() for x in all_test_node_list if x.getValidationState() == 'validated' ]
    invalid_test_node_list = [ x.getObject() for x in all_test_node_list if x.getValidationState() != 'validated' ]

    # Set master property to False for all invalid testnode
    for node in invalid_test_node_list:
      node.setMaster(False)

    # Get all valid slave testnodes
    slave_test_node_list = [ x.getObject() for x in test_node_list if x.getMaster()!=True ]
    master_test_node_list = [ x.getObject() for x in test_node_list if x.getMaster()==True ]

    # Set to 'False' slaves
    for node in slave_test_node_list:
      node.setMaster(False)


    # if there is validated testnodes
    if len(test_node_list) > 0:
      # Only one testnode must be the master
      # if there is no or more than 1 master
      if len(master_test_node_list) != 1:
        # No master: elect the first testnode as master
        if len(master_test_node_list) == 0:
          test_node_list[0].setMaster(True)
        else:
          # Too many master: keep as master only the the first of list
          for node in master_test_node_list[1:]:
            node.setMaster(False)
 
    # Update testnode lists
    slave_test_node_list = [ x.getObject() for x in test_node_list if x.getMaster()!=True ]
    master_test_node_list = [ x.getObject() for x in test_node_list if x.getMaster()==True ]

    # Get test suites and aggregate them to all valid testnode
    test_suite_list = [ x.getRelativeUrl() for x in test_suite_module.searchFolder(
                        portal_type="Scalability Test Suite",
                        validation_state="validated", specialise_uid=self.getUid())]
    for test_node in test_node_list:
      test_node.setAggregateList(test_suite_list)

  security.declarePublic("getInvolvedNodeList")
  def getInvolvedNodeList(self):
    """
    getInvolvedNodeList doc
    """
    test_node_module = self._getTestNodeModule()
    distributor_title = self.getTitle()
    involved_nodes = []   
    involved_nodes = involved_nodes + [ x.getObject() for x in test_node_module.searchFolder(validation_state='validated') if ( x.getSpecialiseTitle() == distributor_title ) ]
    return involved_nodes

  security.declarePublic("getTestNode")
  def getTestNode(self,title,batch_mode=0):
    """
    getTestNode doc
    """
    test_node_module = self._getTestNodeModule()
    portal = self.getPortalObject()

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
      return test_node
    return None

  security.declarePublic("isMasterTestnode")
  def isMasterTestnode(self,title, batch_mode=0):
    """
    isMasterTestnode : return True if the node given in parameter exists and is a validated master
    """
    test_node_module = self._getTestNodeModule()
    test_node_master = [ node for node in test_node_module.searchFolder(portal_type="Test Node", title=title,
                                      specialise=self.getRelativeUrl(),
                                      validation_state="validated") if node.getMaster() == 1 ]
    if len(test_node_master) == 1:
      return True
    else:
      return False
    

  security.declarePublic("getTestType")
  def getTestType(self, batch_mode=0):
    """
    getTestType : return a string defining the type of tests
    """
    return 'ScalabilityTest'


  security.declarePublic("startTestSuite")
  def startTestSuite(self,title, batch_mode=0, computer_guid='unknown'):
    """
    startTestSuite : subscribe node + return testsuite list to the master
    """
    config_list = []
    test_node = self.getTestNode(title,batch_mode)
    test_suite_module =  self._getTestSuiteModule()
    test_node_module =  self._getTestNodeModule()
    portal = self.getPortalObject()

    # If the testnode wich request testsuites is not the master
    # he does not have to receive any testsuites
    master_test_node_title = [x.getTitle() for x in test_node_module.searchFolder(
                validatation_state = 'validated') if (x.getMaster() == True) ][0]
    
    if title == master_test_node_title:
      return super(ERP5ScalabilityDistributor,
                        self).startTestSuite(title=title, batch_mode=batch_mode, computer_guid=computer_guid)
    else:
      if batch_mode:
        return []
      return json.dumps([])


  security.declarePublic("generateConfiguration")
  def generateConfiguration(self, test_suite_title, batch_mode=0):
    """
    generateConfiguration : this is just a proxy to an external method
    """
    generated_configuration = self.ScalabilityTestSuiteUtils_generateConfigurationList(self, test_suite_title)
    if batch_mode:
      return generated_configuration
    return json.dumps(generated_configuration)

  def getRunningTestCase(self, test_result_path, batch_mode=0):
    """
    getRunningTestCase : return informations about the running test case,
              if no running test_case, return None
    """
    test_result = self.getTestResult(test_result_path)
    test_result_lines = test_result.objectValues(portal_type="Test Result Line",
                                                  sort_on='int_index')
    count = 0
    for test_result_line in test_result_lines:
      count += 1
      state = test_result_line.getSimulationState()
      if state == "started":
        relative_path = test_result_line.getRelativeUrl()
        title = test_result_line.getTitle()
        break;
    else:
      return None

    next_test = {"relative_path": relative_path,
                 "title": title, "count" : count,
                }

    if batch_mode:
      return next_test
    return json.dumps(next_test)

  security.declarePublic("isTestCaseAlive")
  def isTestCaseAlive(self, test_result_line_path, batch_mode=0):
    """
    Is a test result line alive or not.
    """
    portal = self.getPortalObject()
    test_result_line = portal.restrictedTraverse(test_result_line_path)
    return test_result_line.getSimulationState() == "started"