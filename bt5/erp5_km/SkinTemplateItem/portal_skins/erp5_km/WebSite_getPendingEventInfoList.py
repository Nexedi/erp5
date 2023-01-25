"""
This scripts returns all documents related to a worklist
by creating a big Complex Query from each worklist
definition.

Romain: this script could be a site killer, as it remove all optimisations done for worklist calculation (like sql_cache).
 XXX TODO: Use WorkflowTool_listActions instead, which uses optimisation and cache the results
      OR remove, and uses gadget instead
"""

from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery

portal = context.getPortalObject()
action_list = portal.portal_actions.listFilteredActionsFor(context)
global_action_list = action_list['global']
ordered_global_action_list = portal.getOrderedGlobalActionList(global_action_list)

# Initialise query
query_list = []

# Assemble query
for action in ordered_global_action_list:
  workflow_id = action.get('workflow_id', None)
  worklist_id = action.get('worklist_id', None)
  if workflow_id is not None and worklist_id is not None:
    # get worklist defined local roles
    local_roles = context.Base_getWorkflowWorklistInfo(workflow_id, worklist_id)
    query_dict = context.WebSite_getWorklistSettingsFor(action)
    if query_dict:
      sub_query_list = []
      for k, v in query_dict.items():
        sub_query_list.append(Query(**{k: v}))
      complex_query = ComplexQuery(logical_operator="AND", *sub_query_list)
      # add to query filtering by local roles as defined in worklist
      complex_query = portal.portal_catalog.getSecurityQuery(query=complex_query, local_roles=local_roles)
      query_list.append(complex_query)

# Return empty list if nothing defined
if not query_list:
  if kw.get('_count', 0):
    return [[0]]
  else:
    return []

# Invoke catalog
query = ComplexQuery(logical_operator="OR", *query_list)
#query = portal.portal_catalog.getSecurityQuery(query)
#result_list = portal.portal_catalog(query=query,
#                                    sort_on='modification_date',
#                                    sort_order='reverse')
kw['query'] = query
kw['sort_order'] = 'reverse'

if kw.get('_count', 0):
  del kw['_count']
  return portal.portal_catalog.countResults(**kw)

return portal.portal_catalog(**kw)
