# This script is called to defer fulltext indexing.
METHOD_ID = script.id + 'Activity'
GROUP_METHOD_ID = context.getPath() + '/' + METHOD_ID
activateObject = context.getPortalObject().portal_activities.activateObject
try:
  priority = context.getActivityRuntimeEnvironment().getPriority()
except KeyError:
  # called outside of an activity, could be an immediate reindexation
  # XXX: duplicates default priority for sake of simplicity and speed.
  # Strictly, this could also look-up default activate parameters, but on
  # which document ? Traversing is expensive. So keep things fast by default.
  priority = 1
# Optimise cache usage by reducing the likelyhood of a processing node
# including activities spawned by others into its activity group.
# But prevent the group from going below 10 activities, for better throughput.
group_method_cost = min(.1, 1. / len(getPath))
for document in getPath:
  getattr(
    activateObject(
      document,
      activity='SQLDict',
      priority=priority,
      node='same',
      group_method_id=GROUP_METHOD_ID,
      group_method_cost=group_method_cost,
      serialization_tag='full_text_' + document,
    ),
    METHOD_ID,
  )()
