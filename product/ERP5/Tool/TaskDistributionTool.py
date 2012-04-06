##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Julien Muchembled <jm@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import random
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5Type.Tool.BaseTool import BaseTool
from zLOG import LOG
from xmlrpclib import Binary

class TaskDistributionTool(BaseTool):
  """
  A Task distribution tool (used for ERP5 unit test runs).
  """

  id = 'portal_task_distribution'
  meta_type = 'ERP5 Task Distribution Tool'
  portal_type = 'Task Distribution Tool'
  allowed_types = ()

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def __init__(self, *args, **kw):
    BaseTool.__init__(self, *args, **kw)
    # XXX Cache information about running test results, because the protocol
    #     is synchronous and we can't rely on the catalog.
    #     This is a hack until a better (and asynchronous) protocol is
    #     implemented.
    self.test_result_dict = {}

  security.declarePublic('getProtocolRevision')
  def getProtocolRevision(self):
    """
    """
    return 1

  def _getTestResultNode(self, test_result, node_title):
    node_list = [x for x in test_result.objectValues(
       portal_type='Test Result Node') if x.getTitle() == node_title]
    node_list_len = len(node_list)
    assert node_list_len in (0, 1)
    node = None
    if len(node_list):
      node = node_list[0]
    return node

  security.declarePublic('createTestResult')
  def createTestResult(self, name, revision, test_name_list, allow_restart,
                       test_title=None, node_title=None, project_title=None):
    """(temporary)
      - name (string)
      - revision (string representation of an integer)
      - test_name_list (list of strings)
      - allow_restart (boolean)

      XXX 'revision' should be a string representing the full revision
          of the tested code, because some projects are tested with different
          revisions of ERP5.

      -> (test_result_path, revision) or None if already completed
    """
    LOG('createTestResult', 0, (name, revision, test_title, project_title))
    self._p_changed = 1
    portal = self.getPortalObject()
    if test_title is None:
      test_title = name
    test_result_path, line_dict = self.test_result_dict.get(
         test_title, ('', {}))
    duration_dict = {}
    def createNode(test_result, node_title):
      if node_title is not None:
        node = self._getTestResultNode(test_result, node_title)
        if node is None:
          node = test_result.newContent(portal_type='Test Result Node',
                                 title=node_title)
          node.start()
    def createTestResultLineList(test_result, test_name_list, line_dict):
      previous_test_result_list = portal.test_result_module.searchFolder(
             title='=%s' % test_result.getTitle(),
             sort_on=[('creation_date','descending')],
             simulation_state='stopped',
             limit=1)
      if len(previous_test_result_list):
        previous_test_result = previous_test_result_list[0].getObject()
        for line in previous_test_result.objectValues():
          if line.getSimulationState() == 'stopped':
            duration_dict[line.getTitle()] = line.getProperty('duration')
      for test_name in test_name_list:
        line = test_result.newContent(portal_type='Test Result Line',
                                      title=test_name)
        line_dict[line.getId()] = duration_dict.get(test_name)
    reference_list_string = None
    if type(revision) is str and '=' in revision:
      reference_list_string = revision
      int_index, reference = None, revision
    elif type(revision) is str:
      # backward compatibility
      int_index, reference = revision, None
    else:
      # backward compatibility
      int_index, reference = revision
    test_result = None
    if test_result_path:
      test_result = portal.unrestrictedTraverse(test_result_path, None)
      if test_result is None or test_result.getSimulationState() in \
               ('cancelled', 'failed'):
        del self.test_result_dict[test_title]
        line_dict = {}
      else:
        last_state = test_result.getSimulationState()
        last_revision = str(test_result.getIntIndex())
        if last_state == 'started':
          createNode(test_result, node_title)
          reference = test_result.getReference()
          if reference_list_string:
            last_revision = reference
          elif reference:
            last_revision = last_revision, reference
          if len(line_dict) == 0 and len(test_name_list):
            createTestResultLineList(test_result, test_name_list, line_dict)
          return test_result_path, last_revision
        if last_state == 'stopped':
          if reference_list_string is not None:
            if reference_list_string == test_result.getReference():
              return
          elif last_revision == int_index and not allow_restart:
            return
    test_result = portal.test_result_module.newContent(
      portal_type='Test Result',
      title=test_title,
      reference=reference,
      predecessor=test_result_path)
    if int_index is not None:
      test_result.setIntIndex(int_index)
    if project_title is not None:
      project_list = portal.portal_catalog(portal_type='Project',
                                           title='="%s"' % project_title)
      if len(project_list) == 1:
        test_result.setSourceProjectValue(project_list[0].getObject())
      else:
        raise ValueError('found this list of project : %r for title %r' % \
                      ([x.path for x in project_list], project_title))
    else:
      # Backward compatibility
      project = portal.ERP5Site_getProjectFromTestSuite(name)
      test_result.setSourceProjectValue(project)
    test_result.updateLocalRolesOnSecurityGroups() # XXX
    test_result_path = test_result.getRelativeUrl()
    self.test_result_dict[test_title] = test_result_path, line_dict
    test_result.start()
    createTestResultLineList(test_result, test_name_list, line_dict)
    createNode(test_result, node_title)
    return test_result_path, revision

  security.declarePublic('startUnitTest')
  def startUnitTest(self, test_result_path, exclude_list=()):
    """(temporary)
      - test_result_path (string)
      - exclude_list (list of strings)

      -> test_path (string), test_name (string)
         or None if finished
    """
    portal = self.getPortalObject()
    test_result = portal.restrictedTraverse(test_result_path)
    if test_result.getSimulationState() != 'started':
      return
    path, line_dict = self.test_result_dict[test_result.getTitle()]
    assert path == test_result_path
    started_list = []
    for line_id, duration in sorted(line_dict.iteritems(),
                                    key=lambda x: x[1], reverse=1):
      line = test_result[line_id]
      test = line.getTitle()
      if test not in exclude_list:
        state = line.getSimulationState()
        test = line.getRelativeUrl(), test
        if state == 'draft':
          line.start()
          return test
        # XXX Make sure we finish all tests.
        if state == 'started':
          started_list.append(test)
    if started_list:
      return random.choice(started_list)

  security.declarePublic('stopUnitTest')
  def stopUnitTest(self, test_path, status_dict):
    """(temporary)
      - test_path (string)
      - status_dict (dict)
    """
    status_dict = self._extractXMLRPCDict(status_dict)
    LOG("TaskDistributionTool.stopUnitTest", 0, repr((test_path,status_dict)))
    portal = self.getPortalObject()
    line = portal.restrictedTraverse(test_path)
    test_result = line.getParentValue()
    path, line_dict = self.test_result_dict[test_result.getTitle()]
    if test_result.getSimulationState() == 'started':
      assert path == test_result.getRelativeUrl()
      line_id = line.getId()
      if line_id in line_dict:
        line.stop(**status_dict)
        del line_dict[line_id]
        self._p_changed = 1
        if not line_dict:
          test_result.stop()

  def _extractXMLRPCDict(self, xmlrpc_dict):
    """
    extract all xmlrpclib.Binary instance
    """
    return dict([(x,isinstance(y, Binary) and y.data or y) \
       for (x, y) in xmlrpc_dict.iteritems()])

  security.declarePublic('reportTaskFailure')
  def reportTaskFailure(self, test_result_path, status_dict, node_title):
    """report failure when a node can not handle task
    """
    status_dict = self._extractXMLRPCDict(status_dict)
    LOG("TaskDistributionTool.reportTaskFailure", 0, repr((test_result_path,
                                                          status_dict)))
    portal = self.getPortalObject()
    test_result = portal.restrictedTraverse(test_result_path)
    node = self._getTestResultNode(test_result, node_title)
    assert node is not None
    node.fail(**status_dict)
    for node in test_result.objectValues(portal_type='Test Result Node'):
      if node.getSimulationState() != 'failed':
        break
    else:
      test_result.fail()

  security.declarePublic('reportTaskStatus')
  def reportTaskStatus(self, test_result_path, status_dict, node_title):
    """report status of node
    """
    status_dict = self._extractXMLRPCDict(status_dict)
    LOG("TaskDistributionTool.reportTaskStatus", 0, repr((test_result_path,
                                                          status_dict)))
    portal = self.getPortalObject()
    test_result = portal.restrictedTraverse(test_result_path)
    node = self._getTestResultNode(test_result, node_title)
    assert node is not None
    node.edit(cmdline=status_dict['command'],
              stdout=status_dict['stdout'], stderr=status_dict['stderr'])
