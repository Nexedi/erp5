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

from zLOG import LOG, WARNING

# Make sure Interaction Workflows are called even if method not wrapped

from AccessControl import Unauthorized
from Products.CMFCore.WorkflowTool import WorkflowTool
from Products.CMFCore.WorkflowCore import ObjectMoved, ObjectDeleted
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.Transitions import TRIGGER_WORKFLOW_METHOD

from Products.CMFCore.utils import getToolByName
from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery
from Products.CMFCore.utils import _getAuthenticatedUser
from Products.ERP5Type.Cache import CachingMethod

def DCWorkflowDefinition_notifyWorkflowMethod(self, ob, method_id, args=None, kw=None, transition_list=None):
    '''
    Allows the system to request a workflow action.  This method
    must perform its own security checks.
    '''
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
    self._changeStateOf(ob, tdef)

def DCWorkflowDefinition_notifyBefore(self, ob, action, args=None, kw=None, transition_list=None):
    '''
    Notifies this workflow of an action before it happens,
    allowing veto by exception.  Unless an exception is thrown, either
    a notifySuccess() or notifyException() can be expected later on.
    The action usually corresponds to a method name.
    '''
    pass

def DCWorkflowDefinition_notifySuccess(self, ob, action, result, args=None, kw=None, transition_list=None):
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
INTERNAL_CRITERION_KEY_LIST = (WORKLIST_METADATA_KEY, SECURITY_PARAMETER_ID)

def groupWorklistListByCondition(worklist_dict, acceptable_key_dict):
  """
    Get a list of dict of WorklistVariableMatchDict grouped by compatible
    conditions.
    Strip any variable which is not a catalog column.
    Keep metadata on worklists.
  
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
        ['foo', 'baz']
      Output:
        [{'workflow_A/worklist_AA': {'foo': (1, 2)}
         },
         {'workflow_A/worklist_AB': {'baz': (5, )},
          'workflow_B/worklist_BA': {'baz': (6, )}
         }
        ]
  """
  acceptable_key_dict = acceptable_key_dict.copy()
  for internal_criterion_key in INTERNAL_CRITERION_KEY_LIST:
    assert internal_criterion_key not in acceptable_key_dict
  # One entry per worklist group, based on filter criterions.
  worklist_set_dict = {}
  for workflow_id, worklist in worklist_dict.iteritems():
    for worklist_id, worklist_match_dict in worklist.iteritems():
      valid_criterion_dict = {}
      for criterion_id, criterion_value in worklist_match_dict.iteritems():
        if criterion_id in acceptable_key_dict \
           or criterion_id in INTERNAL_CRITERION_KEY_LIST:
          if isinstance(criterion_value, tuple):
            criterion_value = list(criterion_value)
          valid_criterion_dict[criterion_id] = criterion_value
        else:
          LOG('WorkflowTool_listActions', WARNING, 'Worklist %s of workflow '\
              '%s filters on variable %s which is not available in '\
              'catalog. Its value will not be checked.' % \
              (worklist_id, workflow_id, criterion_id))
      worklist_set_dict_key = [x for x in valid_criterion_dict.keys() \
                               if x != WORKLIST_METADATA_KEY]
      if len(worklist_set_dict_key):
        worklist_set_dict_key.sort()
        worklist_set_dict_key = tuple(worklist_set_dict_key)
        if worklist_set_dict_key not in worklist_set_dict:
          worklist_set_dict[worklist_set_dict_key] = {}
        worklist_set_dict[worklist_set_dict_key]\
          ['/'.join((workflow_id, worklist_id))] = valid_criterion_dict
  return worklist_set_dict.values()

def generateQueryFromTuple(criterion_id, value, securityQueryHook):
  """
    If given tuple only contains one Query/ComplexQuery, return it and ignore
    given id. Otherwise, generate a new 'IN' query with id and value.
  """
  if criterion_id == SECURITY_PARAMETER_ID:
    query = securityQueryHook(value)
  else:
    query = Query(operator='IN', **{criterion_id: value})
  return query

def generateNestedQuery(priority_list, criterion_dict, securityQueryHook=None, possible_worklist_id_dict=None):
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
        # Do not use iterkeys since the dictionary will be modified in the loop
        for worklist_id in criterion_worklist_id_dict.keys():
          if worklist_id not in possible_worklist_id_dict:
            del criterion_worklist_id_dict[worklist_id]
      else:
        criterion_worklist_id_dict = worklist_id_dict
      if len(criterion_worklist_id_dict):
        subcriterion_query = generateNestedQuery(priority_list=my_priority_list,
          criterion_dict=criterion_dict, securityQueryHook=securityQueryHook,
          possible_worklist_id_dict=criterion_worklist_id_dict)
        if subcriterion_query is not None:
          append(ComplexQuery(generateQueryFromTuple(my_criterion_id,
                                          criterion_value,
                                          securityQueryHook=securityQueryHook),
                              subcriterion_query, operator='AND'))
  else:
    if possible_worklist_id_dict is not None:
      posible_value_list = tuple()
      for criterion_value, criterion_worklist_id_dict \
          in my_criterion_dict.iteritems():
        possible = False
        for worklist_id in criterion_worklist_id_dict.iterkeys():
          if worklist_id in possible_worklist_id_dict:
            possible = True
            break
        if possible:
          posible_value_list = posible_value_list + criterion_value
    else:
      posible_value_list = my_criterion_dict.keys()
    if len(posible_value_list):
      append(generateQueryFromTuple(my_criterion_id, posible_value_list,
                                    securityQueryHook=securityQueryHook))
  if len(query_list):
    return ComplexQuery(operator='OR', *query_list)
  return None

def getWorklistListQuery(grouped_worklist_dict, securityQueryHook):
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
      if criterion_id == WORKLIST_METADATA_KEY:
        continue
      criterion_value_to_worklist_dict_dict = \
        total_criterion_id_dict.setdefault(criterion_id, {})
      criterion_value.sort()
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
                              criterion_dict=total_criterion_id_dict,
                              securityQueryHook=securityQueryHook)
  assert query is not None
  if SECURITY_PARAMETER_ID not in total_criterion_id_list:
    # This request has no defined local_roles, so we must use default
    # security query
    query = ComplexQuery(query, securityQueryHook(), operator='AND')
  group_by_expression = ', '.join([x for x in total_criterion_id_list \
                                   if x != SECURITY_PARAMETER_ID])
  assert COUNT_COLUMN_TITLE not in total_criterion_id_dict
  select_expression = 'count(*) as %s, %s' % (COUNT_COLUMN_TITLE,
                                              group_by_expression)
  return (select_expression, group_by_expression, query)

def _ensemblistMultiply(ensemble_a, ensemble_b):
  """
    Do the ensemblist multiplication on ensemble_a and ensemble_b.
    Ensembles must be lists of tuples.
    Returns a list of tuples.
    Order is preserved.
  """
  result = []
  for a in ensemble_a:
    for b in ensemble_b:
      result.append(a + b)
  return result

def ensemblistMultiply(ensemble_list):
  """
    Return a list of tuple generated from the ensemblist multiplication of
    given ensemble list.
    Order is preserved:
    - Ensemble N will always appear on the Nth position of output tuples.
    - Nth entry of input list will always appear after N-1th and before N+1th.
    Any number of ensemble can be provided in the parameter list.

    Example:
      Input:
        [['a', 'b', 'c'], [0, 1]]
      Output:
        [('a', 0), ('a', 1), ('b', 0), ('b', 1), ('c', 0), ('c', 1)]
  """
  ensemble_list_len = len(ensemble_list)
  if ensemble_list_len == 0:
    return []
  result = [(x, ) for x in ensemble_list[0]]
  for ensemble_position in xrange(1, len(ensemble_list)):
    ensemble_b = [(x, ) for x in ensemble_list[ensemble_position]]
    result = _ensemblistMultiply(result, ensemble_b)
  return result

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
  # List all unique criterions in criterion_id_list
  criterion_id_dict = {}
  for worklist in grouped_worklist_dict.itervalues():
    for criterion_id in worklist.iterkeys():
      if criterion_id in INTERNAL_CRITERION_KEY_LIST:
        continue
      criterion_id_dict[criterion_id] = None
  criterion_id_list = criterion_id_dict.keys()
  # Group all worklists converned by a set of criterion values in
  # criterion_value_to_worklist_key_dict
  # key: criterion value tuple, in the same order as in criterion_id_list
  # value: list of ids of every concerned worklist
  criterion_value_to_worklist_key_dict = {}
  for worklist_id, criterion_dict in grouped_worklist_dict.iteritems():
    # Get all the possible combinations of values for all criterions for this
    # worklist. Worklist filtering on portal_type='Foo' and 
    # validation_state in ['draft', 'validated'] is "interested" by both 
    # ('Foo', 'draft') and ('Foo', 'validated'). This generates both tuples
    # when given initial filter.
    criterion_value_key_list = ensemblistMultiply([criterion_dict[x] for x in \
                                                   criterion_id_list])
    for criterion_value_key in criterion_value_key_list:
      if criterion_value_key not in criterion_value_to_worklist_key_dict:
        criterion_value_to_worklist_key_dict[criterion_value_key] = []
      criterion_value_to_worklist_key_dict[criterion_value_key].append(
        worklist_id)
  # Read catalog result and distribute to matching worklists
  worklist_result_dict = {}
  for result_line in catalog_result:
    criterion_value_key = tuple([result_line[x] for x in criterion_id_list])
    if criterion_value_key not in criterion_value_to_worklist_key_dict:
      LOG('WorkflowTool_listActions', WARNING,
          'No worklist can be found for result combination %s' % \
          (repr(criterion_value_key), ))
      continue
    for worklist_id in \
        criterion_value_to_worklist_key_dict[criterion_value_key]:
      count = worklist_result_dict.get(worklist_id, 0)
      worklist_result_dict[worklist_id] = count + \
                                          result_line[COUNT_COLUMN_TITLE]
  return worklist_result_dict

def generateActionList(grouped_worklist_dict, worklist_result, portal_url):
  """
    For each worklist generate action_list as expected by portal_actions.
  """
  action_list = []
  append = action_list.append
  for key, value in grouped_worklist_dict.iteritems():
    document_count = worklist_result.get(key, 0)
    if document_count:
      metadata = value[WORKLIST_METADATA_KEY]
      format_data = metadata['format_data']
      format_data._push({'count': document_count})
      append({'name': metadata['worklist_title'] % format_data,
              'url': '%s/%s' % (portal_url, metadata['action_box_url'] % format_data),
              'worklist_id': metadata['worklist_id'],
              'workflow_title': metadata['workflow_title'],
              'workflow_id': metadata['workflow_id'],
              'permissions': (),  # Predetermined.
              'category': metadata['action_box_category']})
  return action_list

def WorkflowTool_listActions(self, info=None, object=None):
  """
    Returns a list of actions to be displayed to the user.

        o Invoked by the portal_actions tool.

        o Allows workflows to include actions to be displayed in the
          actions box.

        o Object actions are supplied by workflows that apply to the object.

        o Global actions are supplied by all workflows.

    This patch attemps to make listGlobalActions aware of worklists,
    which allows factorizing them into one single SQL query.
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
    portal_url = getToolByName(self, 'portal_url')()
    portal_catalog = getToolByName(self, 'portal_catalog')
    getSecurityUidListAndRoleColumnDict = portal_catalog.getSecurityUidListAndRoleColumnDict
    security_query_cache_dict = {}
    def securityQueryHook(role_list=None):
      if role_list is None:
        role_list = []
      security_cache_key = list(role_list)
      security_cache_key.sort()
      security_cache_key = tuple(security_cache_key)
      query = security_query_cache_dict.get(security_cache_key, None)
      if query is None:
        security_kw = {}
        if len(role_list):
          security_kw[SECURITY_PARAMETER_ID] = role_list
        security_uid_list, role_column_dict = getSecurityUidListAndRoleColumnDict(**security_kw)
        security_query_list = [Query(operator='IN', **{SECURITY_COLUMN_ID: security_uid_list})]
        for column_id, value in role_column_dict.iteritems():
          if not isinstance(value, (list, tuple)):
            value = (value, )
          security_query_list.append(Query(operator='IN', **{column_id: value}))
        query = ComplexQuery(operator='OR', *security_query_list)
        security_query_cache_dict[security_cache_key] = query
      return query
    def _getWorklistActionList():
      action_list = []
      acceptable_key_dict = portal_catalog.getSQLCatalog().getColumnMap()
      # Get a list of dict of WorklistVariableMatchDict grouped by compatible conditions
      worklist_list_grouped_by_condition = groupWorklistListByCondition(worklist_dict=worklist_dict, acceptable_key_dict=acceptable_key_dict)
      for grouped_worklist_dict in worklist_list_grouped_by_condition:
        # Generate the query for this worklist_list
        (select_expression, group_by_expression, query) = getWorklistListQuery(grouped_worklist_dict=grouped_worklist_dict, securityQueryHook=securityQueryHook)
        search_result = portal_catalog.unrestrictedSearchResults
        search_result_kw = {'select_expression': select_expression,
                            'group_by_expression': group_by_expression,
                            'query': query}
        #LOG('WorklistGeneration', INFO, 'Using query: %s' % (search_result(src__=1, **search_result_kw), ))
        catalog_brain_result = search_result(**search_result_kw)
        worklist_result_dict = sumCatalogResultByWorklist(grouped_worklist_dict=grouped_worklist_dict, catalog_result=catalog_brain_result)
        group_action_list = generateActionList(grouped_worklist_dict=grouped_worklist_dict, worklist_result=worklist_result_dict, portal_url=portal_url)
        action_list.extend(group_action_list)
      def get_action_ident(action):
        return '/'.join((action['workflow_id'], action['worklist_id']))
      def action_cmp(action_a, action_b):
        return cmp(get_action_ident(action_a), get_action_ident(action_b))
      action_list.sort(action_cmp)
      return action_list
    user = str(_getAuthenticatedUser(self))
    _getWorklistActionList = CachingMethod(_getWorklistActionList, id=('_getWorklistActionList', user, portal_url), cache_factory = 'erp5_ui_short')
    actions.extend(_getWorklistActionList())
  return actions 

WorkflowTool.listActions = WorkflowTool_listActions
