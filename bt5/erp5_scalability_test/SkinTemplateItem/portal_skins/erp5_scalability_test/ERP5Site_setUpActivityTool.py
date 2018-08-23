if not context.portal_activities.isSubscribed():
  context.portal_activities.subscribe()

context.portal_activities.manage_removeFromProcessingList(context.portal_activities.getProcessingNodeList())

distribution_node = None
distribution_node_list = []
activity_node_list = []
for node_id in context.portal_activities.getIdleNodeList():
  if node_id.startswith('activities'):
    activity_node_list.append(node_id)
  elif node_id.startswith('distribution'):
    distribution_node_list.append(node_id)

activity_node_list.sort()
distribution_node_list.sort()

if distribution_node_list:
  distribution_node = distribution_node_list[0]

if distribution_node is None:
  distribution_node = activity_node_list[0]

context.portal_activities.manage_addToProcessingList(activity_node_list)
context.portal_activities.manage_setDistributingNode(distribution_node)
