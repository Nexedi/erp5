# This script is called to defer fulltext indexing in a lower priority.
GROUP_METHOD_ID = context.getPath() + '/SQLCatalog_deferFullTextIndexActivity'
for document_value, root_document_path in zip(getObject, getRootDocumentPath):
  document_value.activate(
    activity='SQLQueue',
    priority=4,
    group_method_id=GROUP_METHOD_ID,
    serialization_tag='full_text_' + root_document_path,
  ).SQLCatalog_deferFullTextIndexActivity()
