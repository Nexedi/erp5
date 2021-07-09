import json
business_process = sci['object']
graph = business_process.getProperty('jsplumb_graph')

#assert graph

if graph:
  portal = business_process.getPortalObject()
  trade_state_dict = dict(start=None, end=None)
  for trade_state in portal.portal_categories.trade_state.getCategoryChildValueList():
    # XXX I hope no duplicates
    trade_state_dict[trade_state.getReference() or trade_state.getId()] = trade_state

  graph = json.loads(graph)['graph']
  for edge_data in graph['edge'].values():
    # Create the business link if it does not exist yet.
    if not edge_data.get('business_link_url'):
      business_link = business_process.newContent(
        portal_type='Business Link',
        predecessor_value=trade_state_dict[edge_data['source']],
        successor_value=trade_state_dict[edge_data['destination']],
      )
    else:
  # XXX Zope does not like to traverse unicode ...
      business_link = portal.restrictedTraverse(str(edge_data['business_link_url']))
    business_link.edit(
        title=edge_data.get('name'),
  # XXX Zope does not like to traverse unicode ...
        trade_phase=str(edge_data.get('trade_phase', '')),
    )
