import json
portal_actitivities = context.getPortalObject().portal_activities

distribution_node = ''
processing_nodes = []
idle_nodes = []

# Store each node to distribution, processing or idle group
# in function of his port number.
node_list = portal_actitivities.getNodeList()
for node in node_list:
  port = int(node.split(":")[1])
  # Node with port >= 2300 are processing nodes, others are idle nodes
  if port >= 2300:
    processing_nodes.append(node)
  else:
    idle_nodes.append(node)

  # Special port for distribution
  if port == 2350 or port == 2250:
    distribution_node = node

# Change distribution node
portal_actitivities.manage_setDistributingNode(distribution_node)
# Add processing nodes
for node in processing_nodes:
  portal_actitivities.manage_addToProcessingList((node,))
# Remove idle nodes from processing nodes
for node in idle_nodes:
  portal_actitivities.manage_removeFromProcessingList((node,))

print 'Distributing Node:'
print json.dumps(portal_actitivities.getDistributingNode())
print 'Processing Nodes:'
print json.dumps(portal_actitivities.getProcessingNodeList())

return printed
