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
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery
from zLOG import LOG,ERROR

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
import json
import jinja2
from Products.ERP5.Tool.TaskDistributionTool import TaskDistributionTool

class ERP5ScalabilityDistributor(ERP5ProjectUnitTestDistributor, object):
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.ManagePortal, "optimizeConfiguration")
  def optimizeConfiguration(self):
    """
    Do master testnode selection and associate testsuites.
    """
    # Get modules
    test_node_module = self._getTestNodeModule()
    test_suite_module = self._getTestSuiteModule()

    # Get lists of test node wich belong to the current distributor
    all_test_node_list = test_node_module.searchFolder(
        portal_type="Test Node", specialise_uid=self.getUid())
    test_node_list = [ x.getObject() for x in all_test_node_list
                        if x.getValidationState() == 'validated' ]
    invalid_test_node_list = [ x.getObject() for x in all_test_node_list
                                if x.getValidationState() != 'validated' ]

    # Set master property to False for all invalid testnode
    for node in invalid_test_node_list:
      node.setMaster(False)

    # Get all valid slave testnodes
    slave_test_node_list = [ x.getObject() for x in test_node_list
                              if x.getMaster()!=True ]
    master_test_node_list = [ x.getObject() for x in test_node_list
                               if x.getMaster()==True ]

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
    slave_test_node_list = [ x.getObject() for x in test_node_list
                              if x.getMaster()!=True ]
    master_test_node_list = [ x.getObject() for x in test_node_list
                               if x.getMaster()==True ]

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
    involved_nodes = [ x.getObject() for x in test_node_module.searchFolder(
                       validation_state='validated')
                       if ( x.getSpecialiseTitle() == distributor_title ) ]
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
      test_node_list = test_node_module.searchFolder(
        portal_type="Test Node",
        title=SimpleQuery(comparison_operator='=', title=title),
      )
      assert len(test_node_list) in (0, 1), "Unable to find testnode : %s" % title
      test_node = None
      if len(test_node_list) == 1:
        test_node = test_node_list[0].getObject()
        if test_node.getValidationState() != 'validated':
          try:
            test_node.validate()
          except Exception, e:
            LOG('Test Node Validate',ERROR,'%s' %e)
      return test_node
    return None

  security.declarePublic("isMasterTestnode")
  def isMasterTestnode(self,title, batch_mode=0):
    """
    isMasterTestnode : return True if the node given in
    parameter exists and is a validated master
    """
    test_node_module = self._getTestNodeModule()
    test_node_master = [ node for node in test_node_module.searchFolder(
                              portal_type="Test Node",
                              title=SimpleQuery(comparison_operator='=', title=title),
                              specialise_uid=self.getUid(),
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

  security.declarePublic("createTestResult")
  def createTestResult(self, name, revision, test_name_list, allow_restart,
                       test_title=None, node_title=None, project_title=None):
    """
    Here this is only a proxy to the task distribution tool
    """
    LOG('[ERP5ScalabilityDistributor] createTestResult', 0, (node_title, test_title))
    portal = self.getPortalObject()
    created_test_result_tuple = portal.portal_task_distribution.createTestResult(name,
         revision, test_name_list, allow_restart,
         test_title=test_title, node_title=node_title,
         project_title=project_title)
    if created_test_result_tuple is not None:
      # set int_index which is used for sorting to the title of the test case
      # in created_test_result_tuple we have test result relative url and revision
      test_result = portal.restrictedTraverse(created_test_result_tuple[0])
      for test_result_line in test_result.objectValues(portal_type = "Test Result Line"):
        test_result_line.setIntIndex(int(test_result_line.getTitle()))

      return created_test_result_tuple

  security.declarePublic("startTestSuite")
  def startTestSuite(self,title, computer_guid='unknown', batch_mode=0):
    """
    startTestSuite : subscribe node + return testsuite list to the master
    """
    super(ERP5ScalabilityDistributor, self).subscribeNode(
      title=title, computer_guid=computer_guid, batch_mode=batch_mode)
    test_node_module =  self._getTestNodeModule()

    # If the testnode wich request testsuites is not the master
    # he does not have to receive any testsuites
    master_test_node_title_list = [x.getTitle() for x in test_node_module.searchFolder(
                                                            validation_state = 'validated',
                                                            specialise_uid=self.getUid())
                                   if (x.getMaster() == True) ]
    if len(master_test_node_title_list) == 1 and title == master_test_node_title_list[0]:
      return super(ERP5ScalabilityDistributor,
                   self).startTestSuite(title=title,
                                        batch_mode=batch_mode)
    else:
      if batch_mode:
        return []
      return json.dumps([])

  security.declarePublic("generateConfiguration")
  def generateConfiguration(self, test_suite_title, batch_mode=0):
    """
    generateConfiguration : this is just a proxy to an external method
    """
    portal = self.getPortalObject()
    generated_configuration = self._generateConfigurationList(test_suite_title, portal)
    if batch_mode:
      return generated_configuration
    return json.dumps(generated_configuration)

  def getRunningTestCase(self, test_result_path, batch_mode=0):
    """
    getRunningTestCase : return informations about the running test case,
              if no running test_case, return None
    """
    portal = self.getPortalObject()
    test_result = portal.restrictedTraverse(test_result_path)
    test_result_lines = test_result.objectValues(portal_type="Test Result Line",
                                                  sort_on='int_index')
    count = 0
    for test_result_line in test_result_lines:
      count += 1
      state = test_result_line.getSimulationState()
      if state == "started":
        relative_path = test_result_line.getRelativeUrl()
        title = test_result_line.getTitle()
        break
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

  security.declarePublic("_unvalidateConfig")
  def _unvalidateConfig(self, my_dict):
    my_dict['launchable'] = False
    if 'launcher_nodes_computer_guid' in my_dict:
      my_dict['launcher_nodes_computer_guid'] = {}
    if 'involved_nodes_computer_guid' in my_dict:
      my_dict['involved_nodes_computer_guid'] = {}
    if 'configuration_list' in my_dict:
      my_dict['configuration_list'] = []

  security.declarePublic("_getInvolvedNodes")
  def _getInvolvedNodes(self, available_nodes, return_dict):
    """
    Get the list of all nodes involved in the test
    """
    def _isContained(my_value, my_container):
      def _isInMyDictOrList(current_container):
        if current_container == my_value :
          return True
        elif isinstance(current_container, dict):
          for k,v in current_container.items():
            if str(my_value) in str(k):
              return True
            if _isInMyDictOrList(current_container[k]) :
              return True
        elif isinstance(current_container, list):
          for sub_container in current_container:
            if _isInMyDictOrList(sub_container) :
              return True
        return False
      return _isInMyDictOrList(my_container)

    involved_nodes_computer_guid = []
    for node in available_nodes:
      if _isContained(node, return_dict):
        involved_nodes_computer_guid.append(node)
    return involved_nodes_computer_guid

  security.declarePublic("_getAvailableNodes")
  def _getAvailableNodes(self, test_suite_specialise_title, portal):
    """
    gets testnodes available for this distributor
    """
    distributor_uid = self.getUid()
    test_node_module = portal.test_node_module
    available_nodes = test_node_module.searchFolder(
            portal_type="Test Node", validation_state="validated",
            specialise_uid=distributor_uid)
    available_nodes = [ node.getComputerGuid() for node in available_nodes ]
    return available_nodes

  security.declarePublic("_generateConfigurationList")
  def _generateConfigurationList(self, test_suite_title, portal):
    """
    generateConfigurationList : generate a dict wich contains a list
    of cluster configurations for testnodes, using a test_suite and
    available testnodes.
    If it is not possible to generate a configuration, the 'launchable'
    entry is False, otherwise it is True.
    """
    return_dict = {}
    # Get test_suite informations from his title given in parameter
    try:
      test_suite = portal.test_suite_module.searchFolder(
                                              title=test_suite_title,
                                              validation_state="validated")[0]
      cluster_configuration = test_suite.getClusterConfiguration()
      number_configuration_list = test_suite.getGraphCoordinate()
      randomized_path = test_suite.getRandomizedPath()
    except Exception as e:
      return_dict['error_message'] = 'Error getting test suite information. \
                                      Bad test suite title? ' + str(e)
      self._unvalidateConfig(return_dict)
      return return_dict

    try:
      available_nodes = self._getAvailableNodes(test_suite.getSpecialiseTitle(), portal)
      remaining_nodes = list(available_nodes)
      launcher_nodes = [ remaining_nodes.pop() ]
      if len(remaining_nodes) == 0: # if there is only one computer, use launcher
        remaining_nodes.append(launcher_nodes[0])
    except Exception:
      return_dict['error_message'] = 'Error getting available nodes. \
                                      No test nodes for test suite?'
      self._unvalidateConfig(return_dict)
      return return_dict

    configuration_list_json = []
    return_dict['error_message'] = 'No error.'
    return_dict['randomized_path'] = randomized_path

    try:
      template = jinja2.Template(cluster_configuration)
      for index in xrange(0, len(number_configuration_list)):
        template_vars = { "count" : number_configuration_list[index],
                          "comp" : remaining_nodes }
        configuration_list_json.append( json.loads(
                                          template.render(template_vars)
                                        )
                                      )
      return_dict['launchable'] = True
      return_dict['configuration_list'] = configuration_list_json
      return_dict['launcher_nodes_computer_guid'] = launcher_nodes
    except Exception:
      return_dict['error_message'] = 'Bad json cluster_configuration?'
      self._unvalidateConfig(return_dict)
      return return_dict

    return_dict['involved_nodes_computer_guid'] = self._getInvolvedNodes(available_nodes,
                                                                         return_dict)
    return return_dict
