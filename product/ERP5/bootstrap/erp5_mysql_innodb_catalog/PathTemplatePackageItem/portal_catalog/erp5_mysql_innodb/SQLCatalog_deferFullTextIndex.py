# This script is called to defer fulltext indexing in a lower priority.
context.activate(activity='SQLQueue', priority=4, group_method_id=None).SQLCatalog_deferFullTextIndexActivity(path_list=list(getPath))
