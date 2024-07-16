# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Nexedi SARL and Contributors. All Rights Reserved.
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
"""
Most of the code in this file has been taken from patches/WorkflowTool.py
"""
from collections import defaultdict
import re
import warnings
from six import string_types as basestring
from AccessControl import ClassSecurityInfo, Unauthorized
from Acquisition import aq_base
from DateTime import DateTime
from MySQLdb import ProgrammingError, OperationalError
from Products.CMFCore.utils import Message
from Products.CMFCore.utils import _getAuthenticatedUser
from Products.CMFCore.WorkflowTool import WorkflowTool as OriginalWorkflowTool
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.ERP5Type import Permissions
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.Globals import InitializeClass, PersistentMapping
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type.Utils import deprecated
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, AutoQuery, ComplexQuery, NegatedQuery
from zLOG import LOG, WARNING
import six
from six import reraise

WORKLIST_METADATA_KEY = 'metadata'
COUNT_COLUMN_TITLE = 'count'

SECURITY_PARAMETER_ID = 'local_roles'
from AccessControl.SecurityInfo import ModuleSecurityInfo
ModuleSecurityInfo(__name__).declarePublic('SECURITY_PARAMETER_ID')

class WorkflowTool(BaseTool, OriginalWorkflowTool):
  """
  A new container for DC workflow and workflow;
  inherits methods from original WorkflowTool.py;
  contains patches from ERP5Type/patches/WorkflowTool.py.
  """
  id            = 'portal_workflow'
  title         = 'Workflow Tool'
  meta_type     = 'Workflow Tool'
  portal_type   = 'Workflow Tool'
  allowed_types = ('Workflow', 'Interaction Workflow')

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  property_sheets = (
    'Base',
    'XMLObject',
    'CategoryCore',
    'DublinCore',
  )

  def _isBootstrapRequired(self):
    """
    Required by synchronizeDynamicModules() to bootstrap an empty site and
    thus create portal_components
    """
    return False

  def _bootstrap(self):
    """
    Required by synchronizeDynamicModules() to bootstrap an empty site and
    thus create portal_components
    """
    pass

  def filtered_meta_types(self, user=None):
    return False

  def _jumpToStateFor(self, ob, state_id, wf_id=None, *_, **__):
    """Inspired from doActionFor.
    This is public method to allow passing meta transition (Jump form
    any state to another in same workflow)
    """
    if WITH_LEGACY_WORKFLOW:
      from Products.ERP5.InteractionWorkflow import InteractionWorkflowDefinition
    else:
      InteractionWorkflowDefinition = None.__class__
    from Products.ERP5Type.Core.InteractionWorkflow import InteractionWorkflow
    workflow_list = self.getWorkflowValueListFor(ob.getPortalType())
    if wf_id is None:
      if not workflow_list:
        raise WorkflowException('No workflows found.')
      found = False
      for workflow in workflow_list:
        if not isinstance(workflow, (InteractionWorkflowDefinition, InteractionWorkflow,)) and \
          state_id in workflow.getStateReferenceList():
            found = True
            break
      if not found:
        raise WorkflowException('No workflow provides the destination state %r'\
                                                                      % state_id)
    else:
      workflow = self._getOb(wf_id, None)
      if workflow is None:
        raise WorkflowException('Requested workflow definition not found.')

    workflow._executeMetaTransition(ob, state_id)

  def _isJumpToStatePossibleFor(self, ob, state_id, wf_id=None):
    """Test if given state_id is available for ob
    in at least one associated workflow
    """
    if WITH_LEGACY_WORKFLOW:
      from Products.ERP5.InteractionWorkflow import InteractionWorkflowDefinition
    else:
      InteractionWorkflowDefinition = None.__class__
    from Products.ERP5Type.Core.InteractionWorkflow import InteractionWorkflow
    for workflow in (wf_id and (self[wf_id],) or self.getWorkflowValueListFor(ob.getPortalType())):
      if not isinstance(workflow, (InteractionWorkflowDefinition,
                                   InteractionWorkflow)):
        if state_id in workflow.getStateReferenceList():
          return True
    return False

  security.declarePrivate('getCatalogVariablesFor')
  def getCatalogVariablesFor(self, ob):
    """ Get a mapping of "workflow-relevant" attributes.
        original code from zope CMFCore/WorkflowTool.py
    """
    wfs = self.getWorkflowValueListFor(ob)
    if wfs is None:
      return None
    # Iterate through the workflows backwards so that
    # earlier workflows can override later workflows.
    wfs.reverse()
    variable_dict = {}
    for wf in wfs:
      v = wf.getCatalogVariablesFor(ob)
      if v is not None:
        variable_dict.update(v)
    return variable_dict

  def _invokeWithNotification(self, wfs, ob, action, func, args, kw):
    """ Private utility method:  call 'func', and deal with exceptions
        indicating that the object has been deleted or moved.
    """
    from zope.event import notify
    from Products.CMFCore.WorkflowCore import ActionRaisedExceptionEvent
    from Products.CMFCore.WorkflowCore import ActionSucceededEvent
    from Products.CMFCore.WorkflowCore import ActionWillBeInvokedEvent
    from Products.CMFCore.WorkflowCore import ObjectDeleted
    from Products.CMFCore.WorkflowCore import ObjectMoved
    from Products.CMFCore.WorkflowCore import WorkflowException

    reindex = 1
    for w in wfs:
      w.notifyBefore(ob, action)
      notify(ActionWillBeInvokedEvent(ob, w, action))
    try:
      res = func(*args, **kw)
    except ObjectDeleted as ex:
      res = ex.getResult()
      reindex = 0
    except ObjectMoved as ex:
      res = ex.getResult()
      ob = ex.getNewObject()
    except:
      import sys
      exc = sys.exc_info()
      try:
        for w in wfs:
          w.notifyException(ob, action, exc)
          notify(ActionRaisedExceptionEvent(ob, w, action, exc))
        reraise(*exc)
      finally:
        exc = None
    for w in wfs:
      w.notifySuccess(ob, action, res)
      notify(ActionSucceededEvent(ob, w, action, res))
    if reindex:
      self._reindexWorkflowVariables(ob)
    return res

  security.declarePublic('doActionFor')
  def doActionFor(self, ob, action, wf_id=None, *args, **kw):
    workflow_id = wf_id
    workflow_list = self.getWorkflowValueListFor(ob.getPortalType())
    if workflow_id is None:
      if not workflow_list:
        raise WorkflowException(Message(u'No workflows found.'))
      for workflow in workflow_list:
        is_action_supported = workflow.isActionSupported(ob, action, **kw)
        if is_action_supported:
          kw['is_action_supported'] = is_action_supported
          break
      else:
        raise WorkflowException(
          Message(u"No workflow provides the '${action_id}' action.",
                  mapping={'action_id': action}))
    else:
      workflow = self._getOb(workflow_id, None)
      if workflow is None:
        raise WorkflowException(Message(u'Requested workflow not found.'))

    return self._invokeWithNotification(
      workflow_list,
      ob,
      action,
      workflow.doActionFor, (ob, action) + tuple(args), kw)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getWorkflowValueListFor')
  def getWorkflowValueListFor(self, ob):
    """ Return a list of workflows bound to selected object, this workflow
        list may contain both DC Workflow and Workflow.
    """
    workflow_list = []

    if isinstance(ob, basestring):
        portal_type = self.getPortalObject().portal_types.getTypeInfo(ob)
    elif hasattr(aq_base(ob), 'getTypeInfo'):
        portal_type = ob.getTypeInfo()
    else:
        portal_type = None

    portal_type_workflow_list = tuple()
    if portal_type is not None:
      portal_type_workflow_list = portal_type.getTypeWorkflowList()

      # get workflow assigned in portal types:
      for workflow_id in portal_type_workflow_list:
        workflow_value = self._getOb(workflow_id, None)
        if workflow_value is not None:
          workflow_list.append(workflow_value)
        else:
          LOG("WorkflowTool", WARNING,
              "getWorkflowValueListFor: workflow %s declared on portal_type %s "
              "does not exist" % (workflow_id, portal_type.getId()))

    return workflow_list

  # WITH_LEGACY_WORKFLOW
  __getWorkflowsFor_warning = \
    "getWorkflowsFor() is deprecated; use getWorkflowValueListFor() instead"
  getWorkflowsFor = deprecated(__getWorkflowsFor_warning)(getWorkflowValueListFor)
  # ignore the warning when called from Products.CMFCore, getWorkflowsFor is a
  # CMFCore API that is used internally in CMFCore, we only want to warn when
  # using it from ERP5.
  warnings.filterwarnings(
    'ignore',
    message=re.escape(__getWorkflowsFor_warning),
    module='Products.CMFCore.WorkflowTool')

  @deprecated("getChainFor() is deprecated; use getWorkflowValueListFor() instead")
  def getChainFor(self, ob):
    return [wf.getId() for wf in self.getWorkflowValueListFor(ob)]

  @staticmethod
  def getHistoryOf(wf_id, ob):
      """ Get the history of an object for a given workflow.
      """
      if hasattr(aq_base(ob), 'workflow_history'):
          return ob.workflow_history.get(wf_id, None)
      return ()

  @staticmethod
  def getScriptPathList(workflow, initial_script_name_list):
    if not initial_script_name_list:
      return []

    script_path_list = []
    if isinstance(initial_script_name_list, str):
      initial_script_name_list = [initial_script_name_list]
    for script_name in initial_script_name_list:
      if script_name:
        script = getattr(workflow, workflow.getScriptIdByReference(script_name), None) or \
                 getattr(workflow, workflow.getTransitionIdByReference(script_name), None)
        if script is not None:
          script_path_list.append(script.getRelativeUrl())
    return script_path_list

  _reindexWorkflowVariables = lambda self, ob: \
  hasattr(aq_base(ob), 'reindexObjectSecurity') and ob.reindexObjectSecurity()

  security.declarePublic('isTransitionPossible')
  def isTransitionPossible(self, ob, transition_id, wf_id=None):
    """Test if the given transition exist from the current state.
    """
    for workflow in (wf_id and (self[wf_id],) or self.getWorkflowValueListFor(ob)):
      state = workflow._getWorkflowStateOf(ob)
      if state and transition_id in state.getDestinationReferenceList():
        return True
    return False

  getFutureStateSetFor = lambda self, wf_id, *args, **kw: \
    self[wf_id].getFutureStateSet(*args, **kw)

  security.declarePrivate('getStatusOf')
  def getStatusOf(self, workflow_id, current_object):
    # code taken from CMFCore
    """ Get the last element of a workflow history for a given workflow.
    """
    workflow_history = self.getHistoryOf(workflow_id, current_object)
    if workflow_history:
        return workflow_history[-1]
    return None

  def setStatusOf(self, wf_id, ob, status):
    """ Append an entry to the workflow history.

    o Invoked by workflow definitions.
    """
    from Products.ERP5Type.Workflow import WorkflowHistoryList as NewWorkflowHistoryList
    wfh = None
    has_history = 0
    if getattr(aq_base(ob), 'workflow_history', None) is not None:
        history = ob.workflow_history
        if history is not None:
            has_history = 1
            wfh = history.get(wf_id, None)
            if wfh is not None and not isinstance(wfh, NewWorkflowHistoryList):
                wfh = NewWorkflowHistoryList(wfh)
                ob.workflow_history[wf_id] = wfh
    if wfh is None:
        wfh = NewWorkflowHistoryList()
        if not has_history:
            ob.workflow_history = PersistentMapping()
        ob.workflow_history[wf_id] = wfh
    wfh.append(status)

  security.declareProtected(Permissions.ManagePortal, 'refreshWorklistCache')
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
      wf_ids = self.objectIds()
      for wf_id in wf_ids:
        wf = self._getOb(wf_id, None)
        if wf is not None:
          a = wf.getWorklistVariableMatchDict(info, check_guard=False)
          if a is not None:
            worklist_dict[wf_id] = a
      # End of duplicated code
      if len(worklist_dict):
        Base_zClearWorklistTable = getattr(self, 'Base_zClearWorklistTable', None)
        if Base_zClearWorklistTable is None:
          LOG('WorkflowTool', WARNING, 'Base_zClearWorklistTable cannot be found. ' \
              'Falling back to former refresh method. Please update ' \
              'erp5_worklist_sql business template.')
          self.Base_zCreateWorklistTable()
        else:
          try:
            self.Base_zClearWorklistTable()
          except ProgrammingError as error_value:
            # 1146 = table does not exist
            if error_value.args[0] != 1146:
              raise
            self.Base_zCreateWorklistTable()
        portal_catalog = self.getPortalObject().portal_catalog
        search_result = portal_catalog.unrestrictedSearchResults
        sql_catalog = portal_catalog.getSQLCatalog()
        table_column_id_set = frozenset(
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
          group_by = total_criterion_id_list
          assert COUNT_COLUMN_TITLE not in total_criterion_id_list
          select_dict = dict.fromkeys(total_criterion_id_list)
          select_dict[COUNT_COLUMN_TITLE] = 'count(*)'
          search_result_kw = {
            'select_dict': select_dict,
            'group_by': group_by,
            'query': query,
            'limit': None,
          }
          #LOG('refreshWorklistCache', WARNING, 'Using query: %s' % \
          #    (search_result(src__=1, **search_result_kw), ))
          catalog_brain_result = search_result(**search_result_kw)
          value_column_dict = {x: [] for x in table_column_id_set}
          for catalog_brain_line in catalog_brain_result.dictionaries():
            for column_id, value in six.iteritems(catalog_brain_line):
              if column_id in value_column_dict:
                value_column_dict[column_id].append(value)
          if len(value_column_dict[COUNT_COLUMN_TITLE]):
            try:
              Base_zInsertIntoWorklistTable(**value_column_dict)
            except (ProgrammingError, OperationalError) as error_value:
              # OperationalError 1054 = unknown column
              if isinstance(error_value, OperationalError) and error_value.args[0] != 1054:
                raise
              LOG('WorkflowTool', WARNING, 'Insertion in worklist cache table ' \
                  'failed. Recreating table and retrying.',
                  error=True)
              self.Base_zCreateWorklistTable()
              Base_zInsertIntoWorklistTable(**value_column_dict)

  def _getWorklistIgnoredSecurityColumnSet(self):
    return getattr(self,
      'Base_getWorklistIgnoredSecurityColumnSet', lambda: ())()

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
    actions = []
    portal = self.getPortalObject()
    developer_mode_enabled = portal.portal_preferences.getPreferredHtmlStyleDevelopperMode()

    if info.object is not None:
      object_portal_type = info.object.getTypeInfo()
      if object_portal_type is not None:
        for wf_id in object_portal_type.getTypeWorkflowList():
          wf = self._getOb(wf_id, None)
          if wf is not None:
            if developer_mode_enabled:
              actions.append({
                "id": "onlyjio_%s" % wf.getReference(),
                "name": wf.getTitle(),
                "url": "%s/Base_redirectToWorkflowDocument?workflow_id=%s" % (
                  wf.absolute_url(),
                  wf.getId()),
                "icon": None,
                "category": "object_onlyjio_jump",
                "priority": 100
              })
            actions.extend(wf.listObjectActions(info))

    portal_url = portal.portal_url()
    def _getWorklistActionList():
      worklist_dict = {}
      for wf in self.objectValues():
        if wf is not None:
          a = wf.getWorklistVariableMatchDict(info)
          if a is not None:
            worklist_dict[wf.getId()] = a
      if not worklist_dict:
        return ()
      is_anonymous = portal.portal_membership.isAnonymousUser()
      portal_catalog = portal.portal_catalog
      sql_catalog = portal_catalog.getSQLCatalog()
      catalog_security_uid_groups_columns_dict = \
        sql_catalog.getSQLCatalogSecurityUidGroupsColumnsDict()
      getSecurityUidDictAndRoleColumnDict = \
        portal_catalog.getSecurityUidDictAndRoleColumnDict
      search_result_ = getattr(self, "Base_getCountFromWorklistTable", None)
      use_cache = search_result_ is not None
      if use_cache:
        ignored_security_column_id_set = self._getWorklistIgnoredSecurityColumnSet()
        ignored_security_uid_parameter_set = {x
          for x, y in six.iteritems(catalog_security_uid_groups_columns_dict)
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
        count_column_expression = 'sum(`%s`)' % (COUNT_COLUMN_TITLE, )
        # Prevent catalog from trying to join
        getQuery = SimpleQuery
        # BBB
        def search_result(select_dict, group_by, query, limit, src__):
          select_item_list = []
          for alias, expression in six.iteritems(select_dict):
            if expression is None:
              expression = alias
            select_item_list.append('%s AS %s' % (expression, alias))
          return search_result_(
            select_expression=','.join(select_item_list),
            group_by_expression=','.join(group_by),
            query=query,
            limit=limit,
            src__=src__,
          )
      else:
        search_result = portal_catalog.unrestrictedSearchResults
        count_column_expression = 'count(*)'
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
        group_by = total_criterion_id_list
        assert COUNT_COLUMN_TITLE not in total_criterion_id_list
        select_dict = dict.fromkeys(total_criterion_id_list)
        select_dict[COUNT_COLUMN_TITLE] = count_column_expression
        catalog_brain_result = []
        try:
          catalog_brain_result = search_result(
                                      select_dict=select_dict,
                                      group_by=group_by,
                                      query=query,
                                      limit=None,
                                      src__=src__)
        except Unauthorized:
          if not is_anonymous:
            raise
          LOG('WorkflowTool.listActions', WARNING,
              'Exception while computing worklists: %s'
              % grouped_worklist_dict.keys(),
              error=True)
          continue
        except ProgrammingError as error_value:
          # 1146 = table does not exist
          if not use_cache or error_value.args[0] != 1146:
            raise
          try:
            self.Base_zCreateWorklistTable()
          except ProgrammingError as error_value:
            # 1050 = table exists (alarm run just a bit too late)
            if error_value.args[0] != 1050:
              raise
        if src__:
          action_list.append(catalog_brain_result)
        else:
          grouped_worklist_result = sumCatalogResultByWorklist(
            grouped_worklist_dict=grouped_worklist_dict,
            catalog_result=catalog_brain_result)
          for key, value in six.iteritems(grouped_worklist_result):
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
    if src__:
      actions = _getWorklistActionList()
    else:
      actions.extend(CachingMethod(
        _getWorklistActionList,
        id=(
          '_getWorklistActionList',
          _getAuthenticatedUser(self).getIdOrUserName(),
          portal_url,
        ),
        cache_factory = 'erp5_ui_short',
      )())
    return actions

from Products.ERP5Type import WITH_LEGACY_WORKFLOW
if WITH_LEGACY_WORKFLOW:
  # DCWorkflow copy/paste: WorkflowTool inherits from but CMFCore.WorkflowTool,
  # ObjectManager ends up before IFAwareObjectManager in mro()...
  from OFS.ObjectManager import IFAwareObjectManager
  WorkflowTool.all_meta_types = IFAwareObjectManager.all_meta_types

  # CMFCore methods checking that Workflows implement IWorkflowDefinition, not
  # implemented by ERP5 Workflow
  WorkflowTool.getWorkflowIds = \
    deprecated('getWorkflowIds() is deprecated; use objectIds()')\
              (lambda self: self.objectIds())
  WorkflowTool.security.declarePrivate('getWorkflowIds')

# XXX We still use portal_workflow.getInfoFor, that calls WorkflowTool.getWorkflowById
WorkflowTool.getWorkflowById = lambda self, wf_id: self._getOb(wf_id, None)
WorkflowTool.security.declarePrivate('getWorkflowById')

InitializeClass(WorkflowTool)


class ExclusionSequence(object):
  def __repr__(self):
    return '<%s %s>' % (
      self.__class__.__name__,
      super(ExclusionSequence, self).__repr__())


class ExclusionList(ExclusionSequence, list):
  """
    This is a dummy subclass of list.
    It is only used to detect wether contained values must be negated.
    It is not to be used outside of the scope of this document nor outside
    of the scope of worklist criterion handling.
  """


class ExclusionTuple(ExclusionSequence, tuple):
  """
    This is a dummy subclass of tuple.
    It is only used to detect wether contained values must be negated.
    It is not to be used outside of the scope of this document nor outside
    of the scope of worklist criterion handling.
  """


def getValidCriterionDict(worklist_match_dict, sql_catalog,
                          workflow_worklist_key):
  valid_criterion_dict = {}
  metadata = None
  isValidColumn = sql_catalog.isValidColumn
  for criterion_id, criterion_value in six.iteritems(worklist_match_dict):
    if isValidColumn(criterion_id):
      if isinstance(criterion_value, tuple):
        criterion_value = list(criterion_value)
      elif isinstance(criterion_value, (str,) + six.integer_types):
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
    worklist_set_dict_key = tuple(sorted(worklist_set_dict_key))
    if worklist_set_dict_key not in worklist_set_dict:
      worklist_set_dict[worklist_set_dict_key] = {}
    worklist_set_dict[worklist_set_dict_key]\
      [workflow_worklist_key] = valid_criterion_dict

def groupWorklistListByCondition(worklist_dict, sql_catalog,
      getSecurityUidDictAndRoleColumnDict=None,
      catalog_security_uid_groups_columns_dict=None,
    ):
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
  for workflow_id, worklist in six.iteritems(worklist_dict):
    for worklist_id, worklist_match_dict in six.iteritems(worklist):
      if not worklist_id:
        continue
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

        for local_roles_group_id, uid_list in six.iteritems(uid_dict):
          role_column_dict[
            catalog_security_uid_groups_columns_dict[local_roles_group_id]] = uid_list

        # Make sure every item is a list - or a tuple
        for security_column_id in six.iterkeys(role_column_dict):
          value = role_column_dict[security_column_id]
          if not isinstance(value, (tuple, list)):
            role_column_dict[security_column_id] = [value]
        applied_security_criterion_dict = {}
        # TODO: make security criterions be examined in the same order for all
        # worklists if possible at all.
        for security_column_id, security_column_value in \
            six.iteritems(role_column_dict):
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

def generateNestedQuery(getQuery, priority_list, criterion_dict,
                        possible_worklist_id_dict=None):
  """
  """
  assert possible_worklist_id_dict is None \
         or len(possible_worklist_id_dict) != 0
  my_priority_list = priority_list[:]
  my_criterion_id = my_priority_list.pop()
  query_list = []
  append = query_list.append
  my_criterion_dict = criterion_dict[my_criterion_id]
  if len(my_priority_list) > 0:
    for criterion_value, worklist_id_dict in six.iteritems(my_criterion_dict):
      if possible_worklist_id_dict is not None:
        criterion_worklist_id_dict = worklist_id_dict.copy()
        # Do not use iterkeys since the dictionary will be modified in the
        # loop
        for worklist_id in list(criterion_worklist_id_dict):
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
            query = ComplexQuery(logical_operator='OR',
                      *(query, getQuery(**{my_criterion_id: None})))
          append(ComplexQuery(query, subcriterion_query, logical_operator='AND'))
  else:
    possible_value_list = tuple()
    impossible_value_list = tuple()
    possible = True
    for criterion_value, criterion_worklist_id_dict \
        in six.iteritems(my_criterion_dict):
      if possible_worklist_id_dict is not None:
        possible = False
        for worklist_id in six.iterkeys(criterion_worklist_id_dict):
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
      query = ComplexQuery(logical_operator='OR',
                *(query, getQuery(**{my_criterion_id: None})))
      value_query_list.append(query)
    append(ComplexQuery(logical_operator='AND', *value_query_list))
  if len(query_list):
    return ComplexQuery(logical_operator='OR', *query_list)
  return None

def getWorklistListQuery(getQuery, grouped_worklist_dict):
  """
    Return a tuple of 2 values:
    - a list of columns to select or to group by.
    - a query applying all criterions contained in provided
      grouped_worklist_dict
  """
  total_criterion_id_dict = {}
  for worklist_id, worklist in six.iteritems(grouped_worklist_dict):
    for criterion_id, criterion_value in six.iteritems(worklist):
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
    len(x) for x in six.itervalues(total_criterion_id_dict[y])))
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

  for key, metadata in six.iteritems(worklist_metadata):
    document_count = worklist_result.get(key, 0)
    if document_count:
      format_data = metadata['format_data']
      format_data._push({'count': document_count})
      append({'name': metadata['worklist_title'] % format_data,
              'url': (portal_url if not metadata['action_box_url'] else #in DCWorkflow: metadata['action_box_url] = 'None' (string)
                      '%s/%s' % (portal_url,
                                 metadata['action_box_url'] % format_data)
                     ),
              'worklist_id': metadata['worklist_id'],
              'workflow_title': metadata['workflow_title'],
              'workflow_id': metadata['workflow_id'],
              'count': format_data['count'],
              'permissions': (),  # Predetermined.
              'category': metadata['action_box_category']})
  return action_list

# XXX: see ZMySQLDA/db.py:DB.defs
# This dict is used to tell which cast to apply to worklist parameters to get
# values comparable with SQL result content.
_sql_cast_dict = {
  'i': int if six.PY3 else long,
  'l': int if six.PY3 else long,
  'n': float,
  'd': DateTime,
}
_sql_cast_fallback = str
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
  """
  worklist_result_dict = {}
  if len(catalog_result) > 0:
    # Transtype all worklist definitions where needed
    criterion_id_list_by_worklist_dict = defaultdict(list)
    class_dict = {name: _sql_cast_dict.get(x['type'], _sql_cast_fallback)
      for name, x in six.iteritems(catalog_result.data_dictionary())}
    for worklist_id, criterion_dict in six.iteritems(grouped_worklist_dict):
      for criterion_id, criterion_value_list in six.iteritems(criterion_dict):
        if type(criterion_value_list) is not ExclusionList:
          criterion_id_list_by_worklist_dict[worklist_id].append(criterion_id)
          expected_class = class_dict[criterion_id]
          if type(criterion_value_list[0]) is not expected_class:
            criterion_dict[criterion_id] = frozenset([expected_class(x) for x in criterion_value_list])
          elif type(criterion_value_list) is not frozenset:
            criterion_dict[criterion_id] = frozenset(criterion_dict[criterion_id])
    # Read catalog result and distribute to matching worklists
    for result_line in catalog_result:
      result_count = int(result_line[COUNT_COLUMN_TITLE])
      for worklist_id, criterion_dict in six.iteritems(grouped_worklist_dict):
        is_candidate = True
        for criterion_id in criterion_id_list_by_worklist_dict[worklist_id]:
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
