import json
portal = context.getPortalObject()
graph = {'node': {}, 'edge': {}}


class_definition = {
  'movement': {
    '_class': 'edge',
    'type': 'object',
    'description': 'Movement changing the location of the item',
    'properties': { }
  },
  'node': {
    '_class': 'node',
    'type': 'object',
    'description': 'A Node where the item was moved to',
    'properties': { },
  },
}

for i, tracking in enumerate(reversed(portal.portal_simulation.getTrackingList(aggregate_uid=context.getUid()))):
  movement = portal.portal_catalog.getObject(tracking.delivery_uid)
  for node in (movement.getSourceValue(), movement.getDestinationValue()):
    if node:
      graph['node'][node.getUid()] = dict(
        _class='node',
        name=node.getTitle(),
        link=node.absolute_url())
    else:
      graph['node']["null"] = dict(
        _class='node',
        name="(origin)")

  graph['edge'][movement.getUid()] = dict(
    _class="movement",
    name="%s: %s (%s)" % (i+1, movement.getTitle(), movement.getStopDate().strftime("%Y/%m/%d")),
    link=movement.absolute_url(),
    source=movement.getSourceUid() or "null",
    destination=movement.getDestinationUid() or "null")
return json.dumps(
  dict(graph=graph, class_definition=class_definition),
  sort_keys=True,
  indent=2)
