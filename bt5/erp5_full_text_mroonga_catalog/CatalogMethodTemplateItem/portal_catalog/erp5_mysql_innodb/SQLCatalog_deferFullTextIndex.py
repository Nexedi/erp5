# This script is called to defer fulltext indexing.
METHOD_ID = script.id + 'Activity'
GROUP_METHOD_ID = context.getPath() + '/' + METHOD_ID
activateObject = context.getPortalObject().portal_activities.activateObject
priority = context.getActivityRuntimeEnvironment().getPriority()
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
