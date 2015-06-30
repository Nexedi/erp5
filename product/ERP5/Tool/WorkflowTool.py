# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Nexedi SARL and Contributors. All Rights Reserved.
#                    Wenjie Zheng <wenjie.zheng@tiolive.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import cPickle
import os
import shutil
import sys
import subprocess
import time
import transaction
import struct
import urllib2
import re

from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.SecurityInfo import ModuleSecurityInfo
from Acquisition import aq_base, Implicit, Explicit
from App.config import getConfiguration
from base64 import b64encode, b64decode, decodestring
from cStringIO import StringIO
from DateTime import DateTime
from itertools import izip
from MethodObject import Method
from MySQLdb import ProgrammingError, OperationalError
from Persistence import Persistent
from Products.CMFActivity.ActiveResult import ActiveResult
from Products.CMFCore.utils import Message as _
from Products.CMFCore.utils import getToolByName, _getAuthenticatedUser
from Products.CMFCore.WorkflowTool import WorkflowTool as OriginalWorkflowTool
from Products.CMFCore.WorkflowCore import ObjectMoved, ObjectDeleted,\
                                          WorkflowException
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.Transitions import TRIGGER_WORKFLOW_METHOD
from Products.ERP5 import _dtmldir
from Products.ERP5.Document.BusinessTemplate import BusinessTemplateMissingDependency
from Products.ERP5.genbt5list import generateInformation
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Base import Base
from Products.ERP5Type.Cache import transactional_cached, CachingMethod
from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Type.DiffUtils import DiffFile
from Products.ERP5Type.Globals import InitializeClass, DTMLFile, PersistentMapping
from Products.ERP5Type.Message import translateString
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type.UnrestrictedMethod import unrestricted_apply
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, AutoQuery, ComplexQuery, NegatedQuery
from sets import ImmutableSet
from tempfile import mkstemp, mkdtemp
from types import StringTypes
from urllib import pathname2url, urlopen, splittype, urlretrieve
from xml.dom.minidom import parse
from xml.parsers.expat import ExpatError
from webdav.client import Resource
from zLOG import LOG, INFO, WARNING

"""
Most of the codes in this file are copy-pasted from patches/WorkflowTool.py.
"""

_marker = []  # Create a new marker object.

class WorkflowTool(BaseTool, OriginalWorkflowTool):
  """
  A new container for DC workflow and workflow;
  inherits methods from original WorkflowTool.py;
  contains patches from ERP5Type/pateches/WorkflowTool.py.
  """

  id            = 'portal_workflow'
  title         = 'Workflow Tool'
  meta_type     = 'Workflow Tool'
  portal_type   = 'Workflow Tool'
  allowed_types = ('Workflow', 'Interaction Workflow', 'Configuration Workflow' )
  all_meta_types = OriginalWorkflowTool.all_meta_types

  # This stores information on repositories.
  repository_dict = {}

  # Declarative Security
  security = ClassSecurityInfo()

  manage_options = OriginalWorkflowTool.manage_options
  manage_overview = OriginalWorkflowTool.manage_overview
  _manage_selectWorkflows = OriginalWorkflowTool._manage_selectWorkflows
  manage_selectWorkflows = OriginalWorkflowTool.manage_selectWorkflows
  manage_changeWorkflows = OriginalWorkflowTool.manage_changeWorkflows
  # Declarative properties
  property_sheets = (
    PropertySheet.Base,
    PropertySheet.XMLObject,
    PropertySheet.CategoryCore,
    PropertySheet.DublinCore,
  )

  def _jumpToStateFor(self, ob, state_id, wf_id=None, *args, **kw):
    """Inspired from doActionFor.
    This is public method to allow passing meta transition (Jump form
    any state to another in same workflow)
    """
    from Products.ERP5.InteractionWorkflow import InteractionWorkflowDefinition
    from Products.ERP5Workflow.Document.InteractionWorkflow import InteractionWorkflow
    workflow_list = self.getWorkflowValueListFor(ob.getPortalType())
    if wf_id is None:
      if not workflow_list:
        raise WorkflowException('No workflows found.')
      found = False
      for workflow in workflow_list:
        if not isinstance(workflow, InteractionWorkflowDefinition) and \
            not isinstance(workflow, InteractionWorkflow):
          if state_id in workflow.getStateIdList():
            found = True
            break
      if not found:
        raise WorkflowException('No workflow provides the destination state %r'\
                                                                      % state_id)
    else:
      workflow = self.getWorkflowById(wf_id)
      if workflow is None:
        raise WorkflowException('Requested workflow definition not found.')

    workflow._executeMetaTransition(ob, state_id)

  def _isJumpToStatePossibleFor(self, ob, state_id, wf_id=None):
    """Test if given state_id is available for ob
    in at least one associated workflow
    """
    from Products.ERP5.InteractionWorkflow import InteractionWorkflowDefinition
    from Products.ERP5Workflow.Document.InteractionWorkflow import InteractionWorkflow
    for workflow in (wf_id and (self[wf_id],) or self.getWorkflowValueListFor(ob.getPortalType())):
      if not isinstance(workflow, InteractionWorkflowDefinition) and \
          not isinstance(workflow, InteractionWorkflow):
        if state_id in workflow.getStateIdList():
          return True
    return False

  def doActionFor(self, ob, action, wf_id=None, *args, **kw):
    workflow_list = self.getWorkflowValueListFor(ob.getPortalType())
    action_ref = action
    if wf_id is None:
      if workflow_list == []:
        raise WorkflowException(_(u'No workflows found.'))
      found = 0
      for wf in workflow_list:
        if wf.getPortalType() == 'Workflow':
          # workflow compatibility
          action = 'transition_' + action_ref
        else: action = action_ref
        if wf.isActionSupported(ob, action, **kw):
          found = 1
          break
      if not found:
        msg = _(u"No workflow provides the '${action_id}' action.",mapping={'action_id': action})
        raise WorkflowException(msg)
    else:
      wf = self.getWorkflowById(wf_id)
      if wf is None:
        raise WorkflowException(_(u'Requested workflow definition not found.'))
      if wf.getPortalType() == 'Workflow':
        # workflow compatibility
        action = 'transition_' + action_ref
    return self._invokeWithNotification(
      workflow_list, ob, action, wf.doActionFor, (ob, action) + args, kw)

  def _getInfoFor(self, ob, name, default=_marker, wf_id=None, *args, **kw):
    workflow_list = self.getWorkflowValueListFor(ob.getPortalType())

    if wf_id is None:
        if workflow_list == []:
            if default is _marker:
                raise WorkflowException(_(u'No workflows found.'))
            else:
                return default
        found = 0
        for workflow in workflow_list:
            if workflow.isInfoSuported(ob, name):
              found = 1
              break
        if not found:
            if default is _marker:
                msg = _(u"No workflow provides '${name}' information.",
                        mapping={'name': name})
                raise WorkflowException(msg)
            else:
                return default
    else:
        wf = self.getWorkflowById(wf_id)
        if wf is None:
            if default is _marker:
                raise WorkflowException(
                    _(u'Requested workflow definition not found.'))
            else:
                return default

    res = wf.getInfoFor(ob, name, default, *args, **kw)
    if res is _marker:
        msg = _(u'Could not get info: ${name}', mapping={'name': name})
        raise WorkflowException(msg)
    return res

  def getWorkflowValueListFor(self, portal_type_id):
    """ Return a list of workflows bound to selected portal_type.
    """
    portal_type = self.getPortalObject().getDefaultModule(portal_type="portal_types")._getOb(portal_type_id, None)
    workflow_list = []
    if portal_type is not None:
      for workflow_id in portal_type.getTypeWorkflowList():
        workflow_list.append(self._getOb(workflow_id))

    for wf in self.getWorkflowsFor(portal_type_id):
      if wf is not None:
        workflow_list.append(wf)
    return workflow_list

  security.declarePrivate('getHistoryOf')
  def getHistoryOf(self, wf_id, ob):
      """ Get the history of an object for a given workflow.
      """
      if hasattr(aq_base(ob), 'workflow_history'):
          wfh = ob.workflow_history
          return wfh.get(wf_id, None)
      return ()

  security.declarePrivate('getStatusOf')
  def getStatusOf(self, wf_id, ob):
      """ Get the last element of a workflow history for a given workflow.
      """
      wfh = self.getHistoryOf(wf_id, ob)
      if wfh:
          return wfh[-1]
      return None

  def decodeWorkflowUid(self, uid):
    return cPickle.loads(b64decode(uid))

  def encodeWorkflowUid(self, id):
    return b64encode(cPickle.dumps(id))

  def getObjectFromPath(self, path):
    return self.unrestrictedTraverse(path)

  def getWorkflowTempObjectList(self, temp_obj=1):
    """ Return a list of converted temporary workflows. Only necessary in
        Workflow Tool to get temporarilly converted DCWorkflow.
    """
    temp_workflow_list = []
    temp_workflow_id_list = []
    for dc_workflow in self.getPortalObject().portal_workflow.objectValues():
      workflow_type = dc_workflow.__class__.__name__
      if workflow_type == 'Workflow' or workflow_type == 'Interaction Workflow':
        continue
      temp_workflow = self.dc_workflow_asERP5Object(self, dc_workflow, temp_obj)
      temp_workflow_list.append(temp_workflow)
      temp_workflow_id_list.append(temp_workflow.getTitle())
    return temp_workflow_list

  def dc_workflow_asERP5Object(self, container, dc_workflow, temp):
    # create a temporary ERP5 Workflow
    # instead of adding prefix toavoid id conflict, prefer to put dcworkflow in portal_trash;
    workflow_type_id = dc_workflow.__class__.__name__
    if workflow_type_id == 'DCWorkflowDefinition':
      if temp == 0:
        new_id = 'workflow_' + dc_workflow.id
      else:
        new_id = dc_workflow.id
      uid = self.encodeWorkflowUid(new_id)
      workflow = container.newContent(id=new_id, portal_type='Workflow', temp_object=temp)
      workflow.setStateVariable(dc_workflow.state_var)
      workflow.setWorkflowManagedPermission(dc_workflow.permissions)
    else:
      if temp == 0:
        new_id = 'interactionworkflow_' + dc_workflow.id
      else:
        new_id = dc_workflow.id
      uid = self.encodeWorkflowUid(new_id)
      workflow = container.newContent(id=new_id, portal_type='Interaction Workflow', temp_object=temp)
      workflow.setManagerBypass(dc_workflow.manager_bypass)

    if temp == 1:
      # give temp workflow an uid for form_dialog.
      workflow.uid = uid
    workflow.default_reference = dc_workflow.id
    workflow.edit(title=dc_workflow.title)
    workflow.edit(description=dc_workflow.description)

    if temp == 0:
      # create transitions
      if workflow_type_id == 'DCWorkflowDefinition':
        for tid in dc_workflow.transitions:
          tdef = dc_workflow.transitions.get(tid)
          transition = workflow.newContent(portal_type='Transition', temp_object=temp)
          transition.edit(title=tdef.title)
          transition.setReference(tdef.id)
          transition.setTriggerType(tdef.trigger_type)
          transition.setActboxCategory(tdef.actbox_category)
          transition.setActboxIcon(tdef.actbox_icon)
          transition.setActboxName(tdef.actbox_name)
          transition.setActboxUrl(tdef.actbox_url)
          transition.setDescription(tdef.description)
          if tdef.after_script_name is not None:
            # check after script is a Transion or a Script:
            if tdef.after_script_name in dc_workflow.transitions.objectIds():
              transition.setAfterScriptId('transition_'+tdef.after_script_name)
            elif tdef.after_script_name in dc_workflow.scripts.objectIds():
              transition.setAfterScriptId('script_'+tdef.after_script_name)
          if tdef.script_name is not None:
            # check after script is a Transion or a Script:
            if tdef.script_name in dc_workflow.transitions.objectIds():
              transition.setBeforeScriptId('transition_'+tdef.script_name)
            elif tdef.script_name in dc_workflow.scripts.objectIds():
              transition.setBeforeScriptId('script_'+tdef.script_name)
          # configure guard
          if tdef.guard:
            transition.setRoleList(tdef.guard.roles)
            transition.setPermissionList(tdef.guard.permissions)
            transition.setGroupList(tdef.guard.groups)
            transition.setExpression(tdef.guard.expr)
        # create states (portal_type = State)
        for sid in dc_workflow.states:
          sdef = dc_workflow.states.get(sid)
          state = workflow.newContent(portal_type='State', temp_object=temp)
          state.edit(title=sdef.title)
          state.setReference(sdef.id)
          state.setDescription(sdef.description)
          permission_roles = sdef.permission_roles
          state.setStatePermissionRoles(permission_roles)
          i = -1
          for permission in sorted(workflow.getWorkflowManagedPermissionList()):
            i = i + 1
            j = -1
            for role in workflow.getRoleList():
              j = j + 1
              pr_cell = state.newContent(id='cell_%s_%s'%(i,j), portal_type='PermissionRoles')
              if permission in permission_roles and role in permission_roles[permission]:
                pr_cell.is_selected = 1
        # Set Workflow default state using category setter
        state_path = getattr(workflow, 'state_'+dc_workflow.initial_state).getPath()
        state_path = 'source/' + '/'.join(state_path.split('/')[2:])
        workflow.setCategoryList([state_path])
        # set state's possible transitions:
        for sid in dc_workflow.states:
          sdef = workflow._getOb('state_'+sid)
          new_category = []
          for transition_id in dc_workflow.states.get(sid).transitions:
            tr_path = getattr(workflow, 'transition_'+transition_id).getPath()
            tr_path = 'destination/' + '/'.join(tr_path.split('/')[2:])
            new_category.append(tr_path)
          sdef.setCategoryList(new_category)
        # set transition's destination state:
        for tid in dc_workflow.transitions:
          tdef = workflow._getOb('transition_'+tid)
          state = getattr(workflow, 'state_'+dc_workflow.transitions.get(tid).new_state_id, None)
          if state is None:
            # it's a remain in state transition.
            continue
          state_path = 'destination/' + '/'.join(state.getPath().split('/')[2:])
          tdef.setCategoryList([state_path])
        # create worklists (portal_type = Worklist)
        for qid in dc_workflow.worklists:
          qdef = dc_workflow.worklists.get(qid)
          worklist = workflow.newContent(portal_type='Worklist', temp_object=temp)
          worklist.edit(title=qdef.title)
          worklist.setReference(qdef.id)
          worklist.setDescription(qdef.description)
          for key, values in qdef.var_matches.items():
            if key == 'portal_type':
              worklist.setMatchedPortalTypeList(values)
            elif key == 'simulation_state':
              state_id_list = []
              for value in values:
                state_id = 'state_'+value
                state_id_list.append(state_id)
              worklist.setMatchedSimulationStateList(state_id_list)
            elif key == 'validation_state':
              state_id_list = []
              for value in values:
                state_id = 'state_'+value
                state_id_list.append(state_id)
              worklist.setMatchedValidationStateList(state_id_list)
          worklist.setActboxUrl(qdef.actbox_url)
          worklist.setActboxCategory(qdef.actbox_category)
          worklist.setActboxIcon(qdef.actbox_icon)
          worklist.setActboxName(qdef.actbox_name)
          # configure guard
          if qdef.guard:
            worklist.setRoleList(qdef.guard.roles)
            worklist.setPermissionList(qdef.guard.permissions)
            worklist.setGroupList(qdef.guard.groups)
            worklist.setExpression(qdef.guard.expr)
      else:
        for tid in dc_workflow.interactions:
          interaction = workflow.newContent(portal_type='Interaction', temp_object=temp)
          tdef = dc_workflow.interactions.get(tid)
          interaction.edit(title=tdef.title)
          interaction.setReference(tdef.id)
          for script_name in tdef.activate_script_name:
            if script_name in dc_workflow.interactions.objectIds():
              interaction.setActivateScriptName(('interaction_'+script_name,))
            elif script_name in dc_workflow.scripts.objectIds():
              interaction.setActivateScriptName(('script_'+script_name,))
          for script_name in tdef.after_script_name:
            if script_name in dc_workflow.interactions.objectIds():
              interaction.setAfterScriptName(('interaction_'+script_name,))
            elif script_name in dc_workflow.scripts.objectIds():
              interaction.setAfterScriptName(('script_'+script_name,))
          for script_name in tdef.before_commit_script_name:
            if script_name in dc_workflow.interactions.objectIds():
              interaction.setBeforeCommitScriptName(('interaction_'+script_name,))
            elif script_name in dc_workflow.scripts.objectIds():
              interaction.setBeforeCommitScriptName(('script_'+script_name,))
          for script_name in tdef.script_name:
            if script_name in dc_workflow.interactions.objectIds():
              interaction.setBeforeScriptName(('interaction_'+script_name,))
            elif script_name in dc_workflow.scripts.objectIds():
              interaction.setBeforeScriptName(('script_'+script_name,))
          # configure guard
          if tdef.guard:
            interaction.setRoleList(tdef.guard.roles)
            interaction.setPermissionList(tdef.guard.permissions)
            interaction.setGroupList(tdef.guard.groups)
            interaction.setExpression(tdef.guard.expr)
          interaction.setPortalTypeFilter(tdef.portal_type_filter)
          interaction.setPortalTypeGroupFilter(tdef.portal_type_group_filter)
          interaction.setTemporaryDocumentDisallowed(tdef.temporary_document_disallowed)
          #interaction.setTransitionFormId() # this is not defined in DC interaction?
          interaction.setTriggerMethodId(tdef.method_id)
          interaction.setTriggerOncePerTransaction(tdef.once_per_transaction)
          interaction.setTriggerType(tdef.trigger_type)
          interaction.setDescription(tdef.description)
      # create scripts (portal_type = Workflow Script)
      for script_id in dc_workflow.scripts:
        script = dc_workflow.scripts.get(script_id)
        workflow_script = workflow.newContent(id='script_'+script_id ,portal_type='Workflow Script', temp_object=temp)
        workflow_script.edit(title=script.title)
        workflow_script.default_reference = script_id
        workflow_script.setParameterSignature(script._params)
        #workflow_script.setCallableType(script.callable_type)# not defined in python script?
        workflow_script.setBody(script._body)
        workflow_script.setProxyRole(script._proxy_roles)
      # create variables (portal_type = Variable)
      for vid in dc_workflow.variables:
        vdef = dc_workflow.variables.get(vid)
        variable = workflow.newContent(portal_type='Variable', temp_object=temp)
        variable.edit(title=vdef.title)
        variable.setReference(vdef.id)
        variable.setAutomaticUpdate(vdef.update_always)
        if getattr(vdef, 'default_expr', None) is not None:
          # for a very specific case, action return the reference of transition
          # in order to generation correct workflow history.
          if vid == 'action':
            variable.setDefaultExpr('transition/getReference|nothing')
          else: variable.setDefaultExpr(vdef.default_expr.text)
        variable.info_guard = vdef.info_guard
        variable.setForCatalog(vdef.for_catalog)
        variable.setForStatus(vdef.for_status)
        variable.setInitialValue(vdef.default_value)
        variable.setDescription(vdef.description)
      # configure transition variable
      for tid in dc_workflow.transitions:
        origin_tdef = dc_workflow.transitions[tid]
        transition = workflow._getOb('transition_'+tid)
        new_category = []
        if origin_tdef.var_exprs is None:
          var_exprs = {}
        else: var_exprs = origin_tdef.var_exprs
        LOG("transition '%s' has var_exprs '%s'"%(origin_tdef.__dict__, var_exprs), WARNING, " in WorkflowTool.py 496")
        for key in var_exprs:
          tr_var = transition.newContent(portal_type='Transition Variable', temp_object=temp)
          tr_var.setDefaultExpr(var_exprs[key])
          tr_var_path = getattr(workflow, 'variable_'+key).getPath()
          tr_var_path = 'causality/' + '/'.join(tr_path.split('/')[2:])
          new_category.append(tr_var_path)
          tr_var.setCausalityList(tr_var_path_list)
    return workflow

  def getChainDict(self):
      """Test if the given transition exist from the current state.
      """
      chain_dict = {}
      for portal_type, wf_id_list in self._chains_by_type.iteritems():
          for wf_id in wf_id_list:
              chain_dict.setdefault(wf_id, []).append(portal_type)
      return chain_dict

  _reindexWorkflowVariables = lambda self, ob: \
  hasattr(aq_base(ob), 'reindexObjectSecurity') and ob.reindexObjectSecurity()

  def getWorkflowChainDict(self, sorted=True):
    """Returns workflow chain compatible with workflow_chain_dict signature"""
    chain = self._chains_by_type.copy()
    return_dict = {}
    for portal_type, workflow_id_list in chain.iteritems():
      if sorted:
        workflow_id_list = list(workflow_id_list)
        workflow_id_list.sort()
      return_dict['chain_%s' % portal_type] = ', '.join(workflow_id_list)
    return return_dict

  def isTransitionPossible(self, ob, transition_id, wf_id=None):
    """Test if the given transition exist from the current state.
    """
    for workflow in (wf_id and (self[wf_id],) or self.getWorkflowValueListFor(ob.getPortalType())):
      state = workflow._getWorkflowStateOf(ob)
      if state and transition_id in state.getDestinationReferenceList():
        return 1
    return 0

  getFutureStateSetFor = lambda self, wf_id, *args, **kw: \
    self[wf_id].getFutureStateSet(*args, **kw)

  def setStatusOf(self, wf_id, ob, status):
    """ Append an entry to the workflow history.
    o Invoked by workflow definitions.
    """
    wfh = None
    has_history = 0
    if getattr(aq_base(ob), 'workflow_history', None) is not None:
        history = ob.workflow_history
        if history is not None:
            has_history = 1
            wfh = history.get(wf_id, None)
            if wfh is not None and not isinstance(wfh, WorkflowHistoryList):
                wfh = WorkflowHistoryList(list(wfh))
                ob.workflow_history[wf_id] = wfh
    if wfh is None:
        wfh = WorkflowHistoryList()
        if not has_history:
            ob.workflow_history = PersistentMapping()
        ob.workflow_history[wf_id] = wfh
    wfh.append(status)

  getWorkflowIds = OriginalWorkflowTool.getWorkflowIds

  def refreshWorklistCache(self):
    """
      Refresh worklist cache table.
      - delete everything from that table
        - if it fails, create the table
      - insert new lines
        - if it fails, recrete the table and retry
    """
    # Contrary to WorkflowTool_listActions, related keys are NOT supported.
    Base_zInsertIntoWorklistTable = getattr(self, 'Base_zInsertIntoWorklistTable', None)
    if Base_zInsertIntoWorklistTable is not None:
      # XXX: Code below is duplicated from WorkflowTool_listActions
      info = self._getOAI(None)
      worklist_dict = {}
      wf_ids = self.getWorkflowIds()
      for wf_id in wf_ids:
        wf = self.getWorkflowById(wf_id)
        if wf is not None:
          a = wf.getWorklistVariableMatchDict(info, check_guard=False)
          if a is not None:
            worklist_dict[wf_id] = a
      # End of duplicated code
      if len(worklist_dict):
        Base_zClearWorklistTable = getattr(self, 'Base_zClearWorklistTable', None)
        if Base_zClearWorklistTable is None:
          LOG('WorkflowTool', 100, 'Base_zClearWorklistTable cannot be found. ' \
              'Falling back to former refresh method. Please update ' \
              'erp5_worklist_sql business template.')
          self.Base_zCreateWorklistTable()
        else:
          try:
            self.Base_zClearWorklistTable()
          except ProgrammingError, error_value:
            # 1146 = table does not exist
            if error_value[0] != 1146:
              raise
            self.Base_zCreateWorklistTable()
        portal_catalog = getToolByName(self, 'portal_catalog')
        search_result = portal_catalog.unrestrictedSearchResults
        sql_catalog = portal_catalog.getSQLCatalog()
        table_column_id_set = ImmutableSet(
            [COUNT_COLUMN_TITLE] + self.Base_getWorklistTableColumnIDList())
        security_column_id_list = list(
          sql_catalog.getSQLCatalogSecurityUidGroupsColumnsDict().values()) + \
          [x[1] for x in sql_catalog.getSQLCatalogRoleKeysList()] + \
          [x[1] for x in sql_catalog.getSQLCatalogLocalRoleKeysList()]
        security_column_id_set = set(security_column_id_list)
        assert len(security_column_id_set) == len(security_column_id_list), (
          security_column_id_set, security_column_id_list)
        del security_column_id_list
        security_column_id_set.difference_update(
          self._getWorklistIgnoredSecurityColumnSet())
        for security_column_id in security_column_id_set:
          assert security_column_id in table_column_id_set
        (worklist_list_grouped_by_condition, worklist_metadata) = \
          groupWorklistListByCondition(
            worklist_dict=worklist_dict,
            sql_catalog=sql_catalog)
        assert COUNT_COLUMN_TITLE in table_column_id_set
        for grouped_worklist_dict in worklist_list_grouped_by_condition:
          # Generate the query for this worklist_list
          (total_criterion_id_list, query) = \
            getWorklistListQuery(
              getQuery=SimpleQuery,
              grouped_worklist_dict=grouped_worklist_dict,
            )
          for criterion_id in total_criterion_id_list:
            assert criterion_id in table_column_id_set
          for security_column_id in security_column_id_set:
            assert security_column_id not in total_criterion_id_list
            total_criterion_id_list.append(security_column_id)
          group_by_expression = ', '.join(total_criterion_id_list)
          assert COUNT_COLUMN_TITLE not in total_criterion_id_list
          select_expression = 'count(*) as %s, %s' % (COUNT_COLUMN_TITLE,
                                                      group_by_expression)
          search_result_kw = {'select_expression': select_expression,
                              'group_by_expression': group_by_expression,
                              'query': query,
                              'limit': None}
          #LOG('refreshWorklistCache', WARNING, 'Using query: %s' % \
          #    (search_result(src__=1, **search_result_kw), ))
          catalog_brain_result = search_result(**search_result_kw)
          value_column_dict = {x: [] for x in table_column_id_set}
          for catalog_brain_line in catalog_brain_result.dictionaries():
            for column_id, value in catalog_brain_line.iteritems():
              if column_id in value_column_dict:
                value_column_dict[column_id].append(value)
          if len(value_column_dict[COUNT_COLUMN_TITLE]):
            try:
              Base_zInsertIntoWorklistTable(**value_column_dict)
            except (ProgrammingError, OperationalError), error_value:
              # OperationalError 1054 = unknown column
              if isinstance(error_value, OperationalError) and error_value[0] != 1054:
                raise
              LOG('WorkflowTool', 100, 'Insertion in worklist cache table ' \
                  'failed. Recreating table and retrying.',
                  error=sys.exc_info())
              self.Base_zCreateWorklistTable()
              Base_zInsertIntoWorklistTable(**value_column_dict)

  def _getWorklistIgnoredSecurityColumnSet(self):
    return getattr(self,
      'Base_getWorklistIgnoredSecurityColumnSet', lambda: ())()

  def getChainsByType(self):
    type_workflow_dict = {}
    for type_id, workflow_id_list in self._chains_by_type.iteritems():
        type_workflow_dict.setdefault(type_id, ())
        type_workflow_dict[type_id] = type_workflow_dict[type_id] + workflow_id_list
    return type_workflow_dict

  # For Chains By Type Repair Tool:
  def addTypeCBT(self, pt, wf_id):
    self._chains_by_type[pt] = self._chains_by_type[pt] + (wf_id, )

  def delTypeCBT(self, pt, wf_id):
    self._chains_by_type[pt] = tuple(wf for wf in self._chains_by_type[pt] if wf != wf_id)

  def listActions(self, info=None, object=None, src__=False):
    """
      Returns a list of actions to be displayed to the user.
          o Invoked by the portal_actions tool.
          o Allows workflows to include actions to be displayed in the
            actions box.
          o Object actions are supplied by workflows that apply to the object.
          o Global actions are supplied by all workflows.
      This patch attemps to make listGlobalActions aware of worklists,
      which allows factorizing them into one single SQL query.
      Related keys are supported.
      Warning: the worklist cache does not support them.
    """
    if object is not None or info is None:
      info = self._getOAI(object)
    chain = self.getChainFor(info.object)
    did = {}
    actions = []
    worklist_dict = {}

    document = info.object

    if document is not None:
      document_pt = document.getTypeInfo()
      if document_pt is not None:
        workflow_list = document_pt.getTypeWorkflowList()
        if (workflow_list is not None) and (workflow_list is not []):
          for wf_id in workflow_list:
            did[wf_id] = None
            wf = self.getPortalObject().portal_workflow._getOb(wf_id, None)
            if wf is None:
              raise NotImplementedError ("Can not find workflow: %s, please check if the workflow exists."%wf_id)
            a = wf.listObjectActions(info)
            if a is not None and a != []:
              actions.extend(a)
            a = wf.getWorklistVariableMatchDict(info)
            if a is not None:
              worklist_dict[wf_id] = a
    # DC workflow compatibility
    for wf_id in chain:
      did[wf_id] = None
      wf = self.getWorkflowById(wf_id)
      if wf is not None:
        a = wf.listObjectActions(info)
        if a is not None:
          actions.extend(a)
        a = wf.getWorklistVariableMatchDict(info)
        if a is not None:
          worklist_dict[wf_id] = a

    wf_ids = self.getWorkflowIds()
    for wf_id in wf_ids:
      if not did.has_key(wf_id):
        wf = self.getWorkflowById(wf_id)
        if wf is not None:
          a = wf.getWorklistVariableMatchDict(info)
          if a is not None:
            worklist_dict[wf_id] = a

    if worklist_dict:
      portal = self.getPortalObject()
      portal_url = portal.portal_url()
      def _getWorklistActionList():
        is_anonymous = portal.portal_membership.isAnonymousUser()
        portal_catalog = portal.portal_catalog
        sql_catalog = portal_catalog.getSQLCatalog()
        catalog_security_uid_groups_columns_dict = \
          sql_catalog.getSQLCatalogSecurityUidGroupsColumnsDict()
        getSecurityUidDictAndRoleColumnDict = \
          portal_catalog.getSecurityUidDictAndRoleColumnDict
        search_result = getattr(self, "Base_getCountFromWorklistTable", None)
        use_cache = search_result is not None
        if use_cache:
          ignored_security_column_id_set = self._getWorklistIgnoredSecurityColumnSet()
          ignored_security_uid_parameter_set = {x
            for x, y in catalog_security_uid_groups_columns_dict.iteritems()
            if y in ignored_security_column_id_set
          }
          _getSecurityUidDictAndRoleColumnDict = getSecurityUidDictAndRoleColumnDict
          def getSecurityUidDictAndRoleColumnDict(**kw):
            security_uid_dict, role_column_dict, local_role_column_dict = \
              _getSecurityUidDictAndRoleColumnDict(**kw)
            for ignored_security_column_id in ignored_security_column_id_set:
              role_column_dict.pop(ignored_security_column_id, None)
              local_role_column_dict.pop(ignored_security_column_id, None)
            for ignored_security_uid_parameter in \
                ignored_security_uid_parameter_set:
              security_uid_dict.pop(ignored_security_uid_parameter)
            return security_uid_dict, role_column_dict, local_role_column_dict
          select_expression_prefix = 'sum(`%s`) as %s' % (COUNT_COLUMN_TITLE, COUNT_COLUMN_TITLE)
          # Prevent catalog from trying to join
          getQuery = SimpleQuery
        else:
          search_result = portal_catalog.unrestrictedSearchResults
          select_expression_prefix = 'count(*) as %s' % (COUNT_COLUMN_TITLE, )
          # Let catalog join as needed
          getQuery = lambda comparison_operator=None, **kw: AutoQuery(
            operator=comparison_operator,
            **kw
          )
        worklist_result_dict = {}
        # Get a list of dict of WorklistVariableMatchDict grouped by compatible
        # conditions

        (worklist_list_grouped_by_condition, worklist_metadata) = \
          groupWorklistListByCondition(
            worklist_dict=worklist_dict,
            sql_catalog=sql_catalog,
            getSecurityUidDictAndRoleColumnDict=\
              getSecurityUidDictAndRoleColumnDict,
            catalog_security_uid_groups_columns_dict=\
              catalog_security_uid_groups_columns_dict,
          )
        if src__:
          action_list = []
        for grouped_worklist_dict in worklist_list_grouped_by_condition:
          # Generate the query for this worklist_list
          (total_criterion_id_list, query) = \
            getWorklistListQuery(
              getQuery=getQuery,
              grouped_worklist_dict=grouped_worklist_dict,
            )
          group_by_expression = ', '.join(total_criterion_id_list)
          assert COUNT_COLUMN_TITLE not in total_criterion_id_list
          # If required mapping method is not present on the query, assume it
          # handles column mapping properly, and build a bare select
          # expression.
          select_expression = select_expression_prefix + ', ' \
                              + group_by_expression
          catalog_brain_result = []
          try:
            catalog_brain_result = search_result(
                                        select_expression=select_expression,
                                        group_by_expression=group_by_expression,
                                        query=query,
                                        limit=None,
                                        src__=src__)
          except Unauthorized:
            if not is_anonymous:
              raise
            LOG('WorkflowTool.listActions', WARNING,
                'Exception while computing worklists: %s'
                % grouped_worklist_dict.keys(),
                error=sys.exc_info())
            continue
          except ProgrammingError, error_value:
            # 1146 = table does not exist
            if not use_cache or error_value[0] != 1146:
              raise
            try:
              self.Base_zCreateWorklistTable()
            except ProgrammingError, error_value:
              # 1050 = table exists (alarm run just a bit too late)
              if error_value[0] != 1050:
                raise
          if src__:
            action_list.append(catalog_brain_result)
          else:
            grouped_worklist_result = sumCatalogResultByWorklist(
              grouped_worklist_dict=grouped_worklist_dict,
              catalog_result=catalog_brain_result)
            for key, value in grouped_worklist_result.iteritems():
              worklist_result_dict[key] = value + worklist_result_dict.get(key, 0)
        if not src__:
          action_list = sorted(
            generateActionList(
              worklist_metadata=worklist_metadata,
              worklist_result=worklist_result_dict,
              portal_url=portal_url),
            key=lambda x: '/'.join((x['workflow_id'], x['worklist_id'])),
          )
        return action_list

      user = str(_getAuthenticatedUser(self))
      if src__:
        actions = _getWorklistActionList()
      else:
        _getWorklistActionList = CachingMethod(_getWorklistActionList,
          id=('_getWorklistActionList', user, portal_url),
          cache_factory = 'erp5_ui_short')
        actions.extend(_getWorklistActionList())
    return actions

  def _finalizeWorkflowConversion(self):
    """ Put old dc workflow into trash bin, and remove prefix?"""
    pass

InitializeClass(WorkflowTool)

_sql_cast_dict = {
  'i': long,
  'l': long,
  'n': float,
  'd': DateTime,
}
_sql_cast_fallback = str

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
            except ObjectDeleted, ex:
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

def getValidCriterionDict(worklist_match_dict, sql_catalog, workflow_worklist_key):
  valid_criterion_dict = {}
  metadata = None
  isValidColumn = sql_catalog.isValidColumn
  for criterion_id, criterion_value in worklist_match_dict.iteritems():
    if isValidColumn(criterion_id):
      if isinstance(criterion_value, tuple):
        criterion_value = list(criterion_value)
      elif isinstance(criterion_value, (str, int, long)):
        criterion_value = [criterion_value]
      assert criterion_id not in valid_criterion_dict
      valid_criterion_dict[criterion_id] = criterion_value
    elif criterion_id == WORKLIST_METADATA_KEY:
      metadata = criterion_value
    elif criterion_id == SECURITY_PARAMETER_ID:
      pass
    else:
      LOG('WorkflowTool_listActions', WARNING, 'Worklist %r' \
          ' filters on variable %r which is not available ' \
          'in catalog. Its value will not be checked.' % \
          (workflow_worklist_key, criterion_id))
  return valid_criterion_dict, metadata

def updateWorklistSetDict(worklist_set_dict, workflow_worklist_key, valid_criterion_dict):
  worklist_set_dict_key = valid_criterion_dict.keys()
  if len(worklist_set_dict_key):
    worklist_set_dict_key.sort()
    worklist_set_dict_key = tuple(worklist_set_dict_key)
    if worklist_set_dict_key not in worklist_set_dict:
      worklist_set_dict[worklist_set_dict_key] = {}
    worklist_set_dict[worklist_set_dict_key]\
      [workflow_worklist_key] = valid_criterion_dict

def groupWorklistListByCondition(worklist_dict, sql_catalog, getSecurityUidDictAndRoleColumnDict=None, catalog_security_uid_groups_columns_dict=None,):
  """
    Get a list of dict of WorklistVariableMatchDict grouped by compatible
    conditions.
    Strip any variable which is not a catalog column.
    Returns metadata in a separate dict.

    Example:
      Input:
        worklist_dict:
        {'workflow_A': {'worklist_AA': {'foo': (1, 2), 'bar': (3, 4)},
                        'worklist_AB': {'baz': (5, )}
                       }
         'workflow_B': {'worklist_BA': {'baz': (6, )}
                       }
        }

      Allowed columns are:
      sql_catalog.isValidColumn('foo') is True
      sql_catalog.isValidColumn('baz') is True
      sql_catalog.isValidColumn('bar') is False

      Output a 2-tuple:
        (
          [{'workflow_A/worklist_AA': {'foo': (1, 2)}
           },
           {'workflow_A/worklist_AB': {'baz': (5, )},
            'workflow_B/worklist_BA': {'baz': (6, )}
           }
          ]
        ,
          {} # Contains metadata information, one entry per worklist.
        )
  """
  # One entry per worklist group, based on filter criterions.
  worklist_set_dict = {}
  metadata_dict = {}
  for workflow_id, worklist in worklist_dict.iteritems():
    for worklist_id, worklist_match_dict in worklist.iteritems():
      workflow_worklist_key = '/'.join((workflow_id, worklist_id))
      if getSecurityUidDictAndRoleColumnDict is None:
        valid_criterion_dict, metadata = getValidCriterionDict(
          worklist_match_dict=worklist_match_dict,
          sql_catalog=sql_catalog,
          workflow_worklist_key=workflow_worklist_key)
        if metadata is not None:
          metadata_dict[workflow_worklist_key] = metadata
        updateWorklistSetDict(
          worklist_set_dict=worklist_set_dict,
          workflow_worklist_key=workflow_worklist_key,
          valid_criterion_dict=valid_criterion_dict)
      else:
        security_parameter = worklist_match_dict.get(SECURITY_PARAMETER_ID, [])
        security_kw = {}
        if len(security_parameter):
          security_kw[SECURITY_PARAMETER_ID] = security_parameter
        uid_dict, role_column_dict, local_role_column_dict = \
            getSecurityUidDictAndRoleColumnDict(**security_kw)

        for key, value in local_role_column_dict.items():
          worklist_match_dict[key] = [value]

        for local_roles_group_id, uid_list in uid_dict.iteritems():
          role_column_dict[
            catalog_security_uid_groups_columns_dict[local_roles_group_id]] = uid_list

        # Make sure every item is a list - or a tuple
        for security_column_id in role_column_dict.iterkeys():
          value = role_column_dict[security_column_id]
          if not isinstance(value, (tuple, list)):
            role_column_dict[security_column_id] = [value]
        applied_security_criterion_dict = {}
        # TODO: make security criterions be examined in the same order for all
        # worklists if possible at all.
        for security_column_id, security_column_value in \
            role_column_dict.iteritems():
          valid_criterion_dict, metadata = getValidCriterionDict(
            worklist_match_dict=worklist_match_dict,
            sql_catalog=sql_catalog,
            workflow_worklist_key=workflow_worklist_key)
          if metadata is not None:
            metadata_dict[workflow_worklist_key] = metadata
          valid_criterion_dict.update(applied_security_criterion_dict)
          # Current security criterion must be applied to all further queries
          # for this worklist negated, so the a given line cannot match multiple
          # times.
          applied_security_criterion_dict[security_column_id] = \
            ExclusionList(security_column_value)
          valid_criterion_dict[security_column_id] = security_column_value
          updateWorklistSetDict(
            worklist_set_dict=worklist_set_dict,
            workflow_worklist_key=workflow_worklist_key,
            valid_criterion_dict=valid_criterion_dict)
  return worklist_set_dict.values(), metadata_dict

def generateNestedQuery(getQuery, priority_list, criterion_dict, possible_worklist_id_dict=None):
  assert possible_worklist_id_dict is None \
         or len(possible_worklist_id_dict) != 0
  my_priority_list = priority_list[:]
  my_criterion_id = my_priority_list.pop()
  query_list = []
  append = query_list.append
  my_criterion_dict = criterion_dict[my_criterion_id]
  if len(my_priority_list) > 0:
    for criterion_value, worklist_id_dict in my_criterion_dict.iteritems():
      if possible_worklist_id_dict is not None:
        criterion_worklist_id_dict = worklist_id_dict.copy()
        # Do not use iterkeys since the dictionary will be modified in the
        # loop
        for worklist_id in criterion_worklist_id_dict.keys():
          if worklist_id not in possible_worklist_id_dict:
            del criterion_worklist_id_dict[worklist_id]
      else:
        criterion_worklist_id_dict = worklist_id_dict
      if len(criterion_worklist_id_dict):
        subcriterion_query = generateNestedQuery(
          getQuery=getQuery,
          priority_list=my_priority_list,
          criterion_dict=criterion_dict,
          possible_worklist_id_dict=criterion_worklist_id_dict)
        if subcriterion_query is not None:
          query = getQuery(comparison_operator='IN',
                        **{my_criterion_id: criterion_value})
          if isinstance(criterion_value, ExclusionTuple):
            query = NegatedQuery(query)
            query = ComplexQuery(operator='OR',
                      *(query, getQuery(**{my_criterion_id: None})))
          append(ComplexQuery(query, subcriterion_query, operator='AND'))
  else:
    possible_value_list = tuple()
    impossible_value_list = tuple()
    possible = True
    for criterion_value, criterion_worklist_id_dict \
        in my_criterion_dict.iteritems():
      if possible_worklist_id_dict is not None:
        possible = False
        for worklist_id in criterion_worklist_id_dict.iterkeys():
          if worklist_id in possible_worklist_id_dict:
            possible = True
            break
      if possible:
        if isinstance(criterion_value, ExclusionTuple):
          impossible_value_list += criterion_value
        else:
          possible_value_list += criterion_value
    value_query_list = []
    if len(possible_value_list):
      query = getQuery(
        comparison_operator='IN',
        **{my_criterion_id: possible_value_list}
      )
      value_query_list.append(query)
    if len(impossible_value_list):
      query = getQuery(
        comparison_operator='IN',
        **{my_criterion_id: impossible_value_list}
      )
      query = NegatedQuery(query)
      query = ComplexQuery(operator='OR',
                *(query, getQuery(**{my_criterion_id: None})))
      value_query_list.append(query)
    append(ComplexQuery(operator='AND', *value_query_list))
  if len(query_list):
    return ComplexQuery(operator='OR', *query_list)
  return None

def getWorklistListQuery(getQuery, grouped_worklist_dict):
  """
    Return a tuple of 3 value:
    - a select_expression with a count(*) and all columns used in
      goup_by_expression
    - a group_by_expression with all columns required for provided
      grouped_worklist_dict
    - a query applying all criterions contained in provided
      grouped_worklist_dict
  """
  query_list = []
  total_criterion_id_dict = {}
  for worklist_id, worklist in grouped_worklist_dict.iteritems():
    for criterion_id, criterion_value in worklist.iteritems():
      criterion_value_to_worklist_dict_dict = \
        total_criterion_id_dict.setdefault(criterion_id, {})
      criterion_value.sort()
      if isinstance(criterion_value, ExclusionList):
        criterion_value = ExclusionTuple(criterion_value)
      else:
        criterion_value = tuple(criterion_value)
      criterion_value_to_worklist_dict = \
        criterion_value_to_worklist_dict_dict.setdefault(criterion_value, {})
      criterion_value_to_worklist_dict[worklist_id] = None
  total_criterion_id_list = sorted(total_criterion_id_dict, key=lambda y: max(
    len(x) for x in total_criterion_id_dict[y].itervalues()))
  query = generateNestedQuery(
    getQuery=getQuery,
    priority_list=total_criterion_id_list,
    criterion_dict=total_criterion_id_dict,
  )
  assert query is not None
  assert COUNT_COLUMN_TITLE not in total_criterion_id_dict
  return (total_criterion_id_list, query)

def generateActionList(worklist_metadata, worklist_result, portal_url):
  """
    For each worklist generate action_list as expected by portal_actions.
  """
  action_list = []
  append = action_list.append
  for key, metadata in worklist_metadata.iteritems():
    document_count = worklist_result.get(key, 0)
    if document_count:
      format_data = metadata['format_data']
      format_data._push({'count': document_count})
      append({'name': metadata['worklist_title'] % format_data,
              'url': '%s/%s' % (portal_url, metadata['action_box_url'] % \
                                            format_data),
              'worklist_id': metadata['worklist_id'],
              'workflow_title': metadata['workflow_title'],
              'workflow_id': metadata['workflow_id'],
              'count': format_data['count'],
              'permissions': (),  # Predetermined.
              'category': metadata['action_box_category']})
  return action_list

def sumCatalogResultByWorklist(grouped_worklist_dict, catalog_result):
  """
    Return a dict regrouping each worklist's result, extracting it from
    catalog result.
    Build a dictionnary summing up which value combination interests which
    worklist, then iterate catalog result lines and give results to
    corresponding worklists.

    It is better to avoid reading multiple times the catalog result from
    flexibility point of view: if it must ever be changed into a cursor, this
    code will keep working nicely without needing to rewind the cursor.

    This code assumes that all worklists have the same set of criterion ids,
    and that when a criterion id is associated with an ExclusionList it is
    also true for all worklists.
  """
  worklist_result_dict = {}
  if len(catalog_result) > 0:
    # Transtype all worklist definitions where needed
    criterion_id_list = []
    class_dict = {name: _sql_cast_dict.get(x['type'], _sql_cast_fallback)
      for name, x in catalog_result.data_dictionary().iteritems()}
    for criterion_dict in grouped_worklist_dict.itervalues():
      for criterion_id, criterion_value_list in criterion_dict.iteritems():
        if type(criterion_value_list) is not ExclusionList:
          criterion_id_list.append(criterion_id)
          expected_class = class_dict[criterion_id]
          if type(criterion_value_list[0]) is not expected_class:
            criterion_dict[criterion_id] = ImmutableSet([expected_class(x) for x in criterion_value_list])
          elif type(criterion_value_list) is not ImmutableSet:
            criterion_dict[criterion_id] = ImmutableSet(criterion_dict[criterion_id])
    # Read catalog result and distribute to matching worklists
    for result_line in catalog_result:
      result_count = int(result_line[COUNT_COLUMN_TITLE])
      for worklist_id, criterion_dict in grouped_worklist_dict.iteritems():
        is_candidate = True
        for criterion_id in criterion_id_list:
          criterion_value_set = criterion_dict[criterion_id]
          if result_line[criterion_id] not in criterion_value_set:
            is_candidate = False
            break
        if is_candidate:
          try:
            worklist_result_dict[worklist_id] += result_count
          except KeyError:
            worklist_result_dict[worklist_id] = result_count
  return worklist_result_dict

class WorkflowHistoryList(Persistent):
    _bucket_size = 16

    def __init__(self, iterable=None, prev=None):
        self._prev = prev
        self._slots = []
        if iterable is not None:
            for x in iterable:
                self.append(x)

    def __add__(self, iterable):
        return self.__class__(tuple(self) + tuple(iterable))

    def __contains__(self, item):
        return item in tuple(self)

    def __eq__(self, other):
        return tuple(self) == tuple(other)

    def __getitem__(self, index):
        if index == -1:
            return self._slots[-1]
        elif isinstance(index, (int, long)):
            if index < 0:
                # XXX this implementation is not so good, but rarely used.
                index += len(self)
            iterator = self.__iter__()
            for i in xrange(index):
                iterator.next()
            return iterator.next()
        elif isinstance(index, slice):
            return self.__class__((self[x] for x in
                                   xrange(*index.indices(len(self)))))
        else:
            raise TypeError, 'tuple indices must be integers'

    def __getslice__(self, start, end):
        return self.__getitem__(slice(start, end))

    def __getstate__(self):
        return (self._prev, self._slots)

    def __iter__(self):
        bucket = self
        stack = []
        while bucket is not None:
            stack.append(bucket)
            bucket = bucket._prev
        for i in reversed(stack):
            for j in i._slots:
                yield j

    def __len__(self):
        length = len(self._slots)
        bucket = self._prev
        while bucket is not None:
            length += len(bucket._slots)
            bucket = bucket._prev
        return length

    def __mul__(self, x):
        return self.__class__(tuple(self) * x)

    def __nonzero__(self):
        return len(self._slots) != 0 or self._prev is not None

    def __repr__(self):
        #return '%s' % repr(tuple(self.__iter__()))
        return '<%s object at 0x%x %r>' % (self.__class__.__name__, id(self), tuple(self))

    def __rmul__(self, x):
        return self.__class__(x * tuple(self))

    def __setstate__(self, state):
        self._prev, self._slots = state

    def append(self, value):
        if len(self._slots) < self._bucket_size:
            self._slots.append(value)
            self._p_changed = 1
        else:
            self._prev = self.__class__(self._slots, prev=self._prev)
            self._slots = [value]

def DCWorkflowDefinition_notifyWorkflowMethod(self, ob, transition_list, args=None, kw=None):
    '''
    Allows the system to request a workflow action.  This method
    must perform its own security checks.
    '''
    if type(transition_list) in StringTypes:
      method_id = transition_list
    elif len(transition_list) == 1:
      method_id = transition_list[0]
    else:
      raise ValueError('WorkflowMethod should be attached to exactly 1 transition per DCWorkflow instance.')
    sdef = self._getWorkflowStateOf(ob)
    if sdef is None:
        raise WorkflowException, 'Object is in an undefined state'
    if method_id not in sdef.transitions:
        raise Unauthorized(method_id)
    tdef = self.transitions.get(method_id, None)
    if tdef is None or tdef.trigger_type != TRIGGER_WORKFLOW_METHOD:
        raise WorkflowException, (
            'Transition %s is not triggered by a workflow method'
            % method_id)
    if not self._checkTransitionGuard(tdef, ob):
        raise Unauthorized(method_id)
    self._changeStateOf(ob, tdef, kw)
    if getattr(ob, 'reindexObject', None) is not None:
        if kw is not None:
            activate_kw = kw.get('activate_kw', {})
        else:
            activate_kw = {}
        ob.reindexObject(activate_kw=activate_kw)

def DCWorkflowDefinition_notifyBefore(self, ob, transition_list, args=None, kw=None):
    '''
    Notifies this workflow of an action before it happens,
    allowing veto by exception.  Unless an exception is thrown, either
    a notifySuccess() or notifyException() can be expected later on.
    The action usually corresponds to a method name.
    '''
    pass

def DCWorkflowDefinition_notifySuccess(self, ob, transition_list, result, args=None, kw=None):
    '''
    Notifies this workflow that an action has taken place.
    '''
    pass

DCWorkflowDefinition.notifyWorkflowMethod = DCWorkflowDefinition_notifyWorkflowMethod
DCWorkflowDefinition.notifyBefore = DCWorkflowDefinition_notifyBefore
DCWorkflowDefinition.notifySuccess = DCWorkflowDefinition_notifySuccess

WORKLIST_METADATA_KEY = 'metadata'
SECURITY_PARAMETER_ID = 'local_roles'
COUNT_COLUMN_TITLE = 'count'

class ExclusionList(list):
  """
    This is a dummy subclass of list.
    It is only used to detect wether contained values must be negated.
    It is not to be used outside of the scope of this document nor outside
    of the scope of worklist criterion handling.
  """
  pass

class ExclusionTuple(tuple):
  """
    This is a dummy subclass of tuple.
    It is only used to detect wether contained values must be negated.
    It is not to be used outside of the scope of this document nor outside
    of the scope of worklist criterion handling.
  """
  pass
