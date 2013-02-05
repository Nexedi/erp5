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
    portal = self.getPortalObject()
    if test_title is None:
      test_title = name
    def createNode(test_result, node_title):
      if node_title is not None:
        node = self._getTestResultNode(test_result, node_title)
        if node is None:
          node = test_result.newContent(portal_type='Test Result Node',
                                 title=node_title)
          node.start()
    def createTestResultLineList(test_result, test_name_list):
      duration_list = []
      previous_test_result_list = portal.test_result_module.searchFolder(
             title='="%s"' % test_result.getTitle(),
             sort_on=[('creation_date','descending')],
             simulation_state='stopped',
             limit=1)
      if len(previous_test_result_list):
        previous_test_result = previous_test_result_list[0].getObject()
        for line in previous_test_result.objectValues():
          if line.getSimulationState() == 'stopped':
            duration_list.append((line.getTitle(),line.getProperty('duration')))
      duration_list.sort(key=lambda x: -x[1])
      sorted_test_list = [x[0] for x in duration_list]
      for test_name in test_name_list:
        index = 0
        if sorted_test_list:
          try:
            index = sorted_test_list.index(test_name)
          except ValueError:
            pass
        line = test_result.newContent(portal_type='Test Result Line',
                                      title=test_name,
                                      int_index=index)
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
    result_list = portal.test_result_module.searchFolder(
                         portal_type="Test Result",
                         title='="%s"' % test_title,
                         sort_on=(("creation_date","descending"),),
                         limit=1)
    if result_list:
      test_result = result_list[0].getObject()
      if test_result is not None:
        last_state = test_result.getSimulationState()
        last_revision = str(test_result.getIntIndex())
        if last_state == 'started':
          createNode(test_result, node_title)
          reference = test_result.getReference()
          if reference_list_string:
            last_revision = reference
          elif reference:
            last_revision = last_revision, reference
          if len(test_result.objectValues(portal_type="Test Result Line")) == 0 \
              and len(test_name_list):
            test_result.serialize() # prevent duplicate test result lines
            createTestResultLineList(test_result, test_name_list)
          return test_result.getRelativeUrl(), last_revision
        if last_state in ('stopped',):
          if reference_list_string is not None:
            if reference_list_string == test_result.getReference() \
                and not allow_restart:
              return
          elif last_revision == int_index and not allow_restart:
            return
    test_result = portal.test_result_module.newContent(
      portal_type='Test Result',
      title=test_title,
      reference=reference,
      is_indexable=False)
    if int_index is not None:
      test_result._setIntIndex(int_index)
    if project_title is not None:
      project_list = portal.portal_catalog(portal_type='Project',
                                           title='="%s"' % project_title)
      if len(project_list) != 1:
        raise ValueError('found this list of project : %r for title %r' % \
                      ([x.path for x in project_list], project_title))
      test_result._setSourceProjectValue(project_list[0].getObject())
    test_result.updateLocalRolesOnSecurityGroups() # XXX
    test_result.start()
    del test_result.isIndexable
    test_result.immediateReindexObject()
    self.serialize() # prevent duplicate test result
    # following 2 functions only call 'newContent' on test_result
    createTestResultLineList(test_result, test_name_list)
    createNode(test_result, node_title)
    return test_result.getRelativeUrl(), revision

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
    started_list = []
    for line in test_result.objectValues(portal_type="Test Result Line",
                                         sort_on=[("int_index","ascending")]):
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
    if test_result.getSimulationState() == 'started':
      if line.getSimulationState() == "started":
        line.stop(**status_dict)
      if set([x.getSimulationState() for x in test_result.objectValues(
                portal_type="Test Result Line")]) == set(["stopped"]):
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
      if test_result.getSimulationState() not in ('failed', 'cancelled'):
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

  security.declarePublic('isTaskAlive')
  def isTaskAlive(self, test_result_path):
    """check status of a test suite
    """
    LOG("TaskDistributionTool.checkTaskStatus", 0, repr(test_result_path))
    portal = self.getPortalObject()
    test_result = portal.restrictedTraverse(test_result_path)
    return test_result.getSimulationState() == "started" and 1 or 0

  security.declareObjectProtected(Permissions.AccessContentsInformation)
  def getMemcachedDict(self):
    """ Return a dictionary used for non persistent data related to distribution
    """
    portal = self.getPortalObject()
    memcached_dict = portal.portal_memcached.getMemcachedDict(
                            "task_distribution", "default_memcached_plugin")
    return memcached_dict
