# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002,2005,2015 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import six
from Products.ERP5Type.Workflow import WorkflowHistoryList as NewWorkflowHistoryList

class WorkflowHistoryList(NewWorkflowHistoryList):

  __init__ = None

  def __getstate__(self):
    return self._prev, self._log

  def __bool__(self):
    # not faster than __len__ but avoids migration
    if self._log:
      return True
    assert self._prev is None
    return False

  if six.PY2:
    __nonzero__ = __bool__

  @property
  def _rotate(self):
    self._migrate()
    return self._rotate

  @property
  def _next(self):
    self._migrate()
    return self._next

  @property
  def _tail_count(self):
    self._migrate()
    return self._tail_count

  def _migrate(self):
    self.__class__ = NewWorkflowHistoryList
    bucket = self._prev
    if bucket is None:
      del self._prev
      return
    stack = [self]
    while True:
      stack.append(bucket)
      bucket._p_activate()
      assert bucket.__class__ is WorkflowHistoryList, bucket.__class__
      bucket.__class__ = NewWorkflowHistoryList
      bucket = bucket._prev
      if bucket is None:
        break
    self._next = bucket = stack.pop()
    count = len(bucket._log)
    while True:
      bucket._next = bucket = stack.pop()
      bucket._tail_count = count
      if bucket is self:
        break
      count += len(bucket._log)

# BBB: A production instance used a temporary patch to speed up.
WorkflowHistoryBucketList = WorkflowHistoryList

from Products.ERP5Type import WITH_LEGACY_WORKFLOW
if WITH_LEGACY_WORKFLOW:
  import six
  from zLOG import LOG, WARNING
  from types import StringTypes

  # Make sure Interaction Workflows are called even if method not wrapped

  from AccessControl import ClassSecurityInfo, Unauthorized
  from Products.ERP5Type.Globals import InitializeClass
  from Products.CMFCore.WorkflowTool import WorkflowTool
  from Products.CMFCore.WorkflowCore import ObjectDeleted
  from Products.CMFCore.WorkflowCore import WorkflowException
  from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
  from Products.DCWorkflow.Transitions import TRIGGER_WORKFLOW_METHOD
  from Products.DCWorkflow.utils import Message as _
  from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION

  from Products.CMFCore.utils import getToolByName
  from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, AutoQuery, ComplexQuery, NegatedQuery
  from Products.CMFCore.utils import _getAuthenticatedUser
  from Products.ERP5Type import Permissions
  from Products.ERP5Type.Cache import CachingMethod
  from sets import ImmutableSet
  from Acquisition import aq_base
  from Products.ERP5Type.Globals import PersistentMapping
  from MySQLdb import ProgrammingError, OperationalError
  from DateTime import DateTime

  security = ClassSecurityInfo()
  WorkflowTool.security = security

  WORKLIST_METADATA_KEY = 'metadata'
  SECURITY_PARAMETER_ID = 'local_roles'

  def WorkflowTool_getChainDict(self):
      """Test if the given transition exist from the current state.
      """
      chain_dict = {}
      for portal_type, wf_id_list in six.iteritems(self._chains_by_type):
          for wf_id in wf_id_list:
              chain_dict.setdefault(wf_id, []).append(portal_type)
      return chain_dict

  security.declareProtected(Permissions.ManagePortal, 'getChainDict')
  WorkflowTool.getChainDict = WorkflowTool_getChainDict

  # Backward compatibility, as WorkflowMethod has been removed in CMFCore 2.2
  from MethodObject import Method
  class WorkflowMethod( Method ):

      """ Wrap a method to workflow-enable it.
      """
      _need__name__=1

      def __init__(self, method, id=None, reindex=1):
          self._m = method
          if id is None:
              id = method.__name__
          self._id = id
          # reindex ignored since workflows now perform the reindexing.

      def __call__(self, instance, *args, **kw):

          """ Invoke the wrapped method, and deal with the results.
          """
          wf = getToolByName(instance, 'portal_workflow', None)
          if wf is None or not hasattr(wf, 'wrapWorkflowMethod'):
              # No workflow tool found.
              try:
                  res = self._m(instance, *args, **kw)
              except ObjectDeleted as ex:
                  res = ex.getResult()
              else:
                  if hasattr(aq_base(instance), 'reindexObject'):
                      instance.reindexObject()
          else:
              res = wf.wrapWorkflowMethod(instance, self._id, self._m,
                                          (instance,) + args, kw)

  from Products.CMFCore import WorkflowCore
  # BBB: WorkflowMethod has been removed from CMFCore 2
  WorkflowCore.WorkflowAction = WorkflowMethod

  # XXX: Kept here instead of ERP5Type.Tool.WorkflowTool because not used in
  # erp5.git: is it used in projects?
  security.declarePublic('canDoActionFor')
  def canDoActionFor(self, ob, action, wf_id=None, guard_kw={}):
    """ Check we can perform the given workflow action on 'ob'.
    """
    if wf_id is None:
      workflow_list = self.getWorkflowValueListFor(ob) or ()
    else:
      workflow = self._getOb(wf_id, None)
      if workflow:
        workflow_list = (workflow,)
      else:
        workflow_list = ()

    for workflow in workflow_list:
      state_definition = workflow._getWorkflowStateOf(ob)
      if state_definition is not None:
        if action in state_definition.transitions:
          transition_definition = workflow.transitions.get(action, None)
          if transition_definition is not None and \
            transition_definition.trigger_type == TRIGGER_USER_ACTION:
            return workflow._checkTransitionGuard(transition_definition, ob, **guard_kw)

    raise WorkflowException(_(u"No workflow provides the '${action_id}' action.",
            mapping={'action_id': action}))
  WorkflowTool.canDoActionFor = canDoActionFor

  security.declarePrivate('_listTypeInfo')
  def _listTypeInfo(self):
      """ List the portal types which are available.
      """
      # <patch>
      ttool = getattr(self.getPortalObject(), "portal_types", None)
      # </patch>
      if ttool is not None:
          return ttool.listTypeInfo()
      return ()

  WorkflowTool._listTypeInfo = _listTypeInfo

  ## From here on: migration/compatibility code DCWorkflow => ERP5 Workflow

  # The following 2 functions are necessary for workflow tool dynamic migration
  def WorkflowTool_isBootstrapRequired(self):
    # migration is required if the tool is not the new one from ERP5 Workflow
    # in case of old workflow tool, it acquires the portal type from ERP5 Site
    return self.getPortalType() != "Workflow Tool"

  def WorkflowTool_bootstrap(self):
    """
    Migrate portal_workflow from CMFCore to ERP5 Workflow. Also migrate
    Workflow Chains not defined anymore on portal_workflow but on the Portal
    Type.

    Like other Tools migrations (ERP5CatalogTool...), this is called at
    startup by synchronizeDynamicModules(), thus Workflows are *not* migrated
    from DCWorkflow to ERP5 Workflow (ERP5 Workflow portal_workflow can work
    with both DCWorkflows and ERP5 Workflows), because this is not needed at
    this stage (handled by bt5 upgrade) and avoid making bootstrap more
    complicated than it already is.
    """
    from Products.ERP5Type.Tool.WorkflowTool import WorkflowTool
    if not isinstance(self, WorkflowTool):
      LOG('WorkflowTool', 0, 'Migrating portal_workflow')
      portal = self.getPortalObject()

      # CMFCore portal_workflow -> ERP5 Workflow portal_workflow
      from Products.ERP5.ERP5Site import addERP5Tool
      addERP5Tool(portal, 'portal_workflow_new', 'Workflow Tool')
      new_tool = portal._getOb("portal_workflow_new")
      new_tool._chains_by_type = self._chains_by_type

      for workflow_id, workflow in self.objectItems():
        workflow_copy = workflow._getCopy(new_tool)
        workflow_copy._setId(workflow_id)
        new_tool._setObject(workflow_id, workflow_copy)

        workflow_copy = new_tool._getOb(workflow_id)
        workflow_copy._postCopy(new_tool, op=0)
        workflow_copy.wl_clearLocks()

      portal.portal_workflow = new_tool
      portal.portal_workflow.id = 'portal_workflow'
      portal._delObject('portal_workflow_new')

      # Migrate Workflow Chains to Portal Types
      if getattr(new_tool, '_chains_by_type', None) is not None:
        new_tool.reassignWorkflowWithoutConversion()

  WorkflowTool._isBootstrapRequired = WorkflowTool_isBootstrapRequired
  WorkflowTool._bootstrap = WorkflowTool_bootstrap
  WorkflowTool.getWorkflowValueListFor = WorkflowTool.getWorkflowsFor

  def _deleteChainsByType(self, pt, wf_id):
    self._chains_by_type[pt] = tuple(wf for wf in self._chains_by_type[pt] if wf!=wf_id)
  def getChainsByType(self):
    # XXX(WORKFLOW): compatibility code
    # get old workflow tool's chains_by_type
    if self._chains_by_type is None:
      return {}
    return self._chains_by_type.copy()
  WorkflowTool.getChainsByType = getChainsByType
  def reassignWorkflow(self, workflow_id):
    # type-workflow reassignment
    type_workflow_dict = self.getChainsByType()
    type_tool = self.getPortalObject().portal_types

    for portal_type_id in type_workflow_dict:
      # getTypeInfo takes care of solver, whereas _getOb on Types Tool don't
      portal_type = type_tool.getTypeInfo(portal_type_id)
      if portal_type is not None and workflow_id in type_workflow_dict[portal_type_id]:
        # 1. clean DC workflow tool "chain by type" assignement:
        _deleteChainsByType(self, portal_type_id, workflow_id)
        # 2. assign workflow to portal type:
        type_workflow_list = portal_type.getTypeWorkflowList()
        if workflow_id not in type_workflow_list:
          portal_type.setTypeWorkflowList(
            type_workflow_list + [workflow_id]
          )
  WorkflowTool.reassignWorkflow = reassignWorkflow
  def reassignWorkflowWithoutConversion(self):
    # This function should be called when a new template installed and add
    # portal_types assignment with converted and non-converted workflows into
    # portal_type's workflow list.
    # This function only synchronize assignment information to new added portal
    # type's TypeWorkflowList.

    # To trigger this function, go to portal_workflow and choose "convert DCWorkflow"
    # in the action list. Reassignment happens in the background. Nothing need to
    # be done, just go back to whatever you are doing.
    type_workflow_dict = self.getChainsByType()
    type_tool = self.getPortalObject().portal_types
    for portal_type_id in type_workflow_dict:
      portal_type = type_tool.getTypeInfo(portal_type_id)
      if portal_type is not None:
        for workflow_id in type_workflow_dict[portal_type_id]:
          workflow = getattr(self, workflow_id, None)
          if (workflow is not None and
              workflow.getPortalType() in ('Workflow',
                                          'Interaction Workflow',
                                          'DCWorkflowDefinition',
                                          'InteractionWorkflowDefinition')):
            # 1. clean DC workflow tool "chain by type" assignement:
            _deleteChainsByType(self, portal_type.getId(), workflow.id)
            # 2. assign workflow to portal type:
            type_workflow_list = portal_type.getTypeWorkflowList()
            if workflow_id not in type_workflow_list:
              portal_type.setTypeWorkflowList(
                type_workflow_list + [workflow_id]
              )
  WorkflowTool.reassignWorkflowWithoutConversion = reassignWorkflowWithoutConversion
  WorkflowTool.security.declareProtected(Permissions.AccessContentsInformation,
                                        'getWorkflowTempObjectList')
  def getWorkflowTempObjectList(self, temp_object=1, **kw):
    """ Return a list of converted temporary workflows. Only necessary in
        Workflow Tool to get temporarilly converted DCWorkflow.
    """
    temp_workflow_list = []
    for dc_workflow in self.objectValues():
      workflow_type = dc_workflow.__class__.__name__
      if workflow_type in ['Workflow', 'Interaction Workflow']:
        continue
      temp_workflow = dc_workflow.convertToERP5Workflow(temp_object=temp_object)
      temp_workflow_list.append(temp_workflow)
    return temp_workflow_list
  WorkflowTool.getWorkflowTempObjectList = getWorkflowTempObjectList

  InitializeClass(WorkflowTool)
