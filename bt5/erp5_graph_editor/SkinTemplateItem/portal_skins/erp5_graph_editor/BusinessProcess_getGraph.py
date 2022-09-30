from Products.ERP5Type.Message import translateString
import json
portal = context.getPortalObject()

# if a graph has been saved, we use this info for node coordinates.
position_graph = context.getProperty('jsplumb_graph')
if position_graph:
  position_graph = json.loads(position_graph)['graph']

visited_business_process_set = set() # prevent infinite recurisions

def getBusinessProcessGraph(business_process):
  graph = dict(node=dict(start=dict(_class='erp5.business_process.start',
                                    name=str(translateString('Start'))),
                         end=dict(_class='erp5.business_process.end',
                                  name=str(translateString('End'))),),
               edge=dict())


  for trade_state in portal.portal_categories.trade_state.getCategoryChildValueList(): # XXX do we really want to display all trade states ?
    state_id = trade_state.getReference() or trade_state.getId()
    graph['node'][state_id] = dict(
        _class='erp5.business_process.trade_state',
        name=trade_state.getTranslatedTitle())

  for state_id in graph['node'].keys():
    if position_graph and state_id in position_graph['node']:
      graph['node'][state_id]['coordinate'] = position_graph['node'][state_id]['coordinate']

  if business_process in visited_business_process_set:
    return graph
  visited_business_process_set.add(business_process)
  for link in business_process.contentValues(portal_type='Business Link'):

    predecessor = 'start'
    if link.getPredecessor():
      predecessor = link.getPredecessorReference() or link.getPredecessorId()
    successor = 'end'
    if link.getSuccessor():
      successor = link.getSuccessorReference() or link.getSuccessorId()

    graph['edge'][link.getRelativeUrl()] = dict(
        _class='erp5.business_process.business_link',
        source=predecessor,
        destination=successor,
        name=link.getTranslatedTitle(),
        business_link_url=link.getRelativeUrl(),
        trade_phase=link.getTradePhase() or '')

  for specialise in [context] + business_process.getSpecialiseValueList(portal_type='Business Process'):
    specialise_graph = getBusinessProcessGraph(specialise)
    for node_id, node_data in specialise_graph['node'].items():
      graph['node'].setdefault(node_id, node_data)
    for node_id, node_data in specialise_graph['edge'].items():
      graph['edge'].setdefault(node_id, node_data)
  return graph


class_definition = {
  'erp5.business_process.business_link': {
    '_class': 'edge',
    'type': 'object',
    'description': 'An ERP5 Business Link',
    'properties': {
      'name': {'type': 'string', 'name': str(translateString('Name'))},
      'trade_phase': {'type': 'string', 'name': str(translateString('Trade Phase')), 'enum': [''] + [
          trade_phase.getId() for trade_phase in portal.portal_categories.trade_phase.getCategoryChildValueList(local_sort_on=('int_index', 'title'))]},
    }
  }
}

return json.dumps(dict(graph=getBusinessProcessGraph(context), class_definition=class_definition), indent=2)
