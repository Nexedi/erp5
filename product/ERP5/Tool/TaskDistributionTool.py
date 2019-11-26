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
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, NegatedQuery
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

  def _getTestNodeRelativeUrl(self, node_title):
    portal = self.getPortalObject()
    test_node_list = portal.portal_catalog(
        portal_type="Test Node",
        title=SimpleQuery(comparison_operator='=', title=node_title),
        limit=2
    )
    if len(test_node_list) == 1:
      return test_node_list[0].getRelativeUrl()

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
    # LOG('createTestResult', 0, (name, revision, test_title, project_title))
    portal = self.getPortalObject()
    if test_title is None:
      test_title = name
    def createNode(test_result, node_title):
      if node_title is not None:
        node = self._getTestResultNode(test_result, node_title)
        if node is None:
          # Note: specialise might not be set. This is on purpose, in order
          #       to support cases, when client will call createTestResult
          #       without calling subscribeNode before, and this is required
          #       to find Test Node document returned by
          #       _getTestNodeRelativeUrl.
          node = test_result.newContent(portal_type='Test Result Node',
                                 title=node_title,
                                 specialise=self._getTestNodeRelativeUrl(
                                   node_title))
          node.start()
    def createTestResultLineList(test_result, test_name_list):
      test_priority_list = []
      previous_test_result_list = portal.test_result_module.searchFolder(
             title=SimpleQuery(comparison_operator='=', title=test_result.getTitle()),
             sort_on=[('creation_date','descending')],
             simulation_state=('stopped', 'public_stopped'),
             limit=1)
      if len(previous_test_result_list):
        previous_test_result = previous_test_result_list[0].getObject()
        for line in previous_test_result.objectValues():
          if line.getSimulationState() in ('stopped', 'public_stopped'):
            # Execute first the tests that failed on previous run (so that we
            # can see quickly if a fix was effective) and the slowest tests (to
            # make sure slow tests are executed in parrallel and prevent
            # situations where at the end all test nodes are waiting for the
            # latest to finish).
            test_priority_list.append(
                (line.getStringIndex() == 'PASSED',
                 -line.getProperty('duration'),
                 line.getTitle()))
      sorted_test_list = [x[2] for x in sorted(test_priority_list)]
      # Sort tests by name to have consistent ids for test result line on a
      # test suite.
      for test_name in sorted(test_name_list):
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
    catalog_kw = {'portal_type': 'Test Result',
                  'title': SimpleQuery(comparison_operator='=', title=test_title),
                  'sort_on': (("creation_date","descending"),),
                  'simulation_state': NegatedQuery(SimpleQuery(simulation_state="cancelled")),
                  'limit': 1}
    result_list = portal.test_result_module.searchFolder(**catalog_kw)
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
          result_line_list = test_result.objectValues(portal_type="Test Result Line")
          result_line_list_len = len(result_line_list)
          if result_line_list_len == 0 and len(test_name_list):
            test_result.serialize() # prevent duplicate test result lines
            createTestResultLineList(test_result, test_name_list)
          elif result_line_list_len:
            # Do not process test result if all test result lines are already affected
            if len([x for x in result_line_list if x.getSimulationState() == 'draft']) == 0:
              return
          return test_result.getRelativeUrl(), last_revision
        if last_state in ('stopped', 'public_stopped'):
          if not allow_restart:
            if reference_list_string is not None:
              if reference_list_string == test_result.getReference():
                return
              # If we are here, latest test result might be an old revision created
              # by hand, then we should not test a newer revision already tested
              catalog_kw['simulation_state'] = ["stopped", "public_stopped"]
              if portal.test_result_module.searchFolder(
                   reference=SimpleQuery(comparison_operator='=', reference=reference_list_string),
                   **catalog_kw):
                return
            if last_revision == int_index:
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
        title=SimpleQuery(comparison_operator='=',
          title=project_title.encode('utf-8')))
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
  def startUnitTest(self, test_result_path, exclude_list=(), node_title=None):
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


    import random
#     line_list = test_result.searchFolder(portal_type="Test Result Line",
#                                          simulation_state="draft")
#     # Randomize to prevent all bot to generate DB conflict
#     random.shuffle(line_list)
#     for sql_line in line_list:
#       line = sql_line.getObject()
#       test = line.getTitle()
#       if test not in exclude_list:
#         state = line.getSimulationState()
#         if state == 'draft':
#           if node_title:
#             node = self._getTestNodeRelativeUrl(node_title)
#             line.setSource(node)
#           line.start()
#           return line.getRelativeUrl(), test


    line_id_list = [x for x in test_result.objectIds()]
    # Randomize to prevent all bot to generate DB conflict
    random.shuffle(line_id_list)
    for line_id in line_id_list:
      line = test_result[line_id]
      if (line.getPortalType() != 'Test Result Line'):
        continue
      test = line.getTitle()
      if test not in exclude_list:
        if line.getSimulationState() == 'draft':
          if node_title:
            node = self._getTestNodeRelativeUrl(node_title)
            line.setSource(node)
          line.start()
          return line.getRelativeUrl(), test



#     for line in test_result.objectValues(portal_type="Test Result Line",
#                                          sort_on=[("int_index","ascending")]):
#       test = line.getTitle()
#       if test not in exclude_list:
#         state = line.getSimulationState()
#         test = line.getRelativeUrl(), test
#         if state == 'draft':
#           if node_title:
#             node = self._getTestNodeRelativeUrl(node_title)
#             line.setSource(node)
#           line.start()
#           return test

  security.declarePublic('stopUnitTest')
  def stopUnitTest(self, test_path, status_dict, node_title=None):
    """(temporary)
      - test_path (string)
      - status_dict (dict)
    """
    status_dict = self._extractXMLRPCDict(status_dict)
    # LOG("TaskDistributionTool.stopUnitTest", 0, repr((test_path,status_dict)))
    portal = self.getPortalObject()
    line = portal.restrictedTraverse(test_path)
    test_result = line.getParentValue()
    if test_result.getSimulationState() == 'started':
      if line.getSimulationState() in ["draft", "started"]:
        line.stop(**status_dict)
      # Check by activity is all lines are finished. Do not check synchrnonously
      # in case another test line is stopped in parallel
      test_result.activate().TestResult_stopIfFinished()

  def _extractXMLRPCDict(self, xmlrpc_dict):
    """
    extract all xmlrpclib.Binary instance
    """
    return {x: y.data if isinstance(y, Binary) else y
       for x, y in xmlrpc_dict.iteritems()}

  security.declarePublic('reportTaskFailure')
  def reportTaskFailure(self, test_result_path, status_dict, node_title):
    """report failure when a node can not handle task
    """
    status_dict = self._extractXMLRPCDict(status_dict)
    # LOG("TaskDistributionTool.reportTaskFailure", 0, repr((test_result_path,
    #                                                      status_dict)))
    portal = self.getPortalObject()
    test_result = portal.restrictedTraverse(test_result_path)
    test_result_node = self._getTestResultNode(test_result, node_title)
    assert test_result_node is not None
    test_result_node.fail(**status_dict)
    # Redraft all test result lines that were affected to that test node
    # to allow immediate reexecution (useful in case of timeout raised
    # by a runTestSuite process)
    for line in test_result.objectValues(portal_type="Test Result Line"):
      if line.getSimulationState() == "started" and line.getSourceTitle() == node_title:
        line.redraft()
    # If all test nodes failed, we would like to cancel the test result, giving
    # opportunity to testnode to start working on a newer version of repository,
    # possibly coming with a fix avoiding current failure
    for test_result_node in test_result.objectValues(portal_type='Test Result Node'):
      if test_result_node.getSimulationState() != 'failed':
        break
    else:
      # now check if we had recent work on test line, if so, this means
      # we might just add timeout due to too much tests to execute for too
      # little nodes. In that case we would like to continue the work later
      recent_time = DateTime() - 1.0/24
      for test_result_line in test_result.objectValues(
          portal_type="Test Result Line"):
        if test_result_line.getModificationDate() >= recent_time:
          # do not take into account redrafted lines, this means we already
          # had issues with them (just one time, since we already redraft above)
          if len([x for x in portal.portal_workflow.getInfoFor(
                  ob=test_result_line,
                  name='history',
                  wf_id='test_result_workflow') if x['action']=='redraft']) <= 1:
            break
      else:
        if test_result.getSimulationState() not in ('failed', 'cancelled'):
          test_result.fail()

  security.declarePublic('reportTaskStatus')
  def reportTaskStatus(self, test_result_path, status_dict, node_title):
    """report status of node
    """
    status_dict = self._extractXMLRPCDict(status_dict)
    # LOG("TaskDistributionTool.reportTaskStatus", 0, repr((test_result_path,
    #                                                       status_dict)))
    portal = self.getPortalObject()
    test_result = portal.restrictedTraverse(test_result_path)
    node = self._getTestResultNode(test_result, node_title)
    assert node is not None
    node._edit(cmdline=status_dict['command'],
              stdout=status_dict['stdout'], stderr=status_dict['stderr'])

  security.declarePublic('isTaskAlive')
  def isTaskAlive(self, test_result_path):
    """check status of a test suite
    """
    # LOG("TaskDistributionTool.checkTaskStatus", 0, repr(test_result_path))
    portal = self.getPortalObject()
    test_result = portal.restrictedTraverse(test_result_path)
    return test_result.getSimulationState() == "started" and 1 or 0

  security.declareProtected(Permissions.AccessContentsInformation, 'getMemcachedDict')
  def getMemcachedDict(self):
    """ Return a dictionary used for non persistent data related to distribution
    """
    portal = self.getPortalObject()
    memcached_dict = portal.portal_memcached.getMemcachedDict(
                            "task_distribution", "default_memcached_plugin")
    return memcached_dict
