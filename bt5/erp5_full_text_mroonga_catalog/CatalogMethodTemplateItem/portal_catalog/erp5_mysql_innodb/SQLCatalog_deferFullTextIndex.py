# This script is called to defer fulltext indexing in a lower priority.
GROUP_METHOD_ID = context.getPath() + '/SQLCatalog_deferFullTextIndexActivity'
activateObject = context.getPortalObject().portal_activities.activateObject
for document, root_document_path in zip(getPath, getRootDocumentPath):
  activateObject(
    document,
    activity='SQLQueue',
    priority=4,
    node='same',
    group_method_id=GROUP_METHOD_ID,
    serialization_tag='full_text_' + root_document_path,
  ).SQLCatalog_deferFullTextIndexActivity()
