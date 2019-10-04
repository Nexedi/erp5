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
  # default ERP5 instanciation uses following schema for naming all zope nodes
  # activities-0..9 when number of nodes <= 10
  # activites-01..09 (or n) when number of nodes > 10
  # in scalability tests instance keeps track of old used nodes and when nodes > 10 
  # will pick by default sort "activity-0" which is NO longer an existing zope process
  # this is an ugly fix and real woraround is to have something like activities-000x schema by default
  if distribution_node == "activities-0" and "activities-00" in activity_node_list:
    # give precedence
    distribution_node = "activities-00"

context.portal_activities.manage_addToProcessingList(activity_node_list)
context.portal_activities.manage_setDistributingNode(distribution_node)
