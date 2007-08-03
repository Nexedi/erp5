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

from zLOG import LOG, WARNING, BLATHER, TRACE

# Make sure Interaction Workflows are called even if method not wrapped

from Products.CMFCore.WorkflowTool import WorkflowTool
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.CMFCore.utils import getToolByName
from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery
from Products.CMFCore.utils import _getAuthenticatedUser
from Products.ERP5Type.Cache import CachingMethod

def WorkflowTool_wrapWorkflowMethod(self, ob, method_id, func, args, kw):

    """ To be invoked only by WorkflowCore.
        Allows a workflow definition to wrap a WorkflowMethod.

        By default, the workflow tool takes the first workflow wich
        support the method_id. In ERP5, with Interaction Worfklows, we
        may have many workflows wich can support a worfklow method,
        that's why we need this patch.

        Current implementation supports:
        - at most 1 DCWorkflow per portal type per method_id
        - as many Interaction workflows as needed per portal type

        NOTE: automatic transitions are invoked through
        _findAutomaticTransition in DC Workflows.

        TODO: make it possible to have multiple DC Workflow
        per portal type per method_id (XXX). This could be useful
        for example to make the edit WorkflowMethod trigger
        multiple automatic actions in different workflows.
        More discussion needed on this.
    """
    # Check workflow containing the workflow method
    wf_list = []
    wfs = self.getWorkflowsFor(ob)
    if wfs:
      for w in wfs:
        if (hasattr(w, 'isWorkflowMethodSupported')
            and w.isWorkflowMethodSupported(ob, method_id)):
          wf_list.append(w)
    else:
      wfs = ()
    # If no transition matched, simply call the method    
    # And return
    if len(wf_list)==0:
      return apply(func, args, kw)
    # Call notifyBefore on each workflow
    for w in wfs:
      w.notifyBefore(ob, method_id, args=args, kw=kw)
    # Call the method on matching workflows
    only_interaction_defined = 1
    for w in wf_list:
      if w.__class__.__name__ != 'InteractionWorkflowDefinition':
        only_interaction_defined = 0
        # XXX - There is a problem here if the same workflow method
        # is used by multiple workflows. Function "func" will be
        # called multiple times. Patch or changes required to mak
        # sure func is only called once.
        # Solution consists in reimplementing _invokeWithNotification
        # at the level of each workflow without notification
        # (ex. _invokeWithoutNotification)
        result = self._invokeWithNotification(
            [], ob, method_id, w.wrapWorkflowMethod,
            (ob, method_id, func, args, kw), {})
    # If only interaction workflows are defined, we need to call the method
    # manually
    if only_interaction_defined:
      result = apply(func, args, kw)
    # Call notifySuccess on each workflow
    for w in wfs:
      w.notifySuccess(ob, method_id, result, args=args, kw=kw)
    return result
    
WorkflowTool.wrapWorkflowMethod = WorkflowTool_wrapWorkflowMethod

def DCWorkflowDefinition_notifyBefore(self, ob, action, args=None, kw=None):
    '''
    Notifies this workflow of an action before it happens,
    allowing veto by exception.  Unless an exception is thrown, either
    a notifySuccess() or notifyException() can be expected later on.
    The action usually corresponds to a method name.
    '''
    pass

def DCWorkflowDefinition_notifySuccess(self, ob, action, result, args=None, kw=None):
    '''
    Notifies this workflow that an action has taken place.
    '''
    pass

DCWorkflowDefinition.notifyBefore = DCWorkflowDefinition_notifyBefore
DCWorkflowDefinition.notifySuccess = DCWorkflowDefinition_notifySuccess

WORKLIST_METADATA_KEY = 'metadata'
SECURITY_PARAMETER_ID = 'local_roles'
SECURITY_COLUMN_ID = 'security_uid'
COUNT_COLUMN_TITLE = 'count'
INTERNAL_CRITERION_KEY_LIST = (WORKLIST_METADATA_KEY, SECURITY_PARAMETER_ID)

def groupWorklistListByCondition(worklist_dict, acceptable_key_dict, getSecurityUidListAndRoleColumnDict):
  """
    Get a list of dict of WorklistVariableMatchDict grouped by compatible conditions.
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
  security_cache = {}
  for workflow_id, worklist in worklist_dict.iteritems():
    for worklist_id, worklist_match_dict in worklist.iteritems():
      valid_criterion_dict = {}
      for criterion_id, criterion_value in worklist_match_dict.iteritems():
        if criterion_id in acceptable_key_dict or criterion_id in WORKLIST_METADATA_KEY:
          valid_criterion_dict[criterion_id] = criterion_value
        elif criterion_id == SECURITY_PARAMETER_ID:
          # Caching is done at this level to be as fast as possible.
          security_cache_key = list(criterion_value)
          security_cache_key.sort()
          security_cache_key = tuple(security_cache_key)
          if security_cache_key in security_cache:
            criterion_value = security_cache[security_cache_key]
          else:
            security_uid_list, role_column_dict = getSecurityUidListAndRoleColumnDict(**{criterion_id: criterion_value})
            # XXX: role_column_dict is ignored for now. This must be
            # implemented.
            criterion_value = security_uid_list
            security_cache[security_cache_key] = criterion_value
          criterion_id = SECURITY_COLUMN_ID
        else:
          LOG('WorkflowTool_listActions', WARNING, 'Worklist %s of workflow '\
              '%s filters on variable %s which is not available in '\
              'catalog. Its value will not be checked.' % \
              (worklist_id, workflow_id, criterion_id))
      if len(valid_criterion_dict):
        worklist_set_dict_key = [x for x in valid_criterion_dict.keys() if x != WORKLIST_METADATA_KEY]
        worklist_set_dict_key.sort()
        worklist_set_dict_key = tuple(worklist_set_dict_key)
        if worklist_set_dict_key not in worklist_set_dict:
          worklist_set_dict[worklist_set_dict_key] = {}
        worklist_set_dict[worklist_set_dict_key]['/'.join((workflow_id, worklist_id))] = valid_criterion_dict
  return worklist_set_dict.values()

def generateNestedQuery(priority_list, criterion_dict, possible_worklist_id_dict=None):
  """
  """
  assert possible_worklist_id_dict is None or len(possible_worklist_id_dict) != 0
  my_priority_list = priority_list[:]
  my_criterion_id = my_priority_list.pop(0)
  query_list = []
  append = query_list.append
  my_criterion_dict = criterion_dict[my_criterion_id]
  if len(my_priority_list) > 0:
    for criterion_value, worklist_id_dict in my_criterion_dict.iteritems():
      if possible_worklist_id_dict is not None:
        criterion_worklist_id_dict = worklist_id_dict.copy()
        for worklist_id in criterion_worklist_id_dict.keys(): # Do not use iterkey since the dictionnary will be modified in the loop.
          if worklist_id not in possible_worklist_id_dict:
            del criterion_worklist_id_dict[worklist_id]
      else:
        criterion_worklist_id_dict = worklist_id_dict
      if len(criterion_worklist_id_dict):
        subcriterion_query = generateNestedQuery(priority_list=my_priority_list, criterion_dict=criterion_dict, possible_worklist_id_dict=criterion_worklist_id_dict)
        if subcriterion_query is not None:
          append(ComplexQuery(Query(operator='IN', **{my_criterion_id: criterion_value}), subcriterion_query, operator='AND'))
  else:
    if possible_worklist_id_dict is not None:
      posible_value_list = tuple()
      for criterion_value, criterion_worklist_id_dict in my_criterion_dict.iteritems():
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
      append(Query(operator='IN', **{my_criterion_id: posible_value_list}))
  if len(query_list):
    return ComplexQuery(operator='OR', *query_list)
  return None

def getWorklistListQuery(grouped_worklist_dict):
  """
    Return a tuple of 3 value:
    - a select_expression with a count(*) and all columns used in goup_by_expression
    - a group_by_expression with all columns required for provided grouped_worklist_dict
    - a query applying all criterions contained in provided grouped_worklist_dict
  """
  query_list = []
  total_criterion_id_dict = {}
  for worklist_id, worklist in grouped_worklist_dict.iteritems():
    for criterion_id, criterion_value in worklist.iteritems():
      if criterion_id == WORKLIST_METADATA_KEY:
        continue
      criterion_value_to_worklist_dict_dict = total_criterion_id_dict.setdefault(criterion_id, {})
      criterion_value.sort()
      criterion_value = tuple(criterion_value)
      criterion_value_to_worklist_dict = criterion_value_to_worklist_dict_dict.setdefault(criterion_value, {})
      criterion_value_to_worklist_dict[worklist_id] = None
  total_criterion_id_list = total_criterion_id_dict.keys()
  def criterion_id_cmp(criterion_id_a, criterion_id_b):
    return cmp(max([len(x) for x in total_criterion_id_dict[criterion_id_a].itervalues()]),
               max([len(x) for x in total_criterion_id_dict[criterion_id_b].itervalues()]))
  total_criterion_id_list.sort(criterion_id_cmp)
  total_criterion_id_list.reverse()
  query = generateNestedQuery(priority_list=total_criterion_id_list, criterion_dict=total_criterion_id_dict)
  assert query is not None
  group_by_expression = ', '.join([x for x in total_criterion_id_dict.keys() if x != SECURITY_COLUMN_ID])
  assert COUNT_COLUMN_TITLE not in total_criterion_id_dict
  select_expression = 'count(*) as %s, %s' % (COUNT_COLUMN_TITLE, group_by_expression)
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
    Return a list of tuple generated from the ensemblist multiplication of given ensemble list.
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
  criterion_id_dict = {}
  for worklist in grouped_worklist_dict.itervalues():
    for criterion_id in worklist.iterkeys():
      if criterion_id in INTERNAL_CRITERION_KEY_LIST:
        continue
      criterion_id_dict[criterion_id] = None
  criterion_id_list = criterion_id_dict.keys()
  criterion_value_to_worklist_key_dict = {}
  for worklist_id, criterion_dict in grouped_worklist_dict.iteritems():
    criterion_value_key_list = ensemblistMultiply([criterion_dict[x] for x in criterion_id_list])
    for criterion_value_key in criterion_value_key_list:
      if criterion_value_key not in criterion_value_to_worklist_key_dict:
        criterion_value_to_worklist_key_dict[criterion_value_key] = []
      criterion_value_to_worklist_key_dict[criterion_value_key].append(worklist_id)
  worklist_result_dict = {}
  for result_line in catalog_result:
    criterion_value_key = tuple([result_line[x] for x in criterion_id_list])
    for worklist_id in criterion_value_to_worklist_key_dict[criterion_value_key]:
      count = worklist_result_dict.get(worklist_id, 0)
      worklist_result_dict[worklist_id] = count + result_line[COUNT_COLUMN_TITLE]
  return worklist_result_dict

def generateActionList(grouped_worklist_dict, worklist_result, portal_url):
  """
    For each worklist generate action_list as expected by portal_actions.
  """
  action_dict = {}
  for key, value in grouped_worklist_dict.iteritems():
    document_count = worklist_result.get(key, 0)
    if document_count:
      metadata = value[WORKLIST_METADATA_KEY]
      format_data = metadata['format_data']
      format_data._push({'count': document_count})
      action_dict[key] = {'name': metadata['worklist_title'] % format_data,
                          'url': '%s/%s' % (portal_url, metadata['action_box_url'] % format_data),
                          'worklist_id': metadata['worklist_id'],
                          'workflow_title': metadata['workflow_title'],
                          'workflow_id': metadata['workflow_id'],
                          'permissions': (),  # Predetermined.
                          'category': metadata['action_box_category']}
  action_dict_key_list = action_dict.keys()
  action_dict_key_list.sort()
  return [action_dict[x] for x in action_dict_key_list]

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
    def _getWorklistActionList():
      portal_url = getToolByName(self, 'portal_url')()
      portal_catalog = getToolByName(self, 'portal_catalog')
      getSecurityUidList = portal_catalog.getSecurityUidList
      acceptable_key_dict = portal_catalog.getSQLCatalog().getColumnMap()
      # Get a list of dict of WorklistVariableMatchDict grouped by compatible conditions
      worklist_list_grouped_by_condition = groupWorklistListByCondition(worklist_dict=worklist_dict, acceptable_key_dict=acceptable_key_dict, getSecurityUidList=getSecurityUidList)
      LOG('WorklistGeneration', BLATHER, 'Will grab worklists in %s passes.' % (len(worklist_list_grouped_by_condition), ))
      for grouped_worklist_dict in worklist_list_grouped_by_condition:
        LOG('WorklistGeneration', BLATHER, 'Grabbing %s worklists...' % (len(grouped_worklist_dict), ))
        # Generate the query for this worklist_list
        (select_expression, group_by_expression, query) = getWorklistListQuery(grouped_worklist_dict=grouped_worklist_dict)
        search_result = portal_catalog.unrestrictedSearchResults
        search_result_kw = {'select_expression': select_expression,
                            'group_by_expression': group_by_expression,
                            'query': query}
        LOG('WorklistGeneration', TRACE, 'Using query: %s' % (search_result(src__=1, **search_result_kw), ))
        catalog_brain_result = search_result(**search_result_kw)
        LOG('WorklistGeneration', BLATHER, '%s results' % (len(catalog_brain_result), ))
        worklist_result_dict = sumCatalogResultByWorklist(grouped_worklist_dict=grouped_worklist_dict, catalog_result=catalog_brain_result)
        LOG('WorklistGeneration', BLATHER, 'Distributed into %s worklists.'% (len(worklist_result_dict), ))
        action_list = generateActionList(grouped_worklist_dict=grouped_worklist_dict, worklist_result=worklist_result_dict, portal_url=portal_url)
        LOG('WorklistGeneration', BLATHER, 'Creating %s actions.' % (len(action_list), ))
        return action_list
    user = str(_getAuthenticatedUser(self))
    _getWorklistActionList = CachingMethod(_getWorklistActionList, id=('_getWorklistActionList', user), cache_factory = 'erp5_ui_short')
    actions.extend(_getWorklistActionList())
  return actions 

WorkflowTool.listActions = WorkflowTool_listActions
