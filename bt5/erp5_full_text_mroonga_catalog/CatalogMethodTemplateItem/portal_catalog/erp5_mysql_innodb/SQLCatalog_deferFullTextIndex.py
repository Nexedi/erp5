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
for document, root_document_path in zip(getPath, getRootDocumentPath):
  getattr(
    activateObject(
      document,
      activity='SQLDict',
      priority=priority,
      node='same',
      group_method_id=GROUP_METHOD_ID,
      serialization_tag='full_text_' + root_document_path,
    ),
    METHOD_ID,
  )()
