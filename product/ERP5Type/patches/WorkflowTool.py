##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002,2005 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import sys
from zLOG import LOG, WARNING
from types import StringTypes

# Make sure Interaction Workflows are called even if method not wrapped

from AccessControl import Unauthorized
from Products.CMFCore.WorkflowTool import WorkflowTool
from Products.CMFCore.WorkflowCore import ObjectMoved, ObjectDeleted
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.Transitions import TRIGGER_WORKFLOW_METHOD

from Products.CMFCore.utils import getToolByName
from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery, NegatedQuery
from Products.CMFCore.utils import _getAuthenticatedUser
from Products.ERP5Type.Cache import CachingMethod
from sets import ImmutableSet
from Acquisition import aq_base
from Persistence import Persistent
from Globals import PersistentMapping
from itertools import izip
from MySQLdb import ProgrammingError, OperationalError

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
SECURITY_COLUMN_ID = 'security_uid'
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

def getValidCriterionDict(worklist_match_dict, acceptable_key_dict,
                          workflow_worklist_key):
  valid_criterion_dict = {}
  metadata = None
  for criterion_id, criterion_value in worklist_match_dict.iteritems():
    if criterion_id in acceptable_key_dict:
      if isinstance(criterion_value, tuple):
        criterion_value = list(criterion_value)
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

def groupWorklistListByCondition(worklist_dict, acceptable_key_dict,
                                 getSecurityUidListAndRoleColumnDict=None):
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
        acceptable_key_dict:
        {'foo': None,
         'baz': None}
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
      if getSecurityUidListAndRoleColumnDict is None:
        valid_criterion_dict, metadata = getValidCriterionDict(
          worklist_match_dict=worklist_match_dict,
          acceptable_key_dict=acceptable_key_dict,
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
        uid_list, role_column_dict, local_role_column_dict = \
            getSecurityUidListAndRoleColumnDict(**security_kw)

        for key, value in local_role_column_dict.items():
          worklist_match_dict[key] = [value]

        if len(uid_list):
          uid_list.sort()
          role_column_dict[SECURITY_COLUMN_ID] = uid_list
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
            acceptable_key_dict=acceptable_key_dict,
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

def generateNestedQuery(priority_list, criterion_dict,
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
          priority_list=my_priority_list,
          criterion_dict=criterion_dict,
          possible_worklist_id_dict=criterion_worklist_id_dict)
        if subcriterion_query is not None:
          query = Query(operator='IN',
                        **{my_criterion_id: criterion_value})
          if isinstance(criterion_value, ExclusionTuple):
            query = NegatedQuery(query)
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
      query = Query(operator='IN', **{my_criterion_id: possible_value_list})
      value_query_list.append(query)
    if len(impossible_value_list):
      query = Query(operator='IN', **{my_criterion_id: impossible_value_list})
      query = NegatedQuery(query)
      value_query_list.append(query)
    append(ComplexQuery(operator='AND', *value_query_list))
  if len(query_list):
    return ComplexQuery(operator='OR', *query_list)
  return None

def getWorklistListQuery(grouped_worklist_dict):
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
  total_criterion_id_list = total_criterion_id_dict.keys()
  def criterion_id_cmp(criterion_id_a, criterion_id_b):
    return cmp(max([len(x) for x in \
                    total_criterion_id_dict[criterion_id_a].itervalues()]),
               max([len(x) for x in \
                    total_criterion_id_dict[criterion_id_b].itervalues()]))
  total_criterion_id_list.sort(criterion_id_cmp)
  query = generateNestedQuery(priority_list=total_criterion_id_list,
                              criterion_dict=total_criterion_id_dict)
  assert query is not None
  assert COUNT_COLUMN_TITLE not in total_criterion_id_dict
  return (total_criterion_id_list, query)

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
    class_dict = dict(((name, value.__class__) for name, value in \
                       izip(catalog_result.names(), catalog_result[0])))
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

def WorkflowTool_listActions(self, info=None, object=None, src__=False):
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

  if len(worklist_dict):
    is_anonymous = getToolByName(self, 'portal_membership').isAnonymousUser()
    portal_url = getToolByName(self, 'portal_url')()
    portal_catalog = getToolByName(self, 'portal_catalog')
    search_result = getattr(self, "Base_getCountFromWorklistTable", None)
    use_cache = search_result is not None
    if use_cache:
      select_expression_prefix = 'sum(`%s`) as %s' % (COUNT_COLUMN_TITLE, COUNT_COLUMN_TITLE)
    else:
      search_result = portal_catalog.unrestrictedSearchResults
      select_expression_prefix = 'count(*) as %s' % (COUNT_COLUMN_TITLE, )
    getSecurityUidListAndRoleColumnDict = \
      portal_catalog.getSecurityUidListAndRoleColumnDict
    security_query_cache_dict = {}
    def _getWorklistActionList():
      worklist_result_dict = {}
      sql_catalog = portal_catalog.getSQLCatalog()
      acceptable_key_dict = sql_catalog.getColumnMap().copy()
      for related_key in sql_catalog.getSQLCatalogRelatedKeyList():
        related_key = related_key.split('|')
        acceptable_key_dict[related_key[0].strip()] = related_key[1].strip()
      # Get a list of dict of WorklistVariableMatchDict grouped by compatible
      # conditions
      (worklist_list_grouped_by_condition, worklist_metadata) = \
        groupWorklistListByCondition(
          worklist_dict=worklist_dict,
          acceptable_key_dict=acceptable_key_dict,
          getSecurityUidListAndRoleColumnDict=\
            getSecurityUidListAndRoleColumnDict)
      if src__:
        action_list = []
      for grouped_worklist_dict in worklist_list_grouped_by_condition:
        # Generate the query for this worklist_list
        (total_criterion_id_list, query) = \
          getWorklistListQuery(grouped_worklist_dict=grouped_worklist_dict)
        group_by_expression = ', '.join(total_criterion_id_list)
        assert COUNT_COLUMN_TITLE not in total_criterion_id_list
        getRelatedTableMapDict = getattr(query, 'getRelatedTableMapDict', None)
        if getRelatedTableMapDict is None:
          # If required mapping method is not present on the query, assume it
          # handles column mapping properly, and build a bare select
          # expression.
          select_expression = select_expression_prefix + ', ' \
                              + group_by_expression
        else:
          # We must compute alias names ourselves because we need to know them
          # in order to compute 'select_expression'.
          related_table_map_dict = query.getRelatedTableMapDict()
          # In order to support related keys, the select expression must be
          # completely explicited, to avoid conflicts.
          select_expression = [select_expression_prefix]
          for criterion_id in total_criterion_id_list:
            mapped_key = acceptable_key_dict[criterion_id]
            if use_cache: # no support for related keys
              select_expression.append(criterion_id)
              continue
            elif isinstance(mapped_key, str): # related key
              mapped_key = mapped_key.split('/')
              related_table_map_dict[criterion_id] = table_alias_list = tuple(
                (table_id, '%s_%s' % (criterion_id, i))
                for i, table_id in enumerate(mapped_key[0].split(',')))
              table_id, column_id = table_alias_list[-1][1], mapped_key[1]
            else: # normal column
              if len(mapped_key) == 1:
                table_id = mapped_key[0]
              else:
                table_id = 'catalog'
                assert table_id in mapped_key
              column_id = criterion_id
            select_expression.append('%s.%s as %s'
                                     % (table_id, column_id, criterion_id))
          query.getRelatedTableMapDict = lambda: related_table_map_dict
          select_expression = ', '.join(select_expression)
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
        if src__:
          action_list.append(catalog_brain_result)
        else:
          grouped_worklist_result = sumCatalogResultByWorklist(
            grouped_worklist_dict=grouped_worklist_dict,
            catalog_result=catalog_brain_result)
          for key, value in grouped_worklist_result.iteritems():
            worklist_result_dict[key] = value + worklist_result_dict.get(key, 0)
      if not src__:
        action_list = generateActionList(worklist_metadata=worklist_metadata,
                                         worklist_result=worklist_result_dict,
                                         portal_url=portal_url)
        def get_action_ident(action):
          return '/'.join((action['workflow_id'], action['worklist_id']))
        def action_cmp(action_a, action_b):
          return cmp(get_action_ident(action_a), get_action_ident(action_b))
        action_list.sort(action_cmp)
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

WorkflowTool.listActions = WorkflowTool_listActions

def WorkflowTool_refreshWorklistCache(self):
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
        a = wf.getWorklistVariableMatchDict(info)
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
      acceptable_key_dict = sql_catalog.getColumnMap()
      # XXX: those hardcoded lists should be grabbed from the table dynamicaly
      # (and cached).
      table_column_id_set = ImmutableSet(
          [COUNT_COLUMN_TITLE] + self.Base_getWorklistTableColumnIDList())
      security_column_id_list = ['security_uid'] + \
        [x[1] for x in sql_catalog.getSQLCatalogRoleKeysList()] + \
        [x[1] for x in sql_catalog.getSQLCatalogLocalRoleKeysList()]
      (worklist_list_grouped_by_condition, worklist_metadata) = \
        groupWorklistListByCondition(
          worklist_dict=worklist_dict,
          acceptable_key_dict=acceptable_key_dict)
      assert COUNT_COLUMN_TITLE in table_column_id_set
      for grouped_worklist_dict in worklist_list_grouped_by_condition:
        # Generate the query for this worklist_list
        (total_criterion_id_list, query) = \
          getWorklistListQuery(grouped_worklist_dict=grouped_worklist_dict)
        for criterion_id in total_criterion_id_list:
          assert criterion_id in table_column_id_set
        for security_column_id in security_column_id_list:
          assert security_column_id not in total_criterion_id_list
          assert security_column_id in table_column_id_set
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
        value_column_dict = dict([(x, []) for x in table_column_id_set])
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

WorkflowTool.refreshWorklistCache = WorkflowTool_refreshWorklistCache

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

def WorkflowTool_setStatusOf(self, wf_id, ob, status):
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

WorkflowTool.setStatusOf = WorkflowTool_setStatusOf

WorkflowTool.getFutureStateSetFor = lambda self, wf_id, *args, **kw: \
  self[wf_id].getFutureStateSet(*args, **kw)
