# This script is called to defer fulltext indexing in a lower priority.
METHOD_ID = script.id + 'Activity'
GROUP_METHOD_ID = context.getPath() + '/' + METHOD_ID
activateObject = context.getPortalObject().portal_activities.activateObject
for document, root_document_path in zip(getPath, getRootDocumentPath):
  getattr(
    activateObject(
      document,
      activity='SQLQueue',
      priority=4,
      node='same',
      group_method_id=GROUP_METHOD_ID,
      serialization_tag='full_text_' + root_document_path,
    ),
    METHOD_ID,
  )()
