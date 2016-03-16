# This script is called to defer fulltext indexing in a lower priority.
# Activities are serialised because concurrent write may cause crash of searchd.
context.activate(activity='SQLQueue', priority=4, serialization_tag='sphinxse_indexing', group_method_id=None).SQLCatalog_deferFullTextIndexActivity(path_list=list(getPath))
