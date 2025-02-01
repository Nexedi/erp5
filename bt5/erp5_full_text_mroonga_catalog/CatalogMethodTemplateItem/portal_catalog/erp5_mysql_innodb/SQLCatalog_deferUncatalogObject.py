# This script is called to defer fulltext unindexing.
METHOD_ID = script.id + 'Activity'
GROUP_METHOD_ID = context.getRelativeUrl() + '/' + METHOD_ID
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
# Use unindexObject as dummy method id for compatibility with
#   after_method_id=('unindexObject', ...)
context.activate(
  activity='SQLQueue',
  priority=priority,
  node='same',
  group_method_id=GROUP_METHOD_ID,
).unindexObject(uid=uid)
